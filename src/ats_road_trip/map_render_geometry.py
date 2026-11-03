"""Extract road centerlines and descriptor map links from an effective ATS stack."""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import combinations
from lzma import LZMAError
import math
from pathlib import Path
from tempfile import mkdtemp
import re
import struct
from zipfile import BadZipFile
from zlib import error as DeflateError

from .archive import Archive
from .fuel_matching import _control_positions
from .local_fuel import token
from .map_sector import MapItem, MapNode, SectorFormatError, parse_sector
from .package import Package, ResourceStack, virtual_path
from .ppd import PpdError, PpdMapLinks, inspect_map_links
from .rest_stops import _placed_vertices
from .sii import parse_units


Point = tuple[float, float]
_MEMBER = r'map/([^/]+)/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)'
_DEF = r'def/world/prefab(?:\.[^/]+)?\.sii'
_PREFETCH_DEF = r'def/world/prefab[^/]*\.(?:sii|sui)'
_READ_ERRORS = (BadZipFile, DeflateError, EOFError, LZMAError, OSError, RuntimeError,
                KeyError, ValueError, struct.error)
_MAX_MEMBER = 64 * 1024 * 1024
_COUNTERS = (
    'roads_decoded', 'roads_curved', 'roads_approximated', 'roads_omitted', 'roads_hidden',
    'prefabs_decoded', 'prefabs_drawn', 'prefabs_omitted', 'prefabs_without_links', 'prefab_links',
    'prefab_base_links', 'prefabs_placed_3d',
    'sector_members_decoded', 'sector_members_failed', 'context_members_failed',
)


@dataclass(frozen=True, slots=True)
class GeometryLine:
    path: str
    uid: int
    kind: str
    points: tuple[Point, ...]
    hidden: bool = False
    approximate: bool = False


@dataclass
class GeometryResult:
    lines: list[GeometryLine] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    issues: list[dict] = field(default_factory=list)
    members: dict[str, dict[str, int]] = field(default_factory=dict)
    prefab_resources: set[str] = field(default_factory=set)


@dataclass(frozen=True, slots=True)
class _PlacedItem:
    item: MapItem
    local_nodes: dict[int, MapNode]


@dataclass(frozen=True, slots=True)
class _Member:
    nodes: dict[int, MapNode]
    items: tuple[_PlacedItem, ...]


@dataclass
class GeometryCache:
    """Retain decoded resources for immutable package mounts within one run."""

    cache_dir: Path | None = None
    _members: dict[tuple[Package, str], _Member | str] = field(default_factory=dict, init=False)
    _descriptors: dict[tuple[Package, str], tuple[bytes, PpdMapLinks] | str] = field(default_factory=dict, init=False)
    _prefetched: set[tuple[Package, str]] = field(default_factory=set, init=False)
    _package_dirs: dict[Package, Path] = field(default_factory=dict, init=False)

    def prefetch(self, stack: ResourceStack, paths: Iterable[str]) -> None:
        grouped = defaultdict(list)
        for path in paths:
            package, _ = stack.resources[path]
            if (package, path) not in self._prefetched:
                grouped[package].append(path)
        for package, names in grouped.items():
            if not package.archive or not package.archive.format.startswith('hashfs'):
                continue
            try:
                if package not in self._package_dirs:
                    # Package accepts a single disk cache root for its lifetime.
                    existing = package._disk_cache_root
                    if existing is None:
                        root = self.cache_dir or Archive._scratch_root().parent / 'geometry-cache'
                        root.mkdir(parents=True, exist_ok=True)
                        existing = Path(mkdtemp(prefix='package-', dir=root))
                    self._package_dirs[package] = existing
                package.prefetch(names, disk_cache=self._package_dirs[package], max_bytes=_MAX_MEMBER)
            except _READ_ERRORS:
                # Individual reads below isolate failures to their virtual member.
                continue
            self._prefetched.update((package, name) for name in names)

    def member(self, stack: ResourceStack, path: str) -> _Member | str:
        if path not in stack.resources:
            return 'missing_sector_member'
        package, _ = stack.resources[path]
        key = package, path
        if key not in self._members:
            try:
                sector = parse_sector(stack.read(path, max_bytes=_MAX_MEMBER))
                nodes = {node.uid: node for node in sector.nodes}
                self._members[key] = _Member(nodes, tuple(_geometry_items(sector.items, nodes)))
            except SectorFormatError as exc:
                # Structural parser errors contain only bounded offsets/types.
                self._members[key] = str(exc)
            except _READ_ERRORS:
                self._members[key] = 'unreadable_sector_member'
        return self._members[key]

    def descriptor(self, stack: ResourceStack, path: str) -> tuple[bytes, PpdMapLinks] | str:
        if path not in stack.resources:
            return 'missing_prefab_descriptor'
        package, _ = stack.resources[path]
        key = package, path
        if key not in self._descriptors:
            try:
                data = stack.read(path)
                self._descriptors[key] = data, inspect_map_links(data)
            except PpdError as exc:
                self._descriptors[key] = str(exc)
            except _READ_ERRORS:
                self._descriptors[key] = 'unreadable_or_unsupported_prefab_descriptor'
        return self._descriptors[key]


def _geometry_items(items, nodes):
    for item in items:
        if item.kind in (3, 4):
            yield _PlacedItem(item, nodes)
        elif item.kind == 0x28:
            scoped = {**nodes, **{node.uid: node for node in item.details['compound_nodes']}}
            yield from _geometry_items(item.details['items'], scoped)


def _resolve_node(uid, owner, direction, local, external) -> MapNode:
    def linked(node):
        if direction == 'either':
            return owner in (node.forward, node.backward)
        return getattr(node, direction) == owner

    if uid in local:
        if linked(local[uid]):
            return local[uid]
        raise ValueError(f'Unlinked local node {uid:#x}')
    candidates = external.get(uid, ())
    matches = [node for node in candidates if linked(node)]
    if not matches:
        raise ValueError(f'Missing linked node {uid:#x}')
    # Byte-identical copies and copies differing only in the other owner's
    # linkage agree on the geometry this item uses.
    if len({(node.position, node.rotation) for node in matches}) != 1:
        raise ValueError(f'Ambiguous linked node {uid:#x}')
    return matches[0]


def _xz(point) -> Point:
    return point[0], point[2]


def _road_tangent(node: MapNode, length: float) -> Point:
    w, x, y, z = node.rotation
    if abs(math.hypot(w, x, y, z) - 1) > 0.001:
        raise ValueError('Endpoint orientation is not a unit quaternion')
    # Quaternion rotation of native local (0, 0, -length), projected to XZ.
    return -2 * length * (x * z + y * w), -length * (1 - 2 * (x * x + y * y))


def _road_curve(start: MapNode, end: MapNode, length: float) -> tuple[Point, ...]:
    """Flatten the native-field Hermite reconstruction to a 0.75-unit tolerance.

    The tangent convention and scale follow the inspected TruckLib road
    interpolation. Control-point subdivision bounds the projected chord error.
    """
    if not math.isfinite(length) or not 0 < length <= 1_000_000:
        raise ValueError('Serialized road length is unusable')
    a, d = _xz(start.position), _xz(end.position)
    ta, td = _road_tangent(start, length), _road_tangent(end, length)
    b = a[0] + ta[0] / 3, a[1] + ta[1] / 3
    c = d[0] - td[0] / 3, d[1] - td[1] / 3
    points = [a]
    pending = [(a, b, c, d, 0)]
    while pending:
        a, b, c, d, depth = pending.pop()
        # The corresponding straight cubic has control points at one- and
        # two-thirds of its chord. Maximum control-point deviation bounds
        # the entire difference via the Bézier convex hull.
        b_error = math.hypot(b[0] - (2*a[0]+d[0])/3, b[1] - (2*a[1]+d[1])/3)
        c_error = math.hypot(c[0] - (a[0]+2*d[0])/3, c[1] - (a[1]+2*d[1])/3)
        if max(b_error, c_error) <= 0.75:
            points.append(d)
            continue
        if depth == 10:
            raise ValueError('Projected curve exceeds subdivision budget')
        ab, bc, cd = _midpoint(a, b), _midpoint(b, c), _midpoint(c, d)
        abc, bcd = _midpoint(ab, bc), _midpoint(bc, cd)
        mid = _midpoint(abc, bcd)
        pending.extend(((mid, bcd, cd, d, depth+1), (a, ab, abc, mid, depth+1)))
    if len(set(points)) == 1:
        raise ValueError('Road has no projected extent')
    return tuple(points)


def _midpoint(a, b):
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2


def _difference(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _spatial_frame(a, b):
    """A right-handed orthonormal frame from two independent spans."""
    normal = _cross(a, b)
    scale = math.hypot(*a)
    area = math.hypot(*normal)
    if scale < 1e-6 or area <= 1e-6 * scale * math.hypot(*b):
        raise ValueError('Three noncollinear controls are required for 3D prefab placement')
    axis_x = tuple(v / scale for v in a)
    axis_z = tuple(v / area for v in normal)
    return axis_x, _cross(axis_z, axis_x), axis_z


def _placed_spatial_vertices(data, item, nodes, vertices):
    """Fit a proper XYZ rotation and verify every reciprocal control point."""
    refs, origin = item.details['nodes'], item.details['origin']
    if len(refs) > 6:
        raise ValueError('3D prefab placement supports up to six controls')
    if len(refs) < 3:
        raise ValueError('Three noncollinear controls are required for 3D prefab placement')
    control = _control_positions(data)
    if len(control) != len(refs) or not 0 <= origin < len(control):
        raise ValueError('Prefab control references/origin disagree with descriptor')

    local = control[origin:] + control[:origin]
    world = [nodes[uid].position for uid in refs]
    local_spans = [_difference(point, local[0]) for point in local]
    world_spans = [_difference(point, world[0]) for point in world]
    # The largest source triangle gives the best-conditioned frame while
    # preserving the native origin as the placement translation.
    a, b = max(combinations(range(1, len(control)), 2),
               key=lambda pair: math.hypot(*_cross(local_spans[pair[0]], local_spans[pair[1]])))
    local_frame = _spatial_frame(local_spans[a], local_spans[b])
    world_frame = _spatial_frame(world_spans[a], world_spans[b])

    def place(point):
        span = _difference(point, local[0])
        components = [sum(x * y for x, y in zip(span, axis)) for axis in local_frame]
        return tuple(world[0][i] + sum(axis[i] * value for axis, value in zip(world_frame, components))
                     for i in range(3))

    if any(math.dist(place(p), q) > 0.05 for p, q in zip(local, world)):
        raise ValueError('Prefab controls fail 3D rigid placement check')
    return [_xz(place(point)) for point in vertices]


def _definitions(stack, cache, models, issues):
    definitions: dict[int, set[tuple[str, str]]] = defaultdict(set)
    if not models:
        return definitions
    cache.prefetch(stack, stack.matching(_PREFETCH_DEF))
    for path in stack.matching(_DEF):
        try:
            units = parse_units(stack.text(path), source=path, include_reader=stack.text)
        except _READ_ERRORS:
            issues.append({'path': path, 'reason': 'unreadable_or_unsupported_prefab_definitions'})
            continue
        for unit in units:
            if unit.kind != 'prefab_model':
                continue
            try:
                model = token(unit.name.removeprefix('prefab.').lower())
                if model in models:
                    descriptor = virtual_path((unit.one('prefab_desc') or '').lstrip('/'))
                    if not descriptor.endswith('.ppd'):
                        raise ValueError('Expected a PPD descriptor')
                    definitions[model].add((path, descriptor))
            except ValueError:
                issues.append({'path': path, 'reason': 'invalid_prefab_definition'})
    descriptors = {descriptor for entries in definitions.values() for _, descriptor in entries
                   if descriptor in stack.resources}
    cache.prefetch(stack, sorted(descriptors))
    return definitions


def collect_geometry(stack: ResourceStack, draw_paths: Iterable[str], *,
                     context_paths: Iterable[str] | None = None,
                     cache: GeometryCache | None = None) -> GeometryResult:
    """Draw selected members and resolve their nodes within the same map namespace.

    Caller-provided context limits the reference search. By default inspect all
    effective base/aux members in each selected namespace. Context items never
    contribute geometry unless explicitly drawn.
    """
    cache = cache if cache is not None else GeometryCache()
    draw = dict.fromkeys(draw_paths)
    namespaces = set()
    for path in draw:
        match = re.fullmatch(_MEMBER, path)
        if match is None or virtual_path(path) != path:
            raise ValueError('Drawing requires virtual base/aux sector member paths')
        namespaces.add(match[1])
    if context_paths is None:
        context_paths = stack.matching(_MEMBER)
    context = sorted(set(draw) | {
        path for path in context_paths
        if (match := re.fullmatch(_MEMBER, path)) and match[1] in namespaces
    })
    result = GeometryResult()
    cache.prefetch(stack, (path for path in draw if path in stack.resources))
    drawn = {path: cache.member(stack, path) for path in draw}
    models = {
        entry.item.details['model'] for member in drawn.values() if isinstance(member, _Member)
        for entry in member.items if entry.item.kind == 4
    }
    definitions = _definitions(stack, cache, models, result.issues)

    needed = defaultdict(set)
    for path, member in drawn.items():
        if not isinstance(member, _Member):
            continue
        namespace = path.split('/')[1]
        for entry in member.items:
            item = entry.item
            refs = ((item.details['node'], item.details['forward_node'])
                    if item.kind == 3 else item.details['nodes'])
            needed[namespace].update(uid for uid in refs if uid not in entry.local_nodes)
    cache.prefetch(stack, (path for path in context
                           if path not in drawn and needed[path.split('/')[1]] and path in stack.resources))
    index = defaultdict(lambda: defaultdict(list))
    context_failed = 0
    for path in context:
        if path in drawn:
            member = drawn[path]
        elif needed[path.split('/')[1]]:
            member = cache.member(stack, path)
        else:
            continue
        if isinstance(member, str):
            if path not in drawn:
                context_failed += 1
                result.issues.append({'path': path, 'reason': member, 'role': 'reference'})
            continue
        namespace = path.split('/')[1]
        required = needed[namespace]
        for uid in member.nodes.keys() & required:
            index[namespace][uid].append(member.nodes[uid])

    totals = Counter(dict.fromkeys(_COUNTERS, 0))
    totals['context_members_failed'] = context_failed
    for path, member in drawn.items():
        counts = Counter()
        if isinstance(member, str):
            counts['sector_members_failed'] += 1
            result.issues.append({'path': path, 'reason': member})
        else:
            counts['sector_members_decoded'] += 1
            external = index[path.split('/')[1]]
            for entry in member.items:
                if entry.item.kind == 3:
                    _emit_road(path, entry, external, counts, result)
                else:
                    _emit_prefab(path, entry, external, counts, result, stack, cache, definitions)
        result.members[path] = dict(counts)
        totals.update(counts)
    result.counts = dict(totals)
    return result


def _emit_road(path, entry, external, counts, result):
    item, local = entry.item, entry.local_nodes
    counts['roads_decoded'] += 1
    hidden = not item.details['show_in_ui_map']
    counts['roads_hidden'] += hidden
    try:
        start = _resolve_node(item.details['node'], item.uid, 'forward', local, external)
        end = _resolve_node(item.details['forward_node'], item.uid, 'backward', local, external)
    except ValueError as exc:
        counts['roads_omitted'] += 1
        result.issues.append({'path': path, 'uid': f'{item.uid:#x}', 'reason': str(exc),
                              'kind': 'road', 'status': 'omitted'})
        return
    try:
        points = _road_curve(start, end, item.details['length'])
    except ValueError as exc:
        endpoints = _xz(start.position), _xz(end.position)
        usable = endpoints[0] != endpoints[1]
        status = 'approximated' if usable else 'omitted'
        counts[f'roads_{status}'] += 1
        result.issues.append({'path': path, 'uid': f'{item.uid:#x}', 'reason': str(exc),
                              'kind': 'road', 'status': status})
        if usable:
            result.lines.append(GeometryLine(path, item.uid, 'road', endpoints, hidden, True))
    else:
        counts['roads_curved'] += 1
        result.lines.append(GeometryLine(path, item.uid, 'road', points, hidden))


def _emit_prefab(path, entry, external, counts, result, stack, cache, definitions):
    item, local = entry.item, entry.local_nodes
    counts['prefabs_decoded'] += 1
    model = item.details['model']
    issue = {'path': path, 'uid': f'{item.uid:#x}', 'kind': 'prefab', 'status': 'omitted',
             'model_token': f'{model:#x}'}
    entries = definitions[model]
    descriptors = {descriptor for _, descriptor in entries}
    try:
        if not descriptors:
            raise ValueError('Missing effective prefab definition')
        if len(descriptors) != 1:
            issue['definitions'] = sorted(path for path, _ in entries)
            issue['descriptors'] = sorted(descriptors)
            raise ValueError('Ambiguous effective prefab definition')
        descriptor = next(iter(descriptors))
        issue['descriptor'] = descriptor
        for definition, _ in entries:
            result.prefab_resources.add(definition)
        parsed = cache.descriptor(stack, descriptor)
        if isinstance(parsed, str):
            raise ValueError(parsed)
        result.prefab_resources.add(descriptor)
        data, links = parsed
        if not links.edges:
            counts['prefabs_without_links'] += 1
            return
        nodes = {uid: _resolve_node(uid, item.uid, 'either', local, external)
                 for uid in item.details['nodes']}
        vertices = [point for link in links.edges for point in link]
        try:
            placed = _placed_vertices(data, item, nodes, vertices)
        except ValueError as planar_error:
            try:
                placed = _placed_spatial_vertices(data, item, nodes, vertices)
            except ValueError as spatial_error:
                raise ValueError(f'{planar_error}; {spatial_error}') from spatial_error
            counts['prefabs_placed_3d'] += 1
    except ValueError as exc:
        counts['prefabs_omitted'] += 1
        result.issues.append({**issue, 'reason': str(exc)})
        return
    counts['prefabs_drawn'] += 1
    for a, b in zip(placed[::2], placed[1::2]):
        result.lines.append(GeometryLine(path, item.uid, 'prefab', (a, b), approximate=links.base_only))
        counts['prefab_links'] += 1
        counts['prefab_base_links'] += links.base_only
