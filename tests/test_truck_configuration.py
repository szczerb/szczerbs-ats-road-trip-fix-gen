"""Independent truck option reaches CLI, config and authoritative composition."""
from contextlib import redirect_stderr,redirect_stdout
import io
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ats_road_trip.cli import main,parser
from ats_road_trip.processors import (
    ParkingStrategy,Processor,ProcessorConfig,ProcessorMode,run_processors,
)

SECTOR='map/usa/sec+0000+0000.base'


def original_stack():
    return SimpleNamespace(resources={SECTOR:('original-provider','resource')},
                           packages=[],overrides=[],read=lambda path,**kwargs:b'original-sector')


def complete(**kwargs):
    return {'coverage':{'complete':True,'blockers':[]},**kwargs}


class TruckConfigurationTests(unittest.TestCase):
    def test_default_off_and_strict_boolean_rest_requirement(self):
        self.assertFalse(ProcessorConfig().improve_truck_parking)
        self.assertFalse(ProcessorConfig.from_preset('realistic').improve_truck_parking)
        self.assertFalse(ProcessorConfig.from_preset('broad').improve_truck_parking)
        for value in (1,0,None,'true',[],{}):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'boolean'):
                ProcessorConfig.from_names(['rest'],improve_truck_parking=value)
        for names in (['fuel'],['courier']):
            with self.subTest(names=names),self.assertRaisesRegex(ValueError,'rest processor'):
                ProcessorConfig.from_names(names,mode=ProcessorMode.ANALYZE,improve_truck_parking=True)

    def test_truck_only_none_and_car_policy_flags_remain_independent(self):
        config=ProcessorConfig.from_names(['rest'],parking_strategy='none',improve_truck_parking=True)
        self.assertEqual(config.parking_strategy,ParkingStrategy.NONE)
        self.assertTrue(config.improve_truck_parking)
        self.assertFalse(config.improve_existing_car_parking)
        for kwargs in ({'parking_strategy':'none'},{'parking_strategy':'none','improve_truck_parking':False},
                       {'parking_strategy':'none','improve_truck_parking':True,'improve_existing_car_parking':True}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                ProcessorConfig.from_names(['rest'],**kwargs)
        enhanced=ProcessorConfig.from_preset('realistic',improve_truck_parking=True)
        self.assertEqual(enhanced.parking_strategy,ParkingStrategy.STATION_BAYS)
        self.assertFalse(enhanced.improve_existing_car_parking)
        self.assertEqual(enhanced.fuel_selection,ProcessorConfig.from_preset('realistic').fuel_selection)
        broad=ProcessorConfig.from_preset('broad',improve_truck_parking=True)
        self.assertEqual(broad.parking_strategy,ParkingStrategy.TRUCK_AREAS)

    def test_pipeline_runs_truck_after_fuel_and_car_and_preserves_authoritative_overlay(self):
        stack=original_stack();calls=[]
        def fuel(*args,**kwargs):
            calls.append('fuel');return complete(),{SECTOR:b'fuel-sector'}
        def car(staged,**kwargs):
            calls.append('car');self.assertEqual(staged.read(SECTOR),b'fuel-sector')
            self.assertFalse(kwargs['improve_existing_car_parking'])
            return complete(composed_resource_paths=[SECTOR]),{SECTOR:b'fuel-and-car-sector'}
        def truck(staged,**kwargs):
            calls.append('truck');self.assertEqual(staged.read(SECTOR),b'fuel-and-car-sector')
            self.assertIs(kwargs['ownership_stack'],stack)
            self.assertEqual(kwargs['map_packages'],{'source.scs'})
            self.assertNotIn('radius',kwargs)
            return complete(composed_resource_paths=[SECTOR]),{SECTOR:b'fuel-car-and-truck-sector'}
        with patch('ats_road_trip.processors._fuel_plan',side_effect=fuel), \
             patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',side_effect=car), \
             patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',side_effect=truck), \
             patch('ats_road_trip.prefab_contexts.plan_prefab_contexts',return_value=(complete(),{})) as context:
            result=run_processors(stack,stack,source='source.scs',map_name='Fixture',
                config=ProcessorConfig.from_preset('realistic',enabled=('rest','fuel'),improve_truck_parking=True))
        self.assertEqual(calls,['fuel','car','truck'])
        self.assertTrue(result.coverage['complete'],result.blockers)
        self.assertEqual(result.resources[SECTOR],b'fuel-car-and-truck-sector')
        transitions=context.call_args.args[2]
        self.assertEqual(transitions,[('fuel',SECTOR,b'original-sector',b'fuel-sector'),
            ('rest',SECTOR,b'fuel-sector',b'fuel-and-car-sector'),
            ('truck_parking',SECTOR,b'fuel-and-car-sector',b'fuel-car-and-truck-sector')])
        self.assertIn('truck_parking',result.reports)

    def test_truck_only_pipeline_skips_fuel_car_strategies_and_car_native_gate(self):
        stack=original_stack()
        with patch('ats_road_trip.processors._fuel_plan',side_effect=AssertionError('fuel ran')), \
             patch('ats_road_trip.rest_stops.plan_rest_stops',side_effect=AssertionError('legacy car strategy ran')), \
             patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',side_effect=AssertionError('car strategy ran')), \
             patch('ats_road_trip.station_parking.native_support.classify_native_car_parking',side_effect=AssertionError('car gate ran')), \
             patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',return_value=(complete(),{SECTOR:b'truck'})) as truck, \
             patch('ats_road_trip.prefab_contexts.plan_prefab_contexts',return_value=(complete(),{})):
            result=run_processors(stack,stack,source='source.scs',map_name='Fixture',
                config=ProcessorConfig.from_names(['rest'],parking_strategy='none',improve_truck_parking=True,rest_radius=100000))
        truck.assert_called_once()
        self.assertTrue(result.reports['rest']['disabled'])
        self.assertTrue(result.coverage['complete'],result.blockers)
        self.assertEqual(result.resources,{SECTOR:b'truck'})
        self.assertNotIn('radius',truck.call_args.kwargs)

    def test_existing_or_unknown_car_support_does_not_suppress_truck(self):
        stack=original_stack()
        for state in ('present','unknown'):
            car_report=complete(native_car_parking={'state':state},skip_reasons={'original_native_car_parking_'+state:1})
            with self.subTest(state=state), \
                 patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',return_value=(car_report,{})), \
                 patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',return_value=(complete(),{SECTOR:b'truck'})) as truck, \
                 patch('ats_road_trip.prefab_contexts.plan_prefab_contexts',return_value=(complete(),{})):
                result=run_processors(stack,stack,source='source.scs',map_name='Fixture',
                    config=ProcessorConfig.from_preset('realistic',enabled=('rest',),improve_truck_parking=True))
            truck.assert_called_once()
            self.assertTrue(result.coverage['complete'],result.blockers)
            self.assertEqual(result.resources[SECTOR],b'truck')

    def test_off_keeps_legacy_behavior_and_never_calls_truck_planner(self):
        stack=original_stack()
        with patch('ats_road_trip.rest_stops.plan_rest_stops',return_value=(complete(),{SECTOR:b'car-legacy'})), \
             patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',side_effect=AssertionError('truck option off')), \
             patch('ats_road_trip.prefab_contexts.plan_prefab_contexts',return_value=(complete(),{})):
            result=run_processors(stack,stack,source='source.scs',map_name='Fixture',config=ProcessorConfig.from_names(['rest']))
        self.assertTrue(result.coverage['complete'])
        self.assertEqual(result.resources,{SECTOR:b'car-legacy'})
        self.assertNotIn('truck_parking',result.reports)

    def test_unacknowledged_truck_overlap_or_incomplete_coverage_blocks_completion(self):
        stack=original_stack()
        cases=[(complete(),True),({'coverage':{'complete':False,'blockers':[]}},False),
               ({'coverage':{'complete':False,'blockers':[{'reason':'native geometry unknown'}]}},False)]
        for report,overlap in cases:
            car_changes={SECTOR:b'car'} if overlap else {}
            with self.subTest(report=report,overlap=overlap), \
                 patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',return_value=(complete(),car_changes)), \
                 patch('ats_road_trip.truck_parking.mapwide.plan_map_truck_parking',return_value=(report,{SECTOR:b'truck'})), \
                 patch('ats_road_trip.prefab_contexts.plan_prefab_contexts',return_value=(complete(),{})):
                result=run_processors(stack,stack,source='source.scs',map_name='Fixture',
                    config=ProcessorConfig.from_preset('realistic',enabled=('rest',),improve_truck_parking=True))
            self.assertFalse(result.coverage['complete'])
            self.assertTrue(any(b['processor']=='truck_parking' for b in result.blockers))
            if overlap:
                self.assertTrue(any('collision' in b['reason'].lower() for b in result.blockers))


class TruckCliTests(unittest.TestCase):
    def test_parser_defaults_off_and_supports_single_map_and_complete_stack_options(self):
        for args in (['analyze-map','source.scs','--processor','rest'],
                     ['generate-map-fix','source.scs','--processor','rest'],
                     ['analyze-map-stack','--package','source.scs'],
                     ['generate-map-stack','--package','source.scs']):
            with self.subTest(args=args):
                self.assertFalse(parser().parse_args(args).improve_truck_parking)
                self.assertTrue(parser().parse_args(args+['--improve-truck-parking']).improve_truck_parking)
        with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            parser().parse_args(['generate-map-fuel','source.scs','--improve-truck-parking'])

    def test_cli_flag_reaches_actual_selected_workflow_for_analyze_and_generate(self):
        response={'status':'analyzed','report_path':'audit.json','workflow':{'work_dir':'work'},'planner':{'coverage':{'complete':True}},'outputs':[]}
        cases=[('analyze-map',['source.scs','--processor','rest','--parking-strategy','none'],'ats_road_trip.bulk_run.analyze_map'),
               ('generate-map-fix',['source.scs','--processor','rest','--parking-strategy','none','--experimental'],'ats_road_trip.bulk_run.generate_map_fix'),
               ('analyze-map-stack',['--package','source.scs'],'ats_road_trip.map_stack.run_map_stack'),
               ('generate-map-stack',['--package','source.scs','--experimental'],'ats_road_trip.map_stack.run_map_stack')]
        for command,args,target in cases:
            with self.subTest(command=command),patch(target,return_value=response) as workflow,redirect_stdout(io.StringIO()):
                self.assertEqual(main([command,*args,'--improve-truck-parking']),0)
                self.assertTrue(workflow.call_args.kwargs['improve_truck_parking'])
                self.assertFalse(workflow.call_args.kwargs.get('improve_existing_car_parking',False))
                if 'map-stack' not in command:
                    self.assertEqual(workflow.call_args.kwargs['parking_strategy'],'none')


if __name__=='__main__':
    unittest.main()
