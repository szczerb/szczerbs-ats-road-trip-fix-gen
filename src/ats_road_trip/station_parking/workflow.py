"""Bounded, source-pinned passenger-car station-parking workflow."""

from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from ..archive import Archive
from ..bulk_run import _game_directory, _game_packages, _game_version
from ..mod_writer import write_mod
from ..package import Package, ResourceStack, virtual_path
from .methods.unmarked import ParkingParameters


REPO_ROOT = Path(__file__).resolve().parents[3]
_RESERVED = {"manifest.sii", "mod_description.txt", "road_trip_fix_report.json", "mod_icon.jpg"}

_VARIANT_METADATA = {
    "painted_bays": {
        "code": "A LINES",
        "slug": "a-lines",
        "method": "paint-derived marked bays, grouped from model separators",
        "footprint": "grouped area inferred from source-model separators; paint visibility is not runtime-confirmed",
    },
    "unmarked_geometry": {
        "code": "B GEOMETRY",
        "slug": "b-geometry",
        "method": "unmarked building-side geometry proposal",
        "footprint": None,
    },
}
_EFFECTIVE_VARIANT_METADATA = {
    "painted_bays": {
        "code": "D MARKED",
        "slug": "d-marked",
        "method": "paint-derived marked bays, grouped from visible effective-model separators",
        "footprint": "grouped area inferred from separators visible in the pinned effective model",
    },
    "unmarked_geometry": {
        "code": "C FORECOURT",
        "slug": "c-forecourt",
        "method": "unmarked forecourt geometry from the pinned effective model",
        "footprint": None,
    },
}


def _station_metadata(config: dict, map_name: str, station_id: str, revision: int = 0) -> dict[str, str]:
    """Build concise, player-facing identity for a station experiment variant."""
    schema_two = config["schema_version"] == 2
    variant = (_EFFECTIVE_VARIANT_METADATA if schema_two else _VARIANT_METADATA)[config["method"]]
    variant_label=variant["code"]+(f" r{revision}" if schema_two else "")
    if config["method"] == "unmarked_geometry":
        parameters = ParkingParameters(**config.get("parameters", {}))
        footprint = f"one proposed {parameters.width:g} x {parameters.depth:g} m building-side footprint"
    else:
        footprint = variant["footprint"]
    baseline_line = (
        "Includes the pinned fuel baseline and replaces the selected map compatibility fix only; "
        "keep other source fixes enabled in their current order."
        if "base_fix" in config.get("fingerprints", {}) else
        "Single-station sector override without a fuel baseline. Follow the reviewed handoff for "
        "source priority and sector conflicts; keep unrelated source fixes in their current order.")
    alternatives = (
        "C FORECOURT and D MARKED are alternative geometry proposals; enable one at a time.\n"
        if schema_two else
        "Test exactly one A/B station-parking variant at a time.\n")
    description = (
        f"{variant_label} — {variant['method']} — station {station_id}.\n"
        f"Footprint: {footprint}.\n"
        f"{alternatives}"
        f"{baseline_line}\n"
        "Experimental for ATS 1.61 / Road Trip Ford; fatigue recovery, clearance and reload remain to be checked.\n"
        "Original archives, game files, and profiles are not modified by this generator.\n")
    return {
        "variant_prefix": variant["slug"],
        "display_name": f"{variant_label} | szczerb's Road Trip Station Parking PoC for {map_name} - {station_id} - Experimental",
        "description": description,
    }
_FIX_REPORT = "road_trip_fix_report.json"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _directory_snapshot(path: Path) -> tuple[tuple[str, int, int, bool], ...]:
    """Record names and file stats without reading potentially huge package data."""
    entries = []
    for item in path.rglob("*"):
        if not item.is_file() and not item.is_symlink():
            continue
        stat = item.stat()
        entries.append((item.relative_to(path).as_posix(), stat.st_size, stat.st_mtime_ns,
                        item.is_symlink()))
    return tuple(sorted(entries))


def _directory_snapshot_report(path: Path, snapshot: tuple[tuple[str, int, int, bool], ...]) -> dict:
    encoded = json.dumps(snapshot, separators=(",", ":")).encode("utf-8")
    return {"path": str(path), "file_count": len(snapshot), "snapshot_sha256": _sha256_bytes(encoded)}


def _verify_directory_snapshots(snapshots: dict[Path, tuple[tuple[str, int, int, bool], ...]]) -> None:
    for path, before in snapshots.items():
        if _directory_snapshot(path) != before:
            raise ValueError(f"Directory package changed during station-parking workflow: {path}")


def _verify_selected_resource(path: Path, virtual: str, physical: str, expected_hash: str,
                              *, extractor: str | Path | None, dlcs: tuple[str, ...]) -> None:
    with Package(path, extractor=extractor, dlcs=dlcs) as package:
        if package.files.get(virtual) != physical:
            raise ValueError(f"Effective model resource selection changed during workflow: {virtual}")
        if _sha256_bytes(package.read(virtual, max_bytes=128 * 1024 * 1024)) != expected_hash:
            raise ValueError(f"Effective model resource changed during workflow: {virtual}")


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")


def _slug(value: str, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError(f"{label} must be a lowercase hyphenated slug")
    return value


def _load_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version", "processor", "station_id", "map_name", "game_version",
        "method", "sector", "prefab_uid", "fingerprints", "model_geometry",
        "mesh_materials", "parameters",
    }
    if isinstance(data, dict) and data.get("schema_version") == 2:
        required.add("material_resources")
    if not isinstance(data, dict) or set(data) != required:
        raise ValueError("Station-parking config must match the schema_version 1 or 2 contract")
    if type(data["schema_version"]) is not int or data["schema_version"] not in (1, 2):
        raise ValueError("Unsupported station-parking config schema_version")
    if data["processor"] != "station_parking":
        raise ValueError("Config processor must be station_parking")
    _slug(data["station_id"], "station_id")
    if not isinstance(data["map_name"], str) or not data["map_name"].strip():
        raise ValueError("map_name must be a nonempty string")
    if data["method"] not in ("painted_bays", "unmarked_geometry"):
        raise ValueError("method must be painted_bays or unmarked_geometry")
    if not isinstance(data["sector"], str) or not data["sector"]:
        raise ValueError("sector must name a source map sector")
    virtual_path(data["sector"])
    if not isinstance(data["prefab_uid"], str) or not re.fullmatch(r"0x[0-9a-fA-F]{1,16}", data["prefab_uid"]):
        raise ValueError("prefab_uid must be a hexadecimal UID string")
    if not isinstance(data["model_geometry"], str) or not data["model_geometry"]:
        raise ValueError("model_geometry must name a pinned virtual model geometry resource")
    virtual_path(data["model_geometry"])
    fingerprints = data["fingerprints"]
    if not isinstance(fingerprints, dict):
        raise ValueError("fingerprints must be an object")
    fingerprint_keys = {"source_archive", "sector", "descriptor", "model_geometry", "mesh"}
    if data["schema_version"] == 2:
        fingerprint_keys |= {"model_definition", "mesh_state"}
    if set(fingerprints) not in (fingerprint_keys, fingerprint_keys | {"base_fix"}):
        raise ValueError("fingerprints do not match the station-parking schema contract")
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
           for value in fingerprints.values()):
        raise ValueError("Fingerprints must be lowercase SHA-256 hex strings")
    if not isinstance(data["mesh_materials"], dict) or not isinstance(data["parameters"], dict):
        raise ValueError("mesh_materials and parameters must be JSON objects")
    from . import validate_config
    return validate_config(data)


def _validate_fuel_base_fix(package: Package) -> dict:
    if _FIX_REPORT not in package.files:
        raise ValueError("Base fix must include road_trip_fix_report.json")
    try:
        report = json.loads(package.read(_FIX_REPORT, max_bytes=8 * 1024 * 1024))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Base fix road_trip_fix_report.json is invalid JSON") from exc
    if not isinstance(report, dict):
        raise ValueError("Base fix report must be a JSON object")
    topic_fields = [report[key] for key in ("processors_enabled", "fix_topics") if key in report]
    analysis = report.get("analysis")
    # Legacy r2 reports predate processors_enabled but identify the fuel-only
    # map analysis and include petrol-price reporting. Reject every report that
    # positively identifies rest processing or parking markers.
    legacy_fuel = analysis == "map_wide_missing_car_fuel" and "petrol_prices" in report
    if topic_fields:
        if any(not isinstance(topics, list) or sorted(topics) != ["fuel"] for topics in topic_fields):
            raise ValueError("Base fix report must identify fuel as its only topic")
    elif not legacy_fuel:
        raise ValueError("Base fix report does not establish a legacy fuel-only r2 package")
    serialized = json.dumps(report, sort_keys=True).lower()
    if "parking_car" in serialized or "standalone_twins" in serialized or "rest_stops" in serialized:
        raise ValueError("Base fix report contains rest or car-parking output")
    return report


def _verify_input_identities(identities: dict[Path, tuple[int, int]],
                             pinned_hashes: dict[Path, str],
                             directory_snapshots: dict[Path, tuple[tuple[str, int, int, bool], ...]] | None = None) -> None:
    _verify_directory_snapshots(directory_snapshots or {})
    for path, before in identities.items():
        if (path.stat().st_size, path.stat().st_mtime_ns) != before:
            raise ValueError(f"Input package changed during station-parking workflow: {path}")
    for path, before in pinned_hashes.items():
        if _sha256_file(path) != before:
            raise ValueError(f"Pinned input changed during station-parking workflow: {path}")


def _write_context_overlay(root: Path, resources: dict[str, bytes]) -> None:
    for name, data in sorted(resources.items()):
        clean = virtual_path(name)
        target = root.joinpath(*clean.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)


def _stable_context_report(report: dict) -> dict:
    """Remove machine-specific package roots from embedded context evidence."""
    stable = json.loads(json.dumps(report))
    for alias in stable.get("aliases", []):
        if not isinstance(alias, dict):
            continue
        for field in ("original_contexts", "existing_alias_contexts"):
            for context in alias.get(field, []):
                if isinstance(context, dict) and isinstance(context.get("package"), str):
                    context["package"] = Path(context["package"]).name
    return stable


def _safe_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not normalized:
        raise ValueError("map_name must contain at least one ASCII letter or digit for the output filename")
    return normalized


def run_station_parking(config_path: str | Path, mesh_path: str | Path, map_package: str | Path,
                        *, packages: list[str | Path], base_fix: str | Path | None = None,
                        game_dir: str | Path | None = None, run_id: str | None = None,
                        extractor: str | Path | None = None, generate: bool = False,
                        revision: int = 0, experimental: bool = False) -> dict:
    """Analyze one pinned station or package its bounded parking candidate.

    ``packages`` is the explicit map/dependency order, lowest to highest; the
    source map must appear exactly once wherever the caller places it. The
    installed ATS files mount first, and an optional fuel-only base fix mounts
    last. No profile state is read or changed.
    """
    if generate and not experimental:
        raise ValueError("Generation requires explicit --experimental acknowledgment")
    if type(revision) is not int or revision < 0:
        raise ValueError("revision must be a nonnegative integer")
    config_path = Path(config_path).expanduser().resolve()
    mesh_path = Path(mesh_path).expanduser().resolve()
    map_path = Path(map_package).expanduser().resolve()
    for label, path in (("config", config_path), ("mesh", mesh_path), ("map archive", map_path)):
        if not path.is_file():
            raise ValueError(f"{label} does not exist: {path}")
    config_hash = _sha256_file(config_path)
    mesh_hash = _sha256_file(mesh_path)
    source_hash = _sha256_file(map_path)
    config = _load_config(config_path)
    schema_two = config["schema_version"] == 2
    if schema_two and generate and revision == 0:
        raise ValueError("Schema-2 behavior experiments require a new revision (at least 1)")
    pit_path = mesh_path.with_suffix(".pit") if schema_two else None
    if pit_path is not None and not pit_path.is_file():
        raise ValueError(f"Schema-version 2 config requires the sibling PIT state file: {pit_path}")
    pit_hash = _sha256_file(pit_path) if pit_path is not None else None
    if schema_two and pit_hash != config["fingerprints"]["mesh_state"]:
        raise ValueError("Converted PIT mesh-state SHA-256 does not match pinned fingerprint")
    input_paths = [config_path, mesh_path, map_path, *([pit_path] if pit_path else [])]
    input_stats = {path: (path.stat().st_size, path.stat().st_mtime_ns) for path in input_paths}
    station_id = _slug(config["station_id"], "station_id")
    map_name = config["map_name"]
    mesh_text = mesh_path.read_text(encoding="utf-8-sig")
    mesh_state_text = pit_path.read_text(encoding="utf-8-sig") if pit_path is not None else None
    stamp = run_id or datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d_%H-%M-%S")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", stamp):
        raise ValueError("run_id must use YYYY-MM-DD_HH-MM-SS")
    work = REPO_ROOT / "local_outputs/work" / stamp / station_id
    metadata = _station_metadata(config, map_name, station_id,revision)
    output = (REPO_ROOT / "local_outputs/generated" / stamp /
              f"{metadata['variant_prefix']}-szczerbs-road-trip-station-parking-{_safe_name(map_name)}-"
              f"{station_id}-{config['method']}-1.61-r{revision}-experimental.scs") if generate else None
    if work.exists() or (output is not None and output.exists()):
        raise FileExistsError("Run audit or generated package already exists; choose a new run_id")
    work.mkdir(parents=True, exist_ok=True)
    prior_work_root = Archive._work_root
    Archive.configure_work_root(work)
    audit_path = work / "audit.json"
    try:
        installed = _game_directory(game_dir)
        version = _game_version(installed, extractor)
        if version != config["game_version"]:
            raise ValueError("Installed ATS version does not match the pinned config game_version")
        game_paths, dlcs = _game_packages(installed)
        explicit = [Path(item).expanduser().resolve() for item in packages]
        game_paths=[Path(path).resolve() for path in game_paths]
        if any(not path.is_file() and not path.is_dir() for path in explicit):
            raise ValueError("Every explicit --package must be an existing archive or package directory")
        if len(set(explicit))!=len(explicit) or any(path in game_paths for path in explicit):
            raise ValueError("Do not repeat an installed game package or duplicate an explicit package")
        if map_path not in game_paths and sum(path == map_path for path in explicit) != 1:
            raise ValueError("--map-package must appear exactly once in the explicit LOW-HIGH --package order")
        base_path = Path(base_fix).expanduser().resolve() if base_fix is not None else None
        if base_path is not None and (not base_path.is_file() or base_path in explicit or base_path == map_path):
            raise ValueError("--base-fix must be a separate existing package")
        if (base_path is None) != ("base_fix" not in config["fingerprints"]):
            raise ValueError("Config fingerprints.base_fix must be present exactly when --base-fix is supplied")
        expected = config["fingerprints"]
        if source_hash != expected["source_archive"]:
            raise ValueError("Source archive SHA-256 does not match pinned fingerprint")
        if mesh_hash != expected["mesh"]:
            raise ValueError("Converted mesh SHA-256 does not match pinned fingerprint")
        if base_path is not None:
            base_hash = _sha256_file(base_path)
            if base_hash != expected["base_fix"]:
                raise ValueError("Base-fix whole-archive SHA-256 does not match pinned fingerprint")
        else:
            base_hash = None
        package_paths = [*game_paths, *explicit, *([base_path] if base_path else [])]
        directory_snapshots = {path: _directory_snapshot(path) for path in package_paths if path.is_dir()}
        version_input = installed / "version.sii" if (installed / "version.sii").is_file() else installed / "version.scs"
        identity_paths = list(dict.fromkeys([version_input, *package_paths]))
        identities = {**input_stats,
                      **{path: (path.stat().st_size, path.stat().st_mtime_ns) for path in identity_paths}}
        pinned_hashes = {config_path: config_hash, mesh_path: mesh_hash, map_path: source_hash}
        if pit_path is not None:
            pinned_hashes[pit_path] = pit_hash
        if base_path is not None:
            pinned_hashes[base_path] = base_hash
        workflow = {
            "run_id": stamp, "station_id": station_id, "map_name": map_name,
            "game_version": version, "method": config["method"],
            "analysis_only": not generate,
            "packages_low_to_high": [str(path) for path in package_paths],
            "source_map_package": str(map_path), "mesh_path": str(mesh_path),
            "mesh_state_path": str(pit_path) if pit_path else None,
            "directory_package_snapshots": [_directory_snapshot_report(path, snapshot)
                                             for path, snapshot in sorted(directory_snapshots.items())],
            "base_fix": str(base_path) if base_path else None,
            "input_identities_stat": [{"path": str(path), "size": size, "mtime_ns": mtime}
                                       for path, (size, mtime) in identities.items()],
        }
        with ExitStack() as manager:
            mounted = [manager.enter_context(Package(path, extractor=extractor, dlcs=dlcs))
                       for path in package_paths]
            base_resources = {}
            original_base_paths = set()
            context_resources = {}
            baseline_context_report = None
            if base_path is not None:
                base_package = mounted[-1]
                base_report = _validate_fuel_base_fix(base_package)
                for virtual in sorted(base_package.files):
                    if virtual not in _RESERVED:
                        base_resources[virtual] = base_package.read(virtual, max_bytes=128 * 1024 * 1024)
                original_base_paths = set(base_resources)
                raw_stack = ResourceStack(mounted[:-1])
                transitions = []
                missing_source_sectors = []
                for virtual in sorted(base_resources):
                    if not virtual.startswith("map/") or not virtual.endswith((".base", ".aux")):
                        continue
                    if virtual not in raw_stack.resources:
                        missing_source_sectors.append(virtual)
                        continue
                    before = raw_stack.read(virtual, max_bytes=64 * 1024 * 1024)
                    after = base_resources[virtual]
                    transitions.append(("fuel_base", virtual, before, after))
                if missing_source_sectors:
                    baseline_context_report = {
                        "schema_version": 1,
                        "analysis": "generated_prefab_context_preservation",
                        "aliases": [], "blockers": [
                            {"area": "baseline_sector_lineage", "path": path,
                             "reason": "Fuel baseline sector has no corresponding raw effective source sector"}
                            for path in missing_source_sectors],
                        "coverage": {"complete": False, "blockers": [
                            {"area": "baseline_sector_lineage", "path": path,
                             "reason": "Fuel baseline sector has no corresponding raw effective source sector"}
                            for path in missing_source_sectors]},
                    }
                else:
                    from ..prefab_contexts import plan_prefab_contexts
                    baseline_context_report, context_resources = plan_prefab_contexts(
                        raw_stack, base_resources, transitions,
                        source=expected["source_archive"],
                        map_name="station-parking-fuel-base-" + station_id)
                baseline_coverage = baseline_context_report.get("coverage", {})
                baseline_blockers = baseline_coverage.get("blockers", baseline_context_report.get("blockers", []))
                if baseline_coverage.get("complete") is not True or baseline_blockers:
                    _verify_input_identities(identities, pinned_hashes, directory_snapshots)
                    planner_report = {"coverage": {"complete": False,
                                                    "blockers": baseline_blockers or [{
                                                        "area": "baseline_context_preservation",
                                                        "reason": "Baseline context coverage is incomplete"}]},
                                      "baseline_context_preservation": _stable_context_report(baseline_context_report)}
                    audit = {"status": "blocked", "analysis_only": not generate,
                             "in_game_verified": False,
                             "workflow": {**workflow, "work_dir": str(work)},
                             "planner": planner_report, "planned_resource_count": 0,
                             "composed_resource_count": len(base_resources),
                             "generated_mod_count": 0, "report_path": str(audit_path),
                             "plan_svg_path": None}
                    _write_json(audit_path, audit)
                    return audit
                if context_resources:
                    context_root = work / "baseline-context-overlay"
                    _write_context_overlay(context_root, context_resources)
                    context_package = manager.enter_context(
                        Package(context_root, extractor=extractor, dlcs=dlcs))
                    mounted.append(context_package)
                    base_resources.update(context_resources)
            stack = ResourceStack(mounted)
            selected_model_definition = None
            model_definition_hash = None
            if schema_two:
                model_definition_path = virtual_path(str(Path(config["model_geometry"]).with_suffix(".pmd")))
                selected = stack.resources.get(model_definition_path)
                if selected is None:
                    raise ValueError(f"Effective model definition is missing from the package stack: {model_definition_path}")
                selected_package, selected_resource = selected
                model_definition_bytes = stack.read(model_definition_path, max_bytes=128 * 1024 * 1024)
                model_definition_hash = _sha256_bytes(model_definition_bytes)
                if model_definition_hash != config["fingerprints"]["model_definition"]:
                    raise ValueError("Effective model-definition SHA-256 does not match pinned fingerprint")
                selected_model_definition = (selected_package.path, model_definition_path,
                                             selected_resource.physical_path, model_definition_hash)
                workflow["model_definition_path"] = model_definition_path
                workflow["model_definition_source"] = str(selected_package.path)
                workflow["model_definition_sha256"] = model_definition_hash
            directory_resource_pins=[]
            if schema_two:
                for virtual,expected_hash in sorted(config["material_resources"].items()):
                    selected=stack.resources.get(virtual)
                    if selected and selected[0].path.is_dir():
                        directory_resource_pins.append((selected[0].path / selected[1].physical_path,expected_hash))
                virtual=config["model_geometry"]
                selected=stack.resources.get(virtual)
                if selected and selected[0].path.is_dir():
                    directory_resource_pins.append((selected[0].path / selected[1].physical_path,config["fingerprints"]["model_geometry"]))
            from . import plan_station_parking, render_station_plan
            if schema_two:
                planner_report, planned_resources = plan_station_parking(
                    stack, config, mesh_text, map_package=str(map_path), game_version=version,
                    mesh_state_text=mesh_state_text)
            else:
                planner_report, planned_resources = plan_station_parking(
                    stack, config, mesh_text, map_package=str(map_path), game_version=version)
            _verify_input_identities(identities, pinned_hashes, directory_snapshots)
            if selected_model_definition is not None:
                _verify_selected_resource(*selected_model_definition, extractor=extractor, dlcs=dlcs)
        if not isinstance(planner_report, dict) or not isinstance(planned_resources, dict):
            raise ValueError("Station planner returned an invalid report/resources pair")
        _verify_input_identities(identities, pinned_hashes, directory_snapshots)
        if selected_model_definition is not None:
            _verify_selected_resource(*selected_model_definition, extractor=extractor, dlcs=dlcs)
        # Stable provenance inside the package excludes machine paths, run IDs,
        # mtimes and the work/output directory. The external audit retains those.
        base_overlaps = sorted(original_base_paths & set(planned_resources))
        context_overlaps = sorted(set(context_resources) & set(planned_resources))
        composed = {**base_resources, **planned_resources}
        planner_report = dict(planner_report)
        planner_report["base_fix_composition"] = {
            "enabled": base_path is not None,
            "base_fix_resource_count": len(original_base_paths),
            "preserved_resource_count": len(original_base_paths) - len(base_overlaps),
            "planner_overrides_on_base_fix": base_overlaps,
            "baseline_context_overlay_resource_count": len(context_resources),
            "planner_overrides_on_baseline_context_overlay": context_overlaps,
            "base_fix_topics": ["fuel"] if base_path is not None else [],
            "manual_fuel_validation_required": base_path is not None,
        }
        if baseline_context_report is not None:
            planner_report["baseline_context_preservation"] = _stable_context_report(baseline_context_report)
        if isinstance(planner_report.get("context_preservation"), dict):
            planner_report["context_preservation"] = _stable_context_report(
                planner_report["context_preservation"])
        provenance = {
            "input_fingerprints": {key: value for key, value in sorted(expected.items())},
            "package_basenames_low_to_high": [path.name for path in package_paths],
            "station_id": station_id, "map_name": map_name,
            "game_version": version, "method": config["method"],
            "base_fix_report_analysis": base_report.get("analysis") if base_path else None,
        }
        planner_report["workflow"] = provenance
        coverage = planner_report.get("coverage")
        if not isinstance(coverage, dict):
            raise ValueError("Planner coverage must be an object")
        complete = coverage.get("complete") is True
        blockers = coverage.get("blockers", [])
        if not isinstance(blockers, list):
            raise ValueError("Planner coverage.blockers must be a list")
        svg = render_station_plan(planner_report)
        (work / "plan.svg").write_text(svg, encoding="utf-8")
        already_covered = (planner_report.get("already_covered") is True
                           or planner_report.get("state") == "already_covered")
        if not complete or blockers:
            status = "reported_partial"
        elif not planned_resources:
            status = "already_covered" if already_covered else "no_changes_unproven"
        else:
            status = "reported"
        audit = {"status": status,
                 "analysis_only": not generate, "in_game_verified": False,
                 "workflow": {**workflow, "work_dir": str(work)},
                 "planner": planner_report,
                 "planned_resource_count": len(planned_resources),
                 "composed_resource_count": len(composed),
                 "generated_mod_count": 0,
                 "report_path": str(audit_path), "plan_svg_path": str(work / "plan.svg")}
        if not generate or not complete or blockers or not planned_resources:
            if generate and (not complete or blockers):
                audit["status"] = "blocked"
            elif generate and not planned_resources and not already_covered:
                audit["status"] = "no_changes_unproven"
            _write_json(audit_path, audit)
            return audit
        stable_report = {k: v for k, v in planner_report.items() if k not in ("workflow_path", "work_dir")}
        _verify_input_identities(identities, pinned_hashes, directory_snapshots)
        if selected_model_definition is not None:
            _verify_selected_resource(*selected_model_definition, extractor=extractor, dlcs=dlcs)
        for resource_path,expected_hash in directory_resource_pins:
            if _sha256_file(resource_path)!=expected_hash:
                raise ValueError("Effective directory model/material SHA-256 drift before packaging")
        written = write_mod(output, composed, stable_report, game_version=version,
                            display_name=metadata["display_name"],
                            description=metadata["description"], revision=revision, category="map")
        audit.update({"status": "generated", "output": str(output),
                      "generated_mod_count": 1, "written_report": written})
        _write_json(audit_path, audit)
        return audit
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        if not audit_path.exists():
            _write_json(audit_path, {"status": "failed", "analysis_only": not generate,
                                     "station_id": station_id, "map_name": map_name,
                                     "run_id": stamp, "error": str(exc)})
        raise
    finally:
        Archive.configure_work_root(prior_work_root)
