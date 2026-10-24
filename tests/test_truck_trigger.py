"""Authored PPD fixtures exercise native truck append and car composition."""
import math
import struct
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.rest_stops import inspect_rest_triggers
from ats_road_trip.station_parking.trigger import append_car_parking_polygon
from ats_road_trip.truck_parking.trigger import append_truck_parking_polygon
from tests.test_station_trigger import descriptor, CAR_POLYGON

TRUCK = token('hud_parking')
CAR = token('parking_car')
NATIVE = [(0., 0., 0.), (30., 0., 0.), (30., 0., 22.), (0., 0., 22.)]
BANK = [(40., 0., 10.), (100., 0., 10.), (100., 0., 35.), (40., 0., 35.)]
SIDE = [(110., 0., 10.), (136., 0., 10.), (136., 0., 15.), (110., 0., 15.)]
MODES = {TRUCK: {'truck', 'bus'}, CAR: {'car'}}


def source(*, action='hud_parking', flags=0, params=None):
    return descriptor(((7, action, NATIVE, params or (3., 0., 0., flags)),))


def append(data, points=BANK, **kwargs):
    return append_truck_parking_polygon(data, points,
        source_group_id=kwargs.pop('source_group_id', 7),
        action_modes=kwargs.pop('action_modes', MODES), **kwargs)


class TruckTriggerTests(unittest.TestCase):
    def test_multiple_independent_truck_banks_preserve_source_geometry_and_suffix(self):
        original = source()
        original, car_report = append_car_parking_polygon(original, CAR_POLYGON, partial_activation=True)
        original_groups = inspect_rest_triggers(original)
        first, first_report = append(original, partial_activation=True)
        result, second_report = append(first, SIDE, partial_activation=True)
        old_header = struct.unpack_from('<24I', original)
        new_header = struct.unpack_from('<24I', result)
        self.assertEqual(result[96:old_header[22]], original[96:old_header[22]])
        self.assertEqual(result[old_header[22]+8*48:], original[old_header[22]:])
        self.assertEqual([i for i, (a,b) in enumerate(zip(old_header,new_header)) if a!=b], [9,22,23])
        groups = inspect_rest_triggers(result)
        self.assertEqual(groups[:2], original_groups)
        self.assertEqual(len(groups), 4)
        self.assertEqual(len({g['id'] for g in groups}), 4)
        self.assertEqual([g['action'] for g in groups], [TRUCK, CAR, TRUCK, TRUCK])
        self.assertEqual(groups[1]['id'], car_report['group_id'])
        self.assertEqual(set(groups[2]['vertices']), set(BANK))
        self.assertEqual(set(groups[3]['vertices']), set(SIDE))
        for g, report in zip(groups[2:], [first_report,second_report]):
            self.assertEqual(g['id'], report['group_id'])
            self.assertEqual(g['flags'], 4)
            self.assertEqual(report['vehicles'], ['bus', 'truck'])
            self.assertFalse(report['new_car_eligibility'])
            self.assertEqual(report['parameters'], {'range':3., 'reset_delay':0., 'reset_distance':0., 'flags':4})
            self.assertTrue(set(g['indices']).isdisjoint(original_groups[0]['indices']))
            for i in g['indices']:
                record = struct.unpack_from('<IQfffI3f2i', result, new_header[21]+48*i)
                self.assertEqual(record[:6], (g['id'], TRUCK, 3., 0., 0., 4))
                self.assertTrue(set(record[-2:]) <= set(g['indices']))

    def test_default_clones_native_contact_flag_and_explicit_false_changes_only_new_group(self):
        for source_flags in (0,4):
            original = source(flags=source_flags)
            inherited, inherited_report = append(original)
            self.assertEqual(inherited_report['parameters']['flags'],source_flags)
            explicit, report = append(original, partial_activation=False)
            self.assertEqual([g['flags'] for g in inspect_rest_triggers(explicit)], [source_flags,0])
            self.assertEqual(report['source_parameters']['flags'], source_flags)
            self.assertEqual(inherited_report['source_parameters']['flags'], source_flags)

    def test_mixed_source_requires_explicit_resolved_car_free_action(self):
        mixed_modes = {TRUCK: {'truck','bus','car'}, CAR:{'car'}, token('truck_rest'):{'truck'}}
        original = source()
        with self.assertRaisesRegex(ValueError, 'car eligibility'):
            append(original, action_modes=mixed_modes)
        result, report = append(original, action_modes=mixed_modes, action_token=token('truck_rest'))
        groups = inspect_rest_triggers(result,actions=set(mixed_modes))
        self.assertEqual([g['action'] for g in groups],[TRUCK,token('truck_rest')])
        self.assertEqual(groups[0],inspect_rest_triggers(original)[0])
        self.assertEqual(report['source_vehicles'],['bus','car','truck'])
        self.assertEqual(report['vehicles'],['truck'])

    def test_native_source_parameters_and_flags_must_be_reviewed_and_uniform(self):
        invalid = [(5.,0.,0.,0),(3.,1.,0.,0),(3.,0.,1.,0),
                   (3.,0.,0.,1),(3.,0.,0.,2),(3.,0.,0.,8),(math.nan,0.,0.,0)]
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                append(source(params=params))
        for offset, value in ((12,4.),(16,1.),(20,1.)):
            original = bytearray(source())
            h=struct.unpack_from('<24I',original)
            struct.pack_into('<f',original,h[21]+offset,value)
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError,'nonuniform'):
                append(bytes(original))
        original=bytearray(source())
        h=struct.unpack_from('<24I',original)
        struct.pack_into('<I',original,h[21]+24,4)
        with self.assertRaisesRegex(ValueError,'flags'):
            append(bytes(original))

    def test_effective_actions_must_resolve_truck_rest_and_cannot_extend_unknown_modes(self):
        invalid_modes = [{}, {TRUCK:{'car'}}, {TRUCK:{'truck','train'}},
                         {TRUCK:'truck'}, {TRUCK:{1}}, None]
        for modes in invalid_modes:
            with self.subTest(modes=modes),self.assertRaises(ValueError):
                append(source(),action_modes=modes)
        for action in (True,False,0,-1,2**64,token('missing'),CAR,'hud_parking'):
            with self.subTest(action=action),self.assertRaises(ValueError):
                append(source(),action_token=action)
        with self.assertRaises(ValueError):
            append(source(action='parking_car'))

    def test_absent_ambiguous_source_and_bad_layout_are_rejected(self):
        for group_id in (True,-1,2**32,55):
            with self.subTest(group=group_id),self.assertRaises(ValueError):
                append(source(),source_group_id=group_id)
        ambiguous=descriptor(((7,'hud_parking',NATIVE,(3.,0.,0.,0)),
                              (7,'parking_car',CAR_POLYGON,(3.,0.,0.,0))))
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            append(ambiguous)
        for version in (23,24):
            with self.subTest(version=version),self.assertRaisesRegex(ValueError,'v25'):
                append(descriptor(((7,'hud_parking',NATIVE,(3.,0.,0.,0)),),version=version))
        broken=bytearray(source())
        header=struct.unpack_from('<24I',broken)
        struct.pack_into('<i',broken,header[21]+40,10000)
        with self.assertRaisesRegex(ValueError,'neighbor'):
            append(bytes(broken))
        with self.assertRaises(ValueError):
            append(b'bad')

    def test_invalid_geometry_and_nonboolean_partial_are_rejected(self):
        for partial in (1,0,'true',[],{}):
            with self.subTest(partial=partial),self.assertRaisesRegex(ValueError,'boolean'):
                append(source(),partial_activation=partial)
        for polygon in ([(0,0,0),(1,0,1)],[(0,0,0),(2,0,0),(1,0,0)],
                        [(0,0,0),(2,0,2),(0,0,2),(2,0,0)],
                        [(0,0,0),(2,0,0),(1,math.inf,1)],
                        [(0,0,0),(2,0,0),(1,0,1_000_001)],
                        [(0,0,0),(2,0,0),(1,True,1)]):
            with self.subTest(polygon=polygon),self.assertRaises(ValueError):
                append(source(),polygon)

    def test_car_append_before_or_after_truck_keeps_original_and_other_service_groups(self):
        original=source()
        truck_first,truck_report=append(original)
        truck_then_car,car_report=append_car_parking_polygon(truck_first,CAR_POLYGON,partial_activation=True)
        car_first,first_car=append_car_parking_polygon(original,CAR_POLYGON,partial_activation=True)
        car_then_truck,last_truck=append(car_first)
        one,two=inspect_rest_triggers(truck_then_car),inspect_rest_triggers(car_then_truck)
        for groups in (one,two):
            self.assertEqual(groups[0],inspect_rest_triggers(original)[0])
            self.assertEqual(sum(g['action']==CAR for g in groups),1)
            self.assertEqual(sum(g['action']==TRUCK for g in groups),2)
        self.assertEqual(set(one[1]['vertices']),set(two[2]['vertices']))
        self.assertEqual(set(one[2]['vertices']),set(two[1]['vertices']))
        self.assertEqual(append(original),append(original))


class StandaloneTruckTriggerTests(unittest.TestCase):
    def native_sector(self, *, flags=13, action='hud_parking', custom=False, tagged=False,
                      visibility=False, region=NATIVE, missing_node=False):
        from tests.test_rest_stops import standalone
        from tests.test_map_sector import sector,item,refs,HEADER
        from ats_road_trip.truck_parking.standalone import _projections
        raw,nodes=standalone(500,0.,0.,action=action,custom=custom,flags=flags,tags=('site',) if tagged else ())
        nodes=[bytearray(n) for n in nodes]
        for index,(node,point) in enumerate(zip(nodes,region)):
            struct.pack_into('<3i',node,8,*(round(v*256) for v in point))
            struct.pack_into('<I',node,52,0x3000000 | (1 if index==0 else 0))
        projected=_projections(region);padding=[1.25]*3+[0.92]*2
        bounds=[min(p[i] for p in projected)-padding[i] for i in range(5)]
        bounds += [max(p[i] for p in projected)+padding[i] for i in range(5)]
        raw=bytearray(raw);struct.pack_into('<10f',raw,12,*bounds)
        items=[bytes(raw)]
        if visibility:
            items.append(item(0x30,600,struct.pack('<Qff',0,100.,200.)+refs(500)))
        layer=HEADER+struct.pack('<QBQ',500,2,0xffffffffffffffff)
        return sector(items,[bytes(n) for n in (nodes[:-1] if missing_node else nodes)],(500,) if visibility else ()),layer,[bytes(n) for n in nodes]

    def write(self,data,**kwargs):
        from ats_road_trip.truck_parking.standalone import append_truck_standalone_polygons
        return append_truck_standalone_polygons(data,source_uid=kwargs.pop('source_uid',500),
            areas=kwargs.pop('areas',[{'id':'bank','vertices':BANK},{'id':'side','vertices':SIDE}]),
            action_modes=kwargs.pop('action_modes',MODES),uid_namespace=kwargs.pop('uid_namespace','fixture-v1'),**kwargs)

    def test_new_regions_preserve_native_truck_trailer_partial_flags_and_every_original_record(self):
        from ats_road_trip.map_sector import parse_sector,parse_layer
        from ats_road_trip.rest_stops import _standalone
        original,layer,_=self.native_sector(visibility=True,tagged=True)
        result,new_layer,report=self.write(original,layer_data=layer)
        before,after=parse_sector(original),parse_sector(result)
        self.assertEqual(after.item_count,before.item_count+2)
        self.assertEqual(after.node_count,before.node_count+8)
        self.assertEqual(report['source_activation']['flags'],'0xd')
        self.assertTrue(report['activation_contract']['PPD_flags_not_reused'])
        self.assertEqual(report['marker_count'],2)
        self.assertFalse(report['new_car_eligibility'])
        self.assertEqual([i.flags for i in after.items if i.kind==0x22],[13,13,13])
        after_nodes={n.uid:n for n in after.nodes};after_items={i.uid:i for i in after.items}
        for node in before.nodes:
            self.assertEqual(node.raw,after_nodes[node.uid].raw)
        source=before.items[0];copied=after_items[source.uid]
        self.assertEqual(original[source.offset:source.end],result[copied.offset:copied.end])
        expected_new={int(a['uid'],16) for a in report['areas']}
        self.assertEqual(set(after.visibility_children),{500}|expected_new)
        self.assertEqual(set(after_items[600].details['children']),{500}|expected_new)
        self.assertEqual(parse_layer(new_layer),{500:2,**{u:2 for u in expected_new}})
        native=_standalone(original,source)
        for area in report['areas']:
            item=after_items[int(area['uid'],16)];trigger=_standalone(result,item)
            self.assertEqual(trigger['tags'],native['tags'])
            self.assertEqual(len(trigger['actions']),1)
            self.assertEqual(trigger['actions'][0]['action'],TRUCK)
            self.assertFalse(trigger['actions'][0]['custom'])
            self.assertEqual([list(after_nodes[u].position) for u in trigger['nodes']],area['vertices_xyz'])
            self.assertEqual([after_nodes[u].flags for u in trigger['nodes']],[0x3000001,0x3000000,0x3000000,0x3000000])
            for u in trigger['nodes']:
                self.assertEqual((after_nodes[u].backward,after_nodes[u].forward),(0,item.uid))

    def test_native_contact_and_guard_flags_are_preserved_without_ppd_reinterpretation(self):
        from ats_road_trip.map_sector import parse_sector
        for flags in (12,13,0x30d,0x4000d,0x4000c,29):
            data,_,_=self.native_sector(flags=flags)
            result,layer,report=self.write(data)
            self.assertIsNone(layer)
            self.assertEqual([i.flags for i in parse_sector(result).items],[flags]*3)
            self.assertEqual(report['source_activation']['partial_activation'],bool(flags&1))

    def test_custom_disabled_oriented_collision_and_trailer_missing_contracts_block(self):
        for flags in (4,5,14,45,0x1000d,0x8000000d):
            with self.subTest(flags=flags),self.assertRaises(ValueError):
                self.write(self.native_sector(flags=flags)[0])
        with self.assertRaisesRegex(ValueError,'custom parameters'):
            self.write(self.native_sector(custom=True)[0])
        mixed={TRUCK:{'truck','bus','car'},CAR:{'car'},token('truck_rest'):{'truck'}}
        original,_,_=self.native_sector()
        with self.assertRaisesRegex(ValueError,'car eligibility'):
            self.write(original,action_modes=mixed)
        result,_,report=self.write(original,action_modes=mixed,action_token=token('truck_rest'))
        self.assertEqual(report['areas'][0]['vehicles'],['truck'])
        with self.assertRaisesRegex(ValueError,'native truck-rest action'):
            self.write(self.native_sector(action='parking_car')[0])
        with self.assertRaises(ValueError):
            self.write(original,action_modes={TRUCK:None})

    def test_safe_uid_namespace_collisions_and_quantized_geometry(self):
        data,_,_=self.native_sector()
        points=[(x+0.0011,y+0.0011,z+0.0011) for x,y,z in BANK]
        result,_,report=self.write(data,areas=[{'id':'quantized','vertices':points}])
        for requested,emitted in zip(points,report['areas'][0]['vertices_xyz']):
            self.assertTrue(all(abs(a-b)<=1/512 for a,b in zip(requested,emitted)))
        self.assertEqual((result,report),self.write(data,areas=[{'id':'quantized','vertices':points}])[::2])
        collision=int(report['generated_uids'][0],16)
        with self.assertRaisesRegex(ValueError,'UID collision'):
            self.write(data,areas=[{'id':'quantized','vertices':points}],occupied_uids={collision})
        for kwargs in ({'uid_namespace':''},{'source_uid':True},{'areas':[]},
                       {'areas':[{'id':'x','vertices':BANK},{'id':'x','vertices':SIDE}]},
                       {'areas':[{'id':'x','vertices':[(0,0,0),(0.00001,0,0),(0,0,0.00001)]}]},
                       {'occupied_uids':{0}}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                self.write(data,**kwargs)

    def test_missing_cross_sector_source_nodes_require_explicit_unambiguous_native_records(self):
        from ats_road_trip.map_sector import parse_sector
        complete,_,_=self.native_sector()
        missing,_,_=self.native_sector(missing_node=True)
        with self.assertRaisesRegex(ValueError,'unresolved across sectors'):
            self.write(missing)
        original_node=parse_sector(complete).nodes[-1]
        result,_,report=self.write(missing,external_nodes={original_node.uid:original_node})
        self.assertEqual(report['added_trigger_count'],2)
        with self.assertRaises(ValueError):
            self.write(missing,external_nodes={original_node.uid:'bad'})
        wrong=original_node.__class__(**{**original_node.__dict__,'forward':99})
        with self.assertRaisesRegex(ValueError,'ownership'):
            self.write(missing,external_nodes={original_node.uid:wrong})

    def test_other_car_fuel_and_native_node_data_survive_standalone_composition(self):
        from ats_road_trip.map_sector import parse_sector
        from tests.test_rest_stops import standalone
        from tests.test_map_sector import sector,item,refs,node
        data,_,_=self.native_sector()
        before=parse_sector(data)
        car,car_nodes=standalone(900,250.,250.,action='parking_car')
        service=item(7,1000,struct.pack('<QQ',1001,500)+refs())
        source_items=[data[i.offset:i.end] for i in before.items]+[car,service]
        data=sector(source_items,[n.raw for n in before.nodes]+car_nodes+[node(1001,1000)])
        result,_,report=self.write(data)
        after=parse_sector(result);by_uid={i.uid:i for i in after.items}
        for old in parse_sector(data).items:
            new=by_uid[old.uid]
            self.assertEqual(data[old.offset:old.end],result[new.offset:new.end])
        self.assertFalse(report['new_car_eligibility'])
        self.assertEqual(report['areas'][0]['vehicles'],['bus','truck'])
        broken=bytearray(data)
        original_node=parse_sector(data).nodes[1]
        struct.pack_into('<I',broken,original_node.offset+52,original_node.flags^4)
        with self.assertRaisesRegex(ValueError,'metadata'):
            self.write(bytes(broken))

    def test_native_bounds_calibration_and_emitted_envelope(self):
        from ats_road_trip.truck_parking.standalone import _projections
        data,_,_=self.native_sector()
        for first_bound in (-10000.,4.,math.nan):
            broken=bytearray(data);struct.pack_into('<f',broken,20+12,first_bound)
            with self.subTest(bound=first_bound),self.assertRaises(ValueError):
                self.write(bytes(broken))
        for coords in ((BANK),[(-x-19100,y+32.1,-z-11700) for x,y,z in BANK]):
            _,_,report=self.write(data,areas=[{'id':'envelope','vertices':coords}])
            area=report['areas'][0]
            for point in _projections(area['vertices_xyz']):
                for index,value in enumerate(point):
                    self.assertLessEqual(area['bounds'][index],value)
                    self.assertGreaterEqual(area['bounds'][index+5],value)


if __name__=='__main__':
    unittest.main()
