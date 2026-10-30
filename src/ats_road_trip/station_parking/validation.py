"""Configuration and bounded model-surface validation for station parking."""
from __future__ import annotations

from dataclasses import fields
import math
import re

from ..package import virtual_path
from ..rest_stops import polygon_distance
from .geometry import _contains
from .mesh import sample_surface_height
from .methods.painted import PaintedParkingParameters
from .methods.unmarked import ParkingParameters

def validate_config(config):
    required={'schema_version','processor','station_id','map_name','game_version','method',
              'sector','prefab_uid','fingerprints','model_geometry','mesh_materials','parameters'}
    if isinstance(config,dict) and config.get('schema_version')==2:
        required.add('material_resources')
    if not isinstance(config,dict) or set(config)!=required:
        raise ValueError('Station configuration has missing or unknown fields')
    if type(config['schema_version']) is not int or config['schema_version'] not in (1,2) or config['processor']!='station_parking':
        raise ValueError('Expected station_parking configuration schema 1 or 2')
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
    if config['schema_version']==2:
        fingerprint_keys.update({'model_definition','mesh_state'})
        resources=config['material_resources']
        if not isinstance(resources,dict) or not resources:
            raise ValueError('Schema 2 requires reviewed effective material resource fingerprints')
        for path,digest in resources.items():
            if (not isinstance(path,str) or virtual_path(path)!=path
                    or not path.endswith(('.mat','.tobj','.dds'))
                    or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest)):
                raise ValueError('Material resources must pin canonical MAT/TOBJ/DDS paths and SHA-256 hashes')
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
        if (not isinstance(names,list) or (not names and (role=='ground' or config['method']=='painted_bays'))
                or any(not isinstance(n,str) or not n for n in names) or len(set(names))!=len(names)):
            raise ValueError(f'{role} materials must be explicit unique aliases')
    if not isinstance(config['parameters'],dict):
        raise ValueError('Parking parameters must be an object')
    if config['method']=='painted_bays':
        from .methods.painted import PaintedParkingParameters
        parameter_type=PaintedParkingParameters
    else:
        parameter_type=ParkingParameters
    if set(config['parameters'])-{f.name for f in fields(parameter_type)}:
        raise ValueError('Unsupported station parking parameter')
    parameter_type(**config['parameters'])
    return config

def _mesh_checks(mesh, polygon, approach, ground, paint, *, report_clearance=False):
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
    minimum_model_distance=None
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
            distance=polygon_distance(polygon,xz)
            if approach:distance=min(distance,polygon_distance(approach,xz))
            if report_clearance:
                minimum_model_distance=distance if minimum_model_distance is None else min(distance,minimum_model_distance)
            if distance<.15:
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
            **({'minimum_model_distance':minimum_model_distance,'model_obstacle_margin':.15} if report_clearance else {}),
            'limits':'Sampled render surfaces and model geometry; physics, external furniture and driving access require manual checks.'}
