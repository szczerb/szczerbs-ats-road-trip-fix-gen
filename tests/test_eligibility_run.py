"""End-to-end workflow boundaries using small archive fixtures and a stub plan."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest
import zipfile
from ats_road_trip import eligibility_run as run


def archive(path, files=None):
    with zipfile.ZipFile(path, 'w') as z:
        for name, data in (files or {}).items():
            z.writestr(name, data)


class EligibilityWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / 'game'
        self.game.mkdir()
        archive(self.game/'version.scs', {'version.sii':
                'SiiNunit {\napplication: ats\nversion: "1.61.3.18"\n}\n'})
        for name in ('base.scs', 'base_share.scs', 'base_map.scs', 'def.scs', 'dlc_rt_ford.scs'):
            archive(self.game/name)
        self.config = self.root/'review.toml'
        self.config.write_text('schema_version = 1\n')
        self.patch = patch.object(run, 'REPO_ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.stamp = '2026-10-18_04-01-00'

    def invoke(self, *, generate=False, blockers=(), resources=None, planner=None):
        report = {'coverage': {'complete': not blockers, 'blockers': list(blockers)},
                  'selected_job_ids': ['car_job.documents']}
        if planner is None:
            planner = lambda *a, **kw: (report, {'def/car_job_data.sii': b'patched'} if resources is None else resources)
        with patch('ats_road_trip.courier_eligibility.plan_courier_eligibility', side_effect=planner):
            return run.run_courier_eligibility(self.config, generate=generate,
                                               game_dir=self.game, run_id=self.stamp)

    def test_analysis_never_packages_candidate_bytes(self):
        with patch.object(run, 'write_mod') as writer:
            result = self.invoke()
        writer.assert_not_called()
        self.assertEqual(result['status'], 'reported')
        self.assertEqual(result['generated_mod_count'], 0)
        self.assertFalse((self.root/'local_outputs/generated').exists())
        self.assertEqual(json.loads(Path(result['report_path']).read_text()), result)

    def test_analysis_retains_partial_coverage_without_mod(self):
        result = self.invoke(blockers=[{'reason': 'source changed'}])
        self.assertEqual(result['status'], 'reported_partial')
        self.assertEqual(result['generated_mod_count'], 0)

    def test_generation_self_describes_separate_category_and_preserves_source(self):
        before = self.config.read_bytes()
        result = self.invoke(generate=True)
        self.assertEqual(result['status'], 'generated')
        self.assertEqual(result['generated_mod_count'], 1)
        self.assertEqual(self.config.read_bytes(), before)
        with zipfile.ZipFile(result['output']) as z:
            manifest = z.read('manifest.sii').decode()
            self.assertIn('category[]: "other"', manifest)
            self.assertIn('Practical Courier Jobs', manifest)
            self.assertIn('1.61-r0-experimental', manifest)
            self.assertEqual(z.read('def/car_job_data.sii'), b'patched')
            self.assertNotIn('mod_icon.jpg', z.namelist())
            self.assertFalse(json.loads(z.read('road_trip_fix_report.json'))['in_game_verified'])
            self.assertIsNone(z.testzip())

    def test_blocker_prevents_publication_but_retains_audit(self):
        with self.assertRaisesRegex(ValueError, 'blockers'), patch.object(run, 'write_mod') as writer:
            self.invoke(generate=True, blockers=[{'reason': 'unknown cargo'}])
        writer.assert_not_called()
        audit = self.root/'local_outputs/work'/self.stamp/'practical-courier-jobs/audit.json'
        self.assertEqual(json.loads(audit.read_text())['status'], 'blocked')
        self.assertFalse((self.root/'local_outputs/generated').exists())

    def test_missing_complete_assertion_cannot_publish(self):
        def malformed(*a, **kw):
            return {'coverage': {'blockers': []}}, {'def/car_job_data.sii': b'x'}
        with self.assertRaisesRegex(ValueError, 'blockers'), patch.object(run, 'write_mod') as writer:
            self.invoke(generate=True, planner=malformed)
        writer.assert_not_called()
        self.assertFalse((self.root/'local_outputs/generated').exists())

    def test_noop_is_reported_without_empty_package(self):
        result = self.invoke(generate=True, resources={})
        self.assertEqual(result['status'], 'already_covered')
        self.assertEqual(result['generated_mod_count'], 0)
        self.assertNotIn('output', result)

    def test_unexpected_resources_and_mutating_inputs_do_not_publish(self):
        with self.assertRaisesRegex(ValueError, 'unexpected resource'):
            self.invoke(generate=True, resources={'map/usa/unsafe.base': b'x'})
        self.stamp = '2026-10-18_04-01-01'
        def changed(*a, **kw):
            self.config.write_text('changed configuration with different size')
            return {'coverage': {'complete': True, 'blockers': []}}, {'def/car_job_data.sii': b'x'}
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            self.invoke(generate=True, planner=changed)
        self.assertFalse((self.root/'local_outputs/generated').exists())

    def test_existing_audit_and_invalid_parameters_are_rejected(self):
        self.invoke()
        with self.assertRaises(FileExistsError):
            self.invoke()
        for options in ({'revision': True}, {'run_id': '../escape'}, {'revision': -1}):
            with self.assertRaises(ValueError):
                run.run_courier_eligibility(self.config, game_dir=self.game, **options)
