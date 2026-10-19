"""Find repeated, vehicle-width parking separators in explicit PIM paint meshes.

This is a geometry proposal only. It does not inspect prefab names, PPD triggers,
map placement, collision, or gameplay. Downstream callers must validate access
and obstacles independently before treating any returned bay as usable.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
import hashlib
import json
import math
from collections import defaultdict


class PaintedParkingError(ValueError):
    """Malformed mesh input or unsupported geometry for painted-bay analysis."""


@dataclass(frozen=True)
class PaintedParkingParameters:
    """Generic geometry thresholds; these are not station-specific coordinates."""

    weld_tolerance: float = 0.001
    max_vertical_span: float = 0.15
    min_strip_length: float = 4.0
    max_strip_length: float = 8.0
    min_strip_width: float = 0.05
    max_strip_width: float = 0.40
    min_aspect_ratio: float = 15.0
    min_spacing: float = 2.0
    max_spacing: float = 4.0
    min_bay_width: float = 2.0
    max_bay_width: float = 4.0
    max_parallel_angle_degrees: float = 4.0
    min_longitudinal_overlap: float = 0.80
    max_strip_length_difference: float = 0.50
    max_spacing_variance: float = 0.25
    min_separators: int = 3
    max_separators: int = 32
    max_selected_triangles: int = 200_000

    def __post_init__(self):
        positive = ('weld_tolerance', 'max_vertical_span', 'min_strip_length',
                    'max_strip_length', 'min_strip_width', 'max_strip_width',
                    'min_aspect_ratio', 'min_spacing', 'max_spacing',
                    'min_bay_width', 'max_bay_width',
                    'max_parallel_angle_degrees', 'max_strip_length_difference',
                    'max_spacing_variance')
        for name in positive:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be a finite positive number')
        if self.max_strip_length <= self.min_strip_length:
            raise ValueError('max_strip_length must exceed min_strip_length')
        if self.max_strip_width <= self.min_strip_width:
            raise ValueError('max_strip_width must exceed min_strip_width')
        if self.max_spacing <= self.min_spacing:
            raise ValueError('max_spacing must exceed min_spacing')
        if self.max_bay_width <= self.min_bay_width:
            raise ValueError('max_bay_width must exceed min_bay_width')
        if self.max_parallel_angle_degrees > 15:
            raise ValueError('max_parallel_angle_degrees cannot exceed 15 degrees')
        if (isinstance(self.min_longitudinal_overlap, bool)
                or not isinstance(self.min_longitudinal_overlap, (int, float))
                or not math.isfinite(self.min_longitudinal_overlap)
                or not 0 < self.min_longitudinal_overlap <= 1):
            raise ValueError('min_longitudinal_overlap must be in (0, 1]')
        if (isinstance(self.min_separators, bool) or not isinstance(self.min_separators, int)
                or self.min_separators < 3 or self.min_separators > 32):
            raise ValueError('min_separators must be an integer from 3 to 32')
        if (isinstance(self.max_separators, bool) or not isinstance(self.max_separators, int)
                or self.max_separators < self.min_separators or self.max_separators > 128):
            raise ValueError('max_separators must be between min_separators and 128')
        if (isinstance(self.max_selected_triangles, bool)
                or not isinstance(self.max_selected_triangles, int)
                or self.max_selected_triangles < 2 or self.max_selected_triangles > 1_000_000):
            raise ValueError('max_selected_triangles must be an integer from 2 to 1000000')


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _convex_hull(points):
    unique = sorted(set((float(p[0]), float(p[1])) for p in points))
    if len(unique) < 3:
        return unique
    lower = []
    for p in unique:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 1e-12:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(unique):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 1e-12:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _canonical_direction(dx, dz):
    length = math.hypot(dx, dz)
    if length <= 1e-12:
        return None
    dx, dz = dx / length, dz / length
    if dx < -1e-12 or (abs(dx) <= 1e-12 and dz < 0):
        dx, dz = -dx, -dz
    return dx, dz


def _minimum_rectangle(points):
    """Return the deterministic minimum-area rectangle around an XZ point set."""
    hull = _convex_hull(points)
    if len(hull) < 3:
        return None
    candidates = []
    for a, b in zip(hull, hull[1:] + hull[:1]):
        direction = _canonical_direction(b[0] - a[0], b[1] - a[1])
        if direction is None:
            continue
        dx, dz = direction
        nx, nz = -dz, dx
        along = [p[0] * dx + p[1] * dz for p in hull]
        across = [p[0] * nx + p[1] * nz for p in hull]
        s0, s1, t0, t1 = min(along), max(along), min(across), max(across)
        length, width = s1 - s0, t1 - t0
        if width > length:
            dx, dz = nx, nz
            if dx < -1e-12 or (abs(dx) <= 1e-12 and dz < 0):
                dx, dz = -dx, -dz
            nx, nz = -dz, dx
            along = [p[0] * dx + p[1] * dz for p in hull]
            across = [p[0] * nx + p[1] * nz for p in hull]
            s0, s1, t0, t1 = min(along), max(along), min(across), max(across)
            length, width = s1 - s0, t1 - t0
        area = length * width
        angle = math.atan2(dz, dx)
        candidates.append((area, round(angle, 12), dx, dz, s0, s1, t0, t1, length, width))
    if not candidates:
        return None
    _, _, dx, dz, s0, s1, t0, t1, length, width = min(candidates)
    return {'direction': (dx, dz), 'normal': (-dz, dx), 's_min': s0,
            's_max': s1, 't_min': t0, 't_max': t1,
            'length': length, 'width': width, 'hull': hull}


class _UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item):
        parent = self.parent
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


def _weld_positions(positions, tolerance):
    """Weld coincident XYZ positions within tolerance using a spatial hash."""
    buckets = defaultdict(list)
    welded = []
    offsets = [(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]
    for point in positions:
        cell = tuple(math.floor(value / tolerance) for value in point)
        match = None
        for dx, dy, dz in offsets:
            for index in buckets[(cell[0] + dx, cell[1] + dy, cell[2] + dz)]:
                other = welded[index]
                if math.dist(point, other) <= tolerance:
                    match = index
                    break
            if match is not None:
                break
        if match is None:
            match = len(welded)
            welded.append(point)
            buckets[cell].append(match)
        yield match


def _components(piece, parameters):
    positions = piece['positions']
    triangles = piece['triangles']
    if len(positions) > 1_000_000 or len(triangles) > parameters.max_selected_triangles:
        raise PaintedParkingError('Selected paint mesh exceeds bounded geometry limits')
    welded_ids = list(_weld_positions(positions, parameters.weld_tolerance))
    face_union = _UnionFind(len(triangles))
    edges = {}
    valid = []
    degenerate = []
    for tri_index, tri in enumerate(triangles):
        if (not isinstance(tri, (tuple, list)) or len(tri) != 3
                or any(isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= len(positions)
                       for i in tri)):
            raise PaintedParkingError('Selected paint mesh has an invalid triangle index')
        ids = tuple(welded_ids[i] for i in tri)
        if len(set(ids)) < 3:
            degenerate.append(tri_index)
            continue
        a, b, c = (positions[i] for i in tri)
        area2 = abs(_cross((a[0], a[2]), (b[0], b[2]), (c[0], c[2])))
        if area2 <= 1e-10:
            degenerate.append(tri_index)
            continue
        valid.append(tri_index)
        for a_id, b_id in ((ids[0], ids[1]), (ids[1], ids[2]), (ids[2], ids[0])):
            edge = (min(a_id, b_id), max(a_id, b_id))
            if edge in edges:
                face_union.union(tri_index, edges[edge])
            else:
                edges[edge] = tri_index
    grouped = defaultdict(list)
    for index in valid:
        grouped[face_union.find(index)].append(index)
    return [sorted(indices) for _, indices in sorted(grouped.items(), key=lambda item: min(item[1]))], degenerate


def _strip_record(piece, triangles, parameters):
    positions = piece['positions']
    points = [positions[i] for tri_index in triangles for i in piece['triangles'][tri_index]]
    y_values = [point[1] for point in points]
    rect = _minimum_rectangle([(point[0], point[2]) for point in points])
    if rect is None:
        return None, 'degenerate_component'
    length, width = rect['length'], rect['width']
    if max(y_values) - min(y_values) > parameters.max_vertical_span:
        return None, 'paint_component_not_nearly_flat'
    if not parameters.min_strip_length <= length <= parameters.max_strip_length:
        return None, 'paint_component_length_outside_vehicle_bay_separator_range'
    if not parameters.min_strip_width <= width <= parameters.max_strip_width:
        return None, 'paint_component_width_outside_separator_range'
    if length / width < parameters.min_aspect_ratio:
        return None, 'paint_component_aspect_ratio_too_low'
    dx, dz = rect['direction']
    nx, nz = rect['normal']
    center_x = sum(p[0] for p in points) / len(points)
    center_z = sum(p[2] for p in points) / len(points)
    center_s = center_x * dx + center_z * dz
    center_t = center_x * nx + center_z * nz
    center_y = sum(p[1] for p in points) / len(points)
    return {
        'piece_index': piece['index'], 'material': piece['material'],
        'triangle_indices': triangles, 'vertex_count': len(set(i for t in triangles for i in piece['triangles'][t])),
        'direction_xz': [dx, dz], 'center_xz': [center_x, center_z],
        'center_y_m': center_y, 'center_s': center_s, 'center_t': center_t,
        's_min': rect['s_min'], 's_max': rect['s_max'],
        't_min': rect['t_min'], 't_max': rect['t_max'],
        'length_m': length, 'width_m': width,
        'vertical_span_m': max(y_values) - min(y_values),
        'polygon_xz': _rect_polygon(dx, dz, rect['s_min'], rect['s_max'], rect['t_min'], rect['t_max']),
    }, None


def _rect_polygon(dx, dz, s_min, s_max, t_min, t_max):
    nx, nz = -dz, dx
    return [[dx * s + nx * t, dz * s + nz * t]
            for s, t in ((s_min, t_min), (s_max, t_min), (s_max, t_max), (s_min, t_max))]


def _compatible(a, b, parameters):
    if abs(a['center_y_m'] - b['center_y_m']) > parameters.max_vertical_span:
        return False
    if abs(a['length_m'] - b['length_m']) > parameters.max_strip_length_difference:
        return False
    d1, d2 = a['direction_xz'], b['direction_xz']
    dot = max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1]))
    angle = math.degrees(math.acos(abs(dot)))
    if angle > parameters.max_parallel_angle_degrees:
        return False
    dx, dz = d1
    nx, nz = -dz, dx
    a_points, b_points = a['_points_xz'], b['_points_xz']
    a_s = [p[0] * dx + p[1] * dz for p in a_points]
    b_s = [p[0] * dx + p[1] * dz for p in b_points]
    overlap = max(0.0, min(max(a_s), max(b_s)) - max(min(a_s), min(b_s)))
    shorter = min(max(a_s) - min(a_s), max(b_s) - min(b_s))
    if shorter <= 0 or overlap / shorter < parameters.min_longitudinal_overlap:
        return False
    a_t = sum(p[0] * nx + p[1] * nz for p in a_points) / len(a_points)
    b_t = sum(p[0] * nx + p[1] * nz for p in b_points) / len(b_points)
    spacing = abs(a_t - b_t)
    return parameters.min_spacing <= spacing <= parameters.max_spacing


def _bank_candidate(strips, strip_points, parameters):
    # Direction from sorted immutable evidence, then averaged with sign-aligned axes.
    first = strips[0]['direction_xz']
    dx = sum((1 if s['direction_xz'][0] * first[0] + s['direction_xz'][1] * first[1] >= 0 else -1)
             * s['direction_xz'][0] for s in strips)
    dz = sum((1 if s['direction_xz'][0] * first[0] + s['direction_xz'][1] * first[1] >= 0 else -1)
             * s['direction_xz'][1] for s in strips)
    direction = _canonical_direction(dx, dz)
    dx, dz = direction
    nx, nz = -dz, dx
    ordered = []
    for strip in strips:
        points = strip_points[(strip['piece_index'], tuple(strip['triangle_indices']))]
        svals = [p[0] * dx + p[1] * dz for p in points]
        tvals = [p[0] * nx + p[1] * nz for p in points]
        ordered.append((sum(tvals) / len(tvals), min(tvals), max(tvals), min(svals), max(svals), strip))
    ordered.sort(key=lambda row: (row[0], row[5]['piece_index'], row[5]['triangle_indices']))
    separators = [row[5] for row in ordered]
    bank_rejections = []
    center_spacings = [ordered[i + 1][0] - ordered[i][0] for i in range(len(ordered) - 1)]
    if any(not parameters.min_spacing <= spacing <= parameters.max_spacing
           for spacing in center_spacings):
        bank_rejections.append('adjacent_separator_center_spacing_outside_vehicle_width_range')
    if any((right[1] - left[2]) < parameters.min_bay_width
           or (right[1] - left[2]) > parameters.max_bay_width
           for left, right in zip(ordered, ordered[1:])):
        bank_rejections.append('free_bay_width_outside_vehicle_width_range')
    heights = [strip['center_y_m'] for strip in separators]
    if max(heights) - min(heights) > parameters.max_vertical_span:
        bank_rejections.append('separator_bank_height_span_exceeds_tolerance')
    lengths = [strip['length_m'] for strip in separators]
    if max(lengths) - min(lengths) > parameters.max_strip_length_difference:
        bank_rejections.append('separator_bank_length_variation_exceeds_tolerance')
    first_direction = separators[0]['direction_xz']
    if any(math.degrees(math.acos(max(-1.0, min(1.0, abs(
            strip['direction_xz'][0] * first_direction[0]
            + strip['direction_xz'][1] * first_direction[1])))))
           > parameters.max_parallel_angle_degrees for strip in separators):
        bank_rejections.append('separator_bank_angle_span_exceeds_tolerance')
    common_s_min = max(row[3] for row in ordered)
    common_s_max = min(row[4] for row in ordered)
    shortest_length = min(row[4] - row[3] for row in ordered)
    if shortest_length <= 0 or (common_s_max - common_s_min) / shortest_length < parameters.min_longitudinal_overlap:
        bank_rejections.append('separator_bank_has_insufficient_common_longitudinal_overlap')
    bays = []
    rejected_gaps = []
    for left, right in zip(ordered, ordered[1:]):
        gap = right[1] - left[2]
        s_min, s_max = max(left[3], right[3]), min(left[4], right[4])
        if gap <= 0 or s_max <= s_min:
            rejected_gaps.append({'reason': 'separator_footprints_overlap_or_have_no_common_length',
                                  'triangle_refs': [left[5]['triangle_indices'], right[5]['triangle_indices']]})
            continue
        polygon = _rect_polygon(dx, dz, s_min, s_max, left[2], right[1])
        bays.append({'polygon_xz': polygon, 'width_m': gap, 'length_m': s_max - s_min,
                     'separator_triangle_refs': [left[5]['triangle_indices'], right[5]['triangle_indices']]})
    all_points = [p for strip in separators
                  for p in strip_points[(strip['piece_index'], tuple(strip['triangle_indices']))]]
    svals = [p[0] * dx + p[1] * dz for p in all_points]
    tvals = [p[0] * nx + p[1] * nz for p in all_points]
    bank_polygon = _rect_polygon(dx, dz, min(svals), max(svals), min(tvals), max(tvals))
    evidence = {'strips': [strip['polygon_xz'] for strip in separators],
                'triangles': [[strip['piece_index'], *strip['triangle_indices']] for strip in separators]}
    candidate_id = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:16]
    spacings = center_spacings
    spacing_regular = bool(spacings) and max(spacings) - min(spacings) <= parameters.max_spacing_variance
    return {
        'id': candidate_id, 'polygon_xz': bank_polygon,
        'direction_xz': [dx, dz], 'separator_count': len(separators),
        'bay_count': len(bays), 'center_spacing_m': spacings,
        'spacing_regular': spacing_regular,
        'bank_rejection_reasons': bank_rejections,
        'strips': separators, 'bay_polygons_xz': bays,
        'rejected_gaps': rejected_gaps,
        'evidence': 'Hypothesis — repeated flat mesh strips form parking-bay separators; validate access, obstacles, collision, and runtime independently',
        'validation_status': 'geometry_only_pending_station_validators',
    }


def _include_single_bays(candidates):
    """Retain accepted whole banks and derive only their already measured bays."""
    maximum = 128
    if len(candidates) > maximum:
        raise PaintedParkingError('Painted bank/subbank proposals exceed the 128-candidate bound')
    expanded = list(candidates)
    # Identical geometry already offered by another accepted bank or bay needs
    # no second downstream evaluation. Parent banks themselves remain intact.
    geometry_seen = {tuple(sorted(map(tuple, candidate['polygon_xz']))) for candidate in candidates}
    for bank in candidates:
        for index, bay in enumerate(bank['bay_polygons_xz']):
            key = tuple(sorted(map(tuple, bay['polygon_xz'])))
            if key in geometry_seen:
                continue
            if len(expanded) >= maximum:
                raise PaintedParkingError('Painted bank/subbank proposals exceed the 128-candidate bound')
            geometry_seen.add(key)
            candidate = deepcopy(bank)
            evidence = {'parent_bank_id': bank['id'], 'source_bay_index': index, 'bay': bay}
            candidate.update({
                'id': hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:16],
                'polygon_xz': deepcopy(bay['polygon_xz']), 'bay_count': 1,
                'bay_polygons_xz': [deepcopy(bay)],
                'geometry_scope': 'single_bay_from_accepted_separator_bank',
                'parent_bank_id': bank['id'], 'parent_bay_count': bank['bay_count'],
                'parent_bank_separator_count': bank['separator_count'],
                'source_bay_index': index, 'source_separator_indices': [index, index + 1],
                'source_boundary_separator_count': 2,
                # separator_count, strips and center_spacing_m retain the full
                # accepted parent-bank corroboration. Two isolated strips still
                # cannot produce a proposal under the >=3-separator rule.
                'separator_evidence_scope': 'accepted_parent_bank',
                'source_separator_refs': [
                    {'piece_index': strip['piece_index'], 'triangle_indices': deepcopy(strip['triangle_indices'])}
                    for strip in bank['strips'][index:index + 2]],
            })
            expanded.append(candidate)
    return expanded


def propose_painted_parking(mesh: dict, *, paint_materials, parameters: PaintedParkingParameters | None = None,
                            include_subbanks: bool = False) -> dict:
    """Find banks of repeated parallel separator strips in explicit paint materials.

    `mesh` is the dictionary returned by :func:`station_mesh.read_station_mesh`.
    Material aliases must be supplied explicitly; names are used only to select
    source triangles, never to infer station identity or bay coordinates.
    With ``include_subbanks=True``, each already measured single bay inside an
    accepted bank is offered independently alongside its unchanged parent.
    The >=3-separator parent requirement remains intact; at most 128 total
    proposals are permitted, with excess rejected rather than truncated.

    The returned candidate polygons are hypotheses based solely on model mesh
    geometry. `selected` contains geometry banks satisfying the repeated-strip
    signature; it is not a gameplay or vehicle-clearance approval.
    """
    if type(include_subbanks) is not bool:
        raise PaintedParkingError('include_subbanks must be a boolean')
    parameters = PaintedParkingParameters() if parameters is None else parameters
    if not isinstance(parameters, PaintedParkingParameters):
        raise PaintedParkingError('parameters must be PaintedParkingParameters')
    if not isinstance(mesh, dict) or not isinstance(mesh.get('pieces'), list) or not isinstance(mesh.get('materials'), list):
        raise PaintedParkingError('Mesh must provide materials and pieces from the station mesh reader')
    if isinstance(paint_materials, (str, bytes)):
        raise PaintedParkingError('paint_materials must be a nonempty collection of explicit aliases')
    try:
        requested_aliases = list(paint_materials)
    except TypeError as exc:
        raise PaintedParkingError('paint_materials must be a nonempty collection of explicit aliases') from exc
    if not requested_aliases or any(not isinstance(alias, str) or not alias for alias in requested_aliases):
        raise PaintedParkingError('At least one explicit paint material alias is required')
    aliases = sorted(set(requested_aliases))
    available = {item.get('alias') for item in mesh['materials'] if isinstance(item, dict)}
    missing = sorted(set(aliases) - available)
    if missing:
        raise PaintedParkingError(f'Unknown explicit paint material alias(es): {", ".join(missing)}')
    pieces = [piece for piece in mesh['pieces']
              if isinstance(piece, dict) and piece.get('material') in aliases]
    if not pieces:
        return {'method': 'painted_parallel_separator_mesh', 'parameters': asdict(parameters),
                'paint_materials': aliases, 'candidates': [], 'selected': [],
                'blockers': ['No mesh pieces use the explicitly selected paint material aliases'],
                'rejections': []}
    piece_indices = set()
    for piece in pieces:
        if (isinstance(piece.get('index'), bool) or not isinstance(piece.get('index'), int)
                or piece['index'] < 0 or piece['index'] in piece_indices
                or not isinstance(piece.get('positions'), list)
                or not isinstance(piece.get('triangles'), list)):
            raise PaintedParkingError('Selected paint piece has an invalid mesh structure')
        piece_indices.add(piece['index'])
    triangle_total = sum(len(piece.get('triangles', [])) for piece in pieces)
    if triangle_total > parameters.max_selected_triangles:
        raise PaintedParkingError('Selected paint triangles exceed the configured bounded geometry budget')
    strips, rejections, strip_points = [], [], {}
    for piece in sorted(pieces, key=lambda p: p.get('index', -1)):
        positions = piece['positions']
        for point in positions:
            if (not isinstance(point, (list, tuple)) or len(point) != 3
                    or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
                           for v in point)):
                raise PaintedParkingError('Selected paint piece contains invalid or nonfinite positions')
            if any(abs(float(value)) > 1_000_000 for value in point):
                raise PaintedParkingError('Selected paint piece coordinate exceeds the bounded world range')
        components, degenerate = _components(piece, parameters)
        for tri_index in degenerate:
            rejections.append({'piece_index': piece['index'], 'triangle_indices': [tri_index],
                               'reason': 'degenerate_or_submillimeter_triangle'})
        for component in components:
            record, reason = _strip_record(piece, component, parameters)
            if record is None:
                rejections.append({'piece_index': piece['index'], 'triangle_indices': component,
                                   'reason': reason})
                continue
            record['_points_xz'] = [positions[i][0:3:2] for tri_index in component
                                    for i in piece['triangles'][tri_index]]
            strips.append(record)
            strip_points[(record['piece_index'], tuple(record['triangle_indices']))] = record['_points_xz']
    if len(strips) > 2_000:
        raise PaintedParkingError('Selected paint material produces too many strip components for bounded clustering')
    # Cluster strips that overlap along their long axis, share a level, and have
    # repeated vehicle-width perpendicular spacing.
    cluster_union = _UnionFind(len(strips))
    for i, left in enumerate(strips):
        for j in range(i + 1, len(strips)):
            if _compatible(left, strips[j], parameters):
                cluster_union.union(i, j)
    clusters = defaultdict(list)
    for index, strip in enumerate(strips):
        clusters[cluster_union.find(index)].append(strip)
    candidates = []
    for cluster in sorted(clusters.values(), key=lambda rows: min((s['piece_index'], s['triangle_indices']) for s in rows)):
        if len(cluster) < parameters.min_separators:
            for strip in cluster:
                rejections.append({'piece_index': strip['piece_index'], 'triangle_indices': strip['triangle_indices'],
                                   'reason': 'fewer_than_minimum_parallel_separators'})
            continue
        if len(cluster) > parameters.max_separators:
            rejections.append({'piece_index': min(s['piece_index'] for s in cluster),
                               'triangle_indices': sorted({i for s in cluster for i in s['triangle_indices']}),
                               'reason': 'parallel_separator_cluster_exceeds_maximum_size'})
            continue
        public_strips = [{key: value for key, value in strip.items() if not key.startswith('_')}
                         for strip in cluster]
        candidate = _bank_candidate(public_strips, strip_points, parameters)
        if candidate['bank_rejection_reasons']:
            rejections.append({'piece_index': min(s['piece_index'] for s in cluster),
                               'triangle_indices': sorted({i for s in cluster for i in s['triangle_indices']}),
                               'reason': 'separator_bank_fails_bank_wide_geometry_checks',
                               'details': candidate['bank_rejection_reasons']})
            continue
        if not candidate['spacing_regular']:
            rejections.append({'piece_index': min(s['piece_index'] for s in cluster),
                               'triangle_indices': sorted({i for s in cluster for i in s['triangle_indices']}),
                               'reason': 'parallel_separator_spacing_is_irregular'})
            continue
        if candidate['bay_count'] < parameters.min_separators - 1:
            rejections.append({'piece_index': min(s['piece_index'] for s in cluster),
                               'triangle_indices': sorted({i for s in cluster for i in s['triangle_indices']}),
                               'reason': 'separator_bank_does_not_form_enough_positive_width_bays'})
            continue
        candidates.append(candidate)
    if include_subbanks:
        candidates = _include_single_bays(candidates)
    candidates.sort(key=lambda c: (-c['bay_count'], -c['separator_count'], c['id']))
    selected = list(candidates)
    return {
        'method': 'painted_parallel_separator_mesh', 'parameters': asdict(parameters),
        'paint_materials': aliases, 'candidates': candidates, 'selected': selected,
        'blockers': [] if selected else ['No repeated bank of flat, parallel vehicle-width paint strips was found'],
        'rejections': rejections,
        'runtime_status': 'unverified; no game operation performed',
        'generation_readiness': 'Geometry proposal only; validate map access, other obstacles, vehicle clearance, and trigger semantics independently',
        **({'subbank_policy': {'single_bays_from_accepted_banks': True, 'maximum_total_candidates': 128,
                              'separator_count_scope': 'Accepted parent-bank corroboration; source_boundary_separator_count records each bay boundary'}}
           if include_subbanks else {}),
    }
