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


# Observed locally, ATS 1.61.3.18 / Alaska Expansion 1.2.3, 2026-10-24.
# These are original inputs, independently inspected during the r12 rebuild.
# P05's historical effective sector AND descriptor contain generated overlays;
# neither historical hash may stand in for the original resource below.
_DAWSON_ORIGINAL_SOURCE = {
    'source_archive': 'd879c245c1bc8b88c9a884d88952ccaad88b58ce759f665832fd0b664a6200fb',
    'source_sector': 'ddc5fcee53d1ac3e0b15ba48bb4c47da0492f6abefaea47c4209fa3fa019e532',
    'original_descriptor': '92be3a4ee1a2788d32ca80bde50256c0e73032ee3caad2739df3d001b3715f91',
    'original_descriptor_provider': 'base.scs',
}

def _sha(data):
    return hashlib.sha256(data).hexdigest()


METADATA_PATH = Path(__file__).with_name('reviewed_catalog.json')


def reviewed_metadata(metadata_path=None):
    """Read project-authored review metadata, including all four family pins."""
    return json.loads(Path(metadata_path or METADATA_PATH).read_text(encoding='utf-8'))


def read_evidence(path, expected, family, label):
    """Read ConverterPIX text using the historical normalized-text hash contract."""
    try:
        value = Path(path).read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        raise ValueError(f'Station evidence missing or unreadable: {path}; '
                         'prepare it with python -m ats_road_trip.station_parking.evidence') from exc
    if _sha(value.encode()) != expected:
        raise ValueError(f'Reviewed catalog converted {label} SHA-256 drift: {family}')
    return value


def load_reviewed_catalog(station_evidence_dir=None, *, metadata_path=None):
    """Load four reviewed families from an explicitly supplied flat PIM/PIT dir.

    No historical output directory is searched. Station placement identities and
    historical effective sector/descriptor hashes never select family layouts.
    """
    if station_evidence_dir is None:
        raise ValueError('station_bays requires --station-evidence-dir; '
                         'see docs/reference/STATION_PARKING_EVIDENCE.md')
    root = Path(station_evidence_dir).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f'Station evidence directory does not exist: {root}')
    metadata = reviewed_metadata(metadata_path)
    config_path = Path(metadata_path or METADATA_PATH)
    catalog = {}
    for config in metadata['families']:
        family = config['family']
        mesh_path = root / (family + '.pim')
        mesh = read_evidence(mesh_path, config['fingerprints']['mesh'], family, 'mesh')
        pit = read_evidence(mesh_path.with_suffix('.pit'),
                            config['fingerprints']['mesh_state'], family, 'mesh_state')
        model = config['model_geometry'][:-4] + '.pmd'
        catalog[model] = {
            'family': family, 'model_geometry': config['model_geometry'],
            'fingerprints': deepcopy(config['fingerprints']),
            'mesh_materials': deepcopy(config['mesh_materials']),
            'material_resources': deepcopy(config['material_resources']),
            'mesh_text': mesh, 'mesh_state_text': pit, 'methods': list(config['methods']),
            'parameters': {}, 'evidence_config': str(config_path),
            'evidence_mesh': str(mesh_path),
            'source_descriptors': [model[:-4]+'.ppd', model[:-4]+'_rt.ppd'],
            'policy': {'curb_setback': .15, 'prefer_perpendicular': True,
                       'single_painted_bays': True, 'require_curb_evidence': True},
        }
    # Preserve the accepted exact geometry, bound to its original placement.
    reviewed = metadata['dawson_reviewed_areas']
    override = {'prefab_uid': reviewed['prefab_uid'], 'sector': reviewed['sector'],
                **_DAWSON_ORIGINAL_SOURCE,
                'descriptor': 'prefab/gas/nm_truckstop1_chemron.ppd',
                'mesh': reviewed['mesh'], 'areas': deepcopy(reviewed['areas']),
                'provenance': 'Exact areas: docs/examples/station-parking-dawson-two-reviewed-areas.json, user accepted 2026-10-24. Original guards: Alaska Expansion 1.2.3 archive and direct ZIP sector; effective ATS 1.61.3.18 descriptor from base.scs, inspected 2026-10-24. P05 historical effective sector/descriptor overlay hashes are deliberately excluded.'}
    catalog['prefab/gas/nm_truckstop1_chemron.pmd']['policy']['reviewed_areas'] = [override]
    return catalog
