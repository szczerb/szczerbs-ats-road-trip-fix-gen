"""Reviewed catalog guard pins are independent of historical effective overlays."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ats_road_trip.station_parking.catalog import load_reviewed_catalog


class ReviewedCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.reviewed=json.loads((Path(__file__).parents[1]/
            'docs/examples/station-parking-dawson-two-reviewed-areas.json').read_text())
        self.metadata=json.loads((Path(__file__).parents[1]/
            'src/ats_road_trip/station_parking/reviewed_catalog.json').read_text())
        self.evidence=self.root/'portable-evidence';self.evidence.mkdir()
        for config in self.metadata['families']:
            family=config['family']
            mesh='Authored mesh evidence '+family;pit='Authored paired state '+family
            (self.evidence/(family+'.pim')).write_text(mesh)
            (self.evidence/(family+'.pit')).write_text(pit)
            config['fingerprints'].update(mesh=hashlib.sha256(mesh.encode()).hexdigest(),
                                         mesh_state=hashlib.sha256(pit.encode()).hexdigest())
        self.metadata_path=self.root/'authored-metadata.json'
        self.metadata_path.write_text(json.dumps(self.metadata))

    def override(self):
        entry=load_reviewed_catalog(self.evidence,metadata_path=self.metadata_path)['prefab/gas/nm_truckstop1_chemron.pmd']
        return entry['policy']['reviewed_areas'][0]

    def test_dawson_guards_pin_original_alaska_sector_and_effective_base_descriptor(self):
        override=self.override()
        self.assertEqual(override['source_archive'],'d879c245c1bc8b88c9a884d88952ccaad88b58ce759f665832fd0b664a6200fb')
        self.assertEqual(override['source_sector'],'ddc5fcee53d1ac3e0b15ba48bb4c47da0492f6abefaea47c4209fa3fa019e532')
        self.assertEqual(override['original_descriptor'],'92be3a4ee1a2788d32ca80bde50256c0e73032ee3caad2739df3d001b3715f91')
        self.assertEqual(override['original_descriptor_provider'],'base.scs')
        self.assertIn('historical effective sector/descriptor overlay hashes',override['provenance'])

    def test_accepted_override_preserves_both_exact_areas_and_never_the_old_tiny_bay(self):
        override=self.override()
        self.assertEqual(override['prefab_uid'],'0x5ca1fea582800001')
        self.assertEqual(override['sector'],'map/usa/sec-0029-0045.base')
        self.assertEqual(override['areas'],self.reviewed['areas'])
        self.assertEqual(len(override['areas']),2)
        self.assertTrue(all(a['partial_activation'] for a in override['areas']))
        self.assertFalse(any(a['vertices']==self.reviewed['previous_vertices'] for a in override['areas']))
        override['areas'][0]['vertices'][0][0]=999
        self.assertEqual(self.override()['areas'],self.reviewed['areas'])

    def test_catalog_needs_no_checkout_or_historical_output_directory(self):
        before=deepcopy(self.override())
        # Only authored metadata and eight explicit files exist in this fixture.
        self.assertFalse((self.root/'local_outputs').exists())
        self.assertFalse((self.root/'docs').exists())
        self.assertEqual(self.override(),before)

    def test_missing_directory_and_missing_state_fail_clearly(self):
        with self.assertRaisesRegex(ValueError,'requires --station-evidence-dir'):
            load_reviewed_catalog()
        with self.assertRaisesRegex(ValueError,'directory does not exist'):
            load_reviewed_catalog(self.root/'missing')
        state=self.evidence/'nm_gas_station2-corner_gp.pit'
        state.unlink()
        with self.assertRaisesRegex(ValueError,'missing or unreadable'):
            load_reviewed_catalog(self.evidence,metadata_path=self.metadata_path)

    def test_mesh_and_paired_state_drift_remain_fatal(self):
        for suffix,label in (('.pim','mesh'),('.pit','mesh_state')):
            path=self.evidence/('nm_gas_station2-corner_gp'+suffix)
            before=path.read_bytes();path.write_text('drift')
            with self.subTest(suffix=suffix),self.assertRaisesRegex(ValueError,label+' SHA-256 drift'):
                load_reviewed_catalog(self.evidence,metadata_path=self.metadata_path)
            path.write_bytes(before)

    def test_tracked_gp_metadata_retains_reviewed_source_and_material_pins(self):
        from ats_road_trip.station_parking.catalog import reviewed_metadata
        rows=reviewed_metadata()['families']
        self.assertEqual(len(rows),4)
        gp=next(row for row in rows if row['family']=='nm_gas_station2-corner_gp')
        self.assertEqual(gp['fingerprints'],{
            'model_definition':'2a8d37fa45d33a87284ec29b36c7303ad0b55c1c5c4b9f9515bf739b6eaff294',
            'model_geometry':'39d1d65208af5d676887a4ae7f06ec8eb35bb74d47793190a8630aa4a266a648',
            'mesh':'3088fd090938ad4971540da99d7636de46aca64fe36dcc7779ab0e3e5a0abc02',
            'mesh_state':'4db3aaee046f13b908649362171849ec0cce54da541b145a60e5c36a8e4e8ff8'})
        self.assertEqual(len(gp['mesh_materials']['ground']),4)
        self.assertEqual(gp['mesh_materials']['paint'],[])
        self.assertEqual(len(gp['material_resources']),12)


if __name__=='__main__':unittest.main()
