"""Truck edits compose with prior services and retain cross-sector ownership."""
from contextlib import ExitStack
import struct
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ats_road_trip.map_stack import plan_stack
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import ResourceStack
from ats_road_trip.processors import ProcessorConfig
from tests.test_bulk_fuel import SECTOR
from tests import test_map_stack as stack_fixtures
from tests.test_prefab_contexts import alias, model_change


class TruckStackCompositionTests(unittest.TestCase):
    def test_truck_reads_car_and_fuel_overlay_and_partitions_remote_edits_by_original_owner(self):
        with TemporaryDirectory() as directory, ExitStack() as manager:
            original,neighbor,packages,parts=stack_fixtures.MapStackTests().fixture(directory,manager)
            raw=ResourceStack(packages);observed=[]
            def car(stack,**kwargs):
                if kwargs['map_name']!='Source1':return {'coverage':{'complete':True,'blockers':[]}},{}
                data=stack.read(SECTOR)
                return {'coverage':{'complete':True,'blockers':[]},'composed_resource_paths':[SECTOR]}, {
                    SECTOR:model_change(data,'rts12345678'),
                    'def/world/prefab.rts12345678.sii':alias('rts12345678'),
                    'prefab/rtfix/rts12345678.ppd':b'fixture descriptor'}
            def truck(stack,**kwargs):
                self.assertIs(kwargs['ownership_stack'],raw)
                if kwargs['map_name']!='Source1':return {'coverage':{'complete':True,'blockers':[]}},{}
                local=stack.read(SECTOR);remote=stack.read(neighbor)
                observed.append((parse_sector(local).prefabs[0].details['model'],len(parse_sector(remote).services)))
                data=bytearray(local);prefab=parse_sector(local).prefabs[0]
                struct.pack_into('<I',data,prefab.offset+52,1)
                return {'coverage':{'complete':True,'blockers':[]},'composed_resource_paths':[SECTOR,neighbor]}, {
                    SECTOR:bytes(data),neighbor:remote}
            with patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',side_effect=car), \
                 patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',side_effect=truck):
                report,values=plan_stack(raw,ResourceStack(packages[:1]),parts=parts,
                    config=ProcessorConfig.from_preset('realistic',improve_truck_parking=True),game_version='1.61.3.18')
            self.assertEqual(observed,[(parse_sector(values[1][SECTOR]).prefabs[0].details['model'],2)])
            self.assertIn(SECTOR,values[1]);self.assertNotIn(SECTOR,values[2])
            self.assertIn(neighbor,values[2]);self.assertNotIn(neighbor,values[1])
            self.assertEqual(parse_sector(values[1][SECTOR]).prefabs[0].flags,1)
            self.assertEqual(len(parse_sector(values[2][neighbor]).services),2)
            self.assertEqual(report['contexts']['coverage']['aliases_seen'],2)
            self.assertTrue(report['improve_truck_parking'])

    def test_truck_only_stack_does_not_invoke_car_fuel_or_price_planning(self):
        with TemporaryDirectory() as directory, ExitStack() as manager:
            _,_,packages,parts=stack_fixtures.MapStackTests().fixture(directory,manager)
            with patch('ats_road_trip.map_stack.plan_map_fuel',side_effect=AssertionError('fuel ran')), \
                 patch('ats_road_trip.map_stack.build_policy',side_effect=AssertionError('prices ran')), \
                 patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',side_effect=AssertionError('car ran')), \
                 patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',return_value=({'coverage':{'complete':True,'blockers':[]}},{})) as truck:
                report,values=plan_stack(ResourceStack(packages),ResourceStack(packages[:1]),parts=parts,
                    config=ProcessorConfig.from_names(['rest'],parking_strategy='none',improve_truck_parking=True),game_version='1.61.3.18')
            self.assertEqual(truck.call_count,8)
            self.assertTrue(report['prices']['disabled'])
            self.assertEqual(values,[{} for _ in parts])
