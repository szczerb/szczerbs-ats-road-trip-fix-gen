"""Experimental, placement-local rest eligibility with an immutable proximity index.

Distances are minimum XZ polygon separation in game-world units, inclusive at
``radius``. They do not describe driving distance or physical access. Original
truck/bus eligibility remains intact; polygon geometry and topology stay unchanged. Unsupported
source coverage blocks publication; static validation cannot establish fatigue recovery.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import math
import re
import struct

from .archive import Archive
from .bulk_fuel import _alias_definition, _sha, _splice, prefab_definitions
from .fuel_matching import _control_positions, _node
from .local_fuel import token
from .map_sector import _Reader, parse_sector
from .ppd import inspect_ppd
from .sii import parse_units, _expand_includes, _HEADER, _mask_strings

_CAR = token('parking_car')
_TRUCK = token('hud_parking')


class _Overlay:
    """Read processor output while retaining original sector ownership."""
    def __init__(self, stack, overrides):
        self.base, self.overrides = stack, overrides
        self.packages = stack.packages
        self.resources = dict(stack.resources)
        # Definition discovery only needs membership; sector ownership always
        # comes from the original stack, never this synthetic owner.
        for path in overrides:
            self.resources.setdefault(path, (None, None))

    def read(self, path, *, max_bytes=8*1024*1024):
        if path not in self.overrides:
            return self.base.read(path, max_bytes=max_bytes)
        data = self.overrides[path]
        if len(data) > max_bytes:
            raise ValueError(f'{path}: exceeds read limit')
        return data

    def text(self, path):
        return self.read(path).decode('utf-8-sig')

    def matching(self, pattern):
        return sorted(p for p in self.resources if re.fullmatch(pattern, p))

    def prefetch(self, pattern):
        self.base.prefetch(pattern)


def inspect_rest_triggers(data: bytes, *, actions=None) -> list[dict]:
    """Validate v25 trigger topology; return complete connected rest polygons.

    Group IDs may be reused by different actions, but disconnected components,
    dangling neighbors and branching cycles are refused instead of guessed.
    """
    info = inspect_ppd(data)
    actions = {_CAR, _TRUCK} if actions is None else actions
    h = struct.unpack_from('<24I', data)
    if not h[9]:
        if h[21] != h[22]:
            raise ValueError('PPD zero trigger count disagrees with section extent')
        return []
    if info['version'] != 25 or h[21] + 48*h[9] != h[22]:
        raise ValueError('Rest trigger analysis requires exact PPD v25 records')
    records = []
    for i in range(h[9]):
        values = struct.unpack_from('<IQfffI3f2i', data, h[21] + 48*i)
        if not all(math.isfinite(v) for v in (*values[2:5], *values[6:9])):
            raise ValueError('Nonfinite PPD trigger data')
        records.append({'index': i, 'id': values[0], 'action': values[1],
                        'range': values[2], 'flags': values[5],
                        'position': values[6:9], 'neighbors': values[9:11]})
    groups = defaultdict(list)
    for record in records:
        groups[(record['id'], record['action'])].append(record)
    result = []
    for (group_id, action), group in groups.items():
        if action not in actions:
            continue
        if any(r['flags'] != 0 for r in group):
            raise ValueError('Unsupported rest trigger flags')
        indexes = {r['index'] for r in group}
        if len(group) < 3:
            raise ValueError('Rest trigger is not a supported polygon')
        for record in group:
            neighbors = record['neighbors']
            if len(set(neighbors)) != 2 or any(n not in indexes for n in neighbors):
                raise ValueError('Rest polygon has invalid neighbors')
            if any(record['index'] not in records[n]['neighbors'] for n in neighbors):
                raise ValueError('Rest polygon neighbors are not reciprocal')
        order, previous, current = [], None, min(indexes)
        while current not in order:
            order.append(current)
            choices = [n for n in records[current]['neighbors'] if n != previous]
            previous, current = current, choices[0]
        if current != order[0] or len(order) != len(group):
            raise ValueError('Rest trigger group is disconnected')
        vertices = [records[i]['position'] for i in order]
        _validate_polygon([(p[0], p[2]) for p in vertices])
        result.append({'id': group_id, 'action': action, 'indices': order,
                       'vertices': vertices})
    return result


def retarget_rest_polygons(data: bytes, group_ids: set[int], action: int, *, actions=None) -> tuple[bytes, dict]:
    """Retarget selected truck polygons to a private truck/bus/car action.

    Only each selected vertex's eight action-token bytes change. Geometry,
    indices, flags, ranges and all other sections are preserved exactly.
    """
    groups = inspect_rest_triggers(data, actions=actions)
    selected = [g for g in groups if g['action'] == _TRUCK and g['id'] in group_ids]
    if {g['id'] for g in selected} != group_ids:
        raise ValueError('Selected truck rest groups are absent or ambiguous')
    h = struct.unpack_from('<24I',data)
    result = bytearray(data)
    changed_offsets = set()
    for group in selected:
        for index in group['indices']:
            offset = h[21]+48*index+4
            struct.pack_into('<Q',result,offset,action)
            changed_offsets.update(range(offset,offset+8))
    if any(a != b and i not in changed_offsets for i,(a,b) in enumerate(zip(data,result))):
        raise ValueError('Unexpected PPD rest mutation')
    inspect_rest_triggers(bytes(result),actions=set(actions or {_CAR,_TRUCK}) | {action})
    return bytes(result), {'groups_retargeted':sorted(group_ids),
                           'original_geometry_topology_and_other_sections_preserved':True}


def _validate_polygon(points):
    if len(points) < 3 or len(set(points)) != len(points):
        raise ValueError('Rest polygon is degenerate')
    area = sum(a[0]*b[1] - b[0]*a[1] for a,b in zip(points, points[1:] + points[:1]))
    if abs(area) < 1e-6:
        raise ValueError('Rest polygon has no horizontal area')
    edges = list(zip(points, points[1:] + points[:1]))
    for i, (a,b) in enumerate(edges):
        for j, (c,d) in enumerate(edges):
            if j > i+1 and (i,j) != (0,len(edges)-1) and _segments_intersect(a,b,c,d):
                raise ValueError('Rest polygon self-intersects')


def _segments_intersect(a,b,c,d):
    def cross(p,q,r):
        return (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
    def on(p,q,r):
        return (min(p[0],q[0])-1e-9 <= r[0] <= max(p[0],q[0])+1e-9
                and min(p[1],q[1])-1e-9 <= r[1] <= max(p[1],q[1])+1e-9)
    x,y,z,w = cross(a,b,c), cross(a,b,d), cross(c,d,a), cross(c,d,b)
    return ((x*y < 0 and z*w < 0) or (abs(x)<1e-9 and on(a,b,c))
            or (abs(y)<1e-9 and on(a,b,d)) or (abs(z)<1e-9 and on(c,d,a))
            or (abs(w)<1e-9 and on(c,d,b)))


def _inside(point, polygon):
    inside = False
    for a,b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > point[1]) != (b[1] > point[1]):
            x = a[0] + (point[1]-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if point[0] < x:
                inside = not inside
    return inside


def _point_segment(p,a,b):
    dx,dz = b[0]-a[0], b[1]-a[1]
    t = max(0., min(1., ((p[0]-a[0])*dx + (p[1]-a[1])*dz)/(dx*dx+dz*dz))) if dx or dz else 0.
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dz)


def polygon_distance(a, b):
    """Minimum separation of closed simple polygons (or single points), in XZ."""
    if (len(a) > 1 and _inside(b[0], a)) or (len(b) > 1 and _inside(a[0], b)):
        return 0.
    ae,be = list(zip(a,a[1:]+a[:1])), list(zip(b,b[1:]+b[:1]))
    if any(_segments_intersect(p,q,r,s) for p,q in ae for r,s in be):
        return 0.
    return min([_point_segment(p,r,s) for p in a for r,s in be]
               + [_point_segment(r,p,q) for r in b for p,q in ae])


def _placed_vertices(ppd, prefab, nodes, vertices):
    """Checked control-node horizontal transform; <2 controls fail closed."""
    control = _control_positions(ppd)
    refs,origin = prefab.details['nodes'],prefab.details['origin']
    if len(refs) != len(control) or not 0 <= origin < len(control):
        raise ValueError('Prefab control references/origin disagree with descriptor')
    local = [control[(origin+i)%len(control)] for i in range(len(control))]
    world = [_node(nodes, uid, prefab.uid, either_direction=True).position for uid in refs]
    lx,lz = local[1][0]-local[0][0],local[1][2]-local[0][2]
    wx,wz = world[1][0]-world[0][0],world[1][2]-world[0][2]
    length2 = lx*lx+lz*lz
    if length2 < 1e-6:
        raise ValueError('Coincident PPD control nodes cannot determine rest placement')
    cosine,sine = (lx*wx+lz*wz)/length2,(lz*wx-lx*wz)/length2
    if abs(math.hypot(cosine,sine)-1) > 0.01:
        raise ValueError('Rest prefab control nodes do not define a unit rotation')
    def place(p):
        dx,dz = p[0]-local[0][0],p[2]-local[0][2]
        return world[0][0]+cosine*dx+sine*dz,world[0][2]-sine*dx+cosine*dz
    if any(math.dist(place(p),(q[0],q[2])) > .05 for p,q in zip(local,world)):
        raise ValueError('Rest prefab control nodes fail horizontal placement check')
    return [place(p) for p in vertices]


def _standalone(data, item):
    r = _Reader(data)
    r.pos = item.offset+57
    tags,nodes = r.refs(),r.refs()
    count_offset = r.pos
    actions = []
    for _ in range(r.count(12)):
        start = r.pos
        action = r.read('Q')
        params = r.read('I')
        if params != 0xffffffff:
            r.skip(params*4)
            for _ in range(r.count(8)):
                r.string()
            r.array(8)
            r.skip(8)
        actions.append({'action':action,'offset':start,'custom':params != 0xffffffff,
                        'raw':data[start:r.pos]})
    insertion = r.pos
    radius = r.read('f') if len(nodes)==1 else 0.
    if r.pos != item.end or not nodes or not math.isfinite(radius) or radius < 0:
        raise ValueError('Invalid standalone trigger geometry/extent')
    return {'tags':tags,'nodes':nodes,'actions':actions,'count_offset':count_offset,
            'insertion':insertion,'radius':radius}


def _standalone_activation(flags):
    """Read only Trigger.cs documented bits; preserve the full original word.

    Source: TruckLib/ScsMap/Trigger.cs, inspected 2026-10-18. Bits 0..5 are
    activation modes, byte 1 the DLC guard, bits 16..18 disabled/view/secret.
    DLC availability follows the user's all-DLC ownership assumption; no guard
    is removed or activated by this processor.
    """
    known_mask = 0x0007ff3f
    if flags & ~known_mask:
        raise ValueError(f'Standalone rest trigger has unknown flag bits: {flags & ~known_mask:#x}')
    if flags & 0x2:
        raise ValueError('Oriented standalone rest activation is unsupported')
    if flags & 0x20:
        raise ValueError('Collision-only standalone rest activation is unsupported')
    return {'dlc_guard':(flags >> 8) & 0xff,'partial_activation':bool(flags & 1),
            'vehicle_activation':bool(flags & 4),'init_disabled':bool(flags & 0x10000),
            'flags':hex(flags)}


def _hud_numbers(unit):
    """Normalize supported SII decimal floats without silently hiding HUD IDs.

    Unsupported expressions/encodings and nonfinite values block coverage. A
    definition with rest ID 3 and additional parameters also needs review before
    its vehicle list can be interpreted as a rest eligibility preset.
    """
    numbers = []
    for raw in unit.values('num_params'):
        if not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?',raw):
            raise ValueError(f'Unsupported HUD numeric parameter in {unit.name}: {raw!r}')
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError(f'Nonfinite HUD numeric parameter in {unit.name}')
        numbers.append(value)
    if numbers and numbers[0] == 3 and len(numbers) != 1:
        raise ValueError(f'Unsupported rest HUD numeric parameter list in {unit.name}')
    return tuple(numbers)


def _validate_actions(stack):
    units, blocks = {}, {}
    stack.prefetch(r'def/world/trigger_action.*\.(?:sii|sui)')
    for path in stack.matching(r'def/world/trigger_action(?:\.[^/]+)?\.sii'):
        expanded = _expand_includes(stack.text(path),path,stack.text,())
        masked = _mask_strings(expanded)
        source_blocks = {}
        for match in _HEADER.finditer(masked):
            end,depth = match.end(),1
            while end < len(masked) and depth:
                depth += (masked[end]=='{') - (masked[end]=='}')
                end += 1
            source_blocks[match[2]] = expanded[match.start():end]
        for unit in parse_units(expanded, source=path):
            if unit.kind == 'trigger_action':
                if unit.name in units:
                    raise ValueError('Duplicate effective trigger action: '+unit.name)
                units[unit.name] = unit
                blocks[unit.name] = source_blocks[unit.name]
    hud_numbers = {name:_hud_numbers(unit) for name,unit in units.items()
                   if unit.one('command') == 'hud_activate'}
    for name,vehicles in [('hud_parking',('truck','bus')),('parking_car',('car',))]:
        unit = units.get('trig_action.'+name)
        if (unit is None or unit.one('command') != 'hud_activate'
                or hud_numbers.get(unit.name) != (3.,) or set(unit.values('str_params')) not in (set(vehicles),set(vehicles)|{'car'})):
            raise ValueError('Effective rest action differs from reviewed definition: '+name)
    # Custom aliases with the same command can supply additional rest sites.
    modes = {}
    for name,unit in units.items():
        if hud_numbers.get(name) == (3.,):
            vehicles = set(unit.values('str_params'))
            modes[token(name.removeprefix('trig_action.').lower())] = vehicles
    return (modes,blocks['trig_action.hud_parking'],
            {token(n.removeprefix('trig_action.').lower()) for n in units},
            {token(n.removeprefix('trig_action.').lower()) for n,u in units.items() if u.one('command')=='hud_activate'})


def plan_rest_stops(stack, *, map_packages: set[str], radius=1000., map_name='rest',
                    resource_overrides: dict[str,bytes] | None = None):
    """Plan local car rest additions; never publish when coverage has blockers.

    Inspect source-owned sectors and an approximate neighboring-sector halo.
    Existing car rests beyond this bound may be missed; the user accepts those
    boundary additions. Added car groups never enter the proximity index. ``resource_overrides`` is
    earlier processor output; its sector/resource bytes are composed in place.
    """
    if isinstance(radius,bool) or not isinstance(radius,(int,float)) or not math.isfinite(radius) or radius < 0:
        raise ValueError('Rest radius must be finite and nonnegative')
    overrides = resource_overrides or {}
    effective = _Overlay(stack, overrides)
    report = {'schema_version':1,'analysis':'localized_missing_car_rest','map_name':map_name,
              'radius':radius,'distance_metric':'minimum Euclidean XZ polygon separation in game-world units',
              'inclusive_radius':True,'package_order':[str(p.path) for p in stack.packages],
              'coverage':{'blockers':[],'truck_polygons':0,'existing_car_locations':0,
                          'already_supported':0,'added_car_polygons':0,'placements_changed':0},
              'locations':[],'changed_sectors':[],'source_resources':[],
              'composed_resource_paths':[],
              'scope':{'mode':'source_sectors_with_approximate_halo','omissions':[],
                       'boundary_over_additions_accepted':True,'nominal_sector_width':4000.,
                       'halo_steps':max(1,math.ceil(radius/4000.)),
                       'dlc_guard_assumption':'User owns all DLC; original guards remain unchanged'},
              'excluded_rest_locations':[],
              'limitations':['Experimental: car fatigue recovery, truck rest, icons and reload require manual game tests.',
                             'Distances ignore elevation, road routing and physical access.',
                             'Full-sector overrides require the declared effective stack.',
                             'Single-control-node rest prefabs and compound rest placement are unsupported.',
                             'Car rests outside source sectors and the approximate halo can be missed, causing accepted boundary additions.',
                             'DLC guards remain unchanged; actual runtime availability still depends on the declared game setup.']}
    coverage,blockers = report['coverage'],report['coverage']['blockers']
    resources = {}
    try:
        modes,truck_action_block,action_tokens,hud_actions = _validate_actions(effective)
        definitions = prefab_definitions(effective)
    except (ValueError,KeyError) as exc:
        blockers.append({'reason':str(exc)})
        coverage['complete'] = False
        return report,resources
    all_paths = effective.matching(r'map/[^/]+/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)')
    source_paths = [p for p in all_paths if p in stack.resources
                    and str(stack.resources[p][0].path) in map_packages]
    source_set = set(source_paths)
    if not source_paths:
        blockers.append({'reason':'No effective sectors owned by selected map packages'})
    scope = report['scope']
    def problem(path,reason,**details):
        target = blockers if path in source_set else scope['omissions']
        target.append({'path':path,**details,'reason':reason})
    def prefetch(paths):
        for package in stack.packages:
            package.prefetch([p for p in paths if p not in overrides and stack.resources[p][0] is package],
                             disk_cache=Archive._scratch_root().parent/'package-cache'/_sha(str(package.path).encode())[:12])
    placements,standalones,nodes = [],[],defaultdict(list)
    nested,nonempty_sources = [],[]
    def load(path):
        try:
            data = effective.read(path,max_bytes=64*1024*1024)
            parsed = parse_sector(data)
            if path in source_set and parsed.items:
                nonempty_sources.append(path)
            placements.extend((path,item) for item in parsed.prefabs)
            standalones.extend((path,item,_standalone(data,item)) for item in parsed.items if item.kind==0x22)
            for node in parsed.nodes:
                nodes[node.uid].append((path,node))
            def walk(items):
                for item in items:
                    if item.kind in (4,0x22):
                        nested.append((path,item))
                    if item.kind == 0x28:
                        walk(item.details['items'])
            for item in parsed.items:
                if item.kind==0x28:
                    walk(item.details['items'])
        except (ValueError,KeyError,struct.error) as exc:
            problem(path,str(exc))
    prefetch(source_paths)
    for path in source_paths:
        load(path)
    halo = set()
    steps = scope['halo_steps']
    sector_pattern = r'(map/[^/]+/)sec([+-]\d{4})([+-]\d{4})\.(?:base|aux)'
    source_grid = defaultdict(set)
    for path in nonempty_sources:
        match = re.fullmatch(sector_pattern,path)
        source_grid[match[1]].add((int(match[2]),int(match[3])))
    # Inspect only virtual filenames here. Iterating existing paths also keeps
    # unusually large radii bounded by the mounted resource inventory.
    for path in all_paths:
        if path in source_set:
            continue
        match = re.fullmatch(sector_pattern,path)
        x,z = int(match[2]),int(match[3])
        if any(abs(x-sx)<=steps and abs(z-sz)<=steps for sx,sz in source_grid[match[1]]):
            halo.add(path)
    prefetch(sorted(halo))
    for path in sorted(halo):
        load(path)
    scope.update({'source_sector_count':len(source_paths),'nonempty_source_sector_count':len(nonempty_sources),
                  'halo_sector_count':len(halo),'source_sector_paths':source_paths,'halo_sector_paths':sorted(halo),
                  'halo_rule':'Chebyshev filename neighborhood of nonempty source sectors; no maximum prefab extent is guaranteed'})
    report['sectors_inspected'] = len(source_paths)+len(halo)
    def node_for(uid,path):
        candidates = nodes.get(uid,[])
        same = [n for p,n in candidates if p==path]
        if same:
            return same[0]
        if not candidates or len({n.raw for _,n in candidates}) != 1:
            raise ValueError(f'Unresolved/ambiguous rest node {uid:#x}')
        return candidates[0][1]
    referenced_models = {item.details['model'] for _,item in placements+nested if item.kind==4}
    descriptors = {definitions[model][0].one('prefab_desc','').lstrip('/')
                   for model in referenced_models if model in definitions}
    for package in stack.packages:
        package.prefetch([p for p in descriptors if p in stack.resources and p not in overrides
                          and stack.resources[p][0] is package],
                         disk_cache=Archive._scratch_root().parent/'package-cache'/_sha(str(package.path).encode())[:12])
    ppds,locations = {},[]
    def descriptor_for(item):
        unit,block,definition = definitions[item.details['model']]
        path = unit.one('prefab_desc').lstrip('/')
        if path not in ppds:
            data = effective.read(path)
            groups = inspect_rest_triggers(data,actions=modes.keys())
            ppds[path] = data,groups
        return unit,block,definition,path,*ppds[path]
    for path,item in nested:
        try:
            relevant = item.kind==0x22
            if item.kind==4:
                relevant = bool(descriptor_for(item)[-1])
            if relevant:
                raise ValueError('Compound-contained rest requires a container-aware world transform')
        except (ValueError,KeyError,struct.error) as exc:
            problem(path,str(exc),uid=hex(item.uid))
    for path,item in placements:
        try:
            entry = descriptor_for(item)
            if not entry[-1]:
                continue
            controls = {uid:node_for(uid,path) for uid in item.details['nodes']}
            for group in entry[-1]:
                points = _placed_vertices(entry[-2],item,controls,group['vertices'])
                locations.append({'path':path,'item':item,'entry':entry,'group':group,
                                  'points':points,'radius':0.,'car':'car' in modes[group['action']],
                                  'truck':bool(modes[group['action']] & {'truck','bus'}),'kind':'prefab'})
        except (ValueError,KeyError,struct.error) as exc:
            problem(path,str(exc),uid=hex(item.uid))
    for path,item,trigger in standalones:
        try:
            actions = trigger['actions']
            rest_actions = [a for a in actions if a['action'] in modes]
            if any(a['custom'] and a['action'] in hud_actions for a in actions):
                raise ValueError('Standalone HUD action has unsupported custom parameters')
            if not rest_actions:
                continue
            activation = _standalone_activation(item.flags)
            if activation['init_disabled'] or not activation['vehicle_activation']:
                report['excluded_rest_locations'].append({'path':path,'uid':hex(item.uid),
                    'reason':'initially disabled' if activation['init_disabled'] else 'vehicle activation disabled',**activation})
                continue
            placed = [node_for(uid,path).position for uid in trigger['nodes']]
            points = [(p[0],p[2]) for p in placed]
            if len(points)==2:
                trigger = {**trigger,'radius':math.dist(placed[0],placed[1])}
                points = points[:1]
            elif len(points)>2:
                _validate_polygon(points)
            vehicles = set().union(*(modes[a['action']] for a in rest_actions))
            locations.append({'path':path,'item':item,'trigger':trigger,'points':points,
                              'radius':trigger['radius'],'car':'car' in vehicles,
                              'truck':bool(vehicles & {'truck','bus'}),'kind':'standalone',
                              'activation':activation})
        except (ValueError,KeyError,struct.error) as exc:
            problem(path,str(exc),uid=hex(item.uid))
    cars = [location for location in locations if location['car']]
    coverage['existing_car_locations'] = len(cars)
    scope['guarded_standalone_rest_locations'] = sum(bool(v.get('activation',{}).get('dlc_guard')) for v in locations)
    selected = defaultdict(list)
    def bbox(points):
        return (min(p[0] for p in points),min(p[1] for p in points),
                max(p[0] for p in points),max(p[1] for p in points))
    for car in cars:
        car['bounds']=bbox(car['points'])
    for location in locations:
        path = location['path']
        if not location['truck'] or path not in stack.resources or str(stack.resources[path][0].path) not in map_packages:
            continue
        coverage['truck_polygons'] += 1
        bounds = bbox(location['points'])
        nearby=[]
        for car in cars:
            if path.split('/')[1] != car['path'].split('/')[1]:
                continue
            cb=car['bounds']; limit=radius+location['radius']+car['radius']
            dx=max(0,bounds[0]-cb[2],cb[0]-bounds[2]); dz=max(0,bounds[1]-cb[3],cb[1]-bounds[3])
            if math.hypot(dx,dz)>limit:
                continue
            distance=max(0.,polygon_distance(location['points'],car['points'])-location['radius']-car['radius'])
            if distance<=radius:
                nearby.append((distance,car))
        row={'path':path,'uid':hex(location['item'].uid),'kind':location['kind'],
             'status':'already_supported' if nearby else 'selected',
             'polygon_xz':[list(p) for p in location['points']]}
        if location['kind']=='prefab':
            row['group_id']=location['group']['id']
        if nearby:
            distance,car=min(nearby,key=lambda pair:pair[0])
            row.update({'nearest_car_distance':distance,'nearby_car_path':car['path'],
                        'nearby_car_uid':hex(car['item'].uid)})
            coverage['already_supported'] += 1
        else:
            selected[(path,location['item'].uid)].append(location)
        report['locations'].append(row)
    # Unsafe source parsing blocks edits. Neighbor omissions may hide car rests;
    # those boundary additions are explicitly accepted and remain visible.
    if blockers:
        coverage['complete']=False
        return report,{}
    edits=defaultdict(list)
    action_alias = 'rta'+_sha((map_name+':'+truck_action_block).encode())[:8]
    action_token = token(action_alias)
    action_path = f'def/world/trigger_action.{action_alias}.sii'
    if selected:
        if action_token in action_tokens or action_path in effective.resources:
            blockers.append({'reason':'Private rest action resource/unit collision'})
            coverage['complete']=False
            return report,{}
        action_block,count = re.subn(r'(\btrigger_action\s*:\s*)trig_action\.hud_parking\b',
                                     lambda m:m[1]+'trig_action.'+action_alias,truck_action_block,count=1)
        if count != 1:
            raise ValueError('Unable to clone reviewed truck rest action')
        action_block = action_block[:-1]+'\n str_params[]: "car"\n}'
        resources[action_path] = ('SiiNunit\n{\n'+action_block+'\n}\n').encode()
        report['private_action']={'token':action_alias,'resource':action_path,
                                  'vehicles':['truck','bus','car']}
    for (path,uid),chosen in sorted(selected.items()):
        first=chosen[0]; item=first['item']
        try:
            if first['kind']=='prefab':
                unit,block,definition,descriptor,original,groups=first['entry']
                if any(v['group']['action'] != _TRUCK for v in chosen):
                    raise ValueError('Custom truck-only rest action requires explicit definition cloning')
                changed,change=retarget_rest_polygons(original,{v['group']['id'] for v in chosen},
                                                       action_token,actions=modes.keys())
                seed=f'{map_name}:{path}:{uid:x}:{_sha(changed)}'
                alias='rtr'+hashlib.sha256(seed.encode()).hexdigest()[:8]
                private=f'prefab/rtfix/{alias}.ppd'; defpath=f'def/world/prefab.{alias}.sii'
                if token(alias) in definitions or any(p in effective.resources or p in resources for p in (private,defpath)):
                    raise ValueError('Private rest prefab resource collision')
                resources[private]=changed
                resources[defpath]=_alias_definition(block,unit.name,alias,private)
                edits[path].append((item.offset+57,item.offset+65,struct.pack('<Q',token(alias))))
                report['source_resources'].append({'path':descriptor,'sha256':_sha(original),
                                                   'definition':definition,'prefab_uid':hex(uid),
                                                   'private_alias':alias,**change})
            else:
                trigger=first['trigger']
                rest_actions = [a for a in trigger['actions'] if a['action'] in modes]
                if any(a['action'] != _TRUCK for a in rest_actions):
                    raise ValueError('Custom truck-only rest action requires explicit definition cloning')
                for action in rest_actions:
                    offset=action['offset']
                    edits[path].append((offset,offset+8,struct.pack('<Q',action_token)))
            coverage['added_car_polygons'] += len(chosen)
            coverage['placements_changed'] += 1
        except (ValueError,KeyError,struct.error) as exc:
            blockers.append({'path':path,'uid':hex(uid),'reason':str(exc)})
    for path,operations in sorted(edits.items()):
        original=effective.read(path,max_bytes=64*1024*1024)
        changed=_splice(original,operations)
        before,after=parse_sector(original),parse_sector(changed)
        if tuple(n.raw for n in before.nodes)!=tuple(n.raw for n in after.nodes):
            raise ValueError('Rest planner changed original map nodes')
        if before.visibility_children!=after.visibility_children or before.item_count!=after.item_count:
            raise ValueError('Rest planner changed sector topology')
        resources[path]=changed
        report['changed_sectors'].append({'path':path,'source_package':str(stack.resources[path][0].path),
                                         'source_sha256':_sha(original),'output_sha256':_sha(changed)})
        if path in overrides:
            report['composed_resource_paths'].append(path)
    coverage['complete']=not blockers
    if blockers:
        return report,{}
    report['static_validation']={'original_truck_bus_eligibility_preserved':True,
                                 'original_map_nodes_and_topology_preserved':True,
                                 'proximity_index_uses_original_car_locations':True,
                                 'all_selected_source_sectors_inspected':True,
                                 'bounded_halo_index':True}
    return report,resources
