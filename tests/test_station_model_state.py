import copy
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.station_parking.mesh import StationMeshError, read_station_mesh
from ats_road_trip.station_parking.model_state import resolve_model_state


def pit_text(*, default_city_sign=0, city_main=0):
    return f'''Header {{
 FormatVersion: 1
 Source: "fixture"
 Type: "Trait"
 Name: "station"
}}
Global {{
 LookCount: 1
 VariantCount: 2
 PartCount: 3
 MaterialCount: 3
}}
Look {{
 Name: "default"
 Material {{
  Alias: "asphalt"
  Effect: "eut2.dif.spec"
  Flags: 0
  AttributeCount: 0
  TextureCount: 1
  Texture {{
   Tag: "texture[0]:texture_base"
   Value: "/material/road/asphalt"
  }}
 }}
 Material {{
  Alias: "paint"
  Effect: "eut2.dif.spec"
  Flags: 0
  AttributeCount: 0
  TextureCount: 1
  Texture {{
   Tag: "texture[0]:texture_base"
   Value: "/material/decal/parking_lines"
  }}
 }}
 Material {{
  Alias: "city_sign"
  Effect: "eut2.dif.spec"
  Flags: 0
  AttributeCount: 0
  TextureCount: 1
  Texture {{
   Tag: "texture[0]:texture_base"
   Value: "/material/signs/city"
  }}
 }}
}}
Variant {{
 Name: "default"
 Part {{
  Name: "collpart1"
  AttributeCount: 1
  Attribute {{
   Format: "INT"
   Tag: "visible"
   Value: ( 1 )
  }}
 }}
 Part {{
  Name: "part1"
  AttributeCount: 1
  Attribute {{
   Format: "INT"
   Tag: "visible"
   Value: ( 1 )
  }}
 }}
 Part {{
  Name: "city_sign"
  AttributeCount: 1
  Attribute {{
   Format: "INT"
   Tag: "visible"
   Value: ( {default_city_sign} )
  }}
 }}
}}
Variant {{
 Name: "city"
 Part {{
  Name: "collpart1"
  AttributeCount: 1
  Attribute {{
   Format: "INT"
   Tag: "visible"
   Value: ( 1 )
  }}
 }}
 Part {{
  Name: "part1"
  AttributeCount: 1
  Attribute {{
   Format: "INT"
   Tag: "visible"
   Value: ( {city_main} )
  }}
 }}
 Part {{
  Name: "city_sign"
  AttributeCount: 1
  Attribute {{
   Format: "INT"
   Tag: "visible"
   Value: ( 1 )
  }}
 }}
}}
'''


def mesh_fixture():
    def piece(index, alias, material_index):
        return {"index": index, "material_index": material_index, "material": alias,
                "vertex_count": 3, "triangle_count": 1,
                "positions": [(0., 0., 0.), (1., 0., 0.), (0., 0., 1.)],
                "uv0": None, "streams": {"_POSITION": [(0., 0., 0.), (1., 0., 0.), (0., 0., 1.)]},
                "triangles": [(0, 1, 2)]}

    return {
        "format_version": 5, "name": "station", "source": "fixture",
        "coordinate_order": ("x", "y", "z"), "coordinate_transform_applied": False,
        "counts": {"vertices": 9, "triangles": 3, "materials": 3, "pieces": 3,
                   "parts": 3, "bones": 0, "locators": 2},
        "materials": [{"alias": name, "effect": "eut2.dif.spec"}
                      for name in ("asphalt", "paint", "city_sign")],
        "pieces": [piece(0, "asphalt", 0), piece(1, "paint", 1), piece(2, "city_sign", 2)],
        "parts": [{"name": "collpart1", "pieces": [0], "locators": []},
                  {"name": "part1", "pieces": [1], "locators": [0]},
                  {"name": "city_sign", "pieces": [2], "locators": [1]}],
        "locators": [{"name": "parked_car_0", "hookup": "truck.parked.physics", "index": 0,
                      "position": (1., 0., 1.), "rotation": (0., 0., 0., 1.), "scale": (1., 1., 1.)},
                     {"name": "parked_car_1", "hookup": "truck.parked.physics", "index": 1,
                      "position": (2., 0., 2.), "rotation": (0., 0., 0., 1.), "scale": (1., 1., 1.)}],
    }


def pim_text():
    materials = "\n".join(f'''Material {{
 Alias: "{name}"
 Effect: "eut2.dif.spec"
}}''' for name in ("asphalt", "paint", "city_sign"))
    pieces = []
    for index, material in enumerate(range(3)):
        pieces.append(f'''Piece {{
 Index: {index}
 Material: {material}
 VertexCount: 3
 TriangleCount: 1
 StreamCount: 1
 Stream {{
  Format: FLOAT3
  Tag: "_POSITION"
  0 ( 0 0 0 )
  1 ( 1 0 0 )
  2 ( 0 0 1 )
 }}
 Triangles {{
  0 ( 0 1 2 )
 }}
}}''')
    parts = []
    for index, name in enumerate(("collpart1", "part1", "city_sign")):
        parts.append(f'''Part {{
 Name: "{name}"
 PieceCount: 1
 LocatorCount: 1
 Pieces: {index}
 Locators: {index}
}}''')
    locators = []
    for index in range(3):
        locators.append(f'''Locator {{
 Name: "parked_car_{index}"
 Hookup: "truck.parked.physics"
 Index: {index}
 Position: ( {index} 0 1 )
 Rotation: ( 0 0 0 1 )
 Scale: ( 1 1 1 )
}}''')
    piece_blocks = "\n".join(pieces)
    part_blocks = "\n".join(parts)
    locator_blocks = "\n".join(locators)
    return f'''Header {{
 FormatVersion: 5
 Source: "fixture"
 Type: "Model"
 Name: "station"
}}
Global {{
 VertexCount: 9
 TriangleCount: 3
 MaterialCount: 3
 PieceCount: 3
 PartCount: 3
 BoneCount: 0
 LocatorCount: 3
 Skeleton: "station.pis"
}}
{materials}
{piece_blocks}
{part_blocks}
{locator_blocks}
'''


class StationModelStateTests(unittest.TestCase):
    def test_zero_selects_default_and_filters_pieces_materials_and_locators(self):
        source = mesh_fixture()
        before = copy.deepcopy(source)
        visible, report = resolve_model_state(source, pit_text())
        self.assertEqual(source, before)
        self.assertEqual(report["variant"], "default")
        self.assertEqual(report["visible_parts"], ["collpart1", "part1"])
        self.assertEqual(report["inactive_parts"], ["city_sign"])
        self.assertEqual([piece["source_index"] for piece in visible["pieces"]], [0, 1])
        self.assertEqual([locator["source_index"] for locator in visible["locators"]], [0])
        self.assertEqual([m["alias"] for m in visible["materials"]], ["asphalt", "paint"])
        self.assertEqual(report["materials"][1]["textures"], ["/material/decal/parking_lines"])
        self.assertEqual(report["collision_parts_visible_by_name"], ["collpart1"])
        self.assertEqual(visible["counts"]["pieces"], 2)

    def test_named_variant_and_explicit_extra_part_are_deterministic(self):
        mesh = mesh_fixture()
        city, city_report = resolve_model_state(mesh, pit_text(), variant=token("city"))
        self.assertEqual(city_report["variant"], "city")
        self.assertEqual(city_report["visible_parts"], ["city_sign", "collpart1"])
        self.assertEqual([item["source_index"] for item in city["locators"]], [1])
        extra, report = resolve_model_state(mesh, pit_text(), additional_parts=(token("city_sign"),))
        repeat, repeat_report = resolve_model_state(mesh, pit_text(), additional_parts=(token("city_sign"),))
        self.assertEqual(report, repeat_report)
        self.assertEqual(extra, repeat)
        self.assertEqual(report["visible_parts"], ["city_sign", "collpart1", "part1"])
        self.assertEqual(report["additional_parts"], ["city_sign"])

    def test_unknown_variant_and_additional_parts_fail_closed(self):
        with self.assertRaisesRegex(StationMeshError, "Unknown or unsupported PIT variant"):
            resolve_model_state(mesh_fixture(), pit_text(), variant=token("winter"))
        with self.assertRaisesRegex(StationMeshError, "Unknown PIT additional-part token"):
            resolve_model_state(mesh_fixture(), pit_text(), additional_parts=(token("unknown"),))

    def test_ambiguous_or_incompatible_ownership_fails_closed(self):
        mesh = mesh_fixture()
        mesh["parts"][1]["pieces"].append(0)
        with self.assertRaisesRegex(StationMeshError, "piece ownership is ambiguous"):
            resolve_model_state(mesh, pit_text())
        mesh = mesh_fixture()
        mesh["parts"][1]["pieces"] = [1]
        mesh["parts"][1]["name"] = "other_part"
        with self.assertRaisesRegex(StationMeshError, "part ownership names disagree"):
            resolve_model_state(mesh, pit_text())

    def test_invalid_visibility_and_duplicate_extra_parts_are_rejected(self):
        with self.assertRaisesRegex(StationMeshError, "unsupported or ambiguous visibility"):
            resolve_model_state(mesh_fixture(), pit_text(default_city_sign=2))
        with self.assertRaisesRegex(StationMeshError, "duplicate tokens"):
            resolve_model_state(mesh_fixture(), pit_text(),
                                additional_parts=(token("city_sign"), token("city_sign")))

    def test_authored_pim_and_pit_fixtures_resolve_together(self):
        parsed = read_station_mesh(pim_text())
        visible, report = resolve_model_state(parsed, pit_text())
        self.assertEqual(report["source_counts"]["pieces"], 3)
        self.assertEqual(report["filtered_counts"]["pieces"], 2)
        self.assertEqual([item["source_index"] for item in visible["locators"]], [0, 1])


if __name__ == "__main__":
    unittest.main()
