"""Plan and generate bounded descriptor candidates, not live map modifications."""

from __future__ import annotations

from .mod_writer import sha256
from .package import ResourceStack, virtual_path
from .ppd import PpdError, add_petrol_spawns, inspect_ppd


def plan_fuel(stack: ResourceStack, paths: list[str]) -> tuple[dict, dict[str, bytes]]:
    changes: dict[str, bytes] = {}
    results: list[dict] = []
    if not paths:
        raise ValueError('Select at least one descriptor path or a PPD prefix')
    for path in sorted(set(paths)):
        path = virtual_path(path)
        if not path.lower().endswith('.ppd'):
            raise ValueError(f'Expected a PPD descriptor: {path}')
        source = stack.resources.get(path)
        if source is None:
            raise ValueError(f'Descriptor is not in the declared package stack: {path}')
        _, resource = source
        original = stack.read(path)
        item: dict = {'path': path, 'source_package': resource.package,
                      'source_path': resource.physical_path, 'source_sha256': sha256(original)}
        try:
            item['inspection'] = inspect_ppd(original)
            if item['inspection']['fuel']['gas_spawn_count'] == 0:
                item['status'] = 'no_fuel_locators'
            else:
                patched, mutation = add_petrol_spawns(original)
                item['mutation'] = mutation
                if mutation['added_count']:
                    changes[path] = patched
                    item['status'] = 'experimental_candidate'
                    item['result_sha256'] = sha256(patched)
                else:
                    item['status'] = 'already_has_matching_flag_one_locators'
        except PpdError as exc:
            item['status'] = 'unsupported'
            item['reason'] = str(exc)
        results.append(item)
    return ({'schema_version': 1, 'analysis': 'experimental_fuel_descriptor_candidates',
             'experimental': True, 'in_game_verified': False,
             'package_order': [str(p.path) for p in stack.packages],
             'limitations': ['Flag 1 as car/petrol support is inferred from ATS 1.61 station descriptor comparisons.',
                             'The generator duplicates existing flag-0 GAS transforms and preserves truck locators.',
                             'Placed map service items/spawn caches may also need rebuilding; this tool does not edit sectors.',
                             'Pump reachability and runtime interactions are not validated.',
                             'Versions 23/24 are inspected but never automatically upgraded.',
                             'Selection scope is explicit paths/prefixes, not every station in the map.'],
             'candidate_count': len(changes), 'descriptors': results}, changes)
