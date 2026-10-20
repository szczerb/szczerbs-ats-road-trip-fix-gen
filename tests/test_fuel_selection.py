"""Selective suitability policy and strict source pins use authored fixtures."""
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ats_road_trip.fuel_selection import (FuelSelectionConfig,
                                         classify_groups, load_fuel_selection_config)


def group(index=0, role='public_car'):
    return {'spawn_index': index, 'role': role, 'confidence': 'medium',
            'reason': 'Authored public forecourt / truck-lane distinction',
            'evidence': 'Observed locally: reviewed authored fixture geometry'}


def rule(data=b'fixture', roles=('public_car',), **overrides):
    return {'id': 'fixture', 'descriptor': 'prefab/test/station.ppd',
            'descriptor_sha256': hashlib.sha256(data).hexdigest(),
            'model_desc': '/prefab/test/station.pmd', 'variant': 0, 'parts': [],
            'additional_parts': ['first', 'second'],
            'groups': [group(index, role) for index, role in enumerate(roles)], **overrides}


def config(*rules, unknown='skip'):
    return FuelSelectionConfig.from_dict({'schema_version': 1, 'mode': 'realistic',
                                         'unknown': unknown, 'rules': list(rules)})


class FuelSelectionTests(unittest.TestCase):
    def classify(self, selected, **overrides):
        return classify_groups(selected, descriptor='prefab/test/station.ppd',
                               descriptor_sha256=hashlib.sha256(b'fixture').hexdigest(),
                               model_desc='/prefab/test/station.pmd', variant=0, parts=(),
                               additional_parts=('first', 'second'),
                               gas_trucks=[{'index': i} for i in range(4)], **overrides)

    def test_mixed_layout_preserves_uncertainty_and_reasons(self):
        result = self.classify(config(rule(roles=('public_car', 'truck_lane', 'fleet_yard', 'uncertain'))))
        self.assertEqual([r['selected_for_addition'] for r in result], [True, False, False, False])
        self.assertTrue(all(r['reason'] and r['evidence'] and r['rule_id'] == 'fixture' for r in result))
        result = self.classify(config(rule(roles=('public_car', 'truck_lane', 'fleet_yard', 'uncertain')), unknown='include'))
        self.assertEqual([r['selected_for_addition'] for r in result], [True, False, False, True])

    def test_same_parent_company_is_context_not_ownership_proof(self):
        result = self.classify(config(), company_uids=(123,))
        self.assertTrue(all(r['role'] == 'uncertain' for r in result))
        self.assertTrue(all(r['same_parent_company_uids'] == ['0x7b'] for r in result))
        self.assertIn('not ownership', result[0]['evidence'])
        selected = config(rule(company_linked=False), rule(id='company', roles=('truck_lane',), company_linked=True))
        self.assertEqual(self.classify(selected)[0]['role'], 'public_car')
        self.assertEqual(self.classify(selected, company_uids=(123,))[0]['role'], 'truck_lane')

    def test_unknown_default_skip_and_explicit_include(self):
        self.assertTrue(all(not r['selected_for_addition'] for r in self.classify(config())))
        self.assertTrue(all(r['selected_for_addition'] for r in self.classify(config(unknown='include'))))
        result = self.classify(config(unknown='include'), garage_indices={0})
        self.assertFalse(result[0]['selected_for_addition'])
        self.assertIn('garage facility', result[0]['reason'])

    def test_source_pin_drift_blocks(self):
        for changes in ({'descriptor_sha256': '0' * 64}, {'variant': 1}, {'parts': [5]},
                        {'additional_parts': []}, {'model_desc': '/other.pmd'}):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'drift'):
                self.classify(config(rule(**changes)))
        with self.assertRaisesRegex(ValueError, 'non-truck'):
            self.classify(config(rule(groups=[group(50)])))

    def test_config_is_immutable(self):
        selected = config(rule())
        with self.assertRaises(FrozenInstanceError):
            selected.mode = 'broad'
        with self.assertRaises(FrozenInstanceError):
            selected.rules[0].groups[0].role = 'truck_lane'

    def test_schema_rejects_unknown_fields_and_bad_types(self):
        valid = {'schema_version': 1, 'mode': 'realistic', 'unknown': 'skip', 'rules': [rule()]}
        cases = [{**valid, 'schema_version': True}, {**valid, 'schema_version': 2},
                 {**valid, 'mode': 'typo'}, {**valid, 'unknown': 'guess'}, {**valid, 'extra': 1},
                 {**valid, 'rules': {}}, {**valid, 'mode': 'broad'}]
        for delta in ({'descriptor': '/absolute.ppd'}, {'descriptor': 'prefab/../bad.ppd'},
                      {'descriptor_sha256': 'bad'}, {'variant': True}, {'parts': [False]},
                      {'additional_parts': [2]}, {'groups': [group(), group()]},
                      {'company_linked': 1}, {'groups': [{**group(), 'role': 'diesel_only'}]},
                      {'groups': [{**group(), 'confidence': 'proven'}]}, {'unknown_field': 1}):
            cases.append({**valid, 'rules': [rule(**delta)]})
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                FuelSelectionConfig.from_dict(bad)
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            config(rule(), rule(id='other'))
        with self.assertRaisesRegex(ValueError, 'Duplicate.*id'):
            config(rule(company_linked=True), rule(company_linked=False))
        with self.assertRaises(ValueError):
            FuelSelectionConfig(rules=[])

    def test_loader_rejects_duplicate_json_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            path.write_text('{"schema_version":1,"mode":"broad","mode":"realistic","unknown":"skip","rules":[]}')
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON'):
                load_fuel_selection_config(path)
            path.write_text(json.dumps({'schema_version':1, 'mode':'realistic', 'unknown':'skip', 'rules':[]}))
            self.assertEqual(load_fuel_selection_config(path), config())
