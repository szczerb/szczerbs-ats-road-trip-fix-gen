"""Plan a source-pinned station-parking candidate and its resource edits."""
from __future__ import annotations

import hashlib
import math
import struct

from ..bulk_fuel import _alias_definition, prefab_definitions
from ..fuel_matching import _control_positions, match_gas_services
from ..local_fuel import token
from ..map_sector import parse_sector
from ..package import virtual_path
from ..prefab_contexts import plan_prefab_contexts
from ..rest_stops import _placed_vertices, _validate_actions, inspect_rest_triggers, polygon_distance
from .geometry import _contains, _within, inspect_station_map
from .mesh import read_station_mesh, sample_surface_height
from .methods.painted import PaintedParkingParameters, propose_painted_parking
from .methods.unmarked import ParkingParameters, propose_unmarked_parking
from .trigger import append_car_parking_polygon
from .validation import _mesh_checks, validate_config

def _hash(data):
    return hashlib.sha256(data).hexdigest()

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

def plan_station_parking(stack,config,mesh_text,*,map_package,game_version,mesh_state_text=None):
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
    if config['schema_version']==1 and (prefab.details['parts'] or prefab.details['variant'] not in (0,token('default'))):
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
    if config['schema_version']==2:
        from .model_state import resolve_model_state
        if mesh_state_text is None or _hash(mesh_state_text.encode('utf-8'))!=config['fingerprints']['mesh_state']:
            raise ValueError('mesh_state SHA-256 drift or missing paired PIT')
        if _hash(stack.read(model,max_bytes=32*1024*1024))!=config['fingerprints']['model_definition']:
            raise ValueError('model_definition SHA-256 drift')
        mesh,state=resolve_model_state(mesh,mesh_state_text,variant=prefab.details['variant'],
                                       additional_parts=prefab.details['parts'])
        materials=[]
        for path,digest in sorted(config['material_resources'].items()):
            if path not in stack.resources or _hash(stack.read(path,max_bytes=32*1024*1024))!=digest:
                raise ValueError('Effective material resource SHA-256 drift: '+path)
            materials.append({'path':path,'sha256':digest,'provider':stack.resources[path][1].package})
        role_aliases=set(config['mesh_materials']['ground'])|set(config['mesh_materials']['paint'])
        role_dependencies=[]
        for material in state['materials']:
            if material['alias'] not in role_aliases:continue
            for texture in material['textures']:
                base=texture.lstrip('/')
                for suffix in ('.mat','.tobj','.dds'):
                    path=base if base.endswith(suffix) else base+suffix
                    if path in stack.resources:
                        if path not in config['material_resources']:
                            raise ValueError('Reviewed ground/paint material dependency is not pinned: '+path)
                        role_dependencies.append(path)
        report['role_material_dependency_scope']={'aliases':sorted(role_aliases),
            'direct_named_resources':sorted(set(role_dependencies)),
            'limits':'Paired PIT texture references and same-name MAT/TOBJ/DDS resources; not all visible materials or an exhaustive texture graph parser.'}
        report['effective_model_state']=state
        report['effective_material_resources']=materials
        dependencies=[sector_path,definition,descriptor,model,config['model_geometry']]
        report['effective_inputs']=[{'path':path,'sha256':_hash(stack.read(path,max_bytes=64*1024*1024)),
                                    'provider':stack.resources[path][1].package} for path in dependencies]
        report['activation']={'polygon_range':3.,'range_axis':'vertical','flags':0,
            'partial_activation':False,'vehicle_test_geometry':'Unknown',
            'pose_envelope_status':'Unknown; no engine-predicted usable-pose envelope',
            'physical_vs_activation':'Native polygon retained without assumed vehicle-reference padding'}
    aliases={m['alias'] for m in mesh['materials']}
    if any(set(names)-aliases for names in config['mesh_materials'].values()):
        raise ValueError('Reviewed surface/paint material alias is absent from converted mesh')
    nodes={n.uid:n for n in sector.nodes}
    # Verify original service graph and coordinate convention before proposing
    # any new interaction, including preserved fuel twins from a fuel-only base.
    services=[i for i in sector.services if i.details['parent']==uid]
    fuel_graph_error=None
    try:
        fuel_matches=match_gas_services(ppd,prefab,nodes,services)
    except ValueError as exc:
        if config['schema_version']==1:raise
        fuel_graph_error=str(exc);fuel_matches={}
    if config['schema_version']==2:
        report['fuel_graph_validation']={'complete':fuel_graph_error is None,
            'reason':fuel_graph_error,'linked_service_count':len(services),
            'limits':'A failed service/locator graph permits local diagnostics only, never generation.'}

    geometry=inspect_station_map(ppd)
    original_rest=inspect_rest_triggers(ppd,actions=set(modes))
    if config['schema_version']==2:
        from .features import inspect_model_features
        report['model_features']=inspect_model_features(mesh,ground=config['mesh_materials']['ground'],
                                                      paint=config['mesh_materials']['paint'])
    report.update({'source':{'sector':sector_path,'prefab_uid':hex(uid),'prefab':unit.name,
                            'descriptor':descriptor,'definition':definition,'model':model,
                            'fuel_spawn_to_service':{str(k):hex(v) for k,v in fuel_matches.items()}},
                   'geometry':geometry,'original_rest_groups':original_rest,
                   'mesh_summary':{'counts':mesh['counts'],'parts':mesh['parts'],'locators':mesh['locators']}})
    if config['method']=='painted_bays':
        from .methods.painted import PaintedParkingParameters,propose_painted_parking
        proposal=propose_painted_parking(mesh,paint_materials=config['mesh_materials']['paint'],
                                        parameters=PaintedParkingParameters(**config['parameters']))
    else:
        proposal=propose_unmarked_parking(ppd,ParkingParameters(**config['parameters']),
            **({'layouts':('perpendicular','parallel')} if config['schema_version']==2 else {}))
    if config['schema_version']==2 and config['method']=='unmarked_geometry':
        from .methods.curbside import propose_curb_anchored_candidates
        curb_candidates=propose_curb_anchored_candidates(mesh,geometry,ground=config['mesh_materials']['ground'],
            paint=config['mesh_materials']['paint'],parameters=ParkingParameters(**config['parameters']))
        proposal['candidates'].extend(curb_candidates)
        proposal['curb_candidate_count']=len(curb_candidates)
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
            candidate['trigger_edge_inset']=.25 if config['schema_version']==1 else 0.
            if config['schema_version']==1:
                candidate['polygon_xz']=_inset_rectangle(candidate['polygon_xz'])
        reasons=list(candidate.get('rejection_reasons',[]))
        if config['schema_version']==2:
            conflicts=[]
            for feature in report['model_features']['entrance_clearance']['proxies']:
                if any(polygon_distance(region,feature['polygon_xz'])==0
                       for region in [candidate['polygon_xz'],*([candidate['approach_xz']] if candidate.get('approach_xz') else [])]):
                    conflicts.append(feature['id'])
            candidate['entrance_proxy_conflicts']=conflicts
            if conflicts:reasons.append('intersects_door_keep_clear_proxy')
        polygon=candidate['polygon_xz'];approach=candidate.get('approach_xz')
        if not any(_within(list(map(tuple,polygon)),[(v[0],v[2]) for v in p['vertices']]) for p in accessible):
            reasons.append('outside_accessible_map_proxy')
        if any(polygon_distance(polygon,[(v[0],v[2]) for v in p['vertices']])<.1 for p in obstacles):
            reasons.append('intersects_building_canopy_or_green_proxy')
        # Painted banks have explicit footprint evidence, but still require
        # space to approach from at least one short-edge side. The model test
        # below checks their footprint; driving access is retained as unknown.
        if config['schema_version']==2:
            from .selection import evaluate_access
            candidate['rejection_reasons']=list(dict.fromkeys(reasons))
            access_parameters={}
            if config['method']=='unmarked_geometry':
                parameters=ParkingParameters(**config['parameters'])
                access_parameters={'pump_clearance':parameters.pump_clearance,'aisle_depth':parameters.aisle_depth,
                    'road_clearance':parameters.road_clearance,'obstacle_margin':parameters.obstacle_margin}
            access=evaluate_access(candidate,geometry,mesh,ground=config['mesh_materials']['ground'],
                                   paint=config['mesh_materials']['paint'],**access_parameters)
            candidate.update({key:value for key,value in access.items() if key!='rejection_reasons'})
            reasons.extend(access['rejection_reasons'])
            approach=candidate.get('approach_xz')
            checks=access['model_surface_checks'] or {'rejection_reasons':[],'sampling_status':'Skipped after access rejection'}
            candidate['physical_parking_polygon_xz']=candidate.get('mesh_envelope_xz',polygon)
            candidate['activation_polygon_xz']=polygon
        else:
            checks=_mesh_checks(mesh,polygon,approach,config['mesh_materials']['ground'],config['mesh_materials']['paint'])
        work_budget+=candidate.get('evaluation_work_units',checks.get('work_units',0))
        if work_budget>20_000_000:
            return blocked('Station evaluation exceeds the bounded total mesh work budget')
        reasons.extend(checks['rejection_reasons'])
        candidate['model_surface_checks']=checks
        if checks.get('vertices_xyz') and 'height_status' in candidate:
            candidate['height_status']='source_model_ground_surface_sampled'
        native_cover=[]
        for group in original_rest:
            if modes.get(group['action'])!={'car'}:continue
            native=[(p[0],p[2]) for p in group['vertices']]
            if polygon_distance(polygon,native)==0:
                reasons.append('already_has_overlapping_native_car_rest')
            if _within(polygon,native):native_cover.append(group['id'])
        if config['schema_version']==2:
            candidate['fully_covering_native_car_groups']=native_cover
        candidate['rejection_reasons']=list(dict.fromkeys(reasons))
        evaluated.append(candidate)
    if config['schema_version']==2:
        from .selection import rank_candidates
        evaluated=rank_candidates(evaluated)
        report['ranking_policy']='Valid first; evidence, clearance and capacity components with stable-ID tie break (see ranking_components)'
    report['candidates']=evaluated
    selected=next((c for c in evaluated if not c['rejection_reasons']),None)
    report['selected']=selected
    if fuel_graph_error:
        return blocked('Effective GAS/service graph is unverified: '+fuel_graph_error)
    if (config['schema_version']==2 and config['method']=='painted_bays' and evaluated
            and all(c['fully_covering_native_car_groups'] for c in evaluated)):
        report['already_covered']=True
        report['state']='already_covered'
        report['selection_outcome']='All detected painted banks are contained by original native car rest; no duplicate generated'
        report['coverage']['complete']=True
        return report,{}
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
