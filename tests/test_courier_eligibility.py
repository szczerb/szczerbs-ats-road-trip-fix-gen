"""Small authored definitions exercise the guarded edit without game assets."""

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ats_road_trip.courier_eligibility import (
    plan_courier_eligibility, plan_courier_eligibility_bytes,
    validate_courier_eligibility_config,
)
from ats_road_trip.package import Package, ResourceStack


JOB = b'''SiiNunit {
car_job_data : car_job.paper_0 {
    cargos[]: car_cargo.paper
    vehicle_types[]: sedan // live sedan
    #vehicle_types[]: muscle
    name: "vehicle_types[]: veteran // text"
}
car_job_data : car_job.parts_0 {
    cargos[]: car_cargo.parts
    vehicle_types[]: sedan
}
car_job_data : car_job.jockey_0 {
    vehicle_types[]: sedan
}
car_job_data : car_job.shared_0 {
    cargos[]: car_cargo.paper
    vehicle_types[]: sedan
    vehicle_types[]: muscle
}
}
'''
CARGO = b'''SiiNunit {
car_cargo_data : car_cargo.paper { name: "paper" }
car_cargo_data : car_cargo.parts { name: "parts" }
}
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def config(job=JOB, cargo=CARGO):
    return {
        "schema_version": 1, "profile_id": "fixture", "game_version": "1.61.3.18",
        "job_definition_path": "def/car_job_data.sii", "job_definition_sha256": sha(job),
        "sorted_job_unit_names_sha256": sha(b"car_job.jockey_0\ncar_job.paper_0\ncar_job.parts_0\ncar_job.shared_0\n"),
        "cargo_definition_path": "def/car_cargo.sii", "cargo_definition_sha256": sha(cargo),
        "add_vehicle_type": "muscle", "mustang_vehicle_types": ["muscle", "veteran"],
        "unclassified_policy": "error",
        "empty_cargo_policy": "preserve_listed_transfers_and_error_on_unknown",
        "expected": {"sedan_only_job_units": 3, "cargo_job_units": 2,
                     "classified_cargo_ids": 2, "unchanged_standard_transfer_units": 1,
                     "unchanged_premium_transfer_units": 0, "all_stock_job_units": 4},
        "unchanged": {"vehicle_transfer_job_ids": ["car_job.jockey_0"], "reason": "transfer"},
        "groups": {
            "paper": {"enabled": True, "expected_job_units": 1,
                      "job_family_prefixes": ["car_job.paper_"],
                      "cargo_ids": ["car_cargo.paper"], "review_basis": "small"},
            "parts": {"enabled": False, "expected_job_units": 1,
                      "job_family_prefixes": ["car_job.parts_"],
                      "cargo_ids": ["car_cargo.parts"], "review_basis": "unclear"},
        },
    }


class CourierEligibilityTest(unittest.TestCase):
    def plan(self, job=JOB, cargo=CARGO, cfg=None):
        return plan_courier_eligibility_bytes(job, cargo, config(job, cargo) if cfg is None else cfg,
                                               game_version="1.61.3.18")

    def test_selected_edit_keeps_comments_strings_and_all_other_bytes(self):
        report, resources = self.plan()
        self.assertFalse(report["coverage"]["blockers"])
        self.assertTrue(report["coverage"]["complete"])
        self.assertEqual(report["selected_job_ids"], ["car_job.paper_0"])
        self.assertEqual(report["coverage"]["selected_job_units"], 1)
        self.assertEqual(report["coverage"]["transfer_job_units"], 1)
        self.assertEqual(resources["def/car_job_data.sii"], JOB.replace(
            b"    vehicle_types[]: sedan // live sedan\n",
            b"    vehicle_types[]: sedan // live sedan\n    vehicle_types[]: muscle\n", 1))

    def test_crlf_bom_unicode_and_multiple_insertions_preserve_source(self):
        job = (b"\xef\xbb\xbf" + JOB.replace(
            b"#vehicle_types[]: muscle", "# véhicule_types[]: muscle".encode("utf-8"))
               .replace(b"\n", b"\r\n"))
        cfg = config(job)
        cfg["groups"]["parts"]["enabled"] = True
        report, resources = self.plan(job=job, cfg=cfg)
        self.assertTrue(report["coverage"]["complete"], report["coverage"]["blockers"])
        self.assertEqual(report["selected_job_ids"], ["car_job.paper_0", "car_job.parts_0"])
        expected = job.replace(
            b"    vehicle_types[]: sedan // live sedan\r\n",
            b"    vehicle_types[]: sedan // live sedan\r\n    vehicle_types[]: muscle\r\n", 1)
        expected = expected.replace(
            b"car_job_data : car_job.parts_0 {\r\n    cargos[]: car_cargo.parts\r\n    vehicle_types[]: sedan\r\n",
            b"car_job_data : car_job.parts_0 {\r\n    cargos[]: car_cargo.parts\r\n    vehicle_types[]: sedan\r\n    vehicle_types[]: muscle\r\n", 1)
        self.assertEqual(resources["def/car_job_data.sii"], expected)
        transfer = b"car_job_data : car_job.jockey_0 {\r\n    vehicle_types[]: sedan\r\n}"
        self.assertIn(transfer, resources["def/car_job_data.sii"])

    def test_group_toggle_changes_selection(self):
        cfg = config()
        cfg["groups"]["paper"]["enabled"] = False
        cfg["groups"]["parts"]["enabled"] = True
        report, resources = self.plan(cfg=cfg)
        self.assertFalse(report["coverage"]["blockers"])
        self.assertEqual(report["selected_job_ids"], ["car_job.parts_0"])
        self.assertEqual(resources["def/car_job_data.sii"], JOB.replace(
            b"car_job_data : car_job.parts_0 {\n    cargos[]: car_cargo.parts\n    vehicle_types[]: sedan\n",
            b"car_job_data : car_job.parts_0 {\n    cargos[]: car_cargo.parts\n    vehicle_types[]: sedan\n    vehicle_types[]: muscle\n", 1))

    def test_off_groups_emit_no_replacement(self):
        cfg = config()
        cfg["groups"]["paper"]["enabled"] = False
        report, resources = self.plan(cfg=cfg)
        self.assertFalse(report["coverage"]["blockers"])
        self.assertEqual(resources, {})

    def test_schema_rejects_unknown_and_ambiguous_config(self):
        for mutate in (
            lambda c: c.update(extra=True),
            lambda c: c["groups"]["paper"].update(enabled=1),
            lambda c: c["groups"]["parts"].update(cargo_ids=["car_cargo.paper"]),
            lambda c: c["groups"]["paper"].update(job_family_prefixes=["car_job.parts_"]),
            lambda c: c.update(game_version="1.61"),
        ):
            with self.subTest(mutate=mutate):
                cfg = config()
                mutate(cfg)
                with self.assertRaises(ValueError):
                    validate_courier_eligibility_config(cfg)

    def test_pins_reject_source_or_version_drift(self):
        cfg = config()
        report, resources = self.plan(job=JOB + b"\n", cfg=cfg)
        self.assertEqual(resources, {})
        self.assertFalse(report["coverage"]["complete"])
        self.assertIn("source hash", report["coverage"]["blockers"][0])
        report, resources = plan_courier_eligibility_bytes(JOB, CARGO, cfg,
                                                            game_version="1.61.3.19")
        self.assertEqual(resources, {})
        self.assertIn("version", report["coverage"]["blockers"][0])

    def test_unknown_cargo_and_empty_job_fail_closed(self):
        unknown = JOB.replace(b"cargos[]: car_cargo.paper", b"cargos[]: car_cargo.unknown", 1)
        report, resources = self.plan(unknown)
        self.assertEqual(resources, {})
        self.assertIn("unknown cargo", report["coverage"]["blockers"][0])
        empty = JOB.replace(b"    cargos[]: car_cargo.paper\n", b"", 1)
        report, resources = self.plan(empty)
        self.assertEqual(resources, {})
        self.assertIn("unlisted empty", report["coverage"]["blockers"][0])

    def test_malformed_vehicle_form_fails_closed(self):
        duplicate = JOB.replace(b"    vehicle_types[]: sedan // live sedan\n",
                                b"    vehicle_types[]: sedan // live sedan\n    vehicle_types[]: sedan\n", 1)
        report, resources = self.plan(duplicate)
        self.assertEqual(resources, {})
        self.assertIn("vehicle_types", report["coverage"]["blockers"][0])

    def test_effective_provider_and_duplicate_additive_id(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            low, high, extra = (root / name for name in ("low", "high", "extra"))
            for directory in (low, high, extra):
                (directory / "def").mkdir(parents=True)
            (low / "def/car_job_data.sii").write_bytes(b"stale")
            (high / "def/car_job_data.sii").write_bytes(JOB)
            (high / "def/car_cargo.sii").write_bytes(CARGO)
            stack = ResourceStack([Package(low), Package(high)])
            cfg = config()
            from unittest.mock import patch
            with patch("ats_road_trip.courier_eligibility.tomllib.loads", return_value=cfg):
                path = root / "config.toml"
                path.write_text("fixture")
                report, resources = plan_courier_eligibility(stack, path, game_version="1.61.3.18")
                self.assertFalse(report["coverage"]["blockers"])
                self.assertEqual(report["canonical_providers"]["def/car_job_data.sii"], str(high))
                self.assertEqual(len(report["canonical_overrides"]), 1)
                self.assertTrue(resources)
                (extra / "def/car_job_data.extra.sii").write_bytes(
                    b"SiiNunit { car_job_data : car_job.paper_0 { vehicle_types[]: sedan } }")
                stack = ResourceStack([Package(low), Package(high), Package(extra)])
                report, resources = plan_courier_eligibility(stack, path, game_version="1.61.3.18")
                self.assertEqual(resources, {})
                self.assertIn("duplicate job ID", report["coverage"]["blockers"][0])

    def test_public_planner_rejects_invalid_config_before_resource_lookup(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "invalid.toml"
            path.write_text('job_definition_path = []\n')
            cfg = config()
            cfg["job_definition_path"] = []
            from unittest.mock import patch
            with patch("ats_road_trip.courier_eligibility.tomllib.loads", return_value=cfg):
                with self.assertRaisesRegex(ValueError, "job_definition_path"):
                    plan_courier_eligibility(ResourceStack([]), path, game_version="1.61.3.18")


if __name__ == "__main__":
    unittest.main()
