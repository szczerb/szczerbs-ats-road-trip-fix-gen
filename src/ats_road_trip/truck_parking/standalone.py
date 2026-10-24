"""Source-calibrated additive standalone native truck-rest regions.

Trigger activation flags are not PPD flags. New items inherit the original
vehicle/trailer, partial-contact, DLC and visibility contract, and receive
fresh nodes plus the reviewed world-space parking geometry. Original items
and nodes remain byte-identical.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import math
import struct

from ..bulk_fuel import _splice
from ..map_sector import MapNode, extend_layer, parse_sector
from ..rest_stops import _standalone, _standalone_activation
from ..station_parking.trigger import _validate_vertices
from .trigger import _vehicles

_TRIGGER_SOURCE = 'https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Trigger.cs'
_NODE_SOURCE = 'https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Node.cs'
_BOUNDS_SOURCE = 'https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Serialization/MapItemSerializer.cs'


def _projections(vertices):
    return [(x, y, z, (x+z)/2., (x-z)/2.) for x,y,z in vertices]


def _source_padding(bounds, vertices):
    """Require source evidence for the five observed world-space KDOP axes.

    Min/max storage is documented by the primary reader. Axis interpretation
    and padding are an observed-local contract, individually checked against
    every source polygon; unexplained or excessive bounds block this writer.
    """
    projected = _projections(vertices)
    low = [min(p[i] for p in projected) for i in range(5)]
    high = [max(p[i] for p in projected) for i in range(5)]
    lower = [p-b for p,b in zip(low,bounds[:5])]
    upper = [b-p for p,b in zip(high,bounds[5:])]
    if (any(not math.isfinite(v) or v < -0.005 or v > 8. for v in lower+upper)
            or any(abs(a-b) > 0.05 for a,b in zip(lower,upper))):
        raise ValueError('Standalone native KDOP bounds do not match the reviewed five-axis source calibration')
    return [max(0.,v) for v in lower], [max(0.,v) for v in upper]


def _outward_float32(value, *, lower):
    rounded = struct.unpack('<f',struct.pack('<f',value))[0]
    if (lower and rounded > value) or (not lower and rounded < value):
        bits=struct.unpack('<I',struct.pack('<f',rounded))[0]
        bits += (-1 if rounded > 0 else 1) if lower else (1 if rounded >= 0 else -1)
        rounded=struct.unpack('<f',struct.pack('<I',bits))[0]
    if not math.isfinite(rounded):
        raise ValueError('Standalone native KDOP bounds exceed finite float32 capacity')
    return rounded


def _new_bounds(vertices, padding):
    projected=_projections(vertices)
    low=[_outward_float32(min(p[i] for p in projected)-padding[0][i],lower=True) for i in range(5)]
    high=[_outward_float32(max(p[i] for p in projected)+padding[1][i],lower=False) for i in range(5)]
    if any(not lo <= p[i] <= hi for p in projected for i,(lo,hi) in enumerate(zip(low,high))):
        raise ValueError('Standalone native KDOP bounds do not enclose the emitted nodes')
    return low+high


def append_truck_standalone_polygons(
    data: bytes, *, source_uid: int, areas: list[dict],
    action_modes: Mapping[int,set[str]], uid_namespace: str,
    occupied_uids=frozenset(), action_token: int | None = None,
    layer_data: bytes | None = None, external_nodes: Mapping[int,MapNode] | None = None,
) -> tuple[bytes, bytes | None, dict]:
    """Append independently owned native truck polygons to one owning sector.

    ``areas`` contains unique stable ``id`` strings and reviewed world XYZ
    ``vertices``. Coordinates round to the native 1/256-unit grid; emitted
    coordinates are reported. ``occupied_uids`` must include the caller's
    effective world inventory. Collision is fatal, never retried silently.
    External source nodes may be supplied explicitly; new nodes reside with
    the generated items. The caller must also mirror any visibility references
    in other sectors using ``visibility_clone_pairs`` from the report.

    The optional layer source is composed by copying source membership for
    each new item. Local visibility parents/children are composed here.
    Source native parameters only: exactly one resolved truck-rest action,
    no per-instance parameter override, nonoriented vehicle and connected-
    trailer activation, and uniform native node metadata. An effective mixed
    car action requires an explicitly selected validated car-free rest action.
    """
    if type(source_uid) is not int or not 0 < source_uid < 0xffffffffffffffff:
        raise ValueError('Standalone source UID must be a nonreserved uint64')
    if not isinstance(action_modes,Mapping):
        raise ValueError('Standalone action_modes must be an effective action mapping')
    if not isinstance(uid_namespace,str) or not uid_namespace or len(uid_namespace)>512:
        raise ValueError('Standalone UID namespace must be a nonempty bounded string')
    if not isinstance(occupied_uids,(set,frozenset)) or any(type(u) is not int or not 0 < u < 0xffffffffffffffff for u in occupied_uids):
        raise ValueError('Standalone occupied_uids must be a set of nonreserved uint64 identities')
    if not isinstance(areas,list) or not areas:
        raise ValueError('Standalone generation requires one or more reviewed areas')
    before=parse_sector(data)
    sources=[item for item in before.items if item.uid==source_uid and item.kind==0x22]
    if len(sources)!=1:
        raise ValueError('Standalone source native Trigger is absent or ambiguous')
    source=sources[0]
    trigger=_standalone(data,source)
    activation=_standalone_activation(source.flags)
    if activation['init_disabled'] or source.flags & 0x0c != 0x0c:
        raise ValueError('Standalone source must enable normal vehicle and connected-trailer activation')
    if len(trigger['nodes']) < 3 or trigger['radius']:
        raise ValueError('Standalone source must be a native polygon, not a sphere')
    if any(not isinstance(v,(set,frozenset,list,tuple)) or any(not isinstance(name,str) for name in v)
           for v in action_modes.values()):
        raise ValueError('Standalone effective action vehicles must be explicit name collections')
    rest=[r for r in trigger['actions'] if r['action'] in action_modes and 'truck' in action_modes[r['action']]]
    if len(rest)!=1 or rest[0]['custom']:
        raise ValueError('Standalone source needs exactly one native truck-rest action without custom parameters')
    source_action=rest[0]['action']
    source_vehicles=_vehicles(action_modes,source_action,emitted=False)
    action=source_action if action_token is None else action_token
    vehicles=_vehicles(action_modes,action,emitted=True)
    if external_nodes is not None and (not isinstance(external_nodes,Mapping) or any(
            not isinstance(node,MapNode) or uid!=node.uid or len(node.raw)!=56
            for uid,node in external_nodes.items())):
        raise ValueError('Standalone external_nodes must map native node UIDs to exact MapNode records')
    nodes=dict(external_nodes or {})
    for node in before.nodes:
        if node.uid in nodes and nodes[node.uid].raw != node.raw:
            raise ValueError('Standalone source node has conflicting local/external copies')
        nodes[node.uid]=node
    try:
        native_nodes=[nodes[uid] for uid in trigger['nodes']]
    except KeyError as exc:
        raise ValueError('Standalone source node is unresolved across sectors') from exc
    if any(not isinstance(n,MapNode) or source_uid not in (n.forward,n.backward) for n in native_nodes):
        raise ValueError('Standalone source node ownership is not reciprocal')
    # IsRed is bit 0. Country and all other native flags are preserved; reject
    # an unexplained per-vertex difference instead of synthesizing metadata.
    base_flags=native_nodes[0].flags & ~1
    if any(n.flags != base_flags | (1 if index==0 else 0) or n.rotation!=native_nodes[0].rotation
           for index,n in enumerate(native_nodes)):
        raise ValueError('Standalone source node metadata is not a uniform native polygon contract')
    try:
        _validate_vertices([n.position for n in native_nodes])
    except ValueError as exc:
        raise ValueError('Standalone source geometry is unsupported: '+str(exc)) from exc
    source_bounds=struct.unpack_from('<10f',data,source.offset+12)
    padding=_source_padding(source_bounds,[n.position for n in native_nodes])
    prepared=[];area_ids=set()
    for area in areas:
        if not isinstance(area,dict) or set(area)!={'id','vertices'} or not isinstance(area['id'],str) or not area['id'] or len(area['id'])>128 or area['id'] in area_ids:
            raise ValueError('Standalone areas require unique bounded id strings and only vertices')
        area_ids.add(area['id'])
        try:
            requested=_validate_vertices(area['vertices'])
            quantized=[tuple(round(v*256)/256. for v in p) for p in requested]
            vertices=_validate_vertices(quantized)
        except ValueError as exc:
            raise ValueError('Standalone truck geometry is unsupported: '+str(exc)) from exc
        prepared.append((area['id'],requested,vertices))
    used=set(occupied_uids)|{i.uid for i in before.items}|set(nodes)
    generated=[]
    def allocate(seed):
        uid=int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],'little')
        if uid in (0,0xffffffffffffffff) or uid in used:
            raise ValueError('Generated standalone UID collision; refusing ambiguous output')
        used.add(uid);generated.append(uid)
        return uid
    items=[];node_records=[];reports=[];clone_ids=[]
    result_layer=layer_data
    for area_id,requested,vertices in prepared:
        coords=repr(vertices)
        seed=f'{uid_namespace}:{source_uid:x}:truck-rest:{area_id}:{coords}'
        uid=allocate(seed+':item');clone_ids.append(uid)
        new_node_ids=[]
        for index,point in enumerate(vertices):
            node_uid=allocate(seed+f':node:{index}')
            raw=bytearray(native_nodes[0].raw)
            struct.pack_into('<Q3i',raw,0,node_uid,*(round(v*256) for v in point))
            struct.pack_into('<QQI',raw,36,0,uid,base_flags | (1 if index==0 else 0))
            node_records.append(bytes(raw));new_node_ids.append(node_uid)
        bounds=_new_bounds(vertices,padding)
        raw=bytearray(data[source.offset:source.offset+57])
        struct.pack_into('<Q10f',raw,4,uid,*bounds)
        raw+=struct.pack('<I',len(trigger['tags']))+b''.join(struct.pack('<Q',t) for t in trigger['tags'])
        raw+=struct.pack('<I',len(new_node_ids))+b''.join(struct.pack('<Q',n) for n in new_node_ids)
        raw+=struct.pack('<IQI',1,action,0xffffffff)
        items.append(bytes(raw))
        if result_layer is not None:
            result_layer=extend_layer(result_layer,{source_uid:uid})
        reports.append({'id':area_id,'uid':hex(uid),'node_uids':[hex(n) for n in new_node_ids],
                        'requested_vertices_xyz':[list(p) for p in requested],
                        'vertices_xyz':[list(p) for p in vertices], 'bounds':bounds,
                        'flags':source.flags,'action_token':action,'vehicles':sorted(vehicles),
                        'marker_count':1,'new_car_eligibility':False})
    operations=[]
    for item in before.items:
        children=item.details.get('children',())
        if source_uid in children:
            offset=item.details['child_count_offset'];insertion=item.details['child_insert_offset']
            operations.extend([(offset,offset+4,struct.pack('<I',len(children)+len(clone_ids))),
                               (insertion,insertion,b''.join(struct.pack('<Q',u) for u in clone_ids))])
    children=before.visibility_children
    if source_uid in children:
        offset=before.visibility_children_offset
        operations.append((offset,len(data),struct.pack('<I',len(children)+len(clone_ids))
            +data[offset+4:]+b''.join(struct.pack('<Q',u) for u in clone_ids)))
    combined=[n.raw for n in before.nodes]+node_records
    combined.sort(key=lambda raw:struct.unpack_from('<Q',raw)[0])
    operations.extend([(16,20,struct.pack('<I',before.item_count+len(items))),
                       (before.node_count_offset,before.visibility_children_offset,
                        b''.join(items)+struct.pack('<I',len(combined))+b''.join(combined))])
    result=_splice(data,operations)
    after=parse_sector(result)
    after_items={i.uid:i for i in after.items};after_nodes={n.uid:n for n in after.nodes}
    for item in before.items:
        copied=after_items[item.uid]
        if source_uid in item.details.get('children',()):
            expected=item.details['children']+tuple(clone_ids)
            if copied.details.get('children')!=expected:
                raise ValueError('Standalone visibility parent composition differs from the source relation')
            old_count=item.details['child_count_offset'];new_count=copied.details['child_count_offset']
            old_insert=item.details['child_insert_offset'];new_insert=copied.details['child_insert_offset']
            if (data[item.offset:old_count]!=result[copied.offset:new_count]
                    or data[old_count+4:old_insert]!=result[new_count+4:new_insert-8*len(clone_ids)]
                    or data[old_insert:item.end]!=result[new_insert:copied.end]):
                raise ValueError('Standalone writer changed visibility bytes outside added children')
        elif data[item.offset:item.end] != result[copied.offset:copied.end]:
            raise ValueError('Standalone writer changed an original item')
    if any(after_nodes[n.uid].raw!=n.raw for n in before.nodes):
        raise ValueError('Standalone writer changed an original node')
    for report in reports:
        item=after_items[int(report['uid'],16)];parsed=_standalone(result,item)
        if (item.flags!=source.flags or parsed['tags']!=trigger['tags'] or len(parsed['actions'])!=1
                or parsed['actions'][0]['action']!=action or parsed['actions'][0]['custom']
                or [list(after_nodes[u].position) for u in parsed['nodes']]!=report['vertices_xyz']
                or any(after_nodes[u].forward!=item.uid or after_nodes[u].backward for u in parsed['nodes'])):
            raise ValueError('Standalone output native action/geometry/ownership audit failed')
    return result,result_layer,{
        'experimental':True,'source_uid':hex(source_uid),'source_flags':source.flags,
        'map_format':907,'source_sector_sha256':hashlib.sha256(data).hexdigest(),
        'source_trigger_sha256':hashlib.sha256(data[source.offset:source.end]).hexdigest(),
        'source_action_token':source_action,'source_vehicles':sorted(source_vehicles),
        'source_activation':activation,'areas':reports,'added_trigger_count':len(reports),
        'added_node_count':len(node_records),'marker_count':len(reports),
        'marker_count_scope':'Independent native item count; runtime map presentation unverified',
        'occupied_uid_count':len(occupied_uids),
        'generated_uids':[hex(u) for u in generated],
        'visibility_clone_pairs':[{'original_uid':hex(source_uid),'new_uid':hex(u)} for u in clone_ids],
        'local_visibility_composed':True,'layer_composed':layer_data is not None,
        'source_items_and_nodes_preserved':True,'new_car_eligibility':False,
        'source_bounds':list(source_bounds), 'bounds_padding':{'lower':padding[0],'upper':padding[1]},
        'bounds_contract':{'status':'Observed locally','axes':['x','y','z','(x+z)/2','(x-z)/2'],
                           'source_envelope_calibrated':True,'new_bounds_outward_float32':True,
                           'primary_storage_reference':_BOUNDS_SOURCE},
        'activation_contract':{'status':'Documented in primary parser source',
            'source':_TRIGGER_SOURCE,'node_source':_NODE_SOURCE,
            'partial_bit':1,'vehicle_bit':4,'connected_trailer_bit':8,
            'source_flags_preserved_exactly':True,'PPD_flags_not_reused':True},
        'runtime_behavior':'Unknown; no in-game test performed',
    }
