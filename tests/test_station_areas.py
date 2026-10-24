"""Broad logical regions use authored source fixtures and real writer output."""
from copy import deepcopy
import hashlib
import math
import json
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

from ats_road_trip.local_fuel import token
from ats_road_trip.rest_stops import inspect_rest_triggers
from ats_road_trip.station_parking import plan_station_parking
from ats_road_trip.station_parking.methods.areas import (evaluate_area,propose_broad_unmarked,
                                                       select_logical_areas)
from ats_road_trip.station_parking.trigger import append_car_parking_polygon
from tests.test_station_curbside import fixture
from tests import test_station_effective_planning as effective_fixtures
from tests.test_bulk_fuel import PPD


def area_fixture():
    mesh,geometry=fixture()
    geometry['polygons'].append({'id':2,'color':1,'vertices':
        [[-30.,0.,-30.],[30.,0.,-30.],[30.,0.,30.],[-30.,0.,30.]]})
    mesh['locators']=[{'index':0,'hookup':'car.parked.physics','position':[0.,0.,3.]}]
    return mesh,geometry


class BroadAreaGeometryTests(unittest.TestCase):
    def propose(self,mesh,geometry):
        return propose_broad_unmarked(mesh,geometry,ground={'ground'},paint={'paint'})

    def test_curb_emits_one_broad_bank_with_variable_npc_evidence(self):
        mesh,geometry=area_fixture();before=deepcopy((mesh,geometry))
        first=self.propose(mesh,geometry)
        selected=select_logical_areas(first['candidates'])
        self.assertEqual(len(selected),1)
        self.assertEqual(selected[0]['area_length_m'],12.)
        self.assertEqual(selected[0]['area_depth_m'],6.)
        checked=evaluate_area(selected[0],geometry,mesh,ground={'ground'},paint={'paint'})
        self.assertFalse(checked['rejection_reasons'])
        self.assertEqual(len(checked['parked_npc_evidence']),1)
        self.assertEqual((mesh,geometry),before)
        self.assertEqual(self.propose(mesh,geometry),first)

    def test_permanent_obstruction_shortens_or_rejects_instead_of_tiny_fallback(self):
        mesh,geometry=area_fixture()
        mesh['pieces'].append({'index':2,'material':'permanent_wall',
            'positions':[[0.,0.,.5],[0.,2.,.5],[0.,2.,11.],[0.,0.,11.]],
            'triangles':[(0,1,2),(0,2,3)]})
        result=self.propose(mesh,geometry)
        self.assertFalse(result['candidates'])
        self.assertTrue(any('model_geometry_intersects_car_clearance_volume' in r['reasons']
                            for r in result['rejections']))

    def test_pump_and_circulation_clearances_remain_mandatory(self):
        for kind in ('pump','road'):
            mesh,geometry=area_fixture()
            if kind=='pump':geometry['gas_spawns'][0]['position']=[0.,0.,5.]
            else:geometry['roads']=[{'indices':[0,1],'vertices':[[-20.,0.,6.],[20.,0.,6.]]}]
            result=self.propose(mesh,geometry)
            self.assertFalse(result['candidates'])
            self.assertTrue(result['rejections'])

    def test_unanchored_asphalt_cannot_fall_back_to_arbitrary_bay(self):
        mesh,geometry=area_fixture();mesh['pieces']=mesh['pieces'][:1]
        result=self.propose(mesh,geometry)
        self.assertEqual(result['candidates'],[])

    def test_separate_regions_are_retained_and_overlapping_alternatives_emit_once(self):
        def candidate(name,x):
            return {'id':name,'polygon_xz':[[x,0.],[x+12.,0.],[x+12.,6.],[x,6.]],'rejection_reasons':[]}
        result=select_logical_areas([candidate('a',0.),candidate('b',30.),candidate('c',1.)])
        self.assertEqual([c['id'] for c in result],['a','b'])


class BroadAreaWriterTests(unittest.TestCase):
    def setUp(self):
        self.helper=effective_fixtures.EffectivePlanningTests();self.helper.setUp();self.addCleanup(self.helper.doCleanups)

    def plan(self,**kwargs):
        h=self.helper
        return plan_station_parking(h.stack,h.config,h.helper.mesh,map_package=str(h.package.path),
            game_version='1.61.3.18',mesh_state_text=h.pit,candidate_policy={'broad_areas':True,**kwargs})

    def test_painted_parent_bank_and_partial_contact_flags_are_emitted(self):
        report,resources=self.plan()
        self.assertTrue(resources,report['coverage'])
        self.assertEqual(len(report['selected_areas']),1)
        self.assertEqual(report['selected']['bay_count'],3)
        self.assertNotIn('parent_bank_id',report['selected'])
        self.assertEqual(report['writer']['area_count'],1)
        self.assertEqual(report['writer']['parameters']['flags'],4)
        ppd=next(data for path,data in resources.items() if path.endswith('.ppd'))
        added=[g for g in inspect_rest_triggers(ppd) if g['action']==token('parking_car')]
        self.assertEqual(len(added),1)
        self.assertEqual(added[0]['flags'],4)
        before=self.helper.package.read(PPD);header=struct.unpack_from('<24I',before)
        self.assertEqual(ppd[96:header[22]],before[96:header[22]])

    def test_two_logical_regions_get_separate_groups_and_no_single_bay(self):
        from ats_road_trip.station_parking.methods.painted import propose_painted_parking
        from ats_road_trip.station_parking.mesh import read_station_mesh
        mesh=read_station_mesh(self.helper.helper.mesh)
        bank=propose_painted_parking(mesh,paint_materials=['paint'])['candidates'][0]
        second=deepcopy(bank);second['id']='second-bank'
        second['polygon_xz']=[[x,z+14.] for x,z in bank['polygon_xz']]
        proposal={'candidates':[bank,second]}
        with patch('ats_road_trip.station_parking.methods.painted.propose_painted_parking',return_value=proposal):
            report,resources=self.plan()
        self.assertTrue(resources,report['coverage'])
        self.assertEqual(report['writer']['area_count'],2)
        ppd=next(data for path,data in resources.items() if path.endswith('.ppd'))
        groups=[g for g in inspect_rest_triggers(ppd) if g['action']==token('parking_car')]
        self.assertEqual(len({g['id'] for g in groups}),2)
        self.assertEqual([g['flags'] for g in groups],[4,4])
        self.assertEqual(len(report['selected_areas']),2)

    def test_overlapping_native_area_is_preserved_without_duplicate_even_when_on(self):
        h=self.helper;contents={n:h.package.read(n) for n in h.package.files}
        contents[PPD],_=append_car_parking_polygon(contents[PPD],[[4.,0.,-10.],[15.,0.,-10.],[15.,0.,-2.],[4.,0.,-2.]])
        package,stack,legacy=h.helper.make_stack(contents);h.package=package;h.stack=stack
        for key in ('source_archive','descriptor'):h.config['fingerprints'][key]=legacy['fingerprints'][key]
        report,resources=self.plan(allow_native_improvement=True)
        self.assertFalse(resources)
        self.assertTrue(all('already_has_overlapping_native_car_rest' in c['rejection_reasons'] for c in report['candidates']))

    def test_native_improvement_on_reaches_generation_for_a_disjoint_bank(self):
        h=self.helper;contents={n:h.package.read(n) for n in h.package.files}
        contents[PPD],_=append_car_parking_polygon(contents[PPD],[[-18.,0.,10.],[-8.,0.,10.],[-8.,0.,15.],[-18.,0.,15.]])
        package,stack,legacy=h.helper.make_stack(contents);h.package=package;h.stack=stack
        for key in ('source_archive','descriptor'):h.config['fingerprints'][key]=legacy['fingerprints'][key]
        off,untouched=self.plan()
        self.assertEqual(off['state'],'already_covered');self.assertFalse(untouched)
        on,resources=self.plan(allow_native_improvement=True)
        self.assertTrue(resources,on['coverage'])
        before=contents[PPD];after=next(v for p,v in resources.items() if p.endswith('.ppd'))
        header=struct.unpack_from('<24I',before)
        self.assertEqual(after[96:header[22]],before[96:header[22]])
        self.assertEqual(len([g for g in inspect_rest_triggers(after) if g['action']==token('parking_car')]),2)

    def test_exact_accepted_dawson_rectangles_and_source_override_guards(self):
        h=self.helper
        reviewed=json.loads((Path(__file__).parents[1]/'docs/examples/station-parking-dawson-two-reviewed-areas.json').read_text())
        h.helper.mesh=h.helper.mesh.replace('0.0','0.13931791')
        h.config['fingerprints']['mesh']=hashlib.sha256(h.helper.mesh.encode()).hexdigest()
        config=h.config
        override={'prefab_uid':config['prefab_uid'],'sector':config['sector'],
            'source_archive':config['fingerprints']['source_archive'],
            'source_sector':config['fingerprints']['sector'],
            'original_descriptor':config['fingerprints']['descriptor'],'descriptor':PPD,
            'mesh':config['fingerprints']['mesh'],'areas':reviewed['areas'],'provenance':'Authored regression using exact accepted area coordinates'}
        report,resources=self.plan(reviewed_areas=[override])
        self.assertTrue(resources,report['coverage'])
        self.assertEqual(report['writer']['area_count'],2)
        expected={a['id']:a['vertices'] for a in reviewed['areas']}
        self.assertEqual({a['id']:a['vertices'] for a in report['writer']['areas']},expected)
        self.assertEqual([a['parameters']['flags'] for a in report['writer']['areas']],[4,4])
        self.assertFalse(any(a['vertices']==reviewed['previous_vertices'] for a in report['writer']['areas']))
        override['source_sector']='0'*64
        with self.assertRaisesRegex(ValueError,'override source drift'):self.plan(reviewed_areas=[override])

    def test_reviewed_override_reads_descriptor_from_its_effective_asset_provider(self):
        import zipfile
        from ats_road_trip.package import Package,ResourceStack
        h=self.helper
        reviewed=json.loads((Path(__file__).parents[1]/'docs/examples/station-parking-dawson-two-reviewed-areas.json').read_text())
        h.helper.mesh=h.helper.mesh.replace('0.0','0.13931791')
        h.config['fingerprints']['mesh']=hashlib.sha256(h.helper.mesh.encode()).hexdigest()
        assets=h.package
        path=h.helper.root/'placement-only.scs'
        with zipfile.ZipFile(path,'w') as z:
            for name in assets.files:
                if name!=PPD:z.writestr(name,assets.read(name))
        h.package=Package(path);self.addCleanup(h.package.close)
        h.stack=ResourceStack([assets,h.package])
        h.config['fingerprints']['source_archive']=hashlib.sha256(path.read_bytes()).hexdigest()
        override={'prefab_uid':h.config['prefab_uid'],'sector':h.config['sector'],
            'source_archive':h.config['fingerprints']['source_archive'],
            'source_sector':h.config['fingerprints']['sector'],
            'original_descriptor':h.config['fingerprints']['descriptor'],'descriptor':PPD,
            'mesh':h.config['fingerprints']['mesh'],'areas':reviewed['areas'],
            'provenance':'Authored source placement with shared lower asset descriptor'}
        report,resources=self.plan(reviewed_areas=[override])
        self.assertNotIn(PPD,h.package.files)
        self.assertTrue(resources,report['coverage'])
        self.assertEqual(report['writer']['area_count'],2)

    def test_unknown_or_non_operational_gas_graph_never_generates(self):
        with patch('ats_road_trip.station_parking.planner.match_gas_services',side_effect=ValueError('unresolved')):
            report,resources=self.plan()
        self.assertFalse(resources);self.assertFalse(report['coverage']['complete'])


if __name__=='__main__':unittest.main()
