"""Pinned overlap experiment: retain a truck locator/service and add its car twin.

This edits a reviewed .base suffix and prefab reference list, not arbitrary maps.
Service/node layouts are cross-checked against pinned TruckLib sources; engine
filtering and simultaneous same-position interactions require gameplay testing.
"""

from __future__ import annotations

import hashlib
import math
import struct

from .local_fuel import _record, _refs, patch_local_pump, plan_local_fuel
from .package import ResourceStack, virtual_path
from .ppd import add_petrol_spawns, inspect_ppd


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch_overlapping_pump(sector: bytes, ppd: bytes, *, prefab_uid: int,
                           service_uid: int, alias: str, layout: dict,
                           car_service_uid: int, car_node_uid: int) -> tuple[bytes, bytes, dict]:
    """Duplicate one GAS/service/node, preserving original truck records byte-for-byte.

    Source hashes must be checked by the planner. The declared node-table boundary
    is reviewed metadata; unknown item records before it remain opaque/preserved.
    Only a local 56-byte node table followed by zero visibility children is allowed.
    """
    expected = {'node_count_offset', 'node_count', 'item_count', 'service_node_uid'}
    if not isinstance(layout, dict) or set(layout) != expected:
        raise ValueError('Unsupported overlap layout fields')
    for key in ('node_count_offset', 'node_count', 'item_count'):
        if type(layout[key]) is not int or not 0 < layout[key] < 2 ** 32 - 1:
            raise ValueError('Overlap offsets/counts must be positive integers')
    if not isinstance(layout['service_node_uid'], str):
        raise ValueError('Original service-node UID must be a string')
    node_uid = int(layout['service_node_uid'], 0)
    uids = (prefab_uid, service_uid, node_uid, car_service_uid, car_node_uid)
    if any(type(uid) is not int or not 0 < uid < 2 ** 64 for uid in uids) or len(set(uids)) != 5:
        raise ValueError('Expected five distinct nonzero uint64 identities')
    for uid in (car_service_uid, car_node_uid):
        if struct.pack('<Q', uid) in sector:
            raise ValueError('Generated UID collides with the source sector')

    # Reuse all reviewed 02003/PPD/prefab/service guards. Its conversion result is
    # intentionally discarded: overlap starts from the original truck bytes.
    _, _, checked = patch_local_pump(sector, ppd, prefab_uid=prefab_uid,
                                     service_uid=service_uid, alias=alias)
    prefab = checked['prefab_item_offset']
    service = checked['service_item_offset']
    boundary = layout['node_count_offset']
    count = layout['node_count']
    if (not 20 < boundary < len(sector) - 8
            or struct.unpack_from('<I', sector, 16)[0] != layout['item_count']
            or struct.unpack_from('<I', sector, boundary)[0] != count
            or boundary + 4 + count * 56 + 4 != len(sector)
            or sector[-4:] != b'\0' * 4):
        raise ValueError('Pinned item/node counts, table extent or visibility trailer disagree')
    if not 20 <= prefab < service or service + 77 > boundary:
        raise ValueError('Expected prefab and service records before the node table')
    original_service = sector[service:service + 77]
    if struct.unpack_from('<Q', original_service, 57)[0] != node_uid:
        raise ValueError('Original service does not reference the pinned node')
    node_start = boundary + 4
    node_records = [sector[node_start + i * 56:node_start + (i + 1) * 56] for i in range(count)]
    node_ids = [struct.unpack_from('<Q', record)[0] for record in node_records]
    if len(set(node_ids)) != count or any(not uid for uid in node_ids) or node_ids != sorted(node_ids):
        raise ValueError('Requires a unique, nonzero, UID-sorted original node table')
    if node_uid not in node_ids:
        raise ValueError('Original service node is not in this sector node table')
    if car_node_uid <= max(node_ids) or car_service_uid <= service_uid:
        raise ValueError('Generated UIDs must preserve the reviewed append ordering')
    original_node = node_records[node_ids.index(node_uid)]
    if struct.unpack_from('<QQ', original_node, 36) != (0, service_uid):
        raise ValueError('Expected an independent service node linked forward to its service')
    rotation = struct.unpack_from('<4f', original_node, 20)
    if not all(math.isfinite(value) for value in rotation):
        raise ValueError('Original service node has a nonfinite rotation')
    # Existing variable-length items remain opaque. The reader consumes the item
    # count rather than requiring a final item type or a UID-sort invariant.
    _, after_parts = _refs(sector, prefab + 73)
    _, slave_count_offset = _refs(sector, after_parts)
    slaves, insertion = _refs(sector, slave_count_offset)
    if slaves != [service_uid] or insertion >= service:
        raise ValueError('Expected one original slave reference before the service')
    car_service = bytearray(original_service)
    struct.pack_into('<Q', car_service, 4, car_service_uid)
    struct.pack_into('<I', car_service, 52, 0x80004000)
    struct.pack_into('<Q', car_service, 57, car_node_uid)
    car_node = bytearray(original_node)
    struct.pack_into('<Q', car_node, 0, car_node_uid)
    struct.pack_into('<Q', car_node, 44, car_service_uid)
    changed = bytearray(sector[:boundary])
    # Only the parent prefab's alias/slave list and the file item count change.
    from .local_fuel import token
    struct.pack_into('<Q', changed, prefab + 57, token(alias))
    struct.pack_into('<I', changed, 16, layout['item_count'] + 1)
    struct.pack_into('<I', changed, slave_count_offset, 2)
    changed[insertion:insertion] = struct.pack('<Q', car_service_uid)
    changed.extend(car_service)
    changed.extend(struct.pack('<I', count + 1))
    changed.extend(sector[node_start:-4])
    changed.extend(car_node)
    changed.extend(sector[-4:])
    result = bytes(changed)
    changed_ppd, ppd_report = add_petrol_spawns(ppd)
    if ppd_report['added_count'] != 1:
        raise ValueError('Expected exactly one added car locator')
    after = inspect_ppd(changed_ppd)
    spawns = after['spawns']
    original_spawn_offset = inspect_ppd(ppd)['spawns'][0]['offset']
    if (len(result) != len(sector) + 141 or [s['flags'] for s in spawns] != [0, 1]
            or changed_ppd[spawns[0]['offset']:spawns[0]['offset'] + 36]
            != ppd[original_spawn_offset:original_spawn_offset + 36]
            or changed_ppd[spawns[0]['offset']:spawns[0]['offset'] + 28]
            != changed_ppd[spawns[1]['offset']:spawns[1]['offset'] + 28]):
        raise ValueError('Overlap counts/length or exact PPD transforms disagree')
    old_service_offset = _record(result, 7, service_uid)
    car_service_offset = _record(result, 7, car_service_uid)
    output_boundary = boundary + 8 + 77
    output_node_start = output_boundary + 4
    original_node_offset = output_node_start + node_ids.index(node_uid) * 56
    car_node_offset = output_node_start + count * 56
    if (result[old_service_offset:old_service_offset + 77] != original_service
            or result[original_node_offset:original_node_offset + 56] != original_node
            or result[car_node_offset + 8:car_node_offset + 36] != original_node[8:36]
            or struct.unpack_from('<I', result, output_boundary)[0] != count + 1):
        raise ValueError('Original records or exact map-node transform were not preserved')
    # Reverse the additions and three bounded scalar edits to prove every opaque
    # original item, node, reference and byte survives the reconstruction.
    restored = bytearray(result[:output_boundary - 77])
    del restored[insertion:insertion + 8]
    restored[prefab + 57:prefab + 65] = sector[prefab + 57:prefab + 65]
    restored[16:20] = sector[16:20]
    restored[slave_count_offset:slave_count_offset + 4] = sector[slave_count_offset:slave_count_offset + 4]
    restored.extend(sector[boundary:])
    if bytes(restored) != sector:
        raise ValueError('Source reconstruction failed; opaque original bytes differ')
    return result, changed_ppd, {
        'original_truck_service_preserved': True, 'original_truck_node_preserved': True,
        'original_truck_locator_preserved': True, 'exact_same_ppd_transform': True,
        'exact_same_world_node_transform': True, 'opaque_original_bytes_reconstructed': True,
        'prefab_item_offset': prefab, 'original_service_offset_after': old_service_offset,
        'car_service_offset': car_service_offset, 'car_node_offset': car_node_offset,
        'car_service_uid': hex(car_service_uid), 'car_node_uid': hex(car_node_uid),
        'original_node_uid': hex(node_uid), 'slave_count_before': 1, 'slave_count_after': 2,
        'item_count_before': layout['item_count'], 'item_count_after': layout['item_count'] + 1,
        'node_count_before': count, 'node_count_after': count + 1,
        'node_count_offset_after': output_boundary, 'sector_bytes_added': 141,
        'world_position': [v / 256 for v in struct.unpack_from('<3i', original_node, 8)],
        'world_rotation_wxyz': list(rotation), 'ppd_transformation': ppd_report,
        'ppd_after': after,
    }


def plan_overlapping_fuel(stack: ResourceStack, recipe: dict, *, map_package: str,
                          game_version: str) -> tuple[dict, dict[str, bytes]]:
    """Generate sample 2 from original pinned inputs; never from conversion sample 1."""
    if not isinstance(recipe, dict) or recipe.get('schema_version') != 2 or 'overlap' not in recipe:
        raise ValueError('Overlap generation requires recipe schema version 2')
    overlap = recipe['overlap']
    if not isinstance(overlap, dict) or set(overlap) != {'layout', 'companion_sha256'}:
        raise ValueError('Unsupported overlap metadata')
    baseline_recipe = {key: value for key, value in recipe.items() if key != 'overlap'}
    baseline_recipe['schema_version'] = 1
    # Reuse original fixture validation and private alias creation. Discard all
    # conversion bytes below; this command starts with untouched original data.
    baseline_plan, resources = plan_local_fuel(stack, baseline_recipe, map_package=map_package,
                                              game_version=game_version, alias_prefix='rtp')
    sector_path = baseline_recipe['sector']
    stem = sector_path.removesuffix('.base')
    companions = overlap['companion_sha256']
    if not isinstance(companions, dict) or set(companions) != {stem + ext for ext in ('.data', '.aux', '.desc', '.layer')}:
        raise ValueError('Requires pinned data/aux/desc/layer companions for this fixture')
    buffers = {}
    for path, expected in companions.items():
        virtual_path(path)
        if str(stack.resources[path][0].path) != map_package:
            raise ValueError('Companion resources must come from the selected map package')
        data = stack.read(path)
        if not isinstance(expected, str) or _sha(data) != expected:
            raise ValueError(f'Companion fingerprint mismatch: {path}')
        buffers[path] = data
    if stem + '.snd' in stack.resources:
        raise ValueError('Unexpected sound companion; fixture requires a fresh review')
    layer = buffers[stem + '.layer']
    if len(layer) != 24 or layer[-8:] != b'\xff' * 8:
        raise ValueError('Layer membership is unsupported; requires empty layer fixture')
    sector = stack.read(sector_path)
    source_ppd = 'prefab/gas/us_gas_station_trigger_only.ppd'
    ppd = stack.read(source_ppd)
    uid, service = int(recipe['prefab_uid'], 0), int(recipe['service_uid'], 0)
    seed = f'{recipe["sector_sha256"]}:{uid:x}:overlapping-fuel-pair'
    def generated_uid(role: str) -> int:
        # High prefix preserves the observed local append ordering. These are
        # deterministic ordinary uint64 UIDs, not a game-defined reserved range.
        return (0xf << 60) | (int.from_bytes(hashlib.sha256(f'{seed}:{role}'.encode()).digest()[:8], 'little') & ((1 << 60) - 1))
    car_service_uid, car_node_uid = generated_uid('service'), generated_uid('node')
    for value in (car_service_uid, car_node_uid):
        packed = struct.pack('<Q', value)
        if any(packed in data for data in [sector, *buffers.values()]):
            raise ValueError('Generated UID collides within the pinned sector/companions')
    changed_sector, changed_ppd, changes = patch_overlapping_pump(
        sector, ppd, prefab_uid=uid, service_uid=service, alias=baseline_plan['alias'].split('.')[1],
        layout=overlap['layout'], car_service_uid=car_service_uid, car_node_uid=car_node_uid)
    resources[sector_path] = changed_sector
    private_ppd = next(path for path in resources if path.endswith('.ppd'))
    resources[private_ppd] = changed_ppd
    report = {**baseline_plan, 'analysis': 'same_position_truck_car_pair', 'recipe': recipe,
              'changes': changes,
              'unchanged_companions': [{'path': path, 'sha256': _sha(data), 'size': len(data)}
                                       for path, data in sorted(buffers.items())],
              'limitations': [
                  'Experimental: same-position interaction coexistence and mode filtering are not validated in game.',
                  'Original truck locator/service/node are retained; a separate car locator/service/node shares their transform.',
                  'No physical dispenser, geometry, road or parking position is moved or duplicated.',
                  'The full .base override conflicts with other edits to this sector or its companions.',
                  'Use this sample instead of the previous conversion sample, above ATS Expansion 23.0.',
                  'This is a pinned opaque-byte-preserving splice, not general sector serialization.',
                  'UID collision checks cover this sector and pinned companions, not every object in every possible mod stack.',
              ]}
    return report, resources
