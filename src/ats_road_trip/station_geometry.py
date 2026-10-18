"""Geometry proposals for explicitly selected station-parking experiments.

PPD map polygons are UI proxies, not collision geometry. This module exposes
that evidence and uses it for reproducible hypotheses; it never calls rest's
proximity policy or copies a truck-rest polygon. See TASK-0039 for sources.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import struct

from .ppd import inspect_ppd
from .rest_stops import _inside, _point_segment, _segments_intersect, _validate_polygon, polygon_distance


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


@dataclass(frozen=True)
class ParkingParameters:
    width: float = 3.0
    depth: float = 6.0
    wall_setback: float = 2.5
    obstacle_margin: float = 0.5
    pump_clearance: float = 6.0
    road_clearance: float = 3.5
    aisle_depth: float = 4.0
    edge_spacing: float = 3.2
    max_station_distance: float = 35.0

    def __post_init__(self):
        for key,value in asdict(self).items():
            if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{key} must be positive and finite')
        if self.width < 2 or self.depth < 4 or self.width > 6 or self.depth > 12:
            raise ValueError('Parking footprint must remain passenger-car sized')
        if self.edge_spacing < self.width:
            raise ValueError('Candidate spacing must be at least the bay width')


def propose_unmarked_parking(data: bytes, parameters: ParkingParameters | None = None) -> dict:
    """Propose bays along pump-facing edges of dark non-canopy map polygons.

    This is a geometry-only hypothesis. A canopy is identified by containing a
    GAS locator; every dark polygon remains an exclusion obstacle regardless.
    No native car/truck rest vertices participate in candidate construction.
    """
    parameters = parameters or ParkingParameters()
    geometry = inspect_station_map(data)
    polygons = geometry['polygons']
    accessible = [p for p in polygons if p['color']==1]
    dark = [p for p in polygons if p['color']==2]
    obstacles = [p for p in polygons if p['color']!=1]
    gas = [_xz([s['position']])[0] for s in geometry['gas_spawns']]
    if not accessible or not dark:
        return {'method':'unmarked_map_geometry', 'parameters':asdict(parameters),
                'geometry':geometry, 'candidates':[], 'selected':None,
                'blockers':['No accessible-area and building map proxies available']}
    centroid = tuple(sum(p[i] for p in gas)/len(gas) for i in range(2))
    candidates = []
    for building in dark:
        footprint = _xz(building['vertices'])
        if any(_contains(p,footprint) for p in gas):
            building['interpretation']='canopy_proxy_contains_gas_locator'
            continue
        building['interpretation']='building_proxy_without_gas_locator'
        area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(footprint,footprint[1:]+footprint[:1]))
        for edge,(a,b) in enumerate(zip(footprint,footprint[1:]+footprint[:1])):
            length = math.dist(a,b)
            if length < parameters.width+1:
                continue
            tangent = ((b[0]-a[0])/length,(b[1]-a[1])/length)
            normal = (tangent[1],-tangent[0]) if area>0 else (-tangent[1],tangent[0])
            center = ((a[0]+b[0])/2,(a[1]+b[1])/2)
            toward = (centroid[0]-center[0],centroid[1]-center[1])
            if normal[0]*toward[0]+normal[1]*toward[1] <= 0:
                continue
            usable = length-1-parameters.width
            if usable/parameters.edge_spacing > 1000:
                raise ValueError('Building edge would exceed bounded candidate budget')
            count = int(usable//parameters.edge_spacing)+1
            # Center the finite row; no special station coordinates are supplied.
            first = (length-(count-1)*parameters.edge_spacing)/2
            for index in range(count):
                t = first+index*parameters.edge_spacing
                origin = (a[0]+t*tangent[0],a[1]+t*tangent[1])
                def rectangle(start,end):
                    return [(origin[0]+s*tangent[0]+n*normal[0],origin[1]+s*tangent[1]+n*normal[1])
                            for s,n in [(-parameters.width/2,start),(parameters.width/2,start),
                                        (parameters.width/2,end),(-parameters.width/2,end)]]
                points = rectangle(parameters.wall_setback,parameters.wall_setback+parameters.depth)
                aisle = rectangle(parameters.wall_setback+parameters.depth,
                                  parameters.wall_setback+parameters.depth+parameters.aisle_depth)
                reasons = []
                if not any(_within(points+[],_xz(p['vertices'])) and _within(aisle,_xz(p['vertices'])) for p in accessible):
                    reasons.append('footprint_or_approach_outside_accessible_map_proxy')
                obstacle_ids = [p['id'] for p in obstacles
                                if polygon_distance(points,_xz(p['vertices'])) <= parameters.obstacle_margin
                                or polygon_distance(aisle,_xz(p['vertices'])) <= parameters.obstacle_margin]
                if obstacle_ids:
                    reasons.append('footprint_or_approach_intersects_obstacle_proxy')
                clearance = min(polygon_distance(points,[p]) for p in gas)
                if clearance < parameters.pump_clearance:
                    reasons.append('too_close_to_gas_interaction')
                bay_center = tuple(sum(p[i] for p in points)/4 for i in range(2))
                if min(math.dist(bay_center,p) for p in gas)>parameters.max_station_distance:
                    reasons.append('outside_local_station_search')
                road_conflicts=[]
                for road in geometry['roads']:
                    segment=_xz(road['vertices'])
                    if (polygon_distance(points,segment)<parameters.road_clearance
                            or polygon_distance(aisle,segment)<parameters.road_clearance):
                        road_conflicts.append(road['indices'])
                if road_conflicts:
                    reasons.append('intersects_map_navigation_corridor_proxy')
                key={'building':building['id'],'edge':edge,'index':index,
                     'parameters':asdict(parameters),'polygon':points}
                uid=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
                if len(candidates)>=128:
                    raise ValueError('Station geometry exceeds bounded 128-candidate budget')
                candidates.append({'id':uid,'building_map_polygon':building['id'],'edge':edge,
                                   'polygon_xz':[list(p) for p in points],
                                   'approach_xz':[list(p) for p in aisle],
                                   'pump_clearance':clearance,'obstacle_ids':obstacle_ids,
                                   'road_conflicts':road_conflicts,'rejection_reasons':reasons,
                                   'evidence':'Hypothesis — generated from source UI-map polygons',
                                   'height_status':'unresolved_without_model_surface_evidence'})
    candidates.sort(key=lambda c:(bool(c['rejection_reasons']),-c['pump_clearance'],c['id']))
    selected=next((c for c in candidates if not c['rejection_reasons']),None)
    return {'method':'unmarked_map_geometry','parameters':asdict(parameters),'geometry':geometry,
            'candidates':candidates,'selected':selected,
            'blockers':[] if selected else ['No candidate passes the disclosed geometry-proxy checks'],
            'runtime_status':'unverified; no game operation performed',
            'generation_readiness':'Requires independent model surface/obstacle review; UI polygons alone do not prove safe geometry'}
