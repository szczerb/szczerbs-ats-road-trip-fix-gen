"""Reviewed area replacement uses authored fixtures, without game resources."""
from copy import deepcopy
import struct
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.rest_stops import inspect_rest_triggers
from ats_road_trip.station_parking.reviewed_areas import replace_reviewed_car_parking_areas
from ats_road_trip.station_parking.trigger import append_car_parking_polygon
from tests.test_station_trigger import descriptor


def rectangle(x0, z0, x1, z1):
    return [(x0, 0.1, z0), (x1, 0.1, z0), (x1, 0.1, z1), (x0, 0.1, z1)]


PREVIOUS = rectangle(1, 1, 4, 7)
AREAS = [
    {'id': 'storefront', 'vertices': rectangle(9, -21.15, 26, -14.7),
     'partial_activation': True},
    {'id': 'roadside', 'vertices': rectangle(-13, 7.25, 10, 9.85),
     'partial_activation': True},
]


def baseline_descriptor():
    return descriptor((
        (0, 'hud_parking', rectangle(30, 0, 38, 6), (3., 0., 0., 0)),
        (7, 'gas', rectangle(-30, -30, -28, -28), (2., 1., .5, 4)),
        (11, 'parking_car', rectangle(40, 40, 45, 48), (5., 2., 3., 0)),
    ), trailer=b'opaque-fuel-spawn-and-tail-data\x00\xff')


class ReviewedAreaTests(unittest.TestCase):
    def setUp(self):
        self.baseline = baseline_descriptor()
        self.current, self.previous = append_car_parking_polygon(self.baseline, PREVIOUS)

    def replace(self, areas=AREAS, *, baseline=None, current=None, previous=PREVIOUS):
        return replace_reviewed_car_parking_areas(
            self.baseline if baseline is None else baseline,
            self.current if current is None else current,
            previous_vertices=previous, areas=areas)

    def test_replaces_one_bay_with_two_named_independent_native_car_groups(self):
        original_areas = deepcopy(AREAS)
        result, report = self.replace()
        h_before = struct.unpack_from('<24I', self.baseline)
        h_after = struct.unpack_from('<24I', result)
        self.assertEqual(h_after[9], h_before[9] + 8)
        self.assertEqual(len(result), len(self.current) + 4 * 48)
        self.assertEqual(report['area_count'], 2)
        self.assertEqual([r['id'] for r in report['areas']], ['storefront', 'roadside'])
        ids = {r['group_id'] for r in report['areas']}
        self.assertEqual(len(ids), 2)
        self.assertFalse(ids & {0, 7, 11})
        groups = inspect_rest_triggers(result)
        appended = [g for g in groups if g['id'] in ids]
        self.assertEqual(len(appended), 2)
        for area, row in zip(AREAS, report['areas']):
            group = next(g for g in appended if g['id'] == row['group_id'])
            self.assertEqual(group['action'], token('parking_car'))
            self.assertEqual(group['flags'], 4)
            self.assertEqual(len(group['indices']), 4)
            expected = {struct.unpack('<3f', struct.pack('<3f', *p)) for p in area['vertices']}
            self.assertEqual(set(group['vertices']), expected)
        previous_points = {struct.unpack('<3f', struct.pack('<3f', *p)) for p in PREVIOUS}
        self.assertTrue(all(set(g['vertices']) != previous_points for g in groups))
        self.assertTrue(report['previous_generated_polygon_removed'])
        self.assertTrue(report['exact_previous_descriptor_verified'])
        self.assertEqual(AREAS, original_areas)
        self.assertEqual(self.replace(), (result, report))

    def test_preserves_native_fuel_rest_prefix_tail_and_other_header_fields(self):
        result, report = self.replace()
        before = struct.unpack_from('<24I', self.baseline)
        after = struct.unpack_from('<24I', result)
        self.assertEqual(result[96:before[22]], self.baseline[96:before[22]])
        self.assertEqual(result[before[22] + 8 * 48:], self.baseline[before[22]:])
        self.assertEqual([v for i, v in enumerate(before) if i not in (9, 22, 23)],
                         [v for i, v in enumerate(after) if i not in (9, 22, 23)])
        self.assertEqual(inspect_rest_triggers(result)[:2], inspect_rest_triggers(self.baseline))
        native_fuel = self.baseline[before[21] + 4 * 48:before[21] + 8 * 48]
        self.assertEqual(result[before[21] + 4 * 48:before[21] + 8 * 48], native_fuel)
        self.assertTrue(report['source_trigger_records_preserved'])
        self.assertIn('Unverified', report['runtime_behavior'])

    def test_rejects_source_suffix_previous_geometry_or_extra_group_drift(self):
        prefix = bytearray(self.current)
        prefix[100] ^= 1
        native_fuel = bytearray(self.current)
        header = struct.unpack_from('<24I', native_fuel)
        native_fuel[header[21] + 4 * 48 + 24] ^= 1
        previous_flags = bytearray(self.current)
        previous_flags[header[21] + 12 * 48 + 24] ^= 4
        extra, _ = append_car_parking_polygon(self.current, rectangle(70, 70, 80, 80))
        for drift in (bytes(prefix), self.current + b'suffix-drift',
                      bytes(native_fuel), bytes(previous_flags), extra):
            with self.subTest(drift=drift[-16:]), self.assertRaisesRegex(ValueError, 'differs'):
                self.replace(current=drift)
        changed_baseline = bytearray(self.baseline)
        changed_baseline[100] ^= 1
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.replace(baseline=bytes(changed_baseline))
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.replace(previous=rectangle(1, 1, 4, 8))

    def test_requires_two_unique_explicit_area_definitions(self):
        invalid = [None, [], AREAS[:1], AREAS + [AREAS[0]]]
        for field, value in [('id', ''), ('id', ' storefront'), ('id', 4),
                             ('partial_activation', None), ('partial_activation', 1),
                             ('partial_activation', 'true')]:
            altered = deepcopy(AREAS)
            altered[0][field] = value
            invalid.append(altered)
        missing = deepcopy(AREAS)
        missing[0].pop('partial_activation')
        invalid.append(missing)
        duplicate = deepcopy(AREAS)
        duplicate[1]['id'] = duplicate[0]['id']
        invalid.append(duplicate)
        unknown = deepcopy(AREAS)
        unknown[0]['flags'] = 4
        invalid.append(unknown)
        for areas in invalid:
            with self.subTest(areas=areas), self.assertRaises(ValueError):
                self.replace(areas)

    def test_refuses_invalid_nonrectangular_overlapping_or_touching_areas(self):
        polygons = [
            [(0, 0, 0), (1, 0, 0), (1, 0, 1)],
            [(0, 0, 0), (2, 0, 0), (3, 0, 1), (0, 0, 1)],
            [(0, 0, 0), (2, 0, 2), (0, 0, 2), (2, 0, 0)],
            rectangle(0, 0, 2, 0),
            [(0, 0, 0), (1, 0, 0), (1, float('nan'), 1), (0, 0, 1)],
            [(0, 0, 0), (1, 0, 0), (1, 0, float('inf')), (0, 0, 1)],
            [(0, 0, 0), (1, 0, 0), (1, True, 1), (0, 0, 1)],
        ]
        for polygon in polygons:
            areas = deepcopy(AREAS)
            areas[0]['vertices'] = polygon
            with self.subTest(polygon=polygon), self.assertRaises(ValueError):
                self.replace(areas)
        for polygon in (rectangle(10, -20, 25, -15),  # contained
                        rectangle(20, -20, 28, -10),  # crossing
                        rectangle(26, -21.15, 30, -14.7),  # touching edge
                        deepcopy(AREAS[0]['vertices'])):
            areas = deepcopy(AREAS)
            areas[1]['vertices'] = polygon
            with self.subTest(polygon=polygon), self.assertRaisesRegex(ValueError, 'overlap or touch'):
                self.replace(areas)

    def test_partial_activation_is_explicit_and_only_affects_target_groups(self):
        full = deepcopy(AREAS)
        full[0]['partial_activation'] = False
        partial, report = self.replace()
        mixed, mixed_report = self.replace(full)
        h = struct.unpack_from('<24I', mixed)
        first_id = report['areas'][0]['group_id']
        offsets = {h[21] + index * 48 + 24 for index in range(h[9])
                   if struct.unpack_from('<I', mixed, h[21] + index * 48)[0] == first_id}
        self.assertEqual({i for i, (a, b) in enumerate(zip(partial, mixed)) if a != b}, offsets)
        self.assertEqual(mixed_report['areas'][0]['parameters']['flags'], 0)
        self.assertEqual(mixed_report['areas'][1]['parameters']['flags'], 4)


class AppendActivationTests(unittest.TestCase):
    def test_default_bytes_and_report_match_the_original_pinned_writer(self):
        baseline = descriptor()
        result, report = append_car_parking_polygon(baseline, PREVIOUS)
        header = list(struct.unpack_from('<24I', baseline))
        insertion = header[22]
        records = b''.join(struct.pack('<IQfffI3f2i', 0, token('parking_car'),
                                      3., 0., 0., 0, *point, (i - 1) % 4, (i + 1) % 4)
                           for i, point in enumerate(PREVIOUS))
        header[9] += 4
        header[22] += len(records)
        header[23] += len(records)
        expected = struct.pack('<24I', *header) + baseline[96:insertion] + records + baseline[insertion:]
        self.assertEqual(result, expected)
        self.assertEqual(report, {
            'experimental': True, 'action': 'parking_car', 'group_id': 0,
            'vertex_count': 4,
            'parameters': {'range': 3., 'reset_delay': 0., 'reset_distance': 0., 'flags': 0},
            'source_trigger_records_preserved': True,
            'other_descriptor_sections_preserved': True,
            'selection': 'Caller-supplied explicit station only; no proximity or density inference',
            'runtime_behavior': 'Unknown; no in-game test performed',
        })
        self.assertEqual(append_car_parking_polygon(baseline, PREVIOUS, partial_activation=False),
                         (result, report))

    def test_explicit_partial_flag_only_changes_new_record_flag_fields(self):
        baseline = baseline_descriptor()
        normal, _ = append_car_parking_polygon(baseline, PREVIOUS)
        partial, report = append_car_parking_polygon(baseline, PREVIOUS, partial_activation=True)
        header = struct.unpack_from('<24I', baseline)
        offsets = {header[22] + index * 48 + 24 for index in range(4)}
        self.assertEqual({i for i, (a, b) in enumerate(zip(normal, partial)) if a != b}, offsets)
        self.assertEqual(report['parameters']['flags'], 4)
        self.assertEqual(partial[96:header[22]], baseline[96:header[22]])
        for value in (None, 1, 0, 'true', float('nan')):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'boolean'):
                append_car_parking_polygon(baseline, PREVIOUS, partial_activation=value)


if __name__ == '__main__':
    unittest.main()
