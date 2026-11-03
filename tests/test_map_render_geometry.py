"""Synthetic map-907/PPD resources exercise the renderer through ZIP mounts."""
from contextlib import ExitStack
import math
import struct
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from ats_road_trip.local_fuel import token
from ats_road_trip.map_render_geometry import GeometryCache, collect_geometry
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.ppd import PpdError, inspect_map_links


DRAW = 'map/usa/sec-0001+0000.base'
NEIGHBOR = 'map/usa/sec+0000+0000.aux'
DEF = 'def/world/prefab.synthetic.sii'
PPD = 'prefab/synthetic.ppd'


def _node(uid, x, z, *, forward=0, backward=0, rotation=(1, 0, 0, 0)):
    return struct.pack('<Q3i4fQQI', uid, x * 256, 0, z * 256, *rotation, backward, forward, 0)


def _item(kind, uid, flags=0):
    return struct.pack('<IQ10fIB', kind, uid, *([0] * 10), flags, 0)


def _road(uid=1, start=2, end=3, *, length=150, hidden=False):
    return (_item(3, uid, (2 << 24) if hidden else 0)
            + struct.pack('<IQ', 0, 0) + bytes(180) + struct.pack('<QQf', start, end, length))


def _prefab(uid=4, first=5, second=6, origin=1):
    return (_item(4, uid) + struct.pack('<QQIIQQIQH', token('test'), 0, 0, 2, first, second, 0, 0, origin)
            + bytes(32))


def _sector(items=(), nodes=()):
    return (struct.pack('<IQII', 907, token('euro2'), 3, len(items)) + b''.join(items)
            + struct.pack('<I', len(nodes)) + b''.join(nodes) + bytes(4))


def _ppd(*, broken_neighbors=False, base_only=False):
    controls = bytearray(208)
    struct.pack_into('<3f', controls, 120, 100, 0, 0)
    points = b''.join([
        struct.pack('<II3f6iI', 14 << 8, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
        struct.pack('<II3f6iI', 0, 0, 50, 0, 25, 0, 0, 0, 0, 0, 0, 1 if broken_neighbors else 2),
        struct.pack('<II3f6iI', 0, 0, 100, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    ])
    # Neighbor slots for the middle point are 0 and 2.
    points = bytearray(points)
    struct.pack_into('<i', points, 48 + 24, 2)
    if base_only:
        for index in range(3):
            struct.pack_into('<I', points, 48 * index + 4, 0x200)
    offsets = [96] + [304] * 8 + [448] * 3
    return struct.pack('<24I', 25, 2, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, *offsets) + controls + points


class MapRenderGeometryTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.mounts = ExitStack()
        self.addCleanup(self.mounts.close)

    def mount(self, name, entries):
        path = self.directory / name
        with ZipFile(path, 'w') as archive:
            for key, value in entries.items():
                archive.writestr(key, value)
        return self.mounts.enter_context(Package(path))

    def test_curve_resolves_across_winning_members_with_hidden_flag(self):
        turn = math.sqrt(.5)
        selected = self.mount('selected.scs', {
            DRAW: _sector((_road(hidden=True),), (_node(2, -25, 100, forward=1),)),
            NEIGHBOR: _sector(nodes=(_node(3, 30, 0, backward=1),)),
        })
        overlay = self.mount('overlay.scs', {
            NEIGHBOR: _sector(nodes=(_node(3, 75, 0, backward=1, rotation=(turn, 0, -turn, 0)),)),
        })
        result = collect_geometry(ResourceStack([selected, overlay]), [DRAW])
        line, = result.lines
        self.assertTrue(line.hidden)
        self.assertFalse(line.approximate)
        self.assertEqual((line.points[0], line.points[-1]), ((-25, 100), (75, 0)))
        midpoint = line.points[len(line.points) // 2]
        self.assertAlmostEqual(midpoint[0], 6.25, places=5)
        self.assertAlmostEqual(midpoint[1], 31.25, places=5)
        self.assertEqual(result.counts['roads_curved'], 1)
        self.assertEqual(result.issues, [])

    def test_approximation_requires_both_reciprocal_endpoints(self):
        selected = self.mount('selected.scs', {
            DRAW: _sector((_road(length=float('nan')), _road(4, 5, 6)),
                          (_node(2, -25, 100, forward=1), _node(5, -40, 100, forward=4))),
            NEIGHBOR: _sector(nodes=(_node(3, 75, 0, backward=1), _node(6, 45, 0, backward=9))),
            'map/other/sec+0000+0000.aux': _sector(nodes=(_node(6, 45, 0, backward=4),)),
        })
        stack = ResourceStack([selected])
        result = collect_geometry(stack, [DRAW], cache=GeometryCache())
        line, = result.lines
        self.assertTrue(line.approximate)
        self.assertEqual(line.points, ((-25, 100), (75, 0)))
        self.assertEqual(result.counts['roads_decoded'], 2)
        self.assertEqual(result.counts['roads_approximated'], 1)
        self.assertEqual(result.counts['roads_omitted'], 1)
        bounded = collect_geometry(stack, [DRAW], context_paths=[])
        self.assertEqual(bounded.counts['roads_omitted'], 2)

    def test_prefab_uses_origin_and_effective_descriptor(self):
        selected = self.mount('selected.scs', {
            DRAW: _sector((_prefab(),), (_node(5, 0, 100, forward=4),)),
            NEIGHBOR: _sector(nodes=(_node(6, 0, 0, backward=4),)),
            DEF: 'SiiNunit\n{\nprefab_model : prefab.test { prefab_desc: "/prefab/wrong.ppd" }\n}',
            PPD: _ppd(broken_neighbors=True),
        })
        overlay = self.mount('overlay.scs', {
            DEF: 'SiiNunit\n{\nprefab_model : prefab.test { prefab_desc: "/prefab/synthetic.ppd" }\n}',
            PPD: _ppd(),
        })
        result = collect_geometry(ResourceStack([selected, overlay]), [DRAW])
        self.assertEqual(result.issues, [])
        self.assertEqual(result.counts['prefab_links'], 2)
        self.assertEqual(result.counts['prefabs_drawn'], 1)
        self.assertEqual([line.points for line in result.lines],
                         [((0, 0), (-25, 50)), ((-25, 50), (0, 100))])
        self.assertEqual(result.prefab_resources, {DEF, PPD})

    def test_malformed_member_and_nonreciprocal_ppd(self):
        invalid = 'map/usa/sec+0001+0001.aux'
        selected = self.mount('selected.scs', {DRAW: _sector(), invalid: b'bad'})
        result = collect_geometry(ResourceStack([selected]), [DRAW, invalid])
        self.assertEqual(result.counts['sector_members_decoded'], 1)
        self.assertEqual(result.counts['sector_members_failed'], 1)
        self.assertEqual(result.issues[0]['path'], invalid)
        self.assertNotIn(str(self.directory), repr(result.issues))
        authored = inspect_map_links(_ppd())
        base = inspect_map_links(_ppd(base_only=True))
        self.assertFalse(authored.base_only)
        self.assertTrue(base.base_only)
        self.assertEqual(authored.edges, base.edges)
        with self.assertRaisesRegex(PpdError, 'Nonreciprocal'):
            inspect_map_links(_ppd(broken_neighbors=True))
