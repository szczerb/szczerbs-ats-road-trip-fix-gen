"""Compose a north-up map in native game X/Z coordinates."""

from collections import defaultdict
import colorsys
from itertools import pairwise
import math

from PIL import Image, ImageDraw, ImageFont

TILE_SIZE = 4000
COLORS = (
    (65, 190, 250), (251, 174, 59), (227, 114, 227), (139, 230, 118),
    (252, 113, 119), (95, 223, 202), (188, 156, 255), (250, 220, 104),
    (170, 218, 255), (255, 182, 152), (205, 228, 152), (235, 145, 186),
)
STOCK = (175, 186, 190)


def footprint_bounds(tiles):
    x, z = zip(*tiles)
    return (
        (min(x) - .25) * TILE_SIZE, (min(z) - .25) * TILE_SIZE,
        (max(x) + 1.25) * TILE_SIZE, (max(z) + 1.25) * TILE_SIZE,
    )


def _background(raster, atlas, bounds, size):
    width, height = size
    x0, z0, x1, z1 = bounds
    ax, az, bx, bz = atlas
    sx, sz = raster.width / (bx - ax), raster.height / (bz - az)
    return raster.transform(
        size, Image.Transform.AFFINE,
        ((x1 - x0) * sx / width, 0, (x0 - ax) * sx,
         0, (z1 - z0) * sz / height, (z0 - az) * sz),
        resample=Image.Resampling.BICUBIC, fillcolor=(55, 59, 64),
    )


def _dashed(draw, points, fill, width, length):
    """Carry dash phase through vertices so densely sampled curves stay dashed."""
    remaining, on = length, True
    for start, end in pairwise(points):
        dx, dy = end[0] - start[0], end[1] - start[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            continue
        offset = 0.0
        while offset < distance:
            step = min(remaining, distance - offset)
            if on:
                draw.line(
                    [(start[0] + dx * t / distance, start[1] + dy * t / distance)
                     for t in (offset, offset + step)], fill=fill, width=width,
                )
            offset += step
            remaining -= step
            if remaining <= 1e-8:
                remaining, on = length, not on


def _legend_rows(draw, entries, width, font, gap):
    rows = [[]]
    used = 0
    for color, label in entries:
        while draw.textlength(label, font=font) > width - gap and len(label) > 1:
            label = label[:-2] + '…'
        length = math.ceil(draw.textlength(label, font=font)) + 2 * gap
        if rows[-1] and used + length > width:
            rows.append([])
            used = 0
        rows[-1].append((color, label, length))
        used += length
    return rows


def draw_map(raster, atlas, bounds, tiles, geometries, providers, title, *,
             long_edge, mode, issue_count, issue_tiles, baseline, stock, output):
    """Draw tile fills and lines. Provider order controls overlap painting."""
    x0, z0, x1, z1 = bounds
    extent_x, extent_z = x1 - x0, z1 - z0
    unit = max(1, round(long_edge / 2048))
    margin = 16 * unit
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 13 * unit)
        title_font = ImageFont.truetype('DejaVuSans.ttf', 18 * unit)
    except OSError:
        font = ImageFont.load_default(size=13 * unit)
        title_font = ImageFont.load_default(size=18 * unit)
    palette = {}
    for index, provider in enumerate(providers):
        if index < len(COLORS):
            palette[provider] = COLORS[index]
        else:
            rgb = colorsys.hsv_to_rgb((index * .6180339887) % 1, .86, .8)
            palette[provider] = tuple(round(component * 255) for component in rgb)
    entries = [(color, provider) for provider, color in palette.items()]
    if stock:
        entries.append((STOCK, 'Stock / DLC'))
    probe = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    # Keep the legend readable for exceptionally tall, thin map crops.
    width = max(512 * unit, round(long_edge * min(1, extent_x / extent_z)))
    width = min(width, long_edge)
    rows = _legend_rows(probe, entries, width - 2 * margin, font, 20 * unit)
    header = (94 + 19 * len(rows)) * unit
    available_height = max(1, long_edge - header)
    scale = min(width / extent_x, available_height / extent_z)
    map_width = min(width, max(1, round(scale * extent_x)))
    map_height = min(available_height, max(1, round(scale * extent_z)))
    left = (width - map_width) // 2
    height = header + map_height
    if max(width, height) < long_edge:
        height = long_edge

    def project(x, z):
        return (x - x0) * map_width / extent_x, (z - z0) * map_height / extent_z

    artwork = _background(raster, atlas, bounds, (map_width, map_height))
    # Dim the source artwork just enough to keep subtle roads visible.
    artwork = Image.blend(artwork, Image.new('RGB', artwork.size, (15, 24, 34)), .19)
    for provider, color in palette.items():
        overlay = Image.new('RGBA', artwork.size)
        draw = ImageDraw.Draw(overlay)
        for (x, z), replaced in tiles.get(provider, {}).items():
            sx, sz = project(x * TILE_SIZE, z * TILE_SIZE)
            ex, ez = project((x + 1) * TILE_SIZE, (z + 1) * TILE_SIZE)
            rectangle = round(sx), round(sz), round(ex) - 1, round(ez) - 1
            if rectangle[2] >= rectangle[0] and rectangle[3] >= rectangle[1]:
                draw.rectangle(
                    rectangle, fill=(*color, 52 if replaced else 96),
                    outline=(*color, 151 if replaced else 220),
                )
        artwork.paste(overlay, mask=overlay.getchannel('A'))

    draw = ImageDraw.Draw(artwork)
    by_provider = defaultdict(list)
    for provider, line in geometries:
        by_provider[provider].append(line)
    for provider in (None, *providers):
        color = palette.get(provider, STOCK)
        for line in by_provider[provider]:
            if len(line.points) < 2:
                continue
            # Skip lines entirely outside the chosen view before dash sampling.
            xs, zs = zip(*line.points)
            if max(xs) < x0 or min(xs) > x1 or max(zs) < z0 or min(zs) > z1:
                continue
            points = [project(x, z) for x, z in line.points]
            width_px = unit if line.kind == 'prefab' or line.hidden or provider is None else 2 * unit
            if line.approximate or line.hidden:
                _dashed(draw, points, (255, 247, 223) if line.approximate else color,
                        width_px, (3 if line.approximate else 7) * unit)
            else:
                if provider is not None and line.kind == 'road':
                    draw.line(points, fill=(24, 29, 37), width=width_px + 2 * unit)
                draw.line(points, fill=color, width=width_px)

    for x, z in issue_tiles:
        sx, sz = project(x * TILE_SIZE, z * TILE_SIZE)
        ex, ez = project((x + 1) * TILE_SIZE, (z + 1) * TILE_SIZE)
        if ex < 0 or ez < 0 or sx >= map_width or sz >= map_height:
            continue
        size = min(8 * unit, (ex - sx) / 4, (ez - sz) / 4)
        draw.polygon([(sx + 1, sz + 1), (sx + 1 + size, sz + 1),
                      (sx + 1, sz + 1 + size)], fill=(255, 117, 100))

    canvas = Image.new('RGB', (width, height), (24, 32, 43))
    canvas.paste(artwork, (left, header))
    draw = ImageDraw.Draw(canvas)
    label = title
    while draw.textlength(label, font=title_font) > width - 2 * margin and len(label) > 1:
        label = label[:-2] + '…'
    draw.text((margin, 10 * unit), label, fill='white', font=title_font)
    warning = f'{issue_count:,} geometry issues' + (' · marked tiles' if issue_tiles else '')
    draw.text((margin, 36 * unit), f'{mode} | North up | {warning}',
              fill=(224, 234, 241), font=font)
    draw.text((margin, 54 * unit), 'Solid road  ·  Dashed hidden  ·  Light dotted approximation  ·  Thin prefab',
              fill=(224, 234, 241), font=font)
    tile_key = ('Tiles may include unchanged roads. Pale fill overrides; strong fill is new.'
                if baseline else 'Supplied tiles may include unchanged roads. No lower-priority baseline.')
    if x0 < atlas[0] or z0 < atlas[1] or x1 > atlas[2] or z1 > atlas[3]:
        tile_key = 'Gray outside the registered atlas. ' + tile_key
    while draw.textlength(tile_key, font=font) > width - 2 * margin and len(tile_key) > 1:
        tile_key = tile_key[:-2] + '…'
    draw.text((margin, 72 * unit), tile_key, fill=(224, 234, 241), font=font)
    for index, row in enumerate(rows):
        y = (92 + 19 * index) * unit
        x = margin
        for color, name, length in row:
            draw.rectangle((x, y + 4 * unit, x + 10 * unit, y + 13 * unit), fill=color)
            draw.text((x + 15 * unit, y), name, fill='white', font=font)
            x += length
    with output.open('xb') as stream:
        canvas.save(stream, format='PNG')
    return canvas.size
