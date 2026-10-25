"""Conservative source-model clearance for added parking footprints.

Original map KDOP envelopes are spatial proxies, not complete engine collision
meshes. Parked traffic and ground markings corroborate use; they are not walls.
"""
from __future__ import annotations
import math
import re
import struct
from ..local_fuel import token
from ..map_sector import parse_sector
from ..sii import _LEXEMES, _expand_includes, parse_units
from .geometry import _clip_convex, _signed_area


def model_definitions(stack):
    cache=getattr(stack,'_truck_static_models',None)
    if cache is not None:return cache
    if not any(re.fullmatch(r'def/world/model(?:\.[^/]+)?\.sii',p) for p in stack.resources):return {}
    stack.prefetch(r'def/world/model.*\.(?:sii|sui)')
    rows={}
    for path in stack.matching(r'def/world/model(?:\.[^/]+)?\.sii'):
        text=_expand_includes(stack.text(path),path,stack.text,())
        text=_LEXEMES.sub(lambda m:m[0].replace(chr(9),chr(92)+'t') if m[0].startswith(chr(34)) else m[0],text)
        for unit in parse_units(text,source=path):
            if unit.kind!='model_def':continue
            try:key=token(unit.name.removeprefix('model.'))
            except ValueError:continue
            model=unit.one('model_desc','') or ''
            if key in rows and rows[key]!=model:raise ValueError('Ambiguous original static model definition')
            rows[key]=model
    stack._truck_static_models=rows
    return rows


def _clip_halfplane(poly,a,b,c):
    if not poly:return []
    result=[];p=poly[-1];sp=a*p[0]+b*p[1]-c
    for q in poly:
        sq=a*q[0]+b*q[1]-c
        if (sp<=1e-7)!=(sq<=1e-7):
            t=sp/(sp-sq);result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
        if sq<=1e-7:result.append(q)
        p=q;sp=sq
    return result


def _footprint(bounds):
    x,y,z,d,e,X,Y,Z,D,E=bounds
    poly=[(x,z),(X,z),(X,Z),(x,Z)]
    for a,b,c in ((.5,.5,D),(-.5,-.5,-d),(.5,-.5,E),(-.5,.5,-e)):
        poly=_clip_halfplane(poly,a,b,c)
    return poly


def _area(poly):return abs(_signed_area(poly)) if len(poly)>=3 else 0.


def _intersection(a,b):
    if len(a)<3 or len(b)<3:return 0.
    from .extensions import polygon_intersection_area
    return polygon_intersection_area(a,b)


def _scope(stack,path):
    match=re.fullmatch(r'(map/[^/]+/sec)([+-]\d{4})([+-]\d{4})\.(?:base|aux)',path)
    if match is None:raise ValueError('Truck clearance needs a standard source-sector neighborhood')
    prefix,sx,sz=match.groups()
    return [f'{prefix}{int(sx)+dx:+05d}{int(sz)+dz:+05d}.{suffix}'
        for dx in (-1,0,1) for dz in (-1,0,1) for suffix in ('base','aux')
        if f'{prefix}{int(sx)+dx:+05d}{int(sz)+dz:+05d}.{suffix}' in stack.resources]


def nearby_models(stack,sector,vertices):
    definitions=model_definitions(stack);rows=[]
    cache=getattr(stack,'_truck_model_sectors',None)
    if cache is None:cache={};stack._truck_model_sectors=cache
    poly=[(p[0],p[2]) for p in vertices]
    low=min(p[1] for p in vertices)-.3;high=max(p[1] for p in vertices)+4.5
    for path in _scope(stack,sector):
        if path not in cache:
            data=stack.read(path,max_bytes=128*1024*1024);parsed=parse_sector(data);records=[]
            def walk(items):
                for item in items:
                    if item.kind==5:
                        bounds=struct.unpack_from('<10f',data,item.offset+12)
                        if not all(math.isfinite(v) for v in bounds) or any(bounds[i]>bounds[i+5] for i in range(5)):
                            raise ValueError('Nonfinite/inverted static-model bounds in truck scope')
                        key=struct.unpack_from('<Q',data,item.offset+57)[0]
                        name=definitions.get(key,'');lower=name.lower()
                        occupancy=any(s in lower for s in ('parked_truck','parked_car','parked_vehicle','/traffic/'))
                        marking=any(s in lower for s in ('stencil','parking_line','road_mark','/decals/','road_patch','crack'))
                        records.append({'uid':hex(item.uid),'sector':path,'model_token':hex(key),
                            'model_path':name,'polygon_xz':_footprint(bounds),
                            'bounds_xyz':[bounds[i] for i in (0,1,2,5,6,7)],
                            'class':'occupancy' if occupancy else ('ground_marking' if marking else ('static_model' if name else 'unknown_model'))})
                    if item.kind==0x28:walk(item.details['items'])
            walk(parsed.items);cache[path]=records
        for record in cache[path]:
            b=record['bounds_xyz']
            if b[4]<low or b[1]>high:continue
            if (b[3]<min(p[0] for p in vertices) or b[0]>max(p[0] for p in vertices)
                    or b[5]<min(p[2] for p in vertices) or b[2]>max(p[2] for p in vertices)):continue
            if _intersection(poly,record['polygon_xz'])<=.005:continue
            row=dict(record)
            if b[4]-b[1]<=.25 and b[4]<=max(p[1] for p in vertices)+.2:row['class']='ground_marking'
            rows.append(row)
    return rows


def clear_bank(stack,bank, *, original_vertices=None):
    """Check newly activated space; optionally trim a small curbside fringe.

    A small curbside prop can narrow an additive rectangular bank by at most
    1.5m. Interior obstructions and unclassified models block this region. An
    extension never ignores an obstruction simply because the old bank works.
    """
    vertices=[tuple(p) for p in bank['vertices']]
    rows=nearby_models(stack,bank['sector'],vertices)
    adjustments=[]
    if original_vertices is None and len(vertices)==4:
        a,b,c,d=vertices;length=math.hypot(b[0]-a[0],b[2]-a[2]);depth=math.hypot(d[0]-a[0],d[2]-a[2])
        ux,uz=(b[0]-a[0])/length,(b[2]-a[2])/length;vx,vz=(d[0]-a[0])/depth,(d[2]-a[2])/depth
        inset=0.
        for row in rows:
            if row['class'] not in ('static_model','unknown_model'):continue
            values=[(p[0]-a[0])*vx+(p[1]-a[2])*vz for p in row['polygon_xz']]
            if min(values)<.05 and max(values)<=1.:
                inset=max(inset,max(values)+.5)
        if inset and inset<=1.5 and depth-inset>=20.:
            vertices=[(a[0]+vx*inset,a[1],a[2]+vz*inset),(b[0]+vx*inset,b[1],b[2]+vz*inset),c,d]
            adjustments.append({'kind':'curbside_prop_inset','meters':inset,'remaining_depth':depth-inset})
    footprint=[(p[0],p[2]) for p in vertices]
    old=[(p[0],p[2]) for p in original_vertices] if original_vertices else []
    blockers=[]
    for row in rows:
        if row['class'] in ('occupancy','ground_marking'):continue
        area=_intersection(footprint,row['polygon_xz'])
        if old:
            # Only the portion of the object inside the newly activated union
            # is relevant; old native behavior remains preserved.
            area-= _intersection(old,row['polygon_xz'])
        if area>.005:blockers.append({**row,'newly_activated_overlap_area':area})
    return vertices,{'state':'blocked' if blockers else 'clear_by_source_model_proxies',
        'models':rows,'blockers':blockers,'adjustments':adjustments,
        'scope':'original effective 3x3 base/aux neighborhood; static map-model KDOP proxies',
        'limits':'Not a complete collision mesh/terrain access proof; runtime access unverified.'}
