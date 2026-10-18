"""End-to-end boundaries for the source-pinned tank workflow."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib
import json
import unittest
import zipfile

from ats_road_trip import tank_run as run


def archive(path, files=None):
    with zipfile.ZipFile(path, 'w') as output:
        for name, data in (files or {}).items():
            output.writestr(name, data)


class TankWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / 'game'
        self.game.mkdir()
        archive(self.game / 'version.scs', {'version.sii':
                'SiiNunit {\napplication: ats\nversion: "1.61.3.18"\n}\n'})
        for name in ('base.scs', 'base_share.scs', 'base_map.scs', 'def.scs', 'dlc_rt_ford.scs'):
            archive(self.game / name)
        self.config = self.root / 'review.toml'
        self.config.write_text('synthetic reviewed tank policy\n')
        project_icon = Path(__file__).resolve().parents[1] / 'assets/mod-icons/proposals-v3/j1b.jpg'
        default_icon = self.root / 'assets/mod-icons/reasonable-gas-tank-upgrades.jpg'
        default_icon.parent.mkdir(parents=True)
        default_icon.write_bytes(project_icon.read_bytes())
        self.patch = patch.object(run, 'REPO_ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.stamp = '2026-10-18_18-01-00'
        self.resource_path = 'def/vehicle/car/ford.mustang_67/chassis/rwd.sii'
        self.report = {
            'coverage': {'complete': True, 'blockers': []},
            'vehicles': [
                {'model': 'ford.mustang_67', 'path': self.resource_path,
                 'stock_liters': 61, 'target_liters': 80,
                 'status': 'upgraded'},
                {'model': 'ford.victoria_06', 'stock_liters': 72, 'target_liters': 72,
                 'status': 'unchanged'},
                {'model': 'ford.f150_23', 'stock_liters': 98, 'target_liters': 98,
                 'status': 'unchanged'},
                {'model': 'ford.bronco_24', 'stock_liters': 79, 'target_liters': 79,
                 'status': 'unchanged'},
            ],
        }

    def invoke(self, *, generate=False, blockers=(), resources=None, planner=None,
               icon=None, revision=2, stamp=None):
        report = dict(self.report)
        report['coverage'] = {'complete': not blockers, 'blockers': list(blockers)}
        if planner is None:
            payload = {self.resource_path: b'patched chassis'} if resources is None else resources
            planner = lambda *a, **kw: (report, payload)
        with patch('ats_road_trip.tank_upgrades.plan_tank_upgrades', side_effect=planner):
            return run.run_tank_upgrades(
                self.config, generate=generate, game_dir=self.game,
                run_id=stamp or self.stamp, revision=revision, icon=icon)

    def test_analysis_never_calls_writer_and_persists_audit_without_package(self):
        with patch.object(run, 'write_mod') as writer:
            result = self.invoke()
        writer.assert_not_called()
        self.assertEqual(result['status'], 'reported')
        self.assertTrue(result['analysis_only'])
        self.assertEqual(result['generated_mod_count'], 0)
        self.assertFalse((self.root / 'local_outputs/generated').exists())
        self.assertEqual(json.loads(Path(result['report_path']).read_text()), result)

    def test_analysis_blockers_remain_auditable_without_resources_or_writer(self):
        with patch.object(run, 'write_mod') as writer:
            result = self.invoke(blockers=[{'reason': 'source evidence missing'}])
        writer.assert_not_called()
        self.assertEqual(result['status'], 'reported_partial')
        self.assertEqual(result['planned_resource_count'], 1)
        self.assertEqual(result['generated_mod_count'], 0)
        self.assertFalse((self.root / 'local_outputs/generated').exists())

    def test_generation_blockers_save_audit_and_never_publish(self):
        with self.assertRaisesRegex(ValueError, 'blockers'), patch.object(run, 'write_mod') as writer:
            self.invoke(generate=True, blockers=[{'reason': 'unknown capacity'}])
        writer.assert_not_called()
        audit = self.root / 'local_outputs/work' / self.stamp / f'{run.SLUG}/audit.json'
        self.assertEqual(json.loads(audit.read_text())['status'], 'blocked')
        self.assertFalse((self.root / 'local_outputs/generated').exists())

    def test_default_project_jpeg_is_valid_and_packaged_with_exact_metadata(self):
        # Supply the repository artwork at the workflow's default path so the
        # workflow verifies both default selection and the writer's JPEG checks.
        icon = Path(__file__).resolve().parents[1] / 'assets/mod-icons/proposals-v3/j1b.jpg'
        result = self.invoke(generate=True)
        self.assertEqual(result['status'], 'generated')
        self.assertEqual(result['generated_mod_count'], 1)
        self.assertEqual(Path(result['output']).name,
                         'szczerbs-road-trip-reasonable-gas-tank-upgrades-1.61-r2-experimental.scs')
        with zipfile.ZipFile(result['output']) as package:
            self.assertIsNone(package.testzip())
            names = set(package.namelist())
            self.assertEqual(names, {self.resource_path, 'manifest.sii', 'mod_description.txt',
                                     'road_trip_fix_report.json', 'mod_icon.jpg'})
            manifest = package.read('manifest.sii').decode()
            self.assertIn('display_name: "szczerb\'s Road Trip reasonable gas tank upgrades"', manifest)
            self.assertIn('category[]: "other"', manifest)
            self.assertIn('author: "szczerb"', manifest)
            self.assertIn('package_version: "1.61-r2-experimental"', manifest)
            self.assertEqual(package.read(self.resource_path), b'patched chassis')
            self.assertEqual(package.read('mod_icon.jpg'), icon.read_bytes())
            description = package.read('mod_description.txt').decode()
            self.assertIn('Mustang 1967: 61 -> 80 litres.', description)
            self.assertIn('Unchanged: Crown Victoria 2006, F-150 2023, Bronco 2024.', description)
            self.assertGreaterEqual(description.count('\n\n'), 5)
            self.assertIn('Fuel consumption and other chassis settings are preserved.', description)
            self.assertIn('still require manual testing.', description)
            audit = json.loads(package.read('road_trip_fix_report.json'))
            self.assertFalse(audit['in_game_verified'])
            self.assertEqual(audit['package_metadata']['display_name'],
                             "szczerb's Road Trip reasonable gas tank upgrades")
            self.assertEqual(audit['package_metadata']['author'], 'szczerb')
            self.assertEqual(audit['package_metadata']['category'], 'other')
            self.assertEqual(audit['package_metadata']['package_version'], '1.61-r2-experimental')
            self.assertEqual(audit['package_metadata']['icon']['sha256'], hashlib.sha256(icon.read_bytes()).hexdigest())
            self.assertEqual([row['path'] for row in audit['generated_resources']], [self.resource_path])

    def test_noop_keeps_audit_without_creating_empty_package(self):
        result = self.invoke(generate=True, resources={})
        self.assertEqual(result['status'], 'already_covered')
        self.assertEqual(result['generated_mod_count'], 0)
        self.assertNotIn('output', result)
        self.assertFalse((self.root / 'local_outputs/generated').exists())
        self.assertEqual(json.loads(Path(result['report_path']).read_text())['status'], 'already_covered')

    def test_unexpected_resources_and_changed_config_are_blocked(self):
        with self.assertRaisesRegex(ValueError, 'unexpected resource'):
            self.invoke(generate=True, resources={'def/unsafe.sii': b'no'})
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            def mutate_config(*args, **kwargs):
                self.config.write_text('policy changed during planning and differs in size')
                return self.report, {self.resource_path: b'patched chassis'}
            self.invoke(generate=True, planner=mutate_config,
                        stamp='2026-10-18_18-01-01')
        self.assertFalse((self.root / 'local_outputs/generated').exists())

    def test_invalid_revision_run_id_and_existing_outputs_never_overwrite(self):
        for kwargs in ({'revision': True}, {'revision': -1}, {'stamp': '../escape'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.invoke(**kwargs)
        self.invoke(stamp='2026-10-18_18-01-02')
        with self.assertRaises(FileExistsError):
            self.invoke(stamp='2026-10-18_18-01-02')
        output_stamp = '2026-10-18_18-01-03'
        target = (self.root / 'local_outputs/generated' / output_stamp /
                  f'szczerbs-road-trip-{run.SLUG}-1.61-r2-experimental.scs')
        target.parent.mkdir(parents=True)
        target.write_bytes(b'existing package')
        with self.assertRaises(FileExistsError):
            self.invoke(generate=True, stamp=output_stamp)
        self.assertEqual(target.read_bytes(), b'existing package')

    def test_generation_cli_requires_experimental_acknowledgement(self):
        from ats_road_trip.cli import main
        with self.assertRaises(SystemExit) as raised:
            main(['generate-tank-upgrades', '--config', str(self.config), '--game-dir', str(self.game)])
        self.assertEqual(raised.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
