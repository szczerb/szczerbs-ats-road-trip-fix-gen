"""Deterministic original cartography from Natural Earth vectors."""
from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .geography import features


class Canvas:
    def __init__(self, bounds, size):
        self.bounds, self.size = bounds, size

    def pixels(self, points):
        x0, z0, x1, z1 = self.bounds
        points = np.asarray(points, dtype=float)
        return (points - [x0, z0]) / [x1 - x0, z1 - z0] * self.size


def rings(shape):
    stops = list(shape.parts) + [len(shape.points)]
    for start, stop in zip(stops, stops[1:]):
        points = np.asarray(shape.points[start:stop], dtype=float)
        if len(points) >= 3:
            yield points


def _in_scope(shape, extent):
    west, south, east, north = extent
    a, b, c, d = shape.bbox
    return c >= west and a <= east and d >= south and b <= north


def _ring_pixels(points, calibration, canvas, minimum=3):
    # Split antimeridian rings instead of drawing a line across the map.
    # The canvas contains eastern-hemisphere geography only near the dateline.
    result = []
    breaks = np.flatnonzero(np.abs(np.diff(points[:, 0])) > 180) + 1
    for piece in np.split(points, breaks):
        if len(piece) >= minimum:
            # Geographic coordinates outside this view can wrap the projection.
            if np.all(piece[:, 0] > -30) or np.all(piece[:, 0] < -180):
                continue
            result.append(canvas.pixels(calibration(piece)))
    return result


def render(config, sources, calibration, font_path: Path):
    size = config['texture_size']
    canvas = Canvas(config['world_bounds'], size)
    palette = config['palette']
    image = Image.new('RGB', (size, size), palette['water'])
    draw = ImageDraw.Draw(image)
    counts = {'countries': 0, 'admin1': 0, 'lakes': 0, 'labels': 0}
    borders = []
    # R0 defaults remain reproducible; later revisions pin finer shoreline data.
    for shape, attr in features(sources[config.get('country_layer','ne_50m_admin_0_countries')]):
        if not _in_scope(shape, config['geographic_extent']):
            continue
        country = attr['ADM0_A3']
        color = palette.get(country, palette['land'])
        for points in rings(shape):
            # Shapefile exterior rings clockwise, holes counterclockwise.
            signed = np.sum(points[:-1, 0] * points[1:, 1] - points[1:, 0] * points[:-1, 1])
            for polygon in _ring_pixels(points, calibration, canvas):
                draw.polygon([tuple(p) for p in polygon], fill=color if signed < 0 else palette['water'])
                borders.append(polygon)
        counts['countries'] += 1
    for shape, attr in features(sources['ne_10m_admin_1_states_provinces_lines']):
        if attr['ADM0_A3'] not in ('USA','CAN','MEX'):
            continue
        stops = list(shape.parts) + [len(shape.points)]
        for start, stop in zip(stops, stops[1:]):
            points = np.asarray(shape.points[start:stop],dtype=float)
            for line in _ring_pixels(points,calibration,canvas,minimum=2):
                draw.line([tuple(p) for p in line],fill=palette['province_border'],width=2,joint='curve')
    labels = []
    for shape, attr in features(sources['ne_10m_admin_1_states_provinces']):
        if attr['adm0_a3'] not in ('USA', 'CAN', 'MEX'):
            continue
        if not _in_scope(shape, config['geographic_extent']):
            continue
        name = attr.get('name_en') or attr['name']
        if name:
            labels.append((name, attr['longitude'], attr['latitude'], attr['adm0_a3']))
        counts['admin1'] += 1
    for shape, attr in features(sources[config.get('lake_layer','ne_50m_lakes')]):
        if not _in_scope(shape, config['geographic_extent']):
            continue
        # Preserve lake islands using a mask over the existing country fill.
        # This is opt-in so the historical r0 remains byte reproducible.
        preserve_islands = config.get('preserve_lake_islands',False)
        lake_rings = []
        for points in rings(shape):
            for polygon in _ring_pixels(points, calibration, canvas):
                coords = [tuple(p) for p in polygon]
                if preserve_islands:
                    signed = np.sum(points[:-1,0]*points[1:,1]-points[1:,0]*points[:-1,1])
                    lake_rings.append((coords,signed<0))
                else:
                    draw.polygon(coords, fill=palette['water'])
                    draw.line(coords, fill=palette['coast'], width=2, joint='curve')
        if lake_rings:
            # Bound each mask to its feature, rather than clearing/pasting a full
            # 8192-square image hundreds of times. Holes reveal existing land;
            # separate water features already painted underneath stay intact.
            all_points = np.array([p for coords,_ in lake_rings for p in coords])
            left,top = np.maximum(0,np.floor(all_points.min(axis=0))).astype(int)
            right,bottom = np.minimum(size,np.ceil(all_points.max(axis=0))+1).astype(int)
            if right>left and bottom>top:
                mask = Image.new('L',(right-left,bottom-top))
                mask_draw = ImageDraw.Draw(mask)
                for coords,outer in lake_rings:
                    mask_draw.polygon([(x-left,y-top) for x,y in coords],fill=255 if outer else 0)
                image.paste(palette['water'],(left,top,right,bottom),mask)
            for coords,_ in lake_rings:
                draw.line(coords,fill=palette['coast'],width=2,joint='curve')
        counts['lakes'] += 1
    for polygon in borders:
        draw.line([tuple(p) for p in polygon], fill=palette['coast'], width=3, joint='curve')

    # Label only administrative regions, letting the game provide city names.
    font = ImageFont.truetype(str(font_path), config['label_size'])
    occupied = []
    for name, lon, lat, country in labels:
        if name in config['suppress_labels']:
            continue
        x, y = canvas.pixels(calibration([[lon, lat]]))[0]
        text = config['label_overrides'].get(name, name)
        box = draw.textbbox((x, y), text, font=font, anchor='mm')
        box = (box[0] - 12, box[1] - 8, box[2] + 12, box[3] + 8)
        if min(box) < 0 or box[2] > size or box[3] > size:
            continue
        if any(box[0] < b[2] and box[2] > b[0] and box[1] < b[3] and box[3] > b[1] for b in occupied):
            continue
        draw.text((x, y), text, font=font, anchor='mm', fill=palette['label'],
                  stroke_width=1, stroke_fill=palette['land'])
        occupied.append(box)
        counts['labels'] += 1
    big = ImageFont.truetype(str(font_path), config['country_label_size'])
    for name, lon, lat in config['country_labels']:
        point = tuple(canvas.pixels(calibration([[lon, lat]]))[0])
        draw.text(point, name, font=big, anchor='mm', fill=palette['country_label'])
    return image, counts


def icon(image, font_path):
    """Original geographic artwork and plain typography; no third-party logos."""
    icon = image.resize((276, 276), Image.Resampling.LANCZOS).crop((0, 36, 276, 198))
    draw = ImageDraw.Draw(icon)
    draw.rectangle((0, 112, 276, 162), fill='#17232a')
    font = ImageFont.truetype(str(font_path), 15)
    small = ImageFont.truetype(str(font_path), 11)
    draw.text((11, 117), 'ROAD TRIP', font=font, fill='#e3d4ac')
    draw.text((11, 140), 'North America background', font=small, fill='#d5e1df')
    return icon


def previews(image, config, calibration, anchors, font_path, output):
    """Overall and regional image-plane overlays, separate from mod contents."""
    output.mkdir(parents=True, exist_ok=False)
    canvas = Canvas(config['world_bounds'], image.width)
    overview = image.copy()
    draw = ImageDraw.Draw(overview)
    font = ImageFont.truetype(str(font_path), 22)
    for point in anchors:
        target = canvas.pixels([[point['x'], point['z']]])[0]
        predicted = canvas.pixels(calibration([[point['lon'], point['lat']]]))[0]
        a, b = tuple(target), tuple(predicted)
        draw.line([a, b], fill='#ffb153', width=5)
        x, y = a
        color = '#5ae1ff' if point['role'] == 'check' else '#e3e8e5'
        draw.ellipse((x-8,y-8,x+8,y+8), outline=color, width=3)
        x, y = b
        draw.line((x-7,y-7,x+7,y+7), fill='#ffb153', width=3)
        draw.line((x-7,y+7,x+7,y-7), fill='#ffb153', width=3)
        draw.text((target[0]+12,target[1]-20), point['name'], fill=color, font=font,
                  stroke_width=2, stroke_fill='#17232a')
    overlay_paths = []
    overview.resize((2048,2048), Image.Resampling.LANCZOS).save(output/'overall-alignment.png')
    image.resize((2048,2048), Image.Resampling.LANCZOS).save(output/'overall.png')
    for name, bounds in config['regions'].items():
        p = canvas.pixels(np.array(bounds).reshape(2,2)).ravel()
        box = tuple(int(round(x)) for x in p)
        region = overview.crop(box)
        width = min(region.width, 2200)
        region = region.resize((width, round(region.height*width/region.width)), Image.Resampling.LANCZOS)
        region.save(output/(name+'.png'))
        overlay_paths.append(name+'.png')
    links = ['overall.png','overall-alignment.png',*overlay_paths]
    cards = '\n'.join(f'<figure><a href="{p}"><img src="{p}" loading="lazy"></a><figcaption>{p}</figcaption></figure>' for p in links)
    (output/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Road Trip background review</title>
<style>body{margin:2rem;background:#121c22;color:#dbe4e3;font:16px sans-serif}img{max-width:100%;height:auto}figure{margin:2rem 0}a{color:#7ad6e7}</style>
<h1>Original North America background — offline previews</h1>
<p>Circle: actual game city reference. Amber cross: projected geographic location. Cyan: held-out check; white: fitting input. Amber line: error. These previews do not prove the game's UI mapping or runtime rendering.</p>
''' + cards, encoding='utf-8')
