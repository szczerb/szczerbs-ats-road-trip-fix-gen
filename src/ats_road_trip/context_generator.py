"""Conservative, additive Road Trip context aliases for exact prefab reuse.

This module produces a reviewable plan. It does not install a mod or claim
that static context coverage proves jobs will appear in game.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
from pathlib import PurePosixPath
import re

from .courier_audit import audit_courier
from .package import ResourceStack
from .sii import DefinitionError, Unit, parse_units
from .mod_writer import sha256


_PREFABS = r"def/world/prefab(?:\.[^/]+)?\.sii"
_CONTEXTS = r"def/data_context(?:\.[^/]+)?\.sii"
_EXCLUDED = re.compile(r"^\s*#\s*[^\n]*?(prefab\.[a-z0-9_]+)[^\n]*?excluded\b", re.I | re.M)
_TARGET = "def/data_context.rtfix.sii"


def _units(stack: ResourceStack, pattern: str, kind: str) -> list[Unit]:
    stack.prefetch(pattern)
    result: list[Unit] = []
    for path in stack.matching(pattern):
        result.extend(unit for unit in parse_units(stack.text(path), source=path,
                                                    include_reader=stack.text) if unit.kind == kind)
    return result


def _asset_path(value: str | None) -> str | None:
    if not value:
        return None
    value = value.replace("\\", "/").strip()
    parts = PurePosixPath(value).parts
    if ".." in parts or ":" in value or not value.startswith("/"):
        return None
    normalized = str(PurePosixPath(value))
    return normalized.lstrip("/") if normalized != "/" else None


def _pair(unit: Unit) -> tuple[str, str] | None:
    model = _asset_path(unit.one("model_desc"))
    descriptor = _asset_path(unit.one("prefab_desc"))
    return (model, descriptor) if model and descriptor else None


def _index(units: list[Unit]) -> dict[str, list[Unit]]:
    index: dict[str, list[Unit]] = defaultdict(list)
    for unit in units:
        index[unit.name].append(unit)
    return dict(index)


def _source(stack: ResourceStack, unit: Unit) -> dict[str, str]:
    resource = stack.resources[unit.source][1]
    return {"package": resource.package, "virtual_path": unit.source,
            "physical_path": resource.physical_path}


def plan_context_aliases(
    baseline: ResourceStack,
    effective: ResourceStack,
    map_packages: set[str],
) -> dict:
    """Plan aliases only for map company prefabs reusing a classified base asset pair.

    ``baseline`` and ``effective`` should include mounted definition and asset
    packages. ``map_packages`` identifies the exact packages supplying company
    editor definitions; no package role is inferred from its filename.
    """
    base_prefabs = _index(_units(baseline, _PREFABS, "prefab_model"))
    effective_prefabs = _index(_units(effective, _PREFABS, "prefab_model"))
    base_contexts = _units(baseline, _CONTEXTS, "data_context")
    effective_contexts = _units(effective, _CONTEXTS, "data_context")
    if _TARGET in effective.resources:
        raise DefinitionError(f'Generated context target already exists in input stack: {_TARGET}')
    if not base_contexts or not effective_contexts:
        raise DefinitionError("Both stacks need data_context definitions")
    names: set[str] = set()
    target_tags: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for context in base_contexts:
        if context.name in names:
            raise DefinitionError(f"Duplicate baseline data_context unit: {context.name}")
        names.add(context.name)
        tags = tuple(sorted(set(context.values("tags"))))
        for target in context.values("target_data"):
            if target.startswith("prefab."):
                target_tags[target].add(tags)
    effective_names: set[str] = set()
    classified: set[str] = set()
    for context in effective_contexts:
        if context.name in effective_names:
            raise DefinitionError(f"Duplicate effective data_context unit: {context.name}")
        effective_names.add(context.name)
        classified.update(target for target in context.values("target_data") if target.startswith("prefab."))

    excluded: set[str] = set()
    for stack in (baseline, effective):
        for path in stack.matching(_CONTEXTS):
            excluded.update(_EXCLUDED.findall(stack.text(path)))
    audit = audit_courier(effective, map_packages=map_packages)
    used: dict[str, list[dict]] = defaultdict(list)
    for detail in audit["company_definitions"]:
        used[detail["prefab"]].append({key: detail[key] for key in
            ('company', 'city', 'source_package', 'source_path', 'virtual_path')})

    aliases: list[dict] = []
    skipped: list[dict] = []
    generated_names: set[str] = set()
    for alias in sorted(used):
        companies = sorted(used[alias], key=lambda d: (d["source_package"], d["virtual_path"]))
        reason: str | None = None
        if alias in excluded:
            reason = "explicitly_excluded"
        elif alias in classified:
            reason = "already_classified"
        elif len(effective_prefabs.get(alias, ())) != 1:
            reason = "missing_or_ambiguous_alias_definition"
        else:
            alias_unit = effective_prefabs[alias][0]
            alias_pair = _pair(alias_unit)
            if alias_pair is None:
                reason = "missing_or_invalid_alias_assets"
            else:
                matches: list[tuple[str, Unit, tuple[str, ...]]] = []
                ambiguous = False
                for canonical, tags_set in target_tags.items():
                    if len(base_prefabs.get(canonical, ())) != 1:
                        continue
                    if _pair(base_prefabs[canonical][0]) != alias_pair:
                        continue
                    if canonical in excluded or len(tags_set) != 1:
                        ambiguous = True
                        continue
                    effective_units = effective_prefabs.get(canonical, ())
                    if len(effective_units) != 1 or _pair(effective_units[0]) != alias_pair:
                        ambiguous = True
                        continue
                    tags = next(iter(tags_set))
                    if not tags:
                        ambiguous = True
                        continue
                    matches.append((canonical, base_prefabs[canonical][0], tags))
                unique_tags = {tags for _, _, tags in matches}
                if ambiguous or len(unique_tags) > 1:
                    reason = "ambiguous_canonical_classification"
                elif not matches:
                    reason = "no_exact_classified_canonical_pair"
                else:
                    model, descriptor = alias_pair
                    if model not in effective.resources or descriptor not in effective.resources:
                        reason = "assets_not_in_resource_stack"
                    elif any(effective.resources[path][1].package in map_packages for path in (model, descriptor)):
                        reason = "canonical_asset_overridden_by_map"
                    else:
                        canonical, canonical_unit, tags = sorted(matches, key=lambda m: m[0])[0]
                        generated_name = "context.prefab.rtf" + hashlib.sha256(alias.encode()).hexdigest()[:8]
                        if generated_name in effective_names or generated_name in generated_names:
                            reason = "generated_unit_name_collision"
                        else:
                            generated_names.add(generated_name)
                            aliases.append({"alias": alias, "unit_name": generated_name,
                                            "tags": list(tags), "canonical": canonical,
                                            "model_desc": "/" + model, "prefab_desc": "/" + descriptor,
                                            "canonical_source": _source(baseline, canonical_unit),
                                            "alias_source": _source(effective, alias_unit),
                                            "asset_fingerprints": {path: sha256(effective.read(path)) for path in (model, descriptor)},
                                            "companies": companies})
        if reason:
            skipped.append({"alias": alias, "reason": reason,
                            "company_definition_count": len(companies),
                            "cities": sorted({c['city'] for c in companies if c['city']})})

    return {"schema_version": 1, "analysis": "exact_prefab_context_aliases",
            "package_order": [str(p.path) for p in effective.packages],
            "map_packages": sorted(map_packages), "aliases": aliases, "skipped": skipped,
            "limitations": ["Static definition matching does not prove courier jobs appear in game.",
                            "Map placement, spawn points, route links, vehicle eligibility, DLCs, and market refresh remain unvalidated.",
                            "Asset equality is based on matching referenced paths, not file hashes or prefab behavior."]}


def render_context_patch(plan: dict) -> dict[str, bytes]:
    """Render an additive SII fragment; no baseline file is copied or replaced."""
    aliases = plan.get("aliases", [])
    if not aliases:
        return {}
    lines = ["SiiNunit", "{"]
    names: set[str] = set()
    for alias in sorted(aliases, key=lambda item: item["alias"]):
        name = alias["unit_name"]
        valid_unit = r'[a-z0-9_]{1,12}(?:\.[a-z0-9_]{1,12})*'
        if name in names or not re.fullmatch(valid_unit, name):
            raise DefinitionError(f"Duplicate or invalid generated unit name: {name}")
        if not re.fullmatch(valid_unit, alias['alias']) or not alias['alias'].startswith('prefab.'):
            raise DefinitionError('Invalid generated prefab identifier')
        if not alias['tags'] or any(not re.fullmatch(r'[a-z0-9_]{1,12}', tag) for tag in alias['tags']):
            raise DefinitionError('Invalid generated context tag')
        names.add(name)
        lines.extend([f"data_context : {name}", "{",
                      f"\ttarget_data[]: {alias['alias']}"])
        lines.extend(f"\ttags[]: {tag}" for tag in alias["tags"])
        lines.extend(["}", ""])
    lines.extend(["}", ""])
    return {_TARGET: "\n".join(lines).encode("utf-8")}
