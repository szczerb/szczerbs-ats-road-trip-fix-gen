"""Reviewed model families, independent of station placement identities.

The local converted models are inputs, never shipped in generated mods. Their
PIM/PIT, binary model and named material fingerprints remain review gates.
Callers can serialize this catalog with their reproduction configuration.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def load_reviewed_catalog(repo_root=None):
    """Load retained reviewed conversion evidence for four layout families.

    This is a model-family catalog; the template's station/sector/UID and
    historical descriptor/sector hashes are deliberately discarded. Every
    effective original placement of the family is eligible for evaluation.
    """
    root=Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    bundle=root/'local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle'
    rows=[
        ('nm_gas_station1_chemron',root/'docs/examples/station-parking-forecourt-tour/P01.json',
         bundle/'inputs/models/nm_gas_station1_chemron.pim',('painted_bays',)),
        ('nm_truckstop1_chemron',root/'docs/examples/station-parking-forecourt-tour/P05.json',
         bundle/'inputs/models/nm_truckstop1_chemron.pim',('painted_bays','unmarked_geometry')),
        ('nm_gas_station2-corner_chemron',root/'docs/examples/station-parking-forecourt-tour/P09.json',
         bundle/'inputs/models/nm_gas_station2-corner_chemron.pim',('unmarked_geometry',)),
        ('nm_gas_station2-corner_gp',root/'local_outputs/work/2026-10-19_23-08-00/updated-site-probes/probes/6caf04816ba0000/config.json',
         root/'local_outputs/work/2026-10-19_21-19-20/marked-station-inventory/converted-effective-gp/prefab/gas/nm_gas_station2-corner_gp.pim',('unmarked_geometry',)),
    ]
    catalog={}
    for family,config_path,mesh_path,methods in rows:
        config=json.loads(config_path.read_text(encoding='utf-8'))
        mesh=mesh_path.read_text(encoding='utf-8-sig')
        pit=mesh_path.with_suffix('.pit').read_text(encoding='utf-8-sig')
        for label,text in [('mesh',mesh),('mesh_state',pit)]:
            if _sha(text.encode())!=config['fingerprints'][label]:
                raise ValueError('Reviewed catalog converted '+label+' SHA-256 drift: '+family)
        model=config['model_geometry'][:-4]+'.pmd'
        catalog[model]={
            'family':family,'model_geometry':config['model_geometry'],
            'fingerprints':{key:config['fingerprints'][key] for key in
                            ('model_definition','model_geometry','mesh','mesh_state')},
            'mesh_materials':deepcopy(config['mesh_materials']),
            'material_resources':deepcopy(config['material_resources']),
            'mesh_text':mesh,'mesh_state_text':pit,'methods':list(methods),
            'parameters':{},'evidence_config':str(config_path),'evidence_mesh':str(mesh_path),
            # Only original non-generated descriptor paths may supply a layout.
            # Each actual source descriptor is hash-pinned in the map report.
            'source_descriptors':[model[:-4]+'.ppd',model[:-4]+'_rt.ppd'],
            'policy':{'curb_setback':.15,'prefer_perpendicular':True,
                      'single_painted_bays':True,'require_curb_evidence':True},
        }
    # Keep the exact accepted Dawson geometry, but bind it to the original
    # placement/source rather than mounting the historical generated r10/r11.
    reviewed_path=root/'docs/examples/station-parking-dawson-two-reviewed-areas.json'
    if reviewed_path.is_file():
        reviewed=json.loads(reviewed_path.read_text(encoding='utf-8'))
        pin=json.loads((root/'docs/examples/station-parking-forecourt-tour/P05.json').read_text(encoding='utf-8'))
        override={'prefab_uid':reviewed['prefab_uid'],'sector':reviewed['sector'],
                  'source_archive':pin['fingerprints']['source_archive'],
                  'source_sector':pin['fingerprints']['sector'],
                  'original_descriptor':pin['fingerprints']['descriptor'],
                  'descriptor':'prefab/gas/nm_truckstop1_chemron.ppd',
                  'mesh':reviewed['mesh_sha256'],'areas':deepcopy(reviewed['areas']),
                  'provenance':'docs/examples/station-parking-dawson-two-reviewed-areas.json; user accepted 2026-10-24; original P05 source pins'}
        catalog['prefab/gas/nm_truckstop1_chemron.pmd']['policy']['reviewed_areas']=[override]
    return catalog
