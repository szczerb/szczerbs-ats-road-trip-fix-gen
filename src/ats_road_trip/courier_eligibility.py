"""Source-pinned, byte-preserving Road Trip car-job eligibility experiment.

The output replaces the complete canonical job file. It changes only selected
``vehicle_types[]`` declarations and makes no claim about live job offers.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import tomllib

from .package import ResourceStack
from .sii import DefinitionError, _HEADER, parse_units, strip_comments, _mask_strings


_TOP = {"schema_version", "profile_id", "game_version", "job_definition_path",
        "job_definition_sha256", "sorted_job_unit_names_sha256",
        "cargo_definition_path", "cargo_definition_sha256", "add_vehicle_type",
        "mustang_vehicle_types", "unclassified_policy", "empty_cargo_policy",
        "expected", "unchanged", "groups"}
_EXPECTED = {"sedan_only_job_units", "cargo_job_units", "classified_cargo_ids",
             "unchanged_standard_transfer_units", "unchanged_premium_transfer_units",
             "all_stock_job_units"}
_GROUP = {"enabled", "expected_job_units", "job_family_prefixes", "cargo_ids",
          "review_basis"}
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_VERSION = re.compile(r"\d+(?:\.\d+){3}\Z")
_JOB_PATH = re.compile(r"def/car_job_data(?:\.[^/]+)?\.sii\Z")
_FIELD = re.compile(r"(?m)^[ \t]*vehicle_types\[\][ \t]*:[ \t]*([^\s#]+)[ \t]*(?:\#[^\r\n]*)?\r?$")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unique_strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(v, str) or not v for v in value):
        raise ValueError(f"{label} must be a nonempty string array")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return value


def validate_courier_eligibility_config(config: dict) -> dict:
    """Validate the complete, reviewable TOML schema without coercing values."""
    if not isinstance(config, dict) or set(config) != _TOP:
        raise ValueError(f"config keys must be exactly {sorted(_TOP)}")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("unsupported schema_version")
    if not isinstance(config["profile_id"], str) or not config["profile_id"].strip():
        raise ValueError("profile_id must be nonempty")
    if not isinstance(config["game_version"], str) or not _VERSION.fullmatch(config["game_version"]):
        raise ValueError("game_version must be normalized numeric ATS version")
    for key, path in (("job_definition_path", "def/car_job_data.sii"),
                      ("cargo_definition_path", "def/car_cargo.sii")):
        if config[key] != path:
            raise ValueError(f"{key} must be {path}")
    for key in ("job_definition_sha256", "cargo_definition_sha256", "sorted_job_unit_names_sha256"):
        if not isinstance(config[key], str) or not _HEX.fullmatch(config[key]):
            raise ValueError(f"{key} must be a lowercase SHA-256 digest")
    if config["add_vehicle_type"] != "muscle":
        raise ValueError("only muscle addition is supported")
    if _unique_strings(config["mustang_vehicle_types"], "mustang_vehicle_types") != ["muscle", "veteran"]:
        raise ValueError("Mustang tags must be muscle and veteran")
    if config["unclassified_policy"] != "error":
        raise ValueError("unclassified_policy must be error")
    if config["empty_cargo_policy"] != "preserve_listed_transfers_and_error_on_unknown":
        raise ValueError("unsupported empty_cargo_policy")
    expected = config["expected"]
    if not isinstance(expected, dict) or set(expected) != _EXPECTED:
        raise ValueError("expected counts have missing or unknown keys")
    if any(type(n) is not int or n < 0 for n in expected.values()):
        raise ValueError("expected counts must be nonnegative integers")
    unchanged = config["unchanged"]
    if not isinstance(unchanged, dict) or set(unchanged) != {"vehicle_transfer_job_ids", "reason"}:
        raise ValueError("unchanged requires transfer IDs and reason")
    transfers = _unique_strings(unchanged["vehicle_transfer_job_ids"], "transfer IDs")
    if not isinstance(unchanged["reason"], str) or not unchanged["reason"].strip():
        raise ValueError("transfer reason must be nonempty")
    if len(transfers) != expected["unchanged_standard_transfer_units"] + expected["unchanged_premium_transfer_units"]:
        raise ValueError("transfer count mismatch")
    groups = config["groups"]
    if not isinstance(groups, dict) or not groups:
        raise ValueError("groups must be a nonempty table")
    prefixes, cargo_ids = set(), set()
    for name, group in groups.items():
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError("invalid group ID")
        if not isinstance(group, dict) or set(group) != _GROUP:
            raise ValueError(f"{name}: missing or unknown group keys")
        if type(group["enabled"]) is not bool or type(group["expected_job_units"]) is not int or group["expected_job_units"] <= 0:
            raise ValueError(f"{name}: invalid enabled or expected_job_units")
        if not isinstance(group["review_basis"], str) or not group["review_basis"].strip():
            raise ValueError(f"{name}: review_basis must be nonempty")
        for prefix in _unique_strings(group["job_family_prefixes"], f"{name} prefixes"):
            if not prefix.startswith("car_job.") or not prefix.endswith("_") or prefix in prefixes:
                raise ValueError(f"{name}: invalid or duplicate family prefix {prefix}")
            prefixes.add(prefix)
        for cargo in _unique_strings(group["cargo_ids"], f"{name} cargo IDs"):
            if not cargo.startswith("car_cargo.") or cargo in cargo_ids:
                raise ValueError(f"{name}: invalid or overlapping cargo ID {cargo}")
            cargo_ids.add(cargo)
    if len(cargo_ids) != expected["classified_cargo_ids"]:
        raise ValueError("classified cargo ID count mismatch")
    if sum(g["expected_job_units"] for g in groups.values()) != expected["cargo_job_units"]:
        raise ValueError("group job count mismatch")
    if expected["sedan_only_job_units"] != expected["cargo_job_units"] + expected["unchanged_standard_transfer_units"]:
        raise ValueError("sedan-only count does not reconcile")
    return config


def load_courier_eligibility_config(path: str | Path) -> dict:
    with Path(path).open("rb") as stream:
        return validate_courier_eligibility_config(tomllib.load(stream))


def _job_spans(text: str) -> dict[str, tuple[int, int]]:
    """Find top-level unit bodies with offsets in the original text."""
    mask = _mask_strings(strip_comments(text))
    found = {}
    for match in _HEADER.finditer(mask):
        if match.group(1) != "car_job_data":
            continue
        start, position, depth = match.end(), match.end(), 1
        while position < len(mask) and depth:
            depth += (mask[position] == "{") - (mask[position] == "}")
            position += 1
        if depth or match.group(2) in found:
            raise ValueError("unbalanced or duplicate car_job_data unit span")
        found[match.group(2)] = (start, position - 1)
    return found


def _vehicle_insertion(text: str, span: tuple[int, int], unit_name: str) -> tuple[int, str]:
    start, end = span
    body = text[start:end]
    masked = _mask_strings(strip_comments(body))
    declarations = list(_FIELD.finditer(masked))
    if not declarations:
        raise ValueError(f"{unit_name}: no editable vehicle_types[] declaration")
    # The parser and scanner must agree on all live values; this also catches
    # non-line-oriented declarations, duplicate scalar forms and odd comments.
    line = declarations[-1]
    offset = start + line.end()
    if text[offset - 1:offset + 1] == "\r\n":
        newline = "\r\n"
        boundary = offset + 1
    elif text[offset:offset + 2] == "\r\n":
        newline = "\r\n"
        boundary = offset + 2
    elif text[offset:offset + 1] == "\n":
        newline = "\n"
        boundary = offset + 1
    else:
        raise ValueError(f"{unit_name}: last vehicle declaration lacks newline boundary")
    original = body[line.start():line.end()]
    indent = re.match(r"[ \t]*", original).group()
    return boundary, f"{indent}vehicle_types[]: muscle{newline}"


def _plan(job_data: bytes, cargo_data: bytes, config: dict, game_version: str,
          *, extra_jobs: list[tuple[str, bytes]] | None = None) -> tuple[dict, dict[str, bytes]]:
    report = {"schema_version": 1, "analysis": "courier_eligibility", "in_game_verified": False,
              "game_version": game_version, "config_profile": config.get("profile_id"),
              "shared_job_effects": ["Dispatch", "Quick Jobs", "other readers of car_job_data"],
              "runtime_offer_and_cargo_fit": "unknown",
              "coverage": {"complete": False, "blockers": []}, "groups": {}, "selected_job_ids": [],
              "retained_job_ids": [], "transfer_job_ids": [], "additional_job_files": [],
              "source_hashes": {"def/car_job_data.sii": _sha(job_data),
                                "def/car_cargo.sii": _sha(cargo_data)}}
    blockers = report["coverage"]["blockers"]
    try:
        validate_courier_eligibility_config(config)
        if game_version != config["game_version"]:
            raise ValueError("ATS version differs from pinned game_version")
        if _sha(job_data) != config["job_definition_sha256"] or _sha(cargo_data) != config["cargo_definition_sha256"]:
            raise ValueError("effective source hash differs from reviewed config")
        text = job_data.decode("utf-8")
        cargo_text = cargo_data.decode("utf-8")
        if "@include" in _mask_strings(strip_comments(text)) or "@include" in _mask_strings(strip_comments(cargo_text)):
            raise ValueError("canonical includes are unsupported for byte-preserving replacement")
        units = parse_units(text, source="def/car_job_data.sii")
        cargos = parse_units(cargo_text, source="def/car_cargo.sii")
        if any(u.kind != "car_job_data" for u in units) or any(u.kind != "car_cargo_data" for u in cargos):
            raise ValueError("unexpected unit kind in canonical definitions")
        cargo_names = [u.name for u in cargos]
        if len(cargo_names) != len(set(cargo_names)):
            raise ValueError("duplicate canonical cargo ID")
        names = [u.name for u in units]
        if len(names) != len(set(names)) or len(names) != config["expected"]["all_stock_job_units"]:
            raise ValueError("canonical job ID count or uniqueness mismatch")
        digest = _sha(("\n".join(sorted(names)) + "\n").encode("utf-8"))
        if digest != config["sorted_job_unit_names_sha256"]:
            raise ValueError("sorted canonical job ID digest differs")
        spans = _job_spans(text)
        if set(spans) != set(names):
            raise ValueError("source spans do not match parsed jobs")
        all_units = {u.name: "def/car_job_data.sii" for u in units}
        for path, data in extra_jobs or []:
            other_text = data.decode("utf-8")
            parsed = parse_units(other_text, source=path)
            for unit in parsed:
                if unit.kind != "car_job_data":
                    continue
                if unit.name in all_units:
                    raise ValueError(f"duplicate job ID {unit.name}: {all_units[unit.name]} and {path}")
                all_units[unit.name] = path
            report["additional_job_files"].append({"path": path, "sha256": _sha(data),
                                                    "job_units": sum(u.kind == "car_job_data" for u in parsed)})
        transfers = set(config["unchanged"]["vehicle_transfer_job_ids"])
        if not transfers <= set(names):
            raise ValueError("listed vehicle-transfer ID absent from canonical source")
        groups = config["groups"]
        cargo_to_group = {cargo: name for name, group in groups.items() for cargo in group["cargo_ids"]}
        group_jobs = {name: [] for name in groups}
        observed_cargos = set()
        sedan_only = 0
        sedan_cargo = 0
        insertions = []
        for unit in units:
            if unit.attribute_errors:
                raise ValueError(f"{unit.name}: ambiguous attributes {sorted(unit.attribute_errors)}")
            tags = unit.values("vehicle_types")
            refs = unit.values("cargos")
            if not tags or len(tags) != len(set(tags)) or not all(re.fullmatch(r"[a-z_]+", v) for v in tags):
                raise ValueError(f"{unit.name}: invalid vehicle_types array")
            body = text[slice(*spans[unit.name])]
            live = _FIELD.findall(_mask_strings(strip_comments(body)))
            if tuple(live) != tags:
                raise ValueError(f"{unit.name}: vehicle source declarations differ from parsed values")
            if not refs and unit.name not in transfers:
                raise ValueError(f"{unit.name}: unlisted empty cargos array")
            if unit.name in transfers:
                if refs:
                    raise ValueError(f"{unit.name}: listed transfer has cargo")
                report["transfer_job_ids"].append(unit.name)
            if any(ref not in cargo_names for ref in refs):
                raise ValueError(f"{unit.name}: unknown cargo reference")
            if "sedan" not in tags or any(tag in tags for tag in config["mustang_vehicle_types"]):
                report["retained_job_ids"].append(unit.name)
                continue
            sedan_only += 1
            if unit.name in transfers:
                continue
            sedan_cargo += 1
            if not refs:
                raise ValueError(f"{unit.name}: empty cargo")
            observed_cargos.update(refs)
            family = [name for name, group in groups.items()
                      if any(unit.name.startswith(prefix) for prefix in group["job_family_prefixes"])]
            if len(family) != 1:
                raise ValueError(f"{unit.name}: unclassified or overlapping family")
            group_name = family[0]
            if any(ref not in cargo_to_group for ref in refs):
                raise ValueError(f"{unit.name}: unclassified cargo ID")
            if any(cargo_to_group[ref] != group_name for ref in refs):
                raise ValueError(f"{unit.name}: family/cargo group mismatch")
            group_jobs[group_name].append(unit.name)
            if not groups[group_name]["enabled"]:
                report["retained_job_ids"].append(unit.name)
                continue
            pos, inserted = _vehicle_insertion(text, spans[unit.name], unit.name)
            insertions.append((pos, inserted, unit.name))
            report["selected_job_ids"].append(unit.name)
        if sedan_only != config["expected"]["sedan_only_job_units"] or sedan_cargo != config["expected"]["cargo_job_units"]:
            raise ValueError("sedan-only source counts differ")
        if observed_cargos != set(cargo_to_group):
            raise ValueError("configured cargo IDs differ from sedan-only source cargo IDs")
        if set(report["transfer_job_ids"]) != transfers:
            raise ValueError("transfer inventory differs")
        for name, group in groups.items():
            if len(group_jobs[name]) != group["expected_job_units"]:
                raise ValueError(f"{name}: expected job count differs")
            report["groups"][name] = {"enabled": group["enabled"],
                                      "job_units": len(group_jobs[name]),
                                      "cargo_ids": len(group["cargo_ids"]),
                                      "selected_job_units": len(group_jobs[name]) if group["enabled"] else 0}
        changed = text
        for pos, inserted, _ in sorted(insertions, reverse=True):
            changed = changed[:pos] + inserted + changed[pos:]
        updated = parse_units(changed, source="def/car_job_data.sii")
        before = {u.name: u for u in units}
        if set(u.name for u in updated) != set(before):
            raise ValueError("patched job IDs differ")
        selected = set(report["selected_job_ids"])
        for unit in updated:
            original = before[unit.name]
            expected_attrs = dict(original.attributes)
            if unit.name in selected:
                expected_attrs["vehicle_types"] = (*original.values("vehicle_types"), "muscle")
            if unit.attributes != expected_attrs or unit.attribute_errors:
                raise ValueError(f"{unit.name}: patched attributes differ")
        # Reverse the exact inserted substrings. Equality proves that every
        # original byte, including transfer bodies, survives unchanged.
        restored = changed
        for pos, inserted, _ in sorted(insertions):
            if restored[pos:pos + len(inserted)] != inserted:
                raise ValueError("patched insertion offset mismatch")
            restored = restored[:pos] + restored[pos + len(inserted):]
        if restored.encode("utf-8") != job_data:
            raise ValueError("non-target source bytes changed")
        report["coverage"].update({"all_stock_job_units": len(units), "sedan_only_job_units": sedan_only,
                                   "cargo_job_units": sedan_cargo, "selected_job_units": len(selected),
                                   "disabled_job_units": sedan_cargo - len(selected),
                                   "transfer_job_units": len(transfers), "non_target_bytes_preserved": True,
                                   "complete": True})
        report["changed_fields"] = {name: {"vehicle_types_add": "muscle"}
                                    for name in report["selected_job_ids"]}
        return report, {config["job_definition_path"]: changed.encode("utf-8")} if insertions else {}
    except (ValueError, DefinitionError, UnicodeError, KeyError, TypeError) as exc:
        blockers.append(str(exc))
        return report, {}


def plan_courier_eligibility_bytes(job_data: bytes, cargo_data: bytes, config: dict,
                                   *, game_version: str) -> tuple[dict, dict[str, bytes]]:
    return _plan(job_data, cargo_data, config, game_version)


def plan_courier_eligibility(stack: ResourceStack, config_path: str | Path,
                             *, game_version: str) -> tuple[dict, dict[str, bytes]]:
    """Plan against the effective low-to-high package stack; write nothing."""
    config_bytes = Path(config_path).read_bytes()
    config = validate_courier_eligibility_config(tomllib.loads(config_bytes.decode("utf-8-sig")))
    job_path = config["job_definition_path"]
    cargo_path = config["cargo_definition_path"]
    if job_path not in stack.resources or cargo_path not in stack.resources:
        raise ValueError("effective canonical job or cargo resource is missing")
    extra = []
    for path in stack.matching(_JOB_PATH.pattern):
        if path != job_path:
            extra.append((path, stack.read(path, max_bytes=64 * 1024 * 1024)))
    report, changes = _plan(stack.read(job_path, max_bytes=64 * 1024 * 1024),
                            stack.read(cargo_path, max_bytes=64 * 1024 * 1024),
                            config, game_version, extra_jobs=extra)
    report["config_sha256"] = _sha(config_bytes)
    report["package_order"] = [str(package.path) for package in stack.packages]
    report["canonical_providers"] = {path: stack.resources[path][1].package for path in (job_path, cargo_path)}
    report["canonical_overrides"] = [entry for entry in stack.overrides if entry["path"] in (job_path, cargo_path)]
    return report, changes
