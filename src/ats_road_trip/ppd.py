"""Bounded PPD inspection and experimental v25 fuel locator duplication.

GAS type 3 is documented in SCS Blender Tools. The meaning of flag 1 is
inferred from installed ATS 1.61 Road Trip car station descriptors, and still
requires gameplay validation. This module does not rebuild map spawn caches.
"""

import math
import struct


class PpdError(ValueError):
    """Unsupported or inconsistent descriptor."""


def inspect_ppd(data: bytes) -> dict:
    """Read v23/v24/v25 spawn records without interpreting other sections."""
    if len(data) < 96:
        raise PpdError('PPD header is truncated (requires 96 bytes)')
    header = struct.unpack_from('<24I', data)
    version = header[0]
    if version not in (23, 24, 25):
        raise PpdError(f'Unsupported PPD version {version}; supported: 23, 24, 25')
    offsets = header[12:24]
    if offsets[0] != 96 or any(x > len(data) for x in offsets):
        raise PpdError('PPD section offsets lie outside the descriptor')
    if any(a > b for a, b in zip(offsets, offsets[1:])):
        raise PpdError('PPD section offsets are not ordered')
    stride = 32 if version == 23 else 36
    count, start, end = header[5], header[16], header[17]
    if start + count * stride != end:
        raise PpdError('PPD spawn count and section extent disagree')
    spawns = []
    for i in range(count):
        offset = start + i * stride
        values = struct.unpack_from('<7fI', data, offset)
        if not all(math.isfinite(x) for x in values[:7]):
            raise PpdError(f'Spawn {i} contains a non-finite position or rotation')
        spawns.append({
            'index': i, 'offset': offset, 'type': values[7],
            'flags': struct.unpack_from('<I', data, offset + 32)[0] if version >= 24 else None,
            'position': list(values[:3]), 'rotation': list(values[3:7]),
        })
    gas = [s for s in spawns if s['type'] == 3]
    return {
        'version': version, 'size': len(data), 'spawn_count': count,
        'trigger_count': header[9], 'spawns': spawns,
        'fuel': {
            'gas_spawn_count': len(gas),
            'legacy_unflagged_count': sum(s['flags'] is None for s in gas),
            'flags_zero_count': sum(s['flags'] == 0 for s in gas),
            'flags_one_count': sum(s['flags'] == 1 for s in gas),
            'other_flags': sorted({s['flags'] for s in gas if s['flags'] not in (None, 0, 1)}),
        },
    }


def add_petrol_spawns(data: bytes) -> tuple[bytes, dict]:
    """Duplicate v25 GAS/flags=0 at the same transform using flags=1.

    Original records, section contents and existing indices stay intact. This
    produces an experimental candidate, not a confirmed station repair. Unknown
    GAS flags and older versions are rejected; no implicit format upgrade occurs.
    Exact matching transforms already bearing flags=1 are skipped.
    """
    before = inspect_ppd(data)
    if before['version'] != 25:
        raise PpdError('Experimental fuel generation requires PPD v25; no format upgrade is implemented')
    if before['fuel']['other_flags']:
        raise PpdError('Unknown GAS spawn flags; refusing to infer their meaning')
    def transform(spawn):
        return data[spawn['offset']:spawn['offset'] + 28]
    existing = {transform(s) for s in before['spawns'] if s['type'] == 3 and s['flags'] == 1}
    added = []
    records = []
    for spawn in before['spawns']:
        if spawn['type'] == 3 and spawn['flags'] == 0 and transform(spawn) not in existing:
            records.append(data[spawn['offset']:spawn['offset'] + 32] + struct.pack('<I', 1))
            added.append(spawn['index'])
            existing.add(transform(spawn))
    if not before['fuel']['gas_spawn_count']:
        raise PpdError('Descriptor has no GAS spawn to duplicate')
    header = list(struct.unpack_from('<24I', data))
    insertion = header[17]
    extra = b''.join(records)
    header[5] += len(records)
    for index in range(17, 24):
        header[index] += len(extra)
    result = struct.pack('<24I', *header) + data[96:insertion] + extra + data[insertion:]
    after = inspect_ppd(result)
    return result, {
        'experimental': True,
        'added_count': len(records), 'source_spawn_indices': added,
        'before': before['fuel'], 'after': after['fuel'],
        'map_spawn_rebuild': 'Unknown whether required; PPD-only behavior has not been tested in game',
        'placement': 'New flag-1 locators share existing flag-0 transforms; reachability and interaction untested',
    }


def upgrade_fuel_descriptor(data: bytes) -> tuple[bytes, dict]:
    """Upgrade legacy spawn flags only when all other sections are compatible.

    TruckLib.Models version dispatch: v23 lacks the spawn flags word, v24
    already has it; v25 changes semaphore records too. Refuse nonempty legacy
    semaphores, preserving every other opaque section byte-for-byte.
    """
    info = inspect_ppd(data)
    version = info['version']
    if version == 25:
        return data, {'from_version': 25, 'to_version': 25, 'upgraded': False}
    header = list(struct.unpack_from('<24I', data))
    if header[4]:
        raise PpdError('Legacy PPD semaphore conversion is unsupported')
    start, end = header[16:18]
    if version == 23:
        records = b''.join(data[start + 32*i:start + 32*(i+1)] + b'\0'*4
                           for i in range(header[5]))
        extra = 4 * header[5]
        for i in range(17, 24):
            header[i] += extra
    else:
        records = data[start:end]
    header[0] = 25
    result = struct.pack('<24I', *header) + data[96:start] + records + data[end:]
    inspect_ppd(result)
    return result, {'from_version': version, 'to_version': 25, 'upgraded': True,
                    'legacy_semaphores': 0, 'opaque_nonspawn_sections_preserved': True}
