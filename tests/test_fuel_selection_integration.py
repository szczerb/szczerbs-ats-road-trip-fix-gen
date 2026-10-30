"""Public selective-fuel configuration through real pipeline and archives."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

from ats_road_trip import bulk_run
from ats_road_trip.cli import parser
from ats_road_trip.fuel_selection import FuelSelectionConfig
from ats_road_trip.processors import ProcessorConfig
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.ppd import inspect_ppd
from tests.test_bulk_fuel import resources, SECTOR, PPD
from tests import test_bulk_run as bulk_fixtures
from tests.test_bulk_run import archive


class FuelSelectionIntegrationTests(unittest.TestCase):
    def setUp(self):
        bulk_fixtures.BulkRunTests.setUp(self)
        self.fixture = resources([((2., 0., 3.), 0), ((9., 0., 3.), 0)])
        self.fixture['def/data_context.sii'] = b'SiiNunit\n{\ndata_context : context.fixture {\n target_data[]: prefab.02003\n tags[]: gas_station\n}\n}\n'
        # A source-country omission exercises price repair independently of
        # which station pumps the selection policy admits.
        self.fixture['def/country/fixture.sui'] = b'country_data: country.data.fixture {\n fuel_price: 2.0\n}\n'
        archive(self.source, self.fixture)
        self.config = FuelSelectionConfig.from_dict({
            'schema_version': 1, 'mode': 'realistic', 'unknown': 'skip', 'rules': [{
                'id': 'authored-mixed-layout', 'descriptor': PPD,
                'descriptor_sha256': hashlib.sha256(self.fixture[PPD]).hexdigest(),
                'model_desc': '/prefab/test/station.pmd', 'variant': 0,
                'parts': [], 'additional_parts': ['first', 'second'],
                'groups': [dict(spawn_index=i, role=role, confidence='medium',
                                reason='Authored role comparison', evidence='Authored fixture, not game evidence')
                           for i, role in enumerate(('public_car', 'truck_lane'))]
            }]})

    def generate(self, stamp, selection=FuelSelectionConfig()):
        with patch.object(bulk_run, 'REPO_ROOT', self.root):
            return bulk_run.generate_map_fix(self.source, game_dir=self.game,
                    processors=('fuel',), run_id=stamp, fuel_selection=selection)

    def test_full_workflow_selects_one_pump_preserves_prices_and_context(self):
        broad = self.generate('2026-10-21_01-00-01')
        selected = self.generate('2026-10-21_01-00-02', self.config)
        with zipfile.ZipFile(broad['output']) as a, zipfile.ZipFile(selected['output']) as b:
            self.assertIsNone(a.testzip()); self.assertIsNone(b.testzip())
            car = lambda z: [x for x in parse_sector(z.read(SECTOR)).services if x.flags & 0x4000]
            self.assertEqual(len(car(a)), 2); self.assertEqual(len(car(b)), 1)
            self.assertEqual(a.read('def/country/fixture.sui'), b.read('def/country/fixture.sui'))
            self.assertIn(b'petrol_price', b.read('def/country/fixture.sui'))
            self.assertIn('display_name: "SELECT FUEL |', b.read('manifest.sii').decode())
            self.assertTrue(b.read('mod_description.txt').decode().startswith('SELECT FUEL'))
            self.assertTrue(Path(selected['output']).name.startswith('select-fuel-'))
            report = json.loads(b.read('road_trip_fix_report.json'))
            context = report['processor_reports']['context_preservation']
            self.assertEqual(context['coverage']['aliases_classified'], 1)
            ppds = [b.read(n) for n in b.namelist() if n.endswith('.ppd')]
            self.assertEqual(sum(inspect_ppd(x)['fuel']['flags_one_count'] for x in ppds), 1)

    def test_explicit_broad_and_default_generate_identical_archive_bytes(self):
        a = self.generate('2026-10-21_01-00-03')
        b = self.generate('2026-10-21_01-00-04', FuelSelectionConfig(mode='broad'))
        self.assertEqual(Path(a['output']).read_bytes(), Path(b['output']).read_bytes())

    def test_analysis_propagates_selection_and_never_generates_a_package(self):
        with patch.object(bulk_run, 'REPO_ROOT', self.root), patch.object(bulk_run, 'write_mod') as writer:
            report = bulk_run.analyze_map(self.source, game_dir=self.game, processors=('fuel',),
                    run_id='2026-10-21_01-00-05', fuel_selection=self.config)
        writer.assert_not_called()
        fuel = report['planner']['processor_reports']['fuel']
        self.assertEqual(fuel['coverage']['policy_selected_truck_points'], 1)
        self.assertEqual(fuel['coverage']['policy_skipped_truck_points'], 1)

    def test_configuration_cannot_be_ignored_by_nonfuel_processor(self):
        with self.assertRaisesRegex(ValueError, 'requires the fuel'):
            ProcessorConfig.from_names(['rest'], fuel_selection=self.config)
        with self.assertRaisesRegex(ValueError, 'FuelSelectionConfig'):
            ProcessorConfig.from_names(['fuel'], fuel_selection='realistic')

    def test_public_cli_selection_options_exist_and_are_mutually_exclusive(self):
        for command in ('generate-map-fuel', 'generate-map-fix', 'analyze-map'):
            extra = [] if command == 'generate-map-fuel' else ['--processor', 'fuel']
            arguments = [command, 'source.scs', *extra]
            self.assertEqual(parser().parse_args([*arguments, '--fuel-policy', 'realistic']).fuel_policy, 'realistic')
            self.assertEqual(parser().parse_args([*arguments, '--fuel-selection-json', 'policy.json']).fuel_selection_json, 'policy.json')
            with patch('sys.stderr'), self.assertRaises(SystemExit):
                parser().parse_args([*arguments, '--fuel-policy', 'broad', '--fuel-selection-json', 'policy.json'])


if __name__ == '__main__':
    unittest.main()
