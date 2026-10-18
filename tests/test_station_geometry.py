import math
import struct
import unittest

from ats_road_trip.station_geometry import ParkingParameters, inspect_station_map, propose_unmarked_parking, _within


def station_descriptor(*, malformed=None):
    # Original synthetic fixture: rectangular lot, a canopy over a gas locator,
    # one shop building, and a green verge. No supplied game data is embedded.
    polygons = [
        (1,[(-20.,0.,20.),(30.,0.,20.),(30.,0.,-30.),(-20.,0.,-30.)]),
        (2,[(-8.,0.,6.),(0.,0.,6.),(0.,0.,-4.),(-8.,0.,-4.)]),
        (2,[(-10.,0.,-10.),(18.,0.,-10.),(18.,0.,-20.),(-10.,0.,-20.)]),
        (4,[(20.,0.,-10.),(25.,0.,-10.),(25.,0.,-20.),(20.,0.,-20.)]),
    ]
    records=[]
    for color,vertices in polygons:
        start=len(records)
        for i,p in enumerate(vertices):
            flags=0xd00|(color<<17)|0x100000
            records.append(struct.pack('<II3f6iI',flags,0,*p,start+(i-1)%4,start+(i+1)%4,-1,-1,-1,-1,2))
    gas=struct.pack('<7fII',-4.,0.1,0.,1.,0.,0.,0.,3,0)
    start=96+len(gas)
    end=start+48*len(records)
    h=[0]*24
    h[0],h[5],h[8]=25,1,len(records)
    h[12:24]=[96]*5+[start]*4+[end]*3
    raw=struct.pack('<24I',*h)+gas+b''.join(records)
    if malformed is not None:
        raw=bytearray(raw); malformed(raw,start)
    return bytes(raw)


class StationGeometryTests(unittest.TestCase):
    def test_map_colors_exclude_no_outline_bit_and_validate_canopy(self):
        geometry=inspect_station_map(station_descriptor())
        self.assertEqual([p['color'] for p in geometry['polygons']],[1,2,2,4])
        result=propose_unmarked_parking(station_descriptor())
        dark=[p for p in result['geometry']['polygons'] if p['color']==2]
        self.assertEqual(dark[0]['interpretation'],'canopy_proxy_contains_gas_locator')
        self.assertEqual(dark[1]['interpretation'],'building_proxy_without_gas_locator')
        self.assertTrue(all(c['building_map_polygon']==8 for c in result['candidates']))

    def test_reproducible_real_candidates_have_disclosed_rejections_and_approach(self):
        data=station_descriptor()
        first=propose_unmarked_parking(data)
        self.assertEqual(first,propose_unmarked_parking(data))
        self.assertIsNotNone(first['selected'])
        self.assertTrue(any(c['rejection_reasons'] for c in first['candidates']))
        selected=first['selected']
        self.assertFalse(selected['rejection_reasons'])
        self.assertGreaterEqual(selected['pump_clearance'],6.)
        self.assertEqual(len(selected['polygon_xz']),4)
        self.assertEqual(len(selected['approach_xz']),4)
        self.assertIn('unresolved',selected['height_status'])
        self.assertEqual(first['method'],'unmarked_map_geometry')

    def test_larger_obstacle_margin_rejects_all_without_truck_fallback(self):
        result=propose_unmarked_parking(station_descriptor(),ParkingParameters(obstacle_margin=50.))
        self.assertIsNone(result['selected'])
        self.assertTrue(result['blockers'])
        self.assertTrue(all(c['rejection_reasons'] for c in result['candidates']))
        self.assertNotIn('truck',str(result['candidates']))

    def test_no_building_proxy_produces_explicit_blocker(self):
        data=bytearray(station_descriptor())
        h=struct.unpack_from('<24I',data)
        for i in range(h[8]):
            flags=struct.unpack_from('<I',data,h[20]+48*i)[0]
            struct.pack_into('<I',data,h[20]+48*i,(flags&~(7<<17))|(1<<17))
        result=propose_unmarked_parking(bytes(data))
        self.assertIsNone(result['selected'])
        self.assertTrue(result['blockers'])

    def test_rejects_nonfinite_and_broken_map_topology(self):
        corruptions=[lambda d,o:struct.pack_into('<f',d,o+8,float('nan')),
                     lambda d,o:struct.pack_into('<i',d,o+20,999),
                     lambda d,o:struct.pack_into('<I',d,o+44,7),
                     lambda d,o:struct.pack_into('<i',d,o+20,2)]
        for mutation in corruptions:
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                inspect_station_map(station_descriptor(malformed=mutation))

    def test_invalid_parameters_do_not_enter_candidate_search(self):
        for values in ({'width':True},{'depth':float('inf')},{'edge_spacing':.1},{'width':1.}):
            with self.subTest(values=values),self.assertRaises(ValueError):
                ParkingParameters(**values)

    def test_concave_area_cannot_be_crossed_by_rectangle_with_inside_corners(self):
        lot=[(0,0),(10,0),(10,10),(6,10),(6,3),(4,3),(4,10),(0,10)]
        crossing=[(2,2),(8,2),(8,8),(2,8)]
        self.assertFalse(_within(crossing,lot))
        self.assertTrue(_within([(1,1),(3,1),(3,3),(1,3)],lot))
