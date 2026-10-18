from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from ats_road_trip.cli import main, parser
from ats_road_trip.ppd import inspect_ppd
from ats_road_trip.sii import parse_units


def fuel_descriptor(flags=0):
    header = [25, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0] + [96] * 5 + [132] * 7
    return struct.pack('<24I', *header) + struct.pack('<7fII', 1, 2, 3, 1, 0, 0, 0, 3, flags)


class CliTests(unittest.TestCase):
    def test_courier_eligibility_analysis_and_generation_gate(self):
        result = {'status': 'reported', 'report_path': '/audit.json',
                  'workflow': {'work_dir': '/work'}, 'planner': {'coverage': {'blockers': []}},
                  'generated_mod_count': 0}
        with patch('ats_road_trip.eligibility_run.analyze_courier_eligibility', return_value=result) as analyze:
            response = self.run_cli(['analyze-courier-eligibility', '--config', 'review.toml'])
        self.assertEqual(response['generated_mod_count'], 0)
        self.assertEqual(analyze.call_args.args, ('review.toml',))
        with patch('ats_road_trip.eligibility_run.generate_courier_eligibility', return_value=result) as generate:
            self.run_cli(['generate-courier-eligibility', '--config', 'review.toml'], expected=2)
            generate.assert_not_called()
            self.run_cli(['generate-courier-eligibility', '--config', 'review.toml', '--experimental'])
            self.assertEqual(generate.call_args.kwargs['revision'], 3)
            self.run_cli(['generate-courier-eligibility', '--config', 'review.toml', '--experimental', '--icon', 'selected.jpg'])
            self.assertEqual(generate.call_args.kwargs['icon'], 'selected.jpg')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def run_cli(self, arguments, expected=0):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            try:
                status = main(arguments)
            except SystemExit as exc:
                status = exc.code
        self.assertEqual(status, expected, error.getvalue())
        return json.loads(output.getvalue()) if output.getvalue() else None

    def put(self, package, path, contents):
        target = self.root/package/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents.encode() if isinstance(contents, str) else contents)
        return target

    def test_fuel_generation_gate_and_roundtrip(self):
        source = self.put('map', 'prefab/gas/sample.ppd', fuel_descriptor())
        target = self.root/'fuel.scs'
        args = ['generate-fuel', '--package', str(self.root/'map'), '--path', '/prefab/gas/sample.ppd',
                '--output', str(target), '--game-version', '1.61.3.18', '--map-name', 'Synthetic Map']
        self.run_cli(args, expected=2)
        self.assertFalse(target.exists())
        result = self.run_cli([*args, '--experimental'])
        self.assertFalse(result['report']['in_game_verified'])
        with zipfile.ZipFile(target) as archive:
            patch = archive.read('prefab/gas/sample.ppd')
            self.assertEqual(inspect_ppd(patch)['fuel']['flags_one_count'], 1)
            self.assertEqual(inspect_ppd(patch)['fuel']['flags_zero_count'], 1)
            manifest = parse_units(archive.read('manifest.sii').decode())[0]
            self.assertEqual(manifest.one('display_name'), "szczerb's Road Trip Gas Stations Fix for Synthetic Map")
            self.assertEqual(manifest.one('package_version'), '1.61-r0-experimental')
            self.assertEqual(manifest.one('author'), 'szczerb')
            self.assertIsNone(archive.testzip())
        self.assertEqual(source.read_bytes(), fuel_descriptor())
        self.run_cli([*args, '--experimental'], expected=2)

    def test_noop_does_not_create_empty_mod(self):
        self.put('map', 'prefab/gas/sample.ppd', fuel_descriptor(flags=1))
        target = self.root/'no-op.scs'
        self.run_cli(['generate-fuel', '--package', str(self.root/'map'), '--prefix', '/prefab/gas/',
                      '--output', str(target), '--game-version', '1.61', '--map-name', 'Synthetic Map',
                      '--experimental'], expected=2)
        self.assertFalse(target.exists())

    def test_fuel_metadata_options(self):
        self.put('map', 'prefab/gas/sample.ppd', fuel_descriptor())
        target = self.root/'fuel-metadata.scs'
        base = ['generate-fuel', '--package', str(self.root/'map'), '--path', '/prefab/gas/sample.ppd',
                '--output', str(target), '--game-version', '1.61.3.18', '--experimental']
        self.run_cli(base, expected=2)
        self.run_cli([*base, '--map-name', 'Synthetic Map', '--revision', 'invalid'], expected=2)
        self.assertFalse(target.exists())
        self.run_cli([*base, '--map-name', 'Synthetic Map', '--revision', '3'])
        with zipfile.ZipFile(target) as archive:
            manifest = parse_units(archive.read('manifest.sii').decode())[0]
            self.assertEqual(manifest.one('package_version'), '1.61-r3-experimental')

    def test_context_generation_from_mounted_definitions(self):
        self.put('game', 'def/world/prefab.sii', '''SiiNunit {
prefab_model : prefab.canonical {
model_desc: "/prefab/a.pmd" prefab_desc: "/prefab/a.ppd"
}
}''')
        self.put('game', 'def/data_context.sii', '''SiiNunit {
data_context : context.prefab.sample { target_data[]: prefab.canonical tags[]: retail }
}''')
        self.put('game', 'def/car_job_data.sii', '''SiiNunit {
car_job_data : car_job.sample { source_data_contexts[]: retail }
}''')
        self.put('game', 'prefab/a.pmd', b'model')
        self.put('game', 'prefab/a.ppd', b'descriptor')
        self.put('map', 'base/def/world/prefab.map.sii', '''SiiNunit {
prefab_model : prefab.alias { model_desc: "/prefab/a.pmd" prefab_desc: "/prefab/a.ppd" }
}''')
        self.put('map', 'base/def/company/shop/editor/city.sii', '''SiiNunit {
company_def : .city { city: test_city prefab: alias }
}''')
        target = self.root/'context.scs'
        result = self.run_cli(['generate-context', '--baseline', str(self.root/'game'),
                              '--map', str(self.root/'map'), '--output', str(target),
                              '--game-version', '1.61', '--prefab', 'alias', '--experimental'])
        self.assertEqual(result['report']['aliases'][0]['alias'], 'prefab.alias')
        with zipfile.ZipFile(target) as archive:
            unit = parse_units(archive.read('def/data_context.rtfix.sii').decode())[0]
            self.assertEqual(unit.values('target_data'), ('prefab.alias',))
            self.assertEqual(unit.values('tags'), ('retail',))
            self.assertNotIn('def/data_context.sii', archive.namelist())
            self.assertFalse(any(path.endswith('.ppd') for path in archive.namelist()))

    def test_report_cannot_overwrite_existing_file(self):
        archive = self.root/'map.scs'
        with zipfile.ZipFile(archive, 'w') as output:
            output.writestr('manifest.sii', 'SiiNunit { }')
        report = self.root/'report.json'
        report.write_text('preserve')
        self.run_cli(['inspect', str(archive), '--output', str(report)], expected=2)
        self.assertEqual(report.read_text(), 'preserve')

    def test_map_fuel_revision_and_game_only_reference_options(self):
        options = parser().parse_args(['generate-map-fuel', 'source.scs', '--experimental'])
        self.assertEqual(options.revision, 2)
        self.assertEqual(options.petrol_reference, 'def/country/washington.sui')
        options = parser().parse_args(['generate-map-fuel', 'source.scs', '--experimental',
                                       '--petrol-reference', 'def/country/montana.sui'])
        self.assertEqual(options.petrol_reference, 'def/country/montana.sui')

    def test_map_fix_processor_options_and_dispatch(self):
        self.run_cli(['generate-map-fix', 'source.scs', '--experimental'], expected=2)
        options = parser().parse_args(['generate-map-fix', 'source.scs', '--experimental',
                                       '--processor', 'rest', '--processor', 'fuel',
                                       '--rest-radius', '750'])
        self.assertEqual(options.revision, 8)
        self.assertEqual(options.processor, ['rest', 'fuel'])
        self.assertEqual(options.rest_radius, 750)
        result = {'status': 'generated', 'output': 'generated.scs',
                  'workflow': {'work_dir': 'work'},
                  'planner': {'coverage': {'complete': True}}}
        with patch('ats_road_trip.bulk_run.generate_map_fix', return_value=result) as generate:
            output = self.run_cli(['generate-map-fix', 'source.scs', '--experimental',
                                   '--processor', 'rest', '--rest-radius', '750'])
        self.assertEqual(output['status'], 'generated')
        self.assertEqual(generate.call_args.kwargs['processors'], ['rest'])
        self.assertEqual(generate.call_args.kwargs['rest_radius'], 750)

    def test_map_fix_rejects_unimplemented_courier(self):
        self.run_cli(['generate-map-fix', 'source.scs', '--experimental',
                      '--processor', 'courier'], expected=2)

    def test_map_courier_analysis_needs_no_experimental_acknowledgment(self):
        result = {'status': 'reported_partial', 'report_path': 'work/audit.json',
                  'workflow': {'work_dir': 'work'},
                  'planner': {'coverage': {'complete': False}}}
        with patch('ats_road_trip.bulk_run.analyze_map', return_value=result) as analyze:
            output = self.run_cli(['analyze-map', 'source.scs', '--processor', 'courier'])
        self.assertTrue(output['analysis_only'])
        self.assertEqual(output['generated_mod_count'], 0)
        self.assertEqual(output['report_path'], 'work/audit.json')
        self.assertEqual(output['status'], 'reported_partial')
        self.assertEqual(analyze.call_args.kwargs['processors'], ['courier'])
        self.assertNotIn('revision', analyze.call_args.kwargs)
        self.run_cli(['analyze-map', 'source.scs'], expected=2)


if __name__ == '__main__':
    unittest.main()
