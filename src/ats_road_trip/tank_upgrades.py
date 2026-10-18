"""Plan four reviewed Ford chassis capacity overrides without serializing SII.

The effective source is pinned by its complete SHA-256. A plan is atomic: a
failure in any chassis returns no resources, including earlier successful edits.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import tomllib

from .package import ResourceStack
from .sii import DefinitionError, _HEADER, _mask_strings, parse_units, strip_comments


_CHASSIS = {
    "ford.mustang_67": ("def/vehicle/car/ford.mustang_67/chassis/rwd.sii", "rwd.ford.mustang_67.chassis"),
    "ford.victoria_06": ("def/vehicle/car/ford.victoria_06/chassis/rwd.sii", "rwd.ford.victoria_06.chassis"),
    "ford.f150_23": ("def/vehicle/car/ford.f150_23/chassis/4doors_55_awd.sii", "4d55_awd.ford.f150_23.chassis"),
    "ford.bronco_24": ("def/vehicle/car/ford.bronco_24/chassis/4doors_awd.sii", "4d_awd.ford.bronco_24.chassis"),
}
_TOP = {"schema_version", "profile_id", "game_version", "vehicles"}
_VEHICLE = {"model", "path", "unit", "sha256", "stock_liters", "target_liters",
            "stock_info", "target_info", "rationale", "sources"}
_VERSION = re.compile(r"\d+(?:\.\d+){3}\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_TANK = re.compile(r"(?m)^[ \t]*tank_size[ \t]*:[ \t]*(\d+)(?=[ \t]*(?:\r?$))")
_INFO = re.compile(r'(?m)^[ \t]*info\[\][ \t]*:[ \t]*("[^"\r\n]*")(?=[ \t]*(?:\r?$))')


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_tank_upgrade_config(config: dict) -> dict:
    """Reject missing, extra, or coerced policy fields before reading resources."""
    if not isinstance(config, dict) or set(config) != _TOP:
        raise ValueError(f"tank config keys must be exactly {sorted(_TOP)}")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("unsupported tank schema_version")
    if not isinstance(config["profile_id"], str) or not config["profile_id"].strip():
        raise ValueError("profile_id must be nonempty")
    if not isinstance(config["game_version"], str) or not _VERSION.fullmatch(config["game_version"]):
        raise ValueError("game_version must be a normalized ATS version")
    entries = config["vehicles"]
    if not isinstance(entries, list) or len(entries) != len(_CHASSIS):
        raise ValueError("tank profile must describe exactly four Ford chassis")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != _VEHICLE:
            raise ValueError(f"vehicle keys must be exactly {sorted(_VEHICLE)}")
        model = entry["model"]
        if not isinstance(model, str) or model not in _CHASSIS or model in seen:
            raise ValueError(f"unknown or duplicate Ford model: {model}")
        seen.add(model)
        path, unit = _CHASSIS[model]
        if entry["path"] != path or entry["unit"] != unit:
            raise ValueError(f"{model}: canonical chassis path or unit differs")
        if not isinstance(entry["sha256"], str) or not _DIGEST.fullmatch(entry["sha256"]):
            raise ValueError(f"{model}: sha256 must be a lowercase digest")
        stock, target = entry["stock_liters"], entry["target_liters"]
        if type(stock) is not int or type(target) is not int or stock <= 0 or target < stock or target * 10 > stock * 16:
            raise ValueError(f"{model}: capacities must be positive integer and target within 1.6x stock")
        for field in ("stock_info", "target_info", "rationale"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise ValueError(f"{model}: {field} must be nonempty")
        if any(c in entry[field] for field in ("stock_info", "target_info") for c in '"\\\r\n'):
            raise ValueError(f"{model}: info must be a single plain SII string")
        if stock == target and entry["stock_info"] != entry["target_info"]:
            raise ValueError(f"{model}: unchanged capacity requires unchanged info")
        if stock < target and entry["stock_info"] == entry["target_info"]:
            raise ValueError(f"{model}: upgraded capacity requires updated info")
        sources = entry["sources"]
        if not isinstance(sources, list) or not sources or any(
                not isinstance(s, str) or not re.fullmatch(r"https?://\S+", s) for s in sources):
            raise ValueError(f"{model}: sources must contain evidence URLs")
        if len(set(sources)) != len(sources):
            raise ValueError(f"{model}: duplicate evidence URL")
    if seen != set(_CHASSIS):
        raise ValueError("tank profile does not cover all four Ford models")
    return config


def _unit_body(raw: str, path: str, unit_name: str) -> tuple[int, int]:
    masked = _mask_strings(strip_comments(raw))
    headers = list(_HEADER.finditer(masked))
    chassis = [match for match in headers if match.group(1) == "accessory_chassis_data"]
    if len(chassis) != 1 or chassis[0].group(2) != unit_name:
        raise DefinitionError(f"{path}: expected exactly one canonical accessory_chassis_data")
    pos = chassis[0].end()
    depth = 1
    end = pos
    while depth and end < len(masked):
        depth += (masked[end] == "{") - (masked[end] == "}")
        end += 1
    if depth:
        raise DefinitionError(f"{path}: unbalanced unit body")
    return pos, end - 1


def _edit(data: bytes, entry: dict, stack: ResourceStack) -> bytes:
    path, unit_name = entry["path"], entry["unit"]
    if _sha(data) != entry["sha256"]:
        raise ValueError(f"{path}: effective source hash differs from reviewed config")
    text = data.decode("utf-8-sig")
    units = parse_units(text, source=path, include_reader=stack.text)
    chassis = [unit for unit in units if unit.kind == "accessory_chassis_data"]
    if len(chassis) != 1 or chassis[0].name != unit_name:
        raise DefinitionError(f"{path}: parsed chassis unit differs from expected unit")
    unit = chassis[0]
    if unit.attribute_errors:
        raise DefinitionError(f"{path}: ambiguous chassis attributes {sorted(unit.attribute_errors)}")
    if unit.one("tank_size") != str(entry["stock_liters"]):
        raise DefinitionError(f"{path}: stock tank_size differs from pinned policy")
    if unit.values("info").count(entry["stock_info"]) != 1:
        raise DefinitionError(f"{path}: expected exactly one stock info value")

    # Latin-1 gives one character per original byte, so offsets remain byte
    # offsets even when unrelated labels and comments contain UTF-8 text.
    raw = data.decode("latin-1")
    start, end = _unit_body(raw, path, unit_name)
    clean = strip_comments(raw[start:end])
    masked = _mask_strings(clean)
    tanks = list(_TANK.finditer(masked))
    infos = [m for m in _INFO.finditer(clean) if m.group(1) == f'"{entry["stock_info"]}"']
    if len(tanks) != 1 or tanks[0].group(1) != str(entry["stock_liters"]):
        raise DefinitionError(f"{path}: expected one editable stock tank_size declaration")
    if len(infos) != 1:
        raise DefinitionError(f"{path}: expected one editable stock info declaration")
    # The parser's complete semantic values must agree with the source scan.
    if len(tanks) != len(unit.values("tank_size")):
        raise DefinitionError(f"{path}: unsupported tank_size declaration")
    if len(list(_INFO.finditer(clean))) != len(unit.values("info")):
        raise DefinitionError(f"{path}: unsupported info declaration")
    if entry["target_liters"] == entry["stock_liters"]:
        return data
    replacements = [(start + tanks[0].start(1), start + tanks[0].end(1), str(entry["target_liters"]).encode("ascii")),
                    (start + infos[0].start(1), start + infos[0].end(1),
                     f'"{entry["target_info"]}"'.encode("utf-8"))]
    changed = data
    for left, right, value in sorted(replacements, reverse=True):
        changed = changed[:left] + value + changed[right:]
    edited_units = parse_units(changed.decode("utf-8-sig"), source=path, include_reader=stack.text)
    if len(edited_units) != len(units):
        raise DefinitionError(f"{path}: edited unit count differs")
    expected_attributes = dict(unit.attributes)
    expected_attributes["tank_size"] = (str(entry["target_liters"]),)
    expected_info = list(unit.values("info"))
    expected_info[expected_info.index(entry["stock_info"])] = entry["target_info"]
    expected_attributes["info"] = tuple(expected_info)
    for original, edited in zip(units, edited_units):
        if (edited.kind, edited.name, edited.source, edited.attribute_errors) != (
                original.kind, original.name, original.source, original.attribute_errors):
            raise DefinitionError(f"{path}: edited unit identity or parse state differs")
        expected = expected_attributes if original is unit else original.attributes
        if edited.attributes != expected:
            raise DefinitionError(f"{path}: edited definition changed an unrelated attribute")
    return changed


def plan_tank_upgrades(stack: ResourceStack, config: str | Path | dict,
                       *, game_version: str) -> tuple[dict, dict[str, bytes]]:
    """Return an atomic, source-pinned plan; blocked plans have no resources."""
    report = {"schema_version": 1, "analysis": "tank_upgrades", "game_version": game_version,
              "config_profile": None, "in_game_verified": False,
              "runtime_fuel_behavior": "unknown", "coverage": {"complete": False, "blockers": []},
              "vehicles": [], "changed_count": 0,
              "package_order": [str(package.path) for package in stack.packages]}
    try:
        if isinstance(config, dict):
            policy = validate_tank_upgrade_config(config)
        else:
            policy = validate_tank_upgrade_config(tomllib.loads(Path(config).read_text(encoding="utf-8-sig")))
        report["config_profile"] = policy["profile_id"]
        if game_version != policy["game_version"]:
            raise ValueError("ATS version differs from pinned game_version")
        resources = {}
        for entry in policy["vehicles"]:
            path = entry["path"]
            if path not in stack.resources:
                raise ValueError(f"{path}: effective chassis resource is missing")
            data = stack.read(path)
            changed = _edit(data, entry, stack)
            status = "upgraded" if changed != data else "unchanged"
            report["vehicles"].append({"model": entry["model"], "path": path, "unit": entry["unit"],
                                       "source_sha256": _sha(data), "stock_liters": entry["stock_liters"],
                                       "target_liters": entry["target_liters"],
                                       "stock_info": entry["stock_info"], "target_info": entry["target_info"],
                                       "rationale": entry["rationale"], "sources": list(entry["sources"]),
                                       "output_sha256": _sha(changed), "status": status,
                                       "provider": stack.resources[path][1].package})
            if changed != data:
                resources[path] = changed
        report["changed_count"] = len(resources)
        report["coverage"]["complete"] = True
        return report, resources
    except (ValueError, DefinitionError, UnicodeError, KeyError, TypeError, OSError, tomllib.TOMLDecodeError) as exc:
        report["coverage"]["blockers"].append(str(exc))
        return report, {}
