"""Constrained native bank completion retaining its existing marker and action."""
from __future__ import annotations
import hashlib
import math
import struct
from ..bulk_fuel import _splice
from ..map_sector import parse_sector
from ..rest_stops import _standalone, _standalone_activation, _inside, _point_segment
from .geometry import _clip_convex, _signed_area, _convex
from .standalone import _validate_truck_vertices, _source_padding, _new_bounds
from .trigger import _vehicles


def _hull(points):
    values=sorted(set(points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lower=[]
    for p in values:
        while len(lower)>1 and cross(lower[-2],lower[-1],p)<=1e-8:lower.pop()
        lower.append(p)
    upper=[]
    for p in reversed(values):
        while len(upper)>1 and cross(upper[-2],upper[-1],p)<=1e-8:upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]


def plan_bank_extension(source_vertices, bank_vertices):
    """Exact simple union, with only bounded native-grid rounding outside it.

    New heights follow a plane proven against the native functional polygon.
    This is a bounded geometry rule; callers must separately check obstacles.
    """
    source=_validate_truck_vertices(source_vertices,source=True)
    bank=_validate_truck_vertices(bank_vertices)
    a=[(p[0],p[2]) for p in source];b=[(p[0],p[2]) for p in bank]
    if not _convex(b):raise ValueError('Native extension requires a convex painted bank')
    intersection=polygon_intersection_area(a,b)
    if intersection<=1.:raise ValueError('Native extension needs a materially overlapping same bank')
    # Native coordinate rounding is part of the serialized geometry contract.
    b=[(round(x*256)/256.,round(z*256)/256.) for x,z in b]
    hull=_union_boundary(a,b)
    union=abs(_signed_area(a))+abs(_signed_area(b))-intersection
    bridge=abs(_signed_area(hull))-union
    if bridge>max(1.,.0005*union):raise ValueError('Native extension would bridge circulation space outside the parking union')
    p0=source[0];plane=None
    for p1,p2 in zip(source[1:],source[2:]):
        dx1,dz1,dy1=p1[0]-p0[0],p1[2]-p0[2],p1[1]-p0[1]
        dx2,dz2,dy2=p2[0]-p0[0],p2[2]-p0[2],p2[1]-p0[1]
        det=dx1*dz2-dx2*dz1
        if abs(det)>1e-6:
            plane=((dy1*dz2-dy2*dz1)/det,(dx1*dy2-dx2*dy1)/det);break
    if plane is None:raise ValueError('Native source has no horizontal plane')
    gx,gz=plane
    planar=all(abs(p[1]-(p0[1]+gx*(p[0]-p0[0])+gz*(p[2]-p0[2])))<=.05 for p in source)
    def edge_height(x,z,points):
        candidates=[]
        for a,b in zip(points,points[1:]+points[:1]):
            dx,dz=b[0]-a[0],b[2]-a[2];length2=dx*dx+dz*dz
            t=max(0.,min(1.,((x-a[0])*dx+(z-a[2])*dz)/length2))
            distance=math.hypot(x-a[0]-t*dx,z-a[2]-t*dz)
            candidates.append((distance,a[1]+t*(b[1]-a[1])))
        return min(candidates)
    original={(p[0],p[2]):p[1] for p in source}
    vertices=[]
    for x,z in hull:
        if (x,z) in original:y=original[x,z]
        elif planar:y=p0[1]+gx*(x-p0[0])+gz*(z-p0[2])
        else:
            native_distance,native_y=edge_height(x,z,source)
            bank_distance,bank_y=edge_height(x,z,bank)
            y=native_y if native_distance<=.015 or native_distance<bank_distance else bank_y
        vertices.append((x,round(y*256)/256.,z))
    _validate_truck_vertices(vertices,source=True)
    for p,q in zip(vertices,vertices[1:]+vertices[:1]):
        midpoint=((p[0]+q[0])/2.,(p[2]+q[2])/2.)
        if _inside(midpoint,a) or _on_edge(midpoint,a,.015):continue
        if abs(p[1]-q[1])>math.hypot(p[0]-q[0],p[2]-q[2])*.10+1e-9:
            raise ValueError('New bank boundary exceeds the reviewed truck grade policy')
    return vertices,{'native_area':abs(_signed_area(a)),'bank_area':abs(_signed_area(b)),
        'overlap_area':intersection,'extended_area':abs(_signed_area(hull)),
        'off_union_bridge_area':max(0.,bridge),'source_plane_gradient':[gx,gz] if planar else None,
        'height_policy':'native plane' if planar else 'native boundary interpolation plus authored bank heights'}


def extend_truck_standalone_polygon(data, *, source_uid, vertices, action_modes,
                                    uid_namespace, occupied_uids=frozenset(), external_nodes=None):
    before=parse_sector(data);source=next((i for i in before.items if i.uid==source_uid and i.kind==0x22),None)
    if source is None:raise ValueError('Native extension source is absent')
    trigger=_standalone(data,source);activation=_standalone_activation(source.flags)
    if activation['init_disabled'] or not activation['vehicle_activation'] or source.flags&0xc!=0xc:
        raise ValueError('Native extension requires ordinary vehicle and connected-trailer activation')
    if len(trigger['actions'])!=1 or trigger['actions'][0]['custom'] or trigger['radius']:
        raise ValueError('Native extension requires one unmodified polygon rest action')
    action=trigger['actions'][0]['action'];vehicles=_vehicles(action_modes,action,emitted=True)
    nodes=dict(external_nodes or {});nodes.update({n.uid:n for n in before.nodes})
    if any(u not in nodes for u in trigger['nodes']):raise ValueError('Native extension source nodes unresolved')
    originals=[nodes[u] for u in trigger['nodes']]
    if any(n.forward!=source_uid or n.backward for n in originals):raise ValueError('Native source node ownership is not exclusive')
    local={n.uid for n in before.nodes}
    if not set(trigger['nodes'])<=local:raise ValueError('Native extension requires local source nodes')
    old_vertices=[n.position for n in originals];_validate_truck_vertices(old_vertices,source=True)
    requested=_validate_truck_vertices(vertices,source=True)
    quantized=[tuple(round(v*256)/256. for v in p) for p in requested]
    _validate_truck_vertices(quantized,source=True)
    old_xz=[(p[0],p[2]) for p in old_vertices];new_xz=[(p[0],p[2]) for p in quantized]
    low_y=min(p[1] for p in old_vertices);high_y=max(p[1] for p in old_vertices)
    for point in quantized:
        distance=0. if _inside((point[0],point[2]),old_xz) else min(
            _point_segment((point[0],point[2]),a,b) for a,b in zip(old_xz,old_xz[1:]+old_xz[:1]))
        if not low_y-distance*.10-.05<=point[1]<=high_y+distance*.10+.05:
            raise ValueError('Native extension height is not bounded by the source terrain envelope')
    for p,q in zip(quantized,quantized[1:]+quantized[:1]):
        midpoint=((p[0]+q[0])/2.,(p[2]+q[2])/2.)
        if _inside(midpoint,old_xz) or _on_edge(midpoint,old_xz,.015):continue
        if abs(p[1]-q[1])>math.hypot(p[0]-q[0],p[2]-q[2])*.10+1e-9:
            raise ValueError('Native extension new edge exceeds the truck grade guard')
    if not polygon_retains_native(old_xz,new_xz):
        raise ValueError('Native extension must retain every original covered point')
    if len(quantized)<len(originals):raise ValueError('Native extension may not orphan original node identities')
    base_flags=originals[0].flags&~1
    if any(n.flags!=(base_flags|(1 if i==0 else 0)) for i,n in enumerate(originals)):
        raise ValueError('Native source country/node metadata are inconsistent')
    padding=_source_padding(struct.unpack_from('<10f',data,source.offset+12),old_vertices)
    used=set(occupied_uids)|local|{i.uid for i in before.items};ids=list(trigger['nodes']);added=[]
    for index in range(len(ids),len(quantized)):
        seed=f'{uid_namespace}:{source_uid:x}:extension:{repr(quantized)}:node:{index}'
        uid=int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],'little')
        if uid in used or uid in (0,0xffffffffffffffff):raise ValueError('Native extension node UID collision')
        used.add(uid);ids.append(uid);added.append(uid)
    records={n.uid:n.raw for n in before.nodes};changes=[]
    for index,(uid,point) in enumerate(zip(ids,quantized)):
        template=originals[index%len(originals)];raw=bytearray(template.raw)
        struct.pack_into('<Q3i',raw,0,uid,*(round(v*256) for v in point))
        struct.pack_into('<QQI',raw,36,0,source_uid,base_flags|(1 if index==0 else 0))
        records[uid]=bytes(raw)
        changes.append({'uid':hex(uid),'before_xyz':list(nodes[uid].position) if uid in nodes else None,'after_xyz':list(point)})
    bounds=_new_bounds(quantized,padding)
    old_bounds=struct.unpack_from('<10f',data,source.offset+12)
    bounds[1]=min(bounds[1],old_bounds[1]);bounds[6]=max(bounds[6],old_bounds[6])
    raw=bytearray(data[source.offset:source.offset+57]);struct.pack_into('<10f',raw,12,*bounds)
    raw+=struct.pack('<I',len(trigger['tags']))+b''.join(struct.pack('<Q',u) for u in trigger['tags'])
    raw+=struct.pack('<I',len(ids))+b''.join(struct.pack('<Q',u) for u in ids)
    # Actions are copied exactly, including their parameter sentinel.
    action_offset=source.offset+57+4+8*len(trigger['tags'])+4+8*len(trigger['nodes'])
    raw+=data[action_offset:source.end]
    node_bytes=b''.join(records[u] for u in sorted(records))
    result=_splice(data,[(source.offset,source.end,bytes(raw)),
        (before.node_count_offset,before.visibility_children_offset,struct.pack('<I',len(records))+node_bytes)])
    after=parse_sector(result);out_items={i.uid:i for i in after.items};out_nodes={n.uid:n for n in after.nodes}
    for item in before.items:
        if item.uid!=source_uid:
            other=out_items[item.uid]
            if data[item.offset:item.end]!=result[other.offset:other.end]:raise ValueError('Native extension changed another item')
    for node in before.nodes:
        if node.uid not in trigger['nodes'] and out_nodes[node.uid].raw!=node.raw:
            raise ValueError('Native extension changed an unrelated node')
    return result,{'kind':'native_extension','source_uid':hex(source_uid),'uid':hex(source_uid),
        'source_flags':source.flags,'flags':source.flags,'action_token':action,'vehicles':sorted(vehicles),
        'before_vertices_xyz':[list(p) for p in old_vertices],'vertices_xyz':[list(p) for p in quantized],
        'node_changes':changes,'generated_uids':[hex(u) for u in added],
        'native_source_area_retained':True,'native_vertical_bounds_retained':True,'source_action_parameters_preserved':True,
        'unrelated_items_and_nodes_preserved':True,'marker_count':1,'added_marker_count':0,
        'new_car_eligibility':False,'runtime_behavior':'Unknown; no in-game test performed'}


def _on_edge(point, polygon, tolerance=1e-7):
    return min(_point_segment(point,a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1]))<=tolerance


def _strict_inside(point,polygon):
    return _inside(point,polygon) and not _on_edge(point,polygon)


def _edge_splits(a,b,polygon):
    dx,dz=b[0]-a[0],b[1]-a[1];length2=dx*dx+dz*dz;values=[0.,1.]
    for c,d in zip(polygon,polygon[1:]+polygon[:1]):
        ex,ez=d[0]-c[0],d[1]-c[1];den=dx*ez-dz*ex
        if abs(den)>1e-10:
            t=((c[0]-a[0])*ez-(c[1]-a[1])*ex)/den
            u=((c[0]-a[0])*dz-(c[1]-a[1])*dx)/den
            if -1e-8<=t<=1+1e-8 and -1e-8<=u<=1+1e-8:values.append(min(1.,max(0.,t)))
        elif abs((c[0]-a[0])*dz-(c[1]-a[1])*dx)<1e-7:
            for p in (c,d):
                t=((p[0]-a[0])*dx+(p[1]-a[1])*dz)/length2
                if 0<=t<=1:values.append(t)
    return sorted(set(round(t,12) for t in values))


def polygon_retains_native(native,expanded):
    """Check source boundary intervals as well as vertices for a simple union."""
    def covered(p):return _inside(p,expanded) or _on_edge(p,expanded,1e-6)
    if not all(covered(p) for p in native):return False
    for a,b in zip(native,native[1:]+native[:1]):
        values=_edge_splits(a,b,expanded)
        for lo,hi in zip(values,values[1:]):
            t=(lo+hi)/2
            if not covered((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]))):return False
    return covered((sum(p[0] for p in native)/len(native),sum(p[1] for p in native)/len(native)))


def _union_boundary(a,b):
    a=list(a if _signed_area(a)>0 else reversed(a));b=list(b if _signed_area(b)>0 else reversed(b))
    edges={}
    def key(p):return (round(p[0],7),round(p[1],7))
    for own,other in ((a,b),(b,a)):
        for p,q in zip(own,own[1:]+own[:1]):
            values=_edge_splits(p,q,other)
            for lo,hi in zip(values,values[1:]):
                if hi-lo<1e-9:continue
                middle=(lo+hi)/2;mid=(p[0]+middle*(q[0]-p[0]),p[1]+middle*(q[1]-p[1]))
                if _strict_inside(mid,other):continue
                start=key((p[0]+lo*(q[0]-p[0]),p[1]+lo*(q[1]-p[1])))
                end=key((p[0]+hi*(q[0]-p[0]),p[1]+hi*(q[1]-p[1])))
                if start!=end:edges[(start,end)]=None
    # Identical boundaries share directed edges; opposed shared interior edges
    # disappear. The overlapping convex input union must have one exterior loop.
    for p,q in list(edges):
        if (q,p) in edges:edges.pop((p,q),None);edges.pop((q,p),None)
    canonical=[]
    def merged(point):
        for candidate in canonical:
            if math.dist(candidate,point)<1e-5:return candidate
        canonical.append(point);return point
    edges={(merged(p),merged(q)):None for p,q in edges if math.dist(p,q)>1e-5}
    outgoing={}
    for p,q in edges:
        if p in outgoing and outgoing[p]!=q:raise ValueError('Native union has an ambiguous boundary')
        outgoing[p]=q
    if not outgoing:raise ValueError('Native union has no boundary')
    start=min(outgoing);loop=[];p=start
    while p not in loop:
        loop.append(p)
        if p not in outgoing:raise ValueError('Native union boundary is disconnected')
        p=outgoing[p]
    if p!=start or len(loop)!=len(edges):raise ValueError('Native union has disconnected components')
    # Snap only intersection vertices outward from both source polygons. This
    # preserves every original native point on the game's 1/256 coordinate grid.
    result=[]
    originals=set(a+b)
    for p in loop:
        if any(math.dist(p,q)<1e-6 for q in originals):
            q=min(originals,key=lambda v:math.dist(p,v));result.append(q);continue
        ix,iz=round(p[0]*256),round(p[1]*256);candidates=[]
        for dx in range(-2,3):
            for dz in range(-2,3):
                q=((ix+dx)/256.,(iz+dz)/256.)
                if not _strict_inside(q,a) and not _strict_inside(q,b):candidates.append(q)
        if not candidates:raise ValueError('Native union intersection cannot preserve the source grid envelope')
        result.append(min(candidates,key=lambda q:math.dist(p,q)))
    return result


def _triangles(poly):
    vertices=list(poly if _signed_area(poly)>0 else reversed(poly));result=[]
    while len(vertices)>3:
        found=False
        for i,b in enumerate(vertices):
            a,c=vertices[i-1],vertices[(i+1)%len(vertices)]
            cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
            if abs(cross)<1e-8:
                vertices.pop(i);found=True;break
            if cross<0:continue
            triangle=[a,b,c]
            if any(_strict_inside(p,triangle) for j,p in enumerate(vertices) if j not in ((i-1)%len(vertices),i,(i+1)%len(vertices))):continue
            result.append(triangle);vertices.pop(i);found=True;break
        if not found:raise ValueError('Native parking union cannot be triangulated safely')
    if len(vertices)==3 and abs(_signed_area(vertices))>1e-8:result.append(vertices)
    return result


def polygon_intersection_area(a,b):
    """Area of two simple polygons through disjoint convex triangle pieces."""
    aa=[a] if _convex(a) else _triangles(a);bb=[b] if _convex(b) else _triangles(b)
    return sum(abs(_signed_area(clipped)) for x in aa for y in bb
        if len(clipped:=_clip_convex(x,y))>=3)
