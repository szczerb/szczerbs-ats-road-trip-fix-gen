"""Replace one exactly reconstructed generated bay with two reviewed areas.

This is a bounded caller-pinned replacement, not a general PPD trigger remover.
The caller supplies the immutable baseline and the known previous polygon; the
current descriptor must equal that exact baseline with that polygon appended.
"""
from __future__ import annotations

import hashlib
import math
import struct

from ..rest_stops import polygon_distance
from .trigger import _validate_vertices, append_car_parking_polygon


def _reviewed_rectangle(vertices):
    points = _validate_vertices(vertices)
    if len(points) != 4:
        raise ValueError('Each reviewed area must be a four-corner straight rectangle')
    # Work in the actual serialized precision, so a nominally valid input that
    # collapses after float32 conversion cannot enter the descriptor.
    packed = [struct.unpack('<3f', struct.pack('<3f', *p)) for p in points]
    _validate_vertices(packed)
    horizontal = [(p[0], p[2]) for p in points]
    edges = [(b[0] - a[0], b[1] - a[1])
             for a, b in zip(horizontal, horizontal[1:] + horizontal[:1])]
    lengths = [math.hypot(*edge) for edge in edges]
    for index, edge in enumerate(edges):
        following = edges[(index + 1) % 4]
        if abs(edge[0] * following[0] + edge[1] * following[1]) > 1e-6 * lengths[index] * lengths[(index + 1) % 4]:
            raise ValueError('Reviewed area corners must form a straight rectangle in XZ')
        opposite = edges[(index + 2) % 4]
        if math.hypot(edge[0] + opposite[0], edge[1] + opposite[1]) > 1e-6 * lengths[index]:
            raise ValueError('Reviewed area opposite edges must form a straight rectangle in XZ')
    return points, [(p[0], p[2]) for p in packed]


def replace_reviewed_car_parking_areas(
    baseline: bytes, current: bytes, *, previous_vertices: list,
    areas: list[dict],
) -> tuple[bytes, dict]:
    """Replace exactly one known generated bay with two independent car areas.

    Each area requires a unique nonempty ``id``, four ordered ``vertices`` in
    station-local XYZ coordinates, and an explicit boolean
    ``partial_activation``. The rectangles must have separate XZ footprints.
    Partial activation sets native PPD bit 0x4 (contact enabled); actual runtime
    activation, vehicle shape and two visible map icons remain unverified.

    Source pinning to the reviewed package/path/hash belongs to the caller.
    This primitive independently refuses every byte difference between
    ``current`` and ``append_car_parking_polygon(baseline, previous_vertices)``.
    It rebuilds from ``baseline`` and never deletes an arbitrary source group.
    """
    if not isinstance(baseline, bytes) or not isinstance(current, bytes):
        raise ValueError('Baseline and current descriptors must be immutable bytes')
    if not isinstance(areas, list) or len(areas) != 2:
        raise ValueError('Reviewed replacement requires exactly two separate areas')
    validated, identifiers = [], set()
    for area in areas:
        if not isinstance(area, dict) or set(area) != {'id', 'vertices', 'partial_activation'}:
            raise ValueError('Each reviewed area requires only id, vertices and partial_activation')
        area_id = area['id']
        if not isinstance(area_id, str) or not area_id.strip() or area_id != area_id.strip():
            raise ValueError('Reviewed area ID must be a nonempty trimmed string')
        if area_id in identifiers:
            raise ValueError('Reviewed area IDs must be unique')
        identifiers.add(area_id)
        if type(area['partial_activation']) is not bool:
            raise ValueError('Each reviewed area requires an explicit boolean partial_activation')
        points, footprint = _reviewed_rectangle(area['vertices'])
        validated.append((area_id, points, footprint, area['partial_activation']))
    if polygon_distance(validated[0][2], validated[1][2]) <= 1e-6:
        raise ValueError('Reviewed area rectangles overlap or touch in XZ')

    expected_current, previous_report = append_car_parking_polygon(baseline, previous_vertices)
    if current != expected_current:
        raise ValueError('Current PPD differs from the baseline plus the exact known previous generated polygon; source or suffix drift is refused')

    result, reports = baseline, []
    for area_id, points, _, partial in validated:
        result, writer = append_car_parking_polygon(result, points, partial_activation=partial)
        reports.append({'id': area_id, 'vertices': [list(p) for p in points],
                        'partial_activation': partial, **writer})

    baseline_header = struct.unpack_from('<24I', baseline)
    result_header = struct.unpack_from('<24I', result)
    insertion = baseline_header[22]
    added_size = sum(row['vertex_count'] for row in reports) * 48
    if (result[96:insertion] != baseline[96:insertion]
            or result[insertion + added_size:] != baseline[insertion:]
            or result_header[9] != baseline_header[9] + 8
            or len({row['group_id'] for row in reports}) != 2):
        raise ValueError('Reviewed replacement failed baseline preservation checks')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    return result, {
        'experimental': True,
        'operation': 'replace_exact_known_generated_bay_with_two_reviewed_areas',
        'baseline_sha256': sha(baseline), 'previous_sha256': sha(current),
        'result_sha256': sha(result),
        'exact_previous_descriptor_verified': True,
        'previous_generated_group_id': previous_report['group_id'],
        'previous_generated_polygon_removed': True,
        'area_count': len(reports), 'areas': reports,
        'source_trigger_records_preserved': True,
        'other_descriptor_sections_preserved': True,
        'partial_activation_semantics': 'PPD flag 0x4 enables contact activation; engine vehicle shape remains unknown',
        'runtime_behavior': 'Unverified; no in-game activation or two-icon result is claimed',
    }
