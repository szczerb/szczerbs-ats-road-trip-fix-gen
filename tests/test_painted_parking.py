import math
import unittest

from ats_road_trip.painted_parking import (
    PaintedParkingError,
    PaintedParkingParameters,
    propose_painted_parking,
)


def separator_mesh(*, count=4, angle=0.0, origin=(12.5, -8.25), spacing=2.86,
                   length=6.4, width=0.19, material='paint_lines', noisy=False):
    """Small synthetic PIM-shaped mesh; each stripe quad has two triangles."""
    direction = (math.cos(angle), math.sin(angle))
    normal = (-direction[1], direction[0])
    positions, triangles = [], []

    def point(s, t):
        return (origin[0] + direction[0] * s + normal[0] * t,
                0.1461,
                origin[1] + direction[1] * s + normal[1] * t)

    for row in range(count):
        center_t = row * spacing
        s0, s1 = -length / 2, length / 2
        t0, t1 = center_t - width / 2, center_t + width / 2
        quad = [point(s0, t0), point(s1, t0), point(s1, t1), point(s0, t1)]
        offset = len(positions)
        if noisy:
            # Separate triangle vertices reproduce texture/normal split seams;
            # the shared diagonal must still weld into one strip component.
            positions.extend([quad[0], quad[1], quad[2], quad[0], quad[2], quad[3]])
            triangles.extend([(offset, offset + 1, offset + 2),
                              (offset + 3, offset + 4, offset + 5)])
        else:
            positions.extend(quad)
            triangles.extend([(offset, offset + 1, offset + 2),
                              (offset, offset + 2, offset + 3)])
    if noisy:
        offset = len(positions)
        positions.extend([point(0, -2), point(0.2, -2), point(0, -1.8)])
        triangles.append((offset, offset + 1, offset + 2))
    return {
        'materials': [{'alias': material, 'effect': 'eut2.dif.spec.a.decal.over'}],
        'pieces': [{'index': 0, 'material_index': 0, 'material': material,
                    'positions': positions, 'triangles': triangles}],
    }


class PaintedParkingTests(unittest.TestCase):
    def test_detects_three_bays_from_four_rotated_parallel_mesh_strips(self):
        mesh = separator_mesh(angle=math.radians(31), noisy=True)
        result = propose_painted_parking(mesh, paint_materials={'paint_lines'})
        self.assertEqual(result['method'], 'painted_parallel_separator_mesh')
        self.assertEqual(len(result['selected']), 1)
        bank = result['selected'][0]
        self.assertEqual(bank['separator_count'], 4)
        self.assertEqual(bank['bay_count'], 3)
        self.assertTrue(bank['spacing_regular'])
        self.assertAlmostEqual(bank['center_spacing_m'][0], 2.86, places=6)
        self.assertAlmostEqual(bank['strips'][0]['length_m'], 6.4, places=6)
        self.assertAlmostEqual(bank['strips'][0]['width_m'], 0.19, places=6)
        self.assertTrue(all(abs(bay['width_m'] - 2.67) < 0.01 for bay in bank['bay_polygons_xz']))
        self.assertTrue(any(r['reason'] == 'paint_component_length_outside_vehicle_bay_separator_range'
                            for r in result['rejections']))
        self.assertIn('vehicle clearance', result['generation_readiness'])

    def test_coordinates_translate_without_prefab_specific_positions(self):
        a = propose_painted_parking(separator_mesh(origin=(0, 0)), paint_materials=['paint_lines'])
        b = propose_painted_parking(separator_mesh(origin=(37.25, -91.5)), paint_materials=['paint_lines'])
        self.assertEqual(len(a['selected']), 1)
        self.assertEqual(len(b['selected']), 1)
        a_poly = a['selected'][0]['bay_polygons_xz'][0]['polygon_xz']
        b_poly = b['selected'][0]['bay_polygons_xz'][0]['polygon_xz']
        for pa, pb in zip(a_poly, b_poly):
            self.assertAlmostEqual(pb[0] - pa[0], 37.25, places=6)
            self.assertAlmostEqual(pb[1] - pa[1], -91.5, places=6)

    def test_requires_three_parallel_separators_and_spacing_in_vehicle_range(self):
        two = propose_painted_parking(separator_mesh(count=2), paint_materials=['paint_lines'])
        far = propose_painted_parking(separator_mesh(spacing=5.0), paint_materials=['paint_lines'])
        self.assertEqual(two['selected'], [])
        self.assertTrue(two['blockers'])
        self.assertEqual(far['selected'], [])
        self.assertTrue(far['blockers'])

    def test_rejects_unmarked_noise_and_nonparallel_components(self):
        noise = separator_mesh(count=1, noisy=True)
        result = propose_painted_parking(noise, paint_materials=['paint_lines'])
        self.assertEqual(result['selected'], [])
        self.assertTrue(result['rejections'])
        crossing = separator_mesh(count=3)
        piece = crossing['pieces'][0]
        # Move the last strip diagonally enough to break the parallel-bank match.
        for idx in range(8, 12):
            x, y, z = piece['positions'][idx]
            piece['positions'][idx] = (x + 1.4, y, z + 3.0)
        angled = propose_painted_parking(crossing, paint_materials=['paint_lines'])
        self.assertEqual(angled['selected'], [])

    def test_rejects_pitches_that_leave_a_sub_vehicle_width_bay(self):
        result = propose_painted_parking(separator_mesh(spacing=2.0), paint_materials=['paint_lines'])
        self.assertEqual(result['selected'], [])
        self.assertTrue(any('free_bay_width_outside_vehicle_width_range' in row.get('details', [])
                            for row in result['rejections']))

    def test_rejects_transitive_chain_with_too_little_full_bank_overlap(self):
        mesh = separator_mesh()
        piece = mesh['pieces'][0]
        # Adjacent strips overlap 81.25%, enough to join pairwise, while the
        # first and last leave only 43.75% common longitudinal coverage.
        for row, shift in enumerate((0.0, 1.2, 2.4, 3.6)):
            for index in range(row * 4, row * 4 + 4):
                x, y, z = piece['positions'][index]
                piece['positions'][index] = (x + shift, y, z)
        result = propose_painted_parking(mesh, paint_materials=['paint_lines'])
        self.assertEqual(result['selected'], [])
        self.assertTrue(any('separator_bank_has_insufficient_common_longitudinal_overlap' in row.get('details', [])
                            for row in result['rejections']))

    def test_rejects_transitive_chain_with_bank_wide_angle_height_or_length_drift(self):
        def make_drifted(kind):
            mesh = separator_mesh()
            piece = mesh['pieces'][0]
            for row in range(4):
                center_t = row * 2.86
                angle = math.radians((-3.0, -1.0, 1.0, 3.0)[row]) if kind == 'angle' else 0.0
                for index in range(row * 4, row * 4 + 4):
                    x, y, z = piece['positions'][index]
                    if kind == 'angle':
                        dx, dz = x - 12.5, z - center_t
                        piece['positions'][index] = (12.5 + dx * math.cos(angle) - dz * math.sin(angle), y,
                                                     center_t + dx * math.sin(angle) + dz * math.cos(angle))
                    elif kind == 'height':
                        piece['positions'][index] = (x, row * 0.06, z)
                    elif kind == 'length':
                        length = 6.4 - row * 0.4
                        piece['positions'][index] = (12.5 + math.copysign(length / 2, x - 12.5), y, z)
            return mesh

        expected = {
            'angle': 'separator_bank_angle_span_exceeds_tolerance',
            'height': 'separator_bank_height_span_exceeds_tolerance',
            'length': 'separator_bank_length_variation_exceeds_tolerance',
        }
        for kind, reason in expected.items():
            with self.subTest(kind=kind):
                result = propose_painted_parking(make_drifted(kind), paint_materials=['paint_lines'])
                self.assertEqual(result['selected'], [])
                self.assertTrue(any(reason in row.get('details', []) for row in result['rejections']))

    def test_material_alias_is_explicit_and_unknown_alias_blocks(self):
        mesh = separator_mesh()
        with self.assertRaisesRegex(PaintedParkingError, 'explicit paint material'):
            propose_painted_parking(mesh, paint_materials=[])
        with self.assertRaisesRegex(PaintedParkingError, 'Unknown explicit paint material'):
            propose_painted_parking(mesh, paint_materials=['paint_lines', 'road'])
        other = propose_painted_parking(mesh, paint_materials=['paint_lines'],
                                        parameters=PaintedParkingParameters(min_spacing=3.0,
                                                                           max_spacing=4.0))
        self.assertEqual(other['selected'], [])

    def test_rejects_nonfinite_positions_and_triangle_indices(self):
        mesh = separator_mesh()
        mesh['pieces'][0]['positions'][0] = (float('nan'), 0.0, 0.0)
        with self.assertRaisesRegex(PaintedParkingError, 'nonfinite'):
            propose_painted_parking(mesh, paint_materials=['paint_lines'])
        mesh = separator_mesh()
        mesh['pieces'][0]['triangles'][0] = (0, 1, 999)
        with self.assertRaisesRegex(PaintedParkingError, 'invalid triangle index'):
            propose_painted_parking(mesh, paint_materials=['paint_lines'])

    def test_is_deterministic_for_identical_mesh(self):
        mesh = separator_mesh(angle=-0.42, noisy=True)
        first = propose_painted_parking(mesh, paint_materials=['paint_lines'])
        self.assertEqual(first, propose_painted_parking(mesh, paint_materials=['paint_lines']))

    def test_parameters_are_bounded_and_type_checked(self):
        for values in ({'weld_tolerance': True}, {'min_separators': 2},
                       {'max_parallel_angle_degrees': 16}, {'max_selected_triangles': 1_000_001},
                       {'min_longitudinal_overlap': True},
                       {'min_longitudinal_overlap': float('nan')},
                       {'min_bay_width': 2.0, 'max_bay_width': 2.0}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                PaintedParkingParameters(**values)


if __name__ == '__main__':
    unittest.main()
