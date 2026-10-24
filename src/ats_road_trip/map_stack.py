"""Compose complete source-relative replacements from one original map stack.

The stack is mounted once. Resource ownership remains the original provider,
while staged payloads retain every prior processor edit. Final sector bytes ship
in the replacement above their original owner, including boundary composition.
"""
from contextlib import ExitStack
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import json
import logging
import os
import re

from .archive import Archive
from .bulk_run import _game_directory, _game_packages, _game_version, _profile
from .bulk_fuel import plan_map_fuel, prefab_definitions
from .package import Package, ResourceStack
from .resource_overlay import OverlayResourceStack
from .processors import Processor, ProcessorConfig, CompatibilityPreset, ParkingStrategy
from .petrol_policy import build_policy, DEFAULT_REFERENCE
from .petrol_prices import plan_petrol_prices
from .prefab_contexts import plan_prefab_contexts
from .mod_writer import write_mod
from .mod_artwork import map_icon
from .fuel_selection.batch_workflow import _check_no_generated_fuel_rest

REPO_ROOT = Path(__file__).resolve().parents[2]
_SOURCE_NAMES = ('Reforma', 'ATS Expansion', 'Western Canada Expansion', 'ProMods Canada',
                 'Reforma OtherMaps Patch', 'Western Canada ProMods Connections', 'Alaska Expansion')
_BASE = 'Base Game and DLC'

def _sha(data): return hashlib.sha256(data).hexdigest()

def _json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')

def _snapshot(directory):
    """Scandir-based identity snapshot avoids repeated remote filesystem stats."""
    rows=[]
    def walk(parent):
        with os.scandir(parent) as entries:
            for entry in entries:
                p=Path(entry.path)
                if entry.is_symlink():raise ValueError('Directory input contains a symlink')
                if entry.is_dir(follow_symlinks=False):walk(p)
                elif entry.is_file(follow_symlinks=False):
                    s=entry.stat(follow_symlinks=False);rows.append((p.relative_to(directory).as_posix(),s.st_size,s.st_mtime_ns))
    walk(directory)
    return tuple(sorted(rows))

def _slug(name):return re.sub('[^a-z0-9]+','-',name.lower()).strip('-')

def _owner_index(raw, path, parts, ranks, file_creator):
    if path not in raw.resources:return file_creator[path]
    provider=str(raw.resources[path][0].path)
    exact=[i for i,p in enumerate(parts) if provider in p['source_packages']]
    if exact:return exact[0]
    # Resource-only packages (e.g. ProMods definitions) can provide a country
    # override above their map. Place its repair in the first replacement above
    # that provider rather than shipping an ineffectual lower-priority edit.
    rank=ranks[provider]
    recipient=next((i for i,p in enumerate(parts) if p['rank']>=rank),None)
    if recipient is None:
        raise ValueError('No replacement loads above original resource provider: '+path)
    return recipient

def _prefetch_planning_inputs(raw, work, config):
    """Batch exact descriptors/assets; never reopen a large archive per model."""
    definitions=prefab_definitions(raw)
    paths={(unit.one('prefab_desc','') or '').lstrip('/') for unit,_,_ in definitions.values()}
    if config.parking_strategy is ParkingStrategy.STATION_BAYS:
        from .station_parking.catalog import load_reviewed_catalog
        for model,family in load_reviewed_catalog().items():
            paths.update((model,family['model_geometry']))
            paths.update(family['material_resources'])
    paths &= raw.resources.keys()
    for package in raw.packages:
        selected=sorted(p for p in paths if raw.resources[p][0] is package)
        if selected:
            logging.getLogger(__name__).info('Batch %s exact planning members from %s',len(selected),package.path.name)
            package.prefetch(selected,disk_cache=Path(work)/'package-cache'/_sha(str(package.path).encode())[:12],
                             max_bytes=32*1024*1024)
    return {'paths':sorted(paths),'count':len(paths),'whole_archives_extracted':False}

def plan_stack(raw, game_only, *, parts, config, game_version, work_dir=None):
    """Plan complete source-owner partitions; returns reports and per-part bytes."""
    staged={};creators={};reports=[];transitions=[]
    ranks={str(p.path):i for i,p in enumerate(raw.packages)}
    for index,part in enumerate(parts):
        name=part['map_name'];owners=set(part['source_packages'])
        logging.getLogger(__name__).info('%s: fuel planning',name)
        effective=OverlayResourceStack(raw,staged)
        if Processor.FUEL in config.enabled:
            report,fuel=plan_map_fuel(effective,map_packages=owners,map_name=name,
                fuel_selection=config.fuel_selection,parent_owner_only=True)
        else:
            report,fuel={'coverage':{'complete':True,'blockers':[]},'disabled':True},{}
        # Facilities mode rolls back failed station transactions. Unsafe source
        # sites remain unchanged and visible as incomplete coverage/skips.
        blockers=report.get('coverage',{}).get('blockers',[])
        safe_omissions=(config.fuel_selection.classifier=='facilities' and all(
            b.get('unsupported_unchanged') or b.get('reason')=='Compound-contained fuel needs a container-aware splice'
            for b in blockers))
        if blockers and not safe_omissions:
            raise ValueError(f'{name}: unresolved global fuel structure/ownership blockers')
        for path,data in fuel.items():
            if path.startswith('map/') and path in effective.resources:
                transitions.append(('fuel',path,effective.read(path,max_bytes=128*1024*1024),data))
            if path in staged and not path.startswith('map/') and staged[path]!=data:
                raise ValueError('Conflicting generated private resource '+path)
            staged[path]=data;creators.setdefault(path,index)
        if work_dir:_json(Path(work_dir)/_slug(name)/'fuel.json',report)
        parking={'coverage':{'complete':True,'added_stations':0},'selection_policy':'none'}
        if config.parking_strategy is ParkingStrategy.STATION_BAYS:
            from .station_parking.mapwide import plan_map_station_parking
            logging.getLogger(__name__).info('%s: dedicated station parking',name)
            effective=OverlayResourceStack(raw,staged)
            parking,changes=plan_map_station_parking(effective,map_packages=owners,map_name=name,
                game_version=game_version,ownership_stack=raw,
                improve_existing_car_parking=config.improve_existing_car_parking,
                work_dir=Path(work_dir)/_slug(name)/'parking' if work_dir else None)
            if parking.get('coverage',{}).get('blockers'):
                raise ValueError(f'{name}: dedicated parking returned unsafe output')
        elif config.parking_strategy is ParkingStrategy.TRUCK_AREAS:
            from .rest_stops import plan_rest_stops
            parking,changes=plan_rest_stops(raw,map_packages=owners,map_name=name,
                radius=config.rest_radius,resource_overrides=dict(staged))
            if parking.get('coverage',{}).get('blockers'):
                raise ValueError(f'{name}: truck-area parking coverage is incomplete')
        else:changes={}
        composed=set(parking.get('composed_resource_paths',[]))
        for path,data in changes.items():
            # The full stack emits one authoritative context file after all
            # alias chains are known; per-map context plans remain evidence.
            if re.fullmatch(r'def/data_context(?:\.[^/]+)?\.sii',path):continue
            if path in staged and path not in composed:
                raise ValueError('Parking did not declare composed resource '+path)
            before=staged.get(path)
            if before is None and path in raw.resources:before=raw.read(path,max_bytes=128*1024*1024)
            if path.startswith('map/') and before is not None:transitions.append(('rest',path,before,data))
            staged[path]=data;creators.setdefault(path,index)
        reports.append({'map_name':name,'source_packages':sorted(owners),'fuel':report,'parking':parking})
        if work_dir:_json(Path(work_dir)/_slug(name)/'planning.json',reports[-1])
    # Price repair is independent of facility selection and covers all actual
    # winning original providers, including resource/definition-only packages.
    owners={str(p.path) for p in raw.packages}
    if Processor.FUEL in config.enabled:
        policy,policy_report=build_policy(raw,game_only,target_packages=owners,reference_path=config.petrol_reference)
        prices,price_resources=plan_petrol_prices(raw,target_packages=owners,policy=policy)
    else:
        policy_report={'coverage':{'blockers':[]},'disabled':True}
        prices,price_resources={'coverage':{'blockers':[]},'disabled':True},{}
    if policy_report['coverage']['blockers'] or prices['coverage']['blockers']:
        raise ValueError('Original effective petrol-price planning is incomplete')
    for path,data in price_resources.items():
        if path in staged:raise ValueError('Price collision '+path)
        staged[path]=data;creators[path]=0
    contexts,context_resources=plan_prefab_contexts(raw,staged,transitions,
        source='original-map-stack',map_name='Realistic Map Stack')
    if contexts['coverage']['blockers']:raise ValueError('Global private context lineage is incomplete')
    for path,data in context_resources.items():
        if path in staged:raise ValueError('Context collision '+path)
        staged[path]=data;creators[path]=0
    partitions=[{} for _ in parts]
    for path,data in staged.items():
        index=_owner_index(raw,path,parts,ranks,creators)
        partitions[index][path]=data
    summary={'preset':config.fuel_selection.mode,'fuel_selection':config.fuel_selection.to_dict(),
        'parking_strategy':config.parking_strategy.value,
        'improve_existing_car_parking':config.improve_existing_car_parking,'source_reports':reports,
        'price_policy':policy_report,'prices':prices,'contexts':contexts,
        'resource_count':len(staged),'partition_resources':{
            part['map_name']:sorted(values) for part,values in zip(parts,partitions)},
        'source_coverage_complete':all(not r['fuel'].get('coverage',{}).get('blockers') for r in reports),
        'coverage':{'all_declared_sources_planned':True,'safe_supported_output':True,
                    'unsupported_source_omissions':sum(len(r['fuel'].get('coverage',{}).get('blockers',[])) for r in reports)},
        'in_game_verified':False,'original_baseline_only':True}
    return summary,partitions

def _package_description(part, parts, workflow, preset, revision):
    """Player-facing policy, exact source identities and one current-package mark."""
    name=part['map_name'];realistic=CompatibilityPreset(preset) is CompatibilityPreset.REALISTIC
    source=('Installed original game/map DLC, ATS '+workflow['game_version'] if part['base_companion']
            else ', '.join(Path(p).name for p in part['source_packages']))
    behavior=('Selective public car fueling and broad station parking areas. No generated truck-area car parking or fallback.'
              if realistic else 'Broad added car fueling and qualifying truck-area car access under the existing local proximity rule.')
    contribution=('This source replacement changes country petrol prices only; it adds no station or parking geometry.\n'
                  if name=='Reforma OtherMaps Patch' else '')
    lines=[f'{str(preset.value if hasattr(preset,"value") else preset).upper()} r{revision} | {name} | EXPERIMENTAL',
           'Source: '+source+'.',behavior,contribution.rstrip(),
           'Preserves original car/truck/bus facilities. Unknown fuel sites are provisionally included in realistic mode; unsupported parking areas are skipped.',
           'Native car parking improvements: '+('ON' if workflow.get('improve_existing_car_parking',False) else 'OFF')+'. Parking eligibility never suppresses eligible fueling.',
           'Replace old r9/r10 map fixes and the Alaska-only Dawson r11 with this complete set and its Base Game and DLC companion. Use one policy set at a time.',
           'Disable earlier source fuel/rest fixes and A/B/C/C2/E/F/G parking/fuel experiments.',
           'Keep the separate tank and courier mods unchanged. Prepared for normal career play; existing-save behavior and runtime coverage remain unverified.',
           '', 'Required order, LOWEST to HIGHEST (game/DLC files load automatically):']
    def fix_line(target):
        marker=' (THIS MOD)' if target['map_name']==name else ''
        return f'{str(preset.value if hasattr(preset,"value") else preset).upper()} r{revision} replacement for '+target['map_name']+marker
    lines += [fix_line(parts[0])]
    game_sources=set(parts[0]['source_packages'])
    for path in workflow['packages_low_to_high']:
        if path in game_sources:continue
        lines.append(Path(path).name+' (original source/resource)')
        for target in parts[1:]:
            if path in target['source_packages']:lines.append(fix_line(target))
    return '\n'.join(line for line in lines if line is not None)+'\n'

def run_map_stack(*, packages, preset='realistic', game_dir=None, extractor=None,
                  generate=False, experimental=False, revision=12,run_id=None,
                  improve_existing_car_parking=False):
    """Mount an explicit original low-to-high stack and produce all replacements."""
    if generate and not experimental:raise ValueError('Generation requires --experimental')
    if type(revision)is not int or revision<10:raise ValueError('Replacement revision must be at least10')
    stamp=run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',stamp):raise ValueError('Invalid run timestamp')
    preset=CompatibilityPreset(preset);config=ProcessorConfig.from_preset(preset,
        improve_existing_car_parking=improve_existing_car_parking)
    work=REPO_ROOT/'local_outputs/work'/stamp/f'{preset.value}-map-stack'
    generated=REPO_ROOT/'local_outputs/generated'/stamp
    if work.exists():raise FileExistsError('Use a new run timestamp')
    work.mkdir(parents=True);previous=Archive._work_root;Archive.configure_work_root(work)
    try:
        installed=_game_directory(game_dir);version=_game_version(installed,extractor)
        game_paths,dlcs=_game_packages(installed)
        explicit=[Path(p).expanduser().resolve() for p in packages]
        paths=[*game_paths,*explicit]
        if not explicit or len(set(paths))!=len(paths):raise ValueError('Missing or duplicate original packages')
        if len({p.name for p in paths})!=len(paths):raise ValueError('Duplicate original package basenames')
        identities={p:(p.stat().st_size,p.stat().st_mtime_ns) for p in paths}
        snapshots={p:_snapshot(p) for p in paths if p.is_dir()}
        with ExitStack() as manager:
            mounted=[]
            for index,path in enumerate(paths,1):
                logging.getLogger(__name__).info('Original package %s/%s %s',index,len(paths),path.name)
                package=manager.enter_context(Package(path,extractor=extractor,dlcs=dlcs))
                if path in explicit:_check_no_generated_fuel_rest(package)
                mounted.append(package)
            raw=ResourceStack(mounted);game=ResourceStack(mounted[:len(game_paths)])
            parts=[{'map_name':_BASE,'source_packages':[str(p) for p in game_paths],
                    'rank':len(game_paths)-1,'base_companion':True}]
            for rank,path in enumerate(paths):
                label,_=_profile(path)
                if path in explicit and label in _SOURCE_NAMES:
                    parts.append({'map_name':label,'source_packages':[str(path)],'rank':rank,'base_companion':False})
            if {p['map_name'] for p in parts[1:]}!=set(_SOURCE_NAMES) or len(parts)!=8:
                raise ValueError('Declare exactly the seven supported original map sources plus resources')
            prefetched=_prefetch_planning_inputs(raw,work,config)
            _json(work/'prefetch.json',prefetched)
            report,values=plan_stack(raw,game,parts=parts,config=config,game_version=version,work_dir=work)
            # Identity checks cover the complete declared source set. Relevant
            # visual/geometry byte pins are also retained by the parking reports.
            for path,identity in identities.items():
                st=path.stat()
                if (st.st_size,st.st_mtime_ns)!=identity:raise ValueError('Original input changed: '+str(path))
            for path,snapshot in snapshots.items():
                if _snapshot(path)!=snapshot:raise ValueError('Original directory package changed')
            workflow={'game_version':version,'run_id':stamp,'preset':preset.value,
                'packages_low_to_high':[str(p) for p in paths],
                'archive_identities':[{'path':str(p),'size':v[0],'mtime_ns':v[1]} for p,v in identities.items()],
                'directory_snapshots':[{'path':str(p),'sha256':_sha(json.dumps(s).encode()),'files':len(s)} for p,s in snapshots.items()],
                'parts':parts,'improve_existing_car_parking':config.improve_existing_car_parking,
                'profile_modified':False,'work_dir':str(work)}
            result={'status':'analyzed','report_path':str(work/'audit.json'),'workflow':workflow,'planner':report,'outputs':[]}
            if generate:
                for index,(part,resources) in enumerate(zip(parts,values)):
                    label=part['map_name'];slug=_slug(label)
                    if not resources:
                        resources={f'road_trip_coverage/{slug}.json':json.dumps({'source':label,
                            'reason':'No additional modifications needed in the effective original stack',
                            'preset':preset.value},sort_keys=True).encode()}
                    output=generated/f'{preset.value}-road-trip-map-fix-{slug}-1.61-r{revision}-experimental.scs'
                    description=_package_description(part,parts,workflow,preset,revision)
                    icon=None if part['base_companion'] else map_icon(REPO_ROOT,label,('fuel','rest'))
                    if isinstance(icon,(str,Path)):icon=Path(icon).read_bytes()
                    embedded={'analysis':'complete_map_stack_replacement','processors_enabled':['fuel','rest'],
                        'preset':preset.value,'parking_strategy':config.parking_strategy.value,
                        'improve_existing_car_parking':config.improve_existing_car_parking,
                        'map_name':label,'source_packages':part['source_packages'],
                        'source_report':report['source_reports'][index],
                        'prices':report['prices'],'contexts':report['contexts'],
                        'original_package_order':workflow['packages_low_to_high'],
                        'in_game_verified':False,'complete_set_required':True}
                    written=write_mod(output,resources,embedded,game_version=version,map_name=label,
                        revision=revision,variant_label=f'{preset.value.upper()} r{revision}',
                        fix_topics=('fuel','rest'),description=description,icon=icon)
                    result['outputs'].append({'map_name':label,'path':str(output),'sha256':_sha(output.read_bytes()),
                        'bytes':output.stat().st_size,'resource_count':len(resources),'metadata':written['package_metadata']})
                result['status']='generated'
            _json(work/'audit.json',result)
            return result
    except Exception as exc:
        if not (work/'audit.json').exists():_json(work/'audit.json',{'status':'failed','error':str(exc)})
        raise
    finally:Archive.configure_work_root(previous)
