"""Selection, independent planning, and deterministic overlay composition."""

from types import SimpleNamespace
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.processors import Processor, ProcessorConfig, run_processors
from tests.test_rest_stops import SECTOR, source as rest_source


class ProcessorTests(unittest.TestCase):
    def test_config_requires_distinct_supported_processors_and_finite_radius(self):
        self.assertEqual(ProcessorConfig().enabled, (Processor.FUEL,))
        self.assertEqual(ProcessorConfig.from_names(['rest']).enabled, (Processor.REST,))
        self.assertEqual(ProcessorConfig.from_names(['rest'], rest_radius=0).rest_radius, 0)
        for names, problem in (([], 'at least one'), (['fuel', 'fuel'], 'repeated'),
                               (['courier'], 'not implemented')):
            with self.subTest(names=names), self.assertRaisesRegex(ValueError, problem):
                ProcessorConfig.from_names(names)
        for radius in (-1, float('inf'), float('nan'), True):
            with self.subTest(radius=radius), self.assertRaisesRegex(ValueError, 'radius'):
                ProcessorConfig.from_names(['rest'], rest_radius=radius)

    def test_rest_only_does_not_plan_fuel_and_receives_configured_radius(self):
        seen = []

        def rest(stack, *, map_packages, map_name, radius, resource_overrides):
            seen.append((map_packages, map_name, radius, resource_overrides))
            return {'coverage': {'blockers': []}}, {'map/usa/rest.base': b'rest'}

        module = SimpleNamespace(plan_rest_stops=rest)
        with patch.dict(sys.modules, {'ats_road_trip.rest_stops': module}), \
             patch('ats_road_trip.processors._fuel_plan', side_effect=AssertionError('fuel ran')):
            result = run_processors(None, None, source='source.scs', map_name='Test',
                                    config=ProcessorConfig.from_names(['rest'], rest_radius=750))
        self.assertEqual(seen, [({'source.scs'}, 'Test', 750, {})])
        self.assertEqual(result.resources, {'map/usa/rest.base': b'rest'})
        self.assertTrue(result.coverage['complete'])

    def test_mixed_plans_in_canonical_order_with_composed_overlay(self):
        calls = []

        def fuel(*args, **kwargs):
            calls.append('fuel')
            return {'coverage': {'blockers': []}}, {'map/usa/sec+0000+0000.base': b'fuel'}

        def rest(stack, *, map_packages, map_name, radius, resource_overrides):
            calls.append('rest')
            self.assertEqual(resource_overrides, {'map/usa/sec+0000+0000.base': b'fuel'})
            return {'coverage': {'blockers': []},
                    'composed_resource_paths': ['map/usa/sec+0000+0000.base']}, \
                   {'map/usa/sec+0000+0000.base': b'fuel+rest'}

        module = SimpleNamespace(plan_rest_stops=rest)
        with patch.dict(sys.modules, {'ats_road_trip.rest_stops': module}), \
             patch('ats_road_trip.processors._fuel_plan', side_effect=fuel):
            result = run_processors(None, None, source='source.scs', map_name='Test',
                                    config=ProcessorConfig.from_names(['rest', 'fuel']))
        self.assertEqual(calls, ['fuel', 'rest'])
        self.assertEqual(result.resources['map/usa/sec+0000+0000.base'], b'fuel+rest')
        self.assertTrue(result.coverage['complete'])

    def test_undeclared_overlap_and_any_processor_blocker_prevent_completion(self):
        module = SimpleNamespace(plan_rest_stops=lambda *args, **kwargs:
                                 ({'coverage': {'blockers': [{'reason': 'unknown rest'}]}},
                                  {'same.path': b'rest'}))
        with patch.dict(sys.modules, {'ats_road_trip.rest_stops': module}), \
             patch('ats_road_trip.processors._fuel_plan', return_value=(
                 {'coverage': {'blockers': [{'reason': 'unknown fuel'}]}},
                 {'same.path': b'fuel'})):
            result = run_processors(None, None, source='source.scs', map_name='Test',
                                    config=ProcessorConfig.from_names(['fuel', 'rest']))
        self.assertFalse(result.coverage['complete'])
        self.assertEqual(len(result.blockers), 3)
        self.assertEqual({b['processor'] for b in result.blockers}, {'fuel', 'rest'})
        self.assertTrue(any(b.get('area') == 'resource_collision' for b in result.blockers))

    def test_explicit_incomplete_coverage_blocks_even_without_details(self):
        module = SimpleNamespace(plan_rest_stops=lambda *args, **kwargs:
                                 ({'coverage': {'complete': False, 'blockers': []}},
                                  {'map/usa/rest.base': b'rest'}))
        with patch.dict(sys.modules, {'ats_road_trip.rest_stops': module}):
            result = run_processors(None, None, source='source.scs', map_name='Test',
                                    config=ProcessorConfig.from_names(['rest']))
        self.assertFalse(result.coverage['complete'])
        self.assertEqual(result.blockers[0]['area'], 'coverage')

    def test_real_rest_planner_composes_prior_sector_bytes(self):
        fixture = rest_source()
        # Simulate an earlier processor's valid sector edit that rest does not
        # itself touch. The final sector must retain that byte and the rest edit.
        overlay = bytearray(fixture[SECTOR])
        flag_offset = parse_sector(fixture[SECTOR]).prefabs[0].offset + 52
        overlay[flag_offset] = 1
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for path, contents in fixture.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(contents)
            with Package(root) as package:
                stack = ResourceStack([package])
                with patch('ats_road_trip.processors._fuel_plan', return_value=(
                    {'coverage': {'complete': True, 'blockers': []}},
                    {SECTOR: bytes(overlay)})):
                    result = run_processors(stack, stack, source=str(package.path),
                                            map_name='Fixture',
                                            config=ProcessorConfig.from_names(['rest', 'fuel']))
        self.assertTrue(result.coverage['complete'], result.blockers)
        self.assertEqual(result.resources[SECTOR][flag_offset], 1)
        self.assertNotEqual(result.resources[SECTOR], bytes(overlay))
        self.assertIn(SECTOR, result.reports['rest']['composed_resource_paths'])


if __name__ == '__main__':
    unittest.main()
