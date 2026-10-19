"""Raised-boundary parking proposals from original authored fixtures."""
from copy import deepcopy
import math
import unittest

from ats_road_trip.station_parking.methods.curbside import propose_curb_anchored_candidates
from ats_road_trip.station_parking.methods.unmarked import ParkingParameters


def fixture(height=.1, material='pavement'):
    mesh = {'pieces': [
        {'index': 0, 'material': 'ground',
         'positions': [[-30., 0., -30.], [30., 0., -30.], [30., 0., 30.], [-30., 0., 30.]],
         'triangles': [(0, 1, 2), (0, 2, 3)]},
        {'index': 1, 'material': material,
         'positions': [[-8., height, -2.], [8., height, -2.], [8., height, 0.], [-8., height, 0.]],
         'triangles': [(0, 1, 2), (0, 2, 3)]}], 'locators': []}
    geometry = {'polygons': [{'id': 1, 'color': 2,
                              'vertices': [[-8., 0., -5.], [8., 0., -5.], [8., 0., -1.], [-8., 0., -1.]]}],
                'gas_spawns': [{'position': [0., 0., 18.]}], 'roads': []}
    return mesh, geometry


def propose(mesh, geometry):
    return propose_curb_anchored_candidates(mesh, geometry, ground={'ground'}, paint={'paint'}, parameters=ParkingParameters())


class StationCurbsideTests(unittest.TestCase):
    def test_long_boundary_excludes_interior_diagonal_and_retains_physical_dimensions(self):
        mesh, geometry = fixture()
        original = deepcopy((mesh, geometry))
        candidates = propose(mesh, geometry)
        self.assertTrue(candidates)
        self.assertEqual({c['layout'] for c in candidates}, {'parallel', 'perpendicular'})
        boundaries = {tuple(tuple(p) for p in c['source_edge_evidence']['boundary_xyz']) for c in candidates}
        self.assertEqual(boundaries, {((-8., .1, 0.), (8., .1, 0.))})
        for candidate in candidates:
            points = candidate['polygon_xz']
            self.assertEqual(sorted([math.dist(points[0], points[1]), math.dist(points[1], points[2])]), [3., 6.])
            self.assertEqual(min(p[1] for p in points), .5)
            # UI wall is at -1. The proposal is anchored to the actual raised
            # front at 0 rather than placing a bay from the UI edge alone.
            self.assertEqual(candidate['source_edge_evidence']['edge_offset_m'], .5)
            self.assertLess(min(p[1] for p in points), -1.+ParkingParameters().wall_setback)
            self.assertTrue(all(s['rise'] == .1 for s in candidate['source_edge_evidence']['outside_ground_samples']))
        self.assertEqual((mesh, geometry), original)

    def test_concave_wall_uses_ring_winding_instead_of_vertex_mean(self):
        mesh,geometry=fixture()
        ring=[[-20.,-10.],[20.,-10.],[20.,4.],[6.,4.],[6.,-2.],[-6.,-2.],[-6.,4.],[-20.,4.]]
        geometry['polygons'][0]['vertices']=[[x,0.,z] for x,z in ring]
        first=propose(mesh,geometry)
        self.assertTrue(first)
        geometry['polygons'][0]['vertices'].reverse()
        second=propose(mesh,geometry)
        signature=lambda rows:sorted(tuple(tuple(p) for p in c['polygon_xz']) for c in rows)
        self.assertEqual(signature(first),signature(second))
        self.assertTrue(all(min(p[1] for p in c['polygon_xz'])==.5 for c in first))

    def test_proxy_wall_angle_does_not_skew_the_physical_rectangle(self):
        mesh,geometry=fixture()
        for p in geometry['polygons'][0]['vertices']:p[2]+=.05*p[0]
        candidates=propose(mesh,geometry)
        self.assertTrue(candidates)
        for candidate in candidates:
            a,b,c,d=candidate['polygon_xz']
            self.assertAlmostEqual(sum((b[i]-a[i])*(d[i]-a[i]) for i in (0,1)),0.,places=8)

    def test_flat_decal_or_wrong_height_does_not_qualify_even_with_curb_name(self):
        for height in (0., .02, .3):
            mesh, geometry = fixture(height=height, material='curb_pavement')
            self.assertEqual(propose(mesh, geometry), [])
        mesh, geometry = fixture(height=.1, material='paint')
        self.assertEqual(propose(mesh, geometry), [])

    def test_missing_wall_or_ground_sample_produces_no_candidates(self):
        mesh, geometry = fixture()
        geometry['polygons'] = []
        self.assertEqual(propose(mesh, geometry), [])
        mesh, geometry = fixture()
        mesh['pieces'][0]['positions'] = [[-30., 0., -30.], [30., 0., -30.], [30., 0., -.1], [-30., 0., -.1]]
        self.assertEqual(propose(mesh, geometry), [])

    def test_canopy_proxy_and_pumps_on_building_side_do_not_qualify(self):
        mesh, geometry = fixture()
        geometry['gas_spawns'][0]['position'] = [0., 0., -3.]
        self.assertEqual(propose(mesh, geometry), [])

    def test_welding_duplicates_removes_diagonal_and_order_is_deterministic(self):
        mesh, geometry = fixture()
        expected = propose(mesh, geometry)
        piece = mesh['pieces'][1]
        piece['positions'] += deepcopy(piece['positions'])
        piece['triangles'] = [(4, 6, 7), (0, 1, 2)]
        actual = propose(mesh, geometry)
        signature = lambda rows: sorted(tuple(tuple(p) for p in c['polygon_xz']) for c in rows)
        self.assertEqual(signature(actual), signature(expected))
        self.assertEqual(actual, propose(mesh, geometry))
        mesh['pieces'].reverse()
        self.assertEqual(actual, propose(mesh, geometry))

    def test_rotation_rotates_boundary_footprints_and_heading(self):
        mesh, geometry = fixture()
        first = propose(mesh, geometry)
        for piece in mesh['pieces']:
            piece['positions'] = [[-z, y, x] for x, y, z in piece['positions']]
        for polygon in geometry['polygons']:
            polygon['vertices'] = [[-z, y, x] for x, y, z in polygon['vertices']]
        for spawn in geometry['gas_spawns']:
            x, y, z = spawn['position']; spawn['position'] = [-z, y, x]
        second = propose(mesh, geometry)
        signatures = lambda rows: sorted((c['layout'], tuple(sorted(tuple(round(v, 8) for v in p) for p in c['polygon_xz']))) for c in rows)
        rotated = deepcopy(first)
        for c in rotated:
            c['polygon_xz'] = [[-z, x] for x, z in c['polygon_xz']]
        self.assertEqual(signatures(second), signatures(rotated))
        for candidate in second:
            self.assertAlmostEqual(math.hypot(*candidate.get('parking_heading_xz',candidate.get('direction_xz'))), 1.)

    def test_subdivided_straight_front_edges_merge_into_long_boundary(self):
        mesh, geometry = fixture()
        piece = mesh['pieces'][1]
        piece['positions'] = [[-8., .1, -2.], [0., .1, -2.], [8., .1, -2.],
                              [-8., .1, 0.], [0., .1, 0.], [8., .1, 0.]]
        piece['triangles'] = [(0, 1, 4), (0, 4, 3), (1, 2, 5), (1, 5, 4)]
        candidates = propose(mesh, geometry)
        self.assertTrue(candidates)
        self.assertTrue(all(math.dist(*[p[0:3:2] for p in c['source_edge_evidence']['boundary_xyz']]) == 16. for c in candidates))


if __name__ == '__main__':
    unittest.main()
