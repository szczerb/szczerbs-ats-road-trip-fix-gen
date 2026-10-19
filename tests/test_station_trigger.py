import math
import struct
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.ppd import inspect_ppd
from ats_road_trip.rest_stops import inspect_rest_triggers
from ats_road_trip.station_parking.trigger import append_car_parking_polygon


def descriptor(groups=(), *, version=25, trailer=b'opaque-tail'):
    records = []
    for group_id, action, points, params in groups:
        first = len(records)
        range_value, reset_delay, reset_distance, flags = params
        for i, (x, y, z) in enumerate(points):
            records.append(struct.pack(
                '<IQfffI3f2i', group_id, token(action), range_value,
                reset_delay, reset_distance, flags, x, y, z,
                first + (i - 1) % len(points), first + (i + 1) % len(points),
            ))
    control = bytes((i * 13) % 256 for i in range(208))
    trigger_start = 304
    trigger_end = trigger_start + 48 * len(records)
    h = [0] * 24
    h[0], h[1], h[9] = version, 2, len(records)
    h[12:24] = [96] + [trigger_start] * 9 + [trigger_end, trigger_end]
    return struct.pack('<24I', *h) + control + b''.join(records) + trailer


CAR_POLYGON = [(100.1, 0.3, 200.2), (106.2, 0.3, 200.2),
               (106.2, 0.3, 204.4), (100.1, 0.3, 204.4)]


class StationTriggerTests(unittest.TestCase):
    def test_appends_native_car_polygon_and_preserves_every_original_byte(self):
        original = descriptor(((7, 'hud_parking', [(0., 0., 0.), (8., 0., 0.),
                                                     (8., 0., 6.), (0., 0., 6.)],
                                 (3., 0., 0., 0)),))
        before = inspect_ppd(original)
        old_header = struct.unpack_from('<24I', original)
        old_trigger_bytes = original[old_header[21]:old_header[22]]
        result, report = append_car_parking_polygon(original, CAR_POLYGON)
        new_header = struct.unpack_from('<24I', result)
        extra_size = len(CAR_POLYGON) * 48

        self.assertEqual(new_header[9], old_header[9] + len(CAR_POLYGON))
        self.assertEqual(new_header[22], old_header[22] + extra_size)
        self.assertEqual(new_header[23], old_header[23] + extra_size)
        self.assertEqual(result[96:old_header[22]], original[96:old_header[22]])
        self.assertEqual(result[old_header[22] + extra_size:], original[old_header[22]:])
        self.assertEqual(result[old_header[21]:old_header[22]], old_trigger_bytes)
        self.assertEqual(report['action'], 'parking_car')
        self.assertEqual(report['group_id'], 0)
        self.assertTrue(report['source_trigger_records_preserved'])

        car = next(group for group in inspect_rest_triggers(result)
                   if group['id'] == report['group_id'] and group['action'] == token('parking_car'))
        rounded_vertices = {struct.unpack('<3f', struct.pack('<3f', *point))
                            for point in CAR_POLYGON}
        self.assertEqual(set(car['vertices']), rounded_vertices)
        first_new = old_header[9]
        for i in range(len(CAR_POLYGON)):
            record = struct.unpack_from('<IQfffI3f2i', result, new_header[21] + 48 * (first_new + i))
            self.assertEqual(record[:6], (0, token('parking_car'), 3.0, 0.0, 0.0, 0))
            self.assertEqual(record[-2:], (first_new + (i - 1) % 4, first_new + (i + 1) % 4))
        self.assertEqual(before['trigger_count'], old_header[9])

    def test_non_rest_trigger_groups_are_retained(self):
        other = [(20., 0., 20.), (23., 0., 20.), (23., 0., 22.)]
        original = descriptor(((4, 'weight_check', other, (2., 1., 0.5, 4)),))
        result, report = append_car_parking_polygon(original, CAR_POLYGON)
        groups = inspect_rest_triggers(result, actions={token('weight_check'), token('parking_car')})
        self.assertEqual([g['action'] for g in groups], [token('weight_check'), token('parking_car')])
        self.assertEqual(set(groups[0]['vertices']), set(other))
        old_end = struct.unpack_from('<24I', original)[22]
        self.assertEqual(result[96:old_end], original[96:old_end])
        self.assertEqual(report['group_id'], 0)

    def test_reuses_only_an_unused_id_and_output_is_reproducible(self):
        existing = ((0, 'hud_parking', [(0., 0., 0.), (1., 0., 0.), (1., 0., 1.)],
                     (3., 0., 0., 0)),)
        original = descriptor(existing)
        result1, report1 = append_car_parking_polygon(original, CAR_POLYGON)
        result2, report2 = append_car_parking_polygon(original, CAR_POLYGON)
        self.assertEqual(result1, result2)
        self.assertEqual(report1, report2)
        self.assertEqual(report1['group_id'], 1)

    def test_rejects_invalid_polygons(self):
        too_many = [(math.cos(i * 2 * math.pi / 65), 0.0,
                     math.sin(i * 2 * math.pi / 65)) for i in range(65)]
        invalid = [
            [(0, 0, 0), (1, 0, 1)],
            [(0, 0, 0), (1, 0, 0), (2, 0, 0)],
            [(0, 0, 0), (2, 0, 2), (0, 0, 2), (2, 0, 0)],
            [(0, 0, 0), (1, 1, 0), (1, 0, 1)],
            [(0, 0, 0), (1, 0, 0), (1, float('nan'), 1)],
            [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 0)],
            [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1), (0, 0, 0)],
            [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1_000_001)],
            [(0, 0, 0), (1, 0, 0), (1, 0.1, 0), (0, 0, 1)],
            [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, True, 1)],
            too_many,
        ]
        for vertices in invalid:
            with self.subTest(vertices=vertices), self.assertRaises(ValueError):
                append_car_parking_polygon(descriptor(), vertices)

    def test_rejects_unsupported_or_malformed_descriptors(self):
        with self.assertRaisesRegex(ValueError, 'v25'):
            append_car_parking_polygon(descriptor(version=24), CAR_POLYGON)
        malformed = bytearray(descriptor())
        struct.pack_into('<I', malformed, 21 * 4, 301)
        with self.assertRaises(ValueError):
            append_car_parking_polygon(bytes(malformed), CAR_POLYGON)

        broken = bytearray(descriptor(((3, 'weight_check',
                                       [(0., 0., 0.), (1., 0., 0.), (1., 0., 1.)],
                                       (3., 0., 0., 0)),)))
        h = struct.unpack_from('<24I', broken)
        struct.pack_into('<i', broken, h[21] + 40, 999)
        with self.assertRaisesRegex(ValueError, 'neighbor'):
            append_car_parking_polygon(bytes(broken), CAR_POLYGON)


if __name__ == '__main__':
    unittest.main()
