"""Map-wide dedicated station bays, discovered from original source ownership.

Unsupported layouts are explicit skips. This module never calls the truck-rest
processor or mutates a source rest/service action. Fuel overlays are retained as
its exact baseline and independently checked sector token patches compose bays.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import struct

from ..bulk_fuel import prefab_definitions
from ..map_sector import parse_sector
from ..ppd import inspect_ppd
from ..prefab_contexts import plan_prefab_contexts
from ..rest_stops import _validate_actions, inspect_rest_triggers, _placed_vertices, polygon_distance
from .catalog import load_reviewed_catalog
from .planner import plan_station_parking
from .local_context import load_local_context


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _neighbors(stack,path):
    match=re.fullmatch(r'(map/usa/sec)([+-]\d{4})([+-]\d{4})\.base',path)
    if match is None:raise ValueError('Station ownership requires standard USA base sector')
    prefix,x,z=match.groups()
    return sorted(p for dx in (-1,0,1) for dz in (-1,0,1) for suffix in ('base','aux')
                  if (p:=f'{prefix}{int(x)+dx:+05d}{int(z)+dz:+05d}.{suffix}') in stack.resources)


def _file_hash(path,cache):
    identity=(str(path),path.stat().st_size,path.stat().st_mtime_ns)
    if identity not in cache:
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
        cache[identity]=digest.hexdigest()
    return cache[identity]


def _compose(stack,plans):
    """Apply disjoint eight-byte patches to the shared effective fuel baseline."""
    output={};patches={};baselines={}
    for report,resources in plans:
        if not report['coverage']['complete'] or report['coverage']['blockers']:
            raise ValueError('Cannot compose an incomplete station plan')
        sector=report['configuration']['sector'];before=stack.read(sector,max_bytes=64*1024*1024)
        change=report['changed_sectors'][0];start,end=change['allowed_changed_byte_range']
        after=resources[sector]
        if (_sha(before)!=change['source_sha256'] or _sha(after)!=change['output_sha256']
                or end-start!=8 or len(before)!=len(after)
                or before[:start]!=after[:start] or before[end:]!=after[end:]):
            raise ValueError('Station plan modifies bytes outside its guarded model token')
        if any(start<other_end and other_start<end for other_start,other_end,_ in patches.get(sector,[])):
            raise ValueError('Conflicting station placement model token patches')
        patches.setdefault(sector,[]).append((start,end,after[start:end]));baselines[sector]=before
        for path,data in resources.items():
            if path==sector or re.fullmatch(r'def/data_context(?:\.[^/]+)?\.sii',path):continue
            if path in output and output[path]!=data:raise ValueError('Conflicting private station resource: '+path)
            if path in stack.resources:raise ValueError('Station would overwrite a private input resource: '+path)
            output[path]=data
    changes=[]
    for path in sorted(patches):
        before=baselines[path];after=bytearray(before)
        for start,end,data in sorted(patches[path]):after[start:end]=data
        output[path]=bytes(after)
        changes.append({'path':path,'source_sha256':_sha(before),'output_sha256':_sha(output[path]),
                        'allowed_changed_byte_ranges':[[a,b] for a,b,_ in sorted(patches[path])]})
    return dict(sorted(output.items())),changes


def _service_context(parsed):
    nodes={};services={}
    for sector in parsed.values():
        for node in sector.nodes:
            other=nodes.get(node.uid)
            if other is not None and (other.position!=node.position or other.rotation!=node.rotation):
                raise ValueError('Conflicting cross-sector node positions or orientations')
            nodes.setdefault(node.uid,node)
        for service in sector.services:
            if service.uid in services and (services[service.uid].kind,services[service.uid].flags,services[service.uid].details)!=(service.kind,service.flags,service.details):
                raise ValueError('Conflicting cross-sector service records')
            services.setdefault(service.uid,service)
    return {'nodes':nodes,'services':list(services.values())}


def plan_map_station_parking(stack, *, map_packages:set[str], map_name:str,
                             game_version='1.61.3.18',catalog=None,ownership_stack=None,
                             work_dir=None,method='automatic',improve_existing_car_parking=False):
    """Return ``(report, resources)`` for all original source-owned placements.

    ``stack`` is the effective staged fuel overlay. ``ownership_stack`` is the
    declared original game/map/resource stack, excluding prior generated fixes.
    Family catalog entries contain reviewed PIM/PIT/PMG/PMD/material identities,
    explicit role aliases and permitted original descriptor paths. Original PPD
    and placement bytes are captured in reproducible source pins per location.
    ``method`` selects automatic marked-first, painted_bays or unmarked_geometry.
    Skips are coverage outcomes, never silent truck-space fallbacks.
    """
    if type(improve_existing_car_parking) is not bool:
        raise ValueError('improve_existing_car_parking must be a boolean')
    if method not in ('automatic','painted_bays','unmarked_geometry'):
        raise ValueError('Select automatic, painted_bays or unmarked_geometry station method')
    if not isinstance(map_packages,set) or not map_packages:raise ValueError('Declare original map_packages')
    original=ownership_stack or stack
    if any(path.startswith('prefab/rtfix/') for path in original.resources):
        raise ValueError('Original ownership stack contains generated private fixes; dedicated parking requires original sources')
    names={str(p) for p in map_packages}
    sources=[p for p in original.packages if str(p.path) in names or p.path.name in names]
    if not sources:raise ValueError('No declared original map source is mounted')
    if any(not p.path.is_file() for p in sources):raise ValueError('Original station map source must be an archive')
    source_paths={str(p.path) for p in sources}
    catalog=load_reviewed_catalog() if catalog is None else catalog
    definitions=prefab_definitions(stack);original_defs=prefab_definitions(original)
    from .native_support import station_action_state
    action_state=station_action_state(stack)
    cache={'stack_indexes':{id(stack):(stack,definitions,action_state)},'archive_hashes':{}}
    paths=[p for p in original.matching(r'map/usa/sec[+-]\d{4}[+-]\d{4}\.base')
           if str(original.resources[p][0].path) in source_paths]
    # Model/resource-only archives can be very large. They supply no placement
    # archive pin when none of their base sectors wins in the original stack.
    # The complete declared source list remains visible separately below.
    used_sources={str(original.resources[path][0].path) for path in paths}
    source_hashes={str(p.path):_file_hash(p.path,cache['archive_hashes'])
                   for p in sources if str(p.path) in used_sources}
    report={'schema_version':1,'processor':'station_parking','map_name':map_name,'game_version':game_version,
            'strategy':'station_bays','method':method,'in_game_verified':False,
            'improve_existing_car_parking':improve_existing_car_parking,
            'coverage':{'complete':True,'blockers':[]},'locations':[],'changed_sectors':[],
            'composed_resource_paths':[],'source_archive_sha256':source_hashes,
            'declared_source_archives':sorted(source_paths),
            'selection_policy':'All original source-owned GAS placements; original native support classified independently; confirmed missing support by default; broad coherent reviewed parking regions; no truck fallback',
            'native_facility_policy':'Preserve original car/truck/bus services/actions and unrelated bytes',
            'wheelchair_marked_bays':'Eligible under the same geometry/occupancy/access checks as ordinary marked bays; hatched aisles remain excluded',
            'scope':{'original_source_sectors':len(paths),'family_count':len(catalog),'context_halo':'3x3 base/aux sectors, 100m prefab-anchor search',
                     'unsupported_model_policy':'Unchanged; report each GAS placement and family count'},
            'limitations':['Render/model geometry and UI obstacle proxies are bounded, not a full collision simulation.',
                           'Native car parking exempts its whole facility by default, independently of fueling.',
                           'Broad regions use explicit partial-contact flags; runtime vehicle shape remains unknown.',
                           'The isolated P04 unreliable painted interaction is skipped until its runtime cause is resolved.']}
    parsed={};raws={};plans=[];ground_cache={}
    def sector_bytes(path):
        if path not in raws:raws[path]=stack.read(path,max_bytes=64*1024*1024)
        return raws[path]
    def parsed_sector(path):
        if path not in parsed:parsed[path]=parse_sector(sector_bytes(path))
        return parsed[path]
    descriptor_info={}
    for path in sorted(paths):
        try:sector=parsed_sector(path)
        except ValueError as exc:
            report['coverage']['blockers'].append({'path':path,'reason':str(exc)})
            continue
        raw_sector=parse_sector(original.read(path,max_bytes=64*1024*1024))
        raw_by_uid={p.uid:p for p in raw_sector.prefabs}
        source=original.resources[path][0]
        for prefab in sector.prefabs:
            raw_prefab=raw_by_uid.get(prefab.uid)
            if raw_prefab is None:continue
            raw_entry=original_defs.get(raw_prefab.details['model']);entry=definitions.get(prefab.details['model'])
            if raw_entry is None or entry is None:continue
            raw_unit=raw_entry[0];unit=entry[0]
            raw_desc=(raw_unit.one('prefab_desc','') or '').lstrip('/')
            descriptor=(unit.one('prefab_desc','') or '').lstrip('/')
            model=(unit.one('model_desc','') or '').lstrip('/')
            if not raw_desc:continue
            if raw_desc not in descriptor_info:
                try:
                    raw_ppd=original.read(raw_desc,max_bytes=32*1024*1024)
                    info=inspect_ppd(raw_ppd)
                    descriptor_info[raw_desc]=(raw_ppd,info,None)
                except (KeyError,ValueError) as exc:descriptor_info[raw_desc]=(None,None,str(exc))
            raw_ppd,info,error=descriptor_info[raw_desc]
            if error:
                # Non-station definitions are irrelevant; malformed gas families
                # are explicit structural omissions.
                if '/gas/' not in raw_desc and model not in catalog:continue
            elif not any(s['type']==3 for s in info['spawns']):continue
            row={'sector':path,'prefab_uid':hex(prefab.uid),'source_package':source.path.name,
                 'model':model,'descriptor':descriptor,'original_descriptor':raw_desc,
                 'position':next((list(n.position) for n in sector.nodes if n.uid==prefab.details['nodes'][0]),None)}
            report['locations'].append(row)
            def skip(reason,state='skipped'):
                row.update(state=state,reason=reason)
            if error:skip('original_descriptor_invalid: '+error);continue
            if model!=(raw_unit.one('model_desc','') or '').lstrip('/'):
                skip('effective_model_does_not_match_original_source');continue
            from .native_support import classify_native_car_parking
            native=classify_native_car_parking(original,path,raw_prefab.uid,
                definitions=original_defs,cache=cache)
            row['native_car_parking']=native
            if native['state']=='unknown':
                skip('original_native_car_parking_unknown');continue
            if native['state']=='present' and not improve_existing_car_parking:
                skip('original_native_car_parking_present',state='already_supported');continue
            family=catalog.get(model)
            if family is None:skip('unsupported_model_family');continue
            row['family']=family['family']
            if raw_desc not in family['source_descriptors']:
                skip('original_descriptor_not_reviewed_for_model_family');continue
            # P04's intended bay was specifically unreliable; retain native
            # facilities but do not propagate an unverified repair to this site.
            if prefab.uid==0x89e8c438a900001 and source.path.name=='Reforma_3_0_1_161.scs':
                skip('P04_reported_unreliable_activation_pending_runtime_attribution');continue
            mismatches=[]
            for label,resource_path in [('model_definition',model),('model_geometry',family['model_geometry'])]:
                if resource_path not in ground_cache:ground_cache[resource_path]=_sha(stack.read(resource_path,max_bytes=32*1024*1024))
                if ground_cache[resource_path]!=family['fingerprints'][label]:mismatches.append(label)
            if mismatches:skip('reviewed_effective_model_drift: '+','.join(mismatches));continue
            try:
                neighbors={p:parsed_sector(p) for p in _neighbors(stack,path)}
                services=_service_context(neighbors)
                anchor=services['nodes'][prefab.details['nodes'][0]].position
                context=load_local_context(stack,{p:sector_bytes(p) for p in neighbors},prefab.uid,(anchor[0],anchor[2]),definitions=definitions)
                original_groups=inspect_rest_triggers(raw_ppd,actions=set(action_state[0]))
                row['source_pins']={'sector':_sha(original.read(path,max_bytes=64*1024*1024)),
                                    'descriptor':_sha(raw_ppd),'descriptor_provider':str(original.resources[raw_desc][0].path),
                                    'original_model_token':hex(raw_prefab.details['model']),
                                    'variant':hex(prefab.details['variant']),'parts':[hex(v) for v in prefab.details['parts']]}
                row['original_rest_groups']=original_groups
                methods=family['methods'] if method=='automatic' else [method]
                methods=[m for m in methods if m!='painted_bays' or family['mesh_materials']['paint']]
                attempts=[]
                for selected_method in methods:
                    config={'schema_version':2,'processor':'station_parking',
                            'station_id':'map-station-'+hex(prefab.uid)[2:],'map_name':map_name,
                            'game_version':game_version,'method':selected_method,'sector':path,'prefab_uid':hex(prefab.uid),
                            'model_geometry':family['model_geometry'],'fingerprints':dict(family['fingerprints'],
                                source_archive=source_hashes[str(source.path)],sector=_sha(sector_bytes(path)),
                                descriptor=_sha(stack.read(descriptor,max_bytes=32*1024*1024))),
                            'mesh_materials':deepcopy(family['mesh_materials']),
                            'material_resources':deepcopy(family['material_resources']),
                            'parameters':deepcopy(family.get('parameters',{}))}
                    planned,resources=plan_station_parking(stack,config,family['mesh_text'],map_package=str(source.path),
                        game_version=game_version,mesh_state_text=family['mesh_state_text'],local_context=context,
                        planning_cache=cache,candidate_policy=dict(family.get('policy',{}),
                            broad_areas=True,allow_native_improvement=improve_existing_car_parking,
                            include_unmarked_areas='unmarked_geometry' in methods),service_context=services,original_stack=original)
                    attempts.append(planned)
                    if planned.get('already_covered'):
                        row.update(state='already_supported',reason='native_car_parking_covers_candidates',method=selected_method);break
                    if resources:
                        plans.append((planned,resources))
                        row.update(state='generated',method=selected_method,private_alias=planned['private_alias'],
                                   selected=planned['selected'],selected_areas=planned.get('selected_areas',[planned['selected']]),
                                   area_count=planned.get('writer',{}).get('area_count',1),planner=planned)
                        break
                else:skip('no_safe_dedicated_candidate')
                if row['state']!='generated':row['attempts']=attempts
                if work_dir is not None:
                    folder=Path(work_dir)/hex(prefab.uid)[2:];folder.mkdir(parents=True,exist_ok=True)
                    (folder/'report.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n',encoding='utf-8')
            except (ValueError,KeyError) as exc:skip('unsupported_or_unsafe: '+str(exc))
    resources,changes=_compose(stack,plans)
    if resources:
        transitions=[('station_parking',change['path'],sector_bytes(change['path']),resources[change['path']]) for change in changes]
        context_report,contexts=plan_prefab_contexts(stack,resources,transitions,
            source=_sha(json.dumps(source_hashes,sort_keys=True).encode()),
            map_name='station-parking-map-'+re.sub('[^a-z0-9-]','-',map_name.lower()),planning_cache=cache)
        report['context_preservation']=context_report
        if not context_report['coverage']['complete']:
            report['coverage']['blockers'].extend(context_report['coverage']['blockers'])
        resources.update(contexts)
    report['changed_sectors']=changes
    report['composed_resource_paths']=[p for p in resources if p in stack.resources]
    counts=Counter(row['state'] for row in report['locations'])
    report['coverage'].update(locations=len(report['locations']),generated=counts['generated'],
        already_supported=counts['already_supported'],skipped=counts['skipped'],
        added_car_polygons=sum(row.get('area_count',0) for row in report['locations']),
        placements_changed=counts['generated'],generated_truck_area_access=0,
        native_support=dict(Counter(row.get('native_car_parking',{}).get('state','unknown') for row in report['locations'])))
    report['skip_reasons']=dict(sorted(Counter(row.get('reason','') for row in report['locations'] if row['state']=='skipped').items()))
    report['family_coverage']=[{'model':model,'total':len(rows),'states':dict(Counter(r['state'] for r in rows)),
        'native_support':dict(Counter(r.get('native_car_parking',{}).get('state','unknown') for r in rows)),
        'generated_areas':sum(r.get('area_count',0) for r in rows)}
        for model in sorted({r['model'] for r in report['locations']})
        if (rows:=[r for r in report['locations'] if r['model']==model])]
    report['coverage']['complete']=not report['coverage']['blockers']
    if report['coverage']['blockers']:return report,{}
    return report,resources
