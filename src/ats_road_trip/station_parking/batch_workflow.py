"""One explicit station-parking overlay over a pinned effective package stack."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from ..archive import Archive
from ..bulk_run import _game_directory, _game_packages, _game_version
from ..map_sector import parse_sector
from ..mod_writer import write_mod
from ..package import Package, ResourceStack
from .batch import validate_manifest, compose_station_plans
from .diagnostics import render_station_plan
from .planner import plan_station_parking
from .workflow import (REPO_ROOT, _load_config, _sha256_file, _sha256_bytes,
                       _directory_snapshot, _directory_snapshot_report,
                       _verify_input_identities, _write_json)


def neighboring_sector_paths(stack, path):
    """Declared 3x3 base/aux halo; this is a bounded inspection, not a world proof."""
    match = re.fullmatch(r'(map/[^/]+/sec)([+-]\d{4})([+-]\d{4})\.(?:base|aux)', path)
    if not match:
        raise ValueError('Batch station requires a standard signed sector path')
    prefix, sx, sz = match.groups()
    return sorted(p for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                  for suffix in ('base', 'aux')
                  if (p := f'{prefix}{int(sx)+dx:+05d}{int(sz)+dz:+05d}.{suffix}') in stack.resources)


def _metadata(manifest, revision):
    count = len(manifest['stations'])
    label = f'F BATCH r{revision}'
    return {
        'display_name': f"{label} | szczerb's Road Trip Station Parking - {count} sites - Experimental",
        'description': (
            f'{label} — {count} explicitly selected station parking sites; one combined test mod.\n'
            'Enable all sites together with this single package. Disable previous A/B/C/E geometry experiments.\n'
            'Place above all declared source-map fixes and their source maps; keep those standard fixes enabled.\n'
            'Retain separate N2 above the active background map and other map-data providers.\n'
            'Original effective fuel/rest actions, service records and unselected placements are preserved.\n'
            'Experimental ATS 1.61 / Road Trip Ford; physical access, intuitive activation, fatigue and reload await gameplay tests.\n'
            'Use the accompanying P01/P02 itinerary and plans. Source versions and exact stack are pinned in the audit.\n'
            + 'Selected source archives: ' + ', '.join(sorted({s['source_package'] for s in manifest['stations']})) + '.\n'
        ),
    }


def run_station_parking_batch(manifest_path, *, packages, game_dir=None, extractor=None,
                              generate=False, revision=1, experimental=False, run_id=None):
    """Plan every site against one effective baseline, then compose guarded edits.

    Explicit packages include normal map fixes in their real low-to-high order.
    Unlike the single-station fuel-baseline workflow, no baseline is moved to the
    end or copied wholesale: only reviewed sector patches and new aliases ship.
    """
    if generate and not experimental:
        raise ValueError('Generation requires --experimental; no candidate is verified in game')
    if type(revision) is not int or revision < 1:
        raise ValueError('Batch revision must be a positive integer')
    manifest_path = Path(manifest_path).expanduser().resolve()
    manifest_bytes = manifest_path.read_bytes()
    manifest_digest = _sha256_bytes(manifest_bytes)
    manifest = validate_manifest(json.loads(manifest_bytes.decode('utf-8')))
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('run_id must use YYYY-MM-DD_HH-MM-SS')
    work = REPO_ROOT / 'local_outputs/work' / stamp / manifest['batch_id']
    output = REPO_ROOT / 'local_outputs/generated' / stamp / f'f-batch-r{revision}-{manifest["batch_id"]}-ats-1.61-experimental.scs'
    if work.exists() or (generate and output.exists()):
        raise FileExistsError('Batch audit/output exists; choose a new run_id')
    work.mkdir(parents=True)
    audit_path = work / 'audit.json'
    previous_work = Archive._work_root
    Archive.configure_work_root(work)
    audit = {'status': 'started', 'analysis_only': not generate, 'in_game_verified': False,
             'generated_mod_count': 0, 'report_path': str(audit_path),
             'workflow': {'work_dir': str(work), 'run_id': stamp}, 'sites': []}
    try:
        installed = _game_directory(game_dir)
        version = _game_version(installed, extractor)
        if version != manifest['game_version']:
            raise ValueError('Installed ATS version differs from batch manifest')
        game_paths, dlcs = _game_packages(installed)
        game_paths = [Path(p).resolve() for p in game_paths]
        explicit = [Path(p).expanduser().resolve() for p in packages]
        if any(not p.is_file() and not p.is_dir() for p in explicit):
            raise ValueError('Every explicit package must exist')
        if len(set(explicit)) != len(explicit) or set(explicit) & set(game_paths):
            raise ValueError('Do not repeat explicit or installed game packages')
        paths = [*game_paths, *explicit]
        by_name = {}
        for path in paths:
            by_name.setdefault(path.name, []).append(path)
        loaded = []
        pins = {manifest_path: manifest_digest}
        for site in manifest['stations']:
            source_matches = by_name.get(site['source_package'], [])
            if len(source_matches) != 1 or not source_matches[0].is_file():
                raise ValueError('Each source_package must resolve to exactly one mounted source archive')
            resolve = lambda name: (manifest_path.parent / Path(name).expanduser()).resolve()
            config_path, mesh_path = resolve(site['config']), resolve(site['mesh'])
            config_digest = _sha256_file(config_path)
            config = _load_config(config_path)
            pins[config_path] = config_digest
            if config['schema_version'] != 2 or 'base_fix' in config['fingerprints']:
                raise ValueError('Batch requires effective schema-2 configs without the single-station fuel-only base_fix')
            if config['game_version'] != version:
                raise ValueError('Site game version differs from batch')
            pit_path = mesh_path.with_suffix('.pit')
            for path in (mesh_path, pit_path):
                if not path.is_file():
                    raise ValueError(f'Missing batch config/converted model input: {path}')
                pins[path] = _sha256_file(path)
            source = source_matches[0]
            if source not in pins:
                pins[source] = _sha256_file(source)
            if pins[source] != config['fingerprints']['source_archive']:
                raise ValueError('Site source archive SHA-256 drift')
            if pins[mesh_path] != config['fingerprints']['mesh'] or pins[pit_path] != config['fingerprints']['mesh_state']:
                raise ValueError('Site converted model/state SHA-256 drift')
            loaded.append((site, config, mesh_path.read_text(encoding='utf-8-sig'),
                           pit_path.read_text(encoding='utf-8-sig'), source))
        # All explicit archive bytes, including standard r9 fixes, are pinned.
        for path in explicit:
            if path.is_file() and path not in pins:
                pins[path] = _sha256_file(path)
        snapshots = {p: _directory_snapshot(p) for p in paths if p.is_dir()}
        version_path = installed / ('version.sii' if (installed / 'version.sii').is_file() else 'version.scs')
        identities = {p: (p.stat().st_size, p.stat().st_mtime_ns)
                      for p in dict.fromkeys([*paths, *pins, version_path])}
        audit['workflow'].update({'packages_low_to_high': [str(p) for p in paths],
            'game_version': version, 'manifest': str(manifest_path),
            'sha256_inputs': {str(p): h for p, h in sorted(pins.items())},
            'directory_package_snapshots': [_directory_snapshot_report(p, s) for p, s in sorted(snapshots.items())]})
        plans = []
        with ExitStack() as manager:
            mounted = [manager.enter_context(Package(p, extractor=extractor, dlcs=dlcs)) for p in paths]
            stack = ResourceStack(mounted)
            neighbors = {config['sector']: neighboring_sector_paths(stack, config['sector'])
                         for _, config, _, _, _ in loaded}
            selected_paths = sorted({p for group in neighbors.values() for p in group})
            dependency_paths=set(selected_paths)
            for _,config,_,_,_ in loaded:
                dependency_paths.update(config['material_resources'])
                dependency_paths.add(config['model_geometry'])
                dependency_paths.add(config['model_geometry'][:-4]+'.pmd')
            for package in mounted:
                subset = [p for p in sorted(dependency_paths) if p in stack.resources and stack.resources[p][0] is package]
                if subset:
                    package.prefetch(subset, disk_cache=work / 'resource-cache' / hashlib.sha256(str(package.path).encode()).hexdigest()[:12],max_bytes=128*1024*1024)
            sector_data = {p: stack.read(p, max_bytes=64*1024*1024) for p in selected_paths}
            checked_resource_pins = {p: _sha256_bytes(data) for p, data in sector_data.items()}
            from .local_context import load_local_context
            for site, config, mesh, pit, source in loaded:
                uid = int(config['prefab_uid'], 16)
                parsed = parse_sector(sector_data[config['sector']])
                prefab = next((p for p in parsed.prefabs if p.uid == uid), None)
                if prefab is None:
                    raise ValueError('Selected batch UID missing from effective sector')
                nodes = {n.uid: n for n in parsed.nodes}
                anchor = nodes[prefab.details['nodes'][0]].position
                context = load_local_context(stack, {p: sector_data[p] for p in neighbors[config['sector']]},
                                             uid, (anchor[0], anchor[2]))
                report, resources = plan_station_parking(stack, config, mesh, map_package=str(source),
                    game_version=version, mesh_state_text=pit, local_context=context)
                site_dir = work / site['site_id']
                site_dir.mkdir()
                (site_dir / 'plan.svg').write_text(render_station_plan(report), encoding='utf-8')
                _write_json(site_dir / 'report.json', report)
                audit['sites'].append({'site_id': site['site_id'], 'config': config,
                    'plan_svg': str(site_dir / 'plan.svg'), 'report_path': str(site_dir / 'report.json'),
                    'coverage': report.get('coverage'), 'selected': report.get('selected'),
                    'private_alias': report.get('private_alias'), 'state': report.get('state')})
                plans.append((site['site_id'], report, resources))
                for item in report.get('effective_inputs', []) + report.get('effective_material_resources', []):
                    checked_resource_pins[item['path']] = item['sha256']
                for item in context.get('source_resources', []):
                    checked_resource_pins[item['path']] = item['sha256']
            blockers = [{'site_id': sid, 'coverage': report.get('coverage')}
                        for sid, report, resources in plans
                        if report.get('coverage', {}).get('complete') is not True
                        or report.get('coverage', {}).get('blockers') or not resources]
            if blockers:
                _verify_input_identities(identities, pins, snapshots)
                audit.update(status='blocked' if generate else 'reported_partial',
                             planner={'coverage': {'complete': False, 'blockers': blockers}})
                _write_json(audit_path, audit)
                return audit
            batch_report, resources = compose_station_plans(stack, plans, batch_id=manifest['batch_id'],
                map_name=manifest['map_name'], game_version=version)
            _verify_input_identities(identities, pins, snapshots)
            # Re-read effective dependencies, not only archive metadata. This
            # includes directory-hosted models/materials and local context PPDs.
            for path, expected in sorted(checked_resource_pins.items()):
                provider, resource = stack.resources[path]
                if provider.path.is_dir():
                    physical = provider.path / resource.physical_path
                    if physical.is_symlink() or not physical.resolve().is_relative_to(provider.path.resolve()):
                        raise ValueError('Directory dependency escaped its provider')
                    actual = _sha256_file(physical)
                else:
                    actual = _sha256_bytes(stack.read(path, max_bytes=128*1024*1024))
                if actual != expected:
                    raise ValueError('Effective batch resource SHA-256 drift before packaging: ' + path)
            batch_report['manifest'] = manifest
            batch_report['stack_basenames_low_to_high'] = [p.name for p in paths]
            batch_report['explicit_archive_sha256'] = {p.name: pins[p] for p in explicit if p.is_file()}
            audit['planner'] = batch_report
            audit['workflow']['effective_resource_sha256'] = checked_resource_pins
            if generate:
                metadata = _metadata(manifest, revision)
                metadata['description'] += '\nRequired explicit packages, LOW TO HIGH:\n' + '\n'.join(p.name for p in explicit) + '\nF BATCH (THIS MOD)\nKeep separate N2 above the active background map.\n'
                written = write_mod(output, resources, batch_report, game_version=version,
                                    revision=revision, category='map', **metadata)
                audit.update(status='generated', generated_mod_count=1, output=str(output), written_report=written)
            else:
                audit['status'] = 'reported'
        _write_json(audit_path, audit)
        return audit
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        audit.update(status='failed', error=str(exc))
        if not audit_path.exists():
            _write_json(audit_path, audit)
        raise
    finally:
        Archive.configure_work_root(previous_work)
