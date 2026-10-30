"""Authored access cases isolate approaches, obstacles and ranking choices."""
from copy import deepcopy
import math
import unittest

from ats_road_trip.station_parking.selection import evaluate_access, rank_candidates


def rectangle(x0, z0, x1, z1):
    return [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]


def fixture():
    candidate = {'id': 'bank', 'polygon_xz': rectangle(-3., -3., 3., 3.),
                 'direction_xz': [0., 1.], 'separator_count': 3, 'bay_count': 2}
    geometry = {'polygons': [{'id': 1, 'color': 1,
                              'vertices': [[x, 0., z] for x, z in rectangle(-25., -25., 25., 25.)]}],
                'roads': [], 'gas_spawns': [{'position': [20., 0., 0.]}]}
    mesh = {'pieces': [{'index': 0, 'material': 'ground',
                        'positions': [[-25., 0., -25.], [25., 0., -25.],
                                      [25., 0., 25.], [-25., 0., 25.]],
                        'triangles': [(0, 1, 2), (0, 2, 3)]}], 'locators': []}
    return candidate, geometry, mesh


def evaluate(candidate, geometry, mesh):
    return evaluate_access(candidate, geometry, mesh, ground={'ground'}, paint=set())


class StationSelectionTests(unittest.TestCase):
    def test_explicit_access_parameters_control_both_end_checks(self):
        candidate,geometry,mesh=fixture()
        geometry['roads']=[{'indices':[1,2],'vertices':[[-20.,0.,10.],[20.,0.,10.]]}]
        self.assertFalse(evaluate(candidate,geometry,mesh)['rejection_reasons'])
        result=evaluate_access(candidate,geometry,mesh,ground={'ground'},paint=set(),road_clearance=14.,obstacle_margin=1.2)
        self.assertTrue(all('intersects_map_navigation_corridor_proxy' in c['rejection_reasons'] for c in result['approach_alternatives']))
        self.assertEqual(result['diagnostic_exclusions']['navigation_corridor_radius'],14.)
        self.assertEqual(result['diagnostic_exclusions']['obstacle_proxy_margin'],1.2)

    def test_margin_to_other_exclusions_wins_before_extra_pump_distance(self):
        candidates=[{'id':'near-npc','rejection_reasons':[],'pump_clearance':20.,'minimum_clearance_margin_m':.116},
                    {'id':'robust','rejection_reasons':[],'pump_clearance':12.,'minimum_clearance_margin_m':1.2}]
        ranked=rank_candidates(candidates)
        self.assertEqual(ranked[0]['id'],'robust')
        self.assertEqual(ranked[1]['ranking_components']['minimum_margin_capped_2m_rounded_cm'],.12)
        candidates[0]['minimum_clearance_margin_m']=1.200001
        candidates[1]['minimum_clearance_margin_m']=1.200002
        self.assertEqual(rank_candidates(candidates)[0]['id'],'near-npc')

    def test_painted_bank_tries_both_ends_and_does_not_mutate_inputs(self):
        candidate, geometry, mesh = fixture()
        original = deepcopy((candidate, geometry, mesh))
        geometry['gas_spawns'][0]['position'] = [0., 0., -12.]
        result = evaluate(candidate, geometry, mesh)
        self.assertFalse(result['rejection_reasons'])
        self.assertEqual(len(result['approach_alternatives']), 2)
        self.assertGreater(min(p[1] for p in result['approach_xz']), 0.)
        rejected = next(row for row in result['approach_alternatives'] if row['rejection_reasons'])
        self.assertIn('footprint_or_approach_too_close_to_gas_interaction', rejected['rejection_reasons'])
        self.assertEqual(result['heading_xz'], [0., -1.])
        self.assertTrue(result['model_surface_checks']['vertices_xyz'])
        self.assertEqual(candidate, original[0])
        self.assertEqual(mesh, original[2])

    def test_external_object_at_one_end_preserves_the_clear_opposite_approach(self):
        from ats_road_trip.station_parking.local_context import evaluate_local_context
        candidate,geometry,mesh=fixture()
        context={'objects':[{'id':'separate-building','classification':'obstacle_proxy',
            'extent_status':'declared_conservative_proxy','geometry_xz':rectangle(-1.,-6.,1.,-5.)}]}
        result=evaluate_access(candidate,geometry,mesh,ground={'ground'},paint=set(),
            region_validator=lambda region:evaluate_local_context(region,context))
        self.assertFalse(result['rejection_reasons'])
        self.assertGreater(min(p[1] for p in result['approach_xz']),0.)
        rejected=[a for a in result['approach_alternatives'] if a['rejection_reasons']]
        self.assertEqual(len(rejected),1)
        self.assertIn('intersects_external_map_object_proxy',rejected[0]['rejection_reasons'])
        self.assertIn('external_object',result['clearance_margins_m'])

    def test_parked_vehicle_in_approach_rejects_even_when_footprint_clear(self):
        candidate, geometry, mesh = fixture()
        candidate['approach_xz'] = rectangle(-3., 3., 3., 7.)
        mesh['locators'] = [{'index': 7, 'hookup': 'car.parked.physics', 'position': [0., 0., 7.]}]
        result = evaluate(candidate, geometry, mesh)
        self.assertIn('parked_vehicle_locator_exclusion', result['rejection_reasons'])
        self.assertEqual(result['access_checks']['parked_locator_conflicts'][0]['regions'], ['approach'])
        self.assertIsNone(result['model_surface_checks'])
        self.assertLess(result['clearance_margins_m']['parked_locator'],0.)

    def test_model_obstacle_on_preferred_end_uses_other_end(self):
        candidate, geometry, mesh = fixture()
        mesh['pieces'].append({'index': 1, 'material': 'wall',
                               'positions': [[-2., .3, -6.], [2., .3, -6.], [2., 1.5, -6.]],
                               'triangles': [(0, 1, 2)]})
        result = evaluate(candidate, geometry, mesh)
        self.assertFalse(result['rejection_reasons'])
        self.assertGreater(min(p[1] for p in result['approach_xz']), 0.)
        rejected = next(row for row in result['approach_alternatives'] if row['rejection_reasons'])
        self.assertIn('model_geometry_intersects_car_clearance_volume', rejected['rejection_reasons'])

    def test_both_ends_blocked_are_reported_without_fallback(self):
        candidate, geometry, mesh = fixture()
        geometry['gas_spawns'] = [{'position': [0., 0., z]} for z in (-12., 12.)]
        result = evaluate(candidate, geometry, mesh)
        self.assertTrue(result['rejection_reasons'])
        self.assertTrue(all(row['rejection_reasons'] for row in result['approach_alternatives']))
        self.assertIsNone(result['model_surface_checks'])

    def test_supplied_approach_checks_road_and_ui_proxy(self):
        candidate, geometry, mesh = fixture()
        candidate['approach_xz'] = rectangle(-3., 3., 3., 7.)
        geometry['roads'] = [{'indices': [10, 11], 'vertices': [[-20., 0., 9.], [20., 0., 9.]]}]
        geometry['polygons'].append({'id': 4, 'color': 4,
                                      'vertices': [[x, 0., z] for x, z in rectangle(-1., 5., 1., 6.)]})
        result = evaluate(candidate, geometry, mesh)
        self.assertEqual(len(result['approach_alternatives']), 1)
        self.assertEqual(result['access_checks']['road_conflicts'][0]['regions'], ['approach'])
        self.assertEqual(result['access_checks']['obstacle_proxy_conflicts'][0]['regions'], ['approach'])

    def test_vertex_notch_rejects_footprint_in_access_check(self):
        candidate, geometry, mesh = fixture()
        candidate['polygon_xz'] = rectangle(1, 1, 9, 3)
        candidate['approach_xz'] = rectangle(1, 3, 9, 5)
        lot = [(0,0),(2,0),(2,1),(3,2),(4,1),(4,0),(10,0),(10,10),(0,10)]
        geometry['polygons'][0]['vertices'] = [[x, 0, z] for x, z in lot]
        result = evaluate(candidate, geometry, mesh)
        self.assertIn('footprint_or_approach_outside_accessible_map_proxy', result['rejection_reasons'])
        self.assertIn('footprint', result['access_checks']['outside_accessible_proxy'])

    def test_outside_accessible_and_missing_ground_remain_blockers(self):
        candidate, geometry, mesh = fixture()
        candidate['approach_xz'] = rectangle(-3., 24., 3., 28.)
        result = evaluate(candidate, geometry, mesh)
        self.assertIn('footprint_or_approach_outside_accessible_map_proxy', result['rejection_reasons'])
        candidate, geometry, mesh = fixture()
        mesh['pieces'][0]['positions'] = [[-3., 0., -3.], [3., 0., -3.], [3., 0., 3.], [-3., 0., 3.]]
        result = evaluate(candidate, geometry, mesh)
        self.assertIn('selected_ground_mesh_does_not_cover_all_surface_samples', result['rejection_reasons'])

    def test_rotating_all_inputs_rotates_selected_approach_and_heading(self):
        candidate, geometry, mesh = fixture()
        geometry['gas_spawns'][0]['position'] = [0., 0., -12.]
        first = evaluate(candidate, geometry, mesh)
        rotate = lambda p: [-p[1], p[0]]
        candidate['polygon_xz'] = list(map(rotate, candidate['polygon_xz']))
        candidate['direction_xz'] = rotate(candidate['direction_xz'])
        for polygon in geometry['polygons']:
            polygon['vertices'] = [[-z, y, x] for x, y, z in polygon['vertices']]
        for spawn in geometry['gas_spawns']:
            x, y, z = spawn['position']; spawn['position'] = [-z, y, x]
        for piece in mesh['pieces']:
            piece['positions'] = [[-z, y, x] for x, y, z in piece['positions']]
        second = evaluate(candidate, geometry, mesh)
        self.assertEqual(sorted(second['approach_xz']), sorted(map(rotate, first['approach_xz'])))
        self.assertEqual(second['heading_xz'], rotate(first['heading_xz']))
        candidate['direction_xz'] = [-v for v in candidate['direction_xz']]
        self.assertEqual(evaluate(candidate, geometry, mesh), second)

    def test_ranking_prioritizes_valid_evidence_clearance_bays_then_stable_id(self):
        rows = [{'id': 'bad', 'separator_count': 5, 'bay_count': 4, 'pump_clearance': 100., 'rejection_reasons': ['blocked']},
                {'id': 'ui', 'pump_clearance': 20., 'rejection_reasons': []},
                {'id': 'near', 'separator_count': 3, 'bay_count': 8, 'pump_clearance': 7., 'rejection_reasons': []},
                {'id': 'b', 'separator_count': 3, 'bay_count': 2, 'pump_clearance': 30., 'rejection_reasons': []},
                {'id': 'a', 'separator_count': 3, 'bay_count': 2, 'pump_clearance': 20., 'rejection_reasons': []}]
        original = deepcopy(rows)
        result = rank_candidates(rows)
        self.assertEqual([r['id'] for r in result], ['a', 'b', 'near', 'ui', 'bad'])
        self.assertEqual(rank_candidates(list(reversed(rows))), result)
        self.assertEqual(result[0]['ranking_components']['pump_clearance_capped_20'], 20.)
        self.assertEqual(rows, original)

    def test_rejects_invalid_access_parameters(self):
        candidate, geometry, mesh = fixture()
        for kwargs in ({'pump_clearance': math.nan}, {'aisle_depth': True}):
            with self.assertRaisesRegex(ValueError, 'positive and finite'):
                evaluate_access(candidate, geometry, mesh, ground={'ground'}, paint=set(), **kwargs)


if __name__ == '__main__':
    unittest.main()
