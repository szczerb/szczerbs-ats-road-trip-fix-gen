"""Effective station planning uses authored source/model fixtures only."""
from copy import deepcopy
import hashlib
import math
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from tests import test_station_parking as fixtures
from ats_road_trip.package import ResourceStack
from ats_road_trip.station_parking import plan_station_parking, render_station_plan
from ats_road_trip.station_parking.methods.unmarked import propose_unmarked_parking
from tests.test_station_geometry import station_descriptor


def pit_text():
    materials=''.join('Material {\n Alias: "'+name+'"\n Effect: "eut2.dif.spec"\n Flags: 0\n AttributeCount: 0\n TextureCount: 0\n}\n' for name in ['asphalt','paint'])
    return 'Header {\n FormatVersion: 1\n Source: "authored"\n Type: "Trait"\n Name: "station"\n}\nGlobal {\n LookCount: 1\n VariantCount: 1\n PartCount: 1\n MaterialCount: 2\n}\nLook {\n Name: "default"\n'+materials+'}\nVariant {\n Name: "default"\n Part {\n Name: "part1"\n AttributeCount: 1\n Attribute {\n Format: "INT"\n Tag: "visible"\n Value: ( 1 )\n}\n}\n}\n'


class EffectivePlanningTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.StationPlannerTests();self.helper.setUp();self.addCleanup(self.helper.doCleanups)
        contents=dict(self.helper.original)
        contents['prefab/test/station.pmd']=b'Authored model material identity'
        contents['material/paint.tobj']=b'Authored texture identity'
        self.package,self.stack,self.config=self.helper.make_stack(contents)
        self.config['schema_version']=2
        self.pit=pit_text()
        self.config['fingerprints'].update(model_definition=hashlib.sha256(contents['prefab/test/station.pmd']).hexdigest(),mesh_state=hashlib.sha256(self.pit.encode()).hexdigest())
        self.config['material_resources']={'material/paint.tobj':hashlib.sha256(contents['material/paint.tobj']).hexdigest()}

    def plan(self, config=None, stack=None, pit=None):
        return plan_station_parking(stack or self.stack,config or self.config,self.helper.mesh,
            map_package=str(self.package.path),game_version='1.61.3.18',mesh_state_text=self.pit if pit is None else pit)

    def test_effective_selection_explains_access_heading_materials_and_native_flags(self):
        report,resources=self.plan()
        self.assertTrue(report['coverage']['complete'],report['coverage'])
        selected=report['selected']
        self.assertTrue(selected['approach_xz'])
        self.assertTrue(selected['ranking_components']['passes_checks'])
        self.assertEqual(len(selected['approach_alternatives']),2)
        self.assertEqual(report['effective_model_state']['variant'],'default')
        self.assertEqual(report['writer']['parameters']['flags'],0)
        self.assertEqual(report['activation']['vehicle_test_geometry'],'Unknown')
        svg=render_station_plan(report)
        self.assertIn('Engine pose envelope UNKNOWN',svg)
        self.assertEqual(ET.fromstring(svg).tag,'{http://www.w3.org/2000/svg}svg')
        self.assertTrue(resources)
        self.assertEqual(self.plan(),(report,resources))

    def test_fully_covering_native_car_bank_is_an_explicit_no_output_control(self):
        from ats_road_trip.station_parking.trigger import append_car_parking_polygon
        from tests.test_bulk_fuel import PPD
        contents={n:self.package.read(n) for n in self.package.files}
        contents[PPD],_=append_car_parking_polygon(contents[PPD],[(-20.,0.,-20.),(20.,0.,-20.),(20.,0.,20.),(-20.,0.,20.)])
        package,stack,legacy=self.helper.make_stack(contents)
        self.package=package
        config=deepcopy(self.config)
        for key in ['source_archive','descriptor']:config['fingerprints'][key]=legacy['fingerprints'][key]
        report,resources=self.plan(config=config,stack=stack)
        self.assertEqual(report['state'],'already_covered')
        self.assertTrue(report['coverage']['complete'])
        self.assertFalse(report['in_game_verified'])
        self.assertTrue(report['candidates'][0]['fully_covering_native_car_groups'])
        self.assertEqual(resources,{})
        self.assertNotIn('writer',report)

    def test_external_world_obstacle_blocks_an_otherwise_valid_station_without_mutating_context(self):
        report,resources=self.plan()
        self.assertTrue(resources)
        # Cover the complete evidenced bank, including every new single-bay
        # alternative; blocking only the selected bay may leave a valid neighbor.
        from tests.test_bulk_fuel import PPD, SECTOR
        from ats_road_trip.map_sector import parse_sector
        from ats_road_trip.rest_stops import _placed_vertices
        sector=parse_sector(self.package.read(SECTOR))
        parent=next(c for c in report['candidates'] if not c.get('parent_bank_id'))
        polygon=_placed_vertices(self.package.read(PPD),sector.prefabs[0],
            {n.uid:n for n in sector.nodes},[(x,0.,z) for x,z in parent['polygon_xz']])
        context={'objects':[{'id':'authored-external-building','classification':'obstacle_proxy',
            'extent_status':'declared_conservative_proxy','geometry_xz':polygon}],
            'unassessed_objects':[], 'limits':['Bounded authored external proxy']}
        before=deepcopy(context)
        checked,output=plan_station_parking(self.stack,self.config,self.helper.mesh,
            map_package=str(self.package.path),game_version='1.61.3.18',mesh_state_text=self.pit,
            local_context=context)
        self.assertEqual(context,before)
        self.assertFalse(output)
        self.assertTrue(any('intersects_external_map_object_proxy' in c['rejection_reasons']
                            for c in checked['candidates']))
        self.assertIn('external_context_geometry',checked)
        self.assertIn('external prefab UI obstacle proxies',render_station_plan(checked))

    def test_occupied_painted_bay_keeps_a_clear_source_derived_neighbor(self):
        # The model locator blocks one end of an otherwise evidenced bank.
        # Keep its radius, both approach checks and original bank diagnosis.
        mesh=self.helper.mesh.replace('LocatorCount: 0','LocatorCount: 1').replace('Locators:\n','Locators: 0\n')
        mesh+='Locator {\n Name: "parked"\n Hookup: "car.parked.physics"\n Index: 0\n Position: ( 15 0 -6 )\n Rotation: ( 1 0 0 0 )\n Scale: ( 1 1 1 )\n}\n'
        self.helper.mesh=mesh
        self.config['fingerprints']['mesh']=hashlib.sha256(mesh.encode()).hexdigest()
        report,resources=self.plan()
        self.assertTrue(resources,report['coverage'])
        selected=report['selected']
        self.assertEqual(selected['bay_count'],1)
        self.assertEqual(selected['geometry_scope'],'single_bay_from_accepted_separator_bank')
        self.assertGreaterEqual(selected['parent_bank_separator_count'],3)
        self.assertEqual(selected['source_boundary_separator_count'],2)
        self.assertGreaterEqual(selected['clearance_margins_m']['parked_locator'],0.)
        parent=next(c for c in report['candidates'] if c['id']==selected['parent_bank_id'])
        self.assertIn('parked_vehicle_locator_exclusion',parent['rejection_reasons'])
        self.assertEqual(selected['polygon_xz'],parent['bay_polygons_xz'][selected['source_bay_index']]['polygon_xz'])
        self.assertFalse(selected['rejection_reasons'])

    def test_named_role_texture_present_in_stack_must_be_pinned(self):
        self.pit=self.pit.replace(' TextureCount: 0\n}', ' TextureCount: 1\n Texture {\n Tag: "texture[0]:texture_base"\n Value: "/material/paint"\n }\n}')
        config=deepcopy(self.config);config['fingerprints']['mesh_state']=hashlib.sha256(self.pit.encode()).hexdigest()
        contents={n:self.package.read(n) for n in self.package.files};contents['material/paint.dds']=b'authored diffuse texture'
        package,stack,legacy=self.helper.make_stack(contents);self.package=package
        config['fingerprints']['source_archive']=legacy['fingerprints']['source_archive']
        with self.assertRaisesRegex(ValueError,'dependency is not pinned'):
            self.plan(config=config,stack=stack)

    def test_failed_fuel_graph_retains_local_diagnostics_but_never_resources(self):
        with patch('ats_road_trip.station_parking.planner.match_gas_services',side_effect=ValueError('missing placed services')):
            report,resources=self.plan()
        self.assertFalse(report['coverage']['complete'])
        self.assertFalse(report['fuel_graph_validation']['complete'])
        self.assertTrue(report['candidates'])
        self.assertIn('GAS/service graph',report['coverage']['blockers'][0]['reason'])
        self.assertEqual(resources,{})
        self.assertNotIn('writer',report)

    def test_paired_pit_and_effective_material_and_pmd_drift_block(self):
        for key in ['mesh_state','model_definition']:
            config=deepcopy(self.config);config['fingerprints'][key]='0'*64
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'SHA-256'):
                self.plan(config=config)
        config=deepcopy(self.config);config['material_resources']['material/paint.tobj']='0'*64
        with self.assertRaisesRegex(ValueError,'material resource SHA-256'):
            self.plan(config=config)
        with self.assertRaisesRegex(ValueError,'mesh_state SHA-256'):
            self.plan(pit='different converted state')

    def test_effective_model_override_is_read_before_selection(self):
        content=dict(self.helper.original);content['prefab/test/station.pmd']=b'High priority replacement changes materials'
        override,_,_=self.helper.make_stack(content)
        with self.assertRaisesRegex(ValueError,'model_definition SHA-256'):
            self.plan(stack=ResourceStack([self.package,override]))

    def test_schema_two_unmarked_proposes_both_physical_orientations_without_padding(self):
        config=deepcopy(self.config);config['method']='unmarked_geometry'
        report,resources=self.plan(config=config)
        layouts={c['layout'] for c in report['candidates']}
        self.assertEqual(layouts,{'perpendicular','parallel'})
        for candidate in report['candidates']:
            p=candidate['polygon_xz'];edges=sorted([math.dist(p[0],p[1]),math.dist(p[1],p[2])])
            self.assertAlmostEqual(edges[0],3.);self.assertAlmostEqual(edges[1],6.)
            self.assertEqual(candidate['physical_parking_polygon_xz'],candidate['activation_polygon_xz'])
            if candidate['layout']=='parallel':
                self.assertEqual(len(candidate['approach_alternatives']),2)
                h=candidate['heading_xz'];a=candidate['approach_direction_xz']
                self.assertAlmostEqual(sum(h[i]*a[i] for i in (0,1)),1.)
        self.assertEqual(propose_unmarked_parking(station_descriptor()),propose_unmarked_parking(station_descriptor(),layouts=('perpendicular',)))

if __name__=='__main__':unittest.main()
