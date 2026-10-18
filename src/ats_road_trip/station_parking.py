"""Source-pinned, individually selected gas-station parking proof of concept.

This processor is intentionally separate from the map-wide rest pipeline. It
uses model paint geometry or building/lot proposals corroborated by model
surfaces. It never searches for stations, applies rest proximity rules, or
changes original truck triggers. Physical access remains a gameplay question.
"""
from __future__ import annotations

import hashlib
from dataclasses import fields
from html import escape
import json
import math
import re
import struct

from .bulk_fuel import _alias_definition, prefab_definitions
from .fuel_matching import _control_positions, match_gas_services
from .local_fuel import token
from .map_sector import parse_sector
from .package import virtual_path
from .prefab_contexts import plan_prefab_contexts
from .rest_stops import _placed_vertices, _validate_actions, inspect_rest_triggers, polygon_distance
from .station_geometry import ParkingParameters, _contains, _within, inspect_station_map, propose_unmarked_parking
from .station_mesh import read_station_mesh, sample_surface_height
from .station_trigger import append_car_parking_polygon


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def validate_config(config):
    required={'schema_version','processor','station_id','map_name','game_version','method',
              'sector','prefab_uid','fingerprints','model_geometry','mesh_materials','parameters'}
    if not isinstance(config,dict) or set(config)!=required:
        raise ValueError('Station configuration has missing or unknown fields')
    if type(config['schema_version']) is not int or config['schema_version']!=1 or config['processor']!='station_parking':
        raise ValueError('Expected station_parking configuration schema 1')
    if not isinstance(config['station_id'],str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}',config['station_id']):
        raise ValueError('Station ID must be a short lowercase slug')
    if not isinstance(config['map_name'],str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 ._-]{0,63}',config['map_name']):
        raise ValueError('Map name must be a short printable label')
    if config['method'] not in ('painted_bays','unmarked_geometry'):
        raise ValueError('Select painted_bays or unmarked_geometry explicitly')
    if not isinstance(config['game_version'],str) or not re.fullmatch(r'1\.61(?:\.\d+)*',config['game_version']):
        raise ValueError('Configuration must pin an ATS 1.61 version')
    if not isinstance(config['sector'],str) or not re.fullmatch(r'map/usa/sec[+-]\d{4}[+-]\d{4}\.base',config['sector']):
        raise ValueError('Select one explicit USA base-sector path')
    if not isinstance(config['prefab_uid'],str) or not re.fullmatch(r'0x[0-9a-f]{1,16}',config['prefab_uid']) or int(config['prefab_uid'],16)==0:
        raise ValueError('Select one nonzero prefab UID as lowercase hexadecimal')
    fingerprint_keys={'source_archive','sector','descriptor','model_geometry','mesh'}
    fp=config['fingerprints']
    if (not isinstance(fp,dict) or not fingerprint_keys<=set(fp) or set(fp)-fingerprint_keys-{'base_fix'}
            or any(not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v) for v in fp.values())):
        raise ValueError('Configuration must pin SHA-256 hashes of all station inputs')
    path=config['model_geometry']
    if not isinstance(path,str) or virtual_path(path)!=path or not path.endswith('.pmg'):
        raise ValueError('Pin one virtual model geometry PMG path')
    materials=config['mesh_materials']
    if not isinstance(materials,dict) or set(materials)!={'ground','paint'}:
        raise ValueError('Declare reviewed ground and paint material aliases')
    for role,names in materials.items():
        if not isinstance(names,list) or not names or any(not isinstance(n,str) or not n for n in names) or len(set(names))!=len(names):
            raise ValueError(f'{role} materials must be explicit unique aliases')
    if not isinstance(config['parameters'],dict):
        raise ValueError('Parking parameters must be an object')
    if config['method']=='painted_bays':
        from .painted_parking import PaintedParkingParameters
        parameter_type=PaintedParkingParameters
    else:
        parameter_type=ParkingParameters
    if set(config['parameters'])-{f.name for f in fields(parameter_type)}:
        raise ValueError('Unsupported station parking parameter')
    parameter_type(**config['parameters'])
    return config


def _mesh_checks(mesh, polygon, approach, ground, paint):
    """Check sampled surface coverage plus all model triangle obstacle extents.

    Sampling is disclosed, not a claim of collision-complete access. Vertical
    and elevated render triangles and parked-vehicle locators are exclusions.
    """
    reasons=[]
    queries=[]
    for region in [polygon,*([approach] if approach else [])]:
        xmin,xmax=min(p[0] for p in region),max(p[0] for p in region)
        zmin,zmax=min(p[1] for p in region),max(p[1] for p in region)
        if (xmax-xmin)*(zmax-zmin)>500:
            return {'rejection_reasons':['candidate_exceeds_bounded_surface_budget']}
        queries.extend(region)
        for ix in range(int(math.ceil((xmax-xmin)/.5))+1):
            for iz in range(int(math.ceil((zmax-zmin)/.5))+1):
                point=(min(xmax,xmin+ix*.5),min(zmax,zmin+iz*.5))
                if _contains(point,region): queries.append(point)
    queries=sorted(set(map(tuple,queries)))
    if len(queries)>5000:
        return {'rejection_reasons':['candidate_exceeds_bounded_surface_budget']}
    ground_triangles=sum(len(p['triangles']) for p in mesh['pieces'] if p['material'] in ground)
    work_units=len(queries)*ground_triangles+sum(len(p['triangles']) for p in mesh['pieces'])
    if work_units>5_000_000:
        return {'work_units':work_units,'rejection_reasons':['candidate_exceeds_bounded_mesh_work_budget']}
    heights=[];missing=[]
    for point in queries:
        try: heights.append(sample_surface_height(mesh,point,ground))
        except ValueError as exc: missing.append({'xz':list(point),'reason':str(exc)})
    if missing:
        reasons.append('selected_ground_mesh_does_not_cover_all_surface_samples')
    if not heights:
        return {'sample_count':len(queries),'missing_samples':missing[:10],'rejection_reasons':reasons}
    if max(heights)-min(heights)>.25:
        reasons.append('ground_height_variation_exceeds_0_25')
    height=sum(heights)/len(heights)
    # All non-ground/paint triangles intersecting the passenger-car clearance
    # volume are considered, including collpart1 exported in the model itself.
    # This is render/model geometry, not a verified ATS physics representation.
    obstacles=[]
    for piece in mesh['pieces']:
        if piece['material'] in set(ground)|set(paint): continue
        positions=piece['positions']
        for index,triangle in enumerate(piece['triangles']):
            vertices=[positions[i] for i in triangle]
            if max(p[1] for p in vertices)<height+.2 or min(p[1] for p in vertices)>height+1.9:
                continue
            xz=[(p[0],p[2]) for p in vertices]
            # A degenerate horizontal projection is a wall edge, still a real
            # exclusion. Distance handles polygon/segment/point inputs.
            xz=list(dict.fromkeys(xz))
            if polygon_distance(polygon,xz)<.15 or (approach and polygon_distance(approach,xz)<.15):
                obstacles.append({'piece':piece['index'],'triangle':index,'material':piece['material']})
    if obstacles: reasons.append('model_geometry_intersects_car_clearance_volume')
    parked=[]
    for locator in mesh['locators']:
        hookup=locator['hookup']
        if '.parked.' not in hookup: continue
        position=locator['position']; radius=10. if hookup.startswith('truck.') else 3.5
        if polygon_distance(polygon,[(position[0],position[2])])<radius:
            parked.append({'index':locator['index'],'hookup':hookup,'exclusion_radius':radius})
    if parked: reasons.append('parked_vehicle_locator_exclusion')
    vertices=[]
    if not missing:
        vertices=[[x,sample_surface_height(mesh,(x,z),ground),z] for x,z in polygon]
    return {'height_mean':height,'height_min':min(heights),'height_max':max(heights),
            'sample_count':len(queries),'sample_spacing':.5,'work_units':work_units,'missing_samples':missing[:10],
            'model_obstacles':obstacles[:30],'model_obstacle_count':len(obstacles),
            'parked_locator_conflicts':parked,'vertices_xyz':vertices,
            'rejection_reasons':reasons,
            'limits':'Sampled render surfaces and model geometry; physics, external furniture and driving access require manual checks.'}


def _inset_rectangle(points, margin=.25):
    """Retain source-derived orientation while moving trigger edges off paint."""
    if len(points)!=4:
        raise ValueError('Painted bank must be a four-corner rectangle')
    a,b,c,d=points
    width=math.dist(a,b);depth=math.dist(a,d)
    if min(width,depth)<=2*margin:
        raise ValueError('Painted bank is too small for the trigger edge margin')
    u=((b[0]-a[0])/width,(b[1]-a[1])/width)
    v=((d[0]-a[0])/depth,(d[1]-a[1])/depth)
    if abs(u[0]*v[0]+u[1]*v[1])>1e-5:
        raise ValueError('Painted bank is not rectangular')
    return [[p[0]+margin*(su*u[0]+sv*v[0]),p[1]+margin*(su*u[1]+sv*v[1])]
            for p,su,sv in [(a,1,1),(b,-1,1),(c,-1,-1),(d,1,-1)]]


def _world_vertices(ppd,prefab,nodes,vertices):
    horizontal=_placed_vertices(ppd,prefab,nodes,vertices)
    controls=_control_positions(ppd)
    origin=prefab.details['origin'];anchor=nodes[prefab.details['nodes'][0]].position
    return [[x,anchor[1]+p[1]-controls[origin][1],z] for p,(x,z) in zip(vertices,horizontal)]


def plan_station_parking(stack,config,mesh_text,*,map_package,game_version):
    """Return a reproducible report and only the new station's resource edits."""
    validate_config(config)
    if config['game_version']!=game_version:
        raise ValueError('Installed game version differs from reviewed station configuration')
    report={'schema_version':1,'processor':'station_parking','station_id':config['station_id'],
            'map_name':config['map_name'],'method':config['method'],'configuration':config,
            'coverage':{'complete':False,'blockers':[]},'experimental':True,'in_game_verified':False,
            'selection_policy':'One explicit source-pinned station; no rest radius, density or truck fallback',
            'limitations':['Physical car access, NPC occupancy, icons, fatigue and reload remain unverified.',
                           'Sampled model geometry is not a complete physical-world collision scan.']}
    blockers=report['coverage']['blockers']
    def blocked(reason):
        blockers.append({'area':'station_parking','reason':reason})
        return report,{}
    sector_path=config['sector'];uid=int(config['prefab_uid'],16)
    source_package=next((p for p in stack.packages if str(p.path)==map_package),None)
    if source_package is None or sector_path not in source_package.files:
        raise ValueError('Explicit source map does not contain selected station sector')
    if not source_package.path.is_file():
        raise ValueError('Station source must be a pinned archive, not a directory')
    digest=hashlib.sha256()
    with source_package.path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    if digest.hexdigest()!=config['fingerprints']['source_archive']:
        raise ValueError('Source archive SHA-256 drift')
    source=parse_sector(source_package.read(sector_path,max_bytes=64*1024*1024))
    if not any(p.uid==uid for p in source.prefabs):
        raise ValueError('Selected station UID is absent from original source map')
    data=stack.read(sector_path,max_bytes=64*1024*1024)
    if _hash(data)!=config['fingerprints']['sector']:
        raise ValueError('Effective selected sector SHA-256 drift')
    sector=parse_sector(data);prefab=next((p for p in sector.prefabs if p.uid==uid),None)
    if prefab is None: raise ValueError('Selected station is missing from effective stack')
    if prefab.details['parts'] or prefab.details['variant'] not in (0,token('default')):
        return blocked('Non-default or additional prefab parts require a separate variant review')
    definitions=prefab_definitions(stack)
    entry=definitions.get(prefab.details['model'])
    if entry is None: raise ValueError('Selected prefab has no unique effective definition')
    unit,block,definition=entry
    descriptor=(unit.one('prefab_desc','') or '').lstrip('/')
    model=(unit.one('model_desc','') or '').lstrip('/')
    if not descriptor or not model.endswith('.pmd') or model[:-4]+'.pmg'!=config['model_geometry']:
        raise ValueError('Selected prefab model does not match reviewed model geometry')
    ppd=stack.read(descriptor)
    for label,raw in [('descriptor',ppd),('model_geometry',stack.read(config['model_geometry'],max_bytes=32*1024*1024)),
                      ('mesh',mesh_text.encode('utf-8'))]:
        if _hash(raw)!=config['fingerprints'][label]: raise ValueError(f'{label} SHA-256 drift')
    modes,_,_,_=_validate_actions(stack)
    if modes.get(token('parking_car'))!={'car'}:
        raise ValueError('Native parking_car must be car-only')
    mesh=read_station_mesh(mesh_text)
    if mesh['name']!=model.rsplit('/',1)[-1][:-4]:
        raise ValueError('Converted mesh name differs from selected prefab model')
    aliases={m['alias'] for m in mesh['materials']}
    if any(set(names)-aliases for names in config['mesh_materials'].values()):
        raise ValueError('Reviewed surface/paint material alias is absent from converted mesh')
    nodes={n.uid:n for n in sector.nodes}
    # Verify original service graph and coordinate convention before proposing
    # any new interaction, including preserved fuel twins from a fuel-only base.
    services=[i for i in sector.services if i.details['parent']==uid]
    fuel_matches=match_gas_services(ppd,prefab,nodes,services)
    geometry=inspect_station_map(ppd)
    original_rest=inspect_rest_triggers(ppd,actions=set(modes))
    report.update({'source':{'sector':sector_path,'prefab_uid':hex(uid),'prefab':unit.name,
                            'descriptor':descriptor,'definition':definition,'model':model,
                            'fuel_spawn_to_service':{str(k):hex(v) for k,v in fuel_matches.items()}},
                   'geometry':geometry,'original_rest_groups':original_rest,
                   'mesh_summary':{'counts':mesh['counts'],'parts':mesh['parts'],'locators':mesh['locators']}})
    if config['method']=='painted_bays':
        from .painted_parking import PaintedParkingParameters,propose_painted_parking
        proposal=propose_painted_parking(mesh,paint_materials=config['mesh_materials']['paint'],
                                        parameters=PaintedParkingParameters(**config['parameters']))
    else:
        proposal=propose_unmarked_parking(ppd,ParkingParameters(**config['parameters']))
    report['proposal']=proposal
    report['geometry']=proposal.get('geometry',geometry)
    evaluated=[]
    work_budget=0
    if len(proposal['candidates'])>128:
        return blocked('Station proposal exceeds the bounded 128-candidate budget')
    accessible=[p for p in geometry['polygons'] if p['color']==1]
    obstacles=[p for p in geometry['polygons'] if p['color']!=1]
    for proposed in proposal['candidates']:
        candidate=dict(proposed)
        if config['method']=='painted_bays':
            candidate['mesh_envelope_xz']=candidate['polygon_xz']
            candidate['trigger_edge_inset']=.25
            candidate['polygon_xz']=_inset_rectangle(candidate['polygon_xz'])
        reasons=list(candidate.get('rejection_reasons',[]))
        polygon=candidate['polygon_xz'];approach=candidate.get('approach_xz')
        if not any(_within(list(map(tuple,polygon)),[(v[0],v[2]) for v in p['vertices']]) for p in accessible):
            reasons.append('outside_accessible_map_proxy')
        if any(polygon_distance(polygon,[(v[0],v[2]) for v in p['vertices']])<.1 for p in obstacles):
            reasons.append('intersects_building_canopy_or_green_proxy')
        # Painted banks have explicit footprint evidence, but still require
        # space to approach from at least one short-edge side. The model test
        # below checks their footprint; driving access is retained as unknown.
        checks=_mesh_checks(mesh,polygon,approach,config['mesh_materials']['ground'],config['mesh_materials']['paint'])
        work_budget+=checks.get('work_units',0)
        if work_budget>20_000_000:
            return blocked('Station evaluation exceeds the bounded total mesh work budget')
        reasons.extend(checks['rejection_reasons'])
        candidate['model_surface_checks']=checks
        if checks.get('vertices_xyz') and 'height_status' in candidate:
            candidate['height_status']='source_model_ground_surface_sampled'
        for group in original_rest:
            if modes.get(group['action'])=={'car'} and polygon_distance(polygon,[(p[0],p[2]) for p in group['vertices']])==0:
                reasons.append('already_has_overlapping_native_car_rest')
        candidate['rejection_reasons']=list(dict.fromkeys(reasons))
        evaluated.append(candidate)
    report['candidates']=evaluated
    selected=next((c for c in evaluated if not c['rejection_reasons']),None)
    report['selected']=selected
    if selected is None:
        return blocked('No geometry-derived candidate passes source/model checks; inspect candidate rejection reasons')
    # A bank is one logical area. Its separator-derived envelope allows the
    # user to choose any free bay; it does not add decorative cars or markings.
    vertices=selected['model_surface_checks']['vertices_xyz']
    selected['world_vertices_xyz']=_world_vertices(ppd,prefab,nodes,vertices)
    modified,write_report=append_car_parking_polygon(ppd,vertices)
    alias='rsp'+_hash((config['station_id']+'\0'+_hash(modified)).encode())[:8]
    private='prefab/rtfix/'+alias+'.ppd';defpath='def/world/prefab.'+alias+'.sii'
    if token(alias) in definitions or private in stack.resources or defpath in stack.resources:
        raise ValueError('Generated station prefab namespace collision')
    changed=bytearray(data);struct.pack_into('<Q',changed,prefab.offset+57,token(alias));changed=bytes(changed)
    # The whole sector is emitted, but the only source-sector bytes altered
    # here are the eight model-token bytes of the explicitly selected prefab.
    allowed=set(range(prefab.offset+57,prefab.offset+65))
    if len(changed)!=len(data) or any(i not in allowed for i,(a,b) in enumerate(zip(data,changed)) if a!=b):
        raise ValueError('Unexpected sector mutation outside selected prefab alias')
    resources={sector_path:changed,private:modified,
               defpath:_alias_definition(block,unit.name,alias,private)}
    context_report,contexts=plan_prefab_contexts(stack,resources,
        [('station_parking',sector_path,data,changed)],source=config['fingerprints']['source_archive'],
        map_name='station-parking-'+config['station_id']+'-'+config['method'])
    report['context_preservation']=context_report
    if not context_report['coverage']['complete']:
        blockers.extend(context_report['coverage']['blockers']);return report,{}
    resources.update(contexts)
    report.update({'writer':write_report,'private_alias':alias,
                   'changed_sectors':[{'path':sector_path,'source_sha256':_hash(data),'output_sha256':_hash(changed),
                                       'allowed_changed_byte_range':[prefab.offset+57,prefab.offset+65]}],
                   'model_surface_checks':selected['model_surface_checks'],
                   'static_validation':{'original_trigger_bytes_preserved':True,'original_sector_nodes_and_services_preserved':True,
                                        'only_explicit_station_retargeted':True,'native_car_only_group_appended':True}})
    report['coverage']['complete']=True
    return report,resources


def render_station_plan(report):
    """Render original numeric geometry and proposal decisions as a local SVG."""
    geometry=report.get('geometry',{})
    polygons=geometry.get('polygons',[])
    candidates=report.get('candidates',[])
    selected=report.get('selected')
    points=[(p[0],p[2]) for poly in polygons for p in poly['vertices']]
    points.extend(tuple(p) for c in candidates for p in c['polygon_xz'])
    if not points: points=[(0,0),(10,10)]
    xmin,xmax=min(p[0] for p in points)-5,max(p[0] for p in points)+5
    zmin,zmax=min(p[1] for p in points)-5,max(p[1] for p in points)+5
    scale=min(900/max(xmax-xmin,1),700/max(zmax-zmin,1))
    def pt(p):return (50+(p[0]-xmin)*scale,85+(p[1]-zmin)*scale)
    def poly(points,fill,stroke,extra=''):
        coordinates=' '.join(f'{x:.3f},{y:.3f}' for x,y in map(pt,points))
        return f'<polygon points="{coordinates}" fill="{fill}" stroke="{stroke}" stroke-width="1.2" {extra}/>'
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="880" viewBox="0 0 1050 880">',
           '<rect width="1050" height="880" fill="#fcfcfa"/>',
           f'<text x="30" y="30" font-family="sans-serif" font-size="20">{escape(report.get("station_id","Station"))} / {escape(report.get("method","diagnostic"))}</text>',
           '<text x="30" y="54" font-family="sans-serif" font-size="13">Local XZ metres; grey = building/canopy proxy, green = inaccessible proxy, red = rejected, blue = selected</text>']
    for row in polygons:
        fill={1:'#e7e4dd',2:'#aaa69f',4:'#bdd1b2'}.get(row['color'],'#e0c1cf')
        lines.append(poly([(v[0],v[2]) for v in row['vertices']],fill,'#777'))
    for road in geometry.get('roads',[]):
        a,b=map(pt,[(p[0],p[2]) for p in road['vertices']])
        lines.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#aa9c6e" stroke-width="2"/>')
    for candidate in candidates:
        if selected is not None and candidate['id']==selected['id']:continue
        lines.append(poly(candidate['polygon_xz'],'none','#bb6666' if candidate['rejection_reasons'] else '#b99d52'))
    if selected:
        if selected.get('approach_xz'):lines.append(poly(selected['approach_xz'],'#c5dcf0','#6688aa','fill-opacity="0.5"'))
        lines.append(poly(selected['polygon_xz'],'#4e97ca','#154775','fill-opacity="0.7"'))
        for bay in selected.get('bay_polygons_xz',[]):lines.append(poly(bay['polygon_xz'],'none','#fff'))
    for spawn in geometry.get('gas_spawns',[]):
        x,y=pt((spawn['position'][0],spawn['position'][2]));lines.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#216c43"/>')
    for group in report.get('original_rest_groups',[]):
        lines.append(poly([(p[0],p[2]) for p in group['vertices']],'none','#9c64a0','stroke-dasharray="5 4"'))
    for locator in report.get('mesh_summary',{}).get('locators',[]):
        if '.parked.' in locator['hookup']:
            x,y=pt((locator['position'][0],locator['position'][2]));lines.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#9c64a0"/>')
    lines.extend(['<text x="30" y="835" font-family="sans-serif" font-size="13">Green dots = GAS; purple outline = original rest; purple dots = parked-vehicle model locators.</text>',
                  '<text x="30" y="858" font-family="sans-serif" font-size="13">Experimental source/model geometry checks; game collision, fatigue, icons and reload remain unverified.</text>','</svg>'])
    return '\n'.join(lines)+'\n'
