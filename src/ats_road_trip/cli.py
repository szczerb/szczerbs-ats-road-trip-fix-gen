"""Command-line entrypoint for repeatable research and experimental generation."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .archive import Archive, ArchiveError
from .courier_audit import audit_courier
from .fuel_generator import plan_fuel
from .mod_writer import write_mod
from .package import Package, PackageError, ResourceStack, virtual_path
from .petrol_policy import DEFAULT_REFERENCE
from .sii import DefinitionError


def _emit(data: dict, output: str | None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + '\n'
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8') as stream:
            stream.write(text)
    else:
        sys.stdout.write(text)


def _common_stack(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--package', action='append', required=True,
                        help='Resource package/directory, repeat lowest priority first')
    parser.add_argument('--dlc', action='append', default=[], help='Owned DLC mount token, e.g. dlc_wa')


def _fuel_metadata(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--map-name', required=True, help='Short map name shown in the mod manager, e.g. ATS Expansion')
    parser.add_argument('--revision', type=int, default=0, help='Experimental package revision (default: 0)')
    parser.add_argument('--icon', help='Optional 276x162 JPEG mod manager icon')


def _fuel_writer_options(args: argparse.Namespace) -> dict:
    return {'map_name': args.map_name, 'revision': args.revision,
            'icon': Path(args.icon).read_bytes() if args.icon else None}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description='ATS Road Trip compatibility research prototype')
    root.add_argument('--extractor', help='Path to the external Linux HashFS Extractor')
    sub = root.add_subparsers(dest='command', required=True)
    inventory = sub.add_parser('inspect', help='List archive metadata without extracting content')
    inventory.add_argument('archive')
    inventory.add_argument('--prefix', default='')
    inventory.add_argument('--output', help='Write JSON to a new file instead of stdout')
    extract = sub.add_parser('extract', help='Extract explicit members or a prefix to a separate directory')
    extract.add_argument('archive')
    extract.add_argument('--path', action='append', default=[])
    extract.add_argument('--prefix')
    extract.add_argument('--output', required=True)
    extract.add_argument('--max-bytes', type=int, default=16 * 1024 * 1024, help='Per-member limit')
    courier = sub.add_parser('courier-audit', help='Report static prefab context coverage')
    courier.add_argument('--baseline', action='append', required=True)
    courier.add_argument('--map', action='append', required=True)
    courier.add_argument('--dlc', action='append', default=[])
    courier.add_argument('--output')
    bulk = sub.add_parser('generate-map-fuel', help='Discover missing car fuel points in an entire source map')
    bulk.add_argument('source', help='Source map .scs; known companion packages are resolved beside it')
    bulk.add_argument('--game-dir', help='ATS installation; otherwise ATS_GAME_DIR or detected Steam location')
    bulk.add_argument('--map-name', help='Short map name; inferred for the five supplied map families')
    bulk.add_argument('--revision', type=int, default=2)
    bulk.add_argument('--run-id', help='Run folder timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
    bulk.add_argument('--dependency', action='append', default=[], help='Explicit additional package, lowest priority first')
    bulk.add_argument('--petrol-reference', default=DEFAULT_REFERENCE,
                      help='Game-only mounted country path for the petrol/diesel fallback ratio')
    bulk.add_argument('--icon', help='Optional map-labelled JPEG276x162')
    bulk.add_argument('--experimental', action='store_true')
    for name in ('fuel-audit', 'generate-fuel'):
        fuel = sub.add_parser(name, help='Inspect fuel descriptors' if name == 'fuel-audit' else 'Build experimental v25 fuel candidates')
        _common_stack(fuel)
        fuel.add_argument('--path', action='append', default=[], help='Exact virtual PPD path, repeat as needed')
        fuel.add_argument('--prefix', help='Select all PPDs below a virtual prefix')
        fuel.add_argument('--output', required=name.startswith('generate'))
        if name.startswith('generate'):
            fuel.add_argument('--game-version', required=True)
            fuel.add_argument('--experimental', action='store_true', help='Acknowledge unverified runtime behavior')
            _fuel_metadata(fuel)
    context = sub.add_parser('generate-context', help='Generate exact-model/descriptor courier alias candidates')
    context.add_argument('--baseline', action='append', required=True)
    context.add_argument('--map', action='append', required=True)
    context.add_argument('--dlc', action='append', default=[])
    context.add_argument('--output', required=True)
    context.add_argument('--game-version', required=True)
    context.add_argument('--experimental', action='store_true')
    context.add_argument('--prefab', action='append', help='Restrict generation to reviewed prefab identifiers')
    for name in ('generate-local-fuel', 'generate-overlap-fuel'):
        local = sub.add_parser(name, help='Build a pinned fuel conversion' if name == 'generate-local-fuel'
                              else 'Retain a truck point and add a car point at the same transform')
        local.add_argument('--baseline', action='append', required=True)
        local.add_argument('--map', required=True)
        local.add_argument('--recipe', required=True, help='Reviewed recipe JSON with exact source hashes and UIDs')
        local.add_argument('--dlc', action='append', default=[])
        local.add_argument('--output', required=True)
        local.add_argument('--game-version', required=True)
        local.add_argument('--experimental', action='store_true')
        _fuel_metadata(local)
    return root


def main(argv: list[str] | None = None) -> int:
    command = parser()
    args = command.parse_args(argv)
    try:
        if hasattr(args, 'path'):
            args.path = [virtual_path(p.lstrip('/')) for p in args.path]
        if getattr(args, 'prefix', None):
            prefix = args.prefix.lstrip('/')
            if prefix:
                virtual_path(prefix.rstrip('/'))
            args.prefix = prefix
        if args.command.startswith('generate') and not args.experimental:
            raise ValueError('Generation requires --experimental; no candidate is verified in game')
        if args.command == 'generate-map-fuel':
            import logging
            logging.basicConfig(level=logging.INFO, format='%(message)s')
            from .bulk_run import generate_map_fuel
            result = generate_map_fuel(args.source, game_dir=args.game_dir, map_name=args.map_name,
                                       revision=args.revision, run_id=args.run_id, extractor=args.extractor,
                                       dependency=args.dependency, icon=args.icon,
                                       petrol_reference=args.petrol_reference)
            _emit({'status': result['status'], 'output': result.get('output'),
                   'work_dir': result['workflow']['work_dir'],
                   'coverage': result['planner'].get('coverage')}, None)
            return 0
        if args.command == 'inspect':
            with Archive(args.archive, extractor=args.extractor) as archive:
                entries = archive.entries()
                filtered = [asdict(entry) for entry in entries if entry.path.startswith(args.prefix)]
                _emit({'archive': str(Path(args.archive).resolve()), 'format': archive.format,
                       'entry_count': len(entries), 'selected_entries': filtered}, args.output)
            return 0
        if args.command == 'extract':
            with Archive(args.archive, extractor=args.extractor) as archive:
                names = list(args.path)
                if args.prefix:
                    names.extend(e.path for e in archive.entries() if not e.is_dir and e.path.startswith(args.prefix))
                if not names:
                    raise ValueError('Select --path or --prefix; implicit whole-archive extraction is disabled')
                files = archive.extract(sorted(set(names)), args.output, max_bytes=args.max_bytes)
                _emit({'extracted_file_count': len(files), 'output': str(Path(args.output).resolve())}, None)
            return 0
        with ExitStack() as manager:
            if args.command in ('generate-local-fuel', 'generate-overlap-fuel'):
                from .local_fuel import plan_local_fuel
                packages = [manager.enter_context(Package(path, extractor=args.extractor, dlcs=tuple(args.dlc)))
                            for path in [*args.baseline, args.map]]
                recipe = json.loads(Path(args.recipe).read_text(encoding='utf-8'))
                planner = plan_local_fuel
                options = {}
                if args.command == 'generate-overlap-fuel':
                    from .overlap_fuel import plan_overlapping_fuel
                    planner = plan_overlapping_fuel
                    options = {'description': ('Experimental single-station fuel sample; not a map-wide fix.\n'
                                               'Sample 2: retains the original truck point and adds a car point at identical coordinates.\n'
                                               'Disable previous fuel samples; place this above the source map in a test profile.\n'
                                               'Broader regression and reload testing remains pending. Read road_trip_fix_report.json.\n')}
                plan, changes = planner(ResourceStack(packages), recipe,
                                        map_package=str(packages[-1].path), game_version=args.game_version)
                report = write_mod(args.output, changes, plan, game_version=args.game_version,
                                   **_fuel_writer_options(args), **options)
                _emit({'output': str(Path(args.output).resolve()), 'report': report}, None)
            elif args.command in ('courier-audit', 'generate-context'):
                baseline_packages = [manager.enter_context(Package(path, extractor=args.extractor, dlcs=tuple(args.dlc)))
                                     for path in args.baseline]
                maps = [manager.enter_context(Package(path, extractor=args.extractor, dlcs=tuple(args.dlc))) for path in args.map]
                effective = ResourceStack([*baseline_packages, *maps])
                map_paths = {str(p.path) for p in maps}
                if args.command == 'courier-audit':
                    _emit(audit_courier(effective, map_packages=map_paths), args.output)
                else:
                    from .context_generator import plan_context_aliases, render_context_patch
                    plan = plan_context_aliases(ResourceStack(baseline_packages), effective, map_paths)
                    if args.prefab:
                        selected = {p if p.startswith('prefab.') else 'prefab.' + p for p in args.prefab}
                        plan['selection'] = sorted(selected)
                        omitted = [a for a in plan['aliases'] if a['alias'] not in selected]
                        plan['skipped'].extend({'alias': a['alias'], 'reason': 'outside_requested_selection',
                                                'company_definition_count': len(a['companies'])} for a in omitted)
                        plan['aliases'] = [a for a in plan['aliases'] if a['alias'] in selected]
                    report = write_mod(args.output, render_context_patch(plan), plan, game_version=args.game_version)
                    _emit({'output': str(Path(args.output).resolve()), 'report': report}, None)
            else:
                packages = [manager.enter_context(Package(path, extractor=args.extractor, dlcs=tuple(args.dlc))) for path in args.package]
                stack = ResourceStack(packages)
                paths = list(args.path)
                if args.prefix:
                    paths.extend(path for path in stack.resources if path.startswith(args.prefix) and path.lower().endswith('.ppd'))
                plan, changes = plan_fuel(stack, paths)
                if args.command == 'fuel-audit':
                    _emit(plan, args.output)
                else:
                    report = write_mod(args.output, changes, plan, game_version=args.game_version,
                                       **_fuel_writer_options(args))
                    _emit({'output': str(Path(args.output).resolve()), 'report': report}, None)
        return 0
    except (ArchiveError, PackageError, DefinitionError, OSError, ValueError, KeyError) as exc:
        command.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
