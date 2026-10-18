"""Authored geometry fixtures exercise eligibility, scope and processor composition."""
from pathlib import Path
import hashlib
import struct
import tempfile
import unittest
from unittest.mock import patch

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_layer,parse_sector
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


def standalone(uid,x,z,action='parking_car',custom=False,sphere=None,flags=0x0c,extra_actions=(),two_node_sphere=False,tags=()):
    points=([(x,z),(x+10,z)] if two_node_sphere else
            ([(x,z)] if sphere is not None else [(x,z),(x+10,z),(x+10,z+10),(x,z+10)]))
    nodes=[uid+2000+i for i in range(len(points))]
    params=(struct.pack('<IfII fI',1,3.,0,0,0.,0) if custom else struct.pack('<I',0xffffffff))
    actions=(action,*extra_actions)
    action_bytes=struct.pack('<Q',token(action))+params
    action_bytes+=b''.join(struct.pack('<QI',token(name),0xffffffff) for name in extra_actions)
    raw=item(0x22,uid,refs(*(token(tag) for tag in tags))+refs(*nodes)+struct.pack('<I',len(actions))
             +action_bytes
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

    def test_prefab_car_groups_are_distinct_and_original_trigger_bytes_are_exact(self):
        original=source()
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertNotIn(PPD,out)
        self.assertNotIn('def/world/trigger_action.sii',out)
        self.assertEqual(report['car_action']['token'],'parking_car')
        self.assertFalse(any(path.startswith('def/world/trigger_action.') for path in out))
        private=next(data for path,data in out.items() if path.endswith('.ppd'))
        before_h=struct.unpack_from('<24I',original[PPD])
        after_h=struct.unpack_from('<24I',private)
        self.assertEqual(after_h[9],before_h[9]+4)
        self.assertEqual(after_h[21],before_h[21])
        self.assertEqual(after_h[22],before_h[22]+4*48)
        self.assertEqual(after_h[23],before_h[23]+4*48)
        self.assertEqual(private[before_h[21]:before_h[22]],original[PPD][before_h[21]:before_h[22]])
        groups=inspect_rest_triggers(private)
        self.assertEqual([g['action'] for g in groups],[token('hud_parking'),token('parking_car')])
        self.assertNotEqual(groups[0]['id'],groups[1]['id'])
        self.assertEqual(groups[0]['vertices'],inspect_rest_triggers(original[PPD])[0]['vertices'])
        self.assertEqual(groups[0]['flags'],groups[1]['flags'])
        self.assertEqual(groups[0]['vertices'],groups[1]['vertices'])
        # Car-group links point only at its appended records; truck links stay original.
        self.assertTrue(all(i >= before_h[9] for i in groups[1]['indices']))
        self.assertEqual(set(groups[0]['indices']),{0,1,2,3})
        before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
        self.assertEqual([n.raw for n in before.nodes],[n.raw for n in after.nodes])
        self.assertNotEqual(before.items[0].details['model'],after.items[0].details['model'])
        self.assertEqual(before.items[0].details['variant'],after.items[0].details['variant'])

    def test_multiple_selected_ppd_groups_get_fresh_ids_and_preserve_partial_flags(self):
        original=source(groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                                ('hud_parking',[(20.,0.),(30.,0.),(30.,10.),(20.,10.)])])
        raw=bytearray(original[PPD])
        # Partial source trigger flags are copied to each car group unchanged.
        for index in range(8):
            struct.pack_into('<I',raw,304+index*48+24,4)
        original[PPD]=bytes(raw)
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],2)
        before_h=struct.unpack_from('<24I',original[PPD])
        private=next(data for path,data in out.items() if path.endswith('.ppd'))
        after=inspect_rest_triggers(private)
        self.assertEqual([g['action'] for g in after],
                         [token('hud_parking'),token('hud_parking'),token('parking_car'),token('parking_car')])
        self.assertEqual([g['id'] for g in after[:2]],[0,1])
        self.assertEqual(len({g['id'] for g in after[2:]}),2)
        self.assertTrue(all(g['id'] not in {0,1} for g in after[2:]))
        self.assertEqual([g['flags'] for g in after],[4,4,4,4])
        self.assertEqual(private[before_h[21]:before_h[22]],
                         original[PPD][before_h[21]:before_h[22]])

    def test_nonselected_prefab_group_is_byte_identical(self):
        raw,nodes=standalone(500,1510.,0.)
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':sector([raw],nodes)})
        original=source(groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                                ('hud_parking',[(1500.,0.),(1510.,0.),(1510.,10.),(1500.,10.)])])
        _,(report,out)=self.plan(original,before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        before_h=struct.unpack_from('<24I',original[PPD])
        private=next(data for path,data in out.items() if path.endswith('.ppd'))
        after_h=struct.unpack_from('<24I',private)
        # The nonselected original group's complete records remain exactly at their old offsets.
        first=before_h[21]+4*48
        self.assertEqual(private[first:first+4*48],original[PPD][first:first+4*48])
        self.assertEqual(after_h[9],before_h[9]+4)

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

    def test_standalone_truck_action_clones_car_trigger_and_independent_nodes(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking',False,None,0x0d,
                                                    ('other_action',),False,('tag_enable','tag_disable')),))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
        self.assertEqual(after.item_count,before.item_count+1)
        self.assertEqual(after.node_count,before.node_count+4)
        after_nodes={n.uid:n for n in after.nodes}
        self.assertTrue(all(after_nodes[n.uid].raw==n.raw for n in before.nodes))
        self.assertFalse(any(p.endswith('.ppd') for p in out))
        original_item=before.items[0]
        self.assertEqual(original[SECTOR][original_item.offset:original_item.end],
                         out[SECTOR][after.items[0].offset:after.items[0].end])
        old_trigger=_standalone(original[SECTOR],original_item)
        clone_trigger=_standalone(out[SECTOR],after.items[1])
        self.assertEqual([a['action'] for a in old_trigger['actions']],
                         [token('hud_parking'),token('other_action')])
        self.assertEqual([a['action'] for a in clone_trigger['actions']],[token('parking_car')])
        self.assertEqual(clone_trigger['tags'],old_trigger['tags'])
        self.assertEqual(clone_trigger['tags'],(token('tag_enable'),token('tag_disable')))
        old_nodes={n.uid:n for n in before.nodes}
        new_nodes={n.uid:n for n in after.nodes if n.uid not in old_nodes}
        self.assertEqual(len(set(clone_trigger['nodes']) & set(old_nodes)),0)
        self.assertEqual(len(clone_trigger['nodes']),4)
        for old_uid,new_uid in zip(old_trigger['nodes'],clone_trigger['nodes']):
            self.assertEqual(old_nodes[old_uid].position,new_nodes[new_uid].position)
            self.assertEqual(old_nodes[old_uid].rotation,new_nodes[new_uid].rotation)
            self.assertEqual(old_nodes[old_uid].flags,new_nodes[new_uid].flags)
        self.assertEqual(after.visibility_children,before.visibility_children)

    def test_standalone_sphere_and_two_node_sphere_are_cloned_with_geometry(self):
        for label,args,expected_nodes in [
                ('one-node',((700,0.,0.,'hud_parking',False,5.),),1),
                ('two-node',((700,0.,0.,'hud_parking',False,None,0x0c,(),True),),2)]:
            with self.subTest(label=label):
                # One-node triggers carry an explicit radius. Two-node sphere-like
                # triggers derive the radius from their unchanged node separation.
                original=source(placements=(),standalones=args)
                _,(report,out)=self.plan(original)
                self.complete(report)
                before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
                self.assertEqual(after.node_count,before.node_count+expected_nodes)
                clone=_standalone(out[SECTOR],after.items[-1])
                self.assertEqual([a['action'] for a in clone['actions']],[token('parking_car')])
                self.assertEqual(clone['radius'],5. if expected_nodes==1 else 0.)
                self.assertEqual(len(clone['nodes']),expected_nodes)

    def test_irregular_standalone_geometry_is_cloned_in_original_node_order(self):
        original=self_crossing_standalones((700,'hud_parking',0.))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        before,after=parse_sector(original[SECTOR]),parse_sector(out[SECTOR])
        self.assertEqual(original[SECTOR][before.items[0].offset:before.items[0].end],
                         out[SECTOR][after.items[0].offset:after.items[0].end])
        old_nodes={n.uid:n for n in before.nodes}
        new_nodes={n.uid:n for n in after.nodes if n.uid not in old_nodes}
        old_ids=_standalone(original[SECTOR],before.items[0])['nodes']
        clone_ids=_standalone(out[SECTOR],after.items[1])['nodes']
        self.assertEqual(len(clone_ids),len(old_ids))
        for old_uid,new_uid in zip(old_ids,clone_ids):
            self.assertEqual(old_nodes[old_uid].position,new_nodes[new_uid].position)
            self.assertEqual(old_nodes[old_uid].rotation,new_nodes[new_uid].rotation)
            self.assertEqual(old_nodes[old_uid].flags,new_nodes[new_uid].flags)
        self.assertEqual([a['action'] for a in _standalone(out[SECTOR],after.items[1])['actions']],
                         [token('parking_car')])

    def test_rest_cloning_composes_over_previous_fuel_sector_overlay(self):
        original=source()
        overlay=bytearray(original[SECTOR])
        parsed=parse_sector(bytes(overlay))
        # Simulate an earlier processor's unrelated change to the same prefab.
        struct.pack_into('<Q',overlay,parsed.prefabs[0].offset+65,token('fuel_variant'))
        _,(report,out)=self.plan(original,overrides={SECTOR:bytes(overlay)})
        self.complete(report)
        changed=parse_sector(out[SECTOR])
        self.assertEqual(changed.prefabs[0].details['variant'],token('fuel_variant'))

    def test_standalone_twin_closes_visibility_and_layer_membership(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        sector_info=parse_sector(original[SECTOR])
        trigger=sector_info.items[0]
        trigger_raw=original[SECTOR][trigger.offset:trigger.end]
        visibility=item(0x30,900,struct.pack('<Qff',0,0.,0.)+refs(trigger.uid))
        original[SECTOR]=sector([trigger_raw,visibility],[n.raw for n in sector_info.nodes],[trigger.uid])
        layer_path='map/usa/sec+0000+0000.layer'
        original[layer_path]=(struct.pack('<IQI',907,token('euro2'),3)
                              +struct.pack('<QBQ',trigger.uid,2,0xffffffffffffffff))
        _,(report,out)=self.plan(original)
        self.complete(report)
        car_uid=int(report['standalone_twins'][0]['car_uid'],16)
        result=parse_sector(out[SECTOR])
        self.assertEqual(result.visibility_children,(trigger.uid,car_uid))
        area=next(item for item in result.items if item.kind==0x30)
        self.assertEqual(area.details['children'],(trigger.uid,car_uid))
        self.assertEqual(parse_layer(out[layer_path]),{trigger.uid:2,car_uid:2})

    def test_standalone_source_nodes_resolve_from_neighboring_source_aux_sector(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        parsed=parse_sector(original[SECTOR])
        trigger=parsed.items[0]
        trigger_raw=original[SECTOR][trigger.offset:trigger.end]
        original[SECTOR]=sector([trigger_raw],[])
        aux_path='map/usa/sec+0000+0000.aux'
        original[aux_path]=sector([],[n.raw for n in parsed.nodes])
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_standalone_triggers'],1)
        self.assertIn(SECTOR,out)
        self.assertNotIn(aux_path,out)
        after=parse_sector(out[SECTOR])
        old_ids=_standalone(original[SECTOR],parse_sector(original[SECTOR]).items[0])['nodes']
        clone=_standalone(out[SECTOR],after.items[-1])
        self.assertEqual(len(clone['nodes']),len(old_ids))
        self.assertTrue(set(old_ids).isdisjoint(clone['nodes']))

    def test_deterministic_standalone_uid_collision_blocks_all_output(self):
        collision_uid=0x123456789abcdef0
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        parsed=parse_sector(original[SECTOR])
        items=[original[SECTOR][value.offset:value.end] for value in parsed.items]
        items.append(item(8,collision_uid,struct.pack('<I',0)))
        original[SECTOR]=sector(items,[node.raw for node in parsed.nodes])
        real_sha256=hashlib.sha256

        class FixedDigest:
            def digest(self):
                return struct.pack('<Q',collision_uid)+bytes(24)

        def deterministic_collision(value=b''):
            if value.endswith(b':item'):
                return FixedDigest()
            return real_sha256(value)

        with patch('ats_road_trip.rest_stops.hashlib.sha256',side_effect=deterministic_collision):
            _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('Generated rest UID collision',str(report['coverage']['blockers']))
        self.assertEqual(out,{})

    def test_malformed_source_layer_blocks_generation(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        original['map/usa/sec+0000+0000.layer']=b'not a valid layer resource'
        _,(report,out)=self.plan(original)
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('layer',str(report['coverage']['blockers']).lower())
        self.assertEqual(out,{})

    def test_rest_twin_layer_composes_over_previous_fuel_layer_override(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        parsed=parse_sector(original[SECTOR])
        trigger=parsed.items[0]
        extra=item(8,900,struct.pack('<I',0))
        original[SECTOR]=sector([original[SECTOR][trigger.offset:trigger.end],extra],
                                [node.raw for node in parsed.nodes])
        layer_path='map/usa/sec+0000+0000.layer'
        header=struct.pack('<IQI',907,token('euro2'),3)
        original[layer_path]=header+struct.pack('<QBQBQ',700,2,900,4,0xffffffffffffffff)
        # Earlier fuel output changed an unrelated layer and introduced another membership.
        fuel_override=header+struct.pack('<QBQBQBQ',700,2,900,5,901,7,0xffffffffffffffff)
        _,(report,out)=self.plan(original,overrides={layer_path:fuel_override})
        self.complete(report)
        self.assertIn(layer_path,out)
        car_uid=int(report['standalone_twins'][0]['car_uid'],16)
        self.assertEqual(parse_layer(out[layer_path]),{700:2,900:5,901:7,car_uid:2})

    def test_foreign_baseline_visibility_reference_blocks_source_twin(self):
        original=source(placements=(),standalones=((700,0.,0.,'hud_parking'),))
        foreign_visibility=item(0x30,900,struct.pack('<Qff',0,0.,0.)+refs(700))
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':sector([foreign_visibility])})
        _,(report,out)=self.plan(original,before=[baseline])
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('non-source sector edit',str(report['coverage']['blockers']))
        self.assertEqual(out,{})

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

    def test_source_car_added_to_existing_truck_action_gets_car_only_marker_twin(self):
        original=source()
        original['def/world/trigger_action.sii']=ACTIONS.replace(
            b'str_params[]: "bus"',b'str_params[]: "bus"\n str_params[]: "car"')
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertEqual(report['coverage']['already_supported'],0)
        self.assertEqual(report['coverage']['marker_repairs_existing_car_permissions'],1)
        self.assertEqual(report['coverage']['new_car_permissions'],0)
        self.assertTrue(report['locations'][0]['original_car_eligible'])
        self.assertEqual(report['locations'][0]['addition_reason'],'repair_existing_car_marker')
        private=next(contents for path,contents in out.items() if path.endswith('.ppd'))
        original_h=struct.unpack_from('<24I',original[PPD])
        self.assertEqual(private[original_h[21]:original_h[22]],
                         original[PPD][original_h[21]:original_h[22]])
        self.assertEqual([group['action'] for group in inspect_rest_triggers(private)],
                         [token('hud_parking'),token('parking_car')])

    def test_truck_only_source_near_mixed_physical_car_neighbor_needs_no_new_eligibility(self):
        original=source(groups=[('truck_only',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)])])
        original['def/world/trigger_action.sii']=ACTIONS.replace(
            b'str_params[]: "bus"',b'str_params[]: "bus"\n str_params[]: "car"')[:-2]
        original['def/world/trigger_action.sii']+=b'trigger_action : trig_action.truck_only {\n command: "hud_activate"\n num_params[]: 3\n str_params[]: "truck"\n str_params[]: "bus"\n}\n}\n'
        mixed,nodes=standalone(500,1010.,0.,action='hud_parking')
        baseline=self.package('baseline',{'map/usa/sec+0001+0000.base':sector([mixed],nodes)})
        _,(report,out)=self.plan(original,before=[baseline])
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(report['coverage']['added_car_polygons'],0)
        self.assertEqual(report['coverage']['new_car_permissions'],0)
        self.assertEqual(out,{})

    def test_mixed_source_with_nearby_native_car_marker_needs_no_twin(self):
        original=source(groups=[('hud_parking',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                                ('parking_car',[(500.,0.),(510.,0.),(510.,10.),(500.,10.)])])
        original['def/world/trigger_action.sii']=ACTIONS.replace(
            b'str_params[]: "bus"',b'str_params[]: "bus"\n str_params[]: "car"')
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(report['coverage']['added_car_polygons'],0)
        self.assertEqual(report['coverage']['marker_repairs_existing_car_permissions'],0)
        self.assertEqual(out,{})

    def test_custom_mixed_hud_alias_gets_car_twin_and_car_only_alias_stays_indexed(self):
        original=source(groups=[('custom_mix',[(0.,0.),(10.,0.),(10.,10.),(0.,10.)]),
                                ('custom_car',[(3000.,0.),(3010.,0.),(3010.,10.),(3000.,10.)])])
        custom=('trigger_action : trig_action.custom_mix {\n command: "hud_activate"\n'
                ' num_params[]: 3\n str_params[]: "truck"\n str_params[]: "bus"\n'
                ' str_params[]: "car"\n}\n'
                'trigger_action : trig_action.custom_car {\n command: "hud_activate"\n'
                ' num_params[]: 3\n str_params[]: "car"\n}\n').encode()
        original['def/world/trigger_action.sii']=ACTIONS[:-2]+custom+b'}\n'
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['existing_car_locations'],2)
        self.assertEqual(report['coverage']['existing_car_marker_locations'],1)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertEqual(report['coverage']['marker_repairs_existing_car_permissions'],1)
        self.assertEqual(report['coverage']['new_car_permissions'],0)
        private=next(contents for path,contents in out.items() if path.endswith('.ppd'))
        original_h=struct.unpack_from('<24I',original[PPD])
        self.assertEqual(private[original_h[21]:original_h[22]],
                         original[PPD][original_h[21]:original_h[22]])
        groups=inspect_rest_triggers(private,actions={token('custom_mix'),token('custom_car'),
                                                       token('hud_parking'),token('parking_car')})
        self.assertEqual([(group['id'],group['action']) for group in groups],
                         [(0,token('custom_mix')),(1,token('custom_car')),(2,token('parking_car'))])
        self.assertEqual(groups[0]['vertices'],groups[2]['vertices'])
        self.assertEqual(sorted(groups[1]['vertices']),sorted([(3000.,0.,0.),(3010.,0.,0.),
                                                               (3010.,0.,10.),(3000.,0.,10.)]))

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

    def test_crossed_truck_without_vertex_proven_car_neighbor_gets_exact_car_twin(self):
        original=self_crossing_standalones((600,'hud_parking',0.))
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        self.assertEqual(len(report['conservative_proximity_for_irregular_source']),1)
        self.assertEqual(report['locations'][0]['proximity_method'],
                         'conservative_vertex_proof_only_for_original_irregular_polygon')
        before=original[SECTOR];after=out[SECTOR]
        original_sector,changed_sector=parse_sector(before),parse_sector(after)
        self.assertEqual(changed_sector.item_count,original_sector.item_count+1)
        self.assertEqual(before[original_sector.items[0].offset:original_sector.items[0].end],
                         after[changed_sector.items[0].offset:changed_sector.items[0].end])
        old_nodes={n.uid:n.raw for n in original_sector.nodes}
        self.assertTrue(all(n.raw==old_nodes[n.uid] for n in changed_sector.nodes if n.uid in old_nodes))
        clone=_standalone(after,changed_sector.items[-1])
        self.assertEqual([action['action'] for action in clone['actions']],[token('parking_car')])

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

    def test_partial_activation_flag4_and_original_records_are_preserved_in_car_clone(self):
        original=source()
        data=bytearray(original[PPD]);h=struct.unpack_from('<24I',data)
        for index in range(h[9]):
            struct.pack_into('<I',data,h[21]+48*index+24,4)
        original[PPD]=bytes(data)
        _,(report,out)=self.plan(original)
        self.complete(report)
        self.assertEqual(report['coverage']['added_car_polygons'],1)
        private=next(contents for path,contents in out.items() if path.endswith('.ppd'))
        after_h=struct.unpack_from('<24I',private)
        self.assertEqual(private[h[21]:h[22]],data[h[21]:h[22]])
        groups=inspect_rest_triggers(private)
        self.assertEqual([g['action'] for g in groups],[token('hud_parking'),token('parking_car')])
        self.assertEqual([g['flags'] for g in groups],[4,4])
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
        after=inspect_rest_triggers(private)
        self.assertEqual([(g['id'],g['action']) for g in after],
                         [(0,token('hud_parking')),(1,token('hud_parking')),
                          (2,token('parking_car')),(3,token('parking_car'))])

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
