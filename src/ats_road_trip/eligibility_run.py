"""Standalone source-pinned courier eligibility workflow; no live installation."""
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
TITLE = "szczerb's Road Trip Practical Courier Jobs"


def run_courier_eligibility(config, *, generate=False, game_dir=None, dependency=(),
                            revision=2, run_id=None, extractor=None, icon=None):
    """Analyze a declared definition stack; optionally package its reviewed edits."""
    if type(generate) is not bool:
        raise ValueError('generate must be a boolean')
    if type(revision) is not int or revision < 0:
        raise ValueError('Revision must be a nonnegative integer')
    if generate and icon is None:
        from .mod_artwork import courier_icon
        icon = courier_icon(REPO_ROOT)
    config = Path(config).expanduser().resolve()
    if not config.is_file():
        raise ValueError('Courier eligibility configuration file is missing')
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('Run ID must use YYYY-MM-DD_HH-MM-SS')
    slug = 'practical-courier-jobs' + ('' if generate else '-analysis')
    work = REPO_ROOT / 'local_outputs/work' / stamp / slug
    output = REPO_ROOT / 'local_outputs/generated' / stamp / (
        f'szczerbs-road-trip-practical-courier-jobs-muscle-1.61-r{revision}-experimental.scs')
    audit_path = work / 'audit.json'
    if audit_path.exists() or (generate and output.exists()):
        raise FileExistsError('Run audit or generated package already exists; choose a new run ID')
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
        # Only definitions and the required vehicle DLC are relevant here.
        # No world-sector/base archive inspection is needed for this mod.
        dependencies = [Path(p).expanduser().resolve() for p in dependency]
        if any(not p.exists() for p in dependencies):
            raise ValueError('An explicit dependency package is missing')
        order = [installed / 'def.scs', installed / 'dlc_rt_ford.scs', *dependencies]
        if len(set(order)) != len(order):
            raise ValueError('Definition packages must not be repeated')
        version_path = installed / ('version.sii' if (installed / 'version.sii').is_file() else 'version.scs')
        identity_paths = [config, version_path, *order]
        if generate and isinstance(icon, (str, Path)):
            icon = Path(icon).expanduser().resolve()
            if not icon.is_file():
                raise ValueError('Courier icon file is missing')
            identity_paths.append(icon)
        if any(p.is_dir() for p in dependencies):
            raise ValueError('Use immutable dependency archives for the courier workflow')
        identities = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in identity_paths}
        workflow.update({'game_dir': str(installed), 'game_version': version,
                         'packages_low_to_high': [str(p) for p in order],
                         'config_sha256': hashlib.sha256(config.read_bytes()).hexdigest(),
                         'owned_dlc_assumption': list(dlcs),
                         'source_package_identities': [
                             {'path': str(p), 'size': size, 'mtime_ns': mtime}
                             for p, (size, mtime) in identities.items()],
                         'load_order_assumption': 'Declared archives, not an observed active profile.'})
        with ExitStack() as manager:
            packages = [manager.enter_context(Package(p, extractor=extractor, dlcs=dlcs)) for p in order]
            from .courier_eligibility import plan_courier_eligibility
            report, resources = plan_courier_eligibility(ResourceStack(packages), config,
                                                         game_version=version)
        for p, identity in identities.items():
            if (p.stat().st_size, p.stat().st_mtime_ns) != identity:
                raise ValueError(f'Source changed during courier analysis: {p}')
        audit = {'workflow': workflow, 'planner': report, 'analysis_only': not generate,
                 'in_game_verified': False, 'generated_mod_count': 0,
                 'planned_resource_count': len(resources), 'report_path': str(audit_path)}
        blockers = report.get('coverage', {}).get('blockers', [])
        incomplete = report.get('coverage', {}).get('complete') is not True
        if not generate:
            audit['status'] = 'reported_partial' if blockers or incomplete else 'reported'
        elif blockers or incomplete:
            audit['status'] = 'blocked'
            save(audit)
            raise ValueError('Courier eligibility coverage blockers prevent packaging; read ' + str(audit_path))
        elif not resources:
            audit['status'] = 'already_covered'
        else:
            if set(resources) != {'def/car_job_data.sii'}:
                raise ValueError('Courier eligibility planner emitted unexpected resource paths')
            from .mod_descriptions import courier_description
            description = courier_description(
                report.get('coverage', {}).get('selected_job_units', len(report.get('selected_job_ids', []))),
                report.get('coverage', {}).get('transfer_job_units', len(report.get('transfer_job_ids', []))),
                version='.'.join(version.split('.')[:2]) + f'-r{revision}-experimental')
            icon_bytes = icon.read_bytes() if isinstance(icon, Path) else icon
            package = write_mod(output, resources, {'workflow': workflow, 'planner': report},
                                game_version=version, display_name=TITLE, revision=revision,
                                category='other', description=description, icon=icon_bytes)
            audit.update({'status': 'generated', 'generated_mod_count': 1,
                          'output': str(output), 'package_metadata': package['package_metadata'],
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


def analyze_courier_eligibility(config, **kwargs):
    return run_courier_eligibility(config, generate=False, **kwargs)


def generate_courier_eligibility(config, **kwargs):
    return run_courier_eligibility(config, generate=True, **kwargs)
