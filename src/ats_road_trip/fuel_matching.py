"""Match prefab GAS locators to placed fuel items by their world positions.

The PPD control-node coordinates and map prefab-node positions determine the
placement rotation.  The prefab's origin field rotates the control-node order;
assuming PPD node zero is the map origin misplaces real ATS Expansion stations.
Map positions are fixed-point (1/256 metre). Horizontal matching is tight;
vertical matching allows the measured terrain slopes of placed stations.
"""

from __future__ import annotations

import math
import struct

from .map_sector import MapItem, MapNode
from .ppd import inspect_ppd


_CONTROL_NODE_SIZE = 104
_MAX_XZ_ERROR = 0.05  # metres; comfortably above fixed-point rounding
_MAX_Y_ERROR = 0.25   # placed terrain can slope across the prefab width


def _close(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
    return math.hypot(a[0] - b[0], a[2] - b[2]) <= _MAX_XZ_ERROR and abs(a[1] - b[1]) <= _MAX_Y_ERROR


def _control_positions(ppd: bytes) -> tuple[tuple[float, float, float], ...]:
    header = struct.unpack_from('<24I', ppd)
    count, start, end = header[1], header[12], header[13]
    if count < 2:
        raise ValueError('GAS matching requires at least two PPD control nodes')
    if end - start != count * _CONTROL_NODE_SIZE:
        raise ValueError('PPD control-node section has an unsupported extent')
    result = tuple(struct.unpack_from('<3f', ppd, start + i * _CONTROL_NODE_SIZE + 16)
                   for i in range(count))
    if not all(math.isfinite(v) for point in result for v in point):
        raise ValueError('PPD control node has nonfinite coordinates')
    return result


def _node(nodes: dict[int, MapNode], uid: int, owner: int, *, either_direction: bool = False) -> MapNode:
    node = nodes.get(uid)
    if (node is None or node.uid != uid
            or (node.forward != owner and (not either_direction or node.backward != owner))):
        raise ValueError(f'Missing or unlinked map node {uid:#x}')
    if not all(math.isfinite(v) for v in (*node.position, *node.rotation)):
        raise ValueError(f'Nonfinite map node {uid:#x}')
    return node


def match_gas_services(ppd: bytes, prefab: MapItem, nodes: dict[int, MapNode],
                       services: list[MapItem], *, allow_missing_car: bool = False) -> dict[int, int]:
    """Return GAS spawn index -> linked service UID, rejecting uncertain matches.

    ``services`` must contain only the placed fuel items for this prefab, of
    item kind 7 (Service) or 0x23 (FuelPump).  Existing flag-1/0x4000 car
    records are distinguished when two locators occupy the same position.
    In relaxed mode, an unplaced car locator or an extra already-placed car
    item is allowed only while every truck locator and truck item matches.
    """
    info = inspect_ppd(ppd)
    gas = [spawn for spawn in info['spawns'] if spawn['type'] == 3]
    if not gas:
        raise ValueError('PPD has no GAS locators')
    if any(spawn['flags'] not in (None, 0, 1) for spawn in gas):
        raise ValueError('Unsupported GAS locator flags')
    if prefab.kind != 4:
        raise ValueError('Expected a prefab item')
    control = _control_positions(ppd)
    refs = tuple(prefab.details['nodes'])
    origin = prefab.details['origin']
    if len(refs) != len(control) or not 0 <= origin < len(control):
        raise ValueError('Prefab node references or origin disagree with PPD')
    if ((not allow_missing_car and len(services) != len(gas))
            or len({item.uid for item in services}) != len(services)):
        raise ValueError('Fuel item count/UIDs disagree with GAS locators')
    local = [control[(origin + i) % len(control)] for i in range(len(control))]
    world = [_node(nodes, uid, prefab.uid, either_direction=True).position for uid in refs]

    # Project the placed prefab's rotation into XZ. A sloped placement can
    # shorten the horizontal control-node span slightly, so the projected
    # cosine/sine need not have exact unit length. A single control node cannot
    # establish orientation and is intentionally unsupported.
    lx, lz = local[1][0] - local[0][0], local[1][2] - local[0][2]
    wx, wz = world[1][0] - world[0][0], world[1][2] - world[0][2]
    length2 = lx * lx + lz * lz
    if length2 < 1e-6:
        raise ValueError('PPD control nodes have coincident horizontal positions')
    cosine = (lx * wx + lz * wz) / length2
    sine = (lz * wx - lx * wz) / length2
    scale = math.hypot(cosine, sine)
    if not math.isfinite(scale) or abs(scale - 1) > 0.01:
        raise ValueError('Prefab control nodes do not define a unit rotation')

    # Fit elevation as a plane through the placed controls. With only two
    # controls, use grade along their axis and leave cross-slope unknown; the
    # bounded vertical tolerance covers small unmeasured cross-slopes.
    grade = world[1][1] - world[0][1] - (local[1][1] - local[0][1])
    grade_x, grade_z = grade * lx / length2, grade * lz / length2
    anchors = []
    for i in range(2, len(local)):
        dx, dz = local[i][0] - local[0][0], local[i][2] - local[0][2]
        cross = lx * dz - lz * dx
        if abs(cross) > 1e-3 * math.sqrt(length2 * (dx * dx + dz * dz)):
            anchors.append((abs(cross), cross, dx, dz, i))
    if anchors:
        _, cross, dx, dz, i = max(anchors)
        other_grade = world[i][1] - world[0][1] - (local[i][1] - local[0][1])
        grade_x = (grade * dz - lz * other_grade) / cross
        grade_z = (lx * other_grade - grade * dx) / cross
    if not all(math.isfinite(v) for v in (grade_x, grade_z)) or math.hypot(grade_x, grade_z) > 0.5:
        raise ValueError('Prefab control nodes have unsupported terrain grade')

    def placed(point: tuple[float, float, float] | list[float]) -> tuple[float, float, float]:
        dx, dy, dz = (point[i] - local[0][i] for i in range(3))
        return (world[0][0] + cosine * dx + sine * dz,
                world[0][1] + dy + grade_x * dx + grade_z * dz,
                world[0][2] - sine * dx + cosine * dz)

    if any(not _close(placed(p), q) for p, q in zip(local, world)):
        raise ValueError('Prefab control nodes fail world placement check')

    service_positions: dict[int, tuple[float, float, float]] = {}
    for item in services:
        if item.kind not in (7, 0x23) or item.details['parent'] != prefab.uid:
            raise ValueError(f'Fuel item {item.uid:#x} has unexpected kind or parent')
        if item.kind == 7 and item.flags & 0xff:
            raise ValueError(f'Service {item.uid:#x} is not a GAS service')
        service_positions[item.uid] = _node(nodes, item.details['node'], item.uid).position

    result: dict[int, int] = {}
    truck_positions: list[tuple[float, float, float]] = []
    for spawn in gas:
        position = placed(spawn['position'])
        # The observed ATS 1.61 0x4000 bit separates car from truck fuel
        # interactions. Root planning must also verify these flags.
        matches = [item.uid for item in services
                   if _close(position, service_positions[item.uid])
                   and (spawn['flags'] is None
                        or bool(item.flags & 0x4000) == bool(spawn['flags'] & 1))]
        if allow_missing_car and spawn['flags'] == 1 and not matches:
            continue
        if len(matches) != 1:
            raise ValueError(f'GAS spawn {spawn["index"]} has {len(matches)} unique fuel matches')
        result[spawn['index']] = matches[0]
        if spawn['flags'] in (None, 0):
            truck_positions.append(service_positions[matches[0]])
    if len(set(result.values())) != len(result):
        raise ValueError('Multiple GAS locators matched one fuel item')
    if allow_missing_car:
        used = set(result.values())
        for item in services:
            if item.uid in used:
                continue
            if not item.flags & 0x4000:
                raise ValueError(f'Unmatched truck fuel item {item.uid:#x}')
            if not any(service_positions[item.uid] == position for position in truck_positions):
                raise ValueError(f'Unmatched car fuel item {item.uid:#x} is not co-located with a truck item')
    return result
