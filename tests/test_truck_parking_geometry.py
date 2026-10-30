"""Truck-scale source curve discovery and conservative native coverage checks."""
import math
import struct
import unittest
from types import SimpleNamespace as NS

from ats_road_trip.local_fuel import token
from ats_road_trip.truck_parking.catalog import reviewed_curve_catalog, load_curve_definitions, north_platte_reviewed_regions
from ats_road_trip.truck_parking.geometry import discover_curve_banks, compare_coverage

MODEL='model/props/road/parking_1line_truck_dirt_curve.pmd'
DEFS={token('89'):{'model_path':MODEL}}


def node(uid, position):
    return NS(uid=uid,position=position,rotation=(1.,0.,0.,0.))


def curve(uid=10, refs=(1,2,0,0), length=50., scale=1., flags=0, height=(0.,), variation='yellow'):
    raw=bytes(57)+struct.pack('<4QfI',*refs,length,1)
    raw+=struct.pack('<QIIfffQIf4QI',token('89'),flags,0,1.,scale,0.,0,0xffffff,0.,
                     token('start_y1'),token('end_y1'),token(variation),token('default'),len(height))
    raw+=struct.pack('<'+'f'*len(height),*height)+struct.pack('<5f',0,0,0,0,0)
    return raw,NS(kind=0x2c,uid=uid,offset=0,end=len(raw),flags=0x400000,details={})


class TruckCurveGeometryTests(unittest.TestCase):
    def test_directed_truck_bank_rotates_with_source_curve(self):
        for a,b in [((0,3,0),(0,3,50)),((0,3,0),(50,3,0)),((100,3,100),(70,3,60))]:
            raw,item=curve()
            parsed=NS(nodes=(node(1,a),node(2,b)),items=(item,))
            banks,diagnostics=discover_curve_banks([('map/usa/sec+0000+0000.aux',raw,parsed)],DEFS)
            self.assertEqual(diagnostics,[])
            bank=banks[0];self.assertAlmostEqual(bank['dimensions']['depth'],24.16)
            self.assertAlmostEqual(math.dist(bank['vertices'][0],bank['vertices'][1]),49.2)
            self.assertAlmostEqual(math.dist(bank['vertices'][1],bank['vertices'][2]),24.16)
            self.assertEqual(bank['coordinate_frame'],'world_xyz_including_compound_nodes')
            self.assertEqual(bank['source_flags'],0x400000)

    def test_sector_boundary_node_is_resolved_without_fuel(self):
        raw,item=curve();a=NS(nodes=(node(1,(0,0,0)),),items=(item,));b=NS(nodes=(node(2,(0,0,50)),),items=())
        banks,diagnostics=discover_curve_banks([('a.aux',raw,a),('b.aux',b'',b)],DEFS)
        self.assertEqual(len(banks),1);self.assertEqual(diagnostics,[])

    def test_compound_nodes_are_world_positions_and_scoped(self):
        raw,item=curve();child=NS(uid=44,kind=0x28,details={'items':(item,),
           'compound_nodes':(node(1,(100,7,100)),node(2,(100,7,150)))})
        parsed=NS(nodes=(node(1,(900,0,900)),node(2,(900,0,950))),items=(child,))
        banks,diagnostics=discover_curve_banks([('site.aux',raw,parsed)],DEFS)
        self.assertEqual(diagnostics,[]);self.assertEqual(banks[0]['parent_uid'],hex(44))
        self.assertEqual(banks[0]['source_endpoints'],[(100.,7.,100.),(100.,7.,150.)])
        self.assertLess(max(p[0] for p in banks[0]['vertices']),101)

    def test_no_silent_scaled_offset_or_unknown_variant_geometry(self):
        for kwargs,reason in [({'scale':2},'scaled_or_stretched'),({'flags':16},'unreviewed_subcurve_flags'),
                              ({'height':(.8,)},'offset_bank'),({'variation':'mirror'},'unreviewed_bank_variation')]:
            raw,item=curve(**kwargs);parsed=NS(nodes=(node(1,(0,0,0)),node(2,(0,0,50))),items=(item,))
            banks,d=discover_curve_banks([('site.aux',raw,parsed)],DEFS)
            self.assertFalse(banks);self.assertIn(reason,d[0]['reason'])

    def test_locs_and_nonstraight_curves_are_reported(self):
        for kwargs in [{'refs':(1,2,3,0)},{'length':55}]:
            raw,item=curve(**kwargs);parsed=NS(nodes=(node(1,(0,0,0)),node(2,(0,0,50))),items=(item,))
            banks,d=discover_curve_banks([('site.aux',raw,parsed)],DEFS)
            self.assertFalse(banks);self.assertEqual(len(d),1)

    def test_complete_partial_and_separate_native_coverage(self):
        bank=[(0,0),(50,0),(50,24),(0,24)]
        self.assertEqual(compare_coverage(bank,[bank])['state'],'fully_covered')
        self.assertEqual(compare_coverage(bank,[[(0,0),(20,0),(20,24),(0,24)]])['state'],'partially_covered')
        self.assertEqual(compare_coverage(bank,[[(100,0),(150,0),(150,24),(100,24)]])['state'],'uncovered')
        # Shared edges count as inside, and a native point elsewhere does not
        # exempt another region in the same facility from coverage analysis.
        self.assertEqual(compare_coverage(bank,[[(-1,-1),(51,-1),(51,25),(-1,25)]])['state'],'fully_covered')

    def test_bad_native_or_concavity_never_establishes_complete_coverage(self):
        bank=[(0,0),(50,0),(50,24),(0,24)]
        self.assertEqual(compare_coverage(bank,[[(0,0),(1,0)]])['state'],'unknown')
        concave=[(-1,-1),(51,-1),(51,25),(30,25),(30,10),(20,10),(20,25),(-1,25)]
        self.assertEqual(compare_coverage(bank,[concave])['state'],'partially_covered')

    def test_source_quoted_tabs_are_semantically_preserved(self):
        text='SiiNunit {\ncurve_model : curve.89 {\n name: "bright:'+chr(9)+'255,255,255"\n model_desc: "/'+MODEL+'"\n}\n}'
        stack=NS(prefetch=lambda pattern:None, matching=lambda pattern:['def/world/curve_model.sii'],
                 text=lambda path:text)
        rows=load_curve_definitions(stack)
        self.assertEqual(rows[token('89')]['unit'].one('name'),'bright:'+chr(9)+'255,255,255')
        self.assertEqual(rows[token('89')]['model_path'],MODEL)

    def test_reviewed_placement_is_absent_without_its_selected_source(self):
        missing=NS(resources={},packages=[])
        self.assertIsNone(north_platte_reviewed_regions(missing))
        source='map/usa/sec-0005-0003.base'
        stock=NS(resources={source:(None,NS(package='base_map.scs'))},
                 read=lambda *a,**k:self.fail('Unselected source must not be read'))
        self.assertIsNone(north_platte_reviewed_regions(stock,map_packages={'base_map.scs'}))
        self.assertIsNone(north_platte_reviewed_regions(stock,map_packages={'Western_Canada_Expansion.scs'}))

    def test_reviewed_placement_keeps_selected_source_guards(self):
        source='map/usa/sec-0005-0003.base'
        selected={'originals/ATS_Expansion_v23.0_1.61.scs'}
        changed=NS(resources={source:(None,NS(package='different/new-version.scs'))})
        with self.assertRaisesRegex(ValueError,'provider drift'):
            north_platte_reviewed_regions(changed,map_packages=selected)
        with self.assertRaisesRegex(ValueError,'sector missing'):
            north_platte_reviewed_regions(NS(resources={}),map_packages=selected)
        changed=NS(resources={source:(None,NS(package='originals/ATS_Expansion_v23.0_1.61.scs'))},
                   read=lambda *a,**k:b'changed source sector')
        with self.assertRaisesRegex(ValueError,'sector drift'):
            north_platte_reviewed_regions(changed,map_packages=selected)

    def test_partial_overlap_fraction_is_exact_and_not_a_full_coverage_claim(self):
        bank=[(0,0),(50,0),(50,24),(0,24)]
        result=compare_coverage(bank,[[(0,0),(20,0),(20,24),(0,24)]])
        self.assertEqual(result['state'],'partially_covered')
        self.assertAlmostEqual(result['maximum_native_coverage_fraction'],.4)

    def test_reviewed_family_has_raw_resource_pins(self):
        p=reviewed_curve_catalog()[MODEL]
        self.assertEqual(len(p['model_sha256']),64);self.assertEqual(len(p['geometry_sha256']),64)
        self.assertGreater(p['depth'],24)


if __name__=='__main__':unittest.main()
