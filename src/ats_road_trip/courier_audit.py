"""Static context coverage; deliberately does not predict playable job markets."""

from __future__ import annotations

from collections import Counter, defaultdict
from .package import ResourceStack
from .sii import DefinitionError, Unit, parse_units
import re


def _load(stack: ResourceStack, pattern: str, kind: str) -> list[Unit]:
    stack.prefetch(pattern)
    units: list[Unit] = []
    for path in stack.matching(pattern):
        units.extend(unit for unit in parse_units(stack.text(path), source=path,
                                                  include_reader=stack.text) if unit.kind == kind)
    return units


def audit_courier(stack: ResourceStack, *, map_packages: set[str]) -> dict:
    contexts = _load(stack, r'def/data_context(?:\.[^/]+)?\.sii', 'data_context')
    jobs = _load(stack, r'def/car_job_data(?:\.[^/]+)?\.sii', 'car_job_data')
    if not contexts or not jobs:
        raise DefinitionError('Context and car-job definitions are both required for coverage analysis')
    targets: dict[str, set[str]] = defaultdict(set)
    named: set[str] = set()
    for context in contexts:
        if context.name in named:
            raise DefinitionError(f'Duplicate data_context unit across resources: {context.name}')
        named.add(context.name)
        for target in context.values('target_data'):
            targets[target].update(context.values('tags'))
    source_jobs: dict[str, list[str]] = defaultdict(list)
    target_jobs: dict[str, list[str]] = defaultdict(list)
    for job in jobs:
        for tag in job.values('source_data_contexts'):
            source_jobs[tag].append(job.name)
        for tag in job.values('target_data_contexts'):
            target_jobs[tag].append(job.name)
    excluded: set[str] = set()
    for path in stack.matching(r'def/data_context(?:\.[^/]+)?\.sii'):
        for match in re.finditer(r'^\s*#\s*(prefab\.[\w]+)[^\n]*excluded', stack.text(path), re.M):
            excluded.add(match.group(1))
    details: list[dict] = []
    counts: Counter[str] = Counter()
    editor_pattern = r'def/company/[^/]+/editor/[^/]+\.sii'
    # Only prefetch map-owned editor definitions, not every official company.
    for package in stack.packages:
        if str(package.path) in map_packages:
            package.prefetch([path for path in stack.matching(editor_pattern)
                              if stack.resources[path][0] is package])
    for path in stack.matching(editor_pattern):
        package, resource = stack.resources[path]
        if str(package.path) not in map_packages:
            continue
        for unit in parse_units(stack.text(path), source=path, include_reader=stack.text):
            if unit.kind != 'company_def':
                continue
            token = unit.one('prefab')
            if not token:
                raise DefinitionError(f'{path}: company_def without prefab')
            prefab = token if token.startswith('prefab.') else 'prefab.' + token
            tags = sorted(targets.get(prefab, ()))
            sources = sorted({job for tag in tags for job in source_jobs[tag]})
            destinations = sorted({job for tag in tags for job in target_jobs[tag]})
            status = 'classified' if tags else ('explicitly_excluded' if prefab in excluded else 'unclassified')
            counts[status] += 1
            details.append({'company': path.split('/')[2], 'city': unit.one('city'), 'prefab': prefab,
                            'status': status, 'context_tags': tags,
                            'source_job_definitions': sources, 'target_job_definitions': destinations,
                            'source_package': resource.package, 'source_path': resource.physical_path,
                            'virtual_path': path})
    return {'schema_version': 1, 'analysis': 'static_context_coverage',
            'limitations': ['Context coverage is not in-game courier eligibility or job availability.',
                            'Placed map objects, spawn points, route links, rating, vehicle, DLCs, and market refresh are not validated.',
                            'Excluded prefabs are read from baseline comments and must not be automatically enabled.',
                            'Package order is supplied explicitly, lowest priority first.'],
            'package_order': [str(p.path) for p in stack.packages],
            'context_unit_count': len(contexts), 'job_unit_count': len(jobs),
            'counts': dict(sorted(counts.items())), 'company_definitions': details,
            'overridden_paths': stack.overrides}
