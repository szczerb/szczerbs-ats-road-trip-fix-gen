import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ats_road_trip.station_parking import workflow as station_run


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FakePackage:
    def __init__(self, path, *, extractor=None, dlcs=()):
        self.path = Path(path).resolve()
        self.files = {"asset.bin": "asset.bin"}
        if self.path.is_dir():
            self.files = {p.relative_to(self.path).as_posix(): p.relative_to(self.path).as_posix()
                          for p in self.path.rglob("*") if p.is_file()}
        elif self.path.name == "source.scs":
            self.files = {"asset.bin": "asset.bin", "map/usa/sec-0029-0045.base": "map/usa/sec-0029-0045.base"}
        if self.path.name == "base.scs":
            self.files = {"road_trip_fix_report.json": "road_trip_fix_report.json",
                          "def/base.sii": "def/base.sii",
                          "def/preserved.sii": "def/preserved.sii",
                          "map/usa/sec-0029-0045.base": "map/usa/sec-0029-0045.base"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self, path, *, max_bytes=8 * 1024 * 1024):
        if self.path.is_dir():
            return (self.path / path).read_bytes()
        if path == "road_trip_fix_report.json":
            return json.dumps({"processors_enabled": ["fuel"], "analysis": "map_wide_selected_compatibility"}).encode()
        if path == "map/usa/sec-0029-0045.base":
            return b"base-sector" if self.path.name == "base.scs" else b"source-sector"
        if path == "def/base.sii":
            return b"legacy resource at planned path"
        return b"legacy fuel data"


class StationRunTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config_path = self.root / "config.json"
        self.mesh_path = self.root / "mesh.pim"
        self.source = self.root / "source.scs"
        self.dependency = self.root / "dependency.scs"
        self.base_fix = self.root / "base.scs"
        self.installed = self.root / "game"
        self.installed.mkdir()
        (self.installed / "version.sii").write_text("version", encoding="utf-8")
        for path, content in ((self.mesh_path, "mesh data"), (self.source, "source archive"),
                              (self.dependency, "dependency archive"), (self.base_fix, "fuel fix archive")):
            path.write_text(content, encoding="utf-8")
        self.config = {
            "schema_version": 1, "processor": "station_parking", "station_id": "dawson-east",
            "map_name": "Western Canada Expansion", "game_version": "1.61.3.18",
            "method": "painted_bays", "sector": "map/usa/sec-0029-0045.base", "prefab_uid": "0x407eb9",
            "fingerprints": {"source_archive": _sha(self.source), "sector": "a" * 64,
                             "descriptor": "b" * 64, "model_geometry": "c" * 64,
                             "mesh": _sha(self.mesh_path), "base_fix": _sha(self.base_fix)},
            "model_geometry": "prefab/gas/station.pmg",
            "mesh_materials": {"ground": ["ground"], "paint": ["paint"]}, "parameters": {},
        }
        self._write_config()
        self.patches = [
            patch.object(station_run, "REPO_ROOT", self.root / "repo"),
            patch.object(station_run, "Package", FakePackage),
            patch.object(station_run, "_game_directory", lambda _: self.installed),
            patch.object(station_run, "_game_version", lambda *_: "1.61.3.18"),
            patch.object(station_run, "_game_packages", lambda _: ([], ())),
            patch.object(station_run, "write_mod", self._unexpected_writer),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        planner_module = importlib.import_module("ats_road_trip.station_parking")
        self.planner_module = planner_module
        self.planner_patches = [
            patch.object(planner_module, "plan_station_parking", lambda *args, **kwargs: (
                {"coverage": {"complete": True, "blockers": []}, "selected": []},
                {"def/station.sii": b"planned station parking", "def/base.sii": b"planned override"},
            )),
            patch.object(planner_module, "render_station_plan", lambda report: "<svg/>"),
            patch.object(planner_module, "validate_config", lambda config: config),
        ]
        for item in self.planner_patches:
            item.start()
            self.addCleanup(item.stop)

    def _write_config(self):
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    @staticmethod
    def _unexpected_writer(*args, **kwargs):
        raise AssertionError("analysis called write_mod")

    def test_analysis_never_invokes_mod_writer(self):
        self.config["fingerprints"].pop("base_fix")
        self._write_config()
        result = station_run.run_station_parking(
            self.config_path, self.mesh_path, self.source,
            packages=[self.dependency, self.source], run_id="2026-10-19_12-00-00")
        self.assertTrue(result["analysis_only"])
        self.assertEqual(result["generated_mod_count"], 0)
        self.assertEqual(Path(result["plan_svg_path"]).read_text(), "<svg/>")

    def test_generation_requires_ack_and_base_fix_is_fuel_only(self):
        with self.assertRaisesRegex(ValueError, "experimental"):
            station_run.run_station_parking(self.config_path, self.mesh_path, self.source,
                                            packages=[self.source], generate=True)
        package = FakePackage(self.base_fix)
        report = station_run._validate_fuel_base_fix(package)
        self.assertEqual(report["processors_enabled"], ["fuel"])
        package.read = lambda *a, **kw: b'{"analysis":"map_wide_missing_car_fuel","petrol_prices":{}}'
        self.assertEqual(station_run._validate_fuel_base_fix(package)["analysis"],
                         "map_wide_missing_car_fuel")
        package.read = lambda *a, **kw: b'{"processors_enabled":["fuel","rest"]}'
        with self.assertRaisesRegex(ValueError, "fuel as its only topic"):
            station_run._validate_fuel_base_fix(package)

        self.config["fingerprints"]["base_fix"] = "d" * 64
        self._write_config()
        with self.assertRaisesRegex(ValueError, "whole-archive SHA-256"):
            station_run.run_station_parking(self.config_path, self.mesh_path, self.source,
                                            packages=[self.source], base_fix=self.base_fix,
                                            run_id="2026-10-19_12-00-06")

    def test_generation_preserves_base_resources_and_names_station_method(self):
        calls = []
        writer = patch.object(station_run, "write_mod",
                              lambda path, resources, report, **kw:
                              calls.append((Path(path), dict(resources), report, kw)) or {"output": str(path)})
        with writer:
            result = station_run.run_station_parking(
                self.config_path, self.mesh_path, self.source,
                packages=[self.source, self.dependency], base_fix=self.base_fix,
                run_id="2026-10-19_12-00-01", generate=True, experimental=True)
            output, resources, report, options = calls[0]
            self.assertEqual(result["status"], "generated")
            self.assertTrue(output.name.startswith("a-lines-"))
            self.assertTrue(output.name.endswith("dawson-east-painted_bays-1.61-r0-experimental.scs"))
            self.assertEqual(resources["def/preserved.sii"], b"legacy fuel data")
            self.assertEqual(resources["def/base.sii"], b"planned override")
            self.assertEqual(resources["def/station.sii"], b"planned station parking")
            self.assertEqual(report["base_fix_composition"]["base_fix_resource_count"], 3)
            self.assertEqual(report["base_fix_composition"]["preserved_resource_count"], 2)
            self.assertEqual(report["base_fix_composition"]["planner_overrides_on_base_fix"], ["def/base.sii"])
            self.assertTrue(options["display_name"].startswith("A LINES |"))
            self.assertIn("A LINES", options["display_name"][:32])
            self.assertTrue(options["display_name"].endswith("Experimental"))
            self.assertIn("paint-derived marked bays", options["description"].splitlines()[0])
            self.assertIn("grouped area inferred from source-model separators", options["description"])
            self.assertIn("not runtime-confirmed", options["description"])
            self.assertIn("one A/B station-parking variant at a time", options["description"])
            self.assertIn("Includes the pinned fuel baseline", options["description"])
            self.assertIn("replaces the selected map compatibility fix", options["description"])

            self.config["station_id"] = "town-west"
            self.config["method"] = "unmarked_geometry"
            self._write_config()
            station_run.run_station_parking(
                self.config_path, self.mesh_path, self.source,
                packages=[self.source, self.dependency], base_fix=self.base_fix,
                run_id="2026-10-19_12-00-02", generate=True, experimental=True)
            self.assertTrue(calls[1][0].name.startswith("b-geometry-"))
            self.assertTrue(calls[1][0].name.endswith("town-west-unmarked_geometry-1.61-r0-experimental.scs"))
            self.assertNotEqual(calls[1][0].name, output.name)
            second_options = calls[1][3]
            self.assertTrue(second_options["display_name"].startswith("B GEOMETRY |"))
            self.assertIn("B GEOMETRY", second_options["display_name"][:32])
            self.assertIn("3 x 6 m building-side footprint", second_options["description"].splitlines()[1])
            self.assertIn("unmarked building-side geometry proposal", second_options["description"].splitlines()[0])
            self.assertIn("one A/B station-parking variant at a time", second_options["description"])
            self.assertEqual(resources, calls[1][1])

    def test_incomplete_or_empty_plan_never_packages_fuel_baseline(self):
        self.planner_module.plan_station_parking = lambda *args, **kwargs: (
            {"coverage": {"complete": False, "blockers": []}}, {})
        result = station_run.run_station_parking(
            self.config_path, self.mesh_path, self.source, packages=[self.source],
            base_fix=self.base_fix, run_id="2026-10-19_12-00-03",
            generate=True, experimental=True)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["generated_mod_count"], 0)

        self.planner_module.plan_station_parking = lambda *args, **kwargs: (
            {"coverage": {"complete": True, "blockers": []}}, {})
        result = station_run.run_station_parking(
            self.config_path, self.mesh_path, self.source, packages=[self.source],
            base_fix=self.base_fix, run_id="2026-10-19_12-00-04",
            generate=True, experimental=True)
        self.assertEqual(result["status"], "no_changes_unproven")
        self.assertEqual(result["generated_mod_count"], 0)

        self.planner_module.plan_station_parking = lambda *args, **kwargs: (
            {"coverage": {"complete": True, "blockers": []}, "already_covered": True}, {})
        result = station_run.run_station_parking(
            self.config_path, self.mesh_path, self.source, packages=[self.source],
            base_fix=self.base_fix, run_id="2026-10-19_12-00-05",
            generate=True, experimental=True)
        self.assertEqual(result["status"], "already_covered")
        self.assertEqual(result["generated_mod_count"], 0)

    def test_base_fix_alias_contexts_are_repaired_and_mounted_above_it(self):
        prefab_contexts = importlib.import_module("ats_road_trip.prefab_contexts")
        context_path = "def/data_context.station-base.sii"
        context_data = b"station base contexts"

        def preserve(effective, resources, transitions, *, source, map_name):
            self.assertEqual(map_name, "station-parking-fuel-base-dawson-east")
            self.assertEqual(source, self.config["fingerprints"]["source_archive"])
            self.assertEqual(transitions, [("fuel_base", "map/usa/sec-0029-0045.base",
                                            b"source-sector", b"base-sector")])
            return ({"coverage": {"complete": True, "blockers": []}, "aliases": []},
                    {context_path: context_data})

        context_patch = patch.object(prefab_contexts, "plan_prefab_contexts", side_effect=preserve)
        context_patch.start()
        self.addCleanup(context_patch.stop)
        planner_calls = []

        def planner(stack, *args, **kwargs):
            planner_calls.append(stack.read(context_path))
            return ({"coverage": {"complete": True, "blockers": []}, "selected": []},
                    {"def/station.sii": b"planned station parking"})

        self.planner_module.plan_station_parking = planner
        written = []
        with patch.object(station_run, "write_mod", lambda path, resources, report, **kw:
                          written.append((dict(resources), report)) or {"output": str(path)}):
            result = station_run.run_station_parking(
                self.config_path, self.mesh_path, self.source,
                packages=[self.source], base_fix=self.base_fix,
                run_id="2026-10-19_12-00-07", generate=True, experimental=True)
        self.assertEqual(result["status"], "generated")
        self.assertEqual(planner_calls, [context_data])
        self.assertEqual(written[0][0][context_path], context_data)
        self.assertEqual(written[0][1]["baseline_context_preservation"]["coverage"]["complete"], True)

    def test_base_fix_context_blocker_stops_before_station_planner(self):
        prefab_contexts = importlib.import_module("ats_road_trip.prefab_contexts")
        context_patch = patch.object(
            prefab_contexts, "plan_prefab_contexts",
            return_value=({"coverage": {"complete": False,
                                         "blockers": [{"area": "alias_coverage"}]},
                           "aliases": []}, {}))
        context_patch.start()
        self.addCleanup(context_patch.stop)
        self.planner_module.plan_station_parking = lambda *a, **kw: self.fail(
            "station planner ran despite baseline alias-context blocker")
        result = station_run.run_station_parking(
            self.config_path, self.mesh_path, self.source, packages=[self.source],
            base_fix=self.base_fix, run_id="2026-10-19_12-00-08",
            generate=True, experimental=True)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["planner"]["coverage"]["complete"], False)
        self.assertEqual(result["planner"]["baseline_context_preservation"]["coverage"]["blockers"],
                         [{"area": "alias_coverage"}])


if __name__ == "__main__":
    unittest.main()
