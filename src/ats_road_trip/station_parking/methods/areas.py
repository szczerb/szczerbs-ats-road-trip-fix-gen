"""Deterministic logical parking regions, never isolated fallback bays.

Source paint banks and raised curb boundaries supply parking evidence. Narrow
landscape islands supply parallel edge-strip evidence; driveways are protected
by endpoint setbacks and the same pump/navigation/access tests as other areas.
Variable parked-NPC locators are recorded as evidence, never permanent blockers.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math

from ..geometry import _xz
from ..selection import evaluate_access
from ...rest_stops import polygon_distance
from .curbside import propose_curb_anchored_candidates
from .unmarked import ParkingParameters


def occupancy_mesh(mesh):
    """Keep actual model triangles and all non-parked locators intact."""
    return {**mesh, 'locators': [r for r in mesh['locators'] if '.parked.' not in r['hookup']]}


def _id(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]


def evaluate_area(candidate, geometry, mesh, *, ground, paint, region_validator=None):
    """Validate a complete broad area with NPC occupancy treated as variable."""
    access=evaluate_access(candidate,geometry,occupancy_mesh(mesh),ground=ground,paint=paint,
                           region_validator=region_validator)
    access['parked_npc_evidence']=[{'index':r['index'],'hookup':r['hookup'],'position':r['position']}
        for r in mesh['locators'] if '.parked.' in r['hookup'] and
        polygon_distance(candidate['polygon_xz'],[_xz([r['position']])[0]])<3.5]
    access['occupancy_policy']='Variable NPC locators are parking evidence; permanent source model triangles remain exclusions'
    return access


def propose_broad_unmarked(mesh,geometry,*,ground,paint,parameters=None,edge_offset=.15,keep_clear=()):
    """Split each evidenced edge into contiguous usable strips.

    A one metre deterministic inspection grid shortens regions around pump,
    navigation, entrance and permanent-model exclusions. It never emits grid
    cells: final perpendicular banks need >=6 m along-edge and parallel strips
    >=12 m. Every final rectangle is rechecked as a whole by the caller.
    """
    parameters=parameters or ParkingParameters()
    inspection_geometry={**geometry,'polygons':[
        *geometry['polygons'],*({'id':'entrance-'+str(row['id']),'color':4,
            'vertices':[[x,0.,z] for x,z in row['polygon_xz']]} for row in keep_clear)]}
    seeds=propose_curb_anchored_candidates(mesh,geometry,ground=ground,paint=paint,
                                          parameters=parameters,edge_offset=edge_offset)
    edges={}
    for seed in seeds:
        e=seed['source_edge_evidence'];key=json.dumps(e['boundary_xyz'],sort_keys=True)
        if key in edges:continue
        a,b=[_xz([p])[0] for p in e['boundary_xyz']]
        tangent=[(b[k]-a[k])/math.dist(a,b) for k in (0,1)]
        center=[sum(p[k] for p in seed['polygon_xz'])/4 for k in (0,1)]
        mid=[(a[k]+b[k])/2 for k in (0,1)]
        normal=[-tangent[1],tangent[0]]
        if sum((center[k]-mid[k])*normal[k] for k in (0,1))<0:normal=[-v for v in normal]
        edges[key]=(a,b,normal,{'curb_anchor_evidence':True,'source_edge_evidence':e},'curb')
    # Only narrow landscape islands are accepted. Broad inaccessible areas or
    # arbitrary asphalt frontages cannot create edge parking on their own.
    gas=[_xz([s['position']])[0] for s in geometry['gas_spawns']]
    for polygon in geometry['polygons']:
        if polygon['color']!=4:continue
        ring=_xz(polygon['vertices'])
        if len(ring)!=4:continue
        lengths=[math.dist(a,b) for a,b in zip(ring,ring[1:]+ring[:1])]
        if not (min(lengths)<=4 and max(lengths)>=12):continue
        signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))
        for index,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
            length=math.dist(a,b)
            if length<12:continue
            tangent=[(b[k]-a[k])/length for k in (0,1)]
            normal=[tangent[1],-tangent[0]] if signed>0 else [-tangent[1],tangent[0]]
            mid=[(a[k]+b[k])/2 for k in (0,1)]
            if not gas or min(math.dist(mid,g) for g in gas)>parameters.max_station_distance:continue
            # Use the facility-facing side, avoiding the road side of islands.
            nearest=min(gas,key=lambda g:math.dist(mid,g))
            if sum((nearest[k]-mid[k])*normal[k] for k in (0,1))<=0:continue
            key=f'island-{polygon["id"]}-{index}'
            edges[key]=(a,b,normal,{'landscape_edge_evidence':{'polygon':polygon['id'],'edge':index,
                'source_vertices':deepcopy(polygon['vertices'])}},'landscape')
    candidates=[];rejections=[];checked=0
    for key,(a,b,normal,evidence,kind) in sorted(edges.items()):
        length=math.dist(a,b);tangent=[(b[k]-a[k])/length for k in (0,1)]
        layouts=[('perpendicular',6.,6.),('parallel',2.6,12.)] if kind=='curb' else [('parallel',2.6,12.)]
        for layout,depth,minimum in layouts:
            setback=max(.55,edge_offset) if kind=='landscape' else max(.55,edge_offset)
            def rectangle(start,end,n0,n1):
                return [[a[k]+t*tangent[k]+n*normal[k] for k in (0,1)]
                        for t,n in [(start,n0),(end,n0),(end,n1),(start,n1)]]
            # Two metre end margins retain entrances beside the island/curb.
            start=2.;stop=length-2.;count=max(0,int(math.floor(stop-start)))
            runs=[];run=None
            for index in range(count):
                left=start+index;right=left+1.
                row={'id':'inspection','polygon_xz':rectangle(left,right,setback,setback+depth),
                     'approach_xz':rectangle(left,right,setback+depth,setback+depth+4.) if layout=='perpendicular' else None,
                     'direction_xz':tangent,
                     'parking_heading_xz':[-v for v in normal] if layout=='perpendicular' else tangent,
                     'rejection_reasons':[]}
                # A full area/approach check includes sampled height and all
                # permanent triangles; the NPC locators are deliberately absent.
                result=evaluate_area(row,inspection_geometry,mesh,ground=ground,paint=paint)
                checked+=1
                if checked>4096:raise ValueError('Broad-area inspection exceeds 4096 bounded edge cells')
                if not result['rejection_reasons']:
                    if run is None:run=left
                else:
                    rejections.append({'edge':key,'layout':layout,'interval_m':[left,right],
                                       'reasons':result['rejection_reasons']})
                    if run is not None:runs.append((run,left));run=None
            if run is not None:runs.append((run,start+count))
            for left,right in runs:
                if right-left<minimum:continue
                polygon=rectangle(left,right,setback,setback+depth)
                row={'layout':layout,'polygon_xz':polygon,
                     'approach_xz':rectangle(left,right,setback+depth,setback+depth+4.) if layout=='perpendicular' else None,
                     'direction_xz':tangent,
                     'parking_heading_xz':[-v for v in normal] if layout=='perpendicular' else tangent,
                     'rejection_reasons':[], 'geometry_scope':'contiguous_source_edge_parking_area',
                     'area_length_m':right-left,'area_depth_m':depth,'partial_activation':True,
                     'evidence':'Observed source edge and deterministic contiguous clearance inspection',
                     'height_status':'source_model_ground_surface_sampled',**deepcopy(evidence)}
                row['id']=_id(row);candidates.append(row)
                if len(candidates)>128:raise ValueError('Broad-area proposal exceeds 128 areas')
    return {'method':'broad_source_edge_areas','candidates':candidates,'rejections':rejections,
            'inspection_cells':checked,'geometry':geometry,
            'limits':'Bounded family source geometry; grid may conservatively miss short irregular regions; no arbitrary single-bay fallback'}


def select_logical_areas(candidates):
    """Keep every disjoint valid logical region; overlap alternatives emit once."""
    result=[]
    # Prefer broad capacity over a narrower alternative on the same edge.
    valid=[c for c in candidates if not c['rejection_reasons']]
    def area(c):
        p=c['polygon_xz'];return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
    for candidate in sorted(valid,key=lambda c:(-area(c),c['id'])):
        if any(polygon_distance(candidate['polygon_xz'],c['polygon_xz'])<.5 for c in result):continue
        result.append(candidate)
    return sorted(result,key=lambda c:c['id'])
