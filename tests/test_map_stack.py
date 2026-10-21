"""Original-owner partition and full-stack composition regression fixtures."""
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ats_road_trip.map_stack import plan_stack, _owner_index, run_map_stack, _package_description
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.processors import ProcessorConfig
from tests.test_bulk_fuel import resources, SECTOR, PPD, DEF
from tests.test_map_sector import sector
from tests.test_prefab_contexts import context, alias, model_change


class MapStackTests(unittest.TestCase):
    def fixture(self, directory, manager):
        original=resources();parsed=parse_sector(original[SECTOR])
        # Root and controls in A; its fuel service and node live in adjacent B.
        a={PPD:original[PPD],DEF:original[DEF],
           SECTOR:sector([original[SECTOR][p.offset:p.end] for p in parsed.prefabs],
                         [n.raw for n in parsed.nodes if n.uid<400]),
           'def/data_context.sii':('SiiNunit\n{'+context(target='prefab.02003')+'}').encode()}
        neighbor='map/usa/sec+0001+0000.base'
        b={neighbor:sector([original[SECTOR][s.offset:s.end] for s in parsed.services],
                           [n.raw for n in parsed.nodes if n.uid>=400])}
        stock={'def/country/washington.sui':b'SiiNunit { country_data : country.data.washington { fuel_price: 1.92132 petrol_price: 1.47197 } }'}
        mounted=[]
        for i,contents in enumerate([stock,a,b,{}, {}, {}, {}, {}]):
            root=Path(directory)/str(i);root.mkdir()
            for path,data in contents.items():
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            mounted.append(manager.enter_context(Package(root)))
        parts=[{'map_name':f'Source{i}','source_packages':[str(p.path)],'rank':i} for i,p in enumerate(mounted)]
        return original,neighbor,mounted,parts

    def test_cross_sector_fuel_then_bays_partition_by_original_owner(self):
        with TemporaryDirectory() as directory, ExitStack() as manager:
            original,neighbor,packages,parts=self.fixture(directory,manager)
            raw=ResourceStack(packages);calls=[]
            def parking(stack, **kwargs):
                self.assertIs(kwargs['ownership_stack'],raw)
                calls.append(kwargs['map_name'])
                if kwargs['map_name']!='Source1':return {'coverage':{'complete':True,'blockers':[]}},{}
                fuel=stack.read(SECTOR)
                self.assertNotEqual(parse_sector(fuel).prefabs[0].details['model'],parse_sector(original[SECTOR]).prefabs[0].details['model'])
                output={SECTOR:model_change(fuel,'rts12345678'),
                        'def/world/prefab.rts12345678.sii':alias('rts12345678'),
                        'prefab/rtfix/rts12345678.ppd':b'fixture parking PPD',
                        'def/data_context.permap.sii':b'preview must not ship'}
                return {'coverage':{'complete':True,'blockers':[]},'composed_resource_paths':[SECTOR]},output
            with patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',side_effect=parking), \
                 patch('ats_road_trip.rest_stops.plan_rest_stops',side_effect=AssertionError('truck fallback')):
                report,values=plan_stack(raw,ResourceStack(packages[:1]),parts=parts,
                    config=ProcessorConfig.from_preset('realistic'),game_version='1.61.3.18')
            self.assertEqual(len(calls),8)
            self.assertIn(SECTOR,values[1]);self.assertNotIn(SECTOR,values[2])
            self.assertIn(neighbor,values[2]);self.assertNotIn(neighbor,values[1])
            after=parse_sector(values[2][neighbor]);self.assertEqual(len(after.services),2)
            source=parse_sector(raw.read(neighbor))
            self.assertIn(source.services[0].uid,{s.uid for s in after.services})
            before=source.services[0];retained=next(s for s in after.services if s.uid==before.uid)
            self.assertEqual(raw.read(neighbor)[before.offset:before.end],values[2][neighbor][retained.offset:retained.end])
            merged={k:v for group in values for k,v in group.items()}
            self.assertNotIn('def/data_context.permap.sii',merged)
            contexts=[p for p in merged if p.startswith('def/data_context.')]
            self.assertEqual(len(contexts),1)
            self.assertEqual(report['contexts']['coverage']['aliases_seen'],2)
            self.assertEqual({r['original'] for r in report['contexts']['aliases']},{'prefab.02003'})
            self.assertEqual(raw.read(SECTOR),packages[1].read(SECTOR))
            self.assertEqual(report['parking_strategy'],'station_bays')

    def test_rest_only_does_not_run_fuel_or_prices(self):
        with TemporaryDirectory() as directory, ExitStack() as manager:
            _,_,packages,parts=self.fixture(directory,manager)
            with patch('ats_road_trip.map_stack.plan_map_fuel',side_effect=AssertionError('fuel ran')), \
                 patch('ats_road_trip.map_stack.build_policy',side_effect=AssertionError('prices ran')), \
                 patch('ats_road_trip.station_parking.mapwide.plan_map_station_parking',return_value=({'coverage':{'blockers':[]}},{})):
                report,values=plan_stack(ResourceStack(packages),ResourceStack(packages[:1]),parts=parts,
                    config=ProcessorConfig.from_preset('realistic',enabled=['rest']),game_version='1.61.3.18')
            self.assertTrue(report['prices']['disabled'])
            self.assertEqual(values,[{} for _ in parts])

    def test_resource_provider_repair_is_placed_above_resource_provider(self):
        from types import SimpleNamespace
        provider=SimpleNamespace(path=Path('/resource-defs'))
        raw=SimpleNamespace(resources={'def/country/example.sui':(provider,None)})
        parts=[{'source_packages':['/base'],'rank':0},{'source_packages':['/map'],'rank':2},
               {'source_packages':['/connector'],'rank':5}]
        self.assertEqual(_owner_index(raw,'def/country/example.sui',parts,{'/resource-defs':3},{}),2)
        self.assertEqual(_owner_index(raw,'private/new.ppd',parts,{}, {'private/new.ppd':1}),1)

    def test_repair_cannot_ship_below_a_winning_resource_only_package(self):
        from types import SimpleNamespace
        provider=SimpleNamespace(path=Path('/high-resource'))
        raw=SimpleNamespace(resources={'def/country/example.sui':(provider,None)})
        with self.assertRaisesRegex(ValueError,'loads above'):
            _owner_index(raw,'def/country/example.sui',[{'source_packages':['/map'],'rank':1}],{'/high-resource':2},{})

    def test_global_corruption_is_not_a_safe_facility_omission(self):
        with TemporaryDirectory() as directory, ExitStack() as manager:
            _,_,packages,parts=self.fixture(directory,manager)
            raw=ResourceStack(packages)
            with patch('ats_road_trip.map_stack.plan_map_fuel',return_value=({'coverage':{'blockers':[{'reason':'Conflicting UID ownership'}]}},{})):
                with self.assertRaisesRegex(ValueError,'global fuel structure'):
                    plan_stack(raw,ResourceStack(packages[:1]),parts=parts,config=ProcessorConfig.from_preset('realistic'),game_version='1.61.3.18')

    def test_descriptions_identify_each_source_and_one_current_mod(self):
        parts=[{'map_name':'Base Game and DLC','source_packages':['/game'],'base_companion':True},
               {'map_name':'Reforma OtherMaps Patch','source_packages':['/Reforma_OtherMaps_Patch_40_161.scs'],'base_companion':False}]
        workflow={'game_version':'1.61.3.18','packages_low_to_high':['/game','/Reforma_OtherMaps_Patch_40_161.scs']}
        for part in parts:
            text=_package_description(part,parts,workflow,'realistic',10)
            self.assertEqual(text.count('(THIS MOD)'),1)
            self.assertTrue(text.startswith('REALISTIC r10 | '+part['map_name']))
            self.assertIn('LOWEST to HIGHEST',text)
            self.assertIn('Reforma_OtherMaps_Patch_40_161.scs',text)
            self.assertIn('N2',text)
            self.assertGreater(text.rindex('N2 NAV PARKING FUEL'),text.index('Reforma_OtherMaps_Patch_40_161.scs'))
            self.assertTrue(text.rstrip().endswith('above every listed source/fix)'))
        self.assertIn('country petrol prices only',_package_description(parts[1],parts,workflow,'realistic',10))

    def test_generation_requires_explicit_acknowledgment_before_any_work(self):
        with patch('ats_road_trip.map_stack._game_directory',side_effect=AssertionError('work began')):
            with self.assertRaisesRegex(ValueError,'experimental'):
                run_map_stack(packages=[],generate=True)
            with self.assertRaisesRegex(ValueError,'revision'):
                run_map_stack(packages=[],revision=True)
