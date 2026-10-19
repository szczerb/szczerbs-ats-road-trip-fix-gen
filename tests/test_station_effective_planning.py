"""Effective station planning uses authored source/model fixtures only."""
from copy import deepcopy
import hashlib
import math
import unittest
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
        self.assertIn('Engine pose envelope UNKNOWN',render_station_plan(report))
        self.assertTrue(resources)
        self.assertEqual(self.plan(),(report,resources))

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
        self.assertEqual(propose_unmarked_parking(station_descriptor()),propose_unmarked_parking(station_descriptor(),layouts=('perpendicular',)))

if __name__=='__main__':unittest.main()
