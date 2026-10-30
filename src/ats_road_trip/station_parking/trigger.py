"""Bounded PPD writer for an explicitly selected station's car rest polygon.

This primitive appends one native ``parking_car`` polygon to a v25 descriptor.
It does not select stations, infer geometry, or clone existing truck triggers.
"""
from __future__ import annotations

import math
import struct

from ..local_fuel import token
from ..ppd import inspect_ppd
from ..rest_stops import inspect_rest_triggers

_CAR = token('parking_car')
_TRIGGER = struct.Struct('<IQfffI3f2i')
_MAX_HEIGHT_VARIATION = 0.5
_MAX_VERTICES = 64
_MAX_ABS_COORDINATE = 1_000_000.0


def _validate_vertices(vertices: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    if not isinstance(vertices, list) or len(vertices) < 3:
        raise ValueError('Car parking polygon requires at least three vertices')
    if len(vertices) > _MAX_VERTICES:
        raise ValueError(f'Car parking polygon exceeds {_MAX_VERTICES} vertices')
    points = []
    for vertex in vertices:
        if not isinstance(vertex, (tuple, list)) or len(vertex) != 3:
            raise ValueError('Each car parking vertex must be an (x, y, z) triple')
        if any(isinstance(value, bool) for value in vertex):
            raise ValueError('Car parking vertices must be numeric triples, not booleans')
        try:
            point = tuple(float(value) for value in vertex)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('Car parking vertices must be finite numbers') from exc
        if not all(math.isfinite(value) for value in point):
            raise ValueError('Car parking vertices must be finite numbers')
        if any(abs(value) > _MAX_ABS_COORDINATE for value in point):
            raise ValueError('Car parking vertex coordinates exceed the +/-1,000,000 game-unit bound')
        try:
            packed = struct.pack('<3f', *point)
            unpacked = struct.unpack('<3f', packed)
        except (OverflowError, struct.error) as exc:
            raise ValueError('Car parking vertices must be representable as float32') from exc
        if not all(math.isfinite(value) for value in unpacked):
            raise ValueError('Car parking vertices must be representable as finite float32 values')
        points.append(point)
    if len(set(points)) != len(points):
        raise ValueError('Car parking polygon is degenerate')
    if len({(p[0], p[2]) for p in points}) != len(points):
        raise ValueError('Car parking polygon repeats an XZ point at a different height')
    if max(p[1] for p in points) - min(p[1] for p in points) > _MAX_HEIGHT_VARIATION:
        raise ValueError('Car parking polygon height variation exceeds 0.5 game units')
    horizontal = [(p[0], p[2]) for p in points]
    for a, b in zip(horizontal, horizontal[1:] + horizontal[:1]):
        if a == b:
            raise ValueError('Car parking polygon has a zero-length adjacent XZ edge')
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(horizontal, horizontal[1:] + horizontal[:1]))
    if abs(area) < 1e-6:
        raise ValueError('Car parking polygon has no horizontal area')
    edges = list(zip(horizontal, horizontal[1:] + horizontal[:1]))
    for i, (a, b) in enumerate(edges):
        for j, (c, d) in enumerate(edges):
            if j <= i + 1 or (i == 0 and j == len(edges) - 1):
                continue
            if _intersects(a, b, c, d):
                raise ValueError('Car parking polygon self-intersects')
    return points


def _intersects(a, b, c, d) -> bool:
    def cross(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def on(p, q, r):
        return (min(p[0], q[0]) - 1e-9 <= r[0] <= max(p[0], q[0]) + 1e-9
                and min(p[1], q[1]) - 1e-9 <= r[1] <= max(p[1], q[1]) + 1e-9)

    values = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    return ((values[0] * values[1] < 0 and values[2] * values[3] < 0)
            or (abs(values[0]) < 1e-9 and on(a, b, c))
            or (abs(values[1]) < 1e-9 and on(a, b, d))
            or (abs(values[2]) < 1e-9 and on(c, d, a))
            or (abs(values[3]) < 1e-9 and on(c, d, b)))


def _validate_existing_layout(data: bytes, header: tuple[int, ...]) -> None:
    count, start, end = header[9], header[21], header[22]
    if start + count * _TRIGGER.size != end:
        raise ValueError('PPD trigger count and section extent disagree')
    records = []
    for index in range(count):
        values = _TRIGGER.unpack_from(data, start + index * _TRIGGER.size)
        if not all(math.isfinite(value) for value in (*values[2:5], *values[6:9])):
            raise ValueError('PPD contains nonfinite trigger data')
        records.append(values)
    for index, record in enumerate(records):
        for neighbor in record[9:11]:
            if neighbor < 0 or neighbor >= count or neighbor == index:
                raise ValueError('PPD contains an out-of-range trigger neighbor')
            other = records[neighbor]
            if index not in other[9:11]:
                raise ValueError('PPD trigger neighbors are not reciprocal')
            if record[0:2] != other[0:2]:
                raise ValueError('PPD trigger neighbor crosses a group or action boundary')
    # The existing rest inspector additionally checks supported parking polygon
    # cycles, duplicate/branching links, and horizontal geometry.
    inspect_rest_triggers(data)


def _append_native_parking_polygon(
    data: bytes, points: list[tuple[float, float, float]], *, action: int,
    parameters: tuple[float, float, float, int], actions=None,
    label: str = 'Station car-rest',
) -> tuple[bytes, int]:
    """Shared binary splice after caller-specific eligibility/geometry checks.

    The header and new records are the only authored bytes. Every existing
    trigger, group ID, link, opaque preceding section and suffix is retained.
    """
    try:
        info = inspect_ppd(data)
    except (struct.error, TypeError) as exc:
        raise ValueError(f'Invalid PPD descriptor: {exc}') from exc
    if info['version'] != 25:
        raise ValueError(f'{label} generation requires PPD v25')
    header = list(struct.unpack_from('<24I', data))
    _validate_existing_layout(data, tuple(header))
    if actions is not None:
        inspect_rest_triggers(data, actions=actions)
    count, insertion = header[9], header[22]
    if count >= 0xFFFFFFFF or count + len(points) > 0x7FFFFFFF:
        raise ValueError('PPD trigger count or neighbor index capacity would overflow')
    used_ids = {struct.unpack_from('<I', data, header[21] + _TRIGGER.size * i)[0]
                for i in range(count)}
    group_id = next((candidate for candidate in range(count + 1) if candidate not in used_ids), None)
    if group_id is None or group_id > 0xFFFFFFFF:
        raise ValueError('No independent PPD trigger group ID is available')

    first_index = count
    records = []
    for i, (x, y, z) in enumerate(points):
        records.append(_TRIGGER.pack(
            group_id, action, *parameters, x, y, z,
            first_index + (i - 1) % len(points),
            first_index + (i + 1) % len(points),
        ))
    extra = b''.join(records)
    if insertion + len(extra) > 0xFFFFFFFF:
        raise ValueError('PPD descriptor offsets would overflow')
    header[9] += len(records)
    header[22] += len(extra)
    header[23] += len(extra)
    result = struct.pack('<24I', *header) + data[96:insertion] + extra + data[insertion:]

    after = inspect_ppd(result)
    groups = inspect_rest_triggers(result, actions=actions)
    created = [group for group in groups if group['id'] == group_id and group['action'] == action]
    packed_points = {tuple(struct.unpack('<3f', struct.pack('<3f', *point))) for point in points}
    if (after['trigger_count'] != count + len(points) or len(created) != 1
            or set(created[0]['vertices']) != packed_points
            or result[96:insertion] != data[96:insertion]
            or result[insertion + len(extra):] != data[insertion:]):
        raise ValueError(f'Appended {label.lower()} polygon failed structural preservation checks')
    return result, group_id


def append_car_parking_polygon(
    data: bytes, vertices: list[tuple[float, float, float]], *,
    partial_activation: bool = False,
) -> tuple[bytes, dict]:
    """Append one native v25 car-only rest polygon to a station descriptor.

    ``vertices`` must be the explicitly reviewed station-local polygon in PPD
    coordinates and ordered around its perimeter. The original bytes outside
    the header and insertion point are preserved. Native parameters are pinned
    to the inspected ATS 1.61 ``base.scs`` Chemron ``hud_parking`` PPD template:
    range 3, reset delay 0, reset distance 0, flags 0. An explicit
    ``partial_activation=True`` sets only the new polygon's flag bit 0x4,
    enabling contact activation according to the engine parameter. It does not
    establish the runtime vehicle shape, fatigue behavior or marker count.
    """
    if type(partial_activation) is not bool:
        raise ValueError('partial_activation must be a boolean')
    flags = 4 if partial_activation else 0
    try:
        info = inspect_ppd(data)
    except (struct.error, TypeError) as exc:
        raise ValueError(f'Invalid PPD descriptor: {exc}') from exc
    if info['version'] != 25:
        raise ValueError('Station car-rest generation requires PPD v25')
    points = _validate_vertices(vertices)
    result, group_id = _append_native_parking_polygon(
        data, points, action=_CAR, parameters=(3.0, 0.0, 0.0, flags))
    return result, {
        'experimental': True,
        'action': 'parking_car',
        'group_id': group_id,
        'vertex_count': len(points),
        'parameters': {'range': 3.0, 'reset_delay': 0.0, 'reset_distance': 0.0, 'flags': flags},
        'source_trigger_records_preserved': True,
        'other_descriptor_sections_preserved': True,
        'selection': 'Caller-supplied explicit station only; no proximity or density inference',
        'runtime_behavior': 'Unknown; no in-game test performed',
    }


def partial_activation_diagnostic(data: bytes, group_id: int) -> tuple[bytes, dict]:
    """Set only PPD partial-contact bit 0x4 on one native car polygon.

    This deliberately named diagnostic isolates a documented parameter. It is
    not the default parking writer or a claim about the tested vehicle shape.
    All geometry, action, IDs, range/reset parameters and other groups remain
    byte-identical. Standalone Trigger flags have different semantics.
    """
    if type(group_id) is not int or not 0 <= group_id <= 0xffffffff:
        raise ValueError('Diagnostic group ID must be a uint32 integer')
    info=inspect_ppd(data)
    if info['version']!=25:
        raise ValueError('Partial activation diagnostic requires PPD v25')
    header=struct.unpack_from('<24I',data)
    _validate_existing_layout(data,header)
    groups=inspect_rest_triggers(data)
    matching=[g for g in groups if g['id']==group_id]
    if len(matching)!=1 or matching[0]['action']!=_CAR or matching[0]['flags']!=0:
        raise ValueError('Diagnostic requires exactly one non-partial native parking_car group')
    result=bytearray(data);allowed=set();vertices=0
    for index in range(header[9]):
        offset=header[21]+index*_TRIGGER.size
        record=_TRIGGER.unpack_from(data,offset)
        if record[0]!=group_id:continue
        if record[1]!=_CAR or record[5]!=0:
            raise ValueError('Diagnostic group contains conflicting actions or flags')
        struct.pack_into('<I',result,offset+24,4)
        allowed.update(range(offset+24,offset+28));vertices+=1
    result=bytes(result)
    if not vertices or any(i not in allowed for i,(a,b) in enumerate(zip(data,result)) if a!=b):
        raise ValueError('Diagnostic changed bytes outside the selected flag fields')
    after=inspect_rest_triggers(result)
    expected=[dict(g,flags=4) if g['id']==group_id else g for g in groups]
    if after!=expected:
        raise ValueError('Diagnostic altered geometry or unrelated trigger fields')
    return result,{'diagnostic':'partial_activation_only','group_id':group_id,
        'action':'parking_car','old_flags':0,'new_flags':4,'vertex_count':vertices,
        'geometry_and_other_fields_preserved':True,'engine_vehicle_shape':'Unknown',
        'runtime_behavior':'Unverified; compare stationary edge crossings against the unchanged control'}
