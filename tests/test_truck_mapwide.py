"""Compound-based truck region selection and actual native sector composition."""
from pathlib import Path
from types import SimpleNamespace
import struct
import unittest
from unittest.mock import patch

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_layer,parse_sector
from ats_road_trip.resource_overlay import OverlayResourceStack
from ats_road_trip.rest_stops import _standalone
from ats_road_trip.truck_parking.mapwide import _select_regions,plan_map_truck_parking
from tests import test_truck_trigger as fixtures
from tests.test_map_sector import HEADER,item,node,refs,sector
from tests.test_rest_stops import standalone

SECTOR='map/usa/sec+0000+0000.base'
OTHER='map/usa/sec+0001+0000.base'
LAYER='map/usa/sec+0000+0000.layer'
OWNER='source.scs'
MODES={token('hud_parking'):{'truck','bus'},token('parking_car'):{'car'}}


class MemoryStack:
    def __init__(self,values,owners=None):
        self.values=values;self.packages=[];self.overrides=[]
        owners=owners or {}
        self.resources={p:(SimpleNamespace(path=Path(owners.get(p,OWNER))),None) for p in values}
    def read(self,path,**kwargs):
        return self.values[path]


def bank(area_id,vertices, *, lineage=('0xa',),provider=OWNER):
    return {'id':area_id,'uid':area_id,'sector':SECTOR,'source_provider':provider,
            'compound_lineage':list(lineage),'parent_uid':lineage[-1] if lineage else None,
            'vertices':vertices,'family':'authored-fixture'}


def census(data=None,banks=None):
    if data is None:
        data=fixtures.StandaloneTruckTriggerTests().native_sector()[0]
    parsed=parse_sector(data);source=next(i for i in parsed.items if i.uid==500)
    trigger=_standalone(data,source);nodes={n.uid:n for n in parsed.nodes}
    vertices=[nodes[u].position for u in trigger['nodes']]
    native={'uid':'0x1f4','sector':SECTOR,'source_provider':OWNER,'vertices':vertices,
        'polygon_xz':[(p[0],p[2]) for p in vertices],'height':sum(p[1] for p in vertices)/len(vertices),
        'flags':source.flags,'activation':{'vehicle_activation':True,'init_disabled':False},
        'actions':[{'token':token('hud_parking'),'custom':False,'vehicles':['truck','bus']}],
        '_nodes':{u:nodes[u] for u in trigger['nodes']}}
    return {'banks':banks if banks is not None else [bank('green',fixtures.NATIVE),bank('missing-bank',fixtures.BANK),bank('side',fixtures.SIDE)],
            'native_standalone':[native],'native_prefabs':[],'diagnostics':[],
            'visibility_references':{},'sector_count':1,'modes':MODES,
            'occupied_uids':{i.uid for i in parsed.items}|{n.uid for n in parsed.nodes}}


class TruckRegionSelectionTests(unittest.TestCase):
    def test_working_native_bank_does_not_exempt_uncovered_sibling_banks(self):
        classified,selected=_select_regions(census())
        self.assertEqual({r['id']:r['coverage_state'] for r in classified},
            {'green':'fully_covered','missing-bank':'uncovered','side':'uncovered'})
        self.assertEqual({r['id'] for r,s in selected},{'missing-bank','side'})
        green=next(r for r in classified if r['id']=='green')
        self.assertEqual(green['covering_native_uids'],['0x1f4'])
        self.assertTrue(all(source['uid']=='0x1f4' for row,source in selected))

    def test_geographic_proximity_does_not_associate_an_unrelated_facility(self):
        banks=[bank('green',fixtures.NATIVE),bank('related',fixtures.BANK),
               bank('unrelated',fixtures.SIDE,lineage=('0xb',)),
               bank('unowned',fixtures.SIDE,lineage=())]
        classified,selected=_select_regions(census(banks=banks))
        self.assertEqual([row['id'] for row,source in selected],['related'])
        for row in classified:
            if row['id'] in ('unrelated','unowned'):
                self.assertEqual(row['reason'],'no_unambiguous_native_standalone_compound_anchor')

    def test_partial_bank_selected_separately_and_covered_regions_are_retained(self):
        partial=[(20.,0.,0.),(50.,0.,0.),(50.,0.,22.),(20.,0.,22.)]
        classified,selected=_select_regions(census(banks=[bank('green',fixtures.NATIVE),bank('partial',partial)]))
        self.assertEqual(classified[1]['coverage_state'],'partially_covered')
        self.assertEqual(classified[1]['vertices'],partial)
        self.assertEqual([row['id'] for row,source in selected],['partial'])
        all_covered=census(banks=[bank('green',fixtures.NATIVE),bank('inside',[(2.,0.,2.),(8.,0.,2.),(8.,0.,10.),(2.,0.,10.)])])
        classified,selected=_select_regions(all_covered)
        self.assertEqual(selected,[])
        self.assertTrue(all(r['coverage_state']=='fully_covered' for r in classified))

    def test_native_full_containment_paint_edge_sliver_does_not_add_duplicate_marker(self):
        c=census();c['native_standalone'][0]['flags']=12
        original=fixtures.NATIVE
        expanded=[(x-.001 if x==min(p[0] for p in original) else x,y,z) for x,y,z in original]
        c['banks']=[bank('nearly-native-bank',expanded)]
        rows,selected=_select_regions(c)
        self.assertEqual(selected,[])
        self.assertTrue(rows[0]['operationally_covered'])
        self.assertGreater(rows[0]['native_edge_inset_preserved']['coverage_fraction'],.995)

    def test_material_same_bank_inset_requires_reviewed_extension_instead_of_colocated_marker(self):
        c=census();c['native_standalone'][0]['flags']=12
        original=fixtures.NATIVE
        low=min(p[0] for p in original)
        expanded=[(x-2. if x==low else x,y,z) for x,y,z in original]
        c['banks']=[bank('same-logical-bank',expanded)]
        rows,selected=_select_regions(c)
        self.assertEqual(selected,[])
        self.assertEqual(rows[0]['coverage_state'],'partially_covered')
        self.assertEqual(rows[0]['planning_action'],'unchanged_pending_safe_geometry_extension')

    def test_height_distance_provider_and_ambiguous_native_sources_are_safe_skips(self):
        elevated=[(x,y+2.,z) for x,y,z in fixtures.BANK]
        far=[(x+400,y,z) for x,y,z in fixtures.BANK]
        banks=[bank('green',fixtures.NATIVE),bank('elevated',elevated),bank('far',far),
               bank('other-provider',fixtures.BANK,provider='different.scs')]
        classified,selected=_select_regions(census(banks=banks))
        self.assertEqual(selected,[])
        duplicate=census();extra=dict(duplicate['native_standalone'][0],uid='0x999')
        duplicate['native_standalone'].append(extra)
        classified,selected=_select_regions(duplicate)
        self.assertEqual(selected,[])
        self.assertEqual(next(r for r in classified if r['id']=='missing-bank')['reason'],
                         'no_unambiguous_native_standalone_compound_anchor')

    def test_unknown_standalone_contract_or_sphere_blocks_only_overlapping_uncovered_banks(self):
        source_census=census()
        unknown={'uid':'0x999','vertices':fixtures.BANK,'contract_state':'unknown',
            'activation':{'vehicle_activation':False,'init_disabled':False}}
        source_census['native_standalone'].append(unknown)
        classified,selected=_select_regions(source_census)
        missing=next(r for r in classified if r['id']=='missing-bank')
        self.assertEqual(missing['coverage_state'],'unknown')
        self.assertEqual(missing['uncertain_native_uids'],['0x999'])
        self.assertEqual([r['id'] for r,s in selected],['side'])
        unknown['vertices']=fixtures.NATIVE
        classified,selected=_select_regions(source_census)
        self.assertEqual(classified[0]['coverage_state'],'fully_covered')
        unknown.pop('vertices')
        unknown.update(bounds_xyz=[39.,-1.,9.,101.,1.,36.],geometry_reason='unsupported sphere contract')
        classified,selected=_select_regions(source_census)
        self.assertEqual(next(r for r in classified if r['id']=='missing-bank')['coverage_state'],'unknown')
        self.assertEqual([r['id'] for r,s in selected],['side'])
        unknown['bounds_xyz']=[39.,99.,9.,101.,101.,36.]
        classified,selected=_select_regions(source_census)
        self.assertEqual({r['id'] for r,s in selected},{'missing-bank','side'})

    def test_unknown_prefab_vertical_contract_blocks_overlap_without_exempting_other_banks(self):
        source_census=census()
        source_census['native_prefabs']=[{'uid':'0xabc','world_polygons':[],
            'uncertain_polygons_xz':[[(p[0],p[2]) for p in fixtures.BANK]]}]
        classified,selected=_select_regions(source_census)
        missing=next(r for r in classified if r['id']=='missing-bank')
        self.assertEqual(missing['coverage_state'],'unknown')
        self.assertEqual(missing['reason'],'overlapping_native_prefab_has_unproven_vertical_transform')
        self.assertEqual([r['id'] for r,s in selected],['side'])

    def test_existing_prefab_truck_rest_prevents_duplicate_marker_on_a_sibling_bank(self):
        source_census=census()
        source_census['native_prefabs']=[{'uid':'0xabc','world_polygons':[{
            'id':5,'vertices':fixtures.BANK,'polygon_xz':[(p[0],p[2]) for p in fixtures.BANK],
            'height':0.,'vehicles':['truck','bus'],'flags':0}]}]
        classified,selected=_select_regions(source_census)
        row=next(r for r in classified if r['id']=='missing-bank')
        self.assertEqual(row['coverage_state'],'fully_covered')
        self.assertIn('0xabc',row['covering_native_uids'])
        self.assertEqual([r['id'] for r,source in selected],['side'])
        source_census['native_prefabs'][0]['world_polygons'][0]['height']=10.
        classified,selected=_select_regions(source_census)
        self.assertEqual({r['id'] for r,source in selected},{'missing-bank','side'})

    def test_unresolved_or_invalid_native_geometry_does_not_make_a_working_anchor(self):
        empty=census();empty['banks'].append(bank('unknown',[]))
        classified,selected=_select_regions(empty)
        self.assertEqual(classified[-1]['coverage_state'],'unknown')
        self.assertEqual(classified[-1]['reason'],'bank_has_no_resolved_world_geometry')
        disabled=census();disabled['native_standalone'][0]['activation']['init_disabled']=True
        classified,selected=_select_regions(disabled)
        self.assertFalse(selected)
        self.assertTrue(all(r['coverage_state']=='uncovered' for r in classified))


class TruckMapwideCompositionTests(unittest.TestCase):
    def plan(self,stack,original,source_census,**kwargs):
        with patch('ats_road_trip.truck_parking.mapwide._source_census',return_value=source_census), \
             patch('ats_road_trip.truck_parking.catalog.reviewed_placement_regions',return_value=[],create=True):
            return plan_map_truck_parking(stack,map_packages=kwargs.pop('map_packages',{OWNER}),
                map_name='Fixture',ownership_stack=original,**kwargs)

    def test_real_native_writer_retains_staged_fuel_car_records_and_original_source(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector()
        parsed=parse_sector(data)
        car,car_nodes=standalone(900,250.,250.,action='parking_car')
        service=item(7,1000,struct.pack('<QQ',1001,500)+refs(),flags=0x80004000)
        staged=sector([data[i.offset:i.end] for i in parsed.items]+[car,service],
            [n.raw for n in parsed.nodes]+car_nodes+[node(1001,1000)])
        original=MemoryStack({SECTOR:data,LAYER:layer})
        stack=OverlayResourceStack(original,{SECTOR:staged})
        report,resources=self.plan(stack,original,census(data))
        self.assertTrue(report['coverage']['complete'],report)
        self.assertEqual(report['added_truck_regions'],2)
        self.assertEqual(report['changed_facilities'],1)
        self.assertEqual(report['added_markers'],2)
        after=parse_sector(resources[SECTOR]);by_uid={i.uid:i for i in after.items}
        for old in parse_sector(staged).items:
            new=by_uid[old.uid]
            self.assertEqual(staged[old.offset:old.end],resources[SECTOR][new.offset:new.end])
        self.assertEqual(len(after.services),1)
        self.assertTrue(all(row['emitted']['vehicles']==['bus','truck'] for row in report['changed_locations']))
        self.assertFalse(report['native_car_improvement_gate_applied'])
        self.assertEqual(set(report['composed_resource_paths']),{SECTOR,LAYER})
        self.assertEqual(len(parse_layer(resources[LAYER])),3)

    def test_cross_sector_visibility_and_layer_membership_compose_all_new_regions(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector()
        visibility=item(0x30,600,struct.pack('<Qff',0,100.,200.)+refs(500))
        remote=sector([visibility],children=(500,))
        original=MemoryStack({SECTOR:data,LAYER:layer,OTHER:remote},owners={OTHER:'remote-owner.scs'})
        source_census=census(data);source_census['visibility_references']={500:[OTHER]}
        report,resources=self.plan(original,original,source_census)
        new_uids={int(r['emitted']['uid'],16) for r in report['changed_locations']}
        self.assertEqual(set(resources),{SECTOR,LAYER,OTHER})
        parsed=parse_sector(resources[OTHER])
        self.assertEqual(set(parsed.visibility_children),{500}|new_uids)
        self.assertEqual(set(parsed.items[0].details['children']),{500}|new_uids)
        self.assertEqual(set(parse_layer(resources[LAYER])),{500}|new_uids)
        self.assertEqual(str(original.resources[OTHER][0].path),'remote-owner.scs')

    def test_unsupported_native_contract_is_reported_without_partial_output(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector(flags=5)
        original=MemoryStack({SECTOR:data,LAYER:layer})
        report,resources=self.plan(original,original,census(data))
        self.assertEqual(resources,{})
        self.assertEqual(report['added_truck_regions'],0)
        self.assertEqual(report['skipped'][0]['reason'],'unsupported_native_writer_contract')
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector()
        original=MemoryStack({SECTOR:data,LAYER:layer,OTHER:sector([],children=(500,))})
        source_census=census(data);source_census['visibility_references']={500:[OTHER]}
        with patch('ats_road_trip.truck_parking.mapwide._extend_visibility',side_effect=ValueError('unsupported external visibility')):
            report,resources=self.plan(original,original,source_census)
        self.assertEqual(resources,{})
        self.assertEqual(report['changed_locations'],[])
        self.assertEqual(report['skipped'][0]['reason'],'unsupported_native_writer_contract')

    def test_required_reviewed_region_failure_blocks_completion(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector(flags=5)
        original=MemoryStack({SECTOR:data,LAYER:layer})
        source_census=census(data,banks=[bank('green',fixtures.NATIVE)])
        reviewed={'id':'required-side','vertices':fixtures.SIDE,'source_uid':'0x1f4',
                  'source_sector':SECTOR,'required':True}
        with patch('ats_road_trip.truck_parking.mapwide._source_census',return_value=source_census), \
             patch('ats_road_trip.truck_parking.catalog.reviewed_placement_regions',return_value=[reviewed],create=True):
            report,resources=plan_map_truck_parking(original,map_packages={OWNER},map_name='Fixture',ownership_stack=original)
        self.assertEqual(resources,{})
        self.assertFalse(report['coverage']['complete'])
        self.assertTrue(report['coverage']['blockers'])

    def test_cached_original_census_stays_immutable_and_repeated_planning_is_deterministic(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector()
        original=MemoryStack({SECTOR:data,LAYER:layer})
        source_census=census(data)
        original_ids=set(source_census['occupied_uids'])
        first=self.plan(original,original,source_census)
        second=self.plan(original,original,source_census)
        self.assertEqual(source_census['occupied_uids'],original_ids)
        self.assertEqual(first,second)
        self.assertEqual(first[0]['added_truck_regions'],2)

    def test_world_uid_collision_in_another_staged_sector_is_rejected_before_output(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector()
        original=MemoryStack({SECTOR:data,LAYER:layer})
        initial,_=self.plan(original,original,census(data))
        collision=int(initial['changed_locations'][0]['emitted']['uid'],16)
        staged=OverlayResourceStack(original,{OTHER:sector([],nodes=[node(collision)])})
        report,resources=self.plan(staged,original,census(data))
        self.assertEqual(resources,{})
        self.assertEqual(report['added_truck_regions'],0)
        self.assertIn('UID collision',report['skipped'][0]['detail'])

    def test_source_census_diagnoses_unknown_native_activation_and_keeps_global_identities(self):
        from ats_road_trip.truck_parking.mapwide import _source_census
        data,_,_=fixtures.StandaloneTruckTriggerTests().native_sector(flags=0x8000000d)
        original=MemoryStack({SECTOR:data})
        with patch('ats_road_trip.truck_parking.catalog.load_curve_definitions',return_value={}), \
             patch('ats_road_trip.truck_parking.catalog.reviewed_curve_catalog',return_value={}), \
             patch('ats_road_trip.truck_parking.mapwide.prefab_definitions',return_value={}), \
             patch('ats_road_trip.truck_parking.mapwide._native_modes',return_value=MODES), \
             patch('ats_road_trip.truck_parking.geometry.discover_curve_banks',return_value=([],[])):
            report=_source_census(original)
        self.assertEqual(len(report['native_standalone']),1)
        self.assertEqual(report['native_standalone'][0]['contract_state'],'unknown')
        self.assertTrue(report['native_standalone'][0]['vertices'])
        self.assertTrue(any(r['reason']=='unsupported_native_activation_contract' for r in report['diagnostics']))
        self.assertIn(500,report['occupied_uids'])
        self.assertTrue({n.uid for n in parse_sector(data).nodes}<=report['occupied_uids'])

    def test_census_keeps_unsupported_sphere_custom_parameters_and_missing_nodes_as_uncertainty(self):
        from ats_road_trip.truck_parking.mapwide import _source_census
        cases=[fixtures.StandaloneTruckTriggerTests().native_sector(custom=True)[0],
               fixtures.StandaloneTruckTriggerTests().native_sector(missing_node=True)[0]]
        sphere_raw,sphere_nodes=standalone(500,45.,15.,action='hud_parking',sphere=10.,flags=13)
        cases.append(sector([sphere_raw],sphere_nodes))
        for data in cases:
            original=MemoryStack({SECTOR:data})
            with self.subTest(size=len(data)), \
                 patch('ats_road_trip.truck_parking.catalog.load_curve_definitions',return_value={}), \
                 patch('ats_road_trip.truck_parking.catalog.reviewed_curve_catalog',return_value={}), \
                 patch('ats_road_trip.truck_parking.mapwide.prefab_definitions',return_value={}), \
                 patch('ats_road_trip.truck_parking.mapwide._native_modes',return_value=MODES), \
                 patch('ats_road_trip.truck_parking.geometry.discover_curve_banks',return_value=([],[])):
                report=_source_census(original)
            self.assertEqual(len(report['native_standalone']),1)
            self.assertEqual(report['native_standalone'][0]['contract_state'],'unknown')
            self.assertTrue(report['native_standalone'][0]['bounds_xyz'])
        invalid_sphere=bytearray(cases[-1])
        source_item=parse_sector(invalid_sphere).items[0]
        struct.pack_into('<f',invalid_sphere,source_item.end-4,float('nan'))
        original=MemoryStack({SECTOR:bytes(invalid_sphere)})
        with patch('ats_road_trip.truck_parking.catalog.load_curve_definitions',return_value={}), \
             patch('ats_road_trip.truck_parking.catalog.reviewed_curve_catalog',return_value={}), \
             patch('ats_road_trip.truck_parking.mapwide.prefab_definitions',return_value={}), \
             patch('ats_road_trip.truck_parking.mapwide._native_modes',return_value=MODES), \
             patch('ats_road_trip.truck_parking.geometry.discover_curve_banks',return_value=([],[])):
            report=_source_census(original)
        self.assertTrue(report['uncertain_standalone_bounds'])
        self.assertEqual(report['uncertain_standalone_bounds'][0]['uid'],'0x1f4')

    def test_native_modes_retains_unknown_and_nonrest_action_index(self):
        from ats_road_trip.truck_parking.mapwide import _native_modes
        indexed={token('hud_parking'):{'state':'rest','command':'hud_activate','vehicles':['truck','bus']},
                 token('odd_alias'):{'state':'unknown','command':'hud_activate'},
                 token('sound'):{'state':'nonrest','command':'play_sound','vehicles':[]}}
        stack=SimpleNamespace(prefetch=lambda *args:None)
        with patch('ats_road_trip.truck_parking.mapwide._action_index',return_value=indexed):
            modes=_native_modes(stack)
        self.assertEqual(modes,{token('hud_parking'):{'truck','bus'}})
        self.assertEqual(stack._truck_coverage_action_index,indexed)

    def test_undefined_unknown_and_custom_nonrest_hud_actions_are_bounded_uncertainty(self):
        from ats_road_trip.truck_parking.mapwide import _source_census
        base_index={key:{'state':'rest','command':'hud_activate','vehicles':sorted(vehicles)}
                    for key,vehicles in MODES.items()}
        cases=[('undefined',False,None,True),
               ('odd_alias',False,{'state':'unknown','command':'hud_activate'},True),
               ('other_hud',True,{'state':'nonrest','command':'hud_activate','vehicles':[]},True),
               ('parking_car',True,base_index[token('parking_car')],True),
               ('parking_car',False,base_index[token('parking_car')],False),
               ('sound',False,{'state':'nonrest','command':'play_sound','vehicles':[]},False),
               ('sound',True,{'state':'nonrest','command':'play_sound','vehicles':[]},False)]
        for name,custom,index_row,expected_unknown in cases:
            data,_,_=fixtures.StandaloneTruckTriggerTests().native_sector()
            before=parse_sector(data)
            extra,extra_nodes=standalone(800,40.,10.,action=name,custom=custom,flags=13)
            # Source native XYZ bounds include the extra action's actual
            # footprint, not the helper's generic local header bounds.
            extra=bytearray(extra)
            struct.pack_into('<10f',extra,12,38.75,-1.25,8.75,24.08,14.08,
                             51.25,1.25,21.25,35.92,20.92)
            combined=sector([data[i.offset:i.end] for i in before.items]+[bytes(extra)],
                [n.raw for n in before.nodes]+extra_nodes)
            original=MemoryStack({SECTOR:combined})
            index={**base_index}
            if index_row is not None:index[token(name)]=index_row
            original._truck_coverage_action_index=index
            fixture_banks=census()['banks']
            with self.subTest(name=name,custom=custom), \
                 patch('ats_road_trip.truck_parking.catalog.load_curve_definitions',return_value={}), \
                 patch('ats_road_trip.truck_parking.catalog.reviewed_curve_catalog',return_value={}), \
                 patch('ats_road_trip.truck_parking.mapwide.prefab_definitions',return_value={}), \
                 patch('ats_road_trip.truck_parking.mapwide._native_modes',return_value=MODES), \
                 patch('ats_road_trip.truck_parking.geometry.discover_curve_banks',return_value=(fixture_banks,[])):
                report=_source_census(original)
            classified,selected=_select_regions(report)
            missing=next(row for row in classified if row['id']=='missing-bank')
            self.assertEqual(missing['coverage_state'],'unknown' if expected_unknown else 'uncovered')
            self.assertEqual(bool(report['uncertain_standalone_bounds']),expected_unknown)
            self.assertEqual({row['id'] for row,source in selected},
                             {'side'} if expected_unknown else {'missing-bank','side'})
            if expected_unknown:
                self.assertEqual(missing['uncertain_native_uids'],['0x320'])
                self.assertTrue(any(row['reason']=='standalone_effective_action_or_custom_hud_unresolved'
                                    for row in report['diagnostics']))
            self.assertEqual(report['action_index'],index)

    def test_owner_partition_never_emits_another_source_facility(self):
        data,layer,_=fixtures.StandaloneTruckTriggerTests().native_sector()
        original=MemoryStack({SECTOR:data,LAYER:layer})
        report,resources=self.plan(original,original,census(data),map_packages={'not-source.scs'})
        self.assertEqual(resources,{})
        self.assertEqual(report['added_truck_regions'],0)
        self.assertEqual(report['native_standalone_count'],0)


if __name__=='__main__':
    unittest.main()


class TruckSourceCacheCompositionTests(unittest.TestCase):
    def test_full_source_census_uses_the_shared_archive_package_cache(self):
        from tempfile import TemporaryDirectory
        import hashlib
        from ats_road_trip.archive import Archive
        from ats_road_trip.truck_parking.mapwide import _source_census
        calls=[]
        package=SimpleNamespace(path=Path('/source.scs'),prefetch=lambda names,**kwargs:calls.append((names,kwargs)))
        original=SimpleNamespace(packages=[package],resources={SECTOR:(package,None)},read=lambda *a,**k:sector([],[]))
        with TemporaryDirectory() as directory, \
             patch.object(Archive,'_work_root',Path(directory)), \
             patch('ats_road_trip.truck_parking.catalog.load_curve_definitions',return_value={}), \
             patch('ats_road_trip.truck_parking.catalog.reviewed_curve_catalog',return_value={}), \
             patch('ats_road_trip.truck_parking.mapwide.prefab_definitions',return_value={}), \
             patch('ats_road_trip.truck_parking.mapwide._native_modes',return_value={}):
            _source_census(original,work_dir=Path(directory)/'some-owner'/'truck-parking')
            key=hashlib.sha256(str(package.path).encode()).hexdigest()[:12]
            self.assertEqual(calls[0][1]['disk_cache'],Path(directory)/'package-cache'/key)
            self.assertEqual(calls[0][0],[SECTOR])
