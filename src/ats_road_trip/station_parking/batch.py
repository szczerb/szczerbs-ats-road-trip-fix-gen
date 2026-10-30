"""Compose an explicit finite station list from one unchanged effective stack.

Each individual planner emits a complete sector. Combining dictionary outputs
would discard earlier stations in the same sector, so this module reapplies
only independently checked eight-byte prefab-model substitutions to the exact
shared source bytes. Existing map fixes stay mounted below the new overlay.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import re
import struct

from ..bulk_fuel import _alias_definition, prefab_definitions
from ..local_fuel import token
from ..map_sector import parse_sector
from ..package import virtual_path
from ..prefab_contexts import _contexts
from ..sii import parse_units
from .validation import validate_config
from .trigger import append_car_parking_polygon

MAX_STATIONS = 64
_SITE_ID = re.compile(r'P(?:0[1-9]|[1-9][0-9])')
_SLUG = re.compile(r'[a-z][a-z0-9-]{0,63}')
_LABEL = re.compile(r'[A-Za-z][A-Za-z0-9 ._-]{0,63}')
_VERSION = re.compile(r'1\.61(?:\.\d+)*')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _labels(batch_id, map_name, game_version):
    if not isinstance(batch_id, str) or not _SLUG.fullmatch(batch_id):
        raise ValueError('Batch ID must be a short lowercase slug')
    if not isinstance(map_name, str) or not _LABEL.fullmatch(map_name):
        raise ValueError('Batch map_name must be a short printable label')
    if not isinstance(game_version, str) or not _VERSION.fullmatch(game_version):
        raise ValueError('Batch must pin an ATS 1.61 game_version')


def validate_manifest(manifest):
    """Validate filesystem-independent manifest fields; return a sorted copy.

    Paths are resolved and read only by the workflow. Sources are exact archive
    basenames which that workflow must resolve uniquely in its mounted stack.
    Site IDs are explicit review labels, not a discovery or density policy.
    """
    required = {'schema_version', 'processor', 'batch_id', 'map_name', 'game_version', 'stations'}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError('Batch manifest has missing or unknown fields')
    if type(manifest['schema_version']) is not int or manifest['schema_version'] != 1 or manifest['processor'] != 'station_parking_batch':
        raise ValueError('Expected station_parking_batch manifest schema 1')
    _labels(manifest['batch_id'], manifest['map_name'], manifest['game_version'])
    stations = manifest['stations']
    if not isinstance(stations, list) or not 1 <= len(stations) <= MAX_STATIONS:
        raise ValueError(f'Batch must contain an explicit list of 1..{MAX_STATIONS} stations')
    seen_ids, seen_configs = set(), set()
    for station in stations:
        if not isinstance(station, dict) or set(station) != {'site_id', 'source_package', 'config', 'mesh'}:
            raise ValueError('Batch station has missing or unknown fields')
        site_id = station['site_id']
        if not isinstance(site_id, str) or not _SITE_ID.fullmatch(site_id) or site_id in seen_ids:
            raise ValueError('Batch site_id must be unique and use P01..P99')
        seen_ids.add(site_id)
        for label in ('config', 'mesh'):
            path = station[label]
            if not isinstance(path, str) or not path.strip() or '\x00' in path:
                raise ValueError(f'Batch {label} must be a nonempty filesystem path')
        if station['config'] in seen_configs:
            raise ValueError('Batch must not repeat a station config path')
        seen_configs.add(station['config'])
        source = station['source_package']
        if not isinstance(source, str) or not source.strip() or source in ('.', '..') or any(c in source for c in '/\\\x00'):
            raise ValueError('Batch source_package must be an exact archive basename')
    result = deepcopy(manifest)
    result['stations'].sort(key=lambda station: station['site_id'])
    return result


def _complete(report, label):
    coverage = report.get('coverage') if isinstance(report, dict) else None
    if not isinstance(coverage, dict) or coverage.get('complete') is not True or coverage.get('blockers') != []:
        raise ValueError(f'{label} has partial or blocked coverage')


def compose_station_plans(stack, plans, *, batch_id, map_name, game_version):
    """Return ``(report, resources)`` for complete plans against ``stack``.

    ``plans`` contains ``(site_id, planner_report, resource_dict)`` tuples. Every
    site must add one station, with its own private descriptor. All validation
    completes before returning any resources; caller-owned plans are untouched.
    Reordering plans produces identical resources and report ordering.
    """
    _labels(batch_id, map_name, game_version)
    plans = list(plans)
    if not 1 <= len(plans) <= MAX_STATIONS:
        raise ValueError(f'Batch requires 1..{MAX_STATIONS} plans')
    if any(not isinstance(row, (tuple, list)) or len(row) != 3 for row in plans):
        raise ValueError('Each batch plan must contain site_id, report, resources')
    ids = [row[0] for row in plans]
    if any(not isinstance(site, str) or not _SITE_ID.fullmatch(site) for site in ids) or len(set(ids)) != len(ids):
        raise ValueError('Batch plan site IDs must be unique P01..P99 identifiers')
    definitions = prefab_definitions(stack)
    baselines, patches, additions = {}, {}, {}
    placements, station_ids, aliases, alias_tokens = set(), set(), set(), set()
    _, existing_context_names, _ = _contexts(stack)
    unit_names = {('data_context', name) for name in existing_context_names}
    sites = []
    for site_id, report, resources in sorted(plans, key=lambda row: row[0]):
        _complete(report, site_id)
        if report.get('processor') != 'station_parking':
            raise ValueError(f'{site_id}: expected a station_parking report')
        config = validate_config(report.get('configuration'))
        if config['game_version'] != game_version or report.get('station_id') != config['station_id'] or report.get('map_name') != config['map_name'] or report.get('method') != config['method']:
            raise ValueError(f'{site_id}: planner/configuration identity mismatch')
        if config['station_id'] in station_ids:
            raise ValueError('Batch repeats a station ID')
        station_ids.add(config['station_id'])
        if not isinstance(resources, dict) or not resources:
            raise ValueError(f'{site_id}: no changes; batch requires a new station at every site')
        if any(not isinstance(path, str) or virtual_path(path) != path or type(data) is not bytes for path, data in resources.items()):
            raise ValueError(f'{site_id}: resources must be canonical virtual paths and bytes')
        sector_path, uid = config['sector'], int(config['prefab_uid'], 16)
        if uid in placements:
            raise ValueError('Batch repeats a placement UID')
        placements.add(uid)
        if sector_path not in baselines:
            baselines[sector_path] = stack.read(sector_path, max_bytes=64 * 1024 * 1024)
        baseline = baselines[sector_path]
        if _sha(baseline) != config['fingerprints']['sector']:
            raise ValueError(f'{site_id}: effective sector source SHA-256 drift')
        prefabs = [p for p in parse_sector(baseline).prefabs if p.uid == uid]
        if len(prefabs) != 1:
            raise ValueError(f'{site_id}: selected placement is absent or ambiguous')
        prefab = prefabs[0]
        entry = definitions.get(prefab.details['model'])
        if entry is None:
            raise ValueError(f'{site_id}: selected placement definition is missing')
        unit, block, definition = entry
        descriptor = (unit.one('prefab_desc', '') or '').lstrip('/')
        model = (unit.one('model_desc', '') or '').lstrip('/')
        source = report.get('source', {})
        expected_source = {'sector': sector_path, 'prefab_uid': hex(uid), 'prefab': unit.name,
                           'descriptor': descriptor, 'definition': definition, 'model': model}
        if any(source.get(key) != value for key, value in expected_source.items()):
            raise ValueError(f'{site_id}: planner source identity differs from effective stack')
        if model.removesuffix('.pmd') + '.pmg' != config['model_geometry']:
            raise ValueError(f'{site_id}: effective model differs from configuration')
        pins = {descriptor: config['fingerprints']['descriptor'],
                config['model_geometry']: config['fingerprints']['model_geometry']}
        if config['schema_version'] == 2:
            pins[model] = config['fingerprints']['model_definition']
            pins.update(config['material_resources'])
        for path, digest in pins.items():
            if _sha(stack.read(path, max_bytes=64 * 1024 * 1024)) != digest:
                raise ValueError(f'{site_id}: effective resource SHA-256 drift: {path}')
        if config['schema_version'] == 2:
            declared = report.get('effective_inputs')
            expected_paths = {sector_path, definition, descriptor, model, config['model_geometry']}
            if not isinstance(declared, list) or len(declared) != len(expected_paths) or any(not isinstance(row, dict) for row in declared):
                raise ValueError(f'{site_id}: invalid effective input report')
            if {row.get('path') for row in declared} != expected_paths:
                raise ValueError(f'{site_id}: mismatched effective input report')
            for row in declared:
                path = row['path']
                if row.get('sha256') != _sha(stack.read(path, max_bytes=64 * 1024 * 1024)) or row.get('provider') != stack.resources[path][1].package:
                    raise ValueError(f'{site_id}: effective input report differs from stack')
        alias = report.get('private_alias')
        if not isinstance(alias, str) or not re.fullmatch(r'rsp[0-9a-f]{8}', alias):
            raise ValueError(f'{site_id}: invalid private station alias')
        if alias in aliases or token(alias) in alias_tokens or token(alias) in definitions:
            raise ValueError(f'{site_id}: private alias collision')
        aliases.add(alias)
        alias_tokens.add(token(alias))
        private = 'prefab/rtfix/' + alias + '.ppd'
        defpath = 'def/world/prefab.' + alias + '.sii'
        context = report.get('context_preservation')
        _complete(context, site_id + ' context preservation')
        context_path = context.get('generated_resource')
        if context_path is not None and (not isinstance(context_path, str) or not re.fullmatch(r'def/data_context\.[^/]+\.sii', context_path) or virtual_path(context_path) != context_path):
            raise ValueError(f'{site_id}: invalid generated context resource path')
        allowed = {sector_path, private, defpath} | ({context_path} if context_path is not None else set())
        if set(resources) != allowed:
            raise ValueError(f'{site_id}: missing or unexpected planned resources')
        surface_checks = report.get('model_surface_checks')
        if not isinstance(surface_checks, dict):
            raise ValueError(f'{site_id}: missing selected polygon surface checks')
        expected_ppd, expected_writer = append_car_parking_polygon(
            stack.read(descriptor, max_bytes=64 * 1024 * 1024), surface_checks.get('vertices_xyz'))
        if resources[private] != expected_ppd or report.get('writer') != expected_writer:
            raise ValueError(f'{site_id}: private descriptor differs from source-preserving native car append')
        expected_alias = 'rsp' + _sha((config['station_id'] + '\0' + _sha(resources[private])).encode())[:8]
        if alias != expected_alias:
            raise ValueError(f'{site_id}: private alias does not match station descriptor')
        if resources[defpath] != _alias_definition(block, unit.name, alias, private):
            raise ValueError(f'{site_id}: private definition differs from source-preserving clone')
        start, end = prefab.offset + 57, prefab.offset + 65
        changed = resources[sector_path]
        if len(changed) != len(baseline) or changed[:start] != baseline[:start] or changed[end:] != baseline[end:]:
            raise ValueError(f'{site_id}: unexpected sector bytes outside placement model token')
        replacement = struct.pack('<Q', token(alias))
        if changed[start:end] != replacement or changed == baseline:
            raise ValueError(f'{site_id}: sector has no valid new alias substitution')
        expected_change = {'path': sector_path, 'source_sha256': _sha(baseline),
                           'output_sha256': _sha(changed), 'allowed_changed_byte_range': [start, end]}
        if report.get('changed_sectors') != [expected_change]:
            raise ValueError(f'{site_id}: sector change report differs from checked bytes')
        sector_patches = patches.setdefault(sector_path, [])
        if any(start < other_end and other_start < end for other_start, other_end, _ in sector_patches):
            raise ValueError(f'{site_id}: overlapping station sector patches')
        sector_patches.append((start, end, replacement))
        for path in sorted(allowed - {sector_path}):
            data = resources[path]
            if path in stack.resources:
                raise ValueError(f'{site_id}: new resource would overwrite effective baseline: {path}')
            if path in additions:
                if additions[path] != data or path != context_path:
                    raise ValueError(f'{site_id}: conflicting nonsector resource: {path}')
                continue
            if path.endswith('.sii'):
                generated_units = parse_units(data.decode('utf-8-sig'), source=path)
                if path == context_path and (not generated_units or any(unit.kind != 'data_context' or tuple(unit.values('target_data')) != ('prefab.' + alias,) for unit in generated_units)):
                    raise ValueError(f'{site_id}: context resources must classify only the selected private alias')
                for generated in generated_units:
                    identity = (generated.kind, generated.name)
                    if identity in unit_names:
                        raise ValueError(f'{site_id}: generated definition unit collision')
                    unit_names.add(identity)
            additions[path] = data
        sites.append({'site_id': site_id, 'station_id': config['station_id'],
                      'map_name': config['map_name'], 'sector': sector_path, 'prefab_uid': hex(uid),
                      'private_alias': alias, 'planner': deepcopy(report)})
    composed = dict(additions)
    sectors = []
    for path in sorted(baselines):
        before = baselines[path]
        after = bytearray(before)
        for start, end, replacement in sorted(patches[path]):
            after[start:end] = replacement
        composed[path] = bytes(after)
        sectors.append({'path': path, 'source_sha256': _sha(before), 'output_sha256': _sha(composed[path]),
                        'allowed_changed_byte_ranges': [[start, end] for start, end, _ in sorted(patches[path])]})
    report = {'schema_version': 1, 'processor': 'station_parking_batch', 'batch_id': batch_id,
              'map_name': map_name, 'game_version': game_version, 'experimental': True,
              'in_game_verified': False, 'coverage': {'complete': True, 'blockers': []},
              'station_count': len(sites), 'sites': sites, 'changed_sectors': sectors,
              'composition': 'Source-byte guarded disjoint placement model-token substitutions',
              'baseline_policy': 'Existing effective resources remain dependencies below this overlay; no baseline payload is copied.',
              'limitations': ['Explicit finite station list only; no whole-map coverage or distance/density policy.',
                             'Physical access, NPC occupancy, fatigue, icons and reload require manual validation.']}
    return report, dict(sorted(composed.items()))
