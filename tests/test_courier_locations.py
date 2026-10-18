"""Authored sector fixtures for read-only courier location reporting."""

import struct
import tempfile
import unittest
from pathlib import Path

from ats_road_trip.courier_locations import plan_courier_report
from ats_road_trip.local_fuel import token
from ats_road_trip.package import Package, ResourceStack


HEADER = struct.pack("<IQI", 907, token("euro2"), 3)


def refs(*values):
    return struct.pack("<I", len(values)) + b"".join(struct.pack("<Q", value) for value in values)


def item(kind, uid, payload=b""):
    return struct.pack("<IQ10fIB", kind, uid, *([0.] * 5 + [10.] * 5), 0x80000000, 4) + payload


def node(uid, owner):
    return struct.pack("<Q3i4fQQI", uid, 256, 512, 768, 1., 0., 0., 0., 0, owner, 0)


def sector(items, nodes=()):
    return HEADER + struct.pack("<I", len(items)) + b"".join(items) + struct.pack("<I", len(nodes)) + b"".join(nodes) + refs()


def descriptor():
    header = [0] * 24
    header[0], header[5], header[12] = 25, 1, 96
    for index in range(13, 17):
        header[index] = 96
    for index in range(17, 24):
        header[index] = 132
    return struct.pack("<24I", *header) + struct.pack("<7fII", *([0.] * 7), 13, 0)


class CourierLocationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def put(self, package, path, data):
        target = self.root / package / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data.encode() if isinstance(data, str) else data)

    def stack(self):
        (self.root / "base").mkdir(exist_ok=True)
        baseline = Package(self.root / "base")
        source = Package(self.root / "map")
        self.addCleanup(baseline.close)
        self.addCleanup(source.close)
        return ResourceStack([baseline, source]), {str(source.path)}

    def test_source_company_resolves_effective_editor_context_and_marker(self):
        prefab = item(4, 100, struct.pack("<QQ", token("shop"), 0) + refs() + refs(11, 12)
                      + refs(200) + struct.pack("<QH", 0, 0) + bytes(2 * 12 + 8))
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 100, token("market"), 21)
                       + refs(22) + struct.pack("<I", 1))
        self.put("map", "map/usa/sec+0000+0000.base", sector([prefab, company],
                 [node(21, 200), node(22, 200)]))
        self.put("base", "def/company/market/editor/alpha.sii", """SiiNunit {
company_def : .alpha { city: alpha prefab: other }
}""")
        self.put("map", "def/company/market/editor/alpha.dlc_ok.sii", """SiiNunit {
company_def : .alpha { city: alpha prefab: shop }
}""")
        self.put("base", "def/data_context.sii", """SiiNunit {
data_context : context.shop { target_data[]: prefab.shop tags[]: retail }
}""")
        self.put("base", "def/car_job_data.sii", """SiiNunit {
car_job_data : car_job.test { source_data_contexts[]: retail }
}""")
        self.put("base", "def/world/prefab.sii", """SiiNunit {
prefab_model : prefab.shop { prefab_desc: \"/prefab/shop.ppd\" }
}""")
        self.put("base", "prefab/shop.ppd", descriptor())
        stack, map_packages = self.stack()
        report = plan_courier_report(stack, map_packages=map_packages, map_name="Test Map")
        self.assertTrue(report["analysis_only"])
        self.assertFalse(report["in_game_verified"])
        self.assertEqual(report["counts"]["locations"], 1)
        record = report["locations"][0]
        self.assertEqual((record["company_token"], record["city_token"]), ("market", "alpha"))
        self.assertEqual(record["company_item_flags"], "0x80000000")
        self.assertTrue(record["company_definition"]["source"]["virtual_path"].endswith("alpha.dlc_ok.sii"))
        self.assertEqual(record["company_definition"]["matching_city_candidates"], 2)
        self.assertEqual(record["activation_node"]["position"], [1., 2., 3.])
        self.assertEqual(record["spawn_nodes"][0]["flags"], "0x1")
        self.assertEqual(record["context"]["source_job_definitions"], ["car_job.test"])
        self.assertEqual(record["prefab_descriptor"]["spawn_types"], {"13": 1})
        self.assertEqual(record["marker_evidence"]["ppd_company_point_count"], 1)
        self.assertEqual(record["marker_evidence"]["courier_specific_interpretation"], "unknown")
        self.assertEqual(record["courier_market_eligibility"], "unknown")
        self.assertEqual(record["static_linkage"], "resolved")
        self.assertEqual(len(record["source_sector"]["sha256"]), 64)

    def test_missing_links_and_unsupported_sector_are_partial_not_no_jobs(self):
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 999, token("market"), 21)
                       + refs(22) + struct.pack("<I", 0))
        self.put("map", "map/usa/sec+0000+0000.base", sector([company]))
        self.put("map", "map/usa/sec+0001+0000.base", b"unsupported")
        stack, map_packages = self.stack()
        report = plan_courier_report(stack, map_packages=map_packages)
        self.assertFalse(report["coverage"]["complete"])
        self.assertEqual(report["counts"]["locations"], 1)
        record = report["locations"][0]
        self.assertIn("prefab_reference_unresolved", record["unknowns"])
        self.assertEqual(record["courier_market_eligibility"], "unknown")
        self.assertEqual(record["static_linkage"], "partial")
        self.assertTrue(report["coverage"]["blocked_sectors"])
        self.assertTrue(report["coverage"]["blockers"])

    def test_placed_prefab_drives_context_and_descriptor_when_editor_disagrees(self):
        prefab = item(4, 100, struct.pack("<QQ", token("shop"), 0) + refs() + refs(11, 12)
                      + refs() + struct.pack("<QH", 0, 0) + bytes(2 * 12 + 8))
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 100, token("market"), 21) + refs())
        self.put("map", "map/usa/sec+0000+0000.base", sector([prefab, company], [node(21, 200)]))
        self.put("map", "def/company/market/editor/alpha.sii", """SiiNunit {
company_def : .alpha { city: alpha prefab: other }
}""")
        self.put("base", "def/data_context.sii", """SiiNunit {
data_context : context.other { target_data[]: prefab.other tags[]: retail }
}""")
        self.put("base", "def/car_job_data.sii", """SiiNunit {
car_job_data : car_job.test { source_data_contexts[]: retail }
}""")
        self.put("base", "def/world/prefab.sii", """SiiNunit {
prefab_model : prefab.shop { prefab_desc: \"/prefab/shop.ppd\" }
prefab_model : prefab.other { prefab_desc: \"/prefab/other.ppd\" }
}""")
        self.put("base", "prefab/shop.ppd", descriptor())
        stack, map_packages = self.stack()
        record = plan_courier_report(stack, map_packages=map_packages)["locations"][0]
        self.assertEqual(record["context"]["prefab"], "prefab.shop")
        self.assertEqual(record["context"]["status"], "unclassified")
        self.assertEqual(record["editor_context"]["prefab"], "prefab.other")
        self.assertEqual(record["editor_context"]["status"], "classified")
        self.assertEqual(record["prefab_definition"]["descriptor_path"], "/prefab/shop.ppd")
        self.assertIn("editor_prefab_model_mismatch", record["unknowns"])

    def test_excluded_context_and_duplicate_definitions_are_explicit(self):
        prefab = item(4, 100, struct.pack("<QQ", token("shop"), 0) + refs() + refs(11, 12)
                      + refs() + struct.pack("<QH", 0, 0) + bytes(2 * 12 + 8))
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 100, token("market"), 21) + refs())
        self.put("map", "map/usa/sec+0000+0000.base", sector([prefab, company], [node(21, 200)]))
        self.put("map", "def/company/market/editor/alpha.sii", """SiiNunit {
company_def : .alpha { city: alpha prefab: shop }
}""")
        self.put("base", "def/data_context.sii", """# prefab.shop deliberately excluded
SiiNunit { data_context : context.duplicate { target_data[]: prefab.shop tags[]: retail } }""")
        self.put("map", "def/data_context.extra.sii", """SiiNunit {
data_context : context.duplicate { target_data[]: prefab.shop tags[]: retail }
}""")
        self.put("base", "def/car_job_data.sii", """SiiNunit {
car_job_data : car_job.test { source_data_contexts[]: retail }
}""")
        self.put("map", "def/car_job_data.extra.sii", """SiiNunit {
car_job_data : car_job.test { source_data_contexts[]: retail }
}""")
        self.put("base", "def/world/prefab.sii", """SiiNunit {
prefab_model : prefab.shop { prefab_desc: \"/prefab/shop.ppd\" }
}""")
        self.put("base", "prefab/shop.ppd", descriptor())
        stack, map_packages = self.stack()
        report = plan_courier_report(stack, map_packages=map_packages)
        self.assertEqual(report["locations"][0]["context"]["status"], "explicitly_excluded")
        self.assertFalse(report["coverage"]["complete"])
        self.assertTrue(any("Duplicate data_context" in b["reason"]
                            for b in report["coverage"]["definition_blockers"]))
        self.assertTrue(any("Duplicate car_job_data" in b["reason"]
                            for b in report["coverage"]["definition_blockers"]))

    def test_identical_node_copy_in_neighbor_resolves(self):
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 999, token("market"), 21) + refs())
        self.put("map", "map/usa/sec+0000+0000.base", sector([company]))
        self.put("base", "map/usa/sec+0001+0000.base", sector([], [node(21, 200)]))
        self.put("base", "map/usa/sec+0000+0001.base", sector([], [node(21, 200)]))
        stack, map_packages = self.stack()
        record = plan_courier_report(stack, map_packages=map_packages)["locations"][0]
        self.assertEqual(record["activation_node"]["status"], "resolved")

    def test_nested_company_is_explicit_coverage_blocker(self):
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 999, token("market"), 21) + refs())
        compound = item(0x28, 400, struct.pack("<Q", 12) + struct.pack("<I", 1)
                        + company + struct.pack("<I", 1) + node(21, 200))
        self.put("map", "map/usa/sec+0000+0000.base", sector([compound]))
        stack, map_packages = self.stack()
        report = plan_courier_report(stack, map_packages=map_packages)
        self.assertEqual(report["coverage"]["nested_company_items"], 1)
        self.assertFalse(report["coverage"]["complete"])
        self.assertTrue(any("compound-contained company" in b["reason"]
                            for b in report["coverage"]["blockers"]))

    def test_two_exact_editor_candidates_are_ambiguous(self):
        prefab = item(4, 100, struct.pack("<QQ", token("shop"), 0) + refs() + refs(11, 12)
                      + refs() + struct.pack("<QH", 0, 0) + bytes(2 * 12 + 8))
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 100, token("market"), 21) + refs())
        self.put("map", "map/usa/sec+0000+0000.base", sector([prefab, company], [node(21, 200)]))
        for filename in ("alpha.sii", "alpha.dlc_ok.sii"):
            self.put("map", f"def/company/market/editor/{filename}", """SiiNunit {
company_def : .alpha { city: alpha prefab: shop }
}""")
        stack, map_packages = self.stack()
        record = plan_courier_report(stack, map_packages=map_packages)["locations"][0]
        self.assertEqual(record["company_definition"]["status"], "ambiguous")
        self.assertEqual(record["company_definition"]["candidate_count"], 2)
        self.assertEqual(len(record["company_definition"]["candidates"]), 2)
        self.assertIn("company_definition_ambiguous", record["unknowns"])

    def test_included_sui_company_unit_is_indexed_once(self):
        company = item(6, 200, struct.pack("<4Q", token("alpha"), 999, token("market"), 21) + refs())
        self.put("map", "map/usa/sec+0000+0000.base", sector([company], [node(21, 200)]))
        self.put("map", "def/company/market/editor/alpha.sii", """SiiNunit {
@include "alpha.sui"
}""")
        self.put("map", "def/company/market/editor/alpha.sui", """company_def : .alpha {
city: alpha
prefab: shop
}""")
        stack, map_packages = self.stack()
        record = plan_courier_report(stack, map_packages=map_packages)["locations"][0]
        self.assertEqual(record["company_definition"]["status"], "resolved")
        self.assertEqual(record["company_definition"]["matching_city_candidates"], 1)
        self.assertEqual(record["company_definition"]["source"]["virtual_path"],
                         "def/company/market/editor/alpha.sii")

    def test_two_company_items_share_parent_prefab_without_vehicle_inference(self):
        prefab = item(4, 100, struct.pack("<QQ", token("shop"), 0) + refs() + refs(11, 12)
                      + refs(200, 201) + struct.pack("<QH", 0, 0) + bytes(2 * 12 + 8))
        company_a = item(6, 200, struct.pack("<4Q", token("alpha"), 100, token("market"), 21) + refs())
        company_b = item(6, 201, struct.pack("<4Q", 0, 100, token("market"), 22) + refs())
        self.put("map", "map/usa/sec+0000+0000.base",
                 sector([prefab, company_a, company_b], [node(21, 200), node(22, 201)]))
        stack, map_packages = self.stack()
        report = plan_courier_report(stack, map_packages=map_packages)
        self.assertEqual(report["shared_prefab_companies"][0]["company_item_uids"], ["0xc8", "0xc9"])
        self.assertTrue(all("multiple_company_items_for_prefab" in record["unknowns"]
                            for record in report["locations"]))
        self.assertIn("company_city_token_unresolved", report["locations"][1]["unknowns"])
        self.assertNotIn("invalid_or_empty_company_city_token", report["locations"][1]["unknowns"])


if __name__ == "__main__":
    unittest.main()
