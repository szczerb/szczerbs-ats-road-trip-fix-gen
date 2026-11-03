"""Detailed, source-vector shoreline rendering for the North America map."""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter
import shapefile
from scipy.ndimage import maximum_filter

from .geography import features
from .render import Canvas, _in_scope, rings


_GSHHG_MEMBER = "GSHHS_shp/h/GSHHS_h_L1"
_NORTH_AMERICAN_COUNTRIES = {"CAN", "USA", "MEX"}


def _ring_paths(points: np.ndarray, calibration, canvas: Canvas,
                *, minimum: int = 3) -> list[list[tuple[int, int]]]:
    """Transform a geographic ring once, dropping dateline-spanning chords."""
    breaks = np.flatnonzero(np.abs(np.diff(points[:, 0])) > 180) + 1
    paths = []
    for piece in np.split(points, breaks):
        if len(piece) < minimum or np.all(piece[:, 0] > -30) or np.all(piece[:, 0] < -180):
            continue
        projected = canvas.pixels(calibration(piece))
        if not np.isfinite(projected).all():
            continue
        # PIL clips to the canvas. Clamping only protects it from extremely
        # distant but finite projected vertices; it does not alter the mask.
        projected = np.clip(projected, -canvas.size * 4, canvas.size * 5)
        paths.append([tuple(map(int, point)) for point in np.rint(projected)])
    return paths


def _project_ring_groups(groups, calibration, canvas: Canvas,
                         *, minimum: int = 3,
                         geojson_winding: bool = False):
    """Project many polygon features in one calibration call, retaining rings."""
    pieces = []
    metadata = []
    for group_index, polygon_rings in enumerate(groups):
        for raw_points in polygon_rings:
            points = np.asarray(raw_points, dtype=float)
            signed_area = float(np.sum(points[:-1, 0] * points[1:, 1]
                                       - points[1:, 0] * points[:-1, 1]))
            outer = signed_area > 0 if geojson_winding else signed_area < 0
            breaks = np.flatnonzero(np.abs(np.diff(points[:, 0])) > 180) + 1
            for piece in np.split(points, breaks):
                if (len(piece) < minimum or np.all(piece[:, 0] > -30) or
                        np.all(piece[:, 0] < -180)):
                    continue
                metadata.append((group_index, outer, abs(signed_area), len(piece)))
                pieces.append(piece)

    result = [[] for _ in groups]
    if not pieces:
        return result
    projected = canvas.pixels(calibration(np.concatenate(pieces, axis=0)))
    offset = 0
    for group_index, outer, area, point_count in metadata:
        path_points = projected[offset:offset + point_count]
        offset += point_count
        if not np.isfinite(path_points).all():
            continue
        path_points = np.clip(path_points, -canvas.size * 4, canvas.size * 5)
        path = [tuple(map(int, point)) for point in np.rint(path_points)]
        result[group_index].append((path, outer, area))
    return result


def _draw_polygon_rings(draw: ImageDraw.ImageDraw, polygon_rings, calibration,
                        canvas: Canvas, *, outer_value: int, hole_value: int,
                        geojson_winding: bool = False) -> int:
    """Draw a polygon with shapefile or RFC 7946 ring winding."""
    paths = _project_ring_groups([polygon_rings], calibration, canvas,
                                 geojson_winding=geojson_winding)[0]
    _draw_projected_polygon_rings(draw, paths, outer_value, hole_value)
    return len(paths)


def _draw_projected_polygon_rings(draw: ImageDraw.ImageDraw, paths,
                                  outer_value: int, hole_value: int) -> None:
    """Fill rings largest-first so nested holes and islands restore correctly."""
    for path, outer, _area in sorted(paths, key=lambda item: -item[2]):
        draw.polygon(path, fill=outer_value if outer else hole_value)


def _gshhg_reader(path: Path) -> shapefile.Reader:
    """Read the pinned GSHHG high-resolution L1 shapefile from its ZIP."""
    with zipfile.ZipFile(path) as archive:
        parts = {
            suffix: BytesIO(archive.read(f"{_GSHHG_MEMBER}.{suffix}"))
            for suffix in ("shp", "shx", "dbf")
        }
    return shapefile.Reader(**parts, encoding="utf-8")


def _paint_detailed_land(mask: Image.Image, source: Path, extent, calibration,
                         canvas: Canvas) -> int:
    """Rasterize GSHHG high-resolution L1 land polygons into a binary mask."""
    draw = ImageDraw.Draw(mask)
    groups = []
    reader = _gshhg_reader(source)
    try:
        for item in reader.iterShapeRecords():
            shape = item.shape
            if not _in_scope(shape, extent):
                continue
            polygon_rings = list(rings(shape))
            if not polygon_rings:
                continue
            groups.append(polygon_rings)
    finally:
        reader.close()
    projected_groups = _project_ring_groups(groups, calibration, canvas)
    for paths in projected_groups:
        _draw_projected_polygon_rings(draw, paths, 255, 0)
    return len(groups)


def _paint_lake(mask: Image.Image, polygon_rings, calibration,
                canvas: Canvas, *, geojson_winding: bool = False) -> int:
    """Replace one lake with water while explicitly restoring its land holes."""
    return _draw_polygon_rings(ImageDraw.Draw(mask), polygon_rings,
                               calibration, canvas, outer_value=0,
                               hole_value=255, geojson_winding=geojson_winding)


def _color_country_mask(mask: Image.Image, source: Path, extent,
                        calibration, canvas: Canvas) -> tuple[np.ndarray, dict[str, int], int]:
    """Rasterize stable country IDs; coastline geometry is deliberately absent."""
    records = []
    for shape, attr in features(source):
        if _in_scope(shape, extent):
            polygon_rings = list(rings(shape))
            if polygon_rings:
                records.append((attr["ADM0_A3"], polygon_rings))
    codes = {code for code, _polygon_rings in records}
    code_ids = {code: index + 1 for index, code in enumerate(sorted(codes))}
    if len(code_ids) > 254:
        raise ValueError("Detailed North America country ID mask exceeds 254 countries")
    draw = ImageDraw.Draw(mask)
    groups = [polygon_rings for _code, polygon_rings in records]
    projected_groups = _project_ring_groups(groups, calibration, canvas)
    for (code, _polygon_rings), paths in zip(records, projected_groups):
        _draw_projected_polygon_rings(draw, paths, code_ids[code], 0)
    return np.asarray(mask), code_ids, len(records)


def _extend_and_color(image: Image.Image, source_ids: np.ndarray,
                      country_ids: dict[str, int], land: Image.Image,
                      palette: dict, size: int) -> np.ndarray:
    """Extend country colors a short distance, then apply them only on land."""
    land_pixels = np.asarray(land)
    expanded = np.empty(source_ids.shape, dtype=np.uint8)
    tile_height = 384
    halo = 16  # maximum_filter size 33
    for y0 in range(0, size, tile_height):
        y1 = min(size, y0 + tile_height)
        sy0, sy1 = max(0, y0 - halo), min(size, y1 + halo)
        filtered = maximum_filter(source_ids[sy0:sy1], size=33)
        original = source_ids[y0:y1]
        expanded[y0:y1] = np.where(original != 0, original, filtered[y0 - sy0:y1 - sy0])
    country_palette = {
        code_ids: np.asarray(Image.new("RGB", (1, 1), palette.get(code, palette["land"])),
                             dtype=np.uint8)[0, 0]
        for code, code_ids in country_ids.items()
    }
    water_rgb = np.asarray(Image.new("RGB", (1, 1), palette["water"]), dtype=np.uint8)[0, 0]
    land_rgb = np.asarray(Image.new("RGB", (1, 1), palette["land"]), dtype=np.uint8)[0, 0]
    tile_height = 384
    for y0 in range(0, size, tile_height):
        y1 = min(size, y0 + tile_height)
        ids = expanded[y0:y1]
        is_land = land_pixels[y0:y1] != 0
        rgb = np.empty((y1 - y0, size, 3), dtype=np.uint8)
        rgb[:] = water_rgb
        rgb[is_land] = land_rgb
        for code_id, color in country_palette.items():
            selected = (ids == code_id) & is_land
            rgb[selected] = color
        image.paste(Image.fromarray(rgb), (0, y0))
    return expanded


def _paint_country_id_borders(image: Image.Image, ids: np.ndarray,
                              land: Image.Image, color: str, size: int) -> int:
    """Draw country-ID transitions only where both adjacent pixels are land."""
    land_ids = np.asarray(land) != 0
    rgb_color = np.asarray(Image.new("RGB", (1, 1), color), dtype=np.uint8)[0, 0]
    tile_size = 768
    drawn = 0
    for y0 in range(0, size, tile_size):
        y1 = min(size, y0 + tile_size)
        for x0 in range(0, size, tile_size):
            x1 = min(size, x0 + tile_size)
            sy0, sy1 = max(0, y0 - 1), min(size, y1 + 1)
            sx0, sx1 = max(0, x0 - 1), min(size, x1 + 1)
            local_ids = np.pad(ids[sy0:sy1, sx0:sx1], 1)
            local_land = np.pad(land_ids[sy0:sy1, sx0:sx1], 1)
            ly0, lx0 = 1 + y0 - sy0, 1 + x0 - sx0
            current = local_ids[ly0:ly0 + y1 - y0, lx0:lx0 + x1 - x0]
            current_land = local_land[ly0:ly0 + y1 - y0, lx0:lx0 + x1 - x0]
            edge = np.zeros(current.shape, dtype=bool)
            for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                neighbour = local_ids[ly0 + dy:ly0 + dy + y1 - y0,
                                     lx0 + dx:lx0 + dx + x1 - x0]
                neighbour_land = local_land[ly0 + dy:ly0 + dy + y1 - y0,
                                            lx0 + dx:lx0 + dx + x1 - x0]
                edge |= ((current != neighbour) & (current != 0) &
                         (neighbour != 0) & current_land & neighbour_land)
            if not edge.any():
                continue
            rgb = np.asarray(image.crop((x0, y0, x1, y1))).copy()
            rgb[edge] = rgb_color
            image.paste(Image.fromarray(rgb), (x0, y0))
            drawn += int(edge.sum())
    return drawn


def _draw_admin1_lines(image: Image.Image, source: Path, extent,
                       calibration, canvas: Canvas, color: str,
                       width: int) -> int:
    """Draw Natural Earth province/state lines; caller clips them to actual land."""
    draw = ImageDraw.Draw(image)
    count = 0
    for shape, attr in features(source):
        if attr.get("ADM0_A3") not in _NORTH_AMERICAN_COUNTRIES or not _in_scope(shape, extent):
            continue
        stops = list(shape.parts) + [len(shape.points)]
        for start, stop in zip(stops, stops[1:]):
            points = np.asarray(shape.points[start:stop], dtype=float)
            for path in _ring_paths(points, calibration, canvas, minimum=2):
                if len(path) >= 2:
                    draw.line(path, fill=color, width=width, joint="curve")
                    count += 1
    return count


def _province_overlay(image: Image.Image, source: Path, extent, calibration,
                      canvas: Canvas, land: Image.Image, color: str,
                      water_color: str, width: int) -> int:
    """Rasterize and clip state/province lines by wiping the water pixels."""
    count = _draw_admin1_lines(image, source, extent, calibration, canvas,
                               color, width)
    water = ImageChops.invert(land)
    image.paste(water_color, (0, 0), water)
    return count


def _admin1_labels(source: Path, extent) -> list[tuple[str, float, float]]:
    labels = []
    for shape, attr in features(source):
        if attr.get("adm0_a3") not in _NORTH_AMERICAN_COUNTRIES or not _in_scope(shape, extent):
            continue
        name = attr.get("name_en") or attr.get("name")
        if name:
            labels.append((name, float(attr["longitude"]), float(attr["latitude"])))
    return labels


def _draw_labels(image: Image.Image, labels, config, calibration,
                 canvas: Canvas, font_path: Path) -> int:
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(font_path), max(1, round(config["label_size"] * canvas.size / 8192)))
    occupied = []
    count = 0
    for name, lon, lat in labels:
        if name in config["suppress_labels"]:
            continue
        x, y = canvas.pixels(calibration([[lon, lat]]))[0]
        text = config["label_overrides"].get(name, name)
        box = draw.textbbox((x, y), text, font=font, anchor="mm")
        box = (box[0] - 12, box[1] - 8, box[2] + 12, box[3] + 8)
        if min(box) < 0 or box[2] > canvas.size or box[3] > canvas.size:
            continue
        if any(box[0] < other[2] and box[2] > other[0] and
               box[1] < other[3] and box[3] > other[1] for other in occupied):
            continue
        draw.text((x, y), text, font=font, anchor="mm", fill=config["palette"]["label"],
                  stroke_width=max(1, round(canvas.size / 8192)),
                  stroke_fill=config["palette"]["land"])
        occupied.append(box)
        count += 1

    country_font = ImageFont.truetype(
        str(font_path), max(1, round(config["country_label_size"] * canvas.size / 8192)))
    for name, lon, lat in config["country_labels"]:
        point = tuple(canvas.pixels(calibration([[lon, lat]]))[0])
        draw.text(point, name, font=country_font, anchor="mm",
                  fill=config["palette"]["country_label"])
        count += 1
    return count


def render_detailed(config: dict, sources: dict[str, Path], calibration,
                    font_path: Path, *, land_mask_path: Path | None = None) -> tuple[Image.Image, dict[str, int]]:
    """Render detailed clean geography when ``detailed_shores`` is enabled.

    Required sources are ``gshhg`` (the GSHHG 2.3.7 ZIP),
    ``nhd_lake_michigan`` (a GeoJSON FeatureCollection), and the four
    Natural Earth ZIP paths used by :mod:`background.render`. All vector layers
    are transformed by the same supplied calibration. GSHHG/NHD/NE geometry is
    used as geographic source data; this renderer does not use native map art.
    """
    detail = config.get("detailed_shores")
    if not detail:
        raise ValueError("render_detailed requires config['detailed_shores']")
    if isinstance(detail, dict) and detail.get("scope", "NorthAmerica") not in (
            "NorthAmerica", "scopeNorthAmerica"):
        raise ValueError("Detailed shoreline scope must be NorthAmerica")

    size = int(config["texture_size"])
    if size < 1:
        raise ValueError("texture_size must be positive")
    extent = config["geographic_extent"]
    canvas = Canvas(config["world_bounds"], size)
    palette = config["palette"]
    image = Image.new("RGB", (size, size), palette["water"])
    land = Image.new("L", (size, size), 0)

    counts = {
        "countries": 0,
        "gshhg_land_polygons": 0,
        "natural_earth_lakes": 0,
        "nhd_lake_michigan": 0,
        "country_border_pixels": 0,
        "admin1_line_paths": 0,
        "admin1": 0,
        "labels": 0,
    }
    counts["gshhg_land_polygons"] = _paint_detailed_land(
        land, Path(sources["gshhg"]), extent, calibration, canvas)

    lake_source = Path(sources[config.get("lake_layer", "ne_10m_lakes")])
    for shape, attr in features(lake_source):
        if not _in_scope(shape, extent) or (attr.get("name") or "").casefold() == "lake michigan":
            continue
        _paint_lake(land, list(rings(shape)), calibration, canvas)
        counts["natural_earth_lakes"] += 1

    nhd = json.loads(Path(sources["nhd_lake_michigan"]).read_text(encoding="utf-8"))
    lake_features = nhd.get("features", [])
    if len(lake_features) != 1 or lake_features[0].get("geometry", {}).get("type") != "Polygon":
        raise ValueError("NHD Lake Michigan source must contain exactly one Polygon feature")
    props = lake_features[0].get("properties", {})
    if props.get("GNIS_NAME") != "Lake Michigan" or props.get("GNIS_ID") != "01623080":
        raise ValueError("NHD waterbody identity mismatch; expected Lake Michigan GNIS 01623080")
    _paint_lake(
        land, lake_features[0]["geometry"]["coordinates"], calibration, canvas,
        geojson_winding=True)
    counts["nhd_lake_michigan"] = 1

    country_source = Path(sources[config.get("country_layer", "ne_10m_admin_0_countries")])
    country_mask = Image.new("L", (size, size), 0)
    source_ids, code_ids, counts["countries"] = _color_country_mask(
        country_mask, country_source, extent, calibration, canvas)
    country_id_raster = _extend_and_color(image, source_ids, code_ids, land, palette, size)
    del source_ids
    country_mask.close()

    counts["country_border_pixels"] = _paint_country_id_borders(
        image, country_id_raster, land, palette["coast"], size)
    del country_id_raster

    admin1_lines = Path(sources["ne_10m_admin_1_states_provinces_lines"])
    line_width = max(1, round(2 * size / 8192))
    counts["admin1_line_paths"] = _province_overlay(
        image, admin1_lines, extent, calibration, canvas, land,
        palette["province_border"], palette["water"], line_width)
    admin1_labels = _admin1_labels(
        Path(sources["ne_10m_admin_1_states_provinces"]), extent)
    counts["admin1"] = len(admin1_labels)

    # A one-pixel inner land edge keeps fine shoreline detail legible at 16k
    # without painting over shallow channels with a broad diagnostic stroke.
    coast_edge = ImageChops.subtract(land, land.filter(ImageFilter.MinFilter(3)))
    image.paste(palette["coast"], (0, 0), coast_edge)
    counts["labels"] = _draw_labels(
        image,
        admin1_labels, config, calibration, canvas, Path(font_path))
    if land_mask_path is not None:
        land.save(land_mask_path)
    land.close()
    return image, counts
