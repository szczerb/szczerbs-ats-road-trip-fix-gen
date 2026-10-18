"""Authored geometry fixtures exercise eligibility, scope and processor composition."""
from pathlib import Path
import struct
import tempfile
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package,ResourceStack
from ats_road_trip.rest_stops import (_standalone, inspect_rest_triggers, plan_rest_stops,
                                      polygon_distance,retarget_rest_polygons)
from ats_road_trip.sii import parse_units
from tests.test_map_sector import item,refs,sector

SECTOR='map/usa/sec+0000+0000.base'
PPD='prefab/test/rest.ppd'
DEFINITION=b'''SiiNunit
{
prefab_model : prefab.rest {
 prefab_desc: "/prefab/test/rest.ppd"
 model_desc: "/prefab/test/rest.pmd"
 category: "fixture"
}
}
'''
ACTIONS=b'''SiiNunit
{
trigger_action : trig_action.hud_parking {
 name: "Parking - Large vehicles"
 command: "hud_activate"
 num_params[]: 3
 str_params[]: "truck"
 str_params[]: "bus"
}
trigger_action : trig_action.parking_car {
 name: "Parking - Small vehicles"
 command: "hud_activate"
 num_params[]: 3
 str_params[]: "car"
}
}
'''


def descriptor(groups=None):
    if groups is None:
        groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)])]
    controls=bytearray(208)
    struct.pack_into('<3f',controls,16,0.,0.,0.)
    struct.pack_into('<3f',controls,120,0.,0.,10.)
    records=[]
    for group_id,(action,points) in enumerate(groups):
        first=len(records)
        for i,(x,z) in enumerate(points):
            records.append(struct.pack('<IQfffI3f2i',group_id,token(action),3.,0.,0.,0,
                                       x,0.,z,first+(i-1)%len(points),first+(i+1)%len(points)))
    h=[0]*24
    h[0],h[1],h[9]=25,2,len(records)
    h[12:24]=[96]+[304]*9+[304+48*len(records)]*2
    return struct.pack('<24I',*h)+controls+b''.join(records)


def map_node(uid,x,z,owner):
    return struct.pack('<Q3i4fQQI',uid,round(x*256),0,round(z*256),1.,0.,0.,0.,0,owner,0)


def placement(uid=100,x=0.,z=0.):
    nodes=(uid+1000,uid+1001)
    raw=item(4,uid,struct.pack('<QQ',token('rest'),0)+refs()+refs(*nodes)+refs()
             +struct.pack('<QH',0,0)+bytes(2*12+8))
    return raw,[map_node(nodes[0],x,z,uid),map_node(nodes[1],x,z+10,uid)]


def standalone(uid,x,z,action='parking_car',custom=False,sphere=None,flags=0x0c):
    points=[(x,z)] if sphere is not None else [(x,z),(x+10,z),(x+10,z+10),(x,z+10)]
    nodes=[uid+2000+i for i in range(len(points))]
    params=(struct.pack('<IfII fI',1,3.,0,0,0.,0) if custom else struct.pack('<I',0xffffffff))
    raw=item(0x22,uid,refs()+refs(*nodes)+struct.pack('<IQ',1,token(action))+params
             +(struct.pack('<f',sphere) if sphere is not None else b''),flags=flags)
    return raw,[map_node(n,*p,uid) for n,p in zip(nodes,points)]


def source(placements=((100,0.,0.),),groups=None,standalones=()):
    items,nodes=[],[]
    for args in placements:
        raw,ns=placement(*args); items.append(raw); nodes.extend(ns)
    for args in standalones:
        raw,ns=standalone(*args); items.append(raw); nodes.extend(ns)
    return {SECTOR:sector(items,nodes),PPD:descriptor(groups),
            'def/world/prefab.rest.sii':DEFINITION,'def/world/trigger_action.sii':ACTIONS}


def self_crossing_standalones(*entries):
    """Original trigger nodes form an asymmetric crossed ring with real area."""
    data=source(placements=())
    items,nodes=[],[]
    shape=((0.,0.),(10.,0.),(1.,10.),(10.,5.))
    for uid,action,dx in entries:
        raw,_=standalone(uid,dx,0.,action=action)
        items.append(raw)
        nodes.extend(map_node(uid+2000+i,dx+x,z,uid) for i,(x,z) in enumerate(shape))
    data[SECTOR]=sector(items,nodes)
    return data


class RestTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.packages=[]
        self.addCleanup(lambda:[p.close() for p in self.packages])

    def package(self,name,data):
        root=Path(self.temp.name)/name
        for path,contents in data.items():
            target=root/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(contents)
        p=Package(root); self.packages.append(p)
        return p

    def plan(self,data,*,before=(),overrides=None,radius=1000):
        p=self.package('source',data)
        return p,plan_rest_stops(ResourceStack([*before,p]),map_packages={str(p.path)},
                                map_name='fixture',radius=radius,resource_overrides=overrides)

    def complete(self,report):
        self.assertTrue(report['coverage']['complete'],report['coverage']['blockers'])

    def test_polygon_distance_uses_edges_and_interiors(self):
        a=[(0,0),(3000,0),(3000,10),(0,10)]
        self.assertEqual(polygon_distance(a,[(3999,0),(4009,0),(4009,10),(3999,10)]),999)
        self.assertEqual(polygon_distance(a,[(5,5)]),0)
        self.assertEqual(polygon_distance([(1,2)],[(4,6)]),5)

    def test_definition_only_source_has_no_rest_targets_and_does_not_block_prices(self):
        _, (report, resources) = self.plan({'def/country/example.sui': b'country_data : x {}'})
        self.complete(report)
        self.assertEqual(report['status'], 'not_applicable')
        self.assertEqual(report['scope']['source_sector_count'], 0)
        self.assertEqual(report['coverage']['added_car_polygons'], 0)
        self.assertEqual(resources, {})

    def test_local_private_action_retains_truck_bus_and_all_geometry(self):
        original=source()
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertNotIn(PPD,out)
        self.assertNotIn('def/world/trigger_action.sii',out)
        action=parse_units(out[report['private_action']['resource']].decode())[0]
        self.assertEqual(action.values('str_params'),('truck','bus','car'))
        self.assertEqual(action.values('num_params'),('3',))
        private=next(data for path,data in out.items() if path.endswith('.ppd'))
        alias=token(report['private_action']['token'])
        groups=inspect_rest_triggers(private,actions={alias})
        self.assertEqual(groups[0]['vertices'],inspect_rest_triggers(original[PPD])[0]['vertices'])
        self.assertEqual(len(private),len(original[PPD]))
        h=struct.unpack_from('<24I',private)
        allowed={h[21]+48*i+j for i in range(4) for j in range(4,12)}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(private,original[PPD]))))
        before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
        self.assertEqual([n.raw for n in before.nodes],[n.raw for n in after.nodes])

    def test_baseline_car_standalone_in_aux_suppresses_at_inclusive_boundary(self):
        raw,nodes=standalone(500,1010.,0.)
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.aux':sector([raw],nodes)})
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['locations'][0]['nearest_car_distance'],1000)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(out,{})

    def test_above_boundary_adds_and_large_polygon_distance_is_not_centroid(self):
        raw,nodes=standalone(500,1010.+1/256,0.)
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':sector([raw],nodes)})
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertTrue(out)

    def test_same_descriptor_two_placements_only_one_selected(self):
        raw,nodes=standalone(500,1009.,0.)
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':sector([raw],nodes)})
        original=source(((100,0.,0.),(200,-2.,0.)))
        _,(report,out)=self.plan(original,before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
        self.assertEqual(before.prefabs[0].details['model'],after.prefabs[0].details['model'])
        self.assertNotEqual(before.prefabs[1].details['model'],after.prefabs[1].details['model'])

    def test_new_car_addition_never_suppresses_second_original_truck(self):
        _,(report,out)=self.plan(source(((100,0.,0.),(200,15.,0.))))
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],2)
        self.assertEqual(len([p for p in out if p.endswith('.ppd')]),2)

    def test_existing_car_prefab_polygon_is_in_index(self):
        groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                ('parking_car',[(500.,0.),(510.,0.),(510.,10.),(500.,10.)])]
        _,(report,out)=self.plan(source(groups=groups))
        self.complete(report)
        self.assertEqual(report['coverage']['existing_car_locations'],1)
        self.assertEqual(out,{})

    def test_standalone_truck_action_is_local_retarget_with_unchanged_nodes(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
        self.assertEqual([n.raw for n in before.nodes],[n.raw for n in after.nodes])
        self.assertEqual(len(original[SECTOR]),len(out[SECTOR]))
        self.assertFalse(any(p.endswith('.ppd') for p in out))

    def test_standalone_sphere_car_distance_subtracts_activation_range(self):
        raw,nodes=standalone(500,1020.,0.,sphere=10.)
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':sector([raw],nodes)})
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['locations'][0]['nearest_car_distance'],1000)
        self.assertEqual(out,{})

    def test_custom_source_standalone_parameters_block_absence_conclusions(self):
        original=source(standalones=((500,500.,0.,'parking_car',True),))
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('custom parameters',str(report['coverage']['blockers']))
        self.assertEqual(out,{})

    def test_unknown_sector_and_invalid_polygon_block_all_output(self):
        original=source(); original['map/usa/sec+0030+0030.base']=sector([item(0x77,700)])
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete']); self.assertEqual(out,{})

    def test_effective_action_semantics_are_checked(self):
        original=source(); original['def/world/trigger_action.sii']=ACTIONS.replace(b'"truck"',b'"car"')
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete']); self.assertEqual(out,{})

    def test_processor_overlay_preserves_prior_sector_and_descriptor_changes(self):
        original=source()
        overlay=dict(original)
        # A previous processor adds an unrelated opaque item, and a changed
        # non-trigger descriptor section; both must survive the local alias.
        parsed=parse_sector(original[SECTOR]); raw=original[SECTOR]
        overlay[SECTOR]=sector([raw[i.offset:i.end] for i in parsed.items]+[item(0x12,900,bytes(16))],
                               [n.raw for n in parsed.nodes])
        ppd=bytearray(original[PPD]); ppd[100]=42; overlay[PPD]=bytes(ppd)
        _,(report,out)=self.plan(original,overrides=overlay)
        self.complete(report)
        self.assertEqual(report['composed_resource_paths'],[SECTOR])
        self.assertIn(900,{i.uid for i in parse_sector(out[SECTOR]).items})
        private=next(data for path,data in out.items() if path.endswith('.ppd'))
        self.assertEqual(private[100],42)

    def test_generated_stack_is_idempotent(self):
        p,(report,out)=self.plan(source())
        self.complete(report)
        generated=self.package('generated',out)
        again,changes=plan_rest_stops(ResourceStack([p,generated]),
                                      map_packages={str(p.path),str(generated.path)},map_name='fixture')
        self.complete(again)
        self.assertEqual(again['coverage']['already_supported'],1)
        self.assertEqual(changes,{})

    def test_invalid_neighbor_and_single_control_fail_closed(self):
        ppd=bytearray(descriptor()); h=struct.unpack_from('<24I',ppd)
        struct.pack_into('<i',ppd,h[21]+40,999)
        with self.assertRaisesRegex(ValueError,'invalid neighbors'):
            inspect_rest_triggers(bytes(ppd))

    def test_different_map_namespaces_never_supply_car_neighbors(self):
        raw,nodes=standalone(500,0.,0.)
        baseline=self.package('baseline',{'map/other/sec+0000+0000.base':sector([raw],nodes)})
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertTrue(out)

    def test_source_car_added_to_existing_truck_action_is_already_supported(self):
        original=source()
        original['def/world/trigger_action.sii']=ACTIONS.replace(
            b'str_params[]: "bus"',b'str_params[]: "bus"\n str_params[]: "car"')
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(out,{})

    def test_existing_crossed_car_and_nearby_truck_are_proven_supported(self):
        original=self_crossing_standalones((500,'parking_car',0.),
                                           (600,'hud_parking',2.))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(out,{})
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(len(report['legacy_irregular_polygons']),2)
        self.assertEqual(report['locations'][0]['distance_method'],
                         'vertex_pair_upper_bound_for_original_irregular_polygon')
        self.assertLess(report['locations'][0]['nearest_car_distance'],3.)

    def test_crossed_truck_without_vertex_proven_car_neighbor_changes_only_action(self):
        original=self_crossing_standalones((600,'hud_parking',0.))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertEqual(len(report['conservative_proximity_for_irregular_source']),1)
        self.assertEqual(report['locations'][0]['proximity_method'],
                         'conservative_vertex_proof_only_for_original_irregular_polygon')
        before=original[SECTOR];after=out[SECTOR]
        item=parse_sector(before).items[0]
        action_offset=_standalone(before,item)['actions'][0]['offset']
        changed={index for index,(a,b) in enumerate(zip(before,after)) if a!=b}
        self.assertTrue(changed)
        self.assertTrue(changed<=set(range(action_offset,action_offset+8)))
        self.assertEqual(len(before),len(after))
        self.assertEqual([n.raw for n in parse_sector(before).nodes],
                         [n.raw for n in parse_sector(after).nodes])

    def test_far_irregular_car_does_not_hide_extra_permission(self):
        original=self_crossing_standalones((500,'parking_car',3000.),
                                           (600,'hud_parking',0.))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertEqual(len(report['conservative_proximity_for_irregular_source']),1)
        self.assertIn(SECTOR,out)

    def test_crossed_car_without_truck_does_not_block(self):
        original=self_crossing_standalones((500,'parking_car',0.))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(out,{})
        self.assertEqual(report['coverage']['existing_car_locations'],1)

    def test_repeated_car_vertex_uses_vertex_proximity_without_mutation(self):
        raw,_=standalone(500,0.,0.,action='parking_car')
        shape=((0.,0.),(10.,0.),(10.,0.),(0.,10.))
        nodes=[map_node(2500+i,x,z,500) for i,(x,z) in enumerate(shape)]
        original=source()
        parsed=parse_sector(original[SECTOR]);old=original[SECTOR]
        original[SECTOR]=sector([old[i.offset:i.end] for i in parsed.items]+[raw],
                                [n.raw for n in parsed.nodes]+nodes)
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(out,{})
        self.assertEqual(report['legacy_irregular_polygons'][0]['reason'],
                         'Rest polygon is degenerate')
        self.assertEqual(report['locations'][0]['distance_method'],
                         'vertex_pair_upper_bound_for_original_irregular_polygon')

    def test_legacy_ppd_versions_retain_exact_trigger_records(self):
        for version in (23,24):
            with self.subTest(version=version):
                data=bytearray(descriptor())
                struct.pack_into('<I',data,0,version)
                self.assertEqual(len(inspect_rest_triggers(bytes(data))),1)
                changed,report=retarget_rest_polygons(bytes(data),{0},token('rtatest'),
                                                       actions={token('hud_parking'),token('parking_car')})
                self.assertEqual(struct.unpack_from('<I',changed)[0],version)
                self.assertTrue(report['original_geometry_topology_and_other_sections_preserved'])

    def test_partial_activation_flag4_is_preserved_in_action_token_only_clone(self):
        original=source()
        data=bytearray(original[PPD]);h=struct.unpack_from('<24I',data)
        for index in range(h[9]):
            struct.pack_into('<I',data,h[21]+48*index+24,4)
        original[PPD]=bytes(data)
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        private=next(contents for path,contents in out.items() if path.endswith('.ppd'))
        allowed={h[21]+48*index+offset for index in range(h[9]) for offset in range(4,12)}
        differences={index for index,(before,after) in enumerate(zip(data,private)) if before!=after}
        self.assertTrue(differences)
        self.assertTrue(differences<=allowed)
        self.assertEqual([g['flags'] for g in inspect_rest_triggers(private,
                         actions={token(report['private_action']['token'])})],[4])
        with_car=dict(original)
        raw,nodes=standalone(500,0.,0.,action='parking_car')
        parsed=parse_sector(original[SECTOR]);old=original[SECTOR]
        with_car[SECTOR]=sector([old[i.offset:i.end] for i in parsed.items]+[raw],
                                [n.raw for n in parsed.nodes]+nodes)
        _,(report,out)=self.plan(with_car)
        self.complete(report)
        self.assertEqual(out,{})

    def test_mixed_or_unknown_prefab_trigger_flags_remain_blocked(self):
        for flags in ((4,0,4,4),(8,8,8,8)):
            with self.subTest(flags=flags):
                data=bytearray(descriptor());h=struct.unpack_from('<24I',data)
                for index,value in enumerate(flags):
                    struct.pack_into('<I',data,h[21]+48*index+24,value)
                with self.assertRaisesRegex(ValueError,'Unsupported rest trigger flags'):
                    inspect_rest_triggers(bytes(data))

    def test_generated_alias_on_baseline_is_in_car_index(self):
        original=source()
        p,(report,out)=self.plan(original)
        self.complete(report)
        # Relabel source sector as baseline neighbor; generated private alias
        # carries car eligibility and must suppress a nearby new source site.
        generated=dict(out)
        generated['map/usa/sec+0001+0000.base']=generated.pop(SECTOR)
        baseline=self.package('baseline',generated)
        second=self.package('second',source(((200,100.,0.),)))
        again,changes=plan_rest_stops(ResourceStack([p,baseline,second]),
                                      map_packages={str(second.path)},map_name='second')
        self.complete(again)
        self.assertEqual(again['coverage']['already_supported'],1)
        self.assertEqual(changes,{})

    def test_only_source_owned_placements_are_changed(self):
        baseline_data=source(((200,5000.,0.),))
        baseline_data['map/usa/sec+0001+0000.base']=baseline_data.pop(SECTOR)
        baseline=self.package('baseline',baseline_data)
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['truck_polygons'],1)
        self.assertNotIn('map/usa/sec+0001+0000.base',out)

    def test_missing_control_node_blocks_complete_output(self):
        original=source()
        parsed=parse_sector(original[SECTOR]); raw=original[SECTOR]
        original[SECTOR]=sector([raw[i.offset:i.end] for i in parsed.items],[parsed.nodes[0].raw])
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('Unresolved',str(report['coverage']['blockers']))
        self.assertEqual(out,{})

    def test_disconnected_group_rejected_even_when_neighbors_are_reciprocal(self):
        points=[(0.,0.),(10.,0.),(10.,10.),(0.,10.),(20.,0.),(30.,0.),(30.,10.),(20.,10.)]
        ppd=bytearray(descriptor([('hud_parking',points)])); h=struct.unpack_from('<24I',ppd)
        for i in range(8):
            base=(i//4)*4
            struct.pack_into('<2i',ppd,h[21]+48*i+40,base+(i-1)%4,base+(i+1)%4)
        with self.assertRaisesRegex(ValueError,'disconnected'):
            inspect_rest_triggers(bytes(ppd))

    def test_same_prefab_selects_only_distant_truck_polygon(self):
        groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                ('hud_parking',[(3000.,0.),(3010.,0.),(3010.,10.),(3000.,10.)]),
                ('parking_car',[(500.,0.),(510.,0.),(510.,10.),(500.,10.)])]
        _,(report,out)=self.plan(source(groups=groups))
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        private=next(data for path,data in out.items() if path.endswith('.ppd'))
        alias=token(report['private_action']['token'])
        after=inspect_rest_triggers(private,actions={token('hud_parking'),token('parking_car'),alias})
        self.assertEqual([(g['id'],g['action']) for g in after],
                         [(0,token('hud_parking')),(1,alias),(2,token('parking_car'))])

    def test_single_control_node_rest_prefab_is_an_explicit_blocker(self):
        original=source(); ppd=original[PPD]; h=list(struct.unpack_from('<24I',ppd))
        h[1]=1
        for i in range(13,24):
            h[i]-=104
        original[PPD]=struct.pack('<24I',*h)+ppd[96:200]+ppd[304:]
        raw=item(4,100,struct.pack('<QQ',token('rest'),0)+refs()+refs(1100)+refs()
                 +struct.pack('<QH',0,0)+bytes(12+8))
        original[SECTOR]=sector([raw],[map_node(1100,0.,0.,100)])
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('at least two',str(report['coverage']['blockers']))
        self.assertEqual(out,{})

    def test_decimal_and_exponent_rest_ids_are_normalized_for_alias_car_index(self):
        square=[(500.,0.),(510.,0.),(510.,10.),(500.,10.)]
        for spelling in ('3.0','3.000000','3e0','+3.00'):
            with self.subTest(spelling=spelling):
                original=source(groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                                        ('custom_rest',square)])
                alias=('trigger_action : trig_action.custom_rest {\n command: "hud_activate"\n'
                       ' num_params[]: '+spelling+'\n str_params[]: "car"\n}\n').encode()
                original['def/world/trigger_action.sii']=ACTIONS[:-2]+alias+b'}\n'
                _,(report,out)=self.plan(original)
                self.complete(report)
                self.assertEqual(report['coverage']['existing_car_locations'],1)
                self.assertEqual(report['coverage']['already_supported'],1)
                self.assertEqual(out,{})

    def test_decimal_reviewed_action_ids_and_standalone_alias_are_normalized(self):
        original=source(standalones=((500,500.,0.,'custom_rest'),))
        alias=b'trigger_action : trig_action.custom_rest {\n command: "hud_activate"\n num_params[]: 3.0\n str_params[]: "car"\n}\n'
        original['def/world/trigger_action.sii']=ACTIONS[:-2].replace(b'num_params[]: 3',b'num_params[]: 3.000000')+alias+b'}\n'
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(out,{})

    def test_invalid_or_nonfinite_hud_parameters_block_missing_car_decision(self):
        for spelling in ('nan','inf','1e999','dynamic_id','3_0'):
            with self.subTest(spelling=spelling):
                original=source()
                alias=('trigger_action : trig_action.custom_rest {\n command: "hud_activate"\n'
                       ' num_params[]: '+spelling+'\n str_params[]: "car"\n}\n').encode()
                original['def/world/trigger_action.sii']=ACTIONS[:-2]+alias+b'}\n'
                _,(report,out)=self.plan(original)
                self.assertFalse(report['coverage']['complete'])
                self.assertIn('HUD numeric parameter',str(report['coverage']['blockers']))
                self.assertEqual(out,{})

    def test_other_finite_hud_id_does_not_supply_car_rest(self):
        original=source(groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                                ('custom_rest',[(500.,0.),(510.,0.),(510.,10.),(500.,10.)])])
        alias=b'trigger_action : trig_action.custom_rest {\n command: "hud_activate"\n num_params[]: 2.0\n str_params[]: "car"\n}\n'
        original['def/world/trigger_action.sii']=ACTIONS[:-2]+alias+b'}\n'
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['existing_car_locations'],0)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertTrue(out)

    def test_extra_rest_hud_parameters_block_unreviewed_semantics(self):
        original=source()
        alias=b'trigger_action : trig_action.custom_rest {\n command: "hud_activate"\n num_params[]: 3.0\n num_params[]: 4.0\n str_params[]: "car"\n}\n'
        original['def/world/trigger_action.sii']=ACTIONS[:-2]+alias+b'}\n'
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('parameter list',str(report['coverage']['blockers']))
        self.assertEqual(out,{})

    def test_real_common_trigger_flags_preserved_and_guarded_locations_indexed(self):
        for flags in (0x4,0xc,0xd,0x1c,0x1d,0x140c,0x1d0d,0x4320c,0x4000d):
            with self.subTest(flags=hex(flags)):
                original=source(placements=())
                raw,nodes=standalone(700,0.,0.,'hud_parking',flags=flags)
                original[SECTOR]=sector([raw],nodes)
                _,(report,out)=self.plan(original)
                self.complete(report)
                self.assertEqual(report['coverage']['added_car_polygons'],1)
                self.assertEqual(parse_sector(out[SECTOR]).items[0].flags,flags)
                self.assertEqual(report['scope']['guarded_standalone_rest_locations'],bool(flags&0xff00))

    def test_unknown_or_unsupported_source_activation_modes_block_edits(self):
        for flags in (0x4c,0xe,0x2c,0x8000000c):
            with self.subTest(flags=hex(flags)):
                original=source(placements=())
                raw,nodes=standalone(700,0.,0.,'hud_parking',flags=flags)
                original[SECTOR]=sector([raw],nodes)
                _,(report,out)=self.plan(original)
                self.assertFalse(report['coverage']['complete'])
                self.assertEqual(out,{})

    def test_disabled_or_nonvehicle_car_trigger_does_not_suppress_addition(self):
        for flags in (0x1000c,0x8):
            with self.subTest(flags=hex(flags)):
                original=source()
                parsed=parse_sector(original[SECTOR]); data=original[SECTOR]
                raw,nodes=standalone(700,500.,0.,flags=flags)
                original[SECTOR]=sector([data[i.offset:i.end] for i in parsed.items]+[raw],
                                       [n.raw for n in parsed.nodes]+nodes)
                _,(report,out)=self.plan(original)
                self.complete(report)
                self.assertEqual(report['coverage']['existing_car_locations'],0)
                self.assertEqual(report['coverage']['added_car_polygons'],1)
                self.assertEqual(len(report['excluded_rest_locations']),1)

    def test_real_two_node_sphere_semantics_use_center_and_node_separation(self):
        uid=700; nodes=(2700,2701)
        raw=item(0x22,uid,refs()+refs(*nodes)+struct.pack('<IQI',1,token('parking_car'),0xffffffff),
                 flags=0x4000d)
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':
            sector([raw],[map_node(nodes[0],1025.,0.,uid),map_node(nodes[1],1040.,0.,uid)])})
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['locations'][0]['nearest_car_distance'],1000)
        self.assertEqual(out,{})

    def test_far_regions_are_not_read_and_empty_source_reservations_do_not_expand_halo(self):
        original=source(); original['map/usa/sec+0100+0100.base']=sector([])
        baseline=self.package('baseline',{'map/usa/sec+0101+0100.base':b'far invalid data',
                                           'map/usa/sec-0100-0100.base':b'far invalid data'})
        _,(report,out)=self.plan(original,before=[baseline])
        self.complete(report)
        self.assertEqual(report['sectors_inspected'],2)
        self.assertEqual(report['scope']['halo_sector_count'],0)
        self.assertEqual(report['scope']['nonempty_source_sector_count'],1)
        self.assertTrue(out)

    def test_unparsed_neighbor_is_reported_omission_with_accepted_boundary_addition(self):
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':b'unsupported neighbor'})
        _,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertEqual(len(report['scope']['omissions']),1)
        self.assertTrue(report['scope']['boundary_over_additions_accepted'])
        self.assertTrue(out)

    def test_halo_scales_with_radius_and_far_car_can_be_missed_explicitly(self):
        raw,nodes=standalone(700,500.,0.)
        baseline=self.package('baseline',{'map/usa/sec+0002+0000.base':sector([raw],nodes)})
        p,(report,out)=self.plan(source(),before=[baseline])
        self.complete(report)
        self.assertEqual(report['scope']['halo_steps'],1)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        larger,changes=plan_rest_stops(ResourceStack([baseline,p]),map_packages={str(p.path)},
                                       radius=4001,map_name='fixture')
        self.complete(larger)
        self.assertEqual(larger['scope']['halo_steps'],2)
        self.assertEqual(larger['coverage']['already_supported'],1)
        self.assertEqual(changes,{})

    def test_deterministic_and_radius_validation(self):
        p,(report,out)=self.plan(source())
        self.complete(report)
        stack=ResourceStack([p]); kwargs=dict(map_packages={str(p.path)},map_name='fixture')
        self.assertEqual((report,out),plan_rest_stops(stack,**kwargs))
        for radius in (-1,float('inf'),float('nan'),True,False,'1000',None):
            with self.assertRaises(ValueError):
                plan_rest_stops(stack,radius=radius,**kwargs)


if __name__=='__main__':
    unittest.main()
