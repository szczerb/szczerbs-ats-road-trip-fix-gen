"""Finite fuel batch comparison, provenance and safety gates."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

from ats_road_trip.fuel_selection import FuelSelectionConfig
from ats_road_trip.fuel_selection.batch_workflow import (
    run_fuel_selection_batch, validate_manifest,
)
from ats_road_trip.map_sector import parse_sector
from tests.test_bulk_fuel import PPD, SECTOR, resources
from tests.test_fuel_selection import config, rule
from tests.test_bulk_run import archive


def _sha(data):
    return hashlib.sha256(data).hexdigest()


class FuelSelectionBatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.game = self.root / 'game'
        self.game.mkdir()
        archive(self.game / 'version.scs', {'version.sii':
            b'SiiNunit\n{\nfs_pack_set : .test {\n application: ats\n version: "1.61.3.18"\n}\n}\n'})
        for name in ('base.scs', 'base_share.scs', 'base_map.scs', 'dlc_rt_ford.scs'):
            archive(self.game / name)
        archive(self.game / 'def.scs', {'def/country/washington.sui':
            b'country_data: country.data.washington {\n fuel_price: 1.92132\n petrol_price: 1.47197\n}\n'})
        self.inputs = self.root / 'local_inputs'
        self.inputs.mkdir()
        self.source = self.inputs / 'ATS_Expansion_v23.0_1.61.scs'
        self.fixture = resources([((2., 0., 3.), 0), ((9., 0., 3.), 0)])
        self.fixture['def/data_context.sii'] = (
            b'SiiNunit\n{\ndata_context : context.fixture {\n'
            b' target_data[]: prefab.02003\n tags[]: gas_station\n}\n}\n')
        self.fixture['def/country/fixture.sui'] = (
            b'country_data: country.data.fixture {\n fuel_price: 2.0\n}\n')
        archive(self.source, self.fixture)
        self.manifest_path = self.inputs / 'batch.json'
        self.manifest = self.make_manifest()
        self.manifest_path.write_text(json.dumps(self.manifest), encoding='utf-8')

    def make_manifest(self, *, sites=None, price_packages=None, sector_data=None):
        data = sector_data if sector_data is not None else self.fixture[SECTOR]
        return {'schema_version': 1, 'batch_id': 'fuel-tour', 'game_version': '1.61.3.18',
                'sites': sites if sites is not None else [{
                    'id': 'G01', 'sector': SECTOR, 'sector_sha256': _sha(data),
                    'source_package': self.source.name, 'prefab_uid': '0x64'}],
                'price_packages': [self.source.name] if price_packages is None else price_packages}

    def run_batch(self, stamp, *, source=None, manifest=None, selection=None,
                  generate=True, experimental=True):
        manifest = manifest or self.manifest
        self.manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root):
            return run_fuel_selection_batch(self.manifest_path, packages=[source or self.source],
                game_dir=self.game, run_id=stamp, generate=generate, experimental=experimental,
                fuel_selection=selection or FuelSelectionConfig())

    def test_broad_and_selective_packages_use_same_baseline_but_different_pumps(self):
        selected = config(rule(self.fixture[PPD], roles=('public_car', 'truck_lane')))
        broad = self.run_batch('2026-10-21_02-00-01')
        realistic = self.run_batch('2026-10-21_02-00-02', selection=selected)
        self.assertEqual(broad['status'], 'generated')
        self.assertEqual(realistic['status'], 'generated')
        self.assertEqual(broad['workflow']['packages_low_to_high'],
                         realistic['workflow']['packages_low_to_high'])
        self.assertEqual(broad['workflow']['site_sector_providers'],
                         realistic['workflow']['site_sector_providers'])
        self.assertTrue(broad['output'].endswith('g1-broad-r1-fuel-tour-ats-1.61-experimental.scs'))
        self.assertTrue(realistic['output'].endswith('g2-select-r1-fuel-tour-ats-1.61-experimental.scs'))
        with zipfile.ZipFile(broad['output']) as broad_zip, zipfile.ZipFile(realistic['output']) as select_zip:
            self.assertIsNone(broad_zip.testzip())
            self.assertIsNone(select_zip.testzip())
            broad_sector = parse_sector(broad_zip.read(SECTOR))
            select_sector = parse_sector(select_zip.read(SECTOR))
            self.assertEqual(sum(bool(item.flags & 0x4000) for item in broad_sector.services), 2)
            self.assertEqual(sum(bool(item.flags & 0x4000) for item in select_sector.services), 1)
            self.assertEqual(broad_zip.read('def/country/fixture.sui'),
                             select_zip.read('def/country/fixture.sui'))
            self.assertIn(b'petrol_price:', select_zip.read('def/country/fixture.sui'))
            self.assertIn('G1 BROAD r1', broad_zip.read('mod_description.txt').decode())
            self.assertIn('G2 SELECT r1', select_zip.read('mod_description.txt').decode())
            self.assertIn('enable exactly one', select_zip.read('mod_description.txt').decode())
            report = json.loads(select_zip.read('road_trip_fix_report.json'))
            self.assertTrue(report['bounded_scope'])
            self.assertEqual(report['planner']['fuel']['coverage']['policy_selected_truck_points'], 1)
            self.assertEqual(report['planner']['prices']['coverage']['changed'], 1)
            self.assertEqual(report['fuel_selection_config']['schema_version'], 1)
            self.assertEqual(report['fuel_selection_config']['mode'], 'realistic')
            self.assertEqual(report['fuel_selection_config']['rules'][0]['id'],
                             selected.rules[0].id)
            config_bytes = json.dumps(report['fuel_selection_config'], sort_keys=True,
                                      separators=(',', ':')).encode('utf-8')
            self.assertEqual(report['fuel_selection_config_sha256'], _sha(config_bytes))

    def test_unchanged_site_with_no_prices_emits_no_empty_archive(self):
        native = resources([((2., 0., 3.), 0), ((2., 0., 3.), 1)])
        source = self.inputs / 'native.scs'
        archive(source, native)
        manifest = self.make_manifest(price_packages=[], sector_data=native[SECTOR])
        manifest['sites'][0]['source_package'] = source.name
        selected = config(rule(native[PPD], roles=('public_car',)))
        result = self.run_batch('2026-10-21_02-00-03', source=source, manifest=manifest,
                                selection=selected)
        self.assertEqual(result['status'], 'no_changes')
        self.assertEqual(result['generated_mod_count'], 0)
        self.assertIsNone(result['output'])
        self.assertEqual(result['planner']['baseline_sector_guards'], [])
        self.assertFalse((self.root / 'local_outputs/generated').exists())

    def test_policy_skipped_site_emits_source_sector_guard(self):
        source_data = self.fixture.copy()
        source = self.inputs / 'skipped.scs'
        archive(source, source_data)
        manifest = self.make_manifest(price_packages=[], sector_data=source_data[SECTOR])
        manifest['sites'][0]['source_package'] = source.name
        result = self.run_batch('2026-10-21_02-00-11', source=source, manifest=manifest,
                                selection=config())
        self.assertEqual(result['status'], 'generated')
        self.assertEqual(result['planner']['fuel']['coverage']['policy_skipped_truck_points'], 2)
        guards = result['planner']['baseline_sector_guards']
        self.assertEqual(len(guards), 1)
        self.assertEqual(guards[0]['path'], SECTOR)
        self.assertEqual(guards[0]['source_sha256'], _sha(source_data[SECTOR]))
        self.assertEqual(guards[0]['output_sha256'], _sha(source_data[SECTOR]))
        self.assertEqual(guards[0]['resource_role'], 'raw_source_baseline_guard')
        with zipfile.ZipFile(result['output']) as generated:
            self.assertEqual(generated.read(SECTOR), source_data[SECTOR])
            report = json.loads(generated.read('road_trip_fix_report.json'))
            self.assertEqual(report['planner']['baseline_sector_guards'], guards)
            self.assertIn('other generated parking/fuel edits in those sectors',
                          generated.read('mod_description.txt').decode())

    def test_manifest_rejects_duplicate_uids_and_strict_fields(self):
        duplicate = self.make_manifest()
        duplicate['sites'].append({**duplicate['sites'][0], 'id': 'G02'})
        with self.assertRaisesRegex(ValueError, 'UIDs must be unique'):
            validate_manifest(duplicate)
        with self.assertRaisesRegex(ValueError, 'unknown fields'):
            validate_manifest({**self.manifest, 'extra': True})
        unsafe_path = self.make_manifest()
        unsafe_path['sites'][0]['sector'] = 'map/../sec+0000+0000.base'
        with self.assertRaisesRegex(ValueError, 'normalized map sector'):
            validate_manifest(unsafe_path)

    def test_sector_pin_and_unknown_uid_fail_before_planning(self):
        bad_pin = self.make_manifest()
        bad_pin['sites'][0]['sector_sha256'] = '0' * 64
        self.manifest_path.write_text(json.dumps(bad_pin), encoding='utf-8')
        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root), \
             patch('ats_road_trip.fuel_selection.batch_workflow.plan_map_fuel') as planner:
            with self.assertRaisesRegex(ValueError, 'sector SHA-256 pin mismatch'):
                run_fuel_selection_batch(self.manifest_path, packages=[self.source],
                    game_dir=self.game, run_id='2026-10-21_02-00-04', generate=False,
                    fuel_selection=FuelSelectionConfig())
            planner.assert_not_called()
        missing_uid = self.make_manifest()
        missing_uid['sites'][0]['prefab_uid'] = '0x65'
        self.manifest_path.write_text(json.dumps(missing_uid), encoding='utf-8')
        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root), \
             patch('ats_road_trip.fuel_selection.batch_workflow.plan_map_fuel') as planner:
            with self.assertRaisesRegex(ValueError, 'missing or ambiguous'):
                run_fuel_selection_batch(self.manifest_path, packages=[self.source],
                    game_dir=self.game, run_id='2026-10-21_02-00-05', generate=False,
                    fuel_selection=FuelSelectionConfig())
            planner.assert_not_called()

    def test_sector_provider_override_is_rejected(self):
        higher = self.inputs / 'higher.scs'
        archive(higher, {SECTOR: self.fixture[SECTOR]})
        manifest = self.make_manifest()
        self.manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root), \
             patch('ats_road_trip.fuel_selection.batch_workflow.plan_map_fuel') as planner:
            with self.assertRaisesRegex(ValueError, 'overridden by another package'):
                run_fuel_selection_batch(self.manifest_path, packages=[self.source, higher],
                    game_dir=self.game, run_id='2026-10-21_02-00-06', generate=False,
                    fuel_selection=FuelSelectionConfig())
            planner.assert_not_called()

    def test_generated_fuel_or_rest_package_is_rejected(self):
        generated = self.inputs / 'old-fix.scs'
        archive(generated, {'road_trip_fix_report.json': json.dumps(
            {'processors_enabled': ['fuel'], 'analysis': 'bounded_missing_car_fuel'}).encode()})
        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'generated fuel/rest fix'):
                run_fuel_selection_batch(self.manifest_path, packages=[self.source, generated],
                    game_dir=self.game, run_id='2026-10-21_02-00-07', generate=False,
                    fuel_selection=FuelSelectionConfig())

    def test_price_resource_collision_with_fuel_blocks_generation(self):
        from ats_road_trip.fuel_selection import batch_workflow
        actual_plan = batch_workflow.plan_map_fuel
        actual_prices = batch_workflow.plan_petrol_prices
        fuel_paths = []

        def collide(stack, *, map_packages, map_name, fuel_selection,
                    target_prefab_uids, source_sector_paths):
            report, resources = actual_plan(stack, map_packages=map_packages, map_name=map_name,
                fuel_selection=fuel_selection, target_prefab_uids=target_prefab_uids,
                source_sector_paths=source_sector_paths)
            fuel_paths.extend(path for path in resources if path.endswith('.ppd'))
            return report, resources

        def colliding_prices(stack, *, target_packages, policy):
            report, changes = actual_prices(stack, target_packages=target_packages, policy=policy)
            self.assertTrue(fuel_paths)
            return report, {fuel_paths[0]: b'collision'}

        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root), \
             patch('ats_road_trip.fuel_selection.batch_workflow.plan_map_fuel', side_effect=collide), \
             patch('ats_road_trip.fuel_selection.batch_workflow.plan_petrol_prices', side_effect=colliding_prices):
            with self.assertRaisesRegex(ValueError, 'Fuel and petrol-price planners collide'):
                run_fuel_selection_batch(self.manifest_path, packages=[self.source],
                    game_dir=self.game, run_id='2026-10-21_02-00-11', generate=True,
                    experimental=True, fuel_selection=FuelSelectionConfig())

    def test_generation_requires_experimental_and_never_overwrites(self):
        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'requires --experimental'):
                run_fuel_selection_batch(self.manifest_path, packages=[self.source],
                    game_dir=self.game, run_id='2026-10-21_02-00-08', generate=True,
                    experimental=False)
            self.run_batch('2026-10-21_02-00-09')
            with self.assertRaises(FileExistsError):
                self.run_batch('2026-10-21_02-00-09')

    def test_directory_source_snapshot_detects_midrun_drift(self):
        directory = self.inputs / 'map-directory'
        directory.mkdir()
        for name, data in self.fixture.items():
            file = directory / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        manifest = self.make_manifest()
        manifest['sites'][0]['source_package'] = directory.name
        manifest['price_packages'] = []
        self.manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        from ats_road_trip.fuel_selection import batch_workflow
        actual = batch_workflow.plan_map_fuel

        def drift(*args, **kwargs):
            result = actual(*args, **kwargs)
            (directory / 'late-addition.txt').write_text('changed')
            return result

        with patch('ats_road_trip.fuel_selection.batch_workflow.REPO_ROOT', self.root), \
             patch('ats_road_trip.fuel_selection.batch_workflow.plan_map_fuel', side_effect=drift):
            with self.assertRaisesRegex(ValueError, 'Directory package changed'):
                run_fuel_selection_batch(self.manifest_path, packages=[directory],
                    game_dir=self.game, run_id='2026-10-21_02-00-10', generate=False,
                    fuel_selection=FuelSelectionConfig())


if __name__ == '__main__':
    unittest.main()
