"""Standalone source-pinned tank upgrades; never installs or edits a profile."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from .archive import Archive
from .bulk_run import _game_directory, _game_packages, _game_version
from .mod_writer import write_mod
from .package import Package, ResourceStack

REPO_ROOT = Path(__file__).resolve().parents[2]
TITLE = "szczerb's Road Trip reasonable gas tank upgrades"
SLUG = 'reasonable-gas-tank-upgrades'


def tank_description(report: dict, revision: int) -> str:
    names = {'ford.mustang_67': 'Mustang 1967', 'ford.victoria_06': 'Crown Victoria 2006',
             'ford.f150_23': 'F-150 2023', 'ford.bronco_24': 'Bronco 2024'}
    changes = [f"{names[v['model']]}: {v['stock_liters']} -> {v['target_liters']} litres."
               for v in report['vehicles'] if v['status'] == 'upgraded']
    unchanged = [names[v['model']] for v in report['vehicles'] if v['status'] == 'unchanged']
    return ('Reasonable, researched fuel tank capacity upgrades for the Road Trip Ford DLC.\n\n'
            + '\n'.join(changes) + '\n\n'
            + ('Unchanged: ' + ', '.join(unchanged) + '.\n\n' if unchanged else '')
            + 'Applies to the existing chassis automatically; there is no separate shop purchase. '
              'Fuel consumption and other chassis settings are preserved.\n\n'
              'LOAD ORDER (higher priority = closer to the top):\n'
              'Reasonable gas tank upgrades (THIS MOD)\n'
              'Other vehicle mods that do not replace these chassis definitions\n'
              'Job Types Compat Mustang and map fixes can stay in their existing positions.\n\n'
              'Disable the old 3x tank mod and other tank/chassis capacity overrides. '
              'A higher-priority replacement of the same chassis file wins in full.\n\n'
            + f'ATS 1.61 / Ford DLC required. Version 1.61-r{revision}-experimental. '
              'Capacity display, existing fuel after switching mods, refueling/payment and save/reload '
              'still require manual testing. This is a capacity simulation; no visible tank model is added.\n')


def run_tank_upgrades(config, *, generate=False, game_dir=None, dependency=(),
                      revision=0, run_id=None, extractor=None, icon=None):
    if type(generate) is not bool or type(revision) is not int or revision < 0:
        raise ValueError('generate must be boolean and revision a nonnegative integer')
    config = Path(config).expanduser().resolve()
    if not config.is_file():
        raise ValueError('Tank upgrade configuration file is missing')
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('Run ID must use YYYY-MM-DD_HH-MM-SS')
    work = REPO_ROOT / 'local_outputs/work' / stamp / (SLUG if generate else SLUG + '-analysis')
    output = REPO_ROOT / 'local_outputs/generated' / stamp / (
        f'szczerbs-road-trip-{SLUG}-1.61-r{revision}-experimental.scs')
    audit_path = work / 'audit.json'
    if audit_path.exists() or (generate and output.exists()):
        raise FileExistsError('Run audit or package already exists; choose a new run ID')
    work.mkdir(parents=True, exist_ok=True)
    previous_root = Archive._work_root
    Archive.configure_work_root(work)
    workflow = {'run_id': stamp, 'work_dir': str(work), 'config': str(config),
                'operation': 'generate' if generate else 'analysis_only'}

    def save(audit):
        with audit_path.open('x', encoding='utf-8') as stream:
            json.dump(audit, stream, indent=2, sort_keys=True)
            stream.write('\n')

    try:
        installed = _game_directory(game_dir)
        version = _game_version(installed, extractor)
        _, dlcs = _game_packages(installed)
        dependencies = [Path(p).expanduser().resolve() for p in dependency]
        if any(not p.is_file() for p in dependencies):
            raise ValueError('Use existing immutable archives for tank dependencies')
        order = [installed / 'def.scs', installed / 'dlc_rt_ford.scs', *dependencies]
        if len(set(order)) != len(order):
            raise ValueError('Definition packages must not be repeated')
        version_path = installed / ('version.sii' if (installed / 'version.sii').is_file() else 'version.scs')
        identity_paths = [config, version_path, *order]
        if generate:
            icon = icon if icon is not None else REPO_ROOT / 'assets/mod-icons/reasonable-gas-tank-upgrades.jpg'
            if isinstance(icon, (str, Path)):
                icon = Path(icon).expanduser().resolve()
                if not icon.is_file():
                    raise ValueError('Tank icon file is missing')
                identity_paths.append(icon)
        identities = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in identity_paths}
        workflow.update({'game_dir': str(installed), 'game_version': version,
                         'packages_low_to_high': [str(p) for p in order],
                         'config_sha256': hashlib.sha256(config.read_bytes()).hexdigest(),
                         'source_package_identities': [
                             {'path': str(p), 'size': size, 'mtime_ns': mtime}
                             for p, (size, mtime) in identities.items()],
                         'load_order_assumption': 'Declared archives, not an observed active profile.'})
        with ExitStack() as manager:
            packages = [manager.enter_context(Package(p, extractor=extractor, dlcs=dlcs)) for p in order]
            from .tank_upgrades import plan_tank_upgrades
            report, resources = plan_tank_upgrades(ResourceStack(packages), config, game_version=version)
        for p, identity in identities.items():
            if (p.stat().st_size, p.stat().st_mtime_ns) != identity:
                raise ValueError(f'Source changed during tank analysis: {p}')
        audit = {'workflow': workflow, 'planner': report, 'analysis_only': not generate,
                 'in_game_verified': False, 'generated_mod_count': 0,
                 'planned_resource_count': len(resources), 'report_path': str(audit_path)}
        blocked = report.get('coverage', {}).get('blockers') or report.get('coverage', {}).get('complete') is not True
        if not generate:
            audit['status'] = 'reported_partial' if blocked else 'reported'
        elif blocked:
            audit['status'] = 'blocked'
            save(audit)
            raise ValueError('Tank upgrade blockers prevent packaging; read ' + str(audit_path))
        elif not resources:
            audit['status'] = 'already_covered'
        else:
            allowed = {v['path'] for v in report['vehicles'] if v['status'] == 'upgraded'}
            if set(resources) != allowed:
                raise ValueError('Tank planner emitted unexpected resource paths')
            icon_bytes = icon.read_bytes() if isinstance(icon, Path) else icon
            package = write_mod(output, resources, {'workflow': workflow, 'planner': report},
                                game_version=version, display_name=TITLE, revision=revision,
                                category='other', description=tank_description(report, revision), icon=icon_bytes)
            audit.update({'status': 'generated', 'generated_mod_count': 1, 'output': str(output),
                          'package_metadata': package['package_metadata'],
                          'sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        save(audit)
        return audit
    except Exception as exc:
        if not audit_path.exists():
            save({'status': 'failed', 'workflow': workflow, 'analysis_only': not generate,
                  'generated_mod_count': 0, 'error': str(exc)})
        raise
    finally:
        Archive._work_root = previous_root
