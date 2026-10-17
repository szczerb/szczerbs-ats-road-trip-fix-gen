"""Pinned single-pump map experiment, not a general sector serializer.

The hypothesized petrol service bit is inferred from ATS 1.61 map instances.
Only a reviewed stock 02003 single-GAS prefab and map version 907 are supported.
"""

from __future__ import annotations

import hashlib
import math
import re
import struct

from .package import ResourceStack, virtual_path
from .ppd import inspect_ppd
from .sii import parse_units


def token(value: str) -> int:
    alphabet = '\0' + '0123456789abcdefghijklmnopqrstuvwxyz_'
    if not re.fullmatch(r'[a-z0-9_]{1,12}', value):
        raise ValueError('Invalid SCS token')
    result = sum(alphabet.index(c) * 38 ** i for i, c in enumerate(value))
    if result >= 2 ** 64:
        raise ValueError('SCS token does not fit uint64')
    return result


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record(data: bytes, kind: int, uid: int) -> int:
    needle = struct.pack('<IQ', kind, uid)
    offset = data.find(needle)
    if offset < 16 or data.find(needle, offset + 1) != -1 or offset + 57 > len(data):
        raise ValueError('Expected exactly one complete map item with the requested type/UID')
    bounds = struct.unpack_from('<10f', data, offset + 12)
    if not all(math.isfinite(v) for v in bounds) or any(bounds[i] > bounds[i + 5] for i in range(5)):
        raise ValueError('Invalid map item bounds')
    return offset


def _refs(data: bytes, offset: int) -> tuple[list[int], int]:
    if offset + 4 > len(data):
        raise ValueError('Truncated map reference list')
    count = struct.unpack_from('<I', data, offset)[0]
    if count > 32 or offset + 4 + count * 8 > len(data):
        raise ValueError('Unsupported map reference list')
    return list(struct.unpack_from(f'<{count}Q', data, offset + 4)), offset + 4 + count * 8


def patch_local_pump(sector: bytes, ppd: bytes, *, prefab_uid: int,
                     service_uid: int, alias: str) -> tuple[bytes, bytes, dict]:
    """Change one existing pump, preserving lengths, transforms and references.

    Callers must pin source hashes before invoking this bounded field patcher.
    Pattern lookup plus field cross-checks do not constitute full deserialization.
    """
    if (len(sector) < 16 or struct.unpack_from('<I', sector)[0] != 907
            or struct.unpack_from('<Q', sector, 4)[0] != token('euro2')
            or struct.unpack_from('<I', sector, 12)[0] != 3):
        raise ValueError('Requires reviewed map format 907 / euro2 / 3')
    if (not 0 < prefab_uid < 2 ** 64 or not 0 < service_uid < 2 ** 64
            or prefab_uid == service_uid):
        raise ValueError('Expected distinct nonzero prefab/service UIDs')
    alias_number = token(alias)
    if alias_number == token('02003'):
        raise ValueError('Alias must differ from the original prefab token')
    start = _record(sector, 4, prefab_uid)
    if start + 73 > len(sector):
        raise ValueError('Truncated prefab item')
    model, variant = struct.unpack_from('<QQ', sector, start + 57)
    if model != token('02003') or variant not in (0, token('default')):
        raise ValueError('Only the stock 02003 prefab with its default variant is reviewed')
    parts, offset = _refs(sector, start + 73)
    nodes, offset = _refs(sector, offset)
    slaves, _ = _refs(sector, offset)
    if parts or len(nodes) != 2 or not all(nodes) or len(set(nodes)) != 2 or slaves != [service_uid]:
        raise ValueError('Expected two distinct prefab nodes, no parts and exactly the linked service')
    service = _record(sector, 7, service_uid)
    if service + 77 > len(sector):
        raise ValueError('Truncated service item')
    flags = struct.unpack_from('<I', sector, service + 52)[0]
    node, parent = struct.unpack_from('<QQ', sector, service + 57)
    extra, _ = _refs(sector, service + 73)
    if flags != 0x80000000 or not node or parent != prefab_uid or extra:
        raise ValueError('Unexpected service flags, parent, node or extra references')
    info = inspect_ppd(ppd)
    if (info['version'] != 25 or info['spawn_count'] != 1
            or info['trigger_count'] != 0 or struct.unpack_from('<I', ppd, 4)[0] != 2
            or info['spawns'][0]['type'] != 3 or info['spawns'][0]['flags'] != 0):
        raise ValueError('Requires a v25 descriptor with two nodes and one flags-0 GAS locator')
    flag_offset = info['spawns'][0]['offset'] + 32
    changed_sector = bytearray(sector)
    struct.pack_into('<Q', changed_sector, start + 57, alias_number)
    struct.pack_into('<I', changed_sector, service + 52, flags | 0x4000)
    changed_ppd = bytearray(ppd)
    struct.pack_into('<I', changed_ppd, flag_offset, 1)
    changed_sector, changed_ppd = bytes(changed_sector), bytes(changed_ppd)
    allowed = set(range(start + 57, start + 65)) | set(range(service + 52, service + 56))
    diff = [i for i, (a, b) in enumerate(zip(sector, changed_sector)) if a != b]
    if len(sector) != len(changed_sector) or not set(diff) <= allowed:
        raise ValueError('Unexpected sector mutation')
    if [i for i, (a, b) in enumerate(zip(ppd, changed_ppd)) if a != b] != [flag_offset]:
        raise ValueError('Unexpected descriptor mutation')
    after = inspect_ppd(changed_ppd)
    if after['spawns'][0]['flags'] != 1:
        raise ValueError('Output descriptor cross-check failed')
    return changed_sector, changed_ppd, {
        'prefab_item_offset': start, 'service_item_offset': service,
        'sector_changed_byte_offsets': diff, 'ppd_changed_byte_offsets': [flag_offset],
        'service_flags_before': hex(flags), 'service_flags_after': hex(flags | 0x4000),
        'ppd_before': info, 'ppd_after': after,
    }


def plan_local_fuel(stack: ResourceStack, recipe: dict, *, map_package: str,
                    game_version: str) -> tuple[dict, dict[str, bytes]]:
    """Generate only from reviewed, fingerprinted inputs; never discover a target implicitly."""
    required = {'schema_version', 'game_version', 'sector', 'sector_sha256',
                'descriptor_sha256', 'prefab_uid', 'service_uid', 'location'}
    if not isinstance(recipe, dict) or set(recipe) != required or recipe['schema_version'] != 1:
        raise ValueError('Unsupported local-fuel recipe fields/version')
    if not all(isinstance(recipe[key], str) for key in required - {'schema_version', 'location'}):
        raise ValueError('Recipe paths, UIDs, version and hashes must be strings')
    if not isinstance(recipe['location'], dict):
        raise ValueError('Recipe location must be an object')
    if recipe['game_version'] != game_version or game_version != '1.61.3.18':
        raise ValueError('This recipe requires the inspected ATS 1.61.3.18 baseline')
    sector_path = virtual_path(recipe['sector'])
    if not re.fullmatch(r'map/usa/sec[+-]\d{4}[+-]\d{4}\.base', sector_path):
        raise ValueError('Expected an explicit usa .base sector path')
    if str(stack.resources[sector_path][0].path) != map_package:
        raise ValueError('Target sector must come from the explicitly selected map package')
    source_ppd = 'prefab/gas/us_gas_station_trigger_only.ppd'
    sector, ppd = stack.read(sector_path), stack.read(source_ppd)
    for data, key in ((sector, 'sector_sha256'), (ppd, 'descriptor_sha256')):
        if not isinstance(recipe[key], str) or _hash(data) != recipe[key]:
            raise ValueError(f'Source fingerprint mismatch: {key}')
    uid, slave = int(recipe['prefab_uid'], 0), int(recipe['service_uid'], 0)
    alias = 'rtf' + _hash(f'{sector_path}:{uid:x}'.encode())[:8]
    destination = f'prefab/rtfix/{alias}.ppd'
    definition_path = f'def/world/prefab.{alias}.sii'
    if any(path in stack.resources for path in (destination, definition_path)):
        raise ValueError('Generated resource collides with an input')
    pattern = r'def/world/prefab(?:\.[^/]+)?\.sii'
    stack.prefetch(pattern)
    original_units = []
    for path in stack.matching(pattern):
        text = stack.text(path)
        if re.search(r'\bprefab\.' + re.escape(alias) + r'\b', text):
            raise ValueError('Generated prefab identifier collides with an input')
        original_units.extend(u for u in parse_units(text, source=path, include_reader=stack.text)
                              if u.kind == 'prefab_model' and u.name == 'prefab.02003')
    if len(original_units) != 1:
        raise ValueError('Requires exactly one effective stock 02003 definition')
    unit = original_units[0]
    expected = {'name': ('us gas / trigger only',),
                'model_desc': ('/prefab/gas/us_gas_station_trigger_only.pmd',),
                'prefab_desc': ('/' + source_ppd,), 'category': ('',)}
    if unit.attribute_errors or unit.attributes != expected:
        raise ValueError('Stock 02003 definition differs from the reviewed configuration')
    model_path = expected['model_desc'][0].lstrip('/')
    if model_path not in stack.resources:
        raise ValueError('Source model is absent from the supplied stack')
    changed_sector, changed_ppd, changes = patch_local_pump(
        sector, ppd, prefab_uid=uid, service_uid=slave, alias=alias)
    # Copy the complete supported definition: only identifier/descriptor differ.
    definition = ('SiiNunit\n{\nprefab_model : prefab.' + alias + '\n{\n'
                  '    name: "us gas / trigger only"\n'
                  '    model_desc: "/' + model_path + '"\n'
                  '    prefab_desc: "/' + destination + '"\n'
                  '    category: ""\n}\n}\n').encode()
    report = {
        'schema_version': 1, 'analysis': 'pinned_single_pump_conversion',
        'recipe': recipe, 'alias': 'prefab.' + alias,
        'package_order': [str(p.path) for p in stack.packages],
        'source_resources': [
            {'path': path, 'package': str(stack.resources[path][0].path),
             'sha256': _hash(data)} for path, data in ((sector_path, sector), (source_ppd, ppd))],
        'changes': changes,
        'limitations': [
            'Unverified hypothesis: PPD GAS flags 1 and service bit 0x4000 select car/petrol interaction.',
            'Converts one existing pump to car use; truck access at this pump may disappear.',
            'Other pumps and descriptor users retain their original resources and flags.',
            'A full .base sector override conflicts with any other mod changing that sector.',
            'This is bounded field validation, not full sector deserialization or in-game verification.',
            'Starting-city selection, garage substitution, physical access and successful refueling remain unverified.',
        ],
    }
    return report, {sector_path: changed_sector, destination: changed_ppd, definition_path: definition}
