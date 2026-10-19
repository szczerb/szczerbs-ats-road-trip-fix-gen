"""Exercise the public finite-batch write boundary with authored ZIP fixtures."""
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import struct
import unittest
from unittest.mock import patch
import zipfile

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.station_parking import batch_workflow as workflow
from tests import test_station_parking_batch as fixtures
from tests.test_station_parking_batch import SECTOR, VERSION, manifest, sha
from tests.test_station_effective_planning import pit_text


class StationBatchRunTests(unittest.TestCase):
    def setUp(self):
        self.helper = fixtures.StationBatchTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root = self.helper.root
        fixture_stack, fixture_plans = self.helper.fixture(different_state=True, baseline=True)
        source_contents = {p: fixture_stack.packages[0].read(p) for p in fixture_stack.packages[0].files}
        baseline_contents = {p: fixture_stack.packages[1].read(p) for p in fixture_stack.packages[1].files}
        # Keep the second authored station outside the first one's bounded
        # neighboring-prefab context while retaining both in one sector.
        for contents in (source_contents, baseline_contents):
            data = bytearray(contents[SECTOR])
            for node in parse_sector(data).nodes:
                if node.uid >= 1000:
                    old_x = struct.unpack_from('<i', data, node.offset + 8)[0]
                    struct.pack_into('<i', data, node.offset + 8, old_x + 500 * 256)
            contents[SECTOR] = bytes(data)
        self.sources = [self.helper.package('first-source.scs', source_contents).path,
                        self.helper.package('second-source.scs', {**source_contents, 'authored-source-identity.txt': b'separate source archive'}).path]
        self.baseline = self.helper.package('normal-r9.scs', baseline_contents).path
        self.packages = [*self.sources, self.baseline]
        self.mesh = self.root / 'station.pim'
        self.mesh.write_text(self.helper.mesh, encoding='utf-8')
        self.pit = self.mesh.with_suffix('.pit')
        state = pit_text()
        state += state[state.index('Variant {'):].replace('Name: "default"', 'Name: "city"', 1)
        self.pit.write_text(state.replace('VariantCount: 1', 'VariantCount: 2'), encoding='utf-8')
        self.configs = []
        for index, (_, report, _) in enumerate(fixture_plans):
            config = deepcopy(report['configuration'])
            config['map_name'] = f'Fixture Source {index + 1}'
            config['fingerprints']['sector'] = sha(baseline_contents[SECTOR])
            config['fingerprints']['source_archive'] = sha(self.sources[index].read_bytes())
            config_path = self.root / f'site-{index + 1}.json'
            config_path.write_text(json.dumps(config), encoding='utf-8')
            self.configs.append(config_path)
        self.manifest = manifest()
        for site in self.manifest['stations']:
            index = int(site['site_id'][1:]) - 1
            site.update(source_package=self.sources[index].name, config=self.configs[index].name, mesh=self.mesh.name)
        self.manifest_path = self.root / 'batch.json'
        self.write_manifest()
        self.installed = self.root / 'game'
        self.installed.mkdir()
        (self.installed / 'version.sii').write_text('authored game identity', encoding='utf-8')
        self.profile = self.root / 'profile'
        self.profile.mkdir()
        (self.profile / 'sentinel').write_bytes(b'User profile must stay unchanged')
        self.sequence = 0
        for mocked in (patch.object(workflow, 'REPO_ROOT', self.root / 'repo'),
                       patch.object(workflow, '_game_directory', return_value=self.installed),
                       patch.object(workflow, '_game_version', return_value=VERSION),
                       patch.object(workflow, '_game_packages', return_value=([], ()))):
            mocked.start()
            self.addCleanup(mocked.stop)

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding='utf-8')

    def run_batch(self, **kwargs):
        self.sequence += 1
        return workflow.run_station_parking_batch(self.manifest_path, packages=self.packages,
            run_id=f'2026-10-19_22-00-{self.sequence:02}', **kwargs)

    def test_actual_writer_combines_two_source_maps_over_same_effective_r9_sector(self):
        before = {path: sha(path.read_bytes()) for path in [*self.packages, self.installed / 'version.sii', self.profile / 'sentinel']}
        with patch('subprocess.Popen', side_effect=AssertionError('Workflow must not launch a process')):
            audit = self.run_batch(generate=True, experimental=True)
        self.assertEqual(audit['status'], 'generated')
        self.assertEqual(audit['generated_mod_count'], 1)
        self.assertEqual([site['site_id'] for site in audit['sites']], ['P01', 'P02'])
        self.assertEqual(audit['workflow']['packages_low_to_high'], [str(p) for p in self.packages])
        self.assertNotEqual(audit['sites'][0]['config']['fingerprints']['source_archive'], audit['sites'][1]['config']['fingerprints']['source_archive'])
        for site in audit['sites']:
            self.assertTrue(site['coverage']['complete'])
            self.assertIn('<svg', Path(site['plan_svg']).read_text())
            detail = json.loads(Path(site['report_path']).read_text())
            self.assertTrue(detail['coverage']['complete'])
            self.assertIn('local_context', detail)
        with zipfile.ZipFile(audit['output']) as output:
            data = output.read(SECTOR)
            aliases = [token(site['private_alias']) for site in audit['sites']]
            self.assertEqual([p.details['model'] for p in parse_sector(data).prefabs], aliases)
            self.assertEqual(len([p for p in output.namelist() if p.endswith('.ppd')]), 2)
            self.assertNotIn('prefab/rtfix/r9base.ppd', output.namelist())
            self.assertNotIn('prefab/rtfix/r9-unrelated.ppd', output.namelist())
            self.assertIn('F BATCH r1', output.read('manifest.sii').decode())
            self.assertIn('keep those standard fixes enabled', output.read('mod_description.txt').decode())
        self.assertEqual(before, {path: sha(path.read_bytes()) for path in before})
        self.assertEqual(list(self.profile.iterdir()), [self.profile / 'sentinel'])
        self.assertEqual(list(self.installed.iterdir()), [self.installed / 'version.sii'])

    def test_analysis_orders_manifest_stably_and_never_calls_writer(self):
        with patch.object(workflow, 'write_mod', side_effect=AssertionError('Analysis called writer')):
            first = self.run_batch()
            self.manifest['stations'].reverse()
            self.write_manifest()
            second = self.run_batch()
        self.assertEqual(first['status'], 'reported')
        self.assertEqual(first['generated_mod_count'], 0)
        self.assertEqual(first['planner'], second['planner'])
        self.assertEqual([site['site_id'] for site in second['sites']], ['P01', 'P02'])

    def test_one_blocked_site_prevents_combination_and_writer(self):
        actual_planner = workflow.plan_station_parking
        seen = []
        def planner(*args, **kwargs):
            report, resources = actual_planner(*args, **kwargs)
            seen.append(report['station_id'])
            if len(seen) == 2:
                report['coverage'] = {'complete': False, 'blockers': [{'reason': 'authored blocked control'}]}
                resources = {}
            return report, resources
        with patch.object(workflow, 'plan_station_parking', side_effect=planner), patch.object(workflow, 'compose_station_plans') as compose, patch.object(workflow, 'write_mod') as writer:
            audit = self.run_batch(generate=True, experimental=True)
        self.assertEqual(len(seen), 2)
        self.assertEqual(audit['status'], 'blocked')
        self.assertEqual(audit['generated_mod_count'], 0)
        self.assertEqual(len(audit['sites']), 2)
        self.assertTrue(Path(audit['sites'][0]['report_path']).is_file())
        self.assertFalse(audit['planner']['coverage']['complete'])
        writer.assert_not_called()
        compose.assert_not_called()

    def test_source_or_converted_state_drift_blocks_before_planning(self):
        for path in (self.sources[1], self.mesh, self.pit):
            before = path.read_bytes()
            path.write_bytes(before + b'drift')
            with self.subTest(path=path.name), patch.object(workflow, 'plan_station_parking') as planner, patch.object(workflow, 'write_mod') as writer:
                with self.assertRaisesRegex(ValueError, 'SHA-256 drift'):
                    self.run_batch(generate=True, experimental=True)
                planner.assert_not_called()
                writer.assert_not_called()
            path.write_bytes(before)

    def test_config_and_manifest_changed_during_planning_block_writer(self):
        actual_planner = workflow.plan_station_parking
        for path in (self.configs[0], self.manifest_path):
            before = path.read_bytes()
            changed = False
            def planner(*args, **kwargs):
                nonlocal changed
                result = actual_planner(*args, **kwargs)
                if not changed:
                    path.write_bytes(before + b'\n ')
                    changed = True
                return result
            with self.subTest(path=path.name), patch.object(workflow, 'plan_station_parking', side_effect=planner), patch.object(workflow, 'write_mod') as writer:
                with self.assertRaisesRegex(ValueError, 'changed during'):
                    self.run_batch(generate=True, experimental=True)
                writer.assert_not_called()
            path.write_bytes(before)

    def test_config_changed_immediately_after_parse_cannot_attest_different_settings(self):
        actual_loader=workflow._load_config
        changed=False
        def loader(path):
            nonlocal changed
            result=actual_loader(path)
            if not changed:
                altered=deepcopy(result);altered['map_name']='Changed After Parse'
                Path(path).write_text(json.dumps(altered),encoding='utf-8')
                changed=True
            return result
        with patch.object(workflow,'_load_config',side_effect=loader), patch.object(workflow,'write_mod') as writer:
            with self.assertRaisesRegex(ValueError,'changed during'):
                self.run_batch(generate=True,experimental=True)
            writer.assert_not_called()

    def test_effective_directory_material_same_stat_drift_after_composition_blocks_writer(self):
        override = self.root / 'directory-model'
        material = override / 'material/paint.tobj'
        material.parent.mkdir(parents=True)
        with zipfile.ZipFile(self.sources[0]) as archive:
            material.write_bytes(archive.read('material/paint.tobj'))
        self.packages.append(override)
        actual_compose = workflow.compose_station_plans
        def compose(*args, **kwargs):
            result = actual_compose(*args, **kwargs)
            before = material.stat()
            data = material.read_bytes()
            material.write_bytes(bytes([data[0] ^ 1]) + data[1:])
            os.utime(material, ns=(before.st_atime_ns, before.st_mtime_ns))
            return result
        with patch.object(workflow, 'compose_station_plans', side_effect=compose), patch.object(workflow, 'write_mod') as writer:
            with self.assertRaisesRegex(ValueError, 'resource SHA-256 drift before packaging'):
                self.run_batch(generate=True, experimental=True)
            writer.assert_not_called()

    def test_public_generation_gate_requires_experimental_before_loading_inputs(self):
        with patch.object(workflow, '_game_directory') as game, patch.object(workflow, 'write_mod') as writer:
            with self.assertRaisesRegex(ValueError, 'experimental'):
                self.run_batch(generate=True)
            game.assert_not_called()
            writer.assert_not_called()
        from ats_road_trip.cli import main, parser
        args = parser().parse_args(['generate-station-parking-batch', '--manifest', str(self.manifest_path), '--experimental'])
        self.assertTrue(args.experimental)
        self.assertEqual(args.revision, 1)
        with patch('sys.stderr', new_callable=io.StringIO), self.assertRaises(SystemExit) as exited:
            main(['generate-station-parking-batch', '--manifest', str(self.manifest_path)])
        self.assertEqual(exited.exception.code, 2)
