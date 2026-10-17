"""Small archive fixtures for the one-source map-wide workflow."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import sys
import unittest
from unittest.mock import patch
import zipfile

from ats_road_trip import bulk_run


def archive(path: Path, files=None):
    with zipfile.ZipFile(path, 'w') as z:
        for name, data in (files or {}).items():
            z.writestr(name, data)


class BulkRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / 'game'
        self.inputs = self.root / 'local_inputs'
        self.game.mkdir()
        self.inputs.mkdir()
        archive(self.game / 'version.scs',
                {'version.sii': 'SiiNunit\n{\nfs_pack_set : .test {\n application: ats\n version: "1.61.3.18"\n}\n}\n'})
        for name in (*bulk_run._BASE_PACKAGES, 'dlc_rt_ford.scs'):
            archive(self.game / name)
        self.source = self.inputs / 'ATS_Expansion_v23.0_1.61.scs'
        archive(self.source, {'map/usa/sec+0000+0000.base': b'placeholder'})

    def test_game_version_from_version_archive_and_refuses_other_release(self):
        self.assertEqual(bulk_run._game_version(self.game, None), '1.61.3.18')
        archive(self.game / 'version.scs',
                {'version.sii': 'SiiNunit\n{\n application: ats\n version: "1.62.0"\n}\n'})
        with self.assertRaisesRegex(ValueError, 'ATS 1.61'):
            bulk_run._game_version(self.game, None)

    def test_dependency_profiles_and_output_paths(self):
        resource = self.inputs / 'Reforma_MegaResources_v3.scs'
        reforma = self.inputs / 'Reforma_3.scs'
        for path in (resource, reforma):
            archive(path)
        self.assertEqual(bulk_run._map_packages(reforma, []), [resource, reforma])
        siblings = [self.inputs / f'promods-ats-{role}-v164.scs'
                    for role in ('assets', 'models', 'def', 'map')]
        for path in siblings:
            archive(path)
        wce = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        archive(wce)
        self.assertEqual(bulk_run._map_packages(siblings[-1], []), siblings)
        self.assertEqual(bulk_run._map_packages(wce, []), [*siblings, wce])
        with patch.object(bulk_run, 'REPO_ROOT', self.root):
            work, output, stamp = bulk_run._run_paths('ProMods Canada', 3, '2026-10-17_22-11-10')
        self.assertEqual(work, self.root / 'local_outputs/work/2026-10-17_22-11-10/promods-canada')
        self.assertEqual(output.name,
                         'szczerbs-road-trip-gas-stations-fix-promods-canada-1.61-r3-experimental.scs')
        self.assertEqual(stamp, '2026-10-17_22-11-10')

    def test_connector_source_only_stacks_and_distinct_labels(self):
        reforma_resources = self.inputs / 'Reforma_MegaResources_v3_0_1_161.scs'
        reforma = self.inputs / 'Reforma_3_0_1_161.scs'
        reforma_patch = self.inputs / 'Reforma_OtherMaps_Patch_40_161.scs'
        promods = [self.inputs / f'promods-ats-{role}-v164.scs'
                   for role in ('assets', 'models', 'def', 'map')]
        western = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        western_patch = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        for path in (reforma_resources, reforma, reforma_patch, *promods, western, western_patch):
            archive(path)
        self.assertEqual(bulk_run._profile(reforma_patch)[0], 'Reforma OtherMaps Patch')
        self.assertEqual(bulk_run._profile(western_patch)[0],
                         'Western Canada ProMods Connections')
        self.assertEqual(bulk_run._map_packages(reforma_patch, []),
                         [reforma_resources, reforma, reforma_patch])
        self.assertEqual(bulk_run._map_packages(western_patch, []),
                         [western, promods[1], promods[0], promods[3], promods[2],
                          western_patch])
        # A main-map invocation must never pick the OtherMaps patch as Reforma.
        self.assertEqual(bulk_run._map_packages(reforma, []), [reforma_resources, reforma])
        self.assertEqual(bulk_run._map_packages(western, []), [*promods, western])
        with patch.object(bulk_run, 'REPO_ROOT', self.root):
            _, output, _ = bulk_run._run_paths('Reforma OtherMaps Patch', 1,
                                               '2026-10-17_22-11-10')
        self.assertIn('reforma-othermaps-patch-1.61-r1-experimental', output.name)

    def test_connector_explicit_order_and_missing_or_ambiguous_companions(self):
        reforma_resources = self.inputs / 'Reforma_MegaResources_v3.scs'
        reforma = self.inputs / 'Reforma_3.scs'
        reforma_patch = self.inputs / 'Reforma_OtherMaps_Patch_40_161.scs'
        promods = [self.inputs / f'promods-ats-{role}-v164.scs'
                   for role in ('assets', 'models', 'def', 'map')]
        western = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        western_patch = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        for path in (reforma_resources, reforma_patch, *promods, western, western_patch):
            archive(path)
        with self.assertRaisesRegex(ValueError, 'Reforma_\\[0-9\\]'):
            bulk_run._map_packages(reforma_patch, [])
        archive(reforma)
        self.assertEqual(bulk_run._map_packages(reforma_patch, [str(reforma)]),
                         [reforma_resources, reforma, reforma_patch])
        self.assertEqual(bulk_run._map_packages(western_patch,
                         [str(western), str(promods[3])]),
                         [western, promods[1], promods[0], promods[3],
                          promods[2], western_patch])
        with self.assertRaisesRegex(ValueError, 'Source archive must be highest'):
            bulk_run._map_packages(western_patch, [str(western_patch)])
        # The user can explicitly choose another priority; inference never
        # reorders their supplied archives.
        self.assertEqual(bulk_run._map_packages(western_patch,
                         [str(promods[3]), str(western)]),
                         [promods[1], promods[0], promods[3], western,
                          promods[2], western_patch])
        other = self.inputs / 'Reforma_4.scs'
        archive(other)
        with self.assertRaisesRegex(ValueError, 'Expected exactly one sibling Reforma_'):
            bulk_run._map_packages(reforma_patch, [])
        # An explicit choice resolves sibling ambiguity without pulling both.
        self.assertEqual(bulk_run._map_packages(reforma_patch, [str(reforma)]),
                         [reforma_resources, reforma, reforma_patch])

    def test_connector_does_not_pull_unrelated_or_incomplete_maps(self):
        promods = [self.inputs / f'promods-ats-{role}-v164.scs'
                   for role in ('assets', 'models', 'def', 'map')]
        western = self.inputs / 'Western_Canada_Expansion_v1.7.3.scs'
        connector = self.inputs / 'Western_Canada_Promods_Connections_v1.7.3.scs'
        alaska = self.inputs / 'Alaska_Expansion_v1.2.3.scs'
        for path in (*promods, western, connector, alaska):
            archive(path)
        self.assertNotIn(alaska, bulk_run._map_packages(connector, []))
        promods[2].unlink()
        with self.assertRaisesRegex(ValueError, 'promods-ats-def'):
            bulk_run._map_packages(connector, [])
        # Explicit dependencies can reside outside the source directory.
        separate = self.root / 'separate'
        separate.mkdir()
        explicit_def = separate / promods[2].name
        archive(explicit_def)
        self.assertEqual(bulk_run._map_packages(connector, [str(explicit_def)]),
                         [western, promods[1], promods[0], promods[3], explicit_def,
                          connector])

    def test_full_explicit_live_order_is_unchanged(self):
        names = ('Reforma_MegaResources_v3.scs', 'Reforma_3.scs',
                 'ATS_Expansion_v23.0_1.61.scs',
                 'Western_Canada_Expansion_v1.7.3.scs',
                 'promods-ats-models-v164.scs', 'promods-ats-assets-v164.scs',
                 'promods-ats-map-v164.scs', 'promods-ats-def-v164.scs',
                 'Reforma_OtherMaps_Patch_40_161.scs',
                 'Western_Canada_Promods_Connections_v1.7.3.scs')
        paths = [self.inputs / name for name in names]
        for path in paths:
            archive(path)
        self.assertEqual(bulk_run._map_packages(paths[-1], [str(p) for p in paths[:-1]]),
                         paths)

    def test_connector_generation_uses_distinct_metadata_and_existing_icons(self):
        source_icons = bulk_run.REPO_ROOT / 'assets/mod-icons'
        target_icons = self.root / 'assets/mod-icons'
        target_icons.mkdir(parents=True)
        for base in ('reforma', 'western-canada'):
            (target_icons / f'{base}-c.jpg').write_bytes(
                (source_icons / f'{base}-c.jpg').read_bytes())
        names = ('Reforma_MegaResources_v3.scs', 'Reforma_3.scs',
                 'Reforma_OtherMaps_Patch_40_161.scs',
                 'promods-ats-assets-v164.scs', 'promods-ats-models-v164.scs',
                 'promods-ats-def-v164.scs', 'promods-ats-map-v164.scs',
                 'Western_Canada_Expansion_v1.7.3.scs',
                 'Western_Canada_Promods_Connections_v1.7.3.scs')
        for name in names:
            archive(self.inputs / name)
        module = SimpleNamespace(plan_map_fuel=lambda *args, **kwargs:
                                 ({'blockers': []}, {'map/usa/fixture.base': b'fixture'}))
        cases = (('Reforma_OtherMaps_Patch_40_161.scs',
                  'Reforma OtherMaps Patch', 'reforma', '2026-10-17_22-11-10'),
                 ('Western_Canada_Promods_Connections_v1.7.3.scs',
                  'Western Canada ProMods Connections', 'western-canada',
                  '2026-10-17_22-11-11'))
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.bulk_fuel': module}):
            for source_name, label, icon_base, run_id in cases:
                audit = bulk_run.generate_map_fuel(self.inputs / source_name,
                                                   game_dir=self.game, run_id=run_id)
                self.assertEqual(audit['status'], 'generated')
                self.assertEqual(audit['workflow']['map_name'], label)
                with zipfile.ZipFile(audit['output']) as z:
                    self.assertIn(f'for {label}', z.read('manifest.sii').decode())
                    self.assertEqual(z.read('mod_icon.jpg'),
                                     (target_icons / f'{icon_base}-c.jpg').read_bytes())
                    report = json.loads(z.read('road_trip_fix_report.json'))
                    self.assertEqual(report['workflow']['target_map_package'],
                                     str((self.inputs / source_name).resolve()))

    def _run_with_plan(self, planner):
        module = SimpleNamespace(plan_map_fuel=planner)
        with patch.object(bulk_run, 'REPO_ROOT', self.root), \
             patch.dict(sys.modules, {'ats_road_trip.bulk_fuel': module}):
            return bulk_run.generate_map_fuel(self.source, game_dir=self.game,
                                              run_id='2026-10-17_22-11-10')

    def test_blockers_write_audit_and_refuse_package(self):
        def planner(stack, *, map_packages, map_name):
            self.assertEqual(map_packages, {str(self.source.resolve())})
            self.assertEqual(map_name, 'ATS Expansion')
            return {'blockers': [{'reason': 'unknown sector layout'}]}, {'map/usa/x.base': b'x'}

        with self.assertRaisesRegex(ValueError, 'coverage blocker'):
            self._run_with_plan(planner)
        audit_path = self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json'
        audit = json.loads(audit_path.read_text())
        self.assertEqual(audit['status'], 'blocked')
        self.assertEqual(audit['planned_resource_count'], 1)
        self.assertFalse((self.root / 'local_outputs/generated/2026-10-17_22-11-10').exists())

    def test_already_covered_has_explicit_no_output(self):
        audit = self._run_with_plan(lambda *args, **kwargs: ({'blockers': []}, {}))
        self.assertEqual(audit['status'], 'already_covered')
        self.assertNotIn('output', audit)

    def test_planner_error_writes_failure_audit_without_archive(self):
        def planner(*args, **kwargs):
            raise ValueError('invalid source unit fixture')
        with self.assertRaisesRegex(ValueError, 'invalid source unit'):
            self._run_with_plan(planner)
        path = self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json'
        report = json.loads(path.read_text())
        self.assertEqual(report['status'], 'failed')
        self.assertIn('invalid source unit', report['error'])
        self.assertFalse(list(self.root.rglob('szczerbs-*.scs')))

    def test_source_drift_prevents_packaging(self):
        def planner(*args, **kwargs):
            self.source.write_bytes(self.source.read_bytes() + b'changed fixture')
            return {'coverage': {'blockers': []}}, {'map/usa/fixture.base': b'fixture'}
        with self.assertRaisesRegex(ValueError, 'changed during generation'):
            self._run_with_plan(planner)
        self.assertFalse(list(self.root.rglob('szczerbs-*.scs')))

    def test_generates_package_with_map_metadata_and_audit(self):
        audit = self._run_with_plan(
            lambda *args, **kwargs: ({'blockers': [], 'covered_count': 1},
                                     {'map/usa/fixture.base': b'fixture'}))
        self.assertEqual(audit['status'], 'generated')
        output = Path(audit['output'])
        self.assertTrue(output.is_file())
        with zipfile.ZipFile(output) as z:
            self.assertEqual(z.read('map/usa/fixture.base'), b'fixture')
            manifest = z.read('manifest.sii').decode()
            self.assertIn('for ATS Expansion', manifest)
            self.assertIn('1.61-r1-experimental', manifest)
            report = json.loads(z.read('road_trip_fix_report.json'))
            self.assertEqual(report['workflow']['target_map_package'], str(self.source.resolve()))
        self.assertTrue((self.root / 'local_outputs/work/2026-10-17_22-11-10/ats-expansion/audit.json').is_file())


if __name__ == '__main__':
    unittest.main()
