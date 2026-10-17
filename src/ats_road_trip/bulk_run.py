"""One-source map-wide fuel generation with explicit game and map inputs.

The workflow reads installed ATS packages and supplied map archives, writes an
audit beneath ignored local_outputs/work, and emits a package only when the
planner reports complete supported coverage. It never touches game profiles.
"""

from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import logging
import os
from pathlib import Path
import re

from .archive import Archive, ArchiveError
from .mod_writer import write_mod
from .package import Package, ResourceStack
from .petrol_policy import DEFAULT_REFERENCE, build_policy
from .petrol_prices import plan_petrol_prices


REPO_ROOT = Path(__file__).resolve().parents[2]
_STEAM_WSL = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/American Truck Simulator')
_BASE_PACKAGES = ('base.scs', 'base_share.scs', 'base_map.scs', 'def.scs')


def _game_directory(game_dir: str | Path | None) -> Path:
    candidates = [game_dir] if game_dir is not None else [os.environ.get('ATS_GAME_DIR'), _STEAM_WSL]
    for candidate in candidates:
        if candidate is None:
            continue
        path = Path(candidate).expanduser().resolve()
        if path.is_dir() and (path / 'version.scs').is_file():
            return path
    raise ValueError('ATS game directory with version.scs was not found; pass --game-dir or set ATS_GAME_DIR')


def _game_version(game_dir: Path, extractor: str | Path | None) -> str:
    direct = game_dir / 'version.sii'
    if direct.is_file():
        data = direct.read_bytes()
    else:
        with Archive(game_dir / 'version.scs', extractor=extractor) as version:
            data = version.read('version.sii', max_bytes=1024 * 1024)
    text = data.decode('utf-8-sig')
    if not re.search(r'(?m)^\s*application\s*:\s*ats\s*$', text):
        raise ValueError('Installed version.sii does not identify ATS')
    match = re.search(r'(?m)^\s*version\s*:\s*"([^"]+)"\s*$', text)
    if match is None or not re.fullmatch(r'1\.61(?:\.\d+)*', match.group(1)):
        raise ValueError('Map-wide generator requires an installed ATS 1.61 version')
    return match.group(1)


def _game_packages(game_dir: Path) -> tuple[list[Path], tuple[str, ...]]:
    base = [game_dir / name for name in _BASE_PACKAGES]
    missing = [str(path) for path in base if not path.is_file()]
    if missing:
        raise ValueError('Installed ATS baseline is incomplete: ' + ', '.join(missing))
    # Short tokens are state/map DLCs; the two historical long names are also
    # map DLCs. This excludes vehicle, paint, cargo and accessory archives.
    maps = sorted(path for path in game_dir.glob('dlc_*.scs')
                  if re.fullmatch(r'dlc_(?:[a-z]{2}|arizona|nevada)\.scs', path.name))
    road_trip = game_dir / 'dlc_rt_ford.scs'
    if not road_trip.is_file():
        raise ValueError('Installed Road Trip Ford DLC (dlc_rt_ford.scs) is required')
    packages = [*base, *maps, road_trip]
    return packages, tuple(path.stem for path in [*maps, road_trip])


def _profile(source: Path) -> tuple[str | None, tuple[tuple[str, ...], ...]]:
    name = source.name.lower()
    if name.startswith('ats_expansion'):
        return 'ATS Expansion', ()
    if name.startswith('alaska_expansion'):
        return 'Alaska', ()
    if name.startswith('reforma_othermaps_patch_'):
        return 'Reforma OtherMaps Patch', (('Reforma_MegaResources*.scs',),
                                          ('Reforma_[0-9]*.scs',))
    if re.match(r'reforma_(?:v)?\d', name):
        return 'Reforma', (('Reforma_MegaResources*.scs',),)
    if name.startswith('promods-ats-map-'):
        return 'ProMods Canada', (('promods-ats-assets-*.scs',),
                                   ('promods-ats-models-*.scs',),
                                   ('promods-ats-def-*.scs',))
    if name.startswith('western_canada_promods_connections_'):
        # In the user's observed profile, Western Canada is below ProMods;
        # within ProMods the low-to-high order is models, assets, map, def.
        # Explicit --dependency order remains authoritative.
        return 'Western Canada ProMods Connections', (
            ('Western_Canada_Expansion*.scs',),
            ('promods-ats-models-*.scs',), ('promods-ats-assets-*.scs',),
            ('promods-ats-map-*.scs',), ('promods-ats-def-*.scs',))
    if name.startswith('western_canada_expansion'):
        # Western Canada can use the ProMods stack if the complete companion
        # set is supplied next to it. A partial set is an ambiguous input.
        return 'Western Canada', ()
    return None, ()


def _one_sibling(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one sibling {pattern}; found {len(matches)}')
    return matches[0].resolve()


def _map_packages(source: Path, dependency: list[str]) -> list[Path]:
    label, required = _profile(source)
    supplied = [Path(path).expanduser().resolve() for path in dependency]
    if any(not path.is_file() for path in supplied):
        raise ValueError('An explicit dependency archive is missing')
    if source in supplied:
        raise ValueError('Source archive must be highest; do not repeat it as a dependency')
    # Resolve one archive for each known slot. The caller's explicit sequence is
    # already low-to-high; missing companions are inserted around those slots
    # instead of being appended above explicitly supplied maps.
    if label == 'Western Canada':
        patterns = ('promods-ats-assets-*.scs', 'promods-ats-models-*.scs',
                    'promods-ats-def-*.scs', 'promods-ats-map-*.scs')
        found = []
        for pattern in patterns:
            explicit = [path for path in supplied if path.match(pattern)]
            siblings = sorted(source.parent.glob(pattern)) if not explicit else []
            if len(explicit) > 1 or len(siblings) > 1:
                raise ValueError(f'Ambiguous Western Canada companion {pattern}')
            found.append(bool(explicit or siblings))
        if any(found) and not all(found):
            raise ValueError('Western Canada has an incomplete ProMods companion set')
        if all(found):
            required = tuple((pattern,) for pattern in patterns)
    slots: list[Path] = []
    for group in required:
        matches = [path for path in supplied if any(path.match(pattern) for pattern in group)]
        if len(matches) > 1:
            raise ValueError(f'Ambiguous explicit companion {group[0]}')
        slots.append(matches[0] if matches else _one_sibling(source.parent, group[0]))
    result = list(dict.fromkeys(supplied))
    for index, path in enumerate(slots):
        if path in result:
            continue
        later = [result.index(other) for other in slots[index + 1:] if other in result]
        earlier = [result.index(other) for other in slots[:index] if other in result]
        position = min(later) if later else (max(earlier) + 1 if earlier else 0)
        result.insert(position, path)
    result.append(source)
    return result


def _run_paths(map_name: str, revision: int, run_id: str | None) -> tuple[Path, Path, str]:
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9 ._\-]{0,63}', map_name) or map_name != map_name.strip():
        raise ValueError('Map name must be a short plain-text name')
    if type(revision) is not int or revision < 0:
        raise ValueError('Revision must be a nonnegative integer')
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('Run ID must use YYYY-MM-DD_HH-MM-SS')
    slug = re.sub(r'[^a-z0-9]+', '-', map_name.lower()).strip('-')
    work = REPO_ROOT / 'local_outputs/work' / stamp / slug
    output = (REPO_ROOT / 'local_outputs/generated' / stamp /
              f'szczerbs-road-trip-gas-stations-fix-{slug}-1.61-r{revision}-experimental.scs')
    return work, output, stamp


def _write_audit(path: Path, audit: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(audit, stream, indent=2, sort_keys=True)
        stream.write('\n')


def generate_map_fuel(source, *, game_dir=None, map_name=None, revision=2,
                      run_id=None, extractor=None, dependency: list[str] = (),
                      icon=None, petrol_reference=DEFAULT_REFERENCE) -> dict:
    """Audit one supplied map and emit a complete experimental fuel package.

    Explicit dependencies retain their low-to-high order. Known missing
    companions are inserted into their family slots, with the source highest.
    The actual profile load order is unknown and recorded for review.
    """
    from .bulk_fuel import plan_map_fuel

    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f'Map source archive does not exist: {source}')
    inferred, _ = _profile(source)
    name = map_name or inferred
    if name is None:
        raise ValueError('Unknown map archive name; pass --map-name')
    if icon is None:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        icon_slug = {'reforma-othermaps-patch': 'reforma',
                     'western-canada-promods-connections': 'western-canada'}.get(slug, slug)
        preset = REPO_ROOT / 'assets/mod-icons' / f'{icon_slug}-c.jpg'
        if preset.is_file():
            icon = preset
    work, output, stamp = _run_paths(name, revision, run_id)
    if (work / 'audit.json').exists() or output.exists():
        raise FileExistsError('Run audit or generated package already exists; choose a new run ID')
    work.mkdir(parents=True, exist_ok=True)
    prior_work_root = Archive._work_root
    Archive.configure_work_root(work)
    try:
        installed = _game_directory(game_dir)
        version = _game_version(installed, extractor)
        game_paths, dlcs = _game_packages(installed)
        maps = _map_packages(source, list(dependency))
        order = [*game_paths, *maps]
        version_input = installed / 'version.sii' if (installed / 'version.sii').is_file() else installed / 'version.scs'
        identity_paths = [version_input, *order]
        if isinstance(icon, (str, Path)):
            identity_paths.append(Path(icon).expanduser().resolve())
        identities = {path:(path.stat().st_size, path.stat().st_mtime_ns)
                      for path in identity_paths}
        workflow = {
            'run_id': stamp, 'map_name': name, 'source': str(source),
            'game_dir': str(installed), 'game_version': version,
            'packages_low_to_high': [str(path) for path in order],
            'target_map_package': str(source),
            'petrol_reference': petrol_reference,
            'owned_dlc_assumption': list(dlcs),
            'load_order_assumption': 'Declared order is a generation baseline, not a live profile observation.',
            'work_dir': str(work),
            'source_package_identities': [{'path':str(path), 'size':size, 'mtime_ns':mtime}
                                          for path,(size,mtime) in identities.items()],
        }
        with ExitStack() as manager:
            packages = []
            for index, path in enumerate(order, 1):
                logging.getLogger(__name__).info('%s: package %s/%s %s', name, index, len(order), path.name)
                packages.append(manager.enter_context(Package(path, extractor=extractor, dlcs=dlcs)))
            effective = ResourceStack(packages)
            game_only = ResourceStack(packages[:len(game_paths)])
            report, station_resources = plan_map_fuel(effective,
                                                      map_packages={str(source)}, map_name=name)
            policy, policy_report = build_policy(effective, game_only,
                                                 target_packages={str(source)},
                                                 reference_path=petrol_reference)
            price_report, price_resources = plan_petrol_prices(effective,
                                                               target_packages={str(source)},
                                                               policy=policy)
            price_report['policy'] = policy_report
            report['petrol_prices'] = price_report
            coverage = report.setdefault('coverage', {})
            blockers = list(coverage.get('blockers', report.get('blockers', [])))
            blockers.extend({'area': 'petrol_price_policy', **blocker}
                            for blocker in policy_report['coverage']['blockers'])
            blockers.extend({'area': 'petrol_prices', **blocker}
                            for blocker in price_report['coverage']['blockers'])
            conflicts = sorted(set(station_resources) & set(price_resources))
            blockers.extend({'area': 'resource_collision', 'path': path,
                             'reason': 'station and price planners emitted the same path'}
                            for path in conflicts)
            coverage['blockers'] = blockers
            coverage['complete'] = not blockers
            coverage['petrol_price_changed'] = price_report['coverage']['changed']
            resources = {**station_resources, **price_resources}
        for path, identity in identities.items():
            if (path.stat().st_size, path.stat().st_mtime_ns) != identity:
                raise ValueError(f'Source package changed during generation; retry from a stable stack: {path}')
        audit = {'workflow': workflow, 'planner': report,
                 'planned_resource_count': len(resources)}
        blockers = report['coverage']['blockers']
        if blockers:
            audit['status'] = 'blocked'
            _write_audit(work / 'audit.json', audit)
            raise ValueError(f'{name}: {len(blockers)} coverage blocker(s); see {work / "audit.json"}')
        if not resources:
            audit['status'] = 'already_covered'
            _write_audit(work / 'audit.json', audit)
            return audit
        icon_bytes = Path(icon).read_bytes() if isinstance(icon, (str, Path)) else icon
        description = (f'Experimental map-wide passenger-car refueling and petrol-price package for {name}.\n'
                       'Every supported missing truck fuel point receives a car interaction at the same position.\n'
                       'Country petrol prices may be restored from lower definitions or estimated from stock ATS ratios.\n'
                       'Keep this package above its listed source/dependency maps in a copied test profile.\n'
                       'Read road_trip_fix_report.json for coverage, source assumptions and static verification.\n'
                       'Gameplay and reload behavior outside the tested sample remain unverified.\n')
        # Time/run paths belong to the external audit, keeping generated mod
        # content stable across timestamped runs with identical source inputs.
        provenance = {k:v for k,v in workflow.items() if k not in ('run_id', 'work_dir')}
        full_report = {**report, 'workflow': provenance}
        written = write_mod(output, resources, full_report, game_version=version,
                            map_name=name, revision=revision, icon=icon_bytes,
                            description=description)
        audit.update({'status': 'generated', 'output': str(output), 'written_report': written})
        _write_audit(work / 'audit.json', audit)
        return audit
    except (ArchiveError, OSError, ValueError, KeyError) as exc:
        if not (work / 'audit.json').exists():
            _write_audit(work / 'audit.json', {'status':'failed', 'source':str(source),
                                             'map_name':name, 'run_id':stamp, 'error':str(exc)})
        raise
    finally:
        Archive.configure_work_root(prior_work_root)
