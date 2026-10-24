"""Additive native truck-rest polygons with effective-action validation.

This writer neither discovers facilities nor infers a parking footprint. The
caller supplies reviewed truck-scale local geometry and a native source group.
PPD partial activation is bit 0x4; standalone Trigger flags use another schema.
"""
from __future__ import annotations

from collections.abc import Mapping
import struct

from ..ppd import inspect_ppd
from ..rest_stops import inspect_rest_triggers
from ..station_parking.trigger import (
    _TRIGGER, _append_native_parking_polygon, _validate_existing_layout,
    _validate_vertices,
)


def _vehicles(action_modes, action, *, emitted):
    if type(action) is not int or not 0 < action <= 0xffffffffffffffff:
        raise ValueError('Truck rest action token must be a nonzero uint64 integer')
    if action not in action_modes:
        raise ValueError('Truck rest action has no resolved effective native rest definition')
    vehicles = action_modes[action]
    if not isinstance(vehicles, (set, frozenset, list, tuple)) or any(
            not isinstance(v, str) for v in vehicles):
        raise ValueError('Truck rest effective vehicles must be an explicit collection of names')
    vehicles = set(vehicles)
    if 'truck' not in vehicles or vehicles - {'truck', 'bus', 'car'}:
        raise ValueError('Truck rest effective action has unsupported vehicle eligibility')
    if emitted and 'car' in vehicles:
        raise ValueError('New truck rest polygons must not grant car eligibility; select a validated car-free native action')
    return vehicles


def append_truck_parking_polygon(
    data: bytes, vertices: list[tuple[float, float, float]], *,
    source_group_id: int, action_modes: Mapping[int, set[str]],
    action_token: int | None = None, partial_activation: bool | None = None,
) -> tuple[bytes, dict]:
    """Append one independent native truck group without changing source bytes.

    ``action_modes`` must come from the effective ``hud_activate``/rest-ID-3
    definition census, not a filename guess. The selected native source group
    must support trucks. Its range/reset tuple is accepted only when it matches
    the reviewed ATS 1.61 native (3, 0, 0) contract, uniformly across vertices.
    Unknown parameters, mixed flags, absent/ambiguous groups and new car access
    block generation. Existing mixed truck/bus/car source groups stay intact;
    their parameters may be reused with an explicitly selected, validated
    car-free native action. No shared action definition is rewritten.

    ``None`` preserves source flags. True selects PPD contact flag 0x4; False
    selects full containment flag 0. Range is vertical, not a horizontal truck
    size. Source geometry and all prior groups remain exact. Contact activation
    is documented by SCS's prefab-locator authoring contract; the ATS 1.61
    player/trailer test shape and runtime behavior remain unverified.
    """
    if type(source_group_id) is not int or not 0 <= source_group_id <= 0xffffffff:
        raise ValueError('Truck rest source group ID must be a uint32 integer')
    if partial_activation is not None and type(partial_activation) is not bool:
        raise ValueError('partial_activation must be a boolean or None')
    if not isinstance(action_modes, Mapping):
        raise ValueError('Truck rest action_modes must be an effective action mapping')
    info = inspect_ppd(data)
    if info['version'] != 25:
        raise ValueError('Truck rest generation requires PPD v25')
    header = struct.unpack_from('<24I', data)
    _validate_existing_layout(data, header)
    groups = inspect_rest_triggers(data, actions=set(action_modes))
    selected = [g for g in groups if g['id'] == source_group_id]
    if len(selected) != 1:
        raise ValueError('Truck rest source group is absent or ambiguous')
    source = selected[0]
    source_vehicles = _vehicles(action_modes, source['action'], emitted=False)
    action = source['action'] if action_token is None else action_token
    vehicles = _vehicles(action_modes, action, emitted=True)
    parameters = {_TRIGGER.unpack_from(data, header[21] + i * _TRIGGER.size)[2:6]
                  for i in source['indices']}
    if len(parameters) != 1:
        raise ValueError('Truck rest source group has nonuniform native parameters')
    range_value, reset_delay, reset_distance, source_flags = parameters.pop()
    if (range_value, reset_delay, reset_distance) != (3., 0., 0.) or source_flags not in (0, 4):
        raise ValueError('Truck rest source parameters differ from the reviewed native contract')
    flags = source_flags if partial_activation is None else (4 if partial_activation else 0)
    try:
        points = _validate_vertices(vertices)
    except ValueError as exc:
        raise ValueError(str(exc).replace('Car parking', 'Truck parking').replace('car parking', 'truck parking')) from exc
    result, group_id = _append_native_parking_polygon(
        data, points, action=action,
        parameters=(range_value, reset_delay, reset_distance, flags),
        actions=set(action_modes), label='Truck rest',
    )
    return result, {
        'experimental': True,
        'action_token': action,
        'vehicles': sorted(vehicles),
        'source_group_id': source_group_id,
        'source_action_token': source['action'],
        'source_vehicles': sorted(source_vehicles),
        'group_id': group_id,
        'vertex_count': len(points),
        'parameters': {'range': range_value, 'reset_delay': reset_delay,
                       'reset_distance': reset_distance, 'flags': flags},
        'source_parameters': {'range': range_value, 'reset_delay': reset_delay,
                              'reset_distance': reset_distance, 'flags': source_flags},
        'source_trigger_records_preserved': True,
        'other_descriptor_sections_preserved': True,
        'new_car_eligibility': False,
        'independent_group_and_links': True,
        'partial_activation': bool(flags & 4),
        'activation_semantics': 'PPD flag 0x4 permits boundary contact; range is vertical',
        'selection': 'Caller-supplied reviewed truck parking region; no facility or coverage inference',
        'runtime_vehicle_and_trailer_shape': 'Unknown; no in-game test performed',
        'runtime_behavior': 'Unknown; no in-game test performed',
    }
