"""Diagnostic parameter isolation uses only authored PPD fixtures."""
import struct
import unittest
from ats_road_trip.station_parking.trigger import append_car_parking_polygon,partial_activation_diagnostic
from ats_road_trip.rest_stops import inspect_rest_triggers
from tests.test_station_geometry import station_descriptor

class ActivationDiagnosticTests(unittest.TestCase):
    def test_only_contact_flag_changes_and_geometry_is_identical(self):
        before,report=append_car_parking_polygon(station_descriptor(),[(0.,0.,0.),(3.,0.,0.),(3.,0.,6.),(0.,0.,6.)])
        after,diagnostic=partial_activation_diagnostic(before,report['group_id'])
        header=struct.unpack_from('<24I',before)
        offsets={header[21]+i*48+24 for i in range(header[9])}
        self.assertEqual({i for i,(a,b) in enumerate(zip(before,after)) if a!=b},offsets)
        a,b=inspect_rest_triggers(before)[0],inspect_rest_triggers(after)[0]
        self.assertEqual(a['vertices'],b['vertices']);self.assertEqual(b['flags'],4)
        self.assertEqual(report['parameters']['range'],3.)
        self.assertEqual(diagnostic['engine_vehicle_shape'],'Unknown')
        with self.assertRaisesRegex(ValueError,'non-partial'):
            partial_activation_diagnostic(after,report['group_id'])

    def test_missing_group_wrong_version_and_boolean_are_refused(self):
        before,report=append_car_parking_polygon(station_descriptor(),[(0.,0.,0.),(3.,0.,0.),(3.,0.,6.),(0.,0.,6.)])
        for group in (True,-1,2**32,99):
            with self.subTest(group=group),self.assertRaises(ValueError):partial_activation_diagnostic(before,group)
        broken=bytearray(before);struct.pack_into('<I',broken,0,24)
        with self.assertRaises(ValueError):partial_activation_diagnostic(bytes(broken),report['group_id'])

if __name__=='__main__':unittest.main()
