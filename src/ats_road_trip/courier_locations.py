"""Location-aware, read-only courier inputs from effective ATS map resources.

This is an inventory of placed companies and the static inputs around them.
Neither a context match nor a map marker proves that the market offers a job.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import re
from zoneinfo import ZoneInfo

from .archive import Archive
from .map_sector import SectorFormatError, parse_sector
from .package import ResourceStack
from .ppd import PpdError, inspect_ppd
from .sii import DefinitionError, parse_units


_SECTOR = re.compile(r"(map/[^/]+/)sec([+-]\d{4})([+-]\d{4})\.(base|aux)")
_CONTEXT = r"def/data_context(?:\.[^/]+)?\.sii"
_JOB = r"def/car_job_data(?:\.[^/]+)?\.sii"
_PREFAB = r"def/world/prefab(?:\.[^/]+)?\.sii"
_TOKEN_ALPHABET = "\0" + "0123456789abcdefghijklmnopqrstuvwxyz_"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _token(number: int) -> str | None:
    if not number:
        return None
    chars = []
    while number:
        number, digit = divmod(number, 38)
        if not 0 < digit < len(_TOKEN_ALPHABET):
            return None
        chars.append(_TOKEN_ALPHABET[digit])
    return "".join(chars) if len(chars) <= 12 else None


def _resource(stack: ResourceStack, path: str, data: bytes | None = None) -> dict:
    _, item = stack.resources[path]
    if data is None:
        data = stack.read(path, max_bytes=64 * 1024 * 1024)
    return {"virtual_path": path, "package": item.package,
            "physical_path": item.physical_path, "sha256": _sha(data)}


def _prefetch(stack: ResourceStack, paths: list[str]) -> None:
    grouped = defaultdict(list)
    for path in paths:
        grouped[stack.resources[path][0]].append(path)
    for package, names in grouped.items():
        if package.archive and package.archive.format.startswith("hashfs"):
            cache = Archive._scratch_root().parent / "package-cache" / _sha(str(package.path).encode())[:12]
            package.prefetch(names, disk_cache=cache, max_bytes=64 * 1024 * 1024)


def _units(stack: ResourceStack, pattern: str, kind: str, blockers: list[dict]) -> list:
    paths = stack.matching(pattern)
    _prefetch(stack, paths)
    result = []
    for path in paths:
        try:
            result.extend(unit for unit in parse_units(stack.text(path), source=path,
                                                       include_reader=stack.text) if unit.kind == kind)
        except (DefinitionError, KeyError, UnicodeError, ValueError) as exc:
            blockers.append({"path": path, "reason": str(exc)})
    return result


def _node_record(uid: int, nodes: dict[int, list[tuple[str, object]]]) -> dict:
    matches = nodes.get(uid, [])
    if not uid:
        return {"uid": "0x0", "status": "absent"}
    if len(matches) > 1:
        signatures = {(node.position, node.rotation, node.backward, node.forward, node.flags)
                      for _, node in matches}
        if len(signatures) == 1:
            matches = matches[:1]
    if len(matches) != 1:
        return {"uid": hex(uid), "status": "unresolved" if not matches else "ambiguous"}
    path, node = matches[0]
    return {"uid": hex(uid), "status": "resolved", "position": list(node.position),
            "sector": path}


def _neighbors(paths: set[str]) -> set[str]:
    result = set()
    for path in paths:
        match = _SECTOR.fullmatch(path)
        if not match:
            continue
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for ext in ("base", "aux"):
                    result.add(f"{match[1]}sec{int(match[2])+dx:+05d}{int(match[3])+dz:+05d}.{ext}")
    return result - paths


def _nested_company_count(items: tuple) -> int:
    count = 0
    for item in items:
        if item.kind == 0x28:
            children = item.details["items"]
            count += sum(child.kind == 6 for child in children)
            count += _nested_company_count(children)
    return count


def plan_courier_report(stack: ResourceStack, *, map_packages: set[str],
                        map_name: str = "map") -> dict:
    """Report company placements in source-owned sectors; produce no resources.

    A one-sector halo supplies only local references. Missing links beyond it
    remain unknown. Package order is the caller's explicit low-to-high order.
    """
    report = {
        "schema_version": 1, "analysis": "courier_locations", "analysis_only": True,
        "in_game_verified": False, "map_name": map_name,
        "inspection_date": datetime.now(ZoneInfo("Europe/Warsaw")).date().isoformat(),
        "ats_version": None,
        "package_order": [str(package.path) for package in stack.packages],
        "map_packages": sorted(map_packages), "locations": [], "source_resources": [],
        "shared_prefab_companies": [],
        "definition_sources": [],
        "format_basis": [
            "https://github.com/sk-zk/TruckLib/blob/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/Serialization/CompanySerializer.cs",
            "https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators#Spawn_Point",
        ],
        "coverage": {"source_sectors": 0, "source_sectors_parsed": 0,
                     "neighbor_sectors_parsed": 0, "company_placements": 0,
                     "nested_company_items": 0,
                     "blocked_sectors": [], "definition_blockers": [],
                     "blockers": [], "complete": False},
        "limitations": [
            "Only effective .base/.aux sectors supplied by selected map packages are source targets.",
            "A one-sector halo resolves nearby references; unresolved links may exist beyond it.",
            "Context and job definitions are static inputs, not proof of courier offers or playable pickup/delivery.",
            "Company activation and spawn nodes do not establish car versus truck market semantics.",
            "SCS's Company Point locator describes general delivery check-in, not confirmed ATS Road Trip courier behavior.",
            "Prefab unit source paths identify the parsed root file; definition_sources fingerprints all included prefab inputs without attributing individual included units.",
            "No game/profile market state, route availability, rating, vehicle, or delivery was tested.",
        ],
    }
    coverage = report["coverage"]
    source_paths = {path for path in stack.matching(_SECTOR.pattern)
                    if str(stack.resources[path][0].path) in map_packages}
    coverage["source_sectors"] = len(source_paths)
    if not source_paths:
        coverage["blocked_sectors"].append({"reason": "No effective source-owned .base/.aux sectors"})
        coverage["blockers"] = [{"area": "source_sectors", **coverage["blocked_sectors"][0]}]
        return report
    sectors: dict[str, object] = {}
    sector_data: dict[str, bytes] = {}
    _prefetch(stack, sorted(source_paths))
    for path in sorted(source_paths):
        try:
            data = stack.read(path, max_bytes=64 * 1024 * 1024)
            parsed = parse_sector(data)
            sector_data[path], sectors[path] = data, parsed
            coverage["source_sectors_parsed"] += 1
            nested_count = _nested_company_count(parsed.items)
            coverage["nested_company_items"] += nested_count
            if nested_count:
                coverage["blocked_sectors"].append({"path": path, "role": "nested_company",
                    "reason": f"{nested_count} compound-contained company item(s) require scoped node resolution"})
            if nested_count or any(item.kind == 6 for item in parsed.items):
                report["source_resources"].append(_resource(stack, path, data))
        except (SectorFormatError, KeyError, ValueError) as exc:
            coverage["blocked_sectors"].append({"path": path, "reason": str(exc)})

    # Inspect neighboring sectors only where a placement has an unresolved
    # prefab or node reference in the source-owned sector set.
    company_paths = {path for path in source_paths if path in sectors
                     and any(item.kind == 6 for item in sectors[path].items)}
    source_prefabs = {item.uid for sector in sectors.values() for item in sector.prefabs}
    source_nodes = {node.uid for sector in sectors.values() for node in sector.nodes}
    needs_halo = {path for path in company_paths for item in sectors[path].items
                  if item.kind == 6 and (item.details["prefab"] not in source_prefabs
                  or item.details["node"] not in source_nodes
                  or any(uid not in source_nodes for uid in item.details["spawn_nodes"]))}
    halo = sorted(_neighbors(needs_halo) & stack.resources.keys())
    _prefetch(stack, halo)
    for path in halo:
        try:
            data = stack.read(path, max_bytes=64 * 1024 * 1024)
            sectors[path] = parse_sector(data)
            coverage["neighbor_sectors_parsed"] += 1
        except (SectorFormatError, KeyError, ValueError) as exc:
            coverage["blocked_sectors"].append({"path": path, "reason": str(exc), "role": "neighbor"})

    prefabs: dict[int, list[tuple[str, object]]] = defaultdict(list)
    nodes: dict[int, list[tuple[str, object]]] = defaultdict(list)
    for path, sector in sectors.items():
        for item in sector.prefabs:
            prefabs[item.uid].append((path, item))
        for node in sector.nodes:
            nodes[node.uid].append((path, node))

    def_blockers = coverage["definition_blockers"]
    prefab_source_paths = stack.matching(r"def/world/prefab.*\.(?:sii|sui)")
    _prefetch(stack, prefab_source_paths)
    contexts = _units(stack, _CONTEXT, "data_context", def_blockers)
    jobs = _units(stack, _JOB, "car_job_data", def_blockers)
    prefab_units = _units(stack, _PREFAB, "prefab_model", def_blockers)
    for label, units in (("data_context", contexts), ("car_job_data", jobs)):
        counts = Counter(unit.name for unit in units)
        for name, count in sorted(counts.items()):
            if count > 1:
                def_blockers.append({"reason": f"Duplicate {label} unit {name} across effective resources"})
        units[:] = [unit for unit in units if counts[unit.name] == 1]
    report["definition_sources"] = [_resource(stack, path) for path in sorted(
        {unit.source for unit in (*contexts, *jobs)} | set(prefab_source_paths))]
    if not contexts:
        def_blockers.append({"reason": "No effective data_context units"})
    if not jobs:
        def_blockers.append({"reason": "No effective car_job_data units"})
    tags: dict[str, set[str]] = defaultdict(set)
    context_units: dict[str, list[dict]] = defaultdict(list)
    excluded: set[str] = set()
    for context_path in stack.matching(_CONTEXT):
        try:
            excluded.update(match.group(1).lower() for match in re.finditer(
                r"^\s*#\s*(prefab\.[a-z0-9_]+)[^\n]*excluded\b",
                stack.text(context_path), re.I | re.M))
        except (KeyError, UnicodeError, ValueError) as exc:
            def_blockers.append({"path": context_path, "reason": str(exc)})
    for unit in contexts:
        try:
            for target in unit.values("target_data"):
                tags[target].update(unit.values("tags"))
                context_units[target].append({"name": unit.name, "virtual_path": unit.source})
        except DefinitionError as exc:
            def_blockers.append({"path": unit.source, "reason": str(exc)})
    source_jobs: dict[str, set[str]] = defaultdict(set)
    target_jobs: dict[str, set[str]] = defaultdict(set)
    for job in jobs:
        try:
            for tag in job.values("source_data_contexts"):
                source_jobs[tag].add(job.name)
            for tag in job.values("target_data_contexts"):
                target_jobs[tag].add(job.name)
        except DefinitionError as exc:
            def_blockers.append({"path": job.source, "reason": str(exc)})
    model_index: dict[int, list] = defaultdict(list)
    from .local_fuel import token
    for unit in prefab_units:
        try:
            model_index[token(unit.name.removeprefix("prefab.").lower())].append(unit)
        except ValueError as exc:
            def_blockers.append({"path": unit.source, "reason": str(exc)})

    def context_for(name: str) -> dict:
        found_tags = tags.get(name, set())
        status = ("classified" if found_tags else
                  "explicitly_excluded" if name.lower() in excluded else "unclassified")
        return {"prefab": name, "tags": sorted(found_tags), "status": status,
                "context_units": sorted(context_units.get(name, ()),
                                        key=lambda source: (source["virtual_path"], source["name"])),
                "source_job_definitions": sorted({j for tag in found_tags for j in source_jobs[tag]}),
                "target_job_definitions": sorted({j for tag in found_tags for j in target_jobs[tag]})}

    # HashFS benefits greatly from extracting the exact editor and descriptor
    # members in two batches instead of launching one extractor per placement.
    relevant_companies = {_token(item.details["company"])
                          for path in company_paths for item in sectors[path].companies}
    editor_paths = {path for path in stack.matching(r"def/company/[^/]+/editor/[^/]+\.(?:sii|sui)")
                    if path.split("/")[2] in relevant_companies}
    # SUI files are include fragments. Prefetch them for @include resolution,
    # but parse only SII roots so an included unit is not indexed twice.
    editor_roots = sorted(path for path in editor_paths if path.endswith(".sii"))
    descriptor_paths = set()
    for path in company_paths:
        for company_item in sectors[path].companies:
            for _, prefab_item in prefabs.get(company_item.details["prefab"], ()):  # actual model
                for model_unit in model_index.get(prefab_item.details["model"], ()):
                    try:
                        descriptor = model_unit.one("prefab_desc")
                        if descriptor and descriptor.lstrip("/") in stack.resources:
                            descriptor_paths.add(descriptor.lstrip("/"))
                    except DefinitionError:
                        pass
    _prefetch(stack, sorted(editor_paths))
    _prefetch(stack, sorted(descriptor_paths))

    editor_index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for editor_path in editor_roots:
        company_name = editor_path.split("/")[2]
        try:
            editor_data = stack.read(editor_path)
            source = _resource(stack, editor_path, editor_data)
            units = [unit for unit in parse_units(editor_data.decode("utf-8-sig"),
                                                   source=editor_path, include_reader=stack.text)
                     if unit.kind == "company_def"]
            for unit in units:
                city_name, prefab_name = unit.one("city"), unit.one("prefab")
                if not city_name or not prefab_name:
                    raise DefinitionError(f"{editor_path}: company_def lacks city or prefab")
                name = prefab_name if prefab_name.startswith("prefab.") else "prefab." + prefab_name
                try:
                    model_token = token(name.removeprefix("prefab.").lower())
                except ValueError:
                    model_token = None
                editor_index[company_name, city_name].append({
                    "status": "resolved", "unit": unit.name, "source": source,
                    "city": city_name, "prefab": prefab_name, "model_token": model_token})
        except (DefinitionError, KeyError, UnicodeError, ValueError) as exc:
            def_blockers.append({"path": editor_path, "reason": str(exc)})

    descriptor_cache: dict[str, dict] = {}
    for path in sorted(company_paths):
        data = sector_data[path]
        for item in sectors[path].items:
            if item.kind != 6:
                continue
            coverage["company_placements"] += 1
            detail = item.details
            city, company = _token(detail["city"]), _token(detail["company"])
            record = {
                "item_uid": hex(item.uid), "source_sector": _resource(stack, path, data),
                "company_item_flags": hex(item.flags),
                "city_token": city, "company_token": company,
                "prefab_uid": hex(detail["prefab"]),
                "activation_node": _node_record(detail["node"], nodes),
                "spawn_nodes": [dict(_node_record(uid, nodes), flags=hex(flags))
                                for uid, flags in zip(detail["spawn_nodes"], detail["spawn_flags"])],
                "marker_evidence": {"company_node": "placed", "ppd_company_point_count": None,
                                    "spawn_flags_vehicle_mode": "unknown",
                                    "courier_specific_interpretation": "unknown"},
                "unknowns": [],
            }
            unknowns = record["unknowns"]
            if not city:
                unknowns.append("company_city_token_unresolved")
            if not company:
                unknowns.append("company_token_unresolved")
            matches = prefabs.get(detail["prefab"], [])
            if len(matches) > 1:
                signatures = {(prefab.flags, prefab.details["model"], prefab.details["variant"],
                               prefab.details["parts"], prefab.details["nodes"],
                               prefab.details["slaves"], prefab.details["origin"])
                              for _, prefab in matches}
                if len(signatures) == 1:
                    matches = matches[:1]
            if len(matches) != 1:
                unknowns.append("prefab_reference_unresolved" if not matches else "prefab_reference_ambiguous")
            else:
                prefab_path, prefab = matches[0]
                record["prefab"] = {"item_uid": hex(prefab.uid), "sector": prefab_path,
                                    "model_token": hex(prefab.details["model"]),
                                    "model_name": _token(prefab.details["model"]),
                                    "slave_uids": [hex(uid) for uid in prefab.details["slaves"]]}
            if record["activation_node"]["status"] != "resolved":
                unknowns.append("activation_node_unresolved")
                record["marker_evidence"]["company_node"] = "unresolved"
            if any(node["status"] != "resolved" for node in record["spawn_nodes"]):
                unknowns.append("spawn_node_unresolved")
            if city and company:
                candidates = editor_index.get((company, city), [])
                actual_token = prefab.details["model"] if "prefab" in record else None
                exact = [candidate for candidate in candidates
                         if actual_token is not None and candidate["model_token"] == actual_token]
                chosen = exact if exact else candidates
                if len(chosen) == 1:
                    editor = {key: value for key, value in chosen[0].items() if key != "model_token"}
                    editor["matching_city_candidates"] = len(candidates)
                    editor["matched_placed_prefab"] = bool(exact)
                else:
                    editor = {
                        "status": "missing" if not chosen else "ambiguous",
                        "searched_pattern": f"def/company/{company}/editor/*.sii",
                        "city": city, "candidate_count": len(candidates),
                        "candidates": [{key: value for key, value in candidate.items()
                                        if key != "model_token"} for candidate in candidates],
                    }
                record["company_definition"] = editor
                if editor["status"] != "resolved":
                    unknowns.append("company_definition_" + editor["status"])
                if editor["status"] == "resolved" and editor["prefab"]:
                    name = editor["prefab"] if editor["prefab"].startswith("prefab.") else "prefab." + editor["prefab"]
                    record["editor_context"] = context_for(name)
                    if "prefab" in record and not editor["matched_placed_prefab"]:
                        unknowns.append("editor_prefab_model_mismatch")
                else:
                    unknowns.append("company_definition_prefab_unresolved")
            # The placed prefab's model token is primary location evidence.
            # An editor definition may disagree with it and must remain a
            # distinct observation rather than substituting its descriptor.
            if "prefab" in record:
                actual_token = prefab.details["model"]
                actual_name = _token(actual_token)
                if actual_name:
                    record["context"] = context_for("prefab." + actual_name)
                    if record["context"]["status"] != "classified":
                        unknowns.append("placed_prefab_context_" + record["context"]["status"])
                else:
                    unknowns.append("placed_prefab_model_token_unresolved")
                models = model_index.get(actual_token, [])
                if len(models) != 1:
                    unknowns.append("placed_prefab_definition_missing_or_ambiguous")
                else:
                    unit = models[0]
                    try:
                        descriptor = unit.one("prefab_desc")
                        record["prefab_definition"] = {"name": unit.name,
                            "source": _resource(stack, unit.source),
                            "descriptor_path": descriptor}
                    except (DefinitionError, KeyError, ValueError) as exc:
                        descriptor = None
                        record["prefab_definition"] = {"name": unit.name, "status": "unreadable",
                                                        "reason": str(exc)}
                    if descriptor:
                        descriptor = descriptor.lstrip("/")
                        if descriptor not in descriptor_cache:
                            if descriptor not in stack.resources:
                                descriptor_cache[descriptor] = {"status": "missing"}
                            else:
                                try:
                                    ppd = stack.read(descriptor, max_bytes=64 * 1024 * 1024)
                                    info = inspect_ppd(ppd)
                                    descriptor_cache[descriptor] = {"status": "inspected",
                                        "source": _resource(stack, descriptor, ppd),
                                        "version": info["version"],
                                        "spawn_count": info["spawn_count"],
                                        "trigger_count": info["trigger_count"],
                                        "company_points": [
                                            {"index": spawn["index"], "flags": spawn["flags"]}
                                            for spawn in info["spawns"] if spawn["type"] == 13],
                                        "spawn_types": dict(sorted(Counter(str(s["type"]) for s in info["spawns"]).items()))}
                                except (PpdError, KeyError, ValueError) as exc:
                                    descriptor_cache[descriptor] = {"status": "unreadable", "reason": str(exc)}
                        record["prefab_descriptor"] = descriptor_cache[descriptor]
                        if descriptor_cache[descriptor]["status"] == "inspected":
                            record["marker_evidence"]["ppd_company_point_count"] = len(descriptor_cache[descriptor]["company_points"])
                        else:
                            unknowns.append("placed_prefab_descriptor_unresolved")
                    else:
                        unknowns.append("placed_prefab_descriptor_unspecified")
            record["static_linkage"] = "resolved" if not unknowns else "partial"
            record["courier_market_eligibility"] = "unknown"
            report["locations"].append(record)

    by_prefab: dict[str, list[dict]] = defaultdict(list)
    for record in report["locations"]:
        if record["prefab_uid"] != "0x0":
            by_prefab[record["prefab_uid"]].append(record)
    for prefab_uid, records in sorted(by_prefab.items()):
        unique = {record["item_uid"]: record for record in records}
        if len(unique) < 2:
            continue
        diagnostic = {"prefab_uid": prefab_uid,
                      "company_item_uids": sorted(unique),
                      "company_tokens": sorted({record["company_token"] for record in unique.values()
                                                if record["company_token"]}),
                      "city_tokens": sorted({record["city_token"] for record in unique.values()
                                             if record["city_token"]}),
                      "source_sectors": sorted({record["source_sector"]["virtual_path"]
                                                for record in unique.values()})}
        report["shared_prefab_companies"].append(diagnostic)
        for record in records:
            record["unknowns"].append("multiple_company_items_for_prefab")
            record["static_linkage"] = "partial"

    coverage["complete"] = not coverage["blocked_sectors"] and not def_blockers
    report["counts"] = {"locations": len(report["locations"]),
                        "partial_linkage": sum(r["static_linkage"] == "partial" for r in report["locations"])}
    coverage["partial_locations"] = report["counts"]["partial_linkage"]
    coverage["blockers"] = ([{"area": "sector", **blocker} for blocker in coverage["blocked_sectors"]]
                            + [{"area": "definition", **blocker} for blocker in def_blockers])
    return report
