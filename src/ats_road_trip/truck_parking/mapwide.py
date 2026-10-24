"""Original-source discovery and additive, source-owned truck-rest coverage.

A covered painted bank anchors its authored compound. Only uncovered sibling
banks in that same compound can inherit its functional standalone rest contract.
Distance is a safety bound, never a facility association rule. Other native rest
families remain visible in the census instead of becoming scenery-parking edits.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import struct

from ..bulk_fuel import _splice, prefab_definitions
from ..fuel_matching import _control_positions
from ..local_fuel import token
from ..map_sector import parse_sector
from ..rest_stops import (_placed_vertices, _standalone, _standalone_activation,
                          inspect_rest_triggers, polygon_distance, _validate_polygon)
from ..station_parking.native_support import _action_index
from .standalone import append_truck_standalone_polygons

_SECTOR = r'map/[^/]+/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)'
_LIMIT = 128*1024*1024


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _native_modes(stack):
    stack.prefetch(r'def/world/trigger_action.*\.(?:sii|sui)')
    index=_action_index(stack)
    # Retain unresolved aliases and known non-rest HUD commands as well as
    # native modes: a per-instance override can change their rest parameters.
    stack._truck_coverage_action_index=index
    return {key:set(row['vehicles']) for key,row in index.items()
            if row.get('state') == 'rest'}


def _coverage_state(value):
    return value.get('state',value.get('coverage_state','unknown')) if isinstance(value,dict) else value


def _extend_visibility(data, clones):
    parsed=parse_sector(data);operations=[]
    for item in parsed.items:
        children=item.details.get('children',())
        added=[clones[u] for u in children if u in clones]
        if added:
            offset=item.details['child_count_offset'];insertion=item.details['child_insert_offset']
            operations.extend([(offset,offset+4,struct.pack('<I',len(children)+len(added))),
                (insertion,insertion,b''.join(struct.pack('<Q',u) for u in added))])
    added=[clones[u] for u in parsed.visibility_children if u in clones]
    if added:
        offset=parsed.visibility_children_offset
        operations.append((offset,len(data),struct.pack('<I',len(parsed.visibility_children)+len(added))
            +data[offset+4:]+b''.join(struct.pack('<Q',u) for u in added)))
    result=_splice(data,operations)
    parse_sector(result)
    return result


def _source_census(original, work_dir=None):
    """One complete source scan shared by source-owner planning partitions.

    Retain small geometry and provenance records, not whole sectors/world nodes.
    Cross-sector native references receive an explicit second resolution pass.
    Nested native contracts are diagnosed until their transform/writer is safe.
    """
    cached=getattr(original,'_truck_coverage_census',None)
    if cached is not None:
        return cached
    from .catalog import load_curve_definitions, reviewed_curve_catalog
    from .geometry import discover_curve_banks
    definitions=load_curve_definitions(original)
    model_receipts=[]
    for model,policy in reviewed_curve_catalog().items():
        for name,expected in ((model,policy['model_sha256']),
                              (policy['model_geometry'],policy['geometry_sha256'])):
            actual=_digest(original.read(name,max_bytes=64*1024*1024))
            if actual!=expected:
                raise ValueError('Reviewed truck-bank model source drift: '+name)
            model_receipts.append({'path':name,'sha256':actual,
                'provider':str(original.resources[name][0].path)})
    prefabs=prefab_definitions(original)
    modes=_native_modes(original)
    action_index=getattr(original,'_truck_coverage_action_index',
        {key:{'state':'rest','command':'hud_activate','vehicles':sorted(v)} for key,v in modes.items()})
    actions={a for a,v in modes.items() if 'truck' in v}
    paths=sorted(p for p in original.resources if re.fullmatch(_SECTOR,p))
    for package in original.packages:
        selected=[p for p in paths if original.resources[p][0] is package]
        if selected:
            # The complete-stack prefetch normally already attaches these to
            # its timestamped cache. Never extract into the supplied inputs.
            cache=getattr(package,'_disk_cache_root',None)
            if cache is None and work_dir:
                cache=Path(work_dir)/'original-sector-cache'/_digest(str(package.path).encode())[:12]
            if cache is not None:
                package.prefetch(selected,disk_cache=cache,max_bytes=_LIMIT)
    banks=[]; diagnostics=[]; native=[]; visibility=defaultdict(list); occupied=set()
    prefab_rows=[]; descriptors={}; unresolved={}; uncertain_bounds=[]
    def walk_nested(items,path,lineage=()):
        for item in items:
            occupied.add(item.uid)
            occupied.update(n.uid for n in item.details.get('compound_nodes',()))
            if item.kind in (4,0x22) and lineage:
                diagnostics.append({'sector':path,'uid':hex(item.uid),
                    'reason':'nested_native_rest_contract_not_planned',
                    'kind':item.kind,'compound_lineage':[hex(u) for u in lineage]})
            if item.kind==0x28:
                walk_nested(item.details['items'],path,lineage+(item.uid,))
    for path in paths:
        data=original.read(path,max_bytes=_LIMIT)
        sector=parse_sector(data)
        source=str(original.resources[path][0].path)
        found,issues=discover_curve_banks([(path,data,sector)],definitions)
        for row in found:
            row['source_provider']=source
            row['source_sector_sha256']=_digest(data)
        banks.extend(found);diagnostics.extend(issues)
        nodes={n.uid:n for n in sector.nodes}
        occupied.update(nodes)
        occupied.update(i.uid for i in sector.items)
        occupied.update(sector.visibility_children)
        for uid in sector.visibility_children:
            visibility[uid].append(path)
        for item in sector.items:
            for uid in item.details.get('children',()):
                visibility[uid].append(path)
            if item.kind==0x28:
                walk_nested(item.details['items'],path,(item.uid,))
            if item.kind==0x22:
                bounds=struct.unpack_from('<10f',data,item.offset+12)
                bounds_xyz=[*bounds[:3],*bounds[5:8]]
                try:
                    parsed=_standalone(data,item)
                except (ValueError,KeyError,struct.error) as exc:
                    # The complete map reader established the item extent, but
                    # unsafe radius/geometry cannot establish an absent rest.
                    # Keep only its conservative source bounds near candidates.
                    uncertain_bounds.append({'uid':hex(item.uid),'sector':path,
                        'source_provider':source,'bounds_xyz':bounds_xyz,
                        'reason':'standalone_geometry_or_action_layout_unresolved'})
                    diagnostics.append({'sector':path,'uid':hex(item.uid),
                        'reason':'standalone_geometry_or_action_layout_unresolved','detail':str(exc)})
                    continue
                rest=[a for a in parsed['actions'] if a['action'] in actions]
                uncertain_actions=[a for a in parsed['actions']
                    if a['action'] not in action_index
                    or action_index[a['action']].get('state')=='unknown'
                    or (a['custom'] and action_index[a['action']].get('command')=='hud_activate')]
                if uncertain_actions:
                    issue={'uid':hex(item.uid),'sector':path,'source_provider':source,
                        'reason':'standalone_effective_action_or_custom_hud_unresolved',
                        'action_tokens':[a['action'] for a in uncertain_actions]}
                    diagnostics.append(issue)
                    if not rest:
                        # This may be a rest action, but supplies no proven
                        # native truck contract. Its source envelope prevents
                        # false absence only at overlapping candidate banks.
                        uncertain_bounds.append({**issue,'bounds_xyz':bounds_xyz,
                            'contract_state':'unknown','node_uids':list(parsed['nodes'])})
                if not rest:
                    continue
                contract_state='native'
                try:
                    activation=_standalone_activation(item.flags)
                    if activation['init_disabled'] or not activation['vehicle_activation']:
                        contract_state='inactive'
                except ValueError as exc:
                    diagnostics.append({'sector':path,'uid':hex(item.uid),
                        'reason':'unsupported_native_activation_contract','detail':str(exc)})
                    activation={'vehicle_activation':False,'init_disabled':False,'flags':hex(item.flags)}
                    contract_state='unknown'
                if any(a['custom'] for a in rest):
                    diagnostics.append({'sector':path,'uid':hex(item.uid),
                        'reason':'standalone_rest_parameters_unresolved'})
                if uncertain_actions and contract_state!='inactive':contract_state='unknown'
                row={'uid':hex(item.uid),'sector':path,'source_provider':source,
                    'source_sector_sha256':_digest(data),'flags':item.flags,
                    'actions':[{'token':a['action'],'custom':a['custom'],
                        'vehicles':sorted(modes[a['action']])} for a in rest],
                    'node_uids':list(parsed['nodes']),'radius':parsed['radius'],
                    'activation':activation,'kind':'standalone','contract_state':contract_state,
                    'bounds_xyz':bounds_xyz}
                row['_nodes']={u:nodes[u] for u in parsed['nodes'] if u in nodes}
                missing=set(parsed['nodes'])-nodes.keys()
                for uid in missing:
                    unresolved.setdefault(uid,[]).append(row)
                native.append(row)
            elif item.kind==4:
                entry=prefabs.get(item.details['model'])
                if entry is None:
                    continue
                unit,_,_=entry
                descriptor=(unit.one('prefab_desc','') or '').lstrip('/')
                if not descriptor:
                    continue
                if descriptor not in descriptors:
                    try:
                        ppd=original.read(descriptor,max_bytes=32*1024*1024)
                        descriptors[descriptor]=(ppd,inspect_rest_triggers(ppd,actions=actions),None)
                    except (ValueError,KeyError,OSError) as exc:
                        descriptors[descriptor]=(None,[],str(exc))
                ppd,groups,error=descriptors[descriptor]
                if error:
                    diagnostics.append({'sector':path,'uid':hex(item.uid),'reason':'prefab_descriptor_unresolved','detail':error})
                if not groups:
                    continue
                row={'uid':hex(item.uid),'sector':path,'source_provider':source,
                    'definition':unit.name,'descriptor':descriptor,'kind':'prefab',
                    'variant':item.details['variant'],'parts':list(item.details.get('parts',())),
                    'group_count':len(groups),'world_polygons':[],'uncertain_polygons_xz':[],
                    'planning_support':'native coverage only; additive prefab layout rule not yet reviewed'}
                try:
                    for group in groups:
                        polygon=_placed_vertices(ppd,item,nodes,group['vertices'])
                        row['uncertain_polygons_xz'].append(polygon)
                        # PPD local height is kept separately: the horizontal
                        # transform helper does not assert a vertical transform.
                        controls=_control_positions(ppd)
                        ref=item.details['nodes'][0]
                        local_y=controls[item.details['origin']][1]
                        y0=nodes[ref].position[1]-local_y
                        origin=item.details['origin']; refs=item.details['nodes']
                        offsets=[nodes[u].position[1]-controls[(origin+i)%len(controls)][1]
                                 for i,u in enumerate(refs)]
                        if max(offsets)-min(offsets)>.10:
                            raise ValueError('Prefab controls do not prove a uniform vertical rest transform')
                        placed=[(x,p[1]+y0,z) for (x,z),p in zip(polygon,group['vertices'])]
                        row['world_polygons'].append({'polygon_xz':polygon,'vertices':placed,'id':group['id'],
                            'height':sum(p[1] for p in placed)/len(placed),
                            'vehicles':sorted(modes[group['action']]),'flags':group['flags']})
                        row['uncertain_polygons_xz'].pop()
                except (ValueError,KeyError) as exc:
                    row['geometry_reason']=str(exc)
                    row['world_polygons']=[]
                prefab_rows.append(row)
    if unresolved:
        for path in paths:
            sec=parse_sector(original.read(path,max_bytes=_LIMIT))
            for node in sec.nodes:
                if node.uid not in unresolved:
                    continue
                for row in unresolved[node.uid]:
                    prior=row['_nodes'].get(node.uid)
                    if prior is not None and prior.raw!=node.raw:
                        row['node_conflict']=True
                    row['_nodes'][node.uid]=node
    for row in native:
        ns=row['_nodes']
        if (set(row['node_uids'])<=ns.keys() and not row.get('node_conflict')
                and len(row['node_uids'])>=3 and not row['radius']):
            row['vertices']=[ns[u].position for u in row['node_uids']]
            row['polygon_xz']=[(p[0],p[2]) for p in row['vertices']]
            row['height']=sum(p[1] for p in row['vertices'])/len(row['vertices'])
            try:
                _validate_polygon(row['polygon_xz'])
            except ValueError as exc:
                row['geometry_reason']='unsupported_native_polygon: '+str(exc)
                if row['contract_state']!='inactive':row['contract_state']='unknown'
        else:
            row['geometry_reason']='unresolved/conflicting nodes or unsupported sphere contract'
            if row['contract_state']!='inactive':row['contract_state']='unknown'
    cached={'banks':banks,'native_standalone':native,'native_prefabs':prefab_rows,
        'diagnostics':diagnostics,'visibility_references':dict(visibility),
        'sector_count':len(paths),'modes':modes,'source_stack':original,
        'reviewed_model_sources':model_receipts,'occupied_uids':occupied,
        'original_uid_count':len(occupied),'uncertain_standalone_bounds':uncertain_bounds,
        'action_index':action_index}
    original._truck_coverage_census=cached
    return cached


def _lineage(bank):
    return {str(u) for u in bank.get('compound_lineage',())} | ({str(bank['parent_uid'])} if bank.get('parent_uid') else set())


def _vertices(bank):
    return [tuple(p) for p in bank.get('vertices',bank.get('vertices_xyz',()))]


def _xz(vertices):
    return [(p[0],p[2]) for p in vertices]


def _centre(vertices):
    return tuple(sum(p[i] for p in vertices)/len(vertices) for i in range(3))


def _select_regions(census):
    """Classify every discovered bank and select independently missing siblings."""
    from .geometry import compare_coverage
    native=[r for r in census['native_standalone'] if r.get('vertices')
            and r.get('contract_state','native')=='native'
            and r['activation']['vehicle_activation'] and not r['activation']['init_disabled']]
    uncertain_standalone=[]
    for source in [*census['native_standalone'],*census.get('uncertain_standalone_bounds',())]:
        if source.get('contract_state')=='inactive' or (source.get('contract_state','native')=='native'
                and not source.get('geometry_reason') and source.get('vertices')):
            continue
        bounds=source.get('bounds_xyz')
        if source.get('vertices') and not source.get('geometry_reason'):
            footprint=_xz(source['vertices'])
            heights=[p[1] for p in source['vertices']]
            low,high=min(heights)-1.,max(heights)+1.
        elif bounds:
            footprint=[(bounds[0],bounds[2]),(bounds[3],bounds[2]),
                       (bounds[3],bounds[5]),(bounds[0],bounds[5])]
            low,high=bounds[1],bounds[4]
        else:
            continue
        uncertain_standalone.append({'uid':source['uid'],'footprint':footprint,'low':low,'high':high})
    other_native=[{**g,'uid':p['uid'],'kind':'prefab'} for p in census['native_prefabs']
        for g in p.get('world_polygons',()) if g.get('vertices')]
    classified=[]
    for bank in census['banks']:
        row=dict(bank); vertices=_vertices(bank)
        if not vertices:
            row.update(coverage_state='unknown',reason='bank_has_no_resolved_world_geometry')
            classified.append(row);continue
        centre=_centre(vertices)
        nearby=[r for r in native if abs(r['height']-centre[1])<=1.
                and polygon_distance(_xz(vertices),r['polygon_xz'])<150.]
        prefab_coverage=[r for r in other_native if abs(r['height']-centre[1])<=1.
                and polygon_distance(_xz(vertices),r['polygon_xz'])<150.]
        polygons=[r['vertices'] for r in nearby+prefab_coverage]
        state=compare_coverage(vertices,polygons)
        if isinstance(state,dict):
            row['coverage_evidence']=state
            state=state.get('state',state.get('coverage_state','unknown'))
        uncertain=[p for r in census['native_prefabs'] for p in r.get('uncertain_polygons_xz',())
                   if polygon_distance(_xz(vertices),p)<=.01]
        if uncertain and state!='fully_covered':
            state='unknown'
            row['reason']='overlapping_native_prefab_has_unproven_vertical_transform'
        uncertain_native=[r for r in uncertain_standalone if r['low']<=centre[1]<=r['high']
                          and polygon_distance(_xz(vertices),r['footprint'])<=.01]
        if uncertain_native and state!='fully_covered':
            state='unknown'
            row['reason']='overlapping_standalone_has_unproven_native_contract'
            row['uncertain_native_uids']=[r['uid'] for r in uncertain_native]
        row['coverage_state']=state
        row['covering_native_uids']=[r['uid'] for r in nearby+prefab_coverage
             if _coverage_state(compare_coverage(vertices,[r['vertices']]))=='fully_covered']
        row['_nearby']=nearby
        classified.append(row)
    anchors=[]
    for row in classified:
        if row['coverage_state'] in ('fully_covered','partially_covered') and _lineage(row):
            for source in row['_nearby']:
                evidence=compare_coverage(_vertices(row),[source['vertices']])
                state=_coverage_state(evidence)
                fraction=evidence.get('maximum_native_coverage_fraction',0.) if isinstance(evidence,dict) else 0.
                if state=='fully_covered' or (source.get('flags',0)&1 and fraction>=.95):
                    anchors.append((row,source))
                    row['operationally_covered']=True
                    if state!='fully_covered':
                        row['native_edge_inset_preserved']={
                            'coverage_fraction':fraction,'partial_contact':True,
                            'policy':'At least 95% native convex overlap with native partial-contact activation; retain useful existing marker.'}
    selected=[]
    for row in classified:
        if row.get('operationally_covered') or row['coverage_state'] not in ('uncovered','partially_covered'):
            continue
        matching=[]
        for anchor,source in anchors:
            if (row['source_provider']!=source['source_provider']
                    or not (_lineage(row)&_lineage(anchor))):
                continue
            a,b=_centre(_vertices(row)),_centre(_vertices(anchor))
            if abs(a[1]-b[1])>1. or math.dist((a[0],a[2]),(b[0],b[2]))>200.:
                continue
            matching.append(source)
        contracts={s['uid']:s for s in matching}
        if len(contracts)==1:
            source=next(iter(contracts.values()))
            row['association']={'rule':'covered sibling in shared authored compound',
                'native_uid':source['uid'],'native_sector':source['sector']}
            selected.append((row,source))
        else:
            row['reason']='no_unambiguous_native_standalone_compound_anchor'
    for row in classified:
        row.pop('_nearby',None)
    return classified,selected


def plan_map_truck_parking(stack, *, map_packages, map_name, ownership_stack=None,
                           game_version='1.61.3.18', work_dir=None):
    """Compose truck-only standalone additions after fuel/car sector edits."""
    original=ownership_stack or stack
    census=_source_census(original,work_dir=work_dir)
    classified,selected=_select_regions(census)
    owners=set(map_packages)
    resources={}; changed=[]; skipped=[]; blockers=[]; generated=set()
    occupied=set(census.get('occupied_uids',()))
    # Prior fuel/car edits may allocate world identities in other sectors.
    # Add every staged identity before selecting any new truck identity.
    seen_staged=set(); overlay=stack
    while hasattr(overlay,'values'):
        for path,data in overlay.values.items():
            if path in seen_staged or not re.fullmatch(_SECTOR,path):continue
            seen_staged.add(path);parsed=parse_sector(data)
            occupied.update(n.uid for n in parsed.nodes)
            occupied.update(i.uid for i in parsed.items)
        overlay=getattr(overlay,'base',None)
    # Reviewed placement geometry supplements general compound rules without
    # turning the general scan into a finite station UID allowlist.
    from . import catalog
    reviewed=getattr(catalog,'reviewed_placement_regions',lambda *_:[])(original,census)
    site_review=catalog.north_platte_reviewed_regions(original)
    required_ids=set()
    if site_review:
        native_matches=[n for n in census['native_standalone'] if n['uid']==site_review['template_trigger_uid']]
        if len(native_matches)!=1:raise ValueError('Required North Platte native trigger missing from census')
        if native_matches[0]['source_provider'] in owners:
            for area in site_review['areas']:
                reviewed.append({**area,'source_uid':site_review['template_trigger_uid'],
                    'source_sector':site_review['source_sector'],'required':True,
                    'source_review':{k:v for k,v in site_review.items() if k!='areas'}})
                required_ids.add(area['id'])
            for row,source in selected:
                if row.get('uid')==site_review['missing_bank_curve_uid']:
                    row['required']=True;required_ids.add(row['id'])
            if not any(r.get('uid')==site_review['missing_bank_curve_uid'] for r,s in selected):
                blockers.append({'reason':'required_North_Platte_long_bank_not_selected'})
    for row in reviewed:
        sources=[s for s in census['native_standalone'] if s['uid']==row['source_uid'] and s['sector']==row['source_sector']]
        if len(sources)!=1:
            blockers.append({'reason':'reviewed_native_source_absent_or_ambiguous','target':row.get('id')})
            continue
        selected.append((row,sources[0]))
    grouped=defaultdict(list)
    for row,source in selected:
        if source['source_provider'] in owners:
            grouped[(source['sector'],source['uid'])].append((row,source))
    for (path,source_uid),pairs in sorted(grouped.items()):
        source=pairs[0][1]
        native_actions=source['actions']
        car_free=[a['token'] for a in native_actions if 'car' not in a['vehicles']]
        if len(car_free)!=1:
            candidates=[a for a,v in census['modes'].items() if 'truck' in v and not v-{'truck','bus'}]
            car_free=[token('hud_parking')] if token('hud_parking') in candidates else sorted(candidates)
        if len(car_free)!=1:
            issue={'sector':path,'native_uid':source_uid,'reason':'no_unambiguous_car_free_effective_rest_action'}
            skipped.append(issue)
            if any(row.get('required') for row,_ in pairs):blockers.append(issue)
            continue
        data=resources.get(path,stack.read(path,max_bytes=_LIMIT))
        layer=path.rsplit('.',1)[0]+'.layer'
        layer_data=resources.get(layer)
        if layer_data is None and layer in stack.resources:
            layer_data=stack.read(layer,max_bytes=_LIMIT)
        areas=[{'id':str(row.get('id',row.get('uid'))),'vertices':_vertices(row)} for row,_ in pairs]
        try:
            result,new_layer,receipt=append_truck_standalone_polygons(data,source_uid=int(source_uid,16),
                areas=areas,action_modes=census['modes'],uid_namespace='ats-road-trip:truck-rest:v1',
                occupied_uids=occupied,action_token=car_free[0],layer_data=layer_data,
                external_nodes=source['_nodes'])
            transaction={path:result}
            if new_layer is not None and new_layer!=layer_data:transaction[layer]=new_layer
            for pair in receipt['visibility_clone_pairs']:
                for other in census['visibility_references'].get(int(source_uid,16),()):
                    if other==path:continue
                    other_data=transaction.get(other,resources.get(other))
                    if other_data is None:other_data=stack.read(other,max_bytes=_LIMIT)
                    transaction[other]=_extend_visibility(other_data,{int(pair['original_uid'],16):int(pair['new_uid'],16)})
            resources.update(transaction)
            generated.update(int(u,16) for u in receipt['generated_uids'])
            occupied.update(generated)
            for (row,_),area in zip(pairs,receipt['areas']):
                changed.append({'id':area['id'],'map':map_name,'source_provider':source['source_provider'],
                    'sector':path,'native_uid':source_uid,'before_native_vertices_xyz':source['vertices'],
                    'source_evidence':row,'emitted':area,'writer':{k:v for k,v in receipt.items() if k!='areas'}})
        except (ValueError,KeyError,OSError) as exc:
            issue={'sector':path,'native_uid':source_uid,'reason':'unsupported_native_writer_contract','detail':str(exc)}
            skipped.append(issue)
            if any(row.get('required') for row,_ in pairs):blockers.append(issue)
    emitted_ids={r['id'] for r in changed}
    for missing in sorted(required_ids-emitted_ids):
        blockers.append({'reason':'required_reviewed_truck_region_not_emitted','id':missing})
    own_banks=[r for r in classified if r.get('source_provider') in owners]
    own_native=[r for r in census['native_standalone'] if r['source_provider'] in owners]
    own_prefabs=[r for r in census['native_prefabs'] if r['source_provider'] in owners]
    summary={'version':1,'experimental':True,'game_version':game_version,'map_name':map_name,
        'improve_truck_parking':True,'native_car_improvement_gate_applied':False,
        'source_basis':'original effective stack; independent of GAS/fuel and existing car support',
        'reviewed_model_sources':census.get('reviewed_model_sources',[]),
        'native_standalone_count':len(own_native),'native_prefab_placement_count':len(own_prefabs),
        'native_prefab_group_count':sum(r['group_count'] for r in own_prefabs),
        'native_prefab_families':dict(Counter(r['descriptor'] for r in own_prefabs)),
        'discovered_painted_banks':len(own_banks),
        'operationally_covered_banks':sum(bool(r.get('operationally_covered')) for r in own_banks),'bank_coverage_counts':dict(Counter(r['coverage_state'] for r in own_banks)),
        'banks':own_banks,'changed_locations':changed,'added_truck_regions':len(changed),
        'added_markers':len(changed),'changed_facilities':len({r['native_uid'] for r in changed}),
        'skipped':skipped,'source_diagnostics':[r for r in census['diagnostics'] if r.get('sector') in original.resources and str(original.resources[r['sector']][0].path) in owners],
        'composed_resource_paths':sorted(resources),
        'coverage':{'complete':not blockers,'blockers':blockers,'original_sector_files_scanned':census['sector_count'],
            'scope':'complete source discovery; safe supported curve-bank rules and explicitly reviewed regions only',
            'limitations':['Native prefab families are inventoried; additive geometry requires a reviewed layout rule.',
                'Ambiguous/unassociated scenery and unknown native contracts remain unchanged.',
                'All original and staged world UIDs are checked before writing; final archive UID/preservation checks remain independent delivery audits.',
                'Runtime rest activation and marker rendering remain unverified.']}}
    if work_dir:
        target=Path(work_dir);target.mkdir(parents=True,exist_ok=True)
        (target/'truck-parking.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    return summary,resources
