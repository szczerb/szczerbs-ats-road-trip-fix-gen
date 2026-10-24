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
        bundle=self.root/'local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/inputs/models'
        rows=[('nm_gas_station1_chemron','P01',bundle),
              ('nm_truckstop1_chemron','P05',bundle),
              ('nm_gas_station2-corner_chemron','P09',bundle),
              ('nm_gas_station2-corner_gp',None,self.root/'local_outputs/work/2026-10-19_21-19-20/marked-station-inventory/converted-effective-gp/prefab/gas')]
        for family,site,mesh_root in rows:
            mesh='Authored mesh evidence '+family;pit='Authored paired state '+family
            mesh_root.mkdir(parents=True,exist_ok=True)
            (mesh_root/(family+'.pim')).write_text(mesh)
            (mesh_root/(family+'.pit')).write_text(pit)
            config={'fingerprints':{'mesh':hashlib.sha256(mesh.encode()).hexdigest(),
                'mesh_state':hashlib.sha256(pit.encode()).hexdigest(),
                'model_definition':'1'*64,'model_geometry':'2'*64,
                # Deliberately historical effective-overlay values: these must
                # never supply the accepted placement's original-source guard.
                'source_archive':'3'*64,'sector':'799fc3c78bd6a7e2d9ff6d5a84cefe82328dfac7043475fb7d22faaaec034500',
                'descriptor':'ec979dade04903dd84080e7454849845df2f363324a0559785f51fe05f344a17'},
                'model_geometry':'prefab/gas/'+family+'.pmg',
                'mesh_materials':{'ground':['authored_ground'],'paint':['authored_paint']},
                'material_resources':{'material/authored.dds':'4'*64}}
            path=(self.root/'docs/examples/station-parking-forecourt-tour'/f'{site}.json'
                  if site else self.root/'local_outputs/work/2026-10-19_23-08-00/updated-site-probes/probes/6caf04816ba0000/config.json')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(config))
        reviewed_path=self.root/'docs/examples/station-parking-dawson-two-reviewed-areas.json'
        reviewed_path.write_text(json.dumps(self.reviewed))

    def override(self):
        entry=load_reviewed_catalog(self.root)['prefab/gas/nm_truckstop1_chemron.pmd']
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

    def test_historical_template_guard_edits_cannot_change_original_dawson_pins(self):
        before=deepcopy(self.override())
        path=self.root/'docs/examples/station-parking-forecourt-tour/P05.json'
        historical=json.loads(path.read_text())
        historical['fingerprints'].update(source_archive='a'*64,sector='b'*64,descriptor='c'*64)
        path.write_text(json.dumps(historical))
        self.assertEqual(self.override(),before)


if __name__=='__main__':unittest.main()
