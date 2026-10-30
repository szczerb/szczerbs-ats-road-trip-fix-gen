"""Structural ATS map-907 reader; preserve uninterpreted payload bytes on edits.

Layouts were implemented after consulting TruckLib inspected tree
c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0 (ScsMap/Serialization, Node,
ActionBase, TerrainQuadData and related structs); see THIRD_PARTY_NOTICES.md.
Unlike pattern searching, every item is reached by consuming the preceding item.
Unknown layouts, truncation and trailing data fail closed. This is not a .data
payload serializer, and compound-contained fuel is reported as nested, not a
root-level splice target. Original game assets are never included in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import struct

from .local_fuel import token


class SectorFormatError(ValueError):
    """The input cannot be parsed completely with the supported layout."""


@dataclass(frozen=True)
class MapItem:
    kind: int
    uid: int
    offset: int
    end: int
    flags: int
    details: dict


@dataclass(frozen=True)
class MapNode:
    uid: int
    offset: int
    raw: bytes
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]
    backward: int
    forward: int
    flags: int


@dataclass(frozen=True)
class Sector:
    items: tuple[MapItem, ...]
    nodes: tuple[MapNode, ...]
    node_count_offset: int
    visibility_children_offset: int
    visibility_children: tuple[int, ...]
    suffix: bytes

    @property
    def prefabs(self) -> tuple[MapItem, ...]:
        return tuple(i for i in self.items if i.kind == 4)

    @property
    def services(self) -> tuple[MapItem, ...]:
        return tuple(i for i in self.items if i.kind in (7, 0x23))

    @property
    def companies(self) -> tuple[MapItem, ...]:
        return tuple(i for i in self.items if i.kind == 6)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def node_count(self) -> int:
        return len(self.nodes)


class _Reader:
    def __init__(self, data: bytes):
        self.data, self.pos = data, 0

    def skip(self, size: int) -> None:
        if size < 0 or self.pos + size > len(self.data):
            raise SectorFormatError(f'Truncated map structure at offset {self.pos} (need {size} bytes)')
        self.pos += size

    def read(self, fmt: str):
        size = struct.calcsize('<' + fmt)
        start = self.pos
        self.skip(size)
        result = struct.unpack_from('<' + fmt, self.data, start)
        return result[0] if len(result) == 1 else result

    def count(self, width: int = 1) -> int:
        n = self.read('I')
        if n > (len(self.data) - self.pos) // max(1, width):
            raise SectorFormatError(f'Invalid array extent at offset {self.pos - 4}')
        return n

    def array(self, width: int) -> int:
        n = self.count(width)
        self.skip(n * width)
        return n

    def refs(self) -> tuple[int, ...]:
        n = self.count(8)
        return tuple(self.read('Q') for _ in range(n))

    def string(self) -> bytes:
        n = self.read('Q')
        start = self.pos
        self.skip(n)
        return self.data[start:self.pos]


def _header(r: _Reader) -> None:
    if r.read('IQI') != (907, token('euro2'), 3):
        raise SectorFormatError('Requires map format 907 / euro2 / 3')


def _quad(r: _Reader) -> None:
    r.skip(r.read('H') * 10)  # material token + uint16 rotation
    r.skip(r.read('H') * 4)   # colors
    r.skip(4)                # rows/columns
    r.array(4)               # terrain quads
    r.array(16)              # offset vertices
    r.array(16)              # normals


def _action(r: _Reader) -> None:
    n = r.read('I')
    if n == 0xffffffff:
        return
    r.skip(n * 4)
    for _ in range(r.count(8)):
        r.string()
    r.array(8)
    r.skip(8)


def _nodes(r: _Reader) -> tuple[MapNode, ...]:
    result = []
    for _ in range(r.count(56)):
        start = r.pos
        uid, x, y, z, w, a, b, c, backward, forward, flags = r.read('Q3i4fQQI')
        if not uid or not all(math.isfinite(v) for v in (w, a, b, c)):
            raise SectorFormatError(f'Invalid node at offset {start}')
        result.append(MapNode(uid, start, r.data[start:r.pos], (x / 256, y / 256, z / 256),
                              (w, a, b, c), backward, forward, flags))
    if len({n.uid for n in result}) != len(result):
        raise SectorFormatError('Duplicate node UID')
    return tuple(result)


def _item(r: _Reader, depth: int = 0) -> MapItem:
    if depth > 16:
        raise SectorFormatError('Compound nesting exceeds supported depth')
    start = r.pos
    kind, uid = r.read('IQ')
    bounds = r.read('10f')
    if not uid or not all(math.isfinite(v) for v in bounds) or any(bounds[i] > bounds[i + 5] for i in range(5)):
        raise SectorFormatError(f'Invalid item UID/bounds at offset {start}')
    flags = r.read('I')
    r.skip(1)
    d = {}
    if kind == 4:
        d['model'], d['variant'] = r.read('QQ')
        d['parts'] = r.refs()
        d['nodes'] = r.refs()
        d['slave_count_offset'] = r.pos
        d['slaves'] = r.refs()
        d['slave_insert_offset'] = r.pos
        # This is PrefabSerializer's ferryLinkUid item reference, not Ferry.Port.
        d['ferry'] = r.read('Q')
        d['origin'] = r.read('H')
        if not d['nodes'] or d['origin'] >= len(d['nodes']):
            raise SectorFormatError(f'Invalid prefab origin/nodes at offset {start}')
        r.skip(len(d['nodes']) * 12 + 8)
    elif kind in (7, 0x23):
        d['node'], d['parent'] = r.read('QQ')
        d['nodes'] = r.refs()
    elif kind == 1:  # terrain: 3 railings, 3 vegetation records per side
        r.skip(16 + 24 + 12 + 30)
        r.skip(2 * (26 + 3 * 16 + 4))
        r.array(20)
        _quad(r)
        _quad(r)
        r.skip(32)
    elif kind == 2:
        r.skip(44)
        r.array(4)
    elif kind == 3:  # road flags, profiles, railings, nodes, length
        # KDOP flags belong to the common header, not the four road flags
        # which follow it. Confusing these yields plausible but wrong UI filters.
        d['is_city_road'] = bool(flags & (8 << 16))
        d['show_in_ui_map'] = not bool(flags & (2 << 24))
        d['road_flags'] = r.read('I')
        d['road_type'] = r.read('Q')
        r.skip(8 * 8 + 2 * 12 + 3 * 8 + 6 * 10 + 8)
        d['node'], d['forward_node'] = r.read('QQ')
        d['length'] = r.read('f')
    elif kind == 5:
        r.skip(24)
        r.array(8)
        r.skip(8 + 12 + 8 + 4 + 4)
    elif kind == 6:
        # CompanySerializer: economy-link identity, placed prefab and marker
        # node, then parallel spawn-node and raw flag arrays. Exposing these
        # fields does not infer any new ATS 1.61 vehicle-bit semantics.
        d['city'], d['prefab'], d['company'], d['node'] = r.read('4Q')
        d['spawn_nodes'] = r.refs()
        d['spawn_flags'] = tuple(r.read('I') for _ in d['spawn_nodes'])
    elif kind == 8:
        r.array(8)
    elif kind == 9:
        r.array(8)
        r.skip(40)
        r.array(4)
        r.array(8)
    elif kind == 0x0b:
        r.skip(36)
    elif kind == 0x0c:
        r.skip(24)
    elif kind == 0x0d:
        r.skip(32)
    elif kind == 0x0f:
        r.array(8)
        r.skip(16)
    elif kind == 0x12:
        r.skip(16)
    elif kind == 0x13:
        d['port'] = r.read('Q')
        d['prefab'] = r.read('Q')
        d['node'] = r.read('Q')
        d['unload_offset'] = r.read('3f')
    elif kind == 0x15:
        r.skip(32)
    elif kind == 0x16:
        r.skip(28)
        r.array(8)
    elif kind == 0x17:
        r.array(8)
        r.skip(8)
    elif kind == 0x1c:
        r.skip(28)
        r.array(4)
        r.array(8)
    elif kind == 0x22:
        r.array(8)
        n = r.array(8)
        for _ in range(r.count(12)):
            r.skip(8)
            _action(r)
        if n == 1:
            r.skip(4)
    elif kind == 0x24:
        r.skip(32)
        r.skip(r.read('B') * 24)
        if r.string():
            for _ in range(r.count(9)):
                r.skip(8)
                f = r.read('B')
                if f not in (1, 2, 3):
                    raise SectorFormatError('Unknown sign-board override flags')
                r.skip((2 if f & 1 else 0) + (8 if f & 2 else 0))
            for _ in range(r.count(16)):
                r.skip(12)
                for _ in range(r.count(7)):
                    typ = r.read('H')
                    r.skip(4)
                    if typ == 5:
                        r.string()
                    elif typ in (1, 2, 3, 4, 6):
                        r.skip({1: 1, 2: 4, 3: 4, 4: 4, 6: 8}[typ])
                    else:
                        raise SectorFormatError(f'Unknown sign attribute type {typ}')
    elif kind == 0x25:
        r.skip(24)
    elif kind == 0x26:
        r.array(8)
        r.array(8)
        r.skip(12)
    elif kind == 0x27:
        r.skip(16 * 12 + 4 + 8 + 4 + 3 * 11)
        r.array(20)
        _quad(r)
    elif kind == 0x28:
        d['node'] = r.read('Q')
        d['items'] = _items(r, depth + 1)
        d['compound_node_count_offset'] = r.pos
        d['compound_nodes'] = _nodes(r)
    elif kind == 0x29:
        r.array(8)
        r.skip(8)
        for _ in range(r.count(16)):
            r.skip(12)
            r.array(4)
        r.array(16)
        r.array(8)
    elif kind == 0x2a:
        r.array(8)
        r.skip(4)
    elif kind == 0x2b:
        r.skip(8)
        r.array(20)
        d['child_count_offset'] = r.pos
        d['children'] = r.refs()
        d['child_insert_offset'] = r.pos
        r.array(8)
    elif kind == 0x2c:
        r.skip(36)
        n = r.read('I').bit_count()
        for _ in range(n):
            r.skip(76)
            r.array(4)
            r.skip(20)
    elif kind == 0x2d:
        for _ in range(4):
            r.array(8)
        r.array(40)
        r.skip(4)
    elif kind == 0x2e:
        r.array(8)
        r.skip(8)
        for _ in range(r.count(4)):
            _action(r)
    elif kind == 0x2f:
        r.string()
        r.skip(8)
    elif kind == 0x30:
        d['node'] = r.read('Q')
        r.skip(8)
        d['child_count_offset'] = r.pos
        d['children'] = r.refs()
        d['child_insert_offset'] = r.pos
    elif kind == 0x31:
        r.skip(8)
        r.array(8)
        for _ in range(2):
            r.string()
            r.skip(4)
    else:
        raise SectorFormatError(f'Unsupported map item type {kind:#x} at offset {start}')
    return MapItem(kind, uid, start, r.pos, flags, d)


def _items(r: _Reader, depth: int = 0) -> tuple[MapItem, ...]:
    items = []
    for _ in range(r.count(57)):
        try:
            items.append(_item(r, depth))
        except SectorFormatError as exc:
            raise SectorFormatError(f'Item {len(items)}: {exc}') from exc
    if len({i.uid for i in items}) != len(items):
        raise SectorFormatError('Duplicate item UID')
    return tuple(items)


def parse_sector(data: bytes) -> Sector:
    """Parse a complete 907 .base or .aux, rejecting unsupported/trailing bytes.

    Exact 28-byte empty legacy sectors (895/901/903) observed in the supplied
    ProMods/Western Canada maps are recognized solely as containing no targets.
    Their nonempty layouts remain unsupported; no serializer conversion occurs.
    """
    if (len(data) == 28 and struct.unpack_from('<I', data)[0] in (895, 901, 903)
            and data[4:] == struct.pack('<QI3I', token('euro2'), 3, 0, 0, 0)):
        return Sector((), (), 20, 24, (), data[24:])
    r = _Reader(data)
    _header(r)
    items = _items(r)
    node_offset = r.pos
    nodes = _nodes(r)
    visibility_offset = r.pos
    children = r.refs()
    if r.pos != len(data):
        raise SectorFormatError(f'Trailing sector bytes at offset {r.pos}')
    if len(set(children)) != len(children):
        raise SectorFormatError('Duplicate visibility child UID')
    return Sector(items, nodes, node_offset, visibility_offset, children, data[visibility_offset:])


def parse_layer(data: bytes) -> dict[int, int]:
    """Read exact .layer membership; layer-zero items need no explicit entry."""
    r = _Reader(data)
    _header(r)
    result = {}
    while True:
        uid = r.read('Q')
        if uid == 0xffffffffffffffff:
            break
        if not uid or uid in result:
            raise SectorFormatError('Invalid/duplicate layer UID')
        result[uid] = r.read('B')
    if r.pos != len(data):
        raise SectorFormatError('Trailing layer data')
    return result


def extend_layer(data: bytes, clones: dict[int, int]) -> bytes:
    """Copy original items' explicit layers to their clones; preserve original bytes."""
    layers = parse_layer(data)
    if any(not 0 < new < 0xffffffffffffffff or new in layers for new in clones.values()):
        raise SectorFormatError('Invalid/colliding generated layer UID')
    if len(set(clones.values())) != len(clones):
        raise SectorFormatError('Duplicate generated layer UID')
    additions = b''.join(struct.pack('<QB', new, layers[old]) for old, new in sorted(clones.items()) if old in layers)
    return data[:-8] + additions + data[-8:]
