"""Native truck-bank completion keeps one marker and the existing footprint."""
import unittest
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.rest_stops import _standalone
from ats_road_trip.truck_parking.extensions import (plan_bank_extension,
    extend_truck_standalone_polygon,polygon_retains_native)
from tests import test_truck_trigger as fixture

BANK=[(-3.,0.,2.),(15.,0.,2.),(15.,0.,20.),(-3.,0.,20.)]


class NativeTruckExtensionTests(unittest.TestCase):
    def test_concave_union_preserves_source_and_excludes_intervening_corner(self):
        vertices,proof=plan_bank_extension(fixture.NATIVE,BANK)
        native=[(p[0],p[2]) for p in fixture.NATIVE]
        result=[(p[0],p[2]) for p in vertices]
        self.assertTrue(polygon_retains_native(native,result))
        self.assertGreater(len(vertices),4)
        self.assertLess(proof['off_union_bridge_area'],.1)
        from ats_road_trip.rest_stops import _inside
        self.assertFalse(_inside((-2.,1.),result))
        self.assertFalse(_inside((-2.,21.),result))
        self.assertTrue(_inside((-2.,10.),result))

    def test_actual_writer_preserves_marker_identity_actions_visibility_and_all_node_ids(self):
        original,_,_=fixture.StandaloneTruckTriggerTests().native_sector(visibility=True,tagged=True)
        vertices,_=plan_bank_extension(fixture.NATIVE,BANK)
        result,report=extend_truck_standalone_polygon(original,source_uid=500,vertices=vertices,
            action_modes=fixture.MODES,uid_namespace='test-extension')
        before,after=parse_sector(original),parse_sector(result)
        self.assertEqual(before.item_count,after.item_count)
        self.assertEqual(before.visibility_children,after.visibility_children)
        self.assertLessEqual({n.uid for n in before.nodes},{n.uid for n in after.nodes})
        old=next(i for i in before.items if i.uid==500);new=next(i for i in after.items if i.uid==500)
        self.assertEqual([a['raw'] for a in _standalone(original,old)['actions']],
                         [a['raw'] for a in _standalone(result,new)['actions']])
        self.assertEqual(old.flags,new.flags)
        self.assertEqual(report['added_marker_count'],0)
        self.assertEqual(report['marker_count'],1)
        self.assertFalse(report['new_car_eligibility'])
        for item in before.items:
            if item.uid==500:continue
            copied=next(i for i in after.items if i.uid==item.uid)
            self.assertEqual(original[item.offset:item.end],result[copied.offset:copied.end])
        self.assertEqual((result,report),extend_truck_standalone_polygon(original,source_uid=500,vertices=vertices,
            action_modes=fixture.MODES,uid_namespace='test-extension'))

    def test_chained_bank_union_keeps_prior_completed_bank_and_original_node_ids(self):
        original=fixture.StandaloneTruckTriggerTests().native_sector()[0]
        first,_=plan_bank_extension(fixture.NATIVE,BANK)
        one,report=extend_truck_standalone_polygon(original,source_uid=500,vertices=first,
            action_modes=fixture.MODES,uid_namespace='chain')
        next_bank=[(10.,0.,20.),(25.,0.,20.),(25.,0.,25.),(10.,0.,25.)]
        second,_=plan_bank_extension(first,next_bank)
        two,report=extend_truck_standalone_polygon(one,source_uid=500,vertices=second,
            action_modes=fixture.MODES,uid_namespace='chain')
        self.assertLessEqual({n.uid for n in parse_sector(one).nodes},{n.uid for n in parse_sector(two).nodes})
        self.assertTrue(polygon_retains_native([(p[0],p[2]) for p in first],[(p[0],p[2]) for p in second]))
        self.assertEqual(parse_sector(two).item_count,1)

    def test_car_mixed_actions_custom_parameters_or_cropped_source_are_rejected(self):
        vertices,_=plan_bank_extension(fixture.NATIVE,BANK)
        original=fixture.StandaloneTruckTriggerTests().native_sector()[0]
        mixed={**fixture.MODES,fixture.TRUCK:{'truck','bus','car'}}
        with self.assertRaisesRegex(ValueError,'car eligibility'):
            extend_truck_standalone_polygon(original,source_uid=500,vertices=vertices,action_modes=mixed,uid_namespace='test')
        custom=fixture.StandaloneTruckTriggerTests().native_sector(custom=True)[0]
        with self.assertRaisesRegex(ValueError,'unmodified'):
            extend_truck_standalone_polygon(custom,source_uid=500,vertices=vertices,action_modes=fixture.MODES,uid_namespace='test')
        cropped=[(1.,0.,1.),(10.,0.,1.),(10.,0.,10.),(1.,0.,10.)]
        with self.assertRaisesRegex(ValueError,'retain every original'):
            extend_truck_standalone_polygon(original,source_uid=500,vertices=cropped,action_modes=fixture.MODES,uid_namespace='test')

    def test_unrelated_disconnected_region_and_unproven_grade_cannot_extend(self):
        with self.assertRaisesRegex(ValueError,'overlapping'):
            plan_bank_extension(fixture.NATIVE,fixture.BANK)
        steep=[(x,x*.2,z) for x,_,z in fixture.NATIVE]
        with self.assertRaisesRegex(ValueError,'grade'):
            plan_bank_extension(steep,[(x,x*.2,z) for x,_,z in BANK])

    def test_nonplanar_native_boundary_keeps_source_heights_and_rejects_floating_extension(self):
        source=[(0.,0.,0.),(30.,.3,0.),(30.,.1,22.),(0.,0.,22.)]
        vertices,proof=plan_bank_extension(source,BANK)
        self.assertIsNone(proof['source_plane_gradient'])
        original=fixture.StandaloneTruckTriggerTests().native_sector()[0]
        floating=[(x,y+100.,z) for x,y,z in vertices]
        with self.assertRaisesRegex(ValueError,'terrain envelope'):
            extend_truck_standalone_polygon(original,source_uid=500,vertices=floating,
                action_modes=fixture.MODES,uid_namespace='floating')

    def test_boundary_interval_check_rejects_notch_cropping_even_when_source_vertices_fit(self):
        native=[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]
        notch=[(-1.,-1.),(11.,-1.),(11.,11.),(7.,11.),(7.,5.),(3.,5.),(3.,11.),(-1.,11.)]
        self.assertFalse(polygon_retains_native(native,notch))
