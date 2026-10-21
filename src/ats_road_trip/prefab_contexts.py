"""Preserve effective context classifications across generated prefab aliases.

Only model substitutions proven by the planned sector bytes are considered.
No classification is inferred from prefab names, assets, or company records.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import re

from .local_fuel import token
from .map_sector import parse_sector
from .package import ResourceStack
from .sii import DefinitionError, parse_units


_CONTEXTS = r'def/data_context(?:\.[^/]+)?\.sii'
_PRIVATE_DEFS = re.compile(r'def/world/prefab\.[^/]+\.sii')
_EXCLUDED = re.compile(r'^\s*#\s*[^\n]*?(prefab\.[a-z0-9_]+)[^\n]*?excluded\b', re.I | re.M)
_UNIT = re.compile(r'[a-z0-9_]{1,12}(?:\.[a-z0-9_]{1,12})*')
_TAG = re.compile(r'[a-z0-9_]{1,12}')


def _private_definitions(resources: dict[str, bytes]) -> dict[int, str]:
    names: dict[int, str] = {}
    for path in sorted(resources):
        if not _PRIVATE_DEFS.fullmatch(path):
            continue
        for unit in parse_units(resources[path].decode('utf-8-sig'), source=path):
            if unit.kind != 'prefab_model':
                continue
            descriptor = unit.one('prefab_desc', '') or ''
            if not descriptor.startswith('/prefab/rtfix/'):
                continue
            if not _UNIT.fullmatch(unit.name) or not unit.name.startswith('prefab.'):
                raise DefinitionError(f'{path}: invalid generated prefab identifier {unit.name}')
            uid = token(unit.name.removeprefix('prefab.'))
            if uid in names:
                raise DefinitionError(f'Generated prefab token collision: {unit.name} and {names[uid]}')
            names[uid] = unit.name
    return names


def _effective_prefabs(stack: ResourceStack) -> dict[int, str]:
    # The existing planners already load and validate this effective index.
    from .bulk_fuel import prefab_definitions
    return {uid: entry[0].name for uid, entry in prefab_definitions(stack).items()}


def _contexts(stack: ResourceStack) -> tuple[dict[str, list[dict]], set[str], set[str]]:
    contexts: dict[str, list[dict]] = defaultdict(list)
    names: set[str] = set()
    excluded: set[str] = set()
    stack.prefetch(_CONTEXTS)
    for path in stack.matching(_CONTEXTS):
        contents = stack.text(path)
        excluded.update(_EXCLUDED.findall(contents))
        package = stack.resources[path][1].package
        for unit in parse_units(contents, source=path, include_reader=stack.text):
            if unit.kind != 'data_context':
                continue
            if unit.name in names:
                raise DefinitionError(f'Duplicate effective data_context unit: {unit.name}')
            names.add(unit.name)
            tags = tuple(unit.values('tags'))
            for target in unit.values('target_data'):
                if target.startswith('prefab.'):
                    contexts[target].append({'tags': tags, 'unit': unit.name,
                                             'resource': path, 'package': package})
    return dict(contexts), names, {name.lower() for name in excluded}


def plan_prefab_contexts(
    effective: ResourceStack,
    resources: dict[str, bytes],
    transitions: list[tuple[str, str, bytes, bytes]],
    *, source: str, map_name: str, planning_cache: dict | None = None,
) -> tuple[dict, dict[str, bytes]]:
    """Plan one additive context file for all fuel/rest alias transitions.

    Each transition is ``(processor, sector_path, bytes_before, bytes_after)``.
    The first non-generated model in each UID's chain is the classification
    source. Every generated alias is audited, including an intermediate alias
    later replaced by another processor. ``planning_cache`` may be shared only
    among immutable input stack objects in one planning run.
    """
    report = {'schema_version': 1, 'analysis': 'generated_prefab_context_preservation',
              'aliases': [], 'blockers': [], 'coverage': {}}
    blockers = report['blockers']
    try:
        private = _private_definitions(resources)
    except (ValueError, UnicodeError) as exc:
        blockers.append({'area': 'prefab_definition', 'reason': str(exc)})
        private = {}
    if not private and not blockers:
        report['coverage'] = {'complete': True, 'aliases_seen': 0, 'aliases_classified': 0,
                              'aliases_unclassified': 0, 'blockers': []}
        return report, {}
    if blockers:
        report['coverage'] = {'complete': False, 'blockers': blockers}
        return report, {}

    try:
        cache={} if planning_cache is None else planning_cache
        indexes=cache.setdefault('context_stack_indexes',{})
        # Keep the stack itself alive, preventing object-ID reuse. A staged
        # overlay is immutable for one planning pass; a new overlay requires
        # a distinct index even when it wraps the same original packages.
        if id(effective) not in indexes:
            original=_effective_prefabs(effective)
            contexts,occupied_names,excluded=_contexts(effective)
            indexes[id(effective)]=(effective,original,contexts,occupied_names,excluded)
        _,original,contexts,occupied_names,excluded=indexes[id(effective)]
        # Returned reports expose context records; isolate those from the
        # reusable source index so caller annotations cannot corrupt the cache.
        contexts=deepcopy(contexts)
    except (ValueError, KeyError, UnicodeError) as exc:
        blockers.append({'area': 'effective_definitions', 'reason': str(exc)})
        report['coverage'] = {'complete': False, 'blockers': blockers}
        return report, {}

    lineage: dict[int, tuple[str, str, str]] = {}
    observations: dict[str, list[dict]] = defaultdict(list)
    for processor, path, before_bytes, after_bytes in transitions:
        try:
            before = {item.uid: item for item in parse_sector(before_bytes).prefabs}
            after = {item.uid: item for item in parse_sector(after_bytes).prefabs}
            if set(before) != set(after):
                raise ValueError('Prefab UID set changed during processor composition')
            for uid in sorted(before):
                old = before[uid].details['model']
                new = after[uid].details['model']
                if old == new:
                    continue
                if new not in private:
                    # Only private aliases emitted by these processors need a
                    # generated context. Other model substitutions are outside
                    # this planner's ownership and remain visible as blockers.
                    raise ValueError(f'Changed prefab {uid:#x} targets an unowned model token {new:#x}')
                if old in private:
                    if old not in lineage:
                        raise ValueError(f'Unknown lineage for chained alias {private[old]}')
                    source_name = lineage[old][0]
                else:
                    if old not in original:
                        raise ValueError(f'Original model token {old:#x} has no effective definition')
                    source_name = original[old]
                candidate = (source_name, path, hex(uid))
                if new in lineage and lineage[new][0] != source_name:
                    raise ValueError(f'Alias {private[new]} has conflicting original models')
                lineage[new] = candidate
                observations[private[new]].append({'processor': processor, 'sector': path,
                                                   'prefab_uid': hex(uid), 'source': source_name,
                                                   'from': private.get(old, original.get(old))})
        except (ValueError, KeyError) as exc:
            blockers.append({'area': 'sector_lineage', 'processor': processor,
                             'path': path, 'reason': str(exc)})

    for uid, alias in sorted(private.items(), key=lambda pair: pair[1]):
        if uid not in lineage:
            blockers.append({'area': 'alias_coverage', 'alias': alias,
                             'reason': 'Generated alias has no proven placement transition'})

    namespace = hashlib.sha256((map_name + '\0' + source).encode()).hexdigest()[:12]
    target_path = f'def/data_context.rtf{namespace}.sii'
    if target_path in effective.resources or target_path in resources:
        blockers.append({'area': 'resource_collision', 'path': target_path,
                         'reason': 'Map-specific generated context resource already exists'})

    rendered: list[tuple[str, str, tuple[str, ...]]] = []
    for uid, alias in sorted(private.items(), key=lambda pair: pair[1]):
        if uid not in lineage:
            continue
        source_name = lineage[uid][0]
        source_contexts = contexts.get(source_name, [])
        alias_contexts = contexts.get(alias, [])
        row = {'alias': alias, 'original': source_name,
               'placements': observations[alias], 'original_contexts': source_contexts,
               'existing_alias_contexts': alias_contexts}
        report['aliases'].append(row)
        if source_name.lower() in excluded:
            if any(context['tags'] for context in source_contexts):
                row['status'] = 'blocked'
                blockers.append({'area': 'exclusion_context_conflict', 'alias': alias,
                                 'original': source_name,
                                 'reason': 'Exclusion comment coexists with live original context tags'})
            elif alias_contexts:
                row['status'] = 'blocked'
                blockers.append({'area': 'alias_context_conflict', 'alias': alias,
                                 'original': source_name,
                                 'reason': 'Excluded original has an existing alias context'})
            else:
                row['status'] = 'excluded'
            continue
        distinct = {tuple(sorted(set(context['tags']))) for context in source_contexts}
        if len(distinct) > 1:
            row['status'] = 'blocked'
            blockers.append({'area': 'context_conflict', 'alias': alias, 'original': source_name,
                             'reason': 'Original has conflicting effective context tag sets'})
            continue
        # Keep the source unit's exact tag sequence once all effective units
        # agree on membership; array order and repeated entries stay intact.
        tags = source_contexts[0]['tags'] if distinct else ()
        if not tags:
            if alias_contexts:
                row['status'] = 'blocked'
                blockers.append({'area': 'alias_context_conflict', 'alias': alias,
                                 'original': source_name,
                                 'reason': 'Unclassified original has an existing alias context'})
            else:
                row['status'] = 'unclassified'
            continue
        if any(not _TAG.fullmatch(tag) for tag in tags):
            row['status'] = 'blocked'
            blockers.append({'area': 'unsupported_tags', 'alias': alias, 'original': source_name})
            continue
        if alias_contexts:
            existing_sets = {tuple(sorted(set(context['tags']))) for context in alias_contexts}
            if existing_sets != {tuple(sorted(set(tags)))}:
                row['status'] = 'blocked'
                blockers.append({'area': 'alias_context_conflict', 'alias': alias,
                                 'reason': 'Existing alias context differs from original'})
            else:
                row['status'] = 'already_classified'
            continue
        name = 'context.rtf' + hashlib.sha256((namespace + '\0' + alias).encode()).hexdigest()[:9]
        if name in occupied_names or any(entry[0] == name for entry in rendered):
            row['status'] = 'blocked'
            blockers.append({'area': 'unit_collision', 'alias': alias, 'unit': name})
            continue
        row.update({'status': 'preserved', 'generated_unit': name, 'tags': list(tags)})
        rendered.append((name, alias, tags))

    output: dict[str, bytes] = {}
    if rendered and not blockers:
        lines = ['SiiNunit', '{']
        for name, alias, tags in rendered:
            lines.extend([f'data_context : {name}', '{', f' target_data[]: {alias}'])
            lines.extend(f' tags[]: {tag}' for tag in tags)
            lines.extend(['}', ''])
        lines.extend(['}', ''])
        output[target_path] = '\n'.join(lines).encode('utf-8')
    report['generated_resource'] = target_path if output else None
    report['coverage'] = {'complete': not blockers, 'aliases_seen': len(report['aliases']),
                          'aliases_classified': sum(row['status'] in ('preserved', 'already_classified') for row in report['aliases']),
                          'aliases_unclassified': sum(row['status'] in ('unclassified', 'excluded') for row in report['aliases']),
                          'blockers': blockers}
    return report, output
