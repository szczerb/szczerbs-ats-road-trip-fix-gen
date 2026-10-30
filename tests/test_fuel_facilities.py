"""Whole-facility suitability reuses resources and real graph/lot evidence."""
from dataclasses import FrozenInstanceError, replace
import unittest

from ats_road_trip.fuel_selection import FuelSelectionConfig, classify_groups
from ats_road_trip.fuel_selection.facilities import CompanyLotEvidence, FacilityContext, field_approach_measurements


DEFAULT = 92136531712
CHEMRON = '/prefab/gas/nm_gas_station1_chemron.pmd'
TRUCKSTOP = '/prefab/gas/nm_truckstop1_depot.pmd'
CASTORES = '/prefab/empresas/cedis/castores1.pmd'
GENERIC = '/prefab/gas/us_gas_station_trigger_only.pmd'
FIELD = '/prefab/depots/custom/us_custom_depot_field.pmd'


def facility_config(unknown='include'):
    return FuelSelectionConfig(mode='realistic', unknown=unknown, classifier='facilities')


def classify(*, model_desc=GENERIC, descriptor_sha256='0'*64, variant=DEFAULT,
             company_uids=(), garage_indices=(), context=None, unknown='include', indices=(0,1), **overrides):
    return classify_groups(facility_config(unknown), descriptor='prefab/test/layout.ppd',
                           descriptor_sha256=descriptor_sha256, model_desc=model_desc,
                           variant=variant, parts=(), additional_parts=(),
                           gas_trucks=[{'index':i} for i in indices], company_uids=company_uids,
                           garage_indices=garage_indices, facility_context=context, **overrides)


class FuelFacilityTests(unittest.TestCase):
    def test_accepted_public_families_include_all_truck_groups(self):
        families = [
            (CHEMRON, '3d986bd488fb034f21043540bf9cca3f5966503d8715c6e70612bb722dea5fca', DEFAULT, (0,1)),
            (TRUCKSTOP, '0e7954cd155d6019d04c70dd73623ce7407a9378f742003a2a17026a5f400519', 97903579674243, (0,1)),
            (CHEMRON, 'e0a9084f767216f1611b30ec1f8729dd00a490ad520fc2002072527b5edc4d8b', DEFAULT, (2,)),
        ]
        for model, digest, variant, indices in families:
            with self.subTest(model=model, digest=digest):
                rows = classify(model_desc=model, descriptor_sha256=digest, variant=variant,
                                indices=indices, company_uids=(999,), context=FacilityContext(native_car_locator_count=2))
                self.assertTrue(all(row['selected_for_addition'] for row in rows))
                self.assertTrue(all(row['facility_class'].startswith('public_') for row in rows))
                self.assertTrue(all(not row['provisional'] for row in rows))
                self.assertTrue(all(row['native_car_locator_count'] == 2 for row in rows))

    def test_logistics_review_requires_actual_company_edge_and_exact_source(self):
        options = {'model_desc':CASTORES, 'descriptor_sha256':'b130fdfb51503158d55b06cae22a7f603f23269f1cedf5ea50c83236cdb1d79d'}
        rows = classify(**options, company_uids=(123,))
        self.assertTrue(all(row['facility_class']=='logistics_yard' and not row['selected_for_addition'] for row in rows))
        self.assertTrue(all(row['role']=='uncertain' and row['selected_for_addition'] for row in classify(**options)))
        self.assertTrue(all(row['role']=='uncertain' for row in classify(model_desc=CASTORES, company_uids=(123,))))

    def test_garage_excludes_entire_facility(self):
        rows = classify(garage_indices={0})
        self.assertTrue(all(row['facility_class']=='truck_garage' and not row['selected_for_addition'] for row in rows))

    def test_company_names_depot_filenames_and_generic_triggers_do_not_exclude(self):
        for model in (GENERIC, '/prefab/gas/nm_gas_station1_depot.pmd', '/prefab/test/depot_fuel.pmd'):
            rows=classify(model_desc=model, company_uids=(123,))
            self.assertTrue(all(row['facility_class']=='uncertain' and row['selected_for_addition'] for row in rows))

    def test_agricultural_inference_requires_layout_and_all_pumps_inside_actual_company_lot(self):
        evidence = CompanyLotEvidence(123, 456, FIELD, '6387b090f84b102ef80b7e2c64c0590926ce6778b638cd2e517566a26c435992', (0,1), (3,), 'Authored actual Company lot polygon', variant=30421486)
        rows=classify(context=FacilityContext((evidence,)))
        self.assertTrue(all(row['facility_class']=='agricultural_equipment' and not row['selected_for_addition'] for row in rows))
        self.assertTrue(all(row['provisional'] and row['confidence']=='low' for row in rows))
        for altered in (replace(evidence, matched_spawn_indices=()), replace(evidence, matched_spawn_indices=(0,)),
                        replace(evidence, model_desc='/prefab/test/public_forecourt.pmd'), replace(evidence, parts=(12,)),
                        replace(evidence, variant=42)):
            rows=classify(context=FacilityContext((altered,)))
            self.assertTrue(all(row['role']=='uncertain' and row['selected_for_addition'] for row in rows))

    def test_reviewed_field_approach_matches_measured_ranch_context_not_nearby_public_pump(self):
        entrance=(3109.17578125,5.98828125,43059.16796875)
        inner=(3111.25390625,5.98828125,43068.94921875)
        pumps={0:(3108.4140625,6.1015625,43048.28125)}
        indices, measurements, axis=field_approach_measurements(entrance,inner,pumps)
        self.assertEqual(indices,(0,))
        self.assertAlmostEqual(measurements[0][1],10.8,delta=.1)
        self.assertLess(abs(measurements[0][2]),3)
        evidence=CompanyLotEvidence(123,456,FIELD,
            '6387b090f84b102ef80b7e2c64c0590926ce6778b638cd2e517566a26c435992',indices,(),
            'Measured entrance approach, not lot containment',variant=30421486,
            relationship='bounded_entrance_corridor',entrance_world_xyz=entrance,
            approach_axis_xz=axis,pump_measurements=measurements)
        rows=classify(indices=(0,),context=FacilityContext((evidence,)))
        self.assertFalse(rows[0]['selected_for_addition'])
        self.assertIn('entrance approach',rows[0]['reason'])
        self.assertEqual(rows[0]['contextual_company_lots'][0]['relationship'],'bounded_entrance_corridor')
        # Similar nearby positions are deliberately outside the measured narrow
        # corridor: lateral public forecourt, distant road, inner yard, overpass.
        for point in ((3120,6,43048),(3106,6,43030),(3110,6,43064),(3108.414,12,43048.281)):
            self.assertFalse(field_approach_measurements(entrance,inner,{0:point})[0])
        for wrong in (replace(evidence,matched_spawn_indices=()),replace(evidence,descriptor_sha256='0'*64)):
            self.assertTrue(classify(indices=(0,),context=FacilityContext((wrong,)))[0]['selected_for_addition'])

    def test_unknown_treatment_and_missing_context_are_explicit(self):
        rows=classify(unknown='skip', context=FacilityContext(unavailable_evidence=('unsupported context polygon',)))
        self.assertTrue(all(not row['selected_for_addition'] for row in rows))
        self.assertTrue(all(row['provisional'] and row['context_evidence_unavailable'] for row in rows))
        self.assertTrue(all(row['selected_for_addition'] for row in classify()))

    def test_context_builder_transforms_real_source_graph_controls(self):
        from dataclasses import replace
        from types import SimpleNamespace
        from unittest.mock import patch
        from ats_road_trip.fuel_selection.facilities import FacilityContextIndex
        from ats_road_trip.map_sector import MapItem
        from ats_road_trip.sii import parse_units
        from tests.test_fuel_matching import fixture
        fuel_ppd, fuel_parent, fuel_nodes, services=fixture([((2.,0.,3.),0)])
        field_ppd, field_parent, field_nodes, _=fixture([],control=((0.,0.,0.),(0.,0.,-10.)),origin=0)
        field_parent=replace(field_parent,uid=1100,details={**field_parent.details,'model':42,
            'variant':30421486,'parts':(),'nodes':tuple(uid+1000 for uid in field_parent.details['nodes'])})
        nodes=dict(fuel_nodes)
        for uid,node in field_nodes.items():
            nodes[uid+1000]=replace(node,uid=uid+1000,forward=1100)
        company=MapItem(6,900,0,0,0,{'prefab':1100,'node':1200})
        items={1100:('field.base',field_parent),900:('field.base',company)}
        items.update({service.uid:('station.base',service) for service in services})
        unit=parse_units('prefab_model: prefab.field {\n model_desc: "'+FIELD+'"\n prefab_desc: "/field.ppd"\n}')[0]
        class Stack:
            packages=[]
            resources={'field.ppd':(SimpleNamespace(path='authored-source'),None)}
            def read(self,path):return field_ppd
        # The source-family pin is substituted only for authored test bytes;
        # the actual coordinate transform and classification still run.
        digest=SimpleNamespace(hexdigest=lambda:'6387b090f84b102ef80b7e2c64c0590926ce6778b638cd2e517566a26c435992')
        with patch('ats_road_trip.fuel_selection.facilities.hashlib.sha256',return_value=digest):
            index=FacilityContextIndex(Stack(),items,{42:(unit,None,None)},lambda uid,path=None:nodes[uid])
            context=index.for_station(model_desc=GENERIC,gas_trucks=[{'index':0}],mapping={0:services[0].uid},native_car_locator_count=0)
        self.assertEqual(len(context.company_lots),1)
        self.assertEqual(context.company_lots[0].relationship,'bounded_entrance_corridor')
        self.assertFalse(classify(indices=(0,),context=context)[0]['selected_for_addition'])

    def test_stale_reviewed_rule_is_provisional_in_facility_mode(self):
        from ats_road_trip.fuel_selection import FuelLayoutRule
        from tests.test_fuel_selection import rule
        config=replace(facility_config(),rules=(FuelLayoutRule.from_dict(rule()),))
        rows=classify_groups(config,descriptor='prefab/test/station.ppd',descriptor_sha256='0'*64,
            model_desc='/prefab/test/station.pmd',variant=0,parts=(),additional_parts=('first','second'),
            gas_trucks=[{'index':0}])
        self.assertTrue(rows[0]['reviewed_rule_drift'])
        self.assertTrue(rows[0]['provisional'] and rows[0]['selected_for_addition'])
        self.assertEqual(rows[0]['facility_class'],'uncertain')

    def test_configuration_roundtrip_and_historical_shape(self):
        config=facility_config(); data=config.to_dict()
        self.assertEqual(data['classifier'], 'facilities')
        self.assertEqual(FuelSelectionConfig.from_dict(data), config)
        self.assertNotIn('classifier', FuelSelectionConfig().summary())
        self.assertNotIn('classifier', FuelSelectionConfig().to_dict())
        with self.assertRaises(ValueError): FuelSelectionConfig(classifier='facilities')
        with self.assertRaises(ValueError): FuelSelectionConfig(mode='realistic',classifier='typo')
        with self.assertRaises(FrozenInstanceError): config.classifier='reviewed'
