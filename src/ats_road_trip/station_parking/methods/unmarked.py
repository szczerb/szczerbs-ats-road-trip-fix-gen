"""Propose unmarked station parking from PPD building-side geometry."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math

from ..geometry import _contains, _within, inspect_station_map, _xz
from ...rest_stops import polygon_distance

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

def propose_unmarked_parking(data: bytes, parameters: ParkingParameters | None = None, *, layouts=('perpendicular',)) -> dict:
    """Propose bays along pump-facing edges of dark non-canopy map polygons.

    This is a geometry-only hypothesis. A canopy is identified by containing a
    GAS locator; every dark polygon remains an exclusion obstacle regardless.
    No native car/truck rest vertices participate in candidate construction.
    """
    parameters = parameters or ParkingParameters()
    if (not isinstance(layouts,(list,tuple)) or not layouts
            or set(layouts)-{'perpendicular','parallel'} or len(set(layouts))!=len(layouts)):
        raise ValueError('Select explicit unique perpendicular or parallel layouts')
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
            for layout in layouts:
                along_width=parameters.width if layout=='perpendicular' else parameters.depth
                outward_depth=parameters.depth if layout=='perpendicular' else parameters.width
                spacing=max(parameters.edge_spacing,along_width)
                if length<along_width+1:continue
                usable = length-1-along_width
                if usable/spacing > 1000:
                    raise ValueError('Building edge would exceed bounded candidate budget')
                count = int(usable//spacing)+1
                # Center the finite row; no special station coordinates are supplied.
                first = (length-(count-1)*spacing)/2
                for index in range(count):
                    t = first+index*spacing
                    origin = (a[0]+t*tangent[0],a[1]+t*tangent[1])
                    def rectangle(start,end):
                        return [(origin[0]+s*tangent[0]+n*normal[0],origin[1]+s*tangent[1]+n*normal[1])
                                for s,n in [(-along_width/2,start),(along_width/2,start),
                                            (along_width/2,end),(-along_width/2,end)]]
                    points = rectangle(parameters.wall_setback,parameters.wall_setback+outward_depth)
                    aisle = rectangle(parameters.wall_setback+outward_depth,
                                      parameters.wall_setback+outward_depth+parameters.aisle_depth)
                    reasons = []
                    if not any(_within(points+[],_xz(p['vertices'])) and (layout=='parallel' or _within(aisle,_xz(p['vertices']))) for p in accessible):
                        reasons.append('footprint_or_approach_outside_accessible_map_proxy')
                    obstacle_ids = [p['id'] for p in obstacles
                                    if polygon_distance(points,_xz(p['vertices'])) <= parameters.obstacle_margin
                                    or (layout!='parallel' and polygon_distance(aisle,_xz(p['vertices'])) <= parameters.obstacle_margin)]
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
                                or (layout!='parallel' and polygon_distance(aisle,segment)<parameters.road_clearance)):
                            road_conflicts.append(road['indices'])
                    if road_conflicts:
                        reasons.append('intersects_map_navigation_corridor_proxy')
                    key={'building':building['id'],'edge':edge,'index':index,
                         'parameters':asdict(parameters),'polygon':points}
                    if layout!='perpendicular':key['layout']=layout
                    uid=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
                    if len(candidates)>=128:
                        raise ValueError('Station geometry exceeds bounded 128-candidate budget')
                    candidates.append({'id':uid,'building_map_polygon':building['id'],'edge':edge,
                                       'polygon_xz':[list(p) for p in points],
                                       'approach_xz':[list(p) for p in aisle] if layout!='parallel' else None,
                                       'pump_clearance':clearance,'obstacle_ids':obstacle_ids,
                                       'road_conflicts':road_conflicts,'rejection_reasons':reasons,
                                       'evidence':'Hypothesis — generated from source UI-map polygons',
                                       'height_status':'unresolved_without_model_surface_evidence',
                                       **({'layout':layout,**({'direction_xz':list(tangent)} if layout=='parallel' else {'parking_heading_xz':[-normal[0],-normal[1]]})}
                                          if len(layouts)>1 or layout!='perpendicular' else {})})
    candidates.sort(key=lambda c:(bool(c['rejection_reasons']),-c['pump_clearance'],c['id']))
    selected=next((c for c in candidates if not c['rejection_reasons']),None)
    return {'method':'unmarked_map_geometry','parameters':asdict(parameters),'geometry':geometry,
            'candidates':candidates,'selected':selected,
            'blockers':[] if selected else ['No candidate passes the disclosed geometry-proxy checks'],
            'runtime_status':'unverified; no game operation performed',
            'generation_readiness':'Requires independent model surface/obstacle review; UI polygons alone do not prove safe geometry'}
