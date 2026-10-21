"""Discover and add missing car fuel services using byte-preserving graph edits.

Game assets are copied only into ignored generated packages, never source code.
Unsupported coverage is reported explicitly; callers must refuse a complete mod
when blockers remain. Only the Helena Service pair has user gameplay evidence.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import logging
import re
import struct

from .fuel_matching import match_gas_services
from .fuel_selection import FuelSelectionConfig, classify_groups
from .archive import Archive
from .local_fuel import token
from .map_sector import SectorFormatError, extend_layer, parse_sector
from .package import ResourceStack
from .ppd import inspect_ppd, upgrade_fuel_descriptor, add_petrol_spawns
from .sii import parse_units, _expand_includes, _mask_strings, _HEADER


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prefab_definitions(stack: ResourceStack) -> dict[int, tuple]:
    """Retain complete source unit text, including typed/array attributes."""
    stack.prefetch(r'def/world/prefab.*\.(?:sii|sui)')
    result = {}
    for path in stack.matching(r'def/world/prefab(?:\.[^/]+)?\.sii'):
        expanded = _expand_includes(stack.text(path), path, stack.text, ())
        units = parse_units(expanded, source=path)
        masked = _mask_strings(expanded)
        blocks = {}
        for header in _HEADER.finditer(masked):
            end, depth = header.end(), 1
            while end < len(masked) and depth:
                depth += (masked[end] == '{') - (masked[end] == '}')
                end += 1
            blocks[(header[1], header[2])] = expanded[header.start():end]
        for unit in units:
            if unit.kind != 'prefab_model':
                continue
            key = token(unit.name.removeprefix('prefab.').lower())
            entry = (unit, blocks[(unit.kind, unit.name)], path)
            if key in result:
                # Loading two complete root lists is ambiguous even if identical.
                raise ValueError(f'Duplicate effective prefab definition: {unit.name}')
            result[key] = entry
    return result


def _alias_definition(block: str, old: str, alias: str, descriptor: str) -> bytes:
    changed, count = re.subn(r'(\bprefab_model\s*:\s*)' + re.escape(old) + r'\b',
                             lambda m: m[1] + 'prefab.' + alias, block, count=1)
    if count != 1:
        raise ValueError('Unable to clone prefab definition header')
    changed, count = re.subn(r'(\bprefab_desc\s*:\s*)("(?:\\.|[^"\\])*"|[^\s}]+)',
                             lambda m: m[1] + json.dumps('/' + descriptor), changed)
    if count != 1:
        raise ValueError('Expected one descriptor attribute in prefab definition')
    result = ('SiiNunit\n{\n' + changed + '\n}\n').encode()
    unit = parse_units(result.decode())[0]
    if unit.name != 'prefab.' + alias or unit.one('prefab_desc') != '/' + descriptor:
        raise ValueError('Cloned prefab definition failed round-trip')
    return result


def _is_fuel(item) -> bool:
    return item.kind == 0x23 or (item.kind == 7 and item.flags & 0xff == 0)


def _splice(data: bytes, changes: list[tuple[int, int, bytes]]) -> bytes:
    chunks, cursor = [], 0
    for start, end, replacement in sorted(changes, key=lambda x: (x[0], x[1])):
        if start < cursor or not start <= end <= len(data):
            raise ValueError('Overlapping/out-of-bounds binary edits')
        chunks.extend((data[cursor:start], replacement))
        cursor = end
    chunks.append(data[cursor:])
    return b''.join(chunks)


def plan_map_fuel(stack: ResourceStack, *, map_packages: set[str], map_name: str,
                  fuel_selection: FuelSelectionConfig = FuelSelectionConfig(),
                  target_prefab_uids: frozenset[int] | None = None,
                  source_sector_paths: frozenset[str] | None = None) -> tuple[dict, dict[str, bytes]]:
    """Plan broad or selected additions, optionally within an explicit PoC scope.

    Sector scope selects resources owned by ``map_packages``; the existing
    neighbor halo resolves references without adding neighboring fuel targets.
    Explicit prefab targets must resolve to fuel groups from the selected source
    area. Invalid or empty scopes fail; unresolved targets are coverage blockers.
    Omitting both scope arguments preserves the historical map-wide behavior.
    """
    if not isinstance(fuel_selection, FuelSelectionConfig):
        raise ValueError('fuel_selection must be a FuelSelectionConfig')
    if target_prefab_uids is not None:
        if (not isinstance(target_prefab_uids, frozenset) or not target_prefab_uids
                or any(type(uid) is not int or not 0 < uid < 2**64 for uid in target_prefab_uids)):
            raise ValueError('target_prefab_uids must be a nonempty frozenset of positive uint64 prefab UIDs')
    if source_sector_paths is not None:
        if (not isinstance(source_sector_paths, frozenset) or not source_sector_paths
                or any(not isinstance(path, str) or not re.fullmatch(
                    r'map/[^/]+/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)', path)
                       or not path.isprintable() or any(character in path for character in ('\\', ':', '\x00'))
                       or path.split('/')[1] in ('.', '..') for path in source_sector_paths)):
            raise ValueError('source_sector_paths must be a nonempty frozenset of normalized map sector paths')
    selective = fuel_selection.mode == 'realistic'
    log = logging.getLogger(__name__)
    # R8 renamed these sources for display only, retaining the R7 gameplay
    # payload. Keep their established generated UIDs/aliases across that rename.
    namespace_name = {'Alaska Expansion': 'Alaska',
                      'Western Canada Expansion': 'Western Canada'}.get(map_name, map_name)
    report = {'schema_version': 3, 'analysis': 'map_wide_missing_car_fuel', 'map_name': map_name,
              'package_order': [str(p.path) for p in stack.packages],
              'coverage': {'blockers': [], 'truck_points': 0, 'already_supported': 0,
                           'added_car_points': 0, 'garage_car_points': 0, 'stations_changed': 0},
              'stations': [], 'source_resources': [], 'changed_sectors': [],
              'limitations': [
                  'Experimental: only one ordinary same-position fuel pair has user gameplay evidence.',
                  'Garage FuelPump sources gain Service car twins; this broader case needs gameplay validation.',
                  'No pump geometry or access roads are changed; physical car access remains a gameplay constraint.',
                  'Full-sector overrides require the declared source stack and conflict with other sector replacements.',
              ]}
    if selective:
        report['schema_version'] = 4
        report['fuel_selection'] = fuel_selection.summary()
        report['coverage'].update({'policy_selected_truck_points': 0, 'policy_skipped_truck_points': 0,
                                   'uncertain_included_points': 0, 'uncertain_skipped_points': 0,
                                   'skipped_points_with_native_car_support': 0,
                                   'native_car_services_retained': 0, 'native_car_locators_retained': 0})
        report['limitations'].append('Suitability roles do not prove fuel chemistry or private ownership; native car support is retained even at excluded pumps.')
    coverage = report['coverage']; blockers = coverage['blockers']
    sectors, items, nodes = {}, {}, defaultdict(list)
    inspected = set()
    source_paths = stack.matching(r'map/[^/]+/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)')
    source_paths = [p for p in source_paths if str(stack.resources[p][0].path) in map_packages]
    if source_sector_paths is not None:
        invalid_paths = source_sector_paths - set(source_paths)
        if invalid_paths:
            raise ValueError('Scoped sector is missing or not provided by an eligible source package: '
                             + ', '.join(sorted(invalid_paths)))
        source_paths = [path for path in source_paths if path in source_sector_paths]
    if source_sector_paths is not None or target_prefab_uids is not None:
        report['analysis'] = 'bounded_missing_car_fuel'
        report['scope'] = {
            'kind': 'explicit_prefab_targets' if target_prefab_uids is not None else 'source_sector_subset',
            'source_sector_paths': sorted(source_paths),
            'target_prefab_uids': ([hex(uid) for uid in sorted(target_prefab_uids)]
                                   if target_prefab_uids is not None else None),
            'complete_means': 'All requested fuel groups in the declared bounded source area were inspected; no map-wide coverage claim.'}
        report['limitations'].append('Bounded inspection and generation: unselected prefab fuel groups stay unchanged; neighboring sectors only resolve references.')
    log.info('%s: inspecting %s source sector files', map_name, len(source_paths))
    for package in stack.packages:
        package.prefetch([p for p in source_paths if stack.resources[p][0] is package],
                         disk_cache=Archive._scratch_root().parent / 'package-cache' / _sha(str(package.path).encode())[:12])
    original_service_ids = set()

    def load(path):
        if path in inspected or path not in stack.resources:
            return
        data = stack.read(path, max_bytes=64*1024*1024)
        parsed = parse_sector(data)
        inspected.add(path)
        def nested_fuel(entries):
            return any(_is_fuel(i) or (i.kind == 0x28 and nested_fuel(i.details['items'])) for i in entries)
        # Aux contains large decoration compounds; inspect them structurally,
        # but do not retain unrelated geometry in the fuel working graph.
        if path.endswith('.aux') and not parsed.prefabs and not parsed.services:
            if nested_fuel(parsed.items):
                blockers.append({'path': path, 'reason': 'Compound-contained fuel needs a container-aware splice'})
            return
        sectors[path] = (data, parsed)
        for item in parsed.items:
            if item.uid in items and items[item.uid][1] != item:
                otherpath, other = items[item.uid]
                if data[item.offset:item.end] != sectors[otherpath][0][other.offset:other.end]:
                    raise ValueError(f'Inconsistent duplicate map item UID {item.uid:#x}')
            items[item.uid] = path, item
            if item.kind == 0x28 and nested_fuel(item.details['items']):
                blockers.append({'path': path, 'reason': 'Compound-contained fuel needs a container-aware splice'})
        for node in parsed.nodes:
            nodes[node.uid].append((path, node))

    for path in source_paths:
        try:
            load(path)
            if path in sectors:
                original_service_ids.update(i.uid for i in sectors[path][1].services if _is_fuel(i))
        except (ValueError, KeyError) as exc:
            blockers.append({'path': path, 'reason': str(exc)})
    report['sectors_inspected'] = len(inspected)
    # Cross-boundary prefab/control/service nodes can belong to adjacent stock
    # sectors rather than to the source map's own sector set.
    neighbors = set()
    for path in list(sectors):
        if not sectors[path][1].services and not sectors[path][1].prefabs:
            continue
        m = re.fullmatch(r'(map/[^/]+/)sec([+-]\d{4})([+-]\d{4})\.(base|aux)', path)
        if not m:
            continue
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for ext in ('base', 'aux'):
                    neighbor = f'{m[1]}sec{int(m[2])+dx:+05d}{int(m[3])+dz:+05d}.{ext}'
                    if neighbor in stack.resources and neighbor not in inspected:
                        neighbors.add(neighbor)
    for package in stack.packages:
        package.prefetch([p for p in sorted(neighbors) if stack.resources[p][0] is package],
                         disk_cache=Archive._scratch_root().parent / 'package-cache' / _sha(str(package.path).encode())[:12])
    log.info('%s: resolving %s neighboring sector files', map_name, len(neighbors))
    for neighbor in sorted(neighbors):
        try:
            load(neighbor)
        except (ValueError, KeyError) as exc:
            blockers.append({'path': neighbor, 'reason': str(exc)})
    definitions = prefab_definitions(stack)
    log.info('%s: loaded %s effective prefab definitions', map_name, len(definitions))
    grouped = defaultdict(list)
    for uid in sorted(original_service_ids):
        path, service = items[uid]
        grouped[service.details['parent']].append(service)
    target_prefabs = {i.uid for path, (_, parsed) in sectors.items()
                      if path in source_paths for i in parsed.prefabs
                      if any(uid in items and _is_fuel(items[uid][1]) for uid in i.details['slaves'])}
    for uid in target_prefabs:
        grouped.setdefault(uid, [])
    if target_prefab_uids is not None:
        resolved_targets = {uid for uid in target_prefab_uids
                            if uid in grouped and uid in items and items[uid][1].kind == 4}
        blockers.extend({'area': 'scope', 'prefab_uid': hex(uid),
                         'reason': 'Requested fuel prefab was not resolved as a source-area root fuel group'}
                        for uid in sorted(target_prefab_uids - resolved_targets))
        grouped = {uid: grouped[uid] for uid in sorted(resolved_targets)}
    # Fetch only descriptors referenced by fuel parents, not every game asset.
    ppds = set()
    for parent in grouped:
        if parent in items:
            entry = definitions.get(items[parent][1].details.get('model'))
            if entry:
                ppds.add(entry[0].one('prefab_desc', '').lstrip('/'))
    for package in stack.packages:
        package.prefetch([p for p in ppds if p in stack.resources and stack.resources[p][0] is package])
    log.info('%s: matching %s fuel parents', map_name, len(grouped))
    resources, edits, new_items, new_nodes = {}, defaultdict(list), defaultdict(list), defaultdict(list)
    clones, aliases, eligible_trucks = {}, {}, set()
    descriptor_checks = []
    all_uids = set(items) | set(nodes)

    def new_uid(seed):
        value = int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], 'little')
        if not value or value in all_uids:
            raise ValueError('Generated UID collision; refusing ambiguous output')
        all_uids.add(value)
        return value

    def node_for(uid, preferred=None):
        candidates = nodes.get(uid, [])
        if not candidates:
            raise ValueError(f'Unresolved map node {uid:#x}')
        for path, node in candidates:
            if path == preferred:
                return node
        distinct = {node.raw for _, node in candidates}
        if len(distinct) != 1:
            raise ValueError(f'Inconsistent boundary node {uid:#x}')
        return candidates[0][1]

    for parent_uid, selected_services in sorted(grouped.items()):
        entry_report = {'prefab_uid': hex(parent_uid)}
        try:
            parent_path, prefab = items[parent_uid]
            if prefab.kind != 4:
                raise ValueError('Fuel parent is not a root prefab')
            # Include all its linked fuel services, including adjacent-sector ones.
            services = [items[uid][1] for uid in prefab.details['slaves'] if uid in items and _is_fuel(items[uid][1])]
            orphaned = [s for s in selected_services if s.uid not in {i.uid for i in services}]
            if any(s.kind != 0x23 or s.details['parent'] != parent_uid or s.flags & 0x4000 for s in orphaned):
                raise ValueError('Unlisted fuel service is outside the observed truck FuelPump case')
            # A map can replace one half of a stock sector boundary with an
            # older FuelPump UID. Preserve the pre-existing mismatch, verify
            # the complete GAS/world-position correspondence below, and append
            # only the new car reference rather than rewriting old truck data.
            services.extend(orphaned)
            if orphaned:
                entry_report['preexisting_unlisted_fuel_uids'] = [hex(s.uid) for s in orphaned]
            unit, block, definition_path = definitions[prefab.details['model']]
            descriptor = unit.one('prefab_desc').lstrip('/')
            original_ppd = stack.read(descriptor)
            source_info = inspect_ppd(original_ppd)
            if not source_info['fuel']['gas_spawn_count']:
                if selected_services or target_prefab_uids is not None:
                    raise ValueError('Fuel service parent descriptor has no GAS locators')
                continue
            if source_info['fuel']['other_flags']:
                raise ValueError('Unknown GAS flags in descriptor')
            upgraded, upgrade = upgrade_fuel_descriptor(original_ppd)
            info = inspect_ppd(upgraded)
            trucks = [s for s in services if not s.flags & 0x4000]
            gas_trucks = [s for s in info['spawns'] if s['type'] == 3 and s['flags'] == 0]
            if len(trucks) != len(gas_trucks):
                raise ValueError(f'Truck GAS/service count mismatch: {len(gas_trucks)}/{len(trucks)}')
            coverage['truck_points'] += len(trucks)
            if not selective:
                eligible_trucks.update(s.uid for s in trucks)
            entry_report.update({'path': parent_path, 'model': unit.name, 'descriptor': descriptor,
                                 'truck_points': len(trucks), 'descriptor_upgrade': upgrade})
            if not trucks:
                if selective:
                    native = [service for service in services if service.flags & 0x4000]
                    coverage['native_car_services_retained'] += len(native)
                    coverage['native_car_locators_retained'] += info['fuel']['flags_one_count']
                    entry_report['fuel_selection'] = {'groups': [],
                        'native_car_service_uids': [hex(service.uid) for service in native],
                        'native_car_spawn_indices': [spawn['index'] for spawn in info['spawns']
                                                     if spawn['type'] == 3 and spawn['flags'] == 1]}
                entry_report['status'] = 'car_only'; report['stations'].append(entry_report); continue
            relevant_nodes = {uid: node_for(uid, parent_path) for uid in prefab.details['nodes']}
            for service in services:
                relevant_nodes[service.details['node']] = node_for(service.details['node'], items[service.uid][0])
            # Legacy Garage GAS may coexist with a separately spawned FuelPump.
            mapping = match_gas_services(upgraded, prefab, relevant_nodes, services, allow_missing_car=True)
            car_nodes = [node_for(s.details['node'], items[s.uid][0]) for s in services if s.flags & 0x4000]
            def has_car(spawn):
                truck_node = relevant_nodes[items[mapping[spawn['index']]][1].details['node']]
                return any(n.raw[8:36] == truck_node.raw[8:36] for n in car_nodes)
            selected_indices = None
            if selective:
                # Resolve actual parent links. Spatial proximity alone supplies
                # no company identity or ownership evidence.
                companies = tuple(sorted(uid for uid, (_, candidate) in items.items()
                                         if candidate.kind == 6 and candidate.details['prefab'] == parent_uid))
                garage_indices = {spawn['index'] for spawn in gas_trucks
                                  if items[mapping[spawn['index']]][1].kind == 0x23}
                decisions = classify_groups(fuel_selection, descriptor=descriptor,
                                             descriptor_sha256=_sha(original_ppd),
                                             model_desc=unit.one('model_desc', ''),
                                             variant=prefab.details['variant'], parts=prefab.details['parts'],
                                             additional_parts=unit.values('additional_parts'),
                                             gas_trucks=gas_trucks, company_uids=companies,
                                             garage_indices=garage_indices)
                selected_indices = frozenset(d['spawn_index'] for d in decisions if d['selected_for_addition'])
                # Reject unsupported ownership structures even at policy-skipped
                # pumps; suitability cannot hide unsafe source graph data.
                for spawn in gas_trucks:
                    old = items[mapping[spawn['index']]][1]
                    node = relevant_nodes[old.details['node']]
                    if old.details['nodes'] or node.backward or node.forward != old.uid:
                        raise ValueError('Fuel service has unsupported extra-node/ownership links')
                resolved_node_uids = set(prefab.details['nodes'])
                resolved_node_uids.update(service.details['node'] for service in services)
                resolved_nodes = []
                for node_uid in sorted(resolved_node_uids):
                    candidates = nodes.get(node_uid, [])
                    if not candidates:
                        raise ValueError(f'Unresolved map node {node_uid:#x}')
                    resolved_nodes.append({'uid': hex(node_uid),
                        'resource_paths': sorted({path for path, _ in candidates})})
                all_node_resource_paths = sorted({path for node in resolved_nodes
                                                  for path in node['resource_paths']})
                for decision in decisions:
                    spawn = next(s for s in gas_trucks if s['index'] == decision['spawn_index'])
                    service_uid = mapping[spawn['index']]
                    service = items[service_uid][1]
                    native_locator = any(other['type'] == 3 and other['flags'] == 1
                                         and other['position'] == spawn['position']
                                         and other['rotation'] == spawn['rotation'] for other in info['spawns'])
                    native_service = has_car(spawn)
                    decision.update({'service_uid': hex(service_uid),
                                     'service_resource_path': items[service_uid][0],
                                     'service_node_uid': hex(service.details['node']),
                                     'node_resource_paths': all_node_resource_paths,
                                     'resolved_nodes': resolved_nodes,
                                     'native_car_service_retained': native_service,
                                     'native_car_locator_retained': native_locator,
                                     'native_support_prevents_exclusion': (not decision['selected_for_addition']
                                                                          and (native_service or native_locator))})
                entry_report['fuel_selection'] = {'groups': decisions,
                    'native_car_service_uids': [hex(s.uid) for s in services if s.flags & 0x4000],
                    'native_car_spawn_indices': [s['index'] for s in info['spawns'] if s['type'] == 3 and s['flags'] == 1]}
                coverage['native_car_services_retained'] += len(car_nodes)
                coverage['native_car_locators_retained'] += info['fuel']['flags_one_count']
                coverage['policy_selected_truck_points'] += len(selected_indices)
                coverage['policy_skipped_truck_points'] += len(gas_trucks) - len(selected_indices)
                coverage['skipped_points_with_native_car_support'] += sum(d['native_support_prevents_exclusion'] for d in decisions)
                for decision in decisions:
                    if decision['role'] == 'uncertain':
                        coverage['uncertain_included_points' if decision['selected_for_addition'] else 'uncertain_skipped_points'] += 1
                eligible_trucks.update(mapping[index] for index in selected_indices)
            missing = [s for s in gas_trucks if not has_car(s)
                       and (selected_indices is None or s['index'] in selected_indices)]
            if selective:
                changed_ppd, ppd_change = add_petrol_spawns(upgraded, selected_spawn_indices=selected_indices)
                # An entirely skipped legacy layout needs no new private alias
                # just to upgrade the unchanged source format.
                if not selected_indices:
                    changed_ppd = original_ppd
            else:
                changed_ppd, ppd_change = add_petrol_spawns(upgraded)
            needs_descriptor = changed_ppd != original_ppd
            coverage['already_supported'] += sum(has_car(s) for s in gas_trucks)
            if not missing and not needs_descriptor:
                entry_report['status'] = ('policy_skipped' if selective and not selected_indices else 'already_supported'); report['stations'].append(entry_report); continue
            key = (unit.name, _sha(original_ppd))
            if selective:
                key += (tuple(sorted(selected_indices)),)
            if needs_descriptor and key not in aliases:
                alias_seed = f'{namespace_name}:{unit.name}:{_sha(original_ppd)}'
                if selective:
                    alias_seed += ':fuel-realistic:' + ','.join(map(str, sorted(selected_indices)))
                alias = 'rtg' + _sha(alias_seed.encode())[:8]
                private_ppd = f'prefab/rtfix/{alias}.ppd'; definition = f'def/world/prefab.{alias}.sii'
                if (any(p in stack.resources or p in resources for p in (private_ppd, definition))
                        or token(alias) in definitions):
                    raise ValueError('Private prefab resource/unit collision')
                aliases[key] = alias
                resources[private_ppd] = changed_ppd
                resources[definition] = _alias_definition(block, unit.name, alias, private_ppd)
                report['source_resources'].append({'path': descriptor, 'sha256': _sha(original_ppd),
                                                   'package': str(stack.resources[descriptor][0].path),
                                                   'definition': definition_path})
            alias = aliases.get(key)
            if selective:
                descriptor_checks.append((parent_uid, changed_ppd, ppd_change['added_count']))
            if alias:
                edits[parent_path].append((prefab.offset+57, prefab.offset+65, struct.pack('<Q', token(alias))))
            added_slave_ids = []
            for spawn in missing:
                old = items[mapping[spawn['index']]][1]
                path = items[old.uid][0]
                node = node_for(old.details['node'], path)
                if old.details['nodes'] or node.backward != 0 or node.forward != old.uid:
                    raise ValueError('Fuel service has unsupported extra-node/ownership links')
                seed = f'{namespace_name}:{path}:{old.uid:x}:{_sha(sectors[path][0])}'
                uid, node_uid = new_uid(seed+':car-service'), new_uid(seed+':car-node')
                raw = bytearray(sectors[path][0][old.offset:old.end])
                # Garage FuelPump consumes the first GAS; appended GAS becomes
                # an ordinary Service according to PrefabCreator's ordering.
                struct.pack_into('<I', raw, 0, 7)
                struct.pack_into('<Q', raw, 4, uid)
                struct.pack_into('<I', raw, 52, old.flags | 0x4000)
                struct.pack_into('<Q', raw, 57, node_uid)
                node_raw = bytearray(node.raw)
                struct.pack_into('<Q', node_raw, 0, node_uid)
                struct.pack_into('<Q', node_raw, 44, uid)
                new_items[path].append(bytes(raw)); new_nodes[path].append(bytes(node_raw))
                added_slave_ids.append(uid); clones[old.uid] = uid
                coverage['garage_car_points'] += old.kind == 0x23
            if added_slave_ids:
                count = len(prefab.details['slaves']) + len(added_slave_ids)
                offset = prefab.details['slave_count_offset']; insertion = prefab.details['slave_insert_offset']
                edits[parent_path].extend([(offset, offset+4, struct.pack('<I', count)),
                                          (insertion, insertion, struct.pack('<'+'Q'*len(added_slave_ids), *added_slave_ids))])
            coverage['added_car_points'] += len(missing); coverage['stations_changed'] += 1
            entry_report.update({'status': 'changed', 'added_car_points': len(missing), 'private_alias': alias,
                                 'source_service_uids': [hex(mapping[s['index']]) for s in missing]})
            report['stations'].append(entry_report)
        except (ValueError, KeyError, IndexError, struct.error) as exc:
            blockers.append({**entry_report, 'reason': str(exc)})
    # Follow explicit visibility references and nonzero layer membership for
    # new objects. Existing opaque data/desc/aux payloads stay untouched unless
    # this structural parser proves a particular reference-list edit necessary.
    for path, (data, parsed) in sectors.items():
        for item in parsed.items:
            children = item.details.get('children', ())
            additions = [clones[uid] for uid in children if uid in clones]
            if additions:
                offset = item.details['child_count_offset']; insertion = item.details['child_insert_offset']
                edits[path].extend([(offset,offset+4,struct.pack('<I',len(children)+len(additions))),
                                    (insertion,insertion,b''.join(struct.pack('<Q',uid) for uid in additions))])
        additions = [clones[uid] for uid in parsed.visibility_children if uid in clones]
        if additions:
            offset = parsed.visibility_children_offset
            edits[path].append((offset,len(data),struct.pack('<I',len(parsed.visibility_children)+len(additions))
                                + data[offset+4:] + b''.join(struct.pack('<Q',uid) for uid in additions)))
    for path in sorted(set(edits) | set(new_items)):
        data, parsed = sectors[path]
        operations = list(edits[path])
        if new_items[path]:
            combined_nodes = [n.raw for n in parsed.nodes] + new_nodes[path]
            combined_nodes.sort(key=lambda raw: struct.unpack_from('<Q', raw)[0])
            operations.extend([(16,20,struct.pack('<I',parsed.item_count+len(new_items[path]))),
                               (parsed.node_count_offset, parsed.visibility_children_offset,
                                b''.join(new_items[path])+struct.pack('<I',len(combined_nodes))
                                + b''.join(combined_nodes))])
        changed = _splice(data, operations)
        checked = parse_sector(changed)
        originals = {i.uid: data[i.offset:i.end] for i in parsed.items}
        after = {i.uid: changed[i.offset:i.end] for i in checked.items}
        for item in parsed.items:
            if _is_fuel(item) and originals[item.uid] != after[item.uid]:
                raise ValueError('Original fuel service bytes were not preserved')
        before_nodes = {n.uid:n.raw for n in parsed.nodes}; after_nodes={n.uid:n.raw for n in checked.nodes}
        if any(after_nodes[uid] != raw for uid,raw in before_nodes.items()):
            raise ValueError('Original node bytes were not preserved')
        resources[path] = changed
        report['changed_sectors'].append({'path':path,'source_package':str(stack.resources[path][0].path),
                                         'source_sha256':_sha(data),'output_sha256':_sha(changed),
                                         'added_items':len(new_items[path]),'added_nodes':len(new_nodes[path])})
    for stem in sorted({p.rsplit('.',1)[0] for p in new_items if new_items[p]}):
        path = stem+'.layer'
        if path in stack.resources:
            original = stack.read(path)
            changed = extend_layer(original, clones)
            if changed != original:
                resources[path] = changed
    if not blockers:
        # Validate the resulting graph independently of the edit counters.
        # All original truck points must have an exact-transform car twin,
        # and every new object must be linked back by its resolved parent.
        after_items = dict(items)
        after_nodes = {uid:list(values) for uid,values in nodes.items()}
        for path, data in resources.items():
            if not path.endswith(('.base', '.aux')):
                continue
            checked = parse_sector(data)
            for item in checked.items:
                after_items[item.uid] = path, item
            for node in checked.nodes:
                after_nodes.setdefault(node.uid, []).append((path, node))
        def placed_node(uid, path):
            candidates = after_nodes.get(uid, [])
            same_file = [node for candidate_path,node in candidates if candidate_path == path]
            if same_file:
                return same_file[-1]
            if not candidates or len({node.raw for _,node in candidates}) != 1:
                raise ValueError('Result has an unresolved/ambiguous fuel node')
            return candidates[-1][1]
        car_services = defaultdict(list)
        for path,item in after_items.values():
            if _is_fuel(item) and item.flags & 0x4000:
                car_services[item.details['parent']].append((path,item))
        for uid in eligible_trucks:
            path,truck = after_items[uid]
            original_path,original = items[uid]
            original_bytes = sectors[original_path][0][original.offset:original.end]
            after_data = resources.get(path, sectors[path][0])
            if after_data[truck.offset:truck.end] != original_bytes:
                raise ValueError('Truck record changed during final graph validation')
            transform = placed_node(truck.details['node'], path).raw[8:36]
            if not any(placed_node(car.details['node'], car_path).raw[8:36] == transform
                       for car_path,car in car_services[truck.details['parent']]):
                raise ValueError(f'Truck point {uid:#x} lacks a car counterpart in the output graph')
        if selective:
            for parent_uid, ppd_data, appended_count in descriptor_checks:
                parent_path, parent = after_items[parent_uid]
                linked = [after_items[uid][1] for uid in parent.details['slaves']
                          if uid in after_items and _is_fuel(after_items[uid][1])]
                # Preserve known unlisted legacy FuelPump relationships.
                linked.extend(item for _, item in after_items.values() if _is_fuel(item)
                              and item.details['parent'] == parent_uid and item.uid not in parent.details['slaves'])
                resolved = {uid: placed_node(uid, parent_path) for uid in parent.details['nodes']}
                for service in linked:
                    resolved[service.details['node']] = placed_node(service.details['node'], after_items[service.uid][0])
                matched = match_gas_services(ppd_data, parent, resolved, linked, allow_missing_car=True)
                count = inspect_ppd(ppd_data)['spawn_count']
                if any(index not in matched for index in range(count - appended_count, count)):
                    raise ValueError('Appended car GAS locator lacks its placed service')
        for old,new in clones.items():
            path,car = after_items[new]
            _,parent = after_items[car.details['parent']]
            node = placed_node(car.details['node'], path)
            if new not in parent.details['slaves'] or node.forward != new or node.backward:
                raise ValueError('New car service lacks reciprocal parent/node links')
        report['static_validation'] = {'truck_points_with_car_counterparts':len(eligible_trucks),
                                       'new_services_with_reciprocal_links':len(clones),
                                       'original_fuel_and_node_bytes_preserved':True}
    coverage['complete'] = not blockers
    report['sectors_inspected_with_neighbors'] = len(inspected)
    return report, resources
