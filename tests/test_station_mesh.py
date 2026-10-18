import unittest

from ats_road_trip.station_mesh import StationMeshError, read_station_mesh, sample_surface_height


def pim_text(*, vertices=None, triangles=((0, 1, 2), (0, 2, 3)), y2=0.0,
             material='pavement', extra_stream=''):
    vertices = vertices or [(0., 0., 0.), (2., 0., 0.), (2., y2, 2.), (0., 0., 2.)]
    position_rows = '\n'.join(f'          {i} ( {x} {y} {z} )'
                              for i, (x, y, z) in enumerate(vertices))
    uv_rows = '\n'.join(f'          {i} ( {float(i % 2)} {float((i // 2) % 2)} )'
                         for i in range(len(vertices)))
    triangle_rows = '\n'.join(f'          {i} ( {a} {b} {c} )'
                              for i, (a, b, c) in enumerate(triangles))
    streams = f'''     StreamCount: 2
     Stream {{
          Format: FLOAT3
          Tag: "_POSITION"
{position_rows}
     }}
     Stream {{
          Format: FLOAT2
          Tag: "_UV0"
{uv_rows}
     }}
{extra_stream}'''
    return f'''Header {{
 FormatVersion: 5
 Source: "fixture"
 Type: "Model"
 Name: "station"
}}
Global {{
 VertexCount: {len(vertices)}
 TriangleCount: {len(triangles)}
 MaterialCount: 1
 PieceCount: 1
 PartCount: 1
 BoneCount: 0
 LocatorCount: 1
 Skeleton: "station.pis"
}}
Material {{
 Alias: "{material}"
 Effect: "eut2.dif.spec"
}}
Piece {{
 Index: 0
 Material: 0
 VertexCount: {len(vertices)}
 TriangleCount: {len(triangles)}
{streams}
     Triangles {{
{triangle_rows}
     }}
}}
Part {{
 Name: "part1"
 PieceCount: 1
 LocatorCount: 1
 Pieces: 0
 Locators: 0
}}
Locator {{
 Name: "parking_hook"
 Hookup: "template.station#surface:asphalt"
 Index: 0
 Position: ( &3f800000 &00000000 &40000000 )
 Rotation: ( &00000000 &00000000 &00000000 &3f800000 )
 Scale: ( &3f800000 &3f800000 &3f800000 )
}}
'''


class StationMeshTests(unittest.TestCase):
    def test_reads_model_streams_material_triangles_parts_and_locator_metadata(self):
        mesh = read_station_mesh(pim_text())
        self.assertEqual(mesh['format_version'], 5)
        self.assertEqual(mesh['coordinate_order'], ('x', 'y', 'z'))
        self.assertFalse(mesh['coordinate_transform_applied'])
        self.assertEqual(mesh['counts'], {'vertices': 4, 'triangles': 2,
                         'materials': 1, 'pieces': 1, 'parts': 1,
                         'bones': 0, 'locators': 1})
        self.assertEqual(mesh['materials'][0], {'alias': 'pavement', 'effect': 'eut2.dif.spec'})
        self.assertEqual(mesh['pieces'][0]['triangles'], [(0, 1, 2), (0, 2, 3)])
        self.assertEqual(mesh['pieces'][0]['uv0'], [(0., 0.), (1., 0.), (0., 1.), (1., 1.)])
        self.assertEqual(mesh['parts'][0], {'name': 'part1', 'pieces': [0], 'locators': [0]})
        self.assertEqual(mesh['locators'][0]['hookup'], 'template.station#surface:asphalt')
        self.assertEqual(mesh['locators'][0]['position'], (1., 0., 2.))

    def test_samples_selected_surface_and_ignores_vertical_triangles(self):
        mesh = read_station_mesh(pim_text())
        self.assertEqual(sample_surface_height(mesh, (1., 1.), {'pavement'}), 0.)
        with self.assertRaisesRegex(ValueError, 'No selected'):
            sample_surface_height(mesh, (1., 1.), {'curb'})

    def test_rejects_ambiguous_surface_layers(self):
        vertices = [(0., 0., 0.), (2., 0., 0.), (2., 0., 2.), (0., 0., 2.),
                    (0., 1., 0.), (2., 1., 0.), (2., 1., 2.), (0., 1., 2.)]
        triangles = ((0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7))
        mesh = read_station_mesh(pim_text(vertices=vertices, triangles=triangles))
        with self.assertRaisesRegex(ValueError, 'disagree in height'):
            sample_surface_height(mesh, (1., 1.), {'pavement'})

    def test_rejects_bad_versions_counts_indices_and_nonfinite_values(self):
        with self.assertRaisesRegex(StationMeshError, 'FormatVersion'):
            read_station_mesh(pim_text().replace('FormatVersion: 5', 'FormatVersion: 4'))
        with self.assertRaisesRegex(StationMeshError, 'Triangle vertex index'):
            read_station_mesh(pim_text(triangles=((0, 1, 99),)))
        bad_float = pim_text().replace('0 ( 0.0 0.0 0.0 )', '0 ( &7f800000 0.0 0.0 )')
        with self.assertRaisesRegex(StationMeshError, 'nonfinite'):
            read_station_mesh(bad_float)
        with self.assertRaisesRegex(StationMeshError, 'Duplicate or malformed'):
            read_station_mesh(pim_text().replace(' Alias: "pavement"',
                                                 ' Alias: "pavement"\n Alias: "again"'))

    def test_rejects_membership_and_malformed_braces(self):
        bad_part = pim_text().replace('Pieces: 0', 'Pieces: 4')
        with self.assertRaisesRegex(StationMeshError, 'out-of-range'):
            read_station_mesh(bad_part)
        with self.assertRaisesRegex(StationMeshError, 'Unclosed'):
            read_station_mesh(pim_text().replace('Header {', 'Header {', 1).replace('}\nGlobal', '\nGlobal', 1))

    def test_rejects_text_limit_and_empty_material_selection(self):
        with self.assertRaisesRegex(StationMeshError, '32 MiB'):
            read_station_mesh(' ' * (32 * 1024 * 1024 + 1))
        mesh = read_station_mesh(pim_text())
        with self.assertRaisesRegex(ValueError, 'explicit surface material'):
            sample_surface_height(mesh, (1., 1.), set())


if __name__ == '__main__':
    unittest.main()
