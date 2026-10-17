"""Geometric GAS-to-service matching with origin rotation and ambiguity guards."""

import struct
import unittest

from ats_road_trip.fuel_matching import match_gas_services
from ats_road_trip.map_sector import MapItem, MapNode


def fixture(spawns, *, control=((0.0, 0.0, 10.0), (0.0, 0.0, 0.0)),
            origin=1, order=None, grade=0.0, cross_grade=0.0,
            horizontal_scale=1.0):
    """Build a tiny PPD/sector projection; map service order may be shuffled."""
    count = len(control)
    start = 96
    spawn_start = start + count * 104
    end = spawn_start + len(spawns) * 36
    header = [0] * 24
    header[0], header[1], header[5] = 25, count, len(spawns)
    header[12:24] = [start, spawn_start, spawn_start, spawn_start,
                     spawn_start, end, end, end, end, end, end, end]
    ppd = bytearray(struct.pack('<24I', *header))
    for position in control:
        record = bytearray(104)
        struct.pack_into('<3f', record, 16, *position)
        ppd.extend(record)
    for position, flag in spawns:
        ppd.extend(struct.pack('<3f4fII', *position, 1, 0, 0, 0, 3, flag))

    def place(position):
        dx, dy, dz = (position[i] - control[origin][i] for i in range(3))
        other = control[(origin + 1) % count]
        axis_x, axis_z = other[0] - control[origin][0], other[2] - control[origin][2]
        along = (dx * axis_x + dz * axis_z) / (axis_x * axis_x + axis_z * axis_z) if count > 1 else 0
        return (100 + horizontal_scale * (0.6 * dx + 0.8 * dz),
                5 + dy + along * grade + cross_grade * dz,
                200 + horizontal_scale * (-0.8 * dx + 0.6 * dz))

    node_ids = tuple(200 + i for i in range(count))
    prefab = MapItem(4, 100, 0, 0, 0, {'nodes': node_ids, 'origin': origin})
    nodes = {
        uid: MapNode(uid, 0, b'', place(control[(origin + i) % count]),
                     (1, 0, 0, 0), 0, prefab.uid, 0)
        for i, uid in enumerate(node_ids)
    }
    services = []
    for i, (position, flag) in enumerate(spawns):
        uid, node_uid = 300 + i, 400 + i
        services.append(MapItem(7, uid, 0, 0, 0x80000000 | (0x4000 if flag else 0),
                                {'parent': prefab.uid, 'node': node_uid}))
        nodes[node_uid] = MapNode(node_uid, 0, b'', place(position),
                                  (1, 0, 0, 0), 0, uid, 0)
    if order is not None:
        services = [services[i] for i in order]
    return bytes(ppd), prefab, nodes, services


class FuelMatchingTests(unittest.TestCase):
    def test_four_points_origin_one_and_shuffled_services(self):
        spawns = [((x, 0.02, 2), 0) for x in (-18, -6, 6, 18)]
        ppd, prefab, nodes, services = fixture(spawns, order=(3, 0, 2, 1))
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services),
                         {0: 300, 1: 301, 2: 302, 3: 303})

    def test_mixed_car_truck_same_position(self):
        spawns = [((2, 0, 3), 0), ((2, 0, 3), 1)]
        ppd, prefab, nodes, services = fixture(spawns, order=(1, 0))
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services),
                         {0: 300, 1: 301})

    def test_sloped_prefab_interpolates_service_elevation(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)], grade=0.48)
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services), {0: 300})

    def test_tilted_two_control_prefab_preserves_horizontal_projection(self):
        # Reforma's az63 placement rises 2.94 m over 72 m, shortening its
        # projected horizontal span by roughly 0.058 m.
        control = ((30, 0, 23), (-42, 0, 23))
        ppd, prefab, nodes, services = fixture([((-7.57, 0.155, 8.48), 0)],
                                               control=control, origin=1,
                                               grade=2.9414,
                                               horizontal_scale=0.999186)
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services), {0: 300})

    def test_three_control_prefab_fits_cross_slope(self):
        # Reforma az64's third control lies ~0.84 m off the longitudinal
        # grade. A plane through all three controls places its GAS node.
        control = ((72, 0, 0), (-24, 0, 0), (0, 0, -60))
        ppd, prefab, nodes, services = fixture([((28.24, 0.144, -25.05), 0)],
                                               control=control, origin=0,
                                               cross_grade=-0.014)
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services), {0: 300})

    def test_terrain_cross_slope_has_bounded_vertical_tolerance(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)])
        node = nodes[400]
        x, y, z = node.position
        nodes[400] = MapNode(node.uid, node.offset, node.raw, (x, y + 0.12, z),
                             node.rotation, node.backward, node.forward, node.flags)
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services), {0: 300})
        nodes[400] = MapNode(node.uid, node.offset, node.raw, (x, y + 0.30, z),
                             node.rotation, node.backward, node.forward, node.flags)
        with self.assertRaisesRegex(ValueError, '0 unique fuel matches'):
            match_gas_services(ppd, prefab, nodes, services)

    def test_relaxed_mode_allows_unplaced_car_locator(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0), ((2, 0, 3), 1)])
        with self.assertRaisesRegex(ValueError, 'count/UIDs'):
            match_gas_services(ppd, prefab, nodes, services[:1])
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services[:1],
                                            allow_missing_car=True), {0: 300})

    def test_relaxed_mode_allows_only_exactly_colocated_extra_car_item(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)])
        truck = nodes[400]
        car = MapItem(7, 301, 0, 0, 0x80004000,
                      {'parent': prefab.uid, 'node': 401})
        nodes[401] = MapNode(401, 0, b'', truck.position, truck.rotation, 0, car.uid, 0)
        self.assertEqual(match_gas_services(ppd, prefab, nodes, [*services, car],
                                            allow_missing_car=True), {0: 300})
        x, y, z = truck.position
        nodes[401] = MapNode(401, 0, b'', (x + 0.01, y, z), truck.rotation, 0, car.uid, 0)
        with self.assertRaisesRegex(ValueError, 'not co-located'):
            match_gas_services(ppd, prefab, nodes, [*services, car], allow_missing_car=True)

    def test_relaxed_mode_rejects_unmatched_truck_item(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)])
        extra = MapItem(7, 301, 0, 0, 0x80000000,
                        {'parent': prefab.uid, 'node': 401})
        nodes[401] = MapNode(401, 0, b'', (150, 5, 250), (1, 0, 0, 0), 0, extra.uid, 0)
        with self.assertRaisesRegex(ValueError, 'Unmatched truck'):
            match_gas_services(ppd, prefab, nodes, [*services, extra], allow_missing_car=True)

    def test_prefab_control_node_can_link_backward(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)])
        node = nodes[200]
        nodes[200] = MapNode(node.uid, node.offset, node.raw, node.position,
                             node.rotation, prefab.uid, 999, node.flags)
        self.assertEqual(match_gas_services(ppd, prefab, nodes, services), {0: 300})

    def test_ambiguous_same_mode_duplicate_rejected(self):
        spawns = [((2, 0, 3), 0), ((2, 0, 3), 0)]
        ppd, prefab, nodes, services = fixture(spawns)
        with self.assertRaisesRegex(ValueError, 'unique fuel matches'):
            match_gas_services(ppd, prefab, nodes, services)

    def test_unmatched_service_rejected(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)])
        node = nodes[400]
        nodes[400] = MapNode(node.uid, node.offset, node.raw, (102, 5, 210),
                             node.rotation, node.backward, node.forward, node.flags)
        with self.assertRaisesRegex(ValueError, '0 unique fuel matches'):
            match_gas_services(ppd, prefab, nodes, services)

    def test_single_and_inconsistent_control_nodes_rejected(self):
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)], control=((0, 0, 0),), origin=0)
        with self.assertRaisesRegex(ValueError, 'at least two'):
            match_gas_services(ppd, prefab, nodes, services)
        ppd, prefab, nodes, services = fixture([((2, 0, 3), 0)])
        old = nodes[201]
        nodes[201] = MapNode(old.uid, old.offset, old.raw, (120, 5, 220),
                             old.rotation, old.backward, old.forward, old.flags)
        with self.assertRaisesRegex(ValueError, 'unit rotation'):
            match_gas_services(ppd, prefab, nodes, services)


if __name__ == '__main__':
    unittest.main()
