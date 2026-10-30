"""Source-reviewed truck-parking curve families; no placement allowlist.

Observed locally: ATS 1.61.3.18, 2026-10-25. Model bytes and converted paint
geometry are independently retained under the r13 local research evidence.
"""
from __future__ import annotations

from ..local_fuel import token
from ..sii import _LEXEMES, _expand_includes, parse_units

_TRUCK_DIRT = 'model/props/road/parking_1line_truck_dirt_curve.pmd'


def reviewed_curve_catalog():
    """Return immutable-by-convention family rules backed by original model data."""
    return {_TRUCK_DIRT: {
        'family': 'parking_1line_truck_dirt_curve',
        'model_sha256': '29d624c8bc330ba4955294752bba54923762b31265b5dcedf6ca439ea624e4b9',
        'geometry_sha256': '39649547f340b1ec006a3f38e7f443d104b1af50de3715f78c86457ea23a1723',
        'model_geometry': _TRUCK_DIRT[:-4] + '.pmg',
        # Converted paint X extent is [-24.356079, -.202494]; conservative
        # activation keeps the intended full truck footprint, with a 0.4m
        # longitudinal inset at both ends and no maneuvering-aisle expansion.
        'depth': 24.36, 'near_edge': .20, 'end_setback': .40,
        'side': 'left', 'minimum_length': 7., 'maximum_length': 250.,
        'maximum_height_delta': .75, 'maximum_chord_error': .05,
        'supported_variations': ('default', 'yellow'),
        'supported_center_parts': tuple('center' + s for s in
            ['1','2','3','4','5','6','7','8','9','10','_y1','_y2','_y3','_y4','_y5','_y6','_y7','_y8','_y9','_y10']),
        'supported_end_parts': ('start1', 'start_y1', 'end1', 'end_y1'),
        'evidence': 'local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/site/',
    }}


def load_curve_definitions(stack):
    """Resolve effective semantic curve units, including all DLC root lists."""
    pattern = r'def/world/curve_model(?:\.[^/]+)?\.sii'
    stack.prefetch(r'def/world/curve_model.*\.(?:sii|sui)')
    result = {}
    for path in stack.matching(pattern):
        text = _expand_includes(stack.text(path), path, stack.text, ())
        # SCS source units contain literal horizontal tabs inside display
        # strings. Normalize that legal SII spelling for the strict shared
        # JSON-string reader without interpreting or changing string content.
        text = _LEXEMES.sub(lambda m: m[0].replace(chr(9), chr(92)+'t')
                            if m[0].startswith(chr(34)) else m[0], text)
        for unit in parse_units(text, source=path):
            if unit.kind != 'curve_model':
                continue
            key = token(unit.name.removeprefix('curve.').lower())
            model = unit.one('model_desc')
            if model is None:
                # Tree/vegetation procedural curves have no model descriptor.
                continue
            entry = {'unit': unit, 'definition_path': path,
                     'model_path': model.lstrip('/')}
            if key in result:
                raise ValueError('Ambiguous effective curve definition: ' + unit.name)
            result[key] = entry
    return result


# Source-pinned reviewed supplement to all-placement family rules. User
# clarified the perpendicular short tractor bank on 2026-10-25; source NPC
# classes distinguish that intended arrangement from the full-rig banks.
_NORTH_PLATTE_REVIEW = {'site_id': 'north-platte-east-junction-truck-lot',
 'source_sector': 'map/usa/sec-0005-0003.base',
 'visual_sector': 'map/usa/sec-0005-0003.aux',
 'template_trigger_uid': '0x4f3027f3fdab0001',
 'paint_compound_uid': '0x5269d91ea0100000',
 'native_bank_curve_uid': '0x4ca10d2c8a900001',
 'missing_bank_curve_uid': '0x4ca10ef459d00001',
 'source_hashes': {'map/usa/sec-0005-0003.base': '506a11b2b3649059d95c0740d6ec1d5ad9f31ea78836c1699b737badd7adc431',
                   'map/usa/sec-0005-0003.aux': '7cebac27a9b7f70f58128632b10be2a21b9ba44f6622703d286aa4d93f7c42e7'},
 'source_package_name': 'ATS_Expansion_v23.0_1.61.scs',
 'areas': [{'id': 'north-platte-short-perpendicular-bobtail-bank',
            'vertices': [[-19231.80329515761, 32.171875, -11688.26698707254],
                         [-19208.85798265761, 32.171875, -11694.61073707254],
                         [-19211.44279780174, 32.171875, -11703.960000715775],
                         [-19234.38811030174, 32.171875, -11697.616250715775]],
            'vehicle_fit': 'Source painted nine-to-ten-meter bank with native bobtail NPCs; '
                           'tractor-only parking is intended here, unlike adjacent full-rig banks.',
            'source_curve_uids': ['0x4ca016b0a7900000',
                                  '0x4ca016e84e100000',
                                  '0x4ca016f0ce900000',
                                  '0x4ca01700c0d00000',
                                  '0x4ca01708cc900000',
                                  '0x4ca017105b900000',
                                  '0x4ca01718e3500000',
                                  '0x4ca01728dc900000'],
            'dimensions': {'length': 23.806, 'depth': 9.7}},
           {'id': 'north-platte-edge-parallel-rig-strip',
            'vertices': [[-19252.00906433756, 32.16015625, -11738.609756642636],
                         [-19202.951361462285, 32.16015625, -11752.550409016218],
                         [-19201.42062316244, 32.16015625, -11747.163680857364],
                         [-19250.478326037715, 32.16015625, -11733.223028483782]],
            'vehicle_fit': 'Continuous 51m by 5.6m source edge strip occupied by two variable NPC '
                           'rigs; each intended rig arrangement is parallel to the lot edge.',
            'source_npc_uids': ['0x4ca02b24c1d00000', '0x4ca02b4498100000'],
            'dimensions': {'length': 51.0, 'depth': 5.6}}],
 'source_npcs': [{'uid': '0x4ca0175883100000',
                  'model': 'traffic.parked.truck',
                  'node': '0x4ca017588bd00001',
                  'bounds_xyz': [-19220.38671875,
                                 32.0368766784668,
                                 -11702.8427734375,
                                 -19214.86328125,
                                 36.47687530517578,
                                 -11692.564453125],
                  'flags': 512},
                 {'uid': '0x4ca017bcea900000',
                  'model': 'traffic.parked.truck',
                  'node': '0x4ca017bcdc100001',
                  'bounds_xyz': [-19228.88671875,
                                 32.0368766784668,
                                 -11700.7021484375,
                                 -19223.36328125,
                                 36.47687530517578,
                                 -11690.423828125],
                  'flags': 512},
                 {'uid': '0x4ca017c8a9d00000',
                  'model': 'traffic.parked.truck',
                  'node': '0x4ca017c822d00001',
                  'bounds_xyz': [-19234.51171875,
                                 32.0251579284668,
                                 -11699.1123046875,
                                 -19228.98828125,
                                 36.46515655517578,
                                 -11688.833984375],
                  'flags': 512},
                 {'uid': '0x4ca02b24c1d00000',
                  'model': 'traffic.parked.truck.trailer',
                  'node': '0x4ca02b24ff500001',
                  'bounds_xyz': [-19226.8046875,
                                 32.0368766784668,
                                 -11750.9912109375,
                                 -19203.162109375,
                                 36.34687423706055,
                                 -11741.451171875],
                  'flags': 512},
                 {'uid': '0x4ca02b4498100000',
                  'model': 'traffic.parked.truck.trailer',
                  'node': '0x4ca02b444f900001',
                  'bounds_xyz': [-19250.26953125,
                                 32.0368766784668,
                                 -11744.3232421875,
                                 -19226.626953125,
                                 36.34687423706055,
                                 -11734.783203125],
                  'flags': 512}]}


def north_platte_reviewed_regions(stack, *, map_packages=None):
    """Return two independent reviewed regions after exact original-source pins.

    The main long missing bank comes from general curve-family discovery.
    These supplement it with the source painted perpendicular bobtail bank
    and parallel full-rig edge strip, neither of which may expand car access.
    Call this on the original ownership stack, never a generated overlay.
    Only the partition explicitly selecting the reviewed source may apply this
    supplement. Other maps can legitimately provide these standard sector paths.
    """
    from copy import deepcopy
    import hashlib
    from pathlib import Path
    from ..map_sector import parse_sector
    review = deepcopy(_NORTH_PLATTE_REVIEW)
    selected = (map_packages if map_packages is not None else
                (str(package.path) for package in getattr(stack, 'packages', ())))
    if not any(Path(package).name == review['source_package_name'] for package in selected):
        return None
    for path,digest in review['source_hashes'].items():
        if path not in stack.resources:
            raise ValueError('North Platte reviewed source sector missing: '+path)
        _,resource = stack.resources[path]
        if Path(resource.package).name != review['source_package_name']:
            raise ValueError('North Platte reviewed source provider drift: '+path)
        data = stack.read(path, max_bytes=64*1024*1024)
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('North Platte reviewed original sector drift: '+path)
    data=stack.read(review['source_sector'],max_bytes=64*1024*1024)
    parsed=parse_sector(data)
    trigger=next((i for i in parsed.items if i.uid==int(review['template_trigger_uid'],16)),None)
    if trigger is None or trigger.kind != 0x22:
        raise ValueError('North Platte native standalone source trigger drift')
    review['provenance'] = ('Observed locally, ATS 1.61.3.18, original r12 37-source stack, '
        '2026-10-25. User clarified two large banks separated by an aisle plus '
        'the shorter perpendicular tractor bank. Original NPC classes corroborate '
        'intended parking and variable occupancy; NPCs remain unchanged.')
    review['evidence_receipt'] = 'local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/site/north-platte-original-receipt.json'
    return review
