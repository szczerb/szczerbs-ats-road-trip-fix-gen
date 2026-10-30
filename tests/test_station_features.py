import copy
import unittest

from ats_road_trip.station_parking.features import inspect_model_features


def piece(index, material, positions, triangles):
    return {"index": index, "material": material, "positions": positions,
            "triangles": triangles}


def fixture_mesh():
    # Ground establishes local Y=0. The curb hint has a low vertical riser and
    # a flat top. A separate door-alias panel has door-like vertical geometry.
    return {"pieces": [
        piece(0, "ground", [[-4, 0, -4], [4, 0, -4], [4, 0, 4], [-4, 0, 4]],
              [[0, 1, 2], [0, 2, 3]]),
        piece(1, "paint", [[-1, 0.01, -1], [1, 0.01, -1], [1, 0.01, 1]], [[0, 1, 2]]),
        piece(2, "kerb_stone", [[0, 0, 0], [1, 0, 0], [1, 0.15, 0],
                                [0, 0.15, 0], [1, 0.15, 0.3], [0, 0.15, 0.3]],
              [[0, 1, 2], [0, 2, 3], [2, 4, 5], [2, 5, 3]]),
        piece(3, "door_panel", [[2, 0, 0], [3, 0, 0], [3, 2, 0], [2, 2, 0]],
              [[0, 1, 2], [0, 2, 3]]),
        piece(4, "furniture", [[0, 0.3, 2], [0.5, 0.3, 2], [0.5, 1.2, 2]], [[0, 1, 2]]),
        # A flat, generic surface should not become a curb merely because it
        # occupies a horizontal plane.
        piece(5, "generic_floor", [[-2, 0.1, 2], [-1, 0.1, 2], [-1, 0.1, 3]], [[0, 1, 2]]),
    ]}


class StationFeaturesTests(unittest.TestCase):
    def inspect(self, mesh):
        return inspect_model_features(mesh, ground={"ground"}, paint={"paint"})

    def test_requires_grounded_shape_in_addition_to_material_hint(self):
        result = self.inspect(fixture_mesh())
        self.assertEqual(result["ground_reference"]["height_y"], 0.0)
        self.assertEqual(result["curb_evidence"]["feature_count"], 2)
        self.assertEqual(result["curb_evidence"]["interpretation"],
                         "candidate geometry evidence, not proof that the edge is a curb or usable sidewalk")
        self.assertEqual(result["entrance_clearance"]["proxy_count"], 1)
        self.assertEqual(result["entrance_clearance"]["proxies"][0]["confidence"], "hypothesis")
        self.assertEqual(result["entrance_clearance"]["proxies"][0]["polygon_xz"],
                         [[0.5, -1.5], [4.5, -1.5], [4.5, 1.5], [0.5, 1.5]])

    def test_obstacles_are_individual_triangles_and_ignore_ground_and_paint(self):
        result = self.inspect(fixture_mesh())
        features = result["obstacles"]["features"]
        self.assertEqual([item["material_alias"] for item in features],
                         ["door_panel", "door_panel", "furniture"])
        self.assertTrue(all(len(item["polygon_xz"]) <= 3 for item in features))
        self.assertEqual(result["obstacles"]["grouping"],
                         "individual source triangles; no whole-piece bounding boxes")
        self.assertFalse(result["obstacles"]["complete"] is False)

    def test_flat_generic_geometry_and_name_hints_alone_do_not_claim_curb_or_door(self):
        mesh = {"pieces": [
            piece(0, "ground", [[0, 0, 0], [1, 0, 0], [0, 0, 1]], [[0, 1, 2]]),
            piece(1, "sidewalk_texture_only", [[0, 0, 0], [1, 0, 0], [0, 0, 1]], [[0, 1, 2]]),
            piece(2, "door_atlas", [[2, 0, 0], [3, 0, 0], [2, 0, 1]], [[0, 1, 2]]),
        ]}
        result = self.inspect(mesh)
        self.assertEqual(result["curb_evidence"]["feature_count"], 0)
        self.assertEqual(result["entrance_clearance"]["proxy_count"], 0)
        self.assertEqual(result["entrance_clearance"]["unresolved_component_count"], 1)

    def test_result_is_deterministic_and_input_is_unchanged(self):
        mesh = fixture_mesh()
        original = copy.deepcopy(mesh)
        first = self.inspect(mesh)
        second = self.inspect(mesh)
        self.assertEqual(first, second)
        self.assertEqual(mesh, original)

    def test_feature_output_is_bounded_and_reports_omissions(self):
        positions = []
        triangles = []
        for index in range(520):
            base = len(positions)
            x = float(index * 2)
            positions.extend([[x, 0.4, 0], [x + 1, 0.4, 0], [x, 0.4, 1]])
            triangles.append([base, base + 1, base + 2])
        mesh = {"pieces": [piece(0, "ground", [[0, 0, 0], [1, 0, 0], [0, 0, 1]], [[0, 1, 2]]),
                           piece(1, "chairs", positions, triangles)]}
        result = self.inspect(mesh)
        self.assertEqual(result["obstacles"]["feature_count"], 512)
        self.assertEqual(result["obstacles"]["omitted_feature_count"], 8)
        self.assertFalse(result["obstacles"]["complete"])

    def test_malformed_geometry_fails_closed(self):
        mesh = {"pieces": [piece(0, "ground", [[0, float("nan"), 0]], [])]}
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            self.inspect(mesh)


if __name__ == "__main__":
    unittest.main()
