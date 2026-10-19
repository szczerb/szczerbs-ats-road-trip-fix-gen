"""Strict bounded reader for ConverterPIX text PIM version-5 station models.

This is an independent parser for a narrow observed syntax subset. It does not
execute Blender, evaluate source text, or transform coordinates into PPD space.
"""
from __future__ import annotations

import math
import re
import struct

_MAX_TEXT = 32 * 1024 * 1024
_MAX_TOKENS = 8_000_000
_MAX_BLOCKS = 200_000
_MAX_VERTICES = 1_000_000
_MAX_TRIANGLES = 1_000_000
_MAX_MATERIALS = 4096
_MAX_PIECES = 4096
_MAX_PARTS = 4096
_MAX_LOCATORS = 65536
_TOKEN_RE = re.compile(r'\s+|"(?:\\.|[^"\\])*"|&[0-9a-fA-F]+|[A-Za-z_][A-Za-z0-9_.-]*|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[{}():]')
_NUMBER_RE = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z')
_IDENT_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_.-]*\Z')


class StationMeshError(ValueError):
    """Malformed or unsupported ConverterPIX PIM text."""


class _Block:
    __slots__ = ('name', 'fields', 'children', 'rows')

    def __init__(self, name):
        self.name = name
        self.fields = {}
        self.children = []
        self.rows = []


def _unquote(token: str) -> str:
    body = token[1:-1]
    out = []
    i = 0
    while i < len(body):
        char = body[i]
        if char != '\\':
            out.append(char)
            i += 1
            continue
        i += 1
        if i >= len(body) or body[i] not in ('\\', '"'):
            raise StationMeshError('Unsupported string escape in PIM text')
        out.append(body[i])
        i += 1
    return ''.join(out)


def _atom(token: str):
    if token.startswith('"'):
        return _unquote(token)
    if token.startswith('&'):
        digits = token[1:]
        if len(digits) != 8:
            raise StationMeshError('PIM hexadecimal float must contain exactly eight digits')
        # PIM prints the IEEE-754 word as conventional hexadecimal digits;
        # interpreting those digits as a byte sequence reverses the value.
        value = struct.unpack('<f', struct.pack('<I', int(digits, 16)))[0]
        if not math.isfinite(value):
            raise StationMeshError('PIM contains a nonfinite hexadecimal float')
        return value
    if _NUMBER_RE.fullmatch(token):
        value = float(token) if any(c in token for c in '.eE') else int(token)
        if isinstance(value, float) and not math.isfinite(value):
            raise StationMeshError('PIM contains a nonfinite number')
        return value
    if _IDENT_RE.fullmatch(token):
        return token
    raise StationMeshError(f'Unsupported PIM token {token!r}')


def _line_tokens(line: str, number: int) -> list[str]:
    tokens = []
    cursor = 0
    while cursor < len(line):
        match = _TOKEN_RE.match(line, cursor)
        if not match:
            raise StationMeshError(f'Unsupported character on PIM line {number}')
        token = match.group(0)
        cursor = match.end()
        if token.isspace():
            continue
        tokens.append(token)
        if len(tokens) > 128:
            raise StationMeshError(f'Too many tokens on PIM line {number}')
    return tokens


def _parse_value(tokens: list[str], line: int):
    if not tokens:
        return []
    if tokens[0] == '(':
        if tokens[-1] != ')':
            raise StationMeshError(f'Malformed tuple on PIM line {line}')
        values = [_atom(t) for t in tokens[1:-1] if t != ',']
        if len(values) != len(tokens[1:-1]):
            raise StationMeshError(f'Unexpected punctuation in tuple on PIM line {line}')
        return tuple(values)
    values = [_atom(t) for t in tokens]
    return values[0] if len(values) == 1 else values


def _parse_blocks(text: str) -> list[_Block]:
    roots = []
    stack: list[_Block] = []
    token_count = 0
    block_count = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        tokens = _line_tokens(line, line_number)
        token_count += len(tokens)
        if token_count > _MAX_TOKENS:
            raise StationMeshError('PIM token limit exceeded')
        if not tokens:
            continue
        if tokens == ['}']:
            if not stack:
                raise StationMeshError(f'Unmatched closing brace on PIM line {line_number}')
            stack.pop()
            continue
        if len(tokens) == 2 and _IDENT_RE.fullmatch(tokens[0]) and tokens[1] == '{':
            node = _Block(tokens[0])
            (stack[-1].children if stack else roots).append(node)
            stack.append(node)
            block_count += 1
            if block_count > _MAX_BLOCKS or len(stack) > 12:
                raise StationMeshError('PIM block/depth limit exceeded')
            continue
        if not stack:
            raise StationMeshError(f'Unexpected content outside a PIM block on line {line_number}')
        node = stack[-1]
        if len(tokens) >= 2 and tokens[1] == ':':
            if not _IDENT_RE.fullmatch(tokens[0]) or tokens[0] in node.fields:
                raise StationMeshError(f'Duplicate or malformed PIM field on line {line_number}')
            node.fields[tokens[0]] = _parse_value(tokens[2:], line_number)
        elif len(tokens) >= 3 and tokens[1] == '(' and tokens[-1] == ')':
            row_index = _atom(tokens[0])
            if not isinstance(row_index, int) or row_index < 0:
                raise StationMeshError(f'Malformed indexed PIM row on line {line_number}')
            values = _parse_value(tokens[1:], line_number)
            if not isinstance(values, tuple):
                raise StationMeshError(f'Malformed PIM row tuple on line {line_number}')
            node.rows.append((row_index, values))
        else:
            raise StationMeshError(f'Unsupported PIM statement on line {line_number}')
    if stack:
        raise StationMeshError('Unclosed PIM block')
    return roots


def _required(block: _Block, key: str):
    if key not in block.fields:
        raise StationMeshError(f'{block.name} is missing required field {key}')
    return block.fields[key]


def _fields_only(block: _Block, allowed: set[str]) -> None:
    if set(block.fields) != allowed:
        raise StationMeshError(f'{block.name} has missing or unsupported fields')


def _no_rows(block: _Block) -> None:
    if block.rows:
        raise StationMeshError(f'{block.name} contains unexpected indexed rows')


def _count(value, label: str, cap: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > cap:
        raise StationMeshError(f'Invalid or excessive {label}')
    return value


def _one_child(block: _Block, name: str, required: bool = True):
    found = [child for child in block.children if child.name == name]
    if len(found) > 1 or (required and not found):
        raise StationMeshError(f'{block.name} must contain exactly one {name} block')
    return found[0] if found else None


def _float_tuple(value, size: int, label: str) -> tuple[float, ...]:
    if not isinstance(value, tuple) or len(value) != size:
        raise StationMeshError(f'{label} must contain {size} numeric values')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in value):
        raise StationMeshError(f'{label} contains a nonfinite or nonnumeric value')
    return tuple(float(v) for v in value)


def read_station_mesh(text: str) -> dict:
    """Read a bounded PIM v5 Model and return material, mesh, part and locator data.

    Position and locator coordinates are returned exactly in the source's
    ConverterPIX XYZ ordering. No PPD/prefab transform or axis remapping is
    applied; callers must establish their coordinate relationship separately.
    """
    if not isinstance(text, str) or len(text) > _MAX_TEXT:
        raise StationMeshError('PIM input must be text within the 32 MiB limit')
    roots = _parse_blocks(text)
    named: dict[str, list[_Block]] = {}
    for root in roots:
        named.setdefault(root.name, []).append(root)
    if len(named.get('Header', [])) != 1 or len(named.get('Global', [])) != 1:
        raise StationMeshError('PIM requires exactly one Header and Global block')
    allowed_roots = {'Header', 'Global', 'Material', 'Piece', 'Part', 'Locator'}
    if set(named) - allowed_roots:
        raise StationMeshError('Unsupported top-level PIM block')
    header, global_block = named['Header'][0], named['Global'][0]
    _fields_only(header, {'FormatVersion', 'Source', 'Type', 'Name'})
    _fields_only(global_block, {'VertexCount', 'TriangleCount', 'MaterialCount',
                                'PieceCount', 'PartCount', 'BoneCount',
                                'LocatorCount', 'Skeleton'})
    _no_rows(header)
    _no_rows(global_block)
    if header.children or global_block.children:
        raise StationMeshError('Header and Global blocks cannot contain nested blocks')
    if _required(header, 'Type') != 'Model' or _required(header, 'FormatVersion') != 5:
        raise StationMeshError('Only PIM FormatVersion 5 Type Model is supported')
    counts = {
        'vertices': _count(_required(global_block, 'VertexCount'), 'vertex count', _MAX_VERTICES),
        'triangles': _count(_required(global_block, 'TriangleCount'), 'triangle count', _MAX_TRIANGLES),
        'materials': _count(_required(global_block, 'MaterialCount'), 'material count', _MAX_MATERIALS),
        'pieces': _count(_required(global_block, 'PieceCount'), 'piece count', _MAX_PIECES),
        'parts': _count(_required(global_block, 'PartCount'), 'part count', _MAX_PARTS),
        'bones': _count(_required(global_block, 'BoneCount'), 'bone count', 0),
        'locators': _count(_required(global_block, 'LocatorCount'), 'locator count', _MAX_LOCATORS),
    }
    material_blocks = named.get('Material', [])
    if len(material_blocks) != counts['materials']:
        raise StationMeshError('MaterialCount disagrees with Material blocks')
    materials = []
    aliases = set()
    for block in material_blocks:
        _fields_only(block, {'Alias', 'Effect'})
        _no_rows(block)
        if block.children:
            raise StationMeshError('Material block contains unsupported nested data')
        alias, effect = _required(block, 'Alias'), _required(block, 'Effect')
        if not isinstance(alias, str) or not isinstance(effect, str) or alias in aliases:
            raise StationMeshError('Malformed or duplicate material alias/effect')
        aliases.add(alias)
        materials.append({'alias': alias, 'effect': effect})

    piece_blocks = named.get('Piece', [])
    if len(piece_blocks) != counts['pieces']:
        raise StationMeshError('PieceCount disagrees with Piece blocks')
    pieces = []
    vertex_total = triangle_total = 0
    seen_piece_indices = set()
    for block in piece_blocks:
        _fields_only(block, {'Index', 'Material', 'VertexCount', 'TriangleCount', 'StreamCount'})
        _no_rows(block)
        if any(child.name not in {'Stream', 'Triangles'} for child in block.children):
            raise StationMeshError('Piece contains an unsupported nested block')
        index = _count(_required(block, 'Index'), 'piece index', _MAX_PIECES - 1)
        material_index = _count(_required(block, 'Material'), 'piece material index', _MAX_MATERIALS - 1)
        vertex_count = _count(_required(block, 'VertexCount'), 'piece vertex count', _MAX_VERTICES)
        triangle_count = _count(_required(block, 'TriangleCount'), 'piece triangle count', _MAX_TRIANGLES)
        stream_count = _count(_required(block, 'StreamCount'), 'stream count', 64)
        if index in seen_piece_indices or material_index >= len(materials):
            raise StationMeshError('Duplicate piece index or out-of-range material index')
        seen_piece_indices.add(index)
        stream_blocks = [child for child in block.children if child.name == 'Stream']
        if len(stream_blocks) != stream_count:
            raise StationMeshError('StreamCount disagrees with Stream blocks')
        streams = {}
        for stream in stream_blocks:
            stream_fields = set(stream.fields)
            if stream_fields not in ({'Format', 'Tag'},
                                     {'Format', 'Tag', 'AliasCount', 'Aliases'}):
                raise StationMeshError('Stream has missing or unsupported fields')
            if 'AliasCount' in stream_fields:
                alias_count = _count(stream.fields['AliasCount'], 'stream alias count', 64)
                aliases_value = stream.fields['Aliases']
                aliases = aliases_value if isinstance(aliases_value, list) else [aliases_value]
                if len(aliases) != alias_count or any(not isinstance(alias, str) for alias in aliases):
                    raise StationMeshError('Stream AliasCount disagrees with Aliases')
            if stream.children:
                raise StationMeshError('Stream contains unsupported nested blocks')
            fmt, tag = _required(stream, 'Format'), _required(stream, 'Tag')
            widths = {'FLOAT': 1, 'FLOAT2': 2, 'FLOAT3': 3, 'FLOAT4': 4}
            if fmt not in widths or not isinstance(tag, str) or tag in streams:
                raise StationMeshError('Unsupported or duplicate vertex stream')
            width = widths[fmt]
            if len(stream.rows) != vertex_count:
                raise StationMeshError(f'{tag} stream row count disagrees with VertexCount')
            values = []
            for expected, (row_index, row) in enumerate(stream.rows):
                if row_index != expected:
                    raise StationMeshError(f'{tag} stream indices are not contiguous')
                vector = _float_tuple(row, width, f'{tag} stream row')
                values.append(vector[0] if width == 1 else vector)
            streams[tag] = values
        positions = streams.get('_POSITION')
        if positions is None or next((s.fields.get('Format') for s in stream_blocks
                                      if s.fields.get('Tag') == '_POSITION'), None) != 'FLOAT3':
            raise StationMeshError('Each piece requires one FLOAT3 _POSITION stream')
        if '_UV0' in streams and next(s.fields.get('Format') for s in stream_blocks
                                      if s.fields.get('Tag') == '_UV0') != 'FLOAT2':
            raise StationMeshError('_UV0 must use FLOAT2 format')
        triangle_block = _one_child(block, 'Triangles')
        _fields_only(triangle_block, set())
        if triangle_block.children:
            raise StationMeshError('Triangles block contains nested blocks')
        if len(triangle_block.rows) != triangle_count:
            raise StationMeshError('TriangleCount disagrees with triangle rows')
        triangles = []
        for expected, (row_index, row) in enumerate(triangle_block.rows):
            if row_index != expected or len(row) != 3:
                raise StationMeshError('Malformed or noncontiguous triangle row')
            triangle = tuple(row)
            if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 or v >= vertex_count for v in triangle):
                raise StationMeshError('Triangle vertex index is out of bounds')
            triangles.append(triangle)
        piece_streams = {'_POSITION': positions}
        if '_UV0' in streams:
            piece_streams['_UV0'] = streams['_UV0']
        pieces.append({'index': index, 'material_index': material_index,
                       'material': materials[material_index]['alias'],
                       'vertex_count': vertex_count, 'triangle_count': triangle_count,
                       'positions': positions, 'uv0': streams.get('_UV0'),
                       'streams': piece_streams,
                       'triangles': triangles})
        vertex_total += vertex_count
        triangle_total += triangle_count
    if seen_piece_indices != set(range(counts['pieces'])):
        raise StationMeshError('Piece indices must be contiguous from zero')
    if vertex_total != counts['vertices'] or triangle_total != counts['triangles']:
        raise StationMeshError('Global mesh totals disagree with piece totals')
    pieces.sort(key=lambda piece: piece['index'])

    part_blocks = named.get('Part', [])
    if len(part_blocks) != counts['parts']:
        raise StationMeshError('PartCount disagrees with Part blocks')
    parts = []
    for part in part_blocks:
        _fields_only(part, {'Name', 'PieceCount', 'LocatorCount', 'Pieces', 'Locators'})
        _no_rows(part)
        if part.children:
            raise StationMeshError('Part contains unsupported nested blocks')
        name = _required(part, 'Name')
        piece_count = _count(_required(part, 'PieceCount'), 'part piece count', _MAX_PIECES)
        locator_count = _count(_required(part, 'LocatorCount'), 'part locator count', _MAX_LOCATORS)
        part_pieces = _required(part, 'Pieces')
        part_locators = _required(part, 'Locators')
        if isinstance(part_pieces, int):
            part_pieces = [part_pieces]
        if isinstance(part_locators, int):
            part_locators = [part_locators]
        if not isinstance(part_pieces, list) or len(part_pieces) != piece_count:
            raise StationMeshError('Part Pieces count disagrees with PieceCount')
        if not isinstance(part_locators, list) or len(part_locators) != locator_count:
            raise StationMeshError('Part Locators count disagrees with LocatorCount')
        if (any(not isinstance(i, int) or i < 0 or i >= counts['pieces'] for i in part_pieces)
                or any(not isinstance(i, int) or i < 0 or i >= counts['locators'] for i in part_locators)):
            raise StationMeshError('Part membership references an out-of-range index')
        parts.append({'name': name, 'pieces': part_pieces, 'locators': part_locators})

    locator_blocks = named.get('Locator', [])
    if len(locator_blocks) != counts['locators']:
        raise StationMeshError('LocatorCount disagrees with Locator blocks')
    locators = []
    locator_indices = set()
    assigned_pieces, assigned_locators = [], []
    for part in parts:
        assigned_pieces.extend(part['pieces'])
        assigned_locators.extend(part['locators'])
    if (sorted(assigned_pieces) != list(range(counts['pieces']))
            or sorted(assigned_locators) != list(range(counts['locators']))):
        raise StationMeshError('Part memberships must assign every piece and locator exactly once')

    for block in locator_blocks:
        _fields_only(block, {'Name', 'Hookup', 'Index', 'Position', 'Rotation', 'Scale'})
        _no_rows(block)
        if block.children:
            raise StationMeshError('Locator contains unsupported nested blocks')
        name = _required(block, 'Name')
        hookup = _required(block, 'Hookup')
        index = _count(_required(block, 'Index'), 'locator index', _MAX_LOCATORS - 1)
        if not isinstance(name, str) or not isinstance(hookup, str) or index in locator_indices:
            raise StationMeshError('Malformed or duplicate locator metadata')
        locator_indices.add(index)
        locators.append({'name': name, 'hookup': hookup, 'index': index,
                         'position': _float_tuple(_required(block, 'Position'), 3, 'Locator Position'),
                         'rotation': _float_tuple(_required(block, 'Rotation'), 4, 'Locator Rotation'),
                         'scale': _float_tuple(_required(block, 'Scale'), 3, 'Locator Scale')})
    if locator_indices != set(range(counts['locators'])):
        raise StationMeshError('Locator indices must be contiguous from zero')
    locators.sort(key=lambda item: item['index'])
    return {'format_version': 5, 'name': _required(header, 'Name'),
            'source': _required(header, 'Source'), 'coordinate_order': ('x', 'y', 'z'),
            'coordinate_transform_applied': False, 'counts': counts,
            'materials': materials, 'pieces': pieces, 'parts': parts, 'locators': locators}


def sample_surface_height(mesh: dict, xz: tuple[float, float], allowed_materials) -> float:
    """Return the top height under prefab-local XZ for selected material aliases.

    Vertical/edge-on triangles are ignored. If selected surfaces under the
    query differ in height by more than 0.5 units, the query is ambiguous and
    raises instead of guessing which lot surface the user intended.
    """
    if not isinstance(xz, (tuple, list)) or len(xz) != 2:
        raise ValueError('Surface query requires an (x, z) coordinate')
    try:
        x, z = (float(value) for value in xz)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('Surface query coordinates must be finite') from exc
    if not math.isfinite(x) or not math.isfinite(z):
        raise ValueError('Surface query coordinates must be finite')
    allowed = set(allowed_materials)
    if not allowed:
        raise ValueError('At least one explicit surface material alias is required')
    heights = []
    for piece in mesh.get('pieces', []):
        if piece.get('material') not in allowed:
            continue
        positions = piece['positions']
        for triangle in piece['triangles']:
            a, b, c = (positions[i] for i in triangle)
            denominator = ((b[2] - c[2]) * (a[0] - c[0])
                           + (c[0] - b[0]) * (a[2] - c[2]))
            if abs(denominator) < 1e-10:
                continue
            wa = ((b[2] - c[2]) * (x - c[0])
                  + (c[0] - b[0]) * (z - c[2])) / denominator
            wb = ((c[2] - a[2]) * (x - c[0])
                  + (a[0] - c[0]) * (z - c[2])) / denominator
            wc = 1.0 - wa - wb
            if min(wa, wb, wc) >= -1e-9:
                heights.append(wa * a[1] + wb * b[1] + wc * c[1])
    if not heights:
        raise ValueError('No selected nonvertical triangle covers the query point')
    if max(heights) - min(heights) > 0.5:
        raise ValueError('Selected surface triangles disagree in height by more than 0.5 units')
    return max(heights)
