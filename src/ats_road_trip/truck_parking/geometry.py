"""Decode authored truck paint curves without confusing scenery with facilities.

Curve and compound node positions in map-907 are already world XYZ, including
nested compound nodes. They must not receive a second compound transform.
Discovery is independent of fuel/GAS and of passenger-car eligibility. A bank
is evidence of truck parking intent, not proof of a functional rest facility.
"""
from __future__ import annotations

import math
import struct

from ..local_fuel import token
from ..map_sector import _Reader
from ..rest_stops import _inside, _point_segment, _validate_polygon, polygon_distance
from .catalog import reviewed_curve_catalog


def _point(p):
    if len(p) != 3 or any(not math.isfinite(x) for x in p):
        raise ValueError('Unsafe curve node position')
    return tuple(float(x) for x in p)


def _subcurves(data, item):
    r = _Reader(data)
    r.pos = item.offset + 57
    refs = tuple(r.read('Q') for _ in range(4))
    length, mask = r.read('fI')
    result = []
    for index in range(32):
        if not mask & (1 << index):
            continue
        model = r.read('Q')
        flags, seed, stretch, scale, fixed_step = r.read('IIfff')
        material = r.read('Q')
        color, rotation = r.read('If')
        start, end, variation, look = r.read('4Q')
        heights = tuple(r.read('f') for _ in range(r.count(4)))
        offsets = r.read('5f')
        if any(not math.isfinite(x) for x in
               (length, stretch, scale, fixed_step, rotation, *heights, *offsets)):
            raise ValueError('Nonfinite subcurve layout')
        result.append({'index': index, 'model': model, 'flags': flags,
                       'seed': seed, 'stretch': stretch, 'scale': scale,
                       'fixed_step': fixed_step, 'terrain_material': material,
                       'color': color, 'terrain_rotation': rotation,
                       'start_part': start, 'end_part': end,
                       'variation': variation, 'look': look,
                       'height_offsets': heights, 'offsets': offsets})
    if r.pos != item.end:
        raise ValueError('Curve extent disagrees with supported layout')
    return refs, length, result


def discover_curve_banks(sectors, definitions, catalog=None):
    """Return reviewed-family bank candidates and explicit layout diagnostics.

    ``sectors`` entries are ``{'path','data','parsed'}`` or matching three-tuples.
    Callers validate original effective model hashes before emitting candidates.
    Compound lineage, source UIDs and nodes are retained for facility association;
    geographic proximity alone must not associate otherwise unrelated lots.
    """
    catalog = reviewed_curve_catalog() if catalog is None else catalog
    entries = []
    for row in sectors:
        if isinstance(row, dict):
            entries.append((row['path'], row['data'], row['parsed']))
        else:
            entries.append(tuple(row))
    root_nodes, flattened = {}, []
    for _, _, parsed in entries:
        for node in parsed.nodes:
            old = root_nodes.get(node.uid)
            if old and (old.position != node.position or old.rotation != node.rotation):
                raise ValueError('Conflicting root node identity across sectors')
            root_nodes[node.uid] = node
    def walk(path, data, items, lineage, inherited_nodes):
        for item in items:
            flattened.append((path, data, item, lineage, inherited_nodes))
            children = item.details.get('items', ())
            if children:
                local_nodes = dict(inherited_nodes)
                # Compound internals use a placement-local namespace; identical
                # child UIDs in distinct compounds must not overwrite one another.
                local_nodes.update({n.uid:n for n in item.details.get('compound_nodes', ())})
                walk(path, data, children, (*lineage, item.uid), local_nodes)
    for path, data, parsed in entries:
        walk(path, data, parsed.items, (), root_nodes)
    banks, diagnostics, seen = [], [], set()
    for path, data, item, lineage, nodes in flattened:
        if item.kind != 0x2c:
            continue
        refs, length, subs = _subcurves(data, item)
        for sub in subs:
            definition = definitions.get(sub['model'])
            if not definition:
                continue
            model = definition['model_path'].lstrip('/')
            if model not in catalog and 'parking' not in model:
                continue
            identity = (path, lineage, item.uid, sub['index'])
            if identity in seen:
                raise ValueError('Duplicate effective curve identity')
            seen.add(identity)
            record = {'uid': hex(item.uid), 'sector': path,
                      'parent_uid': hex(lineage[-1]) if lineage else None,
                      'compound_lineage': [hex(v) for v in lineage],
                      'model_path': model, 'subcurve_index': sub['index']}
            if model not in catalog:
                diagnostics.append({**record, 'reason': 'unreviewed_parking_curve_family'})
                continue
            policy = catalog[model]
            try:
                if any(u not in nodes for u in refs[:2]):
                    raise ValueError('unresolved_curve_node_across_sector_boundary')
                if any(refs[2:]):
                    raise ValueError('curved_or_locator_modified_bank')
                if len(subs) != 1:
                    raise ValueError('multiple_subcurves_require_separate_review')
                a, b = (_point(nodes[u].position) for u in refs[:2])
                dx, dz = b[0]-a[0], b[2]-a[2]
                chord = math.hypot(dx, dz)
                if not policy['minimum_length'] <= chord <= policy['maximum_length']:
                    raise ValueError('truck_bank_length_outside_reviewed_range')
                if abs(length-chord) > policy['maximum_chord_error']:
                    raise ValueError('nonstraight_or_modified_bank_curve')
                if abs(a[1]-b[1]) > policy['maximum_height_delta']:
                    raise ValueError('unsafe_bank_height_delta')
                # Source flags are retained in diagnostics; specific nonzero
                # transforms/offsets require evidence rather than silent guesses.
                if item.flags not in (0, 4194304):
                    raise ValueError('unreviewed_curve_item_flags')
                if sub['flags'] != 0:
                    raise ValueError('unreviewed_subcurve_flags')
                if sub['stretch'] != 1. or sub['scale'] != 1.:
                    raise ValueError('scaled_or_stretched_bank_requires_review')
                if (any(abs(v) > .20 for v in sub['height_offsets'])
                        or any(sub['offsets'])):
                    raise ValueError('offset_bank_requires_review')
                allowed = {token(x) for x in policy['supported_variations']}
                # Empty variation lets engine select the definition default.
                if sub['variation'] not in allowed | {0}:
                    raise ValueError('unreviewed_bank_variation')
                if sub['start_part'] not in {0, *(token(x) for x in policy['supported_end_parts'])}:
                    raise ValueError('unreviewed_bank_start_part')
                if sub['end_part'] not in {0, *(token(x) for x in policy['supported_end_parts'])}:
                    raise ValueError('unreviewed_bank_end_part')
                ux, uz = dx/chord, dz/chord
                vx, vz = -uz, ux
                near, far, inset = policy['near_edge'], policy['depth'], policy['end_setback']
                def vertex(t, side):
                    return (a[0]+ux*t+vx*side,
                            a[1]+(b[1]-a[1])*t/chord,
                            a[2]+uz*t+vz*side)
                vertices = [vertex(inset, near), vertex(chord-inset, near),
                            vertex(chord-inset, far), vertex(inset, far)]
                _validate_polygon([(p[0], p[2]) for p in vertices])
                banks.append({**record, 'id': f'curve-{lineage[-1] if lineage else 0:016x}-{item.uid:016x}-{sub["index"]}',
                              'family': policy['family'], 'vertices': vertices,
                              'polygon_xz': [(p[0],p[2]) for p in vertices],
                              'source_curve_nodes': [hex(v) for v in refs[:2]],
                              'source_model_token': hex(sub['model']),
                              'source_endpoints': [a,b], 'source_curve_length': length,
                              'source_flags': item.flags, 'subcurve': sub,
                              'dimensions': {'length': chord-2*inset, 'depth': far-near},
                              'coordinate_frame': 'world_xyz_including_compound_nodes'})
            except ValueError as exc:
                diagnostics.append({**record, 'reason': str(exc)})
    return banks, diagnostics


def _signed_area(poly):
    ox, oz = poly[0]
    return sum((a[0]-ox)*(b[1]-oz)-(b[0]-ox)*(a[1]-oz)
               for a,b in zip(poly,poly[1:]+poly[:1])) / 2


def _clip_convex(subject, clip):
    orientation = 1 if _signed_area(clip) > 0 else -1
    result = list(subject)
    for a,b in zip(clip,clip[1:]+clip[:1]):
        def side(p):
            return orientation*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
        previous, result0 = result, []
        if not previous:break
        p = previous[-1]
        for q in previous:
            sp,sq=side(p),side(q)
            if (sp>=-1e-7)!=(sq>=-1e-7):
                t=sp/(sp-sq)
                result0.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
            if sq>=-1e-7:result0.append(q)
            p=q
        result=result0
    return result


def _convex(poly):
    crosses = []
    for a,b,c in zip(poly,poly[1:]+poly[:1],poly[2:]+poly[:2]):
        cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
        if abs(cross)>1e-7:crosses.append(cross>0)
    return bool(crosses) and len(set(crosses))==1


def compare_coverage(vertices, native_polygons):
    """Conservative exact containment classification against native convex areas.

    A concave native area can prove contact, but cannot establish full coverage
    through this limited classifier. Multiple native areas whose union would
    cover a bank remain partial unless one independently contains it.
    """
    region=[(p[0],p[2]) if len(p)==3 else tuple(p) for p in vertices]
    try:_validate_polygon(region)
    except ValueError:return {'state':'unknown','reason':'invalid_candidate_polygon'}
    touching=[]; unknown=[]; maximum_fraction=0.
    for index,raw in enumerate(native_polygons):
        values=raw.get('vertices', raw.get('polygon_xz')) if isinstance(raw,dict) else raw
        native=[(p[0],p[2]) if len(p)==3 else tuple(p) for p in values]
        try:_validate_polygon(native)
        except ValueError:unknown.append(index);continue
        if polygon_distance(region,native)>1e-6:continue
        touching.append(index)
        if _convex(native):
            overlap=_clip_convex(region,native)
            fraction=abs(_signed_area(overlap)) / abs(_signed_area(region)) if len(overlap)>=3 else 0.
            maximum_fraction=max(maximum_fraction,min(1.,fraction))
        if _convex(native) and all(_inside(p,native) or
                min(_point_segment(p,a,b) for a,b in zip(native,native[1:]+native[:1]))<1e-6 for p in region):
            return {'state':'fully_covered','native_indices':[index], 'maximum_native_coverage_fraction':1.}
    if touching:return {'state':'partially_covered','native_indices':touching,
                        'reason':'native_union_or_concavity_not_assumed',
                        'maximum_native_coverage_fraction':maximum_fraction}
    if unknown:return {'state':'unknown','reason':'invalid_native_polygon','native_indices':unknown}
    return {'state':'uncovered','native_indices':[], 'maximum_native_coverage_fraction':0.}
