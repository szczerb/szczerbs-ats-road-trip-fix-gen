"""Inspect PPD UI-map polygons used as station geometry evidence."""
from __future__ import annotations

import math
import struct

from ..ppd import inspect_ppd
from ..rest_stops import _inside, _point_segment, _segments_intersect, _validate_polygon

def _xz(points):
    return [(p[0], p[2]) for p in points]

def _contains(point, polygon):
    return _inside(point, polygon) or any(
        _point_segment(point, a, b) < 1e-7 for a, b in zip(polygon, polygon[1:] + polygon[:1]))

def _within(points, polygon):
    # Corners alone do not prove containment in a concave polygon. Check edge
    # midpoints as well, and refuse every proper boundary crossing.
    probes = points + [((a[0]+b[0])/2, (a[1]+b[1])/2)
                       for a, b in zip(points, points[1:]+points[:1])]
    if not all(_contains(p, polygon) for p in probes):
        return False
    for a,b in zip(points, points[1:]+points[:1]):
        for c,d in zip(polygon, polygon[1:]+polygon[:1]):
            cross = lambda p,q,r: (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
            if cross(a,b,c)*cross(a,b,d) < -1e-10 and cross(c,d,a)*cross(c,d,b) < -1e-10:
                return False
    return True

def inspect_station_map(data: bytes) -> dict:
    """Decode exact v25 map-point records with checked neighbor topology.

    The 48-byte record layout is locally cross-checked. Road size 13 is a
    polygon; color bits 17..19 distinguish light/dark/green. Bit 20 is not a
    color bit (a four-bit color mask would misclassify no-outline polygons).
    """
    info = inspect_ppd(data)
    if info['version'] != 25:
        raise ValueError('Station geometry requires PPD v25')
    h = struct.unpack_from('<24I', data)
    if h[8] > 4096:
        raise ValueError('Station map-point budget exceeds 4096 records')
    if h[20] + 48*h[8] != h[21]:
        raise ValueError('PPD map-point count and extent disagree')
    points = []
    for i in range(h[8]):
        values = struct.unpack_from('<II3f6iI', data, h[20]+48*i)
        flags, nav, x, y, z = values[:5]
        count = values[-1]
        if count > 6 or not all(math.isfinite(v) for v in (x,y,z)):
            raise ValueError('Invalid map-point coordinates or neighbor count')
        neighbors = list(values[5:5+count])
        if len(set(neighbors)) != count or any(n < 0 or n >= h[8] or n == i for n in neighbors):
            raise ValueError('Invalid map-point neighbor references')
        points.append({'index':i, 'flags':flags, 'navigation_flags':nav,
                       'road_size':(flags>>8)&15, 'color':(flags>>17)&7,
                       'position':[x,y,z], 'neighbors':neighbors})
    for point in points:
        if any(point['index'] not in points[n]['neighbors'] for n in point['neighbors']):
            raise ValueError('Nonreciprocal map-point neighbors')
    polygons, visited = [], set()
    for point in points:
        if point['road_size'] != 13 or point['index'] in visited:
            continue
        order, previous, current = [], None, point['index']
        while current not in order:
            row = points[current]
            if row['road_size'] != 13 or row['color'] != point['color'] or len(row['neighbors']) != 2:
                raise ValueError('Unsupported map polygon class or branching topology')
            if current in visited:
                raise ValueError('Map polygon components overlap')
            order.append(current)
            if len(order)>64:
                raise ValueError('Station map polygon exceeds 64 vertices')
            choices = [n for n in row['neighbors'] if n != previous]
            previous, current = current, min(choices)
        if current != order[0]:
            raise ValueError('Map polygon does not close')
        visited.update(order)
        vertices = [points[i]['position'] for i in order]
        _validate_polygon(_xz(vertices))
        polygons.append({'id':min(order), 'indices':order, 'color':point['color'],
                         'class':{1:'accessible_proxy',2:'building_or_canopy_proxy',4:'inaccessible_proxy'}.get(point['color'],'unknown'),
                         'vertices':vertices})
    roads = []
    for point in points:
        if point['road_size'] in (13,14):
            continue
        for neighbor in point['neighbors']:
            if neighbor > point['index'] and points[neighbor]['road_size'] != 13:
                roads.append({'indices':[point['index'],neighbor],
                              'vertices':[point['position'],points[neighbor]['position']],
                              'road_sizes':[point['road_size'],points[neighbor]['road_size']]})
    gas = [s for s in info['spawns'] if s['type']==3]
    if not gas:
        raise ValueError('Selected descriptor is not a GAS station')
    return {'map_points':points, 'polygons':polygons, 'roads':roads,
            'gas_spawns':gas,
            'evidence_kind':'PPD UI-map geometry; not measured collision or painted-bay geometry',
            'limitations':['Map polygons can omit furniture, curbs, parked NPCs and height changes.',
                           'Dark polygons can represent canopies as well as solid buildings.']}
