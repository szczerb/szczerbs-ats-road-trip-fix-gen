"""Bounded original functional car-rest census for a placed station facility.

This is an action/geometry inspection, never an icon or fuel-eligibility test.
Absent means no support in the declared 3x3 base/aux inspection, not a global
absence proof. Callers must supply the original effective stack, without fixes.
"""
from __future__ import annotations

import math
import re
import struct

from ..bulk_fuel import prefab_definitions
from ..local_fuel import token
from ..map_sector import parse_sector
from ..fuel_matching import _control_positions
from ..ppd import inspect_ppd
from ..rest_stops import (_hud_numbers, _placed_vertices, _standalone,
                          _standalone_activation, _validate_polygon,
                          inspect_rest_triggers, polygon_distance)
from ..sii import _expand_includes, parse_units
from .geometry import _contains, _within, inspect_station_map

_ERRORS = (ValueError, KeyError, OSError, struct.error)


def _action_index(stack):
    """Resolve custom aliases without allowing one unrelated bad HUD to abort.

    Known non-rest definitions remain known. Invalid/duplicate definitions are
    unknown only when referenced by relevant station geometry.
    """
    result = {}
    for path in stack.matching(r'def/world/trigger_action(?:\.[^/]+)?\.sii'):
        try:
            expanded = _expand_includes(stack.text(path), path, stack.text, ())
            units = parse_units(expanded, source=path)
        except _ERRORS:
            continue
        for unit in units:
            if unit.kind != 'trigger_action':
                continue
            try:
                key = token(unit.name.removeprefix('trig_action.').lower())
            except ValueError:
                # This name cannot be encoded in any map action token.
                continue
            state = {'path': path, 'name': unit.name,
                     'state': 'nonrest', 'vehicles': []}
            try:
                state['command'] = unit.one('command')
                if state['command'] == 'hud_activate':
                    numbers = _hud_numbers(unit)
                    if numbers == (3.,):
                        state.update(state='rest', vehicles=sorted(set(unit.values('str_params'))))
            except ValueError as exc:
                state.update(state='unknown', reason=str(exc))
            if key in result:
                result[key] = {'state': 'unknown', 'reason': 'ambiguous_action_definition'}
            else:
                result[key] = state
    return result


def station_action_state(stack):
    """Resolve parking's shared action contract without global custom failures.

    Unresolved custom definitions stay absent from valid modes and are handled
    as unknown by the facility classifier when relevant. Stock writer actions
    must still satisfy the reviewed native vehicle/HUD contract.
    """
    stack.prefetch(r'def/world/trigger_action.*\.(?:sii|sui)')
    index = _action_index(stack)
    for name, allowed in (('parking_car', ({'car'},)),
                          ('hud_parking', ({'truck', 'bus'}, {'truck', 'bus', 'car'}))):
        action = index.get(token(name), {})
        if action.get('state') != 'rest' or set(action.get('vehicles', [])) not in allowed:
            raise ValueError('Effective rest action differs from reviewed definition: '+name)
    modes = {key: set(row['vehicles']) for key, row in index.items() if row.get('state') == 'rest'}
    known = {key for key, row in index.items() if row.get('state') != 'unknown'}
    hud = {key for key, row in index.items() if row.get('command') == 'hud_activate'}
    return modes, '', known, hud


def _trigger_actions(data):
    header = struct.unpack_from('<24I', data)
    if header[21] + 48 * header[9] != header[22]:
        raise ValueError('Unsupported PPD trigger section extent')
    return {struct.unpack_from('<Q', data, header[21] + 48*i + 4)[0]
            for i in range(header[9])}


def classify_native_car_parking(original, sector_path, prefab_uid, *, definitions=None, cache=None):
    """Return JSON-safe present/absent/unknown original facility support.

    A placement's own functional PPD rest group belongs to that placement.
    Additional standalone/non-GAS prefab rest must be wholly contained by its
    placed light UI lot polygon, or explicitly listed as a placement slave.
    Overlap with another station's lot is ambiguous unless a slave relation
    resolves ownership. Nearby facilities and a 1000-unit radius are never used.
    """
    cache = {} if cache is None else cache
    own = cache.setdefault('native_car_support', {}).setdefault(id(original), {})
    # Holding the stack prevents Python object-ID reuse in long batch sessions.
    own.setdefault('stack', original)
    sectors = own.setdefault('sectors', {})
    descriptors = own.setdefault('descriptors', {})
    key = (sector_path, prefab_uid)
    results = own.setdefault('results', {})
    if key in results:
        return results[key]
    report = {'state': 'unknown', 'reasons': [], 'evidence': [],
              'scope': {'mode': 'original_effective_stack_3x3_base_aux',
                        'sector_paths': [], 'absent_sector_paths': [],
                        'association': 'own PPD groups; explicit slaves; rest geometry within placed station lot',
                        'other_prefab_scope': 'control-node anchor inside target lot; other GAS facilities excluded',
                        'facility_disambiguation_scope': 'other GAS anchors within 100m of target lot only; association still requires contained geometry',
                        'standalone_height_tolerance': 3.,
                        'limitations': ['Bounded source-area inspection is not a whole-world absence proof.',
                                       'Light PPD UI polygons are facility association proxies, not collision geometry.',
                                       'Unrelated external prefabs whose anchors are outside the lot are outside association scope.',
                                       'All original DLC guards are retained; all DLC ownership is assumed.']}}
    reasons = report['reasons']
    evidence = report['evidence']
    def uncertain(reason, **details):
        reasons.append({'reason': reason, **details})
    def done():
        report['state'] = 'present' if evidence else ('unknown' if reasons else 'absent')
        results[key] = report
        return report
    if any(p.startswith('prefab/rtfix/') for p in original.resources):
        uncertain('generated_fixes_in_original_stack')
        return done()
    match = re.fullmatch(r'(map/[^/]+/sec)([+-]\d{4})([+-]\d{4})\.(?:base|aux)', sector_path)
    if match is None:
        uncertain('nonstandard_sector_scope')
        return done()
    prefix, sx, sz = match.groups()
    paths = [f'{prefix}{int(sx)+dx:+05d}{int(sz)+dz:+05d}.{suffix}'
             for dx in (-1, 0, 1) for dz in (-1, 0, 1) for suffix in ('base', 'aux')]
    rows = []
    nodes = {}
    for path in sorted(paths):
        if path not in original.resources:
            report['scope']['absent_sector_paths'].append(path)
            continue
        report['scope']['sector_paths'].append(path)
        if path not in sectors:
            try:
                data = original.read(path, max_bytes=64*1024*1024)
                sectors[path] = (data, parse_sector(data), None)
            except _ERRORS as exc:
                sectors[path] = (None, None, str(exc))
        # Keep a bounded working set while traversing thousands of sectors.
        # Reinsert hits so ordinary filename traversal retains the local halo.
        cached_sector = sectors.pop(path)
        sectors[path] = cached_sector
        while len(sectors) > 128:
            del sectors[next(iter(sectors))]
        data, parsed, error = cached_sector
        if error:
            uncertain('sector_unresolved', path=path, detail=error)
            continue
        rows.extend((path, item, data) for item in parsed.items)
        for node in parsed.nodes:
            nodes.setdefault(node.uid, []).append((path, node))
    def node_for(uid, path, owner=None):
        candidates = [n for p, n in nodes.get(uid, ()) if p == path]
        if not candidates:
            candidates = [n for _, n in nodes.get(uid, ())]
        if owner is not None:
            candidates = [n for n in candidates if owner in (n.forward, n.backward)]
        if not candidates or len({(n.position, n.rotation) for n in candidates}) != 1:
            raise ValueError(f'Unresolved/ambiguous linked node {uid:#x}')
        return candidates[0]
    targets = [(p, i) for p, i, _ in rows if p == sector_path and i.kind == 4 and i.uid == prefab_uid]
    if len(targets) != 1:
        uncertain('selected_prefab_unresolved')
        return done()
    _, target = targets[0]
    if definitions is None:
        if 'definitions' not in own:
            try:
                own['definitions'] = prefab_definitions(original)
            except _ERRORS as exc:
                uncertain('prefab_definitions_unresolved', detail=str(exc))
                return done()
        definitions = own['definitions']
    if 'actions' not in own:
        own['actions'] = _action_index(original)
    actions = own['actions']
    def descriptor(item):
        entry = definitions[item.details['model']]
        path = (entry[0].one('prefab_desc', '') or '').lstrip('/')
        if path not in descriptors:
            try:
                raw = original.read(path, max_bytes=32*1024*1024)
                descriptors[path] = (raw, inspect_ppd(raw), None)
            except _ERRORS as exc:
                descriptors[path] = (None, None, str(exc))
        raw, info, error = descriptors[path]
        if error:
            raise ValueError(error)
        return path, raw, info
    def placement_nodes(path, item):
        return {uid: node_for(uid, path, item.uid) for uid in item.details['nodes']}
    try:
        target_desc, target_ppd, target_info = descriptor(target)
        target_nodes = placement_nodes(sector_path, target)
    except _ERRORS as exc:
        uncertain('selected_descriptor_or_placement_unresolved', detail=str(exc))
        return done()
    lots = []
    lot_heights = []
    try:
        lot_polygons = [p for p in inspect_station_map(target_ppd)['polygons'] if p['color'] == 1]
        control_origin = target.details['origin']
        local_origin_y = _control_positions(target_ppd)[control_origin][1]
        anchor_y = target_nodes[target.details['nodes'][0]].position[1]
        lot_heights = [anchor_y+p[1]-local_origin_y for polygon in lot_polygons for p in polygon['vertices']]
        lots = [_placed_vertices(target_ppd, target, target_nodes, p['vertices'])
                for p in lot_polygons]
        if not lots:
            raise ValueError('No light station lot polygon')
    except _ERRORS as exc:
        uncertain('facility_lot_unresolved', detail=str(exc))
    def touches_lot(points):
        return any(polygon_distance(points, lot) < 1e-6 for lot in lots)
    def inside_lot(points):
        return any(_within(points, lot) for lot in lots)
    def inspect_groups(path, item, ppd, relation, own_placement=False):
        group_cache = own.setdefault('groups', {})
        if id(ppd) not in group_cache:
            referenced = _trigger_actions(ppd)
            relevant = {a for a in referenced if actions.get(a, {}).get('state') != 'nonrest'}
            group_cache[id(ppd)] = inspect_rest_triggers(ppd, actions=relevant)
        groups = group_cache[id(ppd)]
        placed_nodes = placement_nodes(path, item)
        for group in groups:
            points = _placed_vertices(ppd, item, placed_nodes, group['vertices'])
            if not own_placement and lot_heights:
                local_y = _control_positions(ppd)[item.details['origin']][1]
                world_y = placed_nodes[item.details['nodes'][0]].position[1]
                heights = [world_y+p[1]-local_y for p in group['vertices']]
                if max(heights) < min(lot_heights)-3. or min(heights) > max(lot_heights)+3.:
                    continue
            if not own_placement and not inside_lot(points):
                if touches_lot(points):
                    uncertain('rest_geometry_partial_facility_overlap', path=path, uid=hex(item.uid))
                continue
            action = actions.get(group['action'], {})
            if action.get('state') in (None, 'unknown'):
                uncertain('rest_action_unresolved', path=path, uid=hex(item.uid), action=hex(group['action']))
            elif action.get('state') == 'rest' and 'car' in action['vehicles']:
                evidence.append({'kind': 'prefab', 'path': path, 'uid': hex(item.uid),
                                 'group': group['id'], 'action': action['name'],
                                 'vehicles': action['vehicles'], 'relation': relation,
                                 'polygon_xz': [list(p) for p in points]})
    try:
        inspect_groups(sector_path, target, target_ppd, 'selected_placement', True)
    except _ERRORS as exc:
        uncertain('selected_rest_groups_unresolved', detail=str(exc))
    # Other GAS lots disambiguate standalone support overlapping two facilities.
    other_lots = []
    external = []
    for path, item, data in rows:
        if item.kind != 4 or item.uid == target.uid:
            continue
        linked = item.uid in target.details['slaves']
        near = False
        try:
            pose = node_for(item.details['nodes'][0], path, item.uid).position
            near = any(_contains((pose[0], pose[2]), lot) for lot in lots)
            disambiguate = any(polygon_distance([(pose[0], pose[2])], lot) <= 100. for lot in lots)
            if not linked and not disambiguate:
                continue
            desc, ppd, info = descriptor(item)
            if any(s['type'] == 3 for s in info['spawns']):
                for polygon in inspect_station_map(ppd)['polygons']:
                    if polygon['color'] == 1:
                        other_lots.append(_placed_vertices(ppd, item, placement_nodes(path, item), polygon['vertices']))
                continue
            if linked or near:
                external.append((path, item, ppd, linked))
        except _ERRORS as exc:
            if linked or near:
                uncertain('associated_prefab_unresolved', path=path, uid=hex(item.uid), detail=str(exc))
    for path, item, ppd, linked in external:
        try:
            inspect_groups(path, item, ppd, 'explicit_slave' if linked else 'contained_in_station_lot', linked)
        except _ERRORS as exc:
            uncertain('associated_rest_prefab_unresolved', path=path, uid=hex(item.uid), detail=str(exc))
    for path, item, data in rows:
        if item.kind == 0x28:
            # Container anchor bounds relevance; nested coordinates themselves
            # have no proven world transform. Do not poison a distant facility.
            try:
                anchor = node_for(item.details['node'], path).position
                if not any(_contains((anchor[0], anchor[2]), lot) for lot in lots):
                    continue
                def potential_nested(items):
                    for child in items:
                        if child.kind == 0x22:
                            return True
                        if child.kind == 4:
                            _, raw, _ = descriptor(child)
                            if any(actions.get(a, {}).get('state') in (None, 'unknown')
                                   or 'car' in actions.get(a, {}).get('vehicles', [])
                                   for a in _trigger_actions(raw)):
                                return True
                        if child.kind == 0x28 and potential_nested(child.details['items']):
                            return True
                    return False
                if potential_nested(item.details['items']):
                    uncertain('compound_rest_scope_unresolved', path=path, uid=hex(item.uid))
            except _ERRORS as exc:
                uncertain('compound_scope_unresolved', path=path, uid=hex(item.uid), detail=str(exc))
            continue
        if item.kind != 0x22:
            continue
        linked = item.uid in target.details['slaves']
        near = False
        try:
            trigger = _standalone(data, item)
            if not any(actions.get(a['action'], {}).get('state') != 'nonrest'
                       or (a['custom'] and actions.get(a['action'], {}).get('command') == 'hud_activate')
                       for a in trigger['actions']):
                continue
            # Raw referenced node poses may safely prove a distant trigger
            # irrelevant even when an ownership link is unsupported. Missing
            # poses never establish that proof. No generic item bounds are used.
            hints = [n.position for uid in trigger['nodes'] for _, n in nodes.get(uid, ())]
            if not linked and all(nodes.get(uid) for uid in trigger['nodes']) and hints and lots:
                hint_radius = trigger['radius']
                if len(trigger['nodes']) == 2:
                    hint_radius = max(math.dist(a, b) for a in hints for b in hints)
                lx = min(p[0] for lot in lots for p in lot)
                hx = max(p[0] for lot in lots for p in lot)
                lz = min(p[1] for lot in lots for p in lot)
                hz = max(p[1] for lot in lots for p in lot)
                if (max(p[0] for p in hints)+hint_radius < lx or min(p[0] for p in hints)-hint_radius > hx
                        or max(p[2] for p in hints)+hint_radius < lz or min(p[2] for p in hints)-hint_radius > hz):
                    continue
            positions = [node_for(uid, path, item.uid).position for uid in trigger['nodes']]
            points = [(p[0], p[2]) for p in positions]
            radius = trigger['radius']
            if len(points) == 2:
                radius = math.dist(positions[0], positions[1])
                points = points[:1]
            elif len(points) > 2:
                _validate_polygon(points)
            near = linked or any(polygon_distance(points, lot) <= radius+1e-6 for lot in lots)
            if not near:
                continue
            if not linked and lot_heights and (max(p[1] for p in positions)+radius < min(lot_heights)-3.
                                               or min(p[1] for p in positions)-radius > max(lot_heights)+3.):
                continue
            activation = _standalone_activation(item.flags)
            if activation['init_disabled'] or not activation['vehicle_activation']:
                continue
            if radius:
                # A finite polygon approximation is insufficient to prove that
                # an entire sphere belongs to this facility. Exact disk extrema
                # plus edge clearance prove containment for simple lot rings.
                contained = any(_contains(points[0], lot) and all(
                    polygon_distance([points[0]], [a, b]) >= radius
                    for a, b in zip(lot, lot[1:]+lot[:1])) for lot in lots)
            else:
                contained = inside_lot(points)
            if not linked and (not contained or any(polygon_distance(points, lot) <= radius+1e-6 for lot in other_lots)):
                uncertain('standalone_facility_association_ambiguous', path=path, uid=hex(item.uid))
                continue
            for record in trigger['actions']:
                action = actions.get(record['action'], {})
                if action.get('state') == 'nonrest' and not (record['custom'] and action.get('command') == 'hud_activate'):
                    continue
                if action.get('state') in (None, 'unknown') or record['custom']:
                    uncertain('standalone_action_or_parameters_unresolved', path=path, uid=hex(item.uid), action=hex(record['action']))
                elif 'car' in action['vehicles']:
                    evidence.append({'kind': 'standalone', 'path': path, 'uid': hex(item.uid),
                                     'action': action['name'], 'vehicles': action['vehicles'],
                                     'relation': 'explicit_slave' if linked else 'contained_in_station_lot',
                                     'polygon_xz': [list(p) for p in points], 'radius': radius,
                                     'activation': activation})
        except _ERRORS as exc:
            # Broken associated nodes cannot prove unrelatedness. Unknown is
            # deliberately conservative for undecodable standalone structures.
            uncertain('standalone_geometry_unresolved', path=path, uid=hex(item.uid), detail=str(exc))
    return done()
