"""Bounded external map-object proximity checks for station parking.

Only decoded PPD v25 non-accessible UI polygons are used as coarse solid
obstacle proxies. They are not collision geometry. Unsupported placements and
uninterpreted item extents are reported, never guessed from generic bounds.
"""
from __future__ import annotations

import hashlib
import math
import struct
from collections import Counter

from ..archive import Archive
from ..bulk_fuel import prefab_definitions
from ..map_sector import parse_sector
from ..package import virtual_path
from ..ppd import inspect_ppd
from ..rest_stops import _placed_vertices, _validate_polygon, polygon_distance
from .geometry import _xz

_ACCESSIBLE_COLOR = 1
_MAX_POLYGONS_PER_PPD = 4096
_MAX_VERTICES_PER_POLYGON = 64
_MAX_SECTORS = 25
_MAX_ITEMS = 100_000
_MAX_CONTEXT_OBJECTS = 20_000


def _finite_xz(points, name, *, minimum=1):
    if not isinstance(points, (tuple, list)) or len(points) < minimum:
        raise ValueError(f'{name} must contain at least {minimum} XZ points')
    result = []
    for point in points:
        if (not isinstance(point, (tuple, list)) or len(point) != 2
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       or not math.isfinite(value) for value in point)):
            raise ValueError(f'{name} contains an invalid XZ coordinate')
        result.append((float(point[0]), float(point[1])))
    return result


def _regions(candidate):
    if not isinstance(candidate, dict):
        raise ValueError('Candidate must be an object')
    footprint = _finite_xz(candidate.get('polygon_xz'), 'polygon_xz', minimum=3)
    _validate_polygon(footprint)
    regions = {'footprint': footprint}
    approach = candidate.get('approach_xz')
    if approach is not None:
        approach = _finite_xz(approach, 'approach_xz', minimum=3)
        _validate_polygon(approach)
        regions['approach'] = approach
    return regions


def _local_polygons(data):
    """Decode supported v25 UI polygons without requiring a GAS spawn."""
    info = inspect_ppd(data)
    if info['version'] != 25:
        raise ValueError('unsupported_ppd_version')
    header = struct.unpack_from('<24I', data)
    count, start, end = header[8], header[20], header[21]
    if count > 4096 or start + 48 * count != end or end > len(data):
        raise ValueError('invalid_ppd_map_point_extent')
    points = []
    for index in range(count):
        values = struct.unpack_from('<II3f6iI', data, start + 48 * index)
        flags, _, x, y, z = values[:5]
        degree = values[-1]
        neighbors = list(values[5:5 + degree])
        if (degree > 6 or not all(math.isfinite(v) for v in (x, y, z))
                or len(set(neighbors)) != degree
                or any(n < 0 or n >= count or n == index for n in neighbors)):
            raise ValueError('invalid_ppd_map_point')
        points.append({'index': index, 'color': (flags >> 17) & 7,
                       'road_size': (flags >> 8) & 15,
                       'position': (x, y, z), 'neighbors': neighbors})
    for point in points:
        if any(point['index'] not in points[n]['neighbors'] for n in point['neighbors']):
            raise ValueError('nonreciprocal_ppd_map_point_neighbors')
    polygons, visited = [], set()
    for point in points:
        if point['road_size'] != 13 or point['index'] in visited:
            continue
        order, previous, current = [], None, point['index']
        while current not in order:
            row = points[current]
            if row['road_size'] != 13 or row['color'] != point['color'] or len(row['neighbors']) != 2:
                raise ValueError('unsupported_ppd_polygon_topology')
            if current in visited:
                raise ValueError('overlapping_ppd_polygon_components')
            order.append(current)
            if len(order) > _MAX_VERTICES_PER_POLYGON:
                raise ValueError('ppd_polygon_vertex_budget_exceeded')
            choices = [n for n in row['neighbors'] if n != previous]
            if not choices or (previous is not None and len(choices) != 1):
                raise ValueError('unsupported_ppd_polygon_branch')
            previous, current = current, min(choices)
        if current != order[0]:
            raise ValueError('open_ppd_polygon')
        visited.update(order)
        polygon = [points[i]['position'] for i in order]
        _validate_polygon(_xz(polygon))
        polygons.append({'id': min(order), 'color': point['color'], 'vertices': polygon})
        if len(polygons) > _MAX_POLYGONS_PER_PPD:
            raise ValueError('ppd_polygon_budget_exceeded')
    return polygons


def _anchor_xz(prefab, nodes):
    refs = prefab.details['nodes']
    if any(uid not in nodes for uid in refs):
        return None
    return nodes[refs[0]].position[0], nodes[refs[0]].position[2]


def _node_record(path, node):
    return {'path': path, 'raw_sha256': hashlib.sha256(node.raw).hexdigest(),
            'position_xyz': list(node.position), 'rotation_xyzw': list(node.rotation),
            'backward_uid': f'{node.backward:#x}', 'forward_uid': f'{node.forward:#x}',
            'flags': node.flags}


def _node_metadata_report(records):
    rows = []
    for uid, copies in sorted(records.items()):
        if len({copy['raw_sha256'] for copy in copies}) < 2:
            continue
        poses = {(tuple(copy['position_xyz']), tuple(copy['rotation_xyzw'])) for copy in copies}
        fields = []
        for key in ('position_xyz', 'rotation_xyzw', 'backward_uid', 'forward_uid', 'flags'):
            if len({tuple(copy[key]) if isinstance(copy[key], list) else copy[key]
                    for copy in copies}) > 1:
                fields.append(key)
        rows.append({'uid': f'{uid:#x}', 'geometry_equal': len(poses) == 1,
                     'differing_fields': fields, 'copies': sorted(copies, key=lambda copy: copy['path'])})
    return rows


def load_local_context(stack, sector_data_by_path, selected_uid, station_anchor_xz,
                       *, search_radius=100.0, max_sectors=_MAX_SECTORS, definitions=None):
    """Build bounded neighboring prefab proxies from already selected sectors.

    ``sector_data_by_path`` is an explicit bounded mapping of virtual sector
    paths to bytes, normally the target sector and supplied neighboring sectors.
    The caller chooses coverage; this function never discovers/indexes every
    map sector. Nearby external PPD UI polygons with color other than 1 become
    conservative coarse solid proxies.
    """
    if isinstance(search_radius, bool) or not isinstance(search_radius, (int, float)) or not math.isfinite(search_radius) or search_radius <= 0:
        raise ValueError('search_radius must be positive and finite')
    if type(max_sectors) is not int or not 1 <= max_sectors <= _MAX_SECTORS:
        raise ValueError('max_sectors must be between 1 and 25')
    anchor = _finite_xz([station_anchor_xz], 'station_anchor_xz')[0]
    if not isinstance(sector_data_by_path, dict) or len(sector_data_by_path) > max_sectors:
        raise ValueError('Supply a bounded mapping of no more than max_sectors')
    sector_rows, source_resources = [], {}
    node_map, sector_nodes, node_records, item_rows = {}, {}, {}, []
    for path, data in sorted(sector_data_by_path.items()):
        if (not isinstance(path, str) or virtual_path(path) != path
                or not path.endswith(('.base', '.aux'))):
            raise ValueError('Context sector paths must be canonical base/aux-sector paths')
        if not isinstance(data, bytes):
            raise ValueError('Context sector payloads must be bytes')
        parsed = parse_sector(data)
        sector_owner = stack.resources.get(path, (None, None))[1]
        source_resources[path] = {'path': path, 'sha256': hashlib.sha256(data).hexdigest(),
                                  'provider': getattr(sector_owner, 'package', None)}
        sector_rows.append({'path': path, 'sha256': hashlib.sha256(data).hexdigest(),
                            'item_count': len(parsed.items)})
        own_nodes = {node.uid: node for node in parsed.nodes}
        sector_nodes[path] = own_nodes
        for node in parsed.nodes:
            node_map.setdefault(node.uid, []).append(node)
            node_records.setdefault(node.uid, []).append(_node_record(path, node))
        item_rows.extend((path, item) for item in parsed.items)
    if len(item_rows) > _MAX_ITEMS:
        raise ValueError('Context item budget exceeded')
    definitions = prefab_definitions(stack) if definitions is None else definitions
    objects, unassessed, unknown_kind_counts = [], [], Counter()
    descriptor_inputs = {}
    nearby_rows = []

    def nodes_for_item(path, item):
        """Prefer placement-local nodes; fallback only to a unique owner-linked pose."""
        refs = item.details['nodes']
        local = sector_nodes[path]
        resolved = {}
        for uid in refs:
            node = local.get(uid)
            if node is not None:
                if node.forward != item.uid and node.backward != item.uid:
                    return None, f'placement_node_unlinked:{uid:#x}'
                resolved[uid] = node
                continue
            linked = [candidate for candidate in node_map.get(uid, ())
                      if candidate.forward == item.uid or candidate.backward == item.uid]
            if not linked:
                return None, f'placement_node_missing_or_unlinked:{uid:#x}'
            poses = {(candidate.position, candidate.rotation) for candidate in linked}
            if len(poses) != 1:
                return None, f'ambiguous_fallback_node_pose:{uid:#x}'
            resolved[uid] = linked[0]
        return resolved, None

    for path, item in item_rows:
        if item.kind != 4:
            unknown_kind_counts[f'{item.kind:#x}'] += 1
            continue
        if item.uid == selected_uid:
            continue
        placement_nodes, node_error = nodes_for_item(path, item)
        if placement_nodes is None:
            unassessed.append({'id': f'{path}#{item.uid:016x}', 'kind': item.kind,
                               'reason': node_error})
            continue
        anchor_other = _anchor_xz(item, placement_nodes)
        if anchor_other is None:
            unassessed.append({'id': f'{path}#{item.uid:016x}', 'kind': item.kind,
                               'reason': 'placement_nodes_outside_supplied_sector_scope'})
            continue
        distance = math.dist(anchor, anchor_other)
        if distance > search_radius:
            continue
        definition = definitions.get(item.details['model'])
        identity = f'{path}#{item.uid:016x}'
        if definition is None:
            unassessed.append({'id': identity, 'kind': item.kind, 'anchor_xz': list(anchor_other),
                               'reason': 'effective_prefab_definition_unresolved'})
            continue
        unit = definition[0]
        descriptor = (unit.one('prefab_desc', '') or '').lstrip('/')
        if not descriptor or descriptor not in stack.resources:
            unassessed.append({'id': identity, 'kind': item.kind, 'anchor_xz': list(anchor_other),
                               'reason': 'effective_prefab_descriptor_unresolved'})
            continue
        nearby_rows.append({'path': path, 'item': item, 'nodes': placement_nodes,
                            'anchor_xz': anchor_other, 'identity': identity,
                            'definition': definition, 'descriptor': descriptor})

    # Batch only the descriptors belonging to nearby, resolved prefabs. HashFS
    # extraction starts an external process, so individual reads in the loop
    # below would be prohibitively slow for repeated road-prefab PPDs.
    prefetch_by_package = {}
    for row in nearby_rows:
        package = stack.resources[row['descriptor']][0]
        prefetch_by_package.setdefault(package, set()).add(row['descriptor'])
    prefetch_reports, prefetch_failures = [], {}
    for package, paths in sorted(prefetch_by_package.items(), key=lambda row: str(row[0].path)):
        try:
            if package.archive is None or not package.archive.format.startswith('hashfs'):
                package.prefetch(sorted(paths), max_bytes=32 * 1024 * 1024)
            else:
                cache_root = getattr(package, '_disk_cache_root', None)
                if cache_root is None:
                    cache_id = hashlib.sha256(str(package.path).encode()).hexdigest()[:12]
                    cache_root = Archive._scratch_root().parent / 'package-cache' / cache_id
                package.prefetch(sorted(paths), disk_cache=cache_root,
                                 max_bytes=32 * 1024 * 1024)
            prefetch_reports.append({'provider': str(package.path), 'descriptor_count': len(paths),
                                     'descriptors': sorted(paths)})
        except (OSError, ValueError) as exc:
            message = str(exc) or type(exc).__name__
            for descriptor in paths:
                prefetch_failures[descriptor] = message

    usable_rows = []
    for row in nearby_rows:
        failure = prefetch_failures.get(row['descriptor'])
        if failure:
            unassessed.append({'id': row['identity'], 'kind': row['item'].kind,
                               'anchor_xz': list(row['anchor_xz']), 'descriptor': row['descriptor'],
                               'reason': 'descriptor_prefetch_failed', 'detail': failure})
        else:
            usable_rows.append(row)

    for row in usable_rows:
        path, item, placement_nodes = row['path'], row['item'], row['nodes']
        anchor_other, identity = row['anchor_xz'], row['identity']
        definition, descriptor = row['definition'], row['descriptor']
        try:
            ppd = stack.read(descriptor, max_bytes=32 * 1024 * 1024)
            owner = stack.resources[descriptor][1]
            descriptor_inputs[descriptor] = {
                'sha256': hashlib.sha256(ppd).hexdigest(),
                'provider': getattr(owner, 'package', None),
            }
            source_resources[descriptor] = {'path': descriptor,
                'sha256': descriptor_inputs[descriptor]['sha256'],
                'provider': descriptor_inputs[descriptor]['provider']}
            definition_path = definition[2]
            definition_data = stack.read(definition_path, max_bytes=8 * 1024 * 1024)
            definition_owner = stack.resources[definition_path][1]
            source_resources[definition_path] = {'path': definition_path,
                'sha256': hashlib.sha256(definition_data).hexdigest(),
                'provider': getattr(definition_owner, 'package', None)}
            polygons = _local_polygons(ppd)
            translated, unsupported_colors = [], []
            for polygon in polygons:
                if polygon['color'] == _ACCESSIBLE_COLOR:
                    continue
                if polygon['color'] not in (2, 4):
                    unsupported_colors.append(polygon['color'])
                    continue
                world = _placed_vertices(ppd, item, placement_nodes, polygon['vertices'])
                translated.append({'polygon_id': polygon['id'], 'color': polygon['color'],
                                   'geometry_xz': [list(point) for point in world]})
            objects.extend({'id': identity + f':ui-polygon-{poly["polygon_id"]}',
                            'kind': item.kind, 'source_sector': path,
                            'descriptor': descriptor, 'classification': 'obstacle_proxy',
                            'extent_status': 'declared_conservative_proxy',
                            'geometry_xz': poly['geometry_xz'], 'color': poly['color']}
                           for poly in translated)
            if unsupported_colors:
                unassessed.append({'id': identity, 'kind': item.kind, 'anchor_xz': list(anchor_other),
                                   'descriptor': descriptor,
                                   'reason': 'unsupported_ppd_ui_polygon_colors',
                                   'colors': sorted(set(unsupported_colors))})
            if not translated and not unsupported_colors:
                unassessed.append({'id': identity, 'kind': item.kind, 'anchor_xz': list(anchor_other),
                                   'descriptor': descriptor,
                                   'reason': 'no_nonaccessible_ui_polygon_proxy'})
        except (ValueError, KeyError, struct.error) as exc:
            unassessed.append({'id': identity, 'kind': item.kind, 'anchor_xz': list(anchor_other),
                               'descriptor': descriptor, 'reason': str(exc) or 'unsupported_external_geometry'})
    if len(objects) + len(unassessed) > _MAX_CONTEXT_OBJECTS:
        raise ValueError('Context object budget exceeded')
    return {'objects': sorted(objects, key=lambda row: (row['id'], row['kind'])),
            'unassessed_objects': sorted(unassessed, key=lambda row: (row['id'], row['reason'])),
            'unassessed_map_item_kind_counts': dict(sorted(unknown_kind_counts.items())),
            'generic_extent_unassessed_kind_counts': dict(sorted(unknown_kind_counts.items())),
            'sector_inputs': sector_rows, 'descriptor_inputs': dict(sorted(descriptor_inputs.items())),
            'duplicate_node_metadata': _node_metadata_report(node_records),
            'descriptor_prefetch': prefetch_reports,
            'source_resources': [source_resources[path] for path in sorted(source_resources)],
            'search_radius': float(search_radius),
            'limits': ['Search is bounded to explicitly supplied sectors and prefab anchor distance; large external prefab extent is not bounded.',
                       'PPD non-accessible UI polygons are coarse obstacle proxies, not collision geometry; accessible polygons, PPD omissions, props, terrain, road furniture, parked NPCs and physics are not resolved.',
                       'Generic map-item bounds have unknown semantics and are not used.',
                       'No whole-world absence or collision-complete claim.']}


def evaluate_local_context(candidate_world, context, *, margin=0.5):
    """Reject candidate footprint or approach near recognized obstacle proxies.

    Inputs are copied/normalized into this report; caller rows and candidate
    values are never mutated. Unknown rows remain visible but do not silently
    become obstacles or clearances.
    """
    if isinstance(margin, bool) or not isinstance(margin, (int, float)) or not math.isfinite(margin) or margin < 0:
        raise ValueError('margin must be finite and nonnegative')
    regions = _regions(candidate_world)
    if not isinstance(context, dict) or not isinstance(context.get('objects'), list):
        raise ValueError('Context requires an objects list')
    if len(context['objects']) > _MAX_CONTEXT_OBJECTS:
        raise ValueError('Context object budget exceeded')
    hits, unassessed, obstacle_count, distances_to_obstacles = [], [], 0, []
    for row in context['objects']:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
            raise ValueError('Every context object requires a stable nonempty id')
        classification = row.get('classification', 'unknown')
        if classification != 'obstacle_proxy':
            unassessed.append({'id': row['id'], 'reason': 'unrecognized_or_non_obstacle_classification'})
            continue
        if row.get('extent_status') not in ('observed_geometry', 'declared_conservative_proxy'):
            unassessed.append({'id': row['id'], 'reason': 'obstacle_extent_unknown'})
            continue
        geometry = _finite_xz(row.get('geometry_xz'), f"{row['id']}.geometry_xz")
        if len(geometry) >= 3:
            try:
                _validate_polygon(geometry)
            except ValueError as exc:
                raise ValueError(f'{row["id"]}: invalid obstacle polygon') from exc
        obstacle_count += 1
        distances = {name: polygon_distance(region, geometry) for name, region in regions.items()}
        distances_to_obstacles.extend(distances.values())
        conflicts = [name for name, distance in distances.items() if distance <= margin]
        if conflicts:
            hits.append({'id': row['id'], 'kind': row.get('kind'), 'regions': conflicts,
                         'minimum_distance': min(distances.values()),
                         'extent_status': row['extent_status']})
    hits.sort(key=lambda row: (row['id'], tuple(row['regions'])))
    unassessed.extend(context.get('unassessed_objects', []))
    unassessed.sort(key=lambda row: (str(row.get('id', '')), str(row.get('reason', ''))))
    reasons = ['intersects_external_map_object_proxy'] if hits else []
    return {'rejection_reasons': reasons, 'external_object_conflicts': hits,
            'external_objects_checked': obstacle_count,
            'minimum_clearance_margin_m': (min(distances_to_obstacles) - margin
                                           if distances_to_obstacles else None),
            'external_objects_unassessed': unassessed,
            'unknown_item_kind_counts': dict(
                context.get('unassessed_map_item_kind_counts',
                            context.get('unknown_item_kind_counts', {}))),
            'unassessed_map_item_kind_counts': dict(
                context.get('unassessed_map_item_kind_counts',
                            context.get('unknown_item_kind_counts', {}))),
            'generic_extent_unassessed_kind_counts': dict(
                context.get('generic_extent_unassessed_kind_counts', {})),
            'local_context_limits': list(context.get('limits', [])),
            'local_context_margin_m': float(margin)}
