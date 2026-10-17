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
