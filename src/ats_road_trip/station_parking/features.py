"""Bounded model-space cues for curbs, entrances, and low obstacles.

These are diagnostic proxies from the effective visible render mesh. Material
names suggest where to inspect; geometry is required for a feature record.
The records do not establish intended function, walkable space, or complete
game collision coverage.
"""
from __future__ import annotations

import math
from statistics import median


_MAX_TRIANGLES = 100_000
_MAX_VERTICES = 300_000
_MAX_GROUND_SAMPLES = 100_000
_MAX_OBSTACLE_FEATURES = 512
_MAX_CURB_FEATURES = 256
_MAX_DOOR_PROXIES = 256
_GROUND_CEILING = 1.9
_GROUND_FLOOR = 0.2
_DOOR_CLEARANCE = 1.5
_CURB_HINTS = ("kerb", "curb", "sidewalk", "pavement")


def _finite_point(point, *, size: int = 3) -> tuple[float, ...]:
    if not isinstance(point, (tuple, list)) or len(point) != size:
        raise ValueError("Model feature input contains a malformed coordinate")
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) for value in point):
        raise ValueError("Model feature input contains a nonfinite coordinate")
    return tuple(float(value) for value in point)


def _aliases(values, label: str) -> set[str]:
    if isinstance(values, str) or not isinstance(values, (list, tuple, set, frozenset)):
        raise ValueError(f"{label} materials must be a collection of aliases")
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{label} materials must contain nonempty aliases")
    return set(values)


def _ground_reference(mesh: dict, ground: set[str]) -> tuple[float | None, dict]:
    samples = []
    for piece in mesh["pieces"]:
        if piece["material"] not in ground:
            continue
        samples.extend(_finite_point(point)[1] for point in piece["positions"])
    if not samples:
        return None, {"status": "unavailable", "reason": "no visible PIM vertices use configured ground materials",
                      "sample_count": 0, "sampling": "all matching vertices"}
    sampling = "all matching vertices"
    if len(samples) > _MAX_GROUND_SAMPLES:
        stride = math.ceil(len(samples) / _MAX_GROUND_SAMPLES)
        samples = samples[::stride]
        sampling = f"deterministic stride sample, step {stride}"
    height = float(median(samples))
    return height, {"status": "sampled", "height_y": height, "sample_count": len(samples),
                    "sampling": sampling, "coordinate_space": "PIM model-local Y"}


def _triangle_components(triangles: list[tuple[int, int, int]]) -> list[list[int]]:
    """Return vertex-connected triangle components with stable source ordering."""
    vertex_triangles: dict[int, list[int]] = {}
    for triangle_index, triangle in enumerate(triangles):
        for vertex_index in triangle:
            vertex_triangles.setdefault(vertex_index, []).append(triangle_index)
    parent = list(range(len(triangles)))

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for adjacent in vertex_triangles.values():
        first = root(adjacent[0])
        for index in adjacent[1:]:
            other = root(index)
            if first != other:
                parent[other] = first
    components: dict[int, list[int]] = {}
    for index in range(len(triangles)):
        components.setdefault(root(index), []).append(index)
    return [components[key] for key in sorted(components, key=lambda key: components[key][0])]


def _triangle_xz(points: list[tuple[float, float, float]]) -> list[list[float]]:
    result = []
    for point in points:
        xz = [point[0], point[2]]
        if xz not in result:
            result.append(xz)
    return result


def _projected_area(points: list[tuple[float, float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    a, b, c = points[:3]
    return abs((b[0] - a[0]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[0] - a[0])) / 2


def _edge_lengths(points: list[tuple[float, float, float]]) -> list[float]:
    return [math.hypot(points[(i + 1) % 3][0] - points[i][0],
                       points[(i + 1) % 3][2] - points[i][2]) for i in range(3)]


def _component_vertices(component: list[int], triangles: list[tuple[int, int, int]]) -> list[int]:
    return sorted({vertex for triangle_index in component for vertex in triangles[triangle_index]})


def _curb_features(mesh: dict, paint: set[str], ground_y: float | None):
    hints = sorted(alias for alias in {piece["material"] for piece in mesh["pieces"]}
                   if any(term in alias.lower() for term in _CURB_HINTS))
    if ground_y is None:
        return [], {"status": "unavailable_without_ground_reference", "material_alias_hints": hints,
                    "hinted_piece_count": sum(piece["material"] in hints for piece in mesh["pieces"]),
                    "feature_count": 0, "omitted_feature_count": 0}
    output = []
    candidate_count = 0
    hinted_pieces = 0
    qualifying_components = 0
    for piece in mesh["pieces"]:
        alias = piece["material"]
        if alias in paint or not any(term in alias.lower() for term in _CURB_HINTS):
            continue
        hinted_pieces += 1
        triangles = piece["triangles"]
        positions = piece["positions"]
        for component_index, component in enumerate(_triangle_components(triangles)):
            vertex_indexes = _component_vertices(component, triangles)
            y_values = [positions[index][1] for index in vertex_indexes]
            low, high = min(y_values), max(y_values)
            span = high - low
            if (span < 0.06 or span > 0.85 or low < ground_y - 0.25
                    or low > ground_y + 0.18 or high < ground_y + 0.05
                    or high > ground_y + 0.9):
                continue
            qualifying_components += 1
            for triangle_index in component:
                triangle = triangles[triangle_index]
                points = [positions[index] for index in triangle]
                ys = [point[1] for point in points]
                if max(ys) - min(ys) > 0.025:
                    continue
                center_y = sum(ys) / 3
                if not ground_y + 0.025 <= center_y <= ground_y + 0.9:
                    continue
                area = _projected_area(points)
                edges = _edge_lengths(points)
                longest = max(edges)
                if area < 0.0005 or longest > 5.0 or 2 * area / max(longest, 1e-12) > 0.9:
                    continue
                candidate_count += 1
                if len(output) >= _MAX_CURB_FEATURES:
                    continue
                output.append({
                    "id": f"curb-p{piece['index']}-c{component_index}-t{triangle_index}",
                    "kind": "low_raised_edge_surface_proxy",
                    "interpretation": "curb_or_sidewalk_geometry_hypothesis",
                    "material_alias": alias,
                    "piece_index": piece["index"], "triangle_index": triangle_index,
                    "component_index": component_index,
                    "polygon_xz": _triangle_xz(points),
                    "component_y_interval": [low, high],
                    "component_vertical_span_m": span,
                    "ground_reference_y": ground_y,
                    "evidence": "material-name hint plus grounded, low-span connected geometry and flat top triangle",
                })
    omitted = max(0, candidate_count - len(output))
    if candidate_count:
        status = "geometry_proxies_found"
    else:
        status = "no_qualifying_low_raised_geometry_in_hinted_materials"
    return output, {"status": status, "material_alias_hints": hints,
                    "hinted_piece_count": hinted_pieces,
                    "qualifying_connected_component_count": qualifying_components,
                    "candidate_feature_count": candidate_count,
                    "feature_count": len(output), "omitted_feature_count": omitted,
                    "interpretation": "candidate geometry evidence, not proof that the edge is a curb or usable sidewalk"}


def _door_features(mesh: dict, ground_y: float | None):
    hints = sorted(alias for alias in {piece["material"] for piece in mesh["pieces"]
                                       if "door" in piece["material"].lower()})
    output = []
    component_count = 0
    unresolved = 0
    proxy_candidate_count = 0
    if ground_y is None:
        return [], {"status": "unavailable_without_ground_reference", "material_alias_hints": hints,
                    "hinted_piece_count": sum(piece["material"] in hints for piece in mesh["pieces"]),
                    "component_count": 0, "unresolved_component_count": 0,
                    "proxy_count": 0, "clearance_margin_m": _DOOR_CLEARANCE,
                    "semantics": "Hypothesis; alias plus geometry cannot establish a working entrance"}
    for piece in mesh["pieces"]:
        alias = piece["material"]
        if "door" not in alias.lower():
            continue
        positions = piece["positions"]
        triangles = piece["triangles"]
        for component_index, component in enumerate(_triangle_components(triangles)):
            component_count += 1
            vertex_indexes = _component_vertices(component, triangles)
            points = [positions[index] for index in vertex_indexes]
            xs, ys, zs = ([point[axis] for point in points] for axis in (0, 1, 2))
            low_y, high_y = min(ys), max(ys)
            x_span, z_span = max(xs) - min(xs), max(zs) - min(zs)
            broad, thin = max(x_span, z_span), min(x_span, z_span)
            vertical_triangles = sum(
                max(positions[index][1] for index in triangles[triangle_index])
                - min(positions[index][1] for index in triangles[triangle_index]) >= 0.4
                for triangle_index in component)
            supported = (1.4 <= high_y - low_y <= 3.5 and
                         ground_y - 0.35 <= low_y <= ground_y + 0.45 and
                         0.55 <= broad <= 3.5 and thin <= 0.6 and vertical_triangles > 0)
            if not supported:
                unresolved += 1
                continue
            min_x, max_x = min(xs) - _DOOR_CLEARANCE, max(xs) + _DOOR_CLEARANCE
            min_z, max_z = min(zs) - _DOOR_CLEARANCE, max(zs) + _DOOR_CLEARANCE
            proxy_candidate_count += 1
            if len(output) >= _MAX_DOOR_PROXIES:
                continue
            output.append({
                "id": f"door-p{piece['index']}-c{component_index}",
                "kind": "entrance_keep_clear_proxy",
                "interpretation": "door-material vertical component proxy; functional entrance is unconfirmed",
                "confidence": "hypothesis",
                "material_alias": alias,
                "piece_index": piece["index"], "component_index": component_index,
                "component_triangle_count": len(component),
                "component_footprint_xz": [[min(xs), min(zs)], [max(xs), min(zs)],
                                           [max(xs), max(zs)], [min(xs), max(zs)]],
                "polygon_xz": [[min_x, min_z], [max_x, min_z], [max_x, max_z], [min_x, max_z]],
                "component_y_interval": [low_y, high_y],
                "vertical_triangle_count": vertical_triangles,
                "clearance_margin_m": _DOOR_CLEARANCE,
                "evidence": "door-alias hint, near-ground connected vertical geometry, door-like bounded footprint",
            })
    omitted = max(0, proxy_candidate_count - len(output))
    status = "proxies_found_partial" if proxy_candidate_count else "no_supported_door_geometry_proxy"
    return output, {"status": status, "material_alias_hints": hints,
                    "hinted_piece_count": sum(piece["material"] in hints for piece in mesh["pieces"]),
                    "component_count": component_count, "unresolved_component_count": unresolved,
                    "proxy_candidate_count": proxy_candidate_count,
                    "proxy_count": len(output), "omitted_proxy_count": omitted,
                    "clearance_margin_m": _DOOR_CLEARANCE,
                    "semantics": "Hypothesis; material and geometry cues do not establish all actual working entrances",
                    "completeness": "partial/unknown; doors without a matching alias or bounded component may be missed"}


def _obstacle_features(mesh: dict, ground: set[str], paint: set[str], ground_y: float | None):
    if ground_y is None:
        return [], {"status": "unavailable_without_ground_reference", "feature_count": 0,
                    "omitted_feature_count": 0, "complete": False}
    features = []
    candidate_count = 0
    for piece in mesh["pieces"]:
        alias = piece["material"]
        if alias in ground or alias in paint:
            continue
        positions, triangles = piece["positions"], piece["triangles"]
        for triangle_index, triangle in enumerate(triangles):
            points = [positions[index] for index in triangle]
            low_y = min(point[1] for point in points)
            high_y = max(point[1] for point in points)
            if high_y < ground_y + _GROUND_FLOOR or low_y > ground_y + _GROUND_CEILING:
                continue
            footprint = _triangle_xz(points)
            if not footprint:
                continue
            candidate_count += 1
            if len(features) >= _MAX_OBSTACLE_FEATURES:
                continue
            features.append({
                "id": f"obstacle-p{piece['index']}-t{triangle_index}",
                "kind": "model_triangle_clearance_proxy",
                "material_alias": alias,
                "piece_index": piece["index"], "triangle_index": triangle_index,
                "polygon_xz": footprint,
                "triangle_y_interval": [low_y, high_y],
                "tested_vertical_band_y": [ground_y + _GROUND_FLOOR, ground_y + _GROUND_CEILING],
                "evidence": "individual non-ground/non-paint source triangle intersects the configured low clearance band",
            })
    omitted = max(0, candidate_count - _MAX_OBSTACLE_FEATURES)
    return features, {"status": "bounded_triangles", "candidate_triangle_count": candidate_count,
                      "feature_count": len(features), "omitted_feature_count": omitted,
                      "complete": omitted == 0,
                      "vertical_band_m": [_GROUND_FLOOR, _GROUND_CEILING],
                      "grouping": "individual source triangles; no whole-piece bounding boxes",
                      "semantics": "render-mesh obstacle proxy, not complete collision or world geometry"}


def inspect_model_features(mesh: dict, *, ground, paint) -> dict:
    """Extract bounded, explainable curb/door/low-obstacle cues from visible mesh.

    Coordinates and height intervals remain in PIM model-local XYZ. ``ground``
    and ``paint`` are explicit material-alias collections from the reviewed
    config. No texture-only inference or external-world completeness claim is
    made.
    """
    if not isinstance(mesh, dict) or not isinstance(mesh.get("pieces"), list):
        raise ValueError("Model feature inspection requires a parsed visible PIM mesh")
    ground_aliases, paint_aliases = _aliases(ground, "Ground"), _aliases(paint, "Paint")
    if not ground_aliases:
        raise ValueError("At least one explicit ground material alias is required")
    pieces = mesh["pieces"]
    for piece in pieces:
        if not isinstance(piece, dict) or not isinstance(piece.get("material"), str):
            raise ValueError("Model feature input contains malformed piece metadata")
        if not isinstance(piece.get("positions"), list) or not isinstance(piece.get("triangles"), list):
            raise ValueError("Model feature input contains malformed piece geometry")
    vertex_total = sum(len(piece["positions"]) for piece in pieces)
    triangle_total = sum(len(piece["triangles"]) for piece in pieces)
    if triangle_total > _MAX_TRIANGLES or vertex_total > _MAX_VERTICES:
        return {
            "status": "bounded_out", "coordinate_space": "PIM model-local XYZ",
            "source_triangle_count": triangle_total, "triangle_limit": _MAX_TRIANGLES,
            "source_vertex_count": vertex_total, "vertex_limit": _MAX_VERTICES,
            "ground_reference": {"status": "not_computed"},
            "curb_evidence": {"status": "not_computed", "features": [], "feature_count": 0},
            "entrance_clearance": {"status": "not_computed", "proxies": [], "proxy_count": 0,
                                   "semantics": "Hypothesis; not complete"},
            "obstacles": {"status": "not_computed", "features": [], "feature_count": 0,
                          "complete": False},
            "blockers": ["model geometry exceeds the bounded feature inspection limit"],
        }
    for piece in pieces:
        for point in piece["positions"]:
            _finite_point(point)
        for triangle in piece["triangles"]:
            if (not isinstance(triangle, (list, tuple)) or len(triangle) != 3
                    or any(isinstance(index, bool) or not isinstance(index, int)
                           or index < 0 or index >= len(piece["positions"]) for index in triangle)):
                raise ValueError("Model feature input contains an invalid triangle")
    ground_y, ground_report = _ground_reference(mesh, ground_aliases)
    curb_features, curb_report = _curb_features(mesh, paint_aliases, ground_y)
    door_proxies, door_report = _door_features(mesh, ground_y)
    obstacle_features, obstacle_report = _obstacle_features(mesh, ground_aliases, paint_aliases, ground_y)
    incomplete = ground_y is None or obstacle_report.get("complete") is False
    return {
        "status": "partial" if incomplete else "inspected",
        "coordinate_space": "PIM model-local XYZ; prefab/world transform not applied",
        "source_triangle_count": triangle_total,
        "ground_reference": ground_report,
        "curb_evidence": {**curb_report, "features": curb_features},
        "entrance_clearance": {**door_report, "proxies": door_proxies},
        "obstacles": {**obstacle_report, "features": obstacle_features},
        "limits": [
            "Geometry features come from the selected visible model state only.",
            "Material aliases are search hints; textures and names do not prove function.",
            "Door proxies are incomplete and do not prove a functional entrance or pedestrian route.",
            "Render triangles do not establish complete game collision, furniture semantics, NPC occupancy, or external-world obstacles.",
        ],
        "blockers": (["configured ground materials provide no visible height reference"] if ground_y is None else []),
    }
