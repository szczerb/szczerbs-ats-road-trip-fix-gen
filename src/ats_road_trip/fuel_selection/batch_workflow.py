"""Run a finite, source-pinned fuel-policy comparison over selected placements.

This is a bounded test workflow: it does not claim map-wide coverage and does
not discover extra targets outside the manifest. Original map packages stay in
their declared low-to-high order beneath the generated overlay.
"""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from ..archive import Archive
from ..bulk_fuel import plan_map_fuel
from ..bulk_run import _game_directory, _game_packages, _game_version
from ..map_sector import parse_sector
from ..mod_writer import write_mod
from ..package import Package, ResourceStack
from ..petrol_policy import DEFAULT_REFERENCE, build_policy
from ..petrol_prices import plan_petrol_prices
from ..prefab_contexts import plan_prefab_contexts
from . import FuelSelectionConfig


REPO_ROOT = Path(__file__).resolve().parents[3]
_SECTOR = re.compile(r'map/[^/]+/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)\Z')
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')
_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
_SITE_ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,31}\Z')
_VERSION = re.compile(r'1\.61(?:\.\d+)+\Z')
_FIX_REPORT = 'road_trip_fix_report.json'


def _unique_json(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f'Duplicate JSON field {key}')
        value[key] = item
    return value


def validate_manifest(value: object) -> dict:
    """Validate schema-1 bounded site and independent price target lists."""
    required = {'schema_version', 'batch_id', 'game_version', 'sites', 'price_packages'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('Fuel selection batch manifest has missing or unknown fields')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('Fuel selection batch requires schema_version 1')
    if not isinstance(value['batch_id'], str) or not _SLUG.fullmatch(value['batch_id']):
        raise ValueError('batch_id must be a lowercase hyphenated slug')
    if not isinstance(value['game_version'], str) or not _VERSION.fullmatch(value['game_version']):
        raise ValueError('game_version must be an exact ATS 1.61 version')
    sites = value['sites']
    if not isinstance(sites, list) or not 1 <= len(sites) <= 32:
        raise ValueError('Fuel selection batch must contain 1..32 explicitly selected sites')
    seen_ids, seen_uids = set(), set()
    for site in sites:
        fields = {'id', 'sector', 'sector_sha256', 'source_package', 'prefab_uid'}
        if not isinstance(site, dict) or set(site) != fields:
            raise ValueError('Fuel batch site has missing or unknown fields')
        if not isinstance(site['id'], str) or not _SITE_ID.fullmatch(site['id']) or site['id'] in seen_ids:
            raise ValueError('Fuel batch site IDs must be unique simple labels')
        seen_ids.add(site['id'])
        if (not isinstance(site['sector'], str) or not _SECTOR.fullmatch(site['sector'])
                or site['sector'].split('/')[1] in ('.', '..')):
            raise ValueError('Fuel batch site sector must be a normalized map sector resource path')
        if not isinstance(site['sector_sha256'], str) or not _SHA256.fullmatch(site['sector_sha256']):
            raise ValueError('sector_sha256 must be lowercase SHA-256 hex')
        source = site['source_package']
        if (not isinstance(source, str) or not source or source in ('.', '..')
                or Path(source).name != source or any(c in source for c in '/\\\x00')):
            raise ValueError('source_package must be an exact archive basename')
        uid = site['prefab_uid']
        if not isinstance(uid, str) or not re.fullmatch(r'0x[0-9a-f]{1,16}', uid):
            raise ValueError('prefab_uid must be a lowercase hexadecimal uint64 string')
        numeric_uid = int(uid, 16)
        if numeric_uid == 0 or numeric_uid in seen_uids:
            raise ValueError('Fuel batch prefab UIDs must be unique positive uint64 values')
        seen_uids.add(numeric_uid)
    prices = value['price_packages']
    if not isinstance(prices, list):
        raise ValueError('price_packages must be an explicit JSON array of original archive basenames')
    seen_prices = set()
    for name in prices:
        if (not isinstance(name, str) or not name or name in ('.', '..')
                or Path(name).name != name or any(c in name for c in '/\\\x00') or name in seen_prices):
            raise ValueError('price_packages must contain unique exact archive basenames')
        seen_prices.add(name)
    return json.loads(json.dumps(value))


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _selection_payload(config: FuelSelectionConfig) -> dict:
    return {'schema_version': 1, 'mode': config.mode, 'unknown': config.unknown,
        'rules': [{
            'id': rule.id, 'descriptor': rule.descriptor,
            'descriptor_sha256': rule.descriptor_sha256, 'model_desc': rule.model_desc,
            'variant': rule.variant, 'parts': list(rule.parts),
            'additional_parts': list(rule.additional_parts),
            'company_linked': rule.company_linked,
            'groups': [{'spawn_index': group.spawn_index, 'role': group.role,
                        'confidence': group.confidence, 'reason': group.reason,
                        'evidence': group.evidence} for group in rule.groups],
        } for rule in config.rules]}


def _directory_snapshot(path: Path) -> tuple[tuple[str, int, int, bool], ...]:
    rows = []
    for item in path.rglob('*'):
        if not item.is_file() and not item.is_symlink():
            continue
        stat = item.stat()
        rows.append((item.relative_to(path).as_posix(), stat.st_size, stat.st_mtime_ns,
                     item.is_symlink()))
    return tuple(sorted(rows))


def _snapshot_report(path: Path, snapshot: tuple[tuple[str, int, int, bool], ...]) -> dict:
    raw = json.dumps(snapshot, separators=(',', ':')).encode('utf-8')
    return {'path': str(path), 'file_count': len(snapshot), 'snapshot_sha256': _sha_bytes(raw)}


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def _report_declares_generated_fuel_or_rest(report: object) -> bool:
    """Recognize generated processor declarations without rejecting courier-only reports."""
    if isinstance(report, list):
        return any(_report_declares_generated_fuel_or_rest(item) for item in report)
    if not isinstance(report, dict):
        return False
    topics = []
    for key in ('processors_enabled', 'fix_topics'):
        value = report.get(key)
        if isinstance(value, list):
            topics.extend(value)
    if {'fuel', 'rest'} & set(item for item in topics if isinstance(item, str)):
        return True
    processor_reports = report.get('processor_reports')
    if isinstance(processor_reports, dict) and {'fuel', 'rest'} & set(processor_reports):
        return True
    processor = report.get('processor')
    if processor in {'fuel', 'rest', 'station_parking', 'station_parking_batch'}:
        return True
    analysis = report.get('analysis')
    if isinstance(analysis, str) and any(marker in analysis.lower() for marker in (
            'missing_car_fuel', 'selected_compatibility', 'station_parking', 'rest_stop')):
        return True
    for nested in report.values():
        if isinstance(nested, (dict, list)) and _report_declares_generated_fuel_or_rest(nested):
            return True
    return False


def _check_no_generated_fuel_rest(package: Package) -> None:
    if _FIX_REPORT not in package.files:
        return
    try:
        report = json.loads(package.read(_FIX_REPORT, max_bytes=8 * 1024 * 1024),
                            object_pairs_hook=_unique_json)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f'{package.path.name} has an invalid {_FIX_REPORT}') from exc
    if _report_declares_generated_fuel_or_rest(report):
        raise ValueError(f'{package.path.name} is a generated fuel/rest fix; use original map archives')


def _verify_inputs(identities: dict[Path, tuple[int, int]],
                   snapshots: dict[Path, tuple[tuple[str, int, int, bool], ...]],
                   stack: ResourceStack, resource_pins: dict[str, str],
                   file_pins: dict[Path, str], package_resource_pins: list[dict]) -> None:
    for path, expected in snapshots.items():
        if _directory_snapshot(path) != expected:
            raise ValueError(f'Directory package changed during fuel batch: {path}')
    for path, (size, mtime) in identities.items():
        stat = path.stat()
        if (stat.st_size, stat.st_mtime_ns) != (size, mtime):
            raise ValueError(f'Input package changed during fuel batch: {path}')
    for path, expected in file_pins.items():
        if _sha_file(path) != expected:
            raise ValueError(f'Pinned input SHA-256 drift during fuel batch: {path}')
    for virtual, expected in sorted(resource_pins.items()):
        if virtual not in stack.resources:
            raise ValueError(f'Pinned effective resource disappeared: {virtual}')
        if _sha_bytes(stack.read(virtual, max_bytes=128 * 1024 * 1024)) != expected:
            raise ValueError(f'Effective resource SHA-256 drift before packaging: {virtual}')
    for pin in package_resource_pins:
        package = pin['package']
        virtual = pin['path']
        if package.files.get(virtual) != pin['physical_path']:
            raise ValueError(f"Selected source resource provider changed: {pin['package_name']}:{virtual}")
        if _sha_bytes(package.read(virtual, max_bytes=128 * 1024 * 1024)) != pin['sha256']:
            raise ValueError(f"Selected source resource SHA-256 drift: {pin['package_name']}:{virtual}")


def _coverage_blockers(report: dict, label: str) -> list[dict]:
    coverage = report.get('coverage') if isinstance(report, dict) else None
    if not isinstance(coverage, dict):
        return [{'area': label, 'reason': 'Planner omitted coverage report'}]
    if coverage.get('complete') is False:
        rows = coverage.get('blockers')
        if not isinstance(rows, list) or not rows:
            return [{'area': label, 'reason': 'Planner did not complete requested coverage'}]
    blockers = coverage.get('blockers', [])
    if not isinstance(blockers, list):
        return [{'area': label, 'reason': 'Planner coverage blockers are malformed'}]
    return [{'area': label, **(item if isinstance(item, dict) else {'reason': str(item)})}
            for item in blockers]


def _variant(mode: str) -> tuple[str, str]:
    return ('g1-broad', 'G1 BROAD') if mode == 'broad' else ('g2-select', 'G2 SELECT')


def _metadata(label: str, revision: int, batch_id: str, package_names: list[str]) -> dict:
    stable_label = f'{label} r{revision}'
    description = (
        f'{stable_label} — finite fuel-site comparison for {batch_id}; fuel-only experimental overlay.\n'
        'Alternative fuel strategy: enable exactly one of G1 BROAD and G2 SELECT for this same test scope.\n'
        'This manifest selects a bounded set of station placements; it is not a map-wide coverage claim.\n'
        'Preserve source-native parking, truck facilities, fuel services and unselected placements.\n'
        'This changes no pump access geometry; reachability, signs, prices and billing need validation.\n'
        'Keep the independent N2 navigation-icons overlay above the background. Old F/A/B/C/E parking experiments stay disabled.\n'
        'Place above all declared source maps and fixes, retaining those raw map archives below this overlay.\n'
        'Selected sectors use pinned original bytes, composed only with this package’s selected fuel additions.\n'
        'This suppresses other generated parking/fuel edits in those sectors; unrelated sectors retain lower fixes.\n'
        'The package is experimental and has not been validated in game.\n'
        'LOW TO HIGH explicit packages: ' + ', '.join(package_names) + '.\n'
    )
    return {'display_name': f"{stable_label} | szczerb's Road Trip Fuel Selection Tour - Experimental",
            'description': description}


def run_fuel_selection_batch(manifest_path, *, packages, game_dir=None, extractor=None,
                             generate=False, revision=1, experimental=False, run_id=None,
                             fuel_selection: FuelSelectionConfig = FuelSelectionConfig()):
    """Audit or generate one broad/selective bounded fuel-site comparison.

    Prices are processed independently of the selected pump policy, but only
    for the manifest's explicitly named original price packages. No package is
    emitted for an empty resource set.
    """
    if generate and not experimental:
        raise ValueError('Generation requires --experimental; no candidate is verified in game')
    if type(revision) is not int or revision < 1:
        raise ValueError('Revision must be a positive integer')
    if type(generate) is not bool or type(experimental) is not bool:
        raise ValueError('generate and experimental must be booleans')
    if not isinstance(fuel_selection, FuelSelectionConfig):
        raise ValueError('fuel_selection must be a FuelSelectionConfig')
    manifest_path = Path(manifest_path).expanduser().resolve()
    manifest_bytes = manifest_path.read_bytes()
    manifest_digest = _sha_bytes(manifest_bytes)
    manifest = validate_manifest(json.loads(manifest_bytes.decode('utf-8-sig'),
                                            object_pairs_hook=_unique_json))
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('run_id must use YYYY-MM-DD_HH-MM-SS')
    variant, variant_title = _variant(fuel_selection.mode)
    selection_payload = _selection_payload(fuel_selection)
    selection_bytes = json.dumps(selection_payload, sort_keys=True,
                                 separators=(',', ':')).encode('utf-8')
    selection_sha256 = _sha_bytes(selection_bytes)
    run_name = f"{manifest['batch_id']}-{variant}"
    work = REPO_ROOT / 'local_outputs/work' / stamp / run_name
    output = (REPO_ROOT / 'local_outputs/generated' / stamp /
              f"{variant}-r{revision}-{manifest['batch_id']}-ats-1.61-experimental.scs")
    if work.exists() or (generate and output.exists()):
        raise FileExistsError('Fuel batch audit/output exists; choose a new run_id')
    work.mkdir(parents=True)
    audit_path = work / 'audit.json'
    previous_work = Archive._work_root
    Archive.configure_work_root(work)
    audit = {'status': 'started', 'analysis_only': not generate, 'in_game_verified': False,
             'generated_mod_count': 0, 'report_path': str(audit_path), 'output': None,
             'workflow': {'run_id': stamp, 'batch_id': manifest['batch_id'],
                          'variant': variant, 'work_dir': str(work)},
             'sites': []}
    try:
        installed = _game_directory(game_dir)
        version = _game_version(installed, extractor)
        if version != manifest['game_version']:
            raise ValueError('Installed ATS version differs from fuel batch manifest')
        game_paths, dlcs = _game_packages(installed)
        game_paths = [Path(path).resolve() for path in game_paths]
        if isinstance(packages, (str, Path)):
            raise ValueError('packages must be an ordered sequence of original archives')
        try:
            explicit = [Path(path).expanduser().resolve() for path in packages]
        except TypeError as exc:
            raise ValueError('packages must be an ordered sequence of original archives') from exc
        if not explicit:
            raise ValueError('At least one explicit original map/archive package is required')
        if any(not path.is_file() and not path.is_dir() for path in explicit):
            raise ValueError('Every explicit package must exist as an archive or directory')
        if len(set(explicit)) != len(explicit) or set(explicit) & set(game_paths):
            raise ValueError('Do not repeat explicit or installed game packages')
        paths = [*game_paths, *explicit]
        by_name: dict[str, list[Path]] = {}
        for path in paths:
            by_name.setdefault(path.name, []).append(path)
        if any(len(matches) != 1 for matches in by_name.values()):
            raise ValueError('Mounted package basenames must be unique')
        explicit_by_name = {path.name: path for path in explicit}
        for name in manifest['price_packages']:
            if name not in explicit_by_name or not explicit_by_name[name].is_file():
                raise ValueError('price_packages must resolve to explicit original archive files')
        selected_sources = {}
        for site in manifest['sites']:
            matches = by_name.get(site['source_package'], [])
            if len(matches) != 1:
                raise ValueError(f"source_package does not resolve uniquely: {site['source_package']}")
            selected_sources[site['source_package']] = matches[0]
        version_input = installed / ('version.sii' if (installed / 'version.sii').is_file()
                                     else 'version.scs')
        identities = {}
        for path in dict.fromkeys([*paths, version_input, manifest_path]):
            stat = path.stat()
            identities[path] = (stat.st_size, stat.st_mtime_ns)
        snapshots = {path: _directory_snapshot(path) for path in paths if path.is_dir()}
        manifest_file_pins = {manifest_path: manifest_digest}
        audit['workflow'].update({
            'game_dir': str(installed), 'game_version': version,
            'manifest': str(manifest_path), 'manifest_sha256': manifest_digest,
            'packages_low_to_high': [str(path) for path in paths],
            'explicit_package_basenames': [path.name for path in explicit],
            'archive_identities': [{'path': str(path), 'size': identities[path][0],
                                    'mtime_ns': identities[path][1]}
                                   for path in [*game_paths, *explicit]],
            'version_source_identity': {'path': str(version_input),
                'size': identities[version_input][0], 'mtime_ns': identities[version_input][1]},
            'directory_package_snapshots': [_snapshot_report(path, snapshot)
                                            for path, snapshot in sorted(snapshots.items())],
            'fuel_selection': fuel_selection.summary(),
            'fuel_selection_config': selection_payload,
            'fuel_selection_config_sha256': selection_sha256,
            'scope': 'finite manifest placements only; no map-wide completeness claim',
        })
        with ExitStack() as stack_manager:
            mounted = []
            for index, path in enumerate(paths, 1):
                logging.getLogger(__name__).info('Fuel comparison: package %s/%s %s', index, len(paths), path.name)
                mounted.append(stack_manager.enter_context(Package(path, extractor=extractor, dlcs=dlcs)))
            for package in mounted[len(game_paths):]:
                _check_no_generated_fuel_rest(package)
            stack = ResourceStack(mounted)
            game_stack = ResourceStack(mounted[:len(game_paths)])
            source_package_paths = {name: selected_sources[name] for name in selected_sources}
            source_sectors = sorted({site['sector'] for site in manifest['sites']})
            targets = frozenset(int(site['prefab_uid'], 16) for site in manifest['sites'])
            providers = {}
            for site in manifest['sites']:
                sector_path = site['sector']
                if sector_path not in stack.resources:
                    raise ValueError(f"Selected sector is absent from effective stack: {sector_path}")
                provider, resource = stack.resources[sector_path]
                expected_provider = selected_sources[site['source_package']]
                if provider.path.resolve() != expected_provider.resolve():
                    raise ValueError(f"Selected sector is overridden by another package: {sector_path}")
                data = stack.read(sector_path, max_bytes=64 * 1024 * 1024)
                digest = _sha_bytes(data)
                if digest != site['sector_sha256']:
                    raise ValueError(f"Selected sector SHA-256 pin mismatch: {sector_path}")
                parsed = parse_sector(data)
                matches = [prefab for prefab in parsed.prefabs if prefab.uid == int(site['prefab_uid'], 16)]
                if len(matches) != 1:
                    raise ValueError(f"Selected prefab UID is missing or ambiguous: {site['prefab_uid']}")
                providers[site['id']] = {'package': str(provider.path),
                    'physical_path': resource.physical_path, 'sha256': digest}
            map_packages = {str(source_package_paths[site['source_package']]) for site in manifest['sites']}
            logging.getLogger(__name__).info('Fuel comparison: planning %s pinned sites', len(targets))
            target_report, fuel_resources = plan_map_fuel(
                stack, map_packages=map_packages, map_name='Fuel Selection Tour',
                fuel_selection=fuel_selection, target_prefab_uids=targets,
                source_sector_paths=frozenset(source_sectors))
            if not isinstance(target_report, dict) or not isinstance(fuel_resources, dict):
                raise ValueError('Fuel planner returned an invalid report or resource set')
            for site in manifest['sites']:
                planned = [row for row in target_report.get('stations', [])
                           if row.get('prefab_uid') == site['prefab_uid']]
                audit['sites'].append({'id': site['id'], **site,
                    'effective_provider': providers[site['id']],
                    'planner_site': planned[0] if len(planned) == 1 else None})

            guarded_sector_details = {}
            for site in manifest['sites']:
                planned = [row for row in target_report.get('stations', [])
                           if row.get('prefab_uid') == site['prefab_uid']]
                if len(planned) != 1:
                    continue
                selection = planned[0].get('fuel_selection')
                groups = selection.get('groups', []) if isinstance(selection, dict) else []
                skipped = [group for group in groups
                           if isinstance(group, dict)
                           and group.get('selected_for_addition') is False]
                if not skipped:
                    continue
                path = site['sector']
                source_sha256 = providers[site['id']]['sha256']
                guard = guarded_sector_details.setdefault(path, {
                    'path': path, 'source_package': site['source_package'],
                    'source_sha256': source_sha256, 'site_ids': [], 'skipped_groups': [],
                    'reason': ('Restore pinned original sector content over lower generated fuel/rest edits; '
                               'retain only this batch’s selected fuel additions in the sector.'),
                })
                if guard['source_sha256'] != source_sha256:
                    raise ValueError(f'Selected sites disagree on source sector pin: {path}')
                guard['site_ids'].append(site['id'])
                guard['skipped_groups'].extend({
                    'site_id': site['id'], 'spawn_index': group.get('spawn_index'),
                    'role': group.get('role'), 'reason': group.get('reason'),
                    'rule_id': group.get('rule_id'),
                } for group in skipped)

            logging.getLogger(__name__).info('Fuel comparison: independent petrol prices and alias contexts')
            target_price_paths = {str(explicit_by_name[name]) for name in manifest['price_packages']}
            price_policy, policy_report = build_policy(
                stack, game_stack, target_packages=target_price_paths,
                reference_path=DEFAULT_REFERENCE)
            price_report, price_resources = plan_petrol_prices(
                stack, target_packages=target_price_paths, policy=price_policy)
            if not isinstance(fuel_resources, dict) or not isinstance(price_resources, dict):
                raise ValueError('Fuel or price planner returned an invalid resource set')
            fuel_price_collisions = set(fuel_resources) & set(price_resources)
            if fuel_price_collisions:
                raise ValueError('Fuel and petrol-price planners collide on: '
                                 + ', '.join(sorted(fuel_price_collisions)))

            guard_resources = {}
            transitions = []
            for change in target_report.get('changed_sectors', []):
                path = change.get('path') if isinstance(change, dict) else None
                if path not in fuel_resources or path not in stack.resources:
                    continue
                transitions.append(('fuel', path, stack.read(path, max_bytes=64 * 1024 * 1024),
                                    fuel_resources[path]))
            for path, guard in sorted(guarded_sector_details.items()):
                source = stack.read(path, max_bytes=64 * 1024 * 1024)
                composed = fuel_resources.get(path)
                if composed is None:
                    guard_resources[path] = source
                    composed = source
                    guard['resource_role'] = 'raw_source_baseline_guard'
                else:
                    guard['resource_role'] = 'fuel_composed_selected_sector'
                guard['output_sha256'] = _sha_bytes(composed)
                guard['scope'] = 'selected sector only'
                if not any(transition[1] == path for transition in transitions):
                    transitions.append(('fuel', path, source, composed))
            context_report, context_resources = plan_prefab_contexts(
                stack, fuel_resources, transitions, source=str(manifest_path),
                map_name='Fuel Selection Tour')
            if not isinstance(context_resources, dict):
                raise ValueError('Context planner returned an invalid resource set')
            if (set(context_resources) & (set(fuel_resources) | set(price_resources))):
                raise ValueError('Generated context resources collide with fuel or price resources')

            blockers = []
            blockers.extend(_coverage_blockers(target_report, 'fuel'))
            blockers.extend(_coverage_blockers(policy_report, 'price_policy'))
            blockers.extend(_coverage_blockers(price_report, 'prices'))
            blockers.extend(_coverage_blockers(context_report, 'contexts'))
            for site in manifest['sites']:
                if not any(row.get('prefab_uid') == site['prefab_uid']
                           for row in target_report.get('stations', [])):
                    blockers.append({'area': 'scope', 'site_id': site['id'],
                                     'prefab_uid': site['prefab_uid'],
                                     'reason': 'Planner did not report the selected fuel group'})
            if set(guard_resources) & (set(price_resources) | set(context_resources)):
                raise ValueError('Baseline sector guards collide with price or context resources')
            resources = {**fuel_resources, **price_resources, **context_resources, **guard_resources}
            resource_pins: dict[str, str] = {}
            package_resource_pins: list[dict] = []
            package_by_path = {package.path.resolve(): package for package in mounted}
            for site in manifest['sites']:
                resource_pins[site['sector']] = providers[site['id']]['sha256']
            for report in (target_report, price_report, context_report):
                for item in report.get('source_resources', []) if isinstance(report, dict) else []:
                    path = item.get('path') if isinstance(item, dict) else None
                    if path and path in stack.resources:
                        resource_pins[path] = item.get('sha256') or _sha_bytes(stack.read(path))
            for station in target_report.get('stations', []):
                definition = station.get('definition')
                descriptor = station.get('descriptor')
                for path in (definition, descriptor):
                    if isinstance(path, str) and path in stack.resources:
                        resource_pins[path] = _sha_bytes(stack.read(path))
            for record in price_report.get('countries', []):
                path = record.get('path') if isinstance(record, dict) else None
                digest = record.get('source_sha256') if isinstance(record, dict) else None
                if path and digest and path in stack.resources:
                    resource_pins[path] = digest
            reference = policy_report.get('reference') if isinstance(policy_report, dict) else None
            if isinstance(reference, dict) and reference.get('path') and reference.get('sha256'):
                provider_path = Path(reference.get('package', '')).resolve()
                provider_package = package_by_path.get(provider_path)
                if provider_package is None:
                    raise ValueError('Price reference provider is absent from mounted packages')
                package_resource_pins.append({'package': provider_package,
                    'package_name': provider_package.path.name, 'path': reference['path'],
                    'physical_path': reference['physical_path'], 'sha256': reference['sha256']})
            for entry in policy_report.get('entries', []) if isinstance(policy_report, dict) else []:
                if not isinstance(entry, dict):
                    continue
                for lower in entry.get('lower_candidates', []):
                    if not isinstance(lower, dict):
                        continue
                    provider_package = package_by_path.get(Path(lower.get('package', '')).resolve())
                    virtual = entry.get('path')
                    if provider_package is None or not isinstance(virtual, str):
                        raise ValueError('Selected lower price source provider is absent from mounted packages')
                    package_resource_pins.append({'package': provider_package,
                        'package_name': provider_package.path.name, 'path': virtual,
                        'physical_path': lower.get('physical_path'), 'sha256': lower.get('sha256')})

            audit['planner'] = {'fuel': target_report, 'price_policy': policy_report,
                                'prices': price_report, 'contexts': context_report,
                                'resource_count': len(resources),
                                'changed_resource_paths': sorted(resources),
                                'baseline_sector_guards': [guarded_sector_details[path]
                                    for path in sorted(guarded_sector_details)],
                                'bounded_scope': 'manifest-selected placements only'}
            audit['workflow']['selected_resource_sha256'] = resource_pins
            audit['workflow']['selected_package_resource_sha256'] = [
                {'package': pin['package_name'], 'path': pin['path'],
                 'physical_path': pin['physical_path'], 'sha256': pin['sha256']}
                for pin in package_resource_pins]
            audit['workflow']['site_sector_providers'] = providers
            _verify_inputs(identities, snapshots, stack, resource_pins, manifest_file_pins,
                           package_resource_pins)
            if blockers:
                audit['status'] = 'blocked' if generate else 'reported_partial'
                audit['planner']['blockers'] = blockers
            elif not resources:
                audit['status'] = 'no_changes'
                audit['planner']['blockers'] = []
            elif generate:
                metadata = _metadata(variant_title, revision, manifest['batch_id'],
                                     [path.name for path in explicit])
                report = {'schema_version': 1, 'analysis': 'bounded_fuel_selection_batch',
                    'processors_enabled': ['fuel'],
                    'batch_id': manifest['batch_id'], 'manifest': manifest,
                    'fuel_selection': fuel_selection.summary(),
                    'fuel_selection_config': selection_payload,
                    'fuel_selection_config_sha256': selection_sha256,
                    'bounded_scope': True,
                    'in_game_verified': False,
                    'workflow': audit['workflow'], 'planner': audit['planner'],
                    'limitations': [
                        'This package covers only the explicitly listed fuel placements; it is not a map-wide coverage claim.',
                        'Fuel suitability rules do not prove fuel chemistry or private ownership.',
                        'Source-native fuel, parking and truck services are retained. In guarded selected sectors, other generated parking/fuel edits are suppressed; unrelated sectors retain lower fixes.',
                        'Generated petrol-price edits are limited to explicitly listed target map packages.',
                        'G1 BROAD and G2 SELECT are alternatives; enable exactly one for this bounded test.',
                        'No game installation, profile or live mod directory was modified.',
                    ]}
                written = write_mod(output, resources, report, game_version=version,
                    display_name=metadata['display_name'], description=metadata['description'],
                    revision=revision, category='map')
                audit.update(status='generated', generated_mod_count=1,
                             output=str(output), written_report=written)
                audit['planner']['blockers'] = []
            else:
                audit['status'] = 'reported'
                audit['planner']['blockers'] = []
        _write_json(audit_path, audit)
        return audit
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        audit.update(status='failed', error=str(exc))
        if not audit_path.exists():
            _write_json(audit_path, audit)
        raise
    finally:
        Archive.configure_work_root(previous_work)
