"""Structural tests use tiny authored byte layouts, never redistributed map assets."""
import struct
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import (SectorFormatError, extend_layer, parse_layer,
                                     parse_sector)


HEADER = struct.pack('<IQI', 907, token('euro2'), 3)


def refs(*uids):
    return struct.pack('<I', len(uids)) + b''.join(struct.pack('<Q', u) for u in uids)


def item(kind, uid, payload=b'', flags=0x80000000):
    return struct.pack('<IQ10fIB', kind, uid, *([0.] * 5 + [10.] * 5), flags, 4) + payload


def node(uid, forward=0):
    return struct.pack('<Q3i4fQQI', uid, 256, -512, 768, 1., 0., 0., 0., 0, forward, 0)


def prefab(uid=100):
    return item(4, uid, struct.pack('<QQ', token('02003'), 0) + refs(token('part_a'), token('part_b'))
                + refs(11, 12, 13, 14) + refs(200, 201, 202)
                + struct.pack('<QH', 0, 2) + bytes(4 * 12 + 8))


def sector(items, nodes=(), children=()):
    return (HEADER + struct.pack('<I', len(items)) + b''.join(items)
            + struct.pack('<I', len(nodes)) + b''.join(nodes) + refs(*children))


class SectorReaderTests(unittest.TestCase):
    def test_company_identity_prefab_marker_and_raw_spawn_flags(self):
        payload = (struct.pack('<4Q', token('helena'), 100, token('shop'), 300)
                   + refs(301, 302) + struct.pack('<2I', 0, 0xf1234567))
        company = item(6, 200, payload)
        data = sector([company, prefab()], [node(300, 200)])
        parsed = parse_sector(data)
        self.assertEqual(parsed.companies[0].details,
                         {'city': token('helena'), 'prefab': 100,
                          'company': token('shop'), 'node': 300,
                          'spawn_nodes': (301, 302), 'spawn_flags': (0, 0xf1234567)})
        self.assertEqual(data[parsed.companies[0].offset:parsed.companies[0].end], company)
        self.assertEqual(parsed.prefabs[0].uid, 100)

    def test_company_parallel_spawn_arrays_require_all_flag_words(self):
        payload = struct.pack('<4Q', 0, 0, 0, 0) + refs(1, 2) + struct.pack('<I', 7)
        with self.assertRaises(SectorFormatError):
            parse_sector(sector([item(6, 200, payload)]))

    def test_variable_prefab_and_service_refs_and_visibility(self):
        p = prefab()
        service = item(7, 200, struct.pack('<QQ', 15, 100) + refs(16, 17))
        vis = item(0x30, 400, struct.pack('<Qff', 18, 100., 200.) + refs(100, 200))
        data = sector([p, service, vis], [node(15, 200), node(11)], (100, 200))
        result = parse_sector(data)
        self.assertEqual((result.item_count, result.node_count), (3, 2))
        self.assertEqual(result.node_count_offset, 20 + len(p) + len(service) + len(vis))
        self.assertEqual(result.visibility_children, (100, 200))
        self.assertEqual(result.suffix, refs(100, 200))
        parsed = result.prefabs[0]
        self.assertEqual((parsed.offset, parsed.end), (20, 20 + len(p)))
        self.assertEqual(parsed.details['nodes'], (11, 12, 13, 14))
        self.assertEqual(parsed.details['parts'], (token('part_a'), token('part_b')))
        self.assertEqual(parsed.details['slaves'], (200, 201, 202))
        self.assertEqual(parsed.details['origin'], 2)
        self.assertEqual(struct.unpack_from('<I', data, parsed.details['slave_count_offset'])[0], 3)
        self.assertEqual(result.services[0].details, {'node': 15, 'parent': 100, 'nodes': (16, 17)})
        self.assertEqual(result.nodes[0].raw, node(15, 200))
        self.assertEqual(result.nodes[0].position, (1., -2., 3.))
        self.assertEqual(result.nodes[0].rotation, (1., 0., 0., 0.))
        self.assertEqual(result.items[2].details['children'], (100, 200))

    def test_compound_is_scoped_not_discovered_as_root_fuel(self):
        nested = item(0x23, 99, struct.pack('<QQ', 15, 100) + refs())
        compound = item(0x28, 400, struct.pack('<Q', 12) + struct.pack('<I', 1)
                        + nested + struct.pack('<I', 1) + node(15, 99))
        result = parse_sector(sector([compound]))
        self.assertEqual(result.services, ())
        self.assertEqual(result.items[0].details['items'][0].kind, 0x23)
        self.assertEqual(result.items[0].details['compound_nodes'][0].uid, 15)

    def test_sign_strings_and_typed_overrides_are_consumed(self):
        # Template has two board overrides and six attribute widths.
        payload = bytes(32) + b'\0' + struct.pack('<Q', 4) + b'test'
        payload += struct.pack('<I', 2) + struct.pack('<QBbb', 1, 1, -1, 2) + struct.pack('<QBQ', 2, 2, 3)
        payload += struct.pack('<IIQI', 1, 42, 9, 6)
        for typ, raw in [(1, b'x'), (2, bytes(4)), (3, bytes(4)), (4, bytes(4)),
                         (5, struct.pack('<Q', 3) + b'abc'), (6, bytes(8))]:
            payload += struct.pack('<HI', typ, 0) + raw
        result = parse_sector(sector([item(0x24, 30, payload), prefab()]))
        self.assertEqual([i.kind for i in result.items], [0x24, 4])

    def test_unknown_item_fails_instead_of_scanning_embedded_prefab(self):
        with self.assertRaisesRegex(SectorFormatError, 'Unsupported map item type'):
            parse_sector(sector([item(0x77, 5, prefab())]))

    def test_truncated_inputs_all_fail(self):
        data = sector([prefab(), item(7, 200, struct.pack('<QQ', 15, 100) + refs())], [node(15, 200)])
        for length in range(len(data)):
            with self.subTest(length=length), self.assertRaises(SectorFormatError):
                parse_sector(data[:length])

    def test_count_version_duplicate_uid_bounds_and_trailing_rejected(self):
        data = sector([prefab()], [node(11)])
        for offset, replacement in [(0, struct.pack('<I', 906)), (16, struct.pack('<I', 1000000)),
                                    (20 + 12, struct.pack('<f', float('nan')))]:
            corrupted = bytearray(data)
            corrupted[offset:offset + len(replacement)] = replacement
            with self.assertRaises(SectorFormatError):
                parse_sector(bytes(corrupted))
        for invalid in [data + b'x', sector([prefab(), prefab()]), sector([], [node(11), node(11)]),
                        sector([], [], (42, 42))]:
            with self.assertRaises(SectorFormatError):
                parse_sector(invalid)

    def test_trigger_no_params_marker_and_variable_params(self):
        action1 = struct.pack('<QI', 3, 0xffffffff)
        action2 = (struct.pack('<QIfI', 4, 1, 2., 1) + struct.pack('<Q', 3) + b'abc'
                   + refs(90, 91) + struct.pack('<fI', 1., 0))
        trigger = item(0x22, 30, refs(1) + refs(11) + struct.pack('<I', 2) + action1 + action2 + struct.pack('<f', 10.))
        result = parse_sector(sector([trigger, prefab()]))
        self.assertEqual(result.items[1].uid, 100)

    def test_empty_sector(self):
        self.assertEqual(parse_sector(sector([])).items, ())

    def test_only_exact_empty_observed_legacy_versions_accepted(self):
        empty = sector([])
        for version in (895, 901, 903):
            data = struct.pack('<I', version) + empty[4:]
            self.assertEqual(parse_sector(data).node_count, 0)
            with self.assertRaises(SectorFormatError):
                parse_sector(struct.pack('<I', version) + sector([prefab()])[4:])
        with self.assertRaises(SectorFormatError):
            parse_sector(struct.pack('<I', 999) + empty[4:])


class LayerTests(unittest.TestCase):
    def test_clone_membership_preserves_original_bytes(self):
        layer = HEADER + struct.pack('<QBQB', 100, 2, 200, 7) + b'\xff' * 8
        result = extend_layer(layer, {100: 101, 200: 201, 300: 301})
        self.assertEqual(parse_layer(result), {100: 2, 200: 7, 101: 2, 201: 7})
        self.assertTrue(result.startswith(layer[:-8]))

    def test_empty_and_invalid_layer(self):
        self.assertEqual(parse_layer(HEADER + b'\xff' * 8), {})
        for data in (HEADER, HEADER + b'\xff' * 9,
                     HEADER + struct.pack('<QBQB', 1, 2, 1, 3) + b'\xff' * 8):
            with self.assertRaises(SectorFormatError):
                parse_layer(data)
        with self.assertRaises(SectorFormatError):
            extend_layer(HEADER + struct.pack('<QB', 2, 3) + b'\xff' * 8, {1: 2})


if __name__ == '__main__':
    unittest.main()
