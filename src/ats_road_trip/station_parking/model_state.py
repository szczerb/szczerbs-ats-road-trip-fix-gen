"""Resolve the visible PIM geometry selected by a bounded PIT model trait.

This reader deliberately supports one PIT look and explicit integer visibility
attributes. It does not infer a texture-only decal, activate an unknown extra
part, or treat a visual mesh as complete world collision data.
"""
from __future__ import annotations

from copy import deepcopy

from ..local_fuel import token
from .mesh import StationMeshError, _parse_blocks


def _fail(message: str) -> None:
    raise StationMeshError(message)


def _field(block, key: str):
    if key not in block.fields:
        _fail(f"PIT {block.name} is missing required field {key}")
    return block.fields[key]


def _count(value, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(f"PIT {label} must be a nonnegative integer")
    return value


def _name(value, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"PIT {label} must be a nonempty string")
    return value


def _only_fields(block, allowed: set[str]) -> None:
    if set(block.fields) != allowed or block.rows:
        _fail(f"PIT {block.name} has missing or unsupported fields")


def _visibility(part) -> bool:
    _only_fields(part, {"Name", "AttributeCount"})
    name = _name(_field(part, "Name"), "part name")
    count = _count(_field(part, "AttributeCount"), "part attribute count")
    if count != 1 or len(part.children) != 1 or part.children[0].name != "Attribute":
        _fail(f"PIT part {name!r} must have exactly one visibility attribute")
    attr = part.children[0]
    _only_fields(attr, {"Format", "Tag", "Value"})
    if attr.children:
        _fail(f"PIT part {name!r} visibility attribute has nested data")
    if (_field(attr, "Format") != "INT" or _field(attr, "Tag") != "visible"
            or _field(attr, "Value") not in ((0,), (1,))):
        _fail(f"PIT part {name!r} has unsupported or ambiguous visibility")
    return _field(attr, "Value") == (1,)


def _pit_state(pit_text: str):
    roots = _parse_blocks(pit_text)
    by_name: dict[str, list] = {}
    for root in roots:
        by_name.setdefault(root.name, []).append(root)
    if set(by_name) != {"Header", "Global", "Look", "Variant"}:
        _fail("PIT must contain only Header, Global, one Look, and Variant blocks")
    if any(len(by_name[key]) != 1 for key in ("Header", "Global", "Look")):
        _fail("PIT requires exactly one Header, Global, and Look block")
    header, global_block, look = (by_name[key][0] for key in ("Header", "Global", "Look"))
    _only_fields(header, {"FormatVersion", "Source", "Type", "Name"})
    _only_fields(global_block, {"LookCount", "VariantCount", "PartCount", "MaterialCount"})
    if header.children or global_block.children:
        _fail("PIT Header and Global cannot contain nested blocks")
    if (_field(header, "Type") != "Trait" or _field(header, "FormatVersion") != 1):
        _fail("Only PIT FormatVersion 1 Type Trait is supported")
    variants = by_name["Variant"]
    expected_variants = _count(_field(global_block, "VariantCount"), "variant count")
    if expected_variants != len(variants) or not variants:
        _fail("PIT VariantCount disagrees with Variant blocks")
    if _count(_field(global_block, "LookCount"), "look count") != 1:
        _fail("PIT must declare exactly one look")

    _only_fields(look, {"Name"})
    look_name = _name(_field(look, "Name"), "look name")
    expected_materials = _count(_field(global_block, "MaterialCount"), "material count")
    material_aliases: dict[str, tuple[str, ...]] = {}
    for material in look.children:
        if material.name != "Material":
            _fail("PIT Look contains an unsupported child block")
        if set(material.fields) != {"Alias", "Effect", "Flags", "AttributeCount", "TextureCount"} or material.rows:
            _fail("PIT Look material has missing or unsupported fields")
        alias = _name(_field(material, "Alias"), "material alias")
        if alias in material_aliases:
            _fail(f"PIT Look has duplicate material alias {alias!r}")
        expected_attributes = _count(_field(material, "AttributeCount"), "material attribute count")
        expected_textures = _count(_field(material, "TextureCount"), "material texture count")
        textures = []
        children_seen = set()
        attribute_count = 0
        for child in material.children:
            if child.name == "Attribute":
                if set(child.fields) != {"Format", "Tag", "Value"} or child.rows or child.children:
                    _fail(f"PIT material {alias!r} has malformed attribute data")
                _name(_field(child, "Format"), "material attribute format")
                _name(_field(child, "Tag"), "material attribute tag")
                attribute_count += 1
                continue
            if child.name != "Texture" or set(child.fields) != {"Tag", "Value"} or child.rows or child.children:
                _fail(f"PIT material {alias!r} has unsupported texture data")
            tag = _name(_field(child, "Tag"), "texture tag")
            value = _name(_field(child, "Value"), "texture path")
            if tag in children_seen:
                _fail(f"PIT material {alias!r} has duplicate texture tag")
            children_seen.add(tag)
            textures.append(value)
        if attribute_count != expected_attributes or len(textures) != expected_textures:
            _fail(f"PIT material {alias!r} disagrees with its attribute/texture counts")
        material_aliases[alias] = tuple(textures)
    if len(material_aliases) != expected_materials:
        _fail("PIT MaterialCount disagrees with the selected Look")

    expected_parts = _count(_field(global_block, "PartCount"), "part count")
    variant_states: dict[str, dict[str, bool]] = {}
    for variant in variants:
        _only_fields(variant, {"Name"})
        variant_name = _name(_field(variant, "Name"), "variant name")
        if variant_name in variant_states:
            _fail(f"PIT has duplicate variant name {variant_name!r}")
        state: dict[str, bool] = {}
        for part in variant.children:
            if part.name != "Part":
                _fail(f"PIT variant {variant_name!r} has an unsupported child block")
            part_name = _name(_field(part, "Name"), "part name")
            if part_name in state:
                _fail(f"PIT variant {variant_name!r} has duplicate part {part_name!r}")
            state[part_name] = _visibility(part)
        if len(state) != expected_parts:
            _fail(f"PIT variant {variant_name!r} disagrees with Global.PartCount")
        variant_states[variant_name] = state
    if len({frozenset(state) for state in variant_states.values()}) != 1:
        _fail("PIT variants define different part ownership sets")
    return look_name, material_aliases, variant_states, expected_parts


def resolve_model_state(mesh: dict, pit_text: str, *, variant: int = 0,
                        additional_parts: list[int] | tuple[int, ...] = ()) -> tuple[dict, dict]:
    """Filter parsed PIM geometry using the selected PIT variant and extra parts.

    Map variant and additional-part names are SCS tokens. Variant zero is the
    documented default selector; all other values must match a named PIT
    variant. Additional parts are unioned with that variant's visible parts.
    Unknown tokens, inconsistent PIM/PIT part names, and ambiguous ownership
    block instead of exposing the entire unfiltered model.
    """
    if not isinstance(mesh, dict):
        _fail("PIM mesh must be a parsed mesh mapping")
    if isinstance(variant, bool) or not isinstance(variant, int) or not 0 <= variant < 2**64:
        _fail("Map model variant must be a uint64 SCS token")
    if not isinstance(additional_parts, (list, tuple)):
        _fail("Map additional parts must be a list or tuple of SCS tokens")
    if any(isinstance(part, bool) or not isinstance(part, int) or not 0 <= part < 2**64
           for part in additional_parts):
        _fail("Map additional parts must contain uint64 SCS tokens")
    if len(additional_parts) != len(set(additional_parts)):
        _fail("Map additional parts contain duplicate tokens")

    look_name, pit_materials, variants, pit_part_count = _pit_state(pit_text)
    try:
        variant_tokens = {token(name): name for name in variants}
    except ValueError as exc:
        raise StationMeshError("PIT variant name cannot be represented as an SCS token") from exc
    if len(variant_tokens) != len(variants):
        _fail("PIT variant names collide as SCS tokens")
    default_token = token("default")
    if variant == 0:
        variant_name = "default"
    elif variant == default_token:
        variant_name = "default"
    else:
        variant_name = variant_tokens.get(variant)
    if variant_name is None or variant_name not in variants:
        _fail(f"Unknown or unsupported PIT variant token {variant:#x}")

    mesh_parts = mesh.get("parts")
    pieces = mesh.get("pieces")
    locators = mesh.get("locators")
    materials = mesh.get("materials")
    counts = mesh.get("counts")
    if not all(isinstance(value, list) for value in (mesh_parts, pieces, locators, materials)):
        _fail("PIM mesh is missing parsed part, piece, locator, or material arrays")
    if not isinstance(counts, dict):
        _fail("PIM mesh is missing source counts")
    names = [part.get("name") if isinstance(part, dict) else None for part in mesh_parts]
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        _fail("PIM has malformed or ambiguous part names")
    pit_part_names = set(next(iter(variants.values())))
    if set(names) != pit_part_names:
        _fail("PIM and PIT part ownership names disagree")
    if len(mesh_parts) != pit_part_count:
        _fail("PIM and PIT part counts disagree")

    try:
        by_token = {token(name): name for name in names}
    except ValueError as exc:
        raise StationMeshError("PIM part name cannot be represented as an SCS token") from exc
    if len(by_token) != len(names):
        _fail("PIM part names collide as SCS tokens")
    requested_names = []
    for part_token in additional_parts:
        name = by_token.get(part_token)
        if name is None:
            _fail(f"Unknown PIT additional-part token {part_token:#x}")
        requested_names.append(name)

    base_state = variants[variant_name]
    visible_names = {name for name, visible in base_state.items() if visible} | set(requested_names)
    # Build one-to-one source ownership maps. Duplicated, missing, or invalid
    # references are unsafe even if the PIM parser normally prevents them.
    piece_owner: dict[int, str] = {}
    locator_owner: dict[int, str] = {}
    for part in mesh_parts:
        for index in part.get("pieces", ()):
            if isinstance(index, bool) or not isinstance(index, int) or index in piece_owner:
                _fail("PIM piece ownership is ambiguous")
            piece_owner[index] = part["name"]
        for index in part.get("locators", ()):
            if isinstance(index, bool) or not isinstance(index, int) or index in locator_owner:
                _fail("PIM locator ownership is ambiguous")
            locator_owner[index] = part["name"]
    if set(piece_owner) != set(range(len(pieces))) or set(locator_owner) != set(range(len(locators))):
        _fail("PIM pieces or locators have missing/invalid part ownership")

    material_index = {material.get("alias"): i for i, material in enumerate(materials)
                      if isinstance(material, dict)}
    if len(material_index) != len(materials) or any(alias not in pit_materials for alias in material_index):
        _fail("PIM material aliases are malformed or missing from the selected PIT look")
    source_counts = deepcopy(counts)
    source_counts.update({"parts": len(mesh_parts), "pieces": len(pieces), "locators": len(locators),
                          "materials": len(materials)})
    filtered = deepcopy(mesh)
    filtered_materials = []
    material_remap = {}
    filtered_pieces = []
    for piece in pieces:
        index = piece.get("index")
        owner = piece_owner.get(index)
        if owner not in visible_names:
            continue
        old_material = piece.get("material_index")
        if isinstance(old_material, bool) or not isinstance(old_material, int) or not 0 <= old_material < len(materials):
            _fail("PIM piece has invalid material ownership")
        if old_material not in material_remap:
            material_remap[old_material] = len(filtered_materials)
            filtered_materials.append(deepcopy(materials[old_material]))
        clone = deepcopy(piece)
        clone["source_index"] = index
        clone["index"] = len(filtered_pieces)
        clone["material_index"] = material_remap[old_material]
        filtered_pieces.append(clone)
    filtered_locators = []
    for locator in locators:
        index = locator.get("index")
        if locator_owner.get(index) not in visible_names:
            continue
        clone = deepcopy(locator)
        clone["source_index"] = index
        clone["index"] = len(filtered_locators)
        filtered_locators.append(clone)
    filtered_parts = []
    piece_indexes = {piece["source_index"]: piece["index"] for piece in filtered_pieces}
    locator_indexes = {item["source_index"]: item["index"] for item in filtered_locators}
    for part in mesh_parts:
        if part["name"] not in visible_names:
            continue
        filtered_parts.append({"name": part["name"],
                               "pieces": [piece_indexes[index] for index in part["pieces"] if index in piece_indexes],
                               "locators": [locator_indexes[index] for index in part["locators"] if index in locator_indexes]})
    if not filtered_pieces:
        _fail("Selected PIT model state has no visible PIM pieces")
    filtered["materials"] = filtered_materials
    filtered["pieces"] = filtered_pieces
    filtered["locators"] = filtered_locators
    filtered["parts"] = filtered_parts
    filtered["counts"] = {
        "vertices": sum(piece["vertex_count"] for piece in filtered_pieces),
        "triangles": sum(piece["triangle_count"] for piece in filtered_pieces),
        "materials": len(filtered_materials), "pieces": len(filtered_pieces),
        "parts": len(filtered_parts), "bones": source_counts.get("bones", 0),
        "locators": len(filtered_locators),
    }
    used_aliases = sorted({piece["material"] for piece in filtered_pieces})
    report = {
        "look": look_name,
        "variant": variant_name,
        "variant_token": variant,
        "visible_parts": sorted(visible_names),
        "variant_visible_parts": sorted(name for name, visible in base_state.items() if visible),
        "additional_parts": sorted(requested_names),
        "inactive_parts": sorted(set(names) - visible_names),
        "source_counts": source_counts,
        "filtered_counts": deepcopy(filtered["counts"]),
        "materials": [{"alias": alias, "textures": list(pit_materials[alias])} for alias in used_aliases],
        "collision_parts_visible_by_name": sorted(name for name in visible_names if name.startswith("collpart")),
        "collision_semantics": "PIT visibility only; not proof of complete game collision coverage",
    }
    return filtered, report
