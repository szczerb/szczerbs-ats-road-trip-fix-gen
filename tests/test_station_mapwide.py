"""Map-wide family selection and composition use authored fixture resources."""
from copy import deepcopy
import hashlib
import struct
import unittest
from unittest.mock import patch

from ats_road_trip.bulk_fuel import plan_map_fuel
from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import ResourceStack
from ats_road_trip.station_parking.mapwide import plan_map_station_parking, _compose, _service_context
from tests import test_station_effective_planning as effective_fixtures
from tests.test_bulk_fuel import PPD,SECTOR


class MapStationParkingTests(unittest.TestCase):
    def setUp(self):
        self.fixture=effective_fixtures.EffectivePlanningTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.package=self.fixture.package;self.stack=self.fixture.stack
        from ats_road_trip.archive import Archive
        previous_work=Archive._work_root
        Archive.configure_work_root(self.fixture.helper.root/'scratch')
        self.addCleanup(lambda:Archive.configure_work_root(previous_work))
        config=self.fixture.config
        self.catalog={'prefab/test/station.pmd':{
            'family':'authored-marked','model_geometry':config['model_geometry'],
            'fingerprints':{key:config['fingerprints'][key] for key in
                            ('model_definition','model_geometry','mesh','mesh_state')},
            'mesh_materials':deepcopy(config['mesh_materials']),
            'material_resources':deepcopy(config['material_resources']),
            'mesh_text':self.fixture.helper.mesh,'mesh_state_text':self.fixture.pit,
            'methods':['painted_bays'],'parameters':{},'source_descriptors':[PPD],
            'policy':{'single_painted_bays':True}}}

    def plan(self,stack=None,**kwargs):
        return plan_map_station_parking(stack or self.stack,map_packages={str(self.package.path)},
            map_name='Authored Map',catalog=self.catalog,ownership_stack=self.stack,**kwargs)

    def test_discovers_family_without_uid_manifest_and_preserves_services(self):
        report,resources=self.plan()
        self.assertEqual(report['coverage']['generated'],1,report['locations'])
        self.assertEqual(report['coverage']['generated_truck_area_access'],0)
        row=report['locations'][0]
        self.assertEqual(row['state'],'generated')
        self.assertEqual(row['selected']['bay_count'],3)
        self.assertEqual(row['area_count'],1)
        self.assertEqual(row['native_car_parking']['state'],'absent')
        self.assertEqual(row['source_pins']['descriptor'],hashlib.sha256(self.package.read(PPD)).hexdigest())
        before=parse_sector(self.package.read(SECTOR));after=parse_sector(resources[SECTOR])
        self.assertEqual(before.nodes,after.nodes)
        self.assertEqual(before.services,after.services)
        self.assertEqual(report['composed_resource_paths'],[SECTOR])

    def test_declared_archive_without_owned_base_sectors_is_not_hashed(self):
        import zipfile
        from ats_road_trip.package import Package
        from ats_road_trip.station_parking import mapwide
        path=self.fixture.helper.root/'resource-only.scs'
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr('authored-resource.txt',b'No map sectors in this large resource archive')
        resource_only=Package(path);self.addCleanup(resource_only.close)
        raw=ResourceStack([resource_only,self.package])
        with patch('ats_road_trip.station_parking.mapwide._file_hash',wraps=mapwide._file_hash) as file_hash:
            report,resources=plan_map_station_parking(raw,
                map_packages={str(path),str(self.package.path)},map_name='Authored Map',
                catalog=self.catalog,ownership_stack=raw)
        self.assertEqual([call.args[0] for call in file_hash.call_args_list],[self.package.path])
        self.assertEqual(report['declared_source_archives'],sorted([str(path),str(self.package.path)]))
        self.assertEqual(set(report['source_archive_sha256']),{str(self.package.path)})
        self.assertEqual(report['coverage']['generated'],1)
        self.assertTrue(resources)
        with patch('ats_road_trip.station_parking.mapwide._file_hash') as file_hash:
            report,resources=plan_map_station_parking(raw,map_packages={str(path)},
                map_name='Resource Only',catalog=self.catalog,ownership_stack=raw)
        file_hash.assert_not_called()
        self.assertEqual(report['source_archive_sha256'],{})
        self.assertEqual(report['coverage']['locations'],0)
        self.assertEqual(resources,{})

    def test_no_candidate_has_no_fallback_and_is_complete_supported_subset(self):
        self.catalog['prefab/test/station.pmd']['mesh_materials']['paint']=[]
        report,resources=self.plan()
        self.assertEqual(resources,{})
        self.assertTrue(report['coverage']['complete'])
        self.assertEqual(report['coverage']['generated_truck_area_access'],0)
        self.assertEqual(report['coverage']['skipped'],1)
        self.assertEqual(report['locations'][0]['reason'],'no_safe_dedicated_candidate')

    def test_model_and_material_drift_skip_without_guessing(self):
        self.catalog['prefab/test/station.pmd']['fingerprints']['model_definition']='0'*64
        report,resources=self.plan()
        self.assertEqual(resources,{})
        self.assertIn('reviewed_effective_model_drift',report['locations'][0]['reason'])

    def test_unsupported_layout_remains_unchanged_with_coverage_count(self):
        self.catalog={}
        report,resources=self.plan()
        self.assertEqual(resources,{})
        self.assertEqual(report['skip_reasons'],{'unsupported_model_family':1})

    def test_context_cache_reuses_one_stack_and_isolates_new_overlay_and_reports(self):
        from ats_road_trip.resource_overlay import OverlayResourceStack
        from ats_road_trip.station_parking.planner import plan_station_parking
        from ats_road_trip import prefab_contexts
        cache={}
        def plan(stack):
            return plan_station_parking(stack,self.fixture.config,self.fixture.helper.mesh,
                map_package=str(self.package.path),game_version='1.61.3.18',
                mesh_state_text=self.fixture.pit,planning_cache=cache)
        with patch('ats_road_trip.prefab_contexts._effective_prefabs',wraps=prefab_contexts._effective_prefabs) as prefabs:
            first,resources=plan(self.stack)
            first['context_preservation']['aliases'][0]['original_contexts'][0]['tags']=('tampered',)
            second,_=plan(self.stack)
            self.assertEqual(prefabs.call_count,1)
            self.assertEqual(second['context_preservation']['aliases'][0]['tags'],['gas_station'])
            overlay=OverlayResourceStack(self.stack,{'def/data_context.sii':
                self.stack.read('def/data_context.sii').replace(b'gas_station',b'urban')})
            third,_=plan(overlay)
            self.assertEqual(prefabs.call_count,2)
            self.assertEqual(third['context_preservation']['aliases'][0]['tags'],['urban'])

    def test_source_descriptor_drift_outside_reviewed_family_is_skipped(self):
        self.catalog['prefab/test/station.pmd']['source_descriptors']=['prefab/test/different.ppd']
        report,resources=self.plan()
        self.assertEqual(resources,{})
        self.assertEqual(report['locations'][0]['reason'],'original_descriptor_not_reviewed_for_model_family')

    def test_original_ownership_survives_fuel_overlay_and_preserves_added_fuel(self):
        from ats_road_trip.resource_overlay import OverlayResourceStack
        fuel_report,fuel_resources=plan_map_fuel(self.stack,map_packages={str(self.package.path)},map_name='Authored Map')
        self.assertTrue(fuel_report['coverage']['complete'])
        overlay=OverlayResourceStack(self.stack,fuel_resources)
        report,resources=self.plan(stack=overlay)
        self.assertEqual(report['coverage']['generated'],1,report['locations'])
        before=parse_sector(overlay.read(SECTOR));after=parse_sector(resources[SECTOR])
        self.assertEqual(before.services,after.services)
        old_descriptor=report['locations'][0]['descriptor']
        changed=next(data for path,data in resources.items() if path.endswith('.ppd'))
        from ats_road_trip.station_parking.trigger import append_car_parking_polygon
        selected=report['locations'][0]['selected']['model_surface_checks']['vertices_xyz']
        expected,_=append_car_parking_polygon(overlay.read(old_descriptor),selected,partial_activation=True)
        self.assertEqual(changed,expected)

    def test_repeated_family_at_new_uid_is_discovered(self):
        # Change the original source UID and its backlinks, proving selection is
        # independent of the old explicit sample UID rather than adding one to it.
        contents={p:self.package.read(p) for p in self.package.files}
        raw=contents[SECTOR];needle=struct.pack('<Q',100);replacement=struct.pack('<Q',101)
        contents[SECTOR]=raw.replace(needle,replacement)
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)
        report,resources=self.plan()
        self.assertEqual(report['coverage']['generated'],1,report['locations'])
        self.assertEqual(report['locations'][0]['prefab_uid'],'0x65')

    def test_multiple_discovered_stations_in_one_sector_keep_both_patches(self):
        from tests.test_station_parking_batch import clone_station
        from tests.test_map_sector import sector as build_sector
        contents={p:self.package.read(p) for p in self.package.files}
        before=contents[SECTOR];parsed=parse_sector(before)
        entries,nodes=clone_station(before)
        moved=[]
        for source in nodes:
            data=bytearray(source)
            x=struct.unpack_from('<i',data,8)[0]
            struct.pack_into('<i',data,8,x+200*256)
            moved.append(bytes(data))
        contents[SECTOR]=build_sector([before[i.offset:i.end] for i in parsed.items]+entries,
                                     [n.raw for n in parsed.nodes]+moved)
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)
        report,resources=self.plan()
        self.assertEqual(report['coverage']['generated'],2,report['locations'])
        after=parse_sector(resources[SECTOR])
        original=parse_sector(contents[SECTOR])
        self.assertEqual(original.services,after.services)
        self.assertEqual(original.nodes,after.nodes)
        self.assertTrue(all(a.details['model']!=b.details['model'] for a,b in zip(original.prefabs,after.prefabs)))
        self.assertEqual(len(report['changed_sectors'][0]['allowed_changed_byte_ranges']),2)

    def test_cross_sector_fuel_service_nodes_are_resolved_without_losing_records(self):
        from tests.test_map_sector import sector as build_sector
        contents={p:self.package.read(p) for p in self.package.files}
        raw=contents[SECTOR];parsed=parse_sector(raw)
        prefab_items=[raw[i.offset:i.end] for i in parsed.prefabs]
        service_items=[raw[i.offset:i.end] for i in parsed.services]
        prefab_node_ids={uid for item in parsed.prefabs for uid in item.details['nodes']}
        contents[SECTOR]=build_sector(prefab_items,[n.raw for n in parsed.nodes if n.uid in prefab_node_ids])
        neighbor='map/usa/sec+0001+0000.aux'
        contents[neighbor]=build_sector(service_items,[n.raw for n in parsed.nodes if n.uid not in prefab_node_ids])
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)
        report,resources=self.plan()
        self.assertEqual(report['coverage']['generated'],1,report['locations'])
        self.assertNotIn(neighbor,resources)
        self.assertEqual(self.stack.read(neighbor),contents[neighbor])
        self.assertTrue(report['locations'][0]['planner']['fuel_graph_validation']['complete'])

    def test_native_car_bank_is_preserved_and_never_gets_a_truck_fallback(self):
        from ats_road_trip.station_parking.trigger import append_car_parking_polygon
        contents={p:self.package.read(p) for p in self.package.files}
        contents[PPD],_=append_car_parking_polygon(contents[PPD],
            [(-20.,0.,-20.),(20.,0.,-20.),(20.,0.,20.),(-20.,0.,20.)])
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)
        report,resources=self.plan()
        self.assertEqual(resources,{})
        self.assertEqual(report['coverage']['already_supported'],1)
        self.assertEqual(report['coverage']['generated_truck_area_access'],0)

    def test_generated_private_baseline_is_rejected_as_original_ownership(self):
        from ats_road_trip.resource_overlay import OverlayResourceStack
        original=OverlayResourceStack(self.stack,{'prefab/rtfix/old-r9.ppd':b'generated old fix'})
        with self.assertRaisesRegex(ValueError,'Original ownership stack contains generated'):
            plan_map_station_parking(original,map_packages={str(self.package.path)},
                map_name='Authored Map',catalog=self.catalog)

    def test_invalid_method_and_missing_source_are_configuration_errors(self):
        with self.assertRaisesRegex(ValueError,'Select automatic'):
            self.plan(method='truck')
        with self.assertRaisesRegex(ValueError,'No declared original'):
            plan_map_station_parking(self.stack,map_packages={'missing.scs'},map_name='Map',catalog=self.catalog)

    def test_composition_rejects_overlapping_placement_patches(self):
        report,resources=self.plan();planner=report['locations'][0]['planner']
        with self.assertRaisesRegex(ValueError,'Conflicting station placement'):
            _compose(self.stack,[(planner,resources),(planner,resources)])

    def test_unrelated_malformed_custom_action_does_not_abort_parking(self):
        contents={p:self.package.read(p) for p in self.package.files}
        contents['def/world/trigger_action.custom.sii']=b'SiiNunit { trigger_action : trig_action.bad_custom { command: hud_activate num_params[]: broken str_params[]: car } }'
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)
        report,resources=self.plan()
        self.assertTrue(resources,report['locations'])
        self.assertEqual(report['locations'][0]['native_car_parking']['state'],'absent')

    def remove_native_fueling(self):
        from tests.test_map_sector import item,refs,sector
        contents={p:self.package.read(p) for p in self.package.files}
        ppd=contents[PPD];h=list(struct.unpack_from('<24I',ppd))
        start=h[16]+36;end=start+36
        h[5]-=1
        for i in range(17,24):h[i]-=36
        contents[PPD]=struct.pack('<24I',*h)+ppd[96:start]+ppd[end:]
        parsed=parse_sector(contents[SECTOR]);pf=parsed.prefabs[0]
        services=[x for x in parsed.services if not x.flags & 0x4000]
        slave_ids=[x.uid for x in services]
        new_pf=item(4,pf.uid,struct.pack('<QQ',pf.details['model'],pf.details['variant'])+refs()
            +refs(*pf.details['nodes'])+refs(*slave_ids)+struct.pack('<QH',0,pf.details['origin'])
            +bytes(len(pf.details['nodes'])*12+8))
        wanted=set(pf.details['nodes'])|{x.details['node'] for x in services}
        original=contents[SECTOR]
        contents[SECTOR]=sector([new_pf]+[original[x.offset:x.end] for x in services],
            [n.raw for n in parsed.nodes if n.uid in wanted])
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)

    def add_native_small_area(self):
        from ats_road_trip.station_parking.trigger import append_car_parking_polygon
        contents={p:self.package.read(p) for p in self.package.files}
        contents[PPD],_=append_car_parking_polygon(contents[PPD],
            [(-18.,0.,-18.),(-14.,0.,-18.),(-14.,0.,-14.),(-18.,0.,-14.)])
        self.package,self.stack,_=self.fixture.helper.make_stack(contents)

    def test_native_support_exempts_entire_station_until_improvement_opt_in(self):
        from ats_road_trip.rest_stops import inspect_rest_triggers
        self.add_native_small_area()
        off,resources=self.plan()
        self.assertFalse(resources)
        self.assertEqual(off['locations'][0]['native_car_parking']['state'],'present')
        self.assertEqual(off['coverage']['already_supported'],1)
        on,resources=self.plan(improve_existing_car_parking=True)
        self.assertTrue(resources,on['locations'])
        row=on['locations'][0]
        self.assertEqual(row['state'],'generated')
        self.assertTrue(on['improve_existing_car_parking'])
        old=inspect_rest_triggers(self.stack.read(PPD))
        after=inspect_rest_triggers(next(data for name,data in resources.items() if name.endswith('.ppd')))
        self.assertEqual(after[:len(old)],old)
        self.assertTrue(all(g['flags']==4 for g in after[len(old):]))

    def test_existing_car_parking_never_suppresses_missing_fueling(self):
        from ats_road_trip.processors import ProcessorConfig,run_processors
        self.remove_native_fueling()
        self.add_native_small_area()
        def fuel(stack,game,*,source,map_name,**kwargs):
            return plan_map_fuel(stack,map_packages={source},map_name=map_name)
        with patch('ats_road_trip.processors._fuel_plan',side_effect=fuel), \
             patch('ats_road_trip.station_parking.catalog.load_reviewed_catalog',return_value=self.catalog):
            # mapwide imports its loader directly, so patch that reference too.
            with patch('ats_road_trip.station_parking.mapwide.load_reviewed_catalog',return_value=self.catalog):
                result=run_processors(self.stack,self.stack,source=str(self.package.path),
                    map_name='Authored Map',config=ProcessorConfig.from_preset('realistic'))
        self.assertTrue(result.coverage['complete'],result.blockers)
        self.assertEqual(result.reports['fuel']['coverage']['added_car_points'],1)
        self.assertEqual(result.reports['rest']['coverage']['already_supported'],1)
        self.assertEqual(result.reports['rest']['coverage']['generated'],0)
        after=parse_sector(result.resources[SECTOR])
        before=parse_sector(self.stack.read(SECTOR))
        self.assertEqual(len(after.services),len(before.services)+1)

    def test_existing_car_fueling_does_not_suppress_missing_parking(self):
        fuel,fuel_resources=plan_map_fuel(self.stack,map_packages={str(self.package.path)},map_name='Authored Map')
        self.assertEqual(fuel['coverage']['added_car_points'],0)
        report,resources=self.plan()
        self.assertEqual(report['coverage']['generated'],1,report['locations'])
        self.assertEqual(report['locations'][0]['native_car_parking']['state'],'absent')
        self.assertEqual(parse_sector(resources[SECTOR]).services,parse_sector(self.stack.read(SECTOR)).services)

    def test_unknown_parking_does_not_cancel_independently_added_fuel(self):
        self.remove_native_fueling()
        from ats_road_trip.processors import ProcessorConfig,run_processors
        def fuel(stack,game,*,source,map_name,**kwargs):
            return plan_map_fuel(stack,map_packages={source},map_name=map_name)
        with patch('ats_road_trip.processors._fuel_plan',side_effect=fuel), \
             patch('ats_road_trip.station_parking.mapwide.load_reviewed_catalog',return_value=self.catalog), \
             patch('ats_road_trip.station_parking.native_support.classify_native_car_parking',
                   return_value={'state':'unknown','reasons':['authored unresolved boundary'],'scope':{}}):
            result=run_processors(self.stack,self.stack,source=str(self.package.path),
                map_name='Authored Map',config=ProcessorConfig.from_preset('realistic'))
        self.assertTrue(result.coverage['complete'],result.blockers)
        self.assertEqual(result.reports['fuel']['coverage']['added_car_points'],1)
        self.assertEqual(result.reports['rest']['skip_reasons'],{'original_native_car_parking_unknown':1})
        self.assertIn(SECTOR,result.resources)


if __name__=='__main__':unittest.main()
