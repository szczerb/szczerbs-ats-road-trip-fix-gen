"""Small integrated checks for source-vector shore and border composition."""
from pathlib import Path
from types import SimpleNamespace
import json

import pytest

pytest.importorskip("numpy")
pytest.importorskip("PIL")
pytest.importorskip("scipy")
pytest.importorskip("shapefile")

import numpy as np
from PIL import ImageFont

from ats_road_trip.background import shores


def _polygon_shape(rings):
    points = []
    parts = []
    for ring in rings:
        parts.append(len(points))
        points.extend(ring)
    xs, ys = zip(*points)
    return SimpleNamespace(parts=parts, points=points,
                           bbox=[min(xs), min(ys), max(xs), max(ys)])


def _clockwise_box(x0, y0, x1, y1):
    return [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]


def _counterclockwise_box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def test_render_keeps_lake_island_and_clips_country_seam_to_land(tmp_path, monkeypatch):
    """A lake hole restores land; the country seam stops in water and returns on the island."""
    sources = {
        "gshhg": tmp_path / "gshhg.zip",
        "nhd_lake_michigan": tmp_path / "michigan.geojson",
        "ne_10m_lakes": tmp_path / "lakes.zip",
        "ne_10m_admin_0_countries": tmp_path / "countries.zip",
        "ne_10m_admin_1_states_provinces_lines": tmp_path / "lines.zip",
        "ne_10m_admin_1_states_provinces": tmp_path / "states.zip",
    }
    sources["nhd_lake_michigan"].write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {
            "GNIS_NAME": "Lake Michigan", "GNIS_ID": "01623080"},
            "geometry": {"type": "Polygon", "coordinates": [[
                [-88, 12], [-86, 12], [-86, 14], [-88, 14], [-88, 12]]]} }]
    }))

    # A continuous continent mask beneath the selected Natural Earth lake.
    land = _polygon_shape([_clockwise_box(-90, 10, -10, 90)])
    lake = _polygon_shape([
        _clockwise_box(-70, 30, -30, 70),
        _counterclockwise_box(-60, 40, -40, 60),
    ])
    country_shapes = [
        (_polygon_shape([_clockwise_box(-90, 10, -50, 90)]), {"ADM0_A3": "USA"}),
        (_polygon_shape([_clockwise_box(-50, 10, -10, 90)]), {"ADM0_A3": "CAN"}),
    ]
    source_features = {
        sources["ne_10m_lakes"]: [(lake, {"name": "Test Lake"})],
        sources["ne_10m_admin_0_countries"]: country_shapes,
        sources["ne_10m_admin_1_states_provinces_lines"]: [],
        sources["ne_10m_admin_1_states_provinces"]: [],
    }
    monkeypatch.setattr(shores, "features", lambda path: iter(source_features[path]))
    # Repeated feature records make per-feature projection setup visible without
    # changing the raster result; production should calibrate this layer once.
    many_land_shapes = [SimpleNamespace(shape=land) for _ in range(24)]
    monkeypatch.setattr(shores, "_gshhg_reader", lambda _path: SimpleNamespace(
        iterShapeRecords=lambda: iter(many_land_shapes), close=lambda: None))
    default_font = ImageFont.load_default()
    monkeypatch.setattr(shores.ImageFont, "truetype", lambda *_args, **_kwargs: default_font)

    config = {
        "detailed_shores": {"scope": "NorthAmerica"},
        "texture_size": 100,
        "geographic_extent": [-100, 0, 0, 100],
        "world_bounds": [-100, 0, 0, 100],
        "palette": {
            "water": "#112233", "land": "#445566", "USA": "#445566",
            "CAN": "#556677", "coast": "#ddeeff",
            "province_border": "#aabbcc", "label": "#ffffff",
            "country_label": "#ffffff",
        },
        "label_size": 8, "country_label_size": 8, "country_labels": [],
        "suppress_labels": [], "label_overrides": {},
    }
    calibration_calls = []

    def calibration(points):
        calibration_calls.append(len(points))
        return np.asarray(points, dtype=float)

    image, counts = shores.render_detailed(
        config, sources, calibration, tmp_path / "font.ttf")

    # The point is inside lake water, far from its edge. The country boundary
    # must not leak into it, even though it crossed the same longitude on land.
    assert image.getpixel((50, 35)) == (17, 34, 51)
    assert image.getpixel((13, 13)) == (17, 34, 51)
    # The oppositely wound inner ring is an island and restores the base land;
    # the country transition is therefore valid again there.
    assert image.getpixel((50, 50)) == (221, 238, 255)
    assert image.getpixel((50, 20)) == (221, 238, 255)
    assert counts["gshhg_land_polygons"] == 24
    assert counts["natural_earth_lakes"] == 1
    assert counts["nhd_lake_michigan"] == 1
    # GSHHG records and the two country features are each projected in a batch.
    assert len(calibration_calls) == 4
