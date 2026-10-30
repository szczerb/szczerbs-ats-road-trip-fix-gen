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
from .fuel_selection import FuelSelectionConfig, load_fuel_selection_config
from .mod_writer import write_mod
from .package import Package, PackageError, ResourceStack, virtual_path
from .petrol_policy import DEFAULT_REFERENCE
from .processors import Processor
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
    for name in ('analyze-courier-eligibility', 'generate-courier-eligibility'):
        eligibility = sub.add_parser(name, help='Analyze or package reviewed practical-cargo vehicle eligibility')
        eligibility.add_argument('--config', required=True, help='Reviewed source-pinned TOML policy')
        eligibility.add_argument('--game-dir', help='ATS installation; otherwise detected automatically')
        eligibility.add_argument('--dependency', action='append', default=[], help='Declared archives, lowest priority first')
        eligibility.add_argument('--run-id', help='Run folder timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        if name.startswith('generate'):
            eligibility.add_argument('--revision', type=int, default=3)
            eligibility.add_argument('--icon', help='Optional courier JPEG 276x162')
            eligibility.add_argument('--experimental', action='store_true')
    for name in ('analyze-tank-upgrades', 'generate-tank-upgrades'):
        tanks = sub.add_parser(name, help='Report or package source-pinned reasonable Ford tank upgrades')
        tanks.add_argument('--config', required=True, help='Reviewed source-pinned tank TOML policy')
        tanks.add_argument('--game-dir', help='ATS installation; otherwise detected automatically')
        tanks.add_argument('--dependency', action='append', default=[], help='Declared archives, lowest priority first')
        tanks.add_argument('--run-id', help='Run folder timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        if name.startswith('generate'):
            tanks.add_argument('--revision', type=int, default=0)
            tanks.add_argument('--icon', help='Optional 276x162 JPEG tank icon')
            tanks.add_argument('--experimental', action='store_true')
    for name in ('analyze-fuel-selection-batch', 'generate-fuel-selection-batch'):
        batch = sub.add_parser(name, help='Analyze or generate a pinned, finite pump-selection comparison')
        batch.add_argument('--manifest', required=True, help='Pinned finite-site fuel comparison JSON')
        batch.add_argument('--package', action='append', default=[], help='Original map/resource archives in LOW-HIGH order; omit generated fixes and installed game packages')
        batch.add_argument('--game-dir', help='ATS installation; otherwise detected automatically')
        batch.add_argument('--run-id', help='Run timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        selection = batch.add_mutually_exclusive_group(required=True)
        selection.add_argument('--fuel-policy', choices=('broad', 'realistic'))
        selection.add_argument('--fuel-selection-json', help='Strict reviewed fuel policy JSON')
        if name.startswith('generate'):
            batch.add_argument('--revision', type=int, default=1)
            batch.add_argument('--experimental', action='store_true')
    for name in ('analyze-station-parking-batch', 'generate-station-parking-batch'):
        batch = sub.add_parser(name, help='Analyze or generate one explicit multi-site station parking overlay')
        batch.add_argument('--manifest', required=True, help='Explicit P01/P02 batch manifest JSON')
        batch.add_argument('--package', action='append', default=[], help='Resource archives/directories including standard fixes in LOW-HIGH order; omit installed game packages')
        batch.add_argument('--game-dir', help='ATS installation; otherwise detected automatically')
        batch.add_argument('--run-id', help='Run folder timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        if name.startswith('generate'):
            batch.add_argument('--revision', type=int, default=1, help='Positive experimental batch revision')
            batch.add_argument('--experimental', action='store_true')
    for name in ('analyze-station-parking', 'generate-station-parking'):
        station = sub.add_parser(name, help=('Analyze one source-pinned station parking candidate'
                                             if name == 'analyze-station-parking' else
                                             'Generate one experimental station parking candidate'))
        station.add_argument('--config', required=True, help='Source-pinned station JSON config')
        station.add_argument('--mesh', required=True, help='Converted station PIM; schema 2 also requires its paired sibling PIT')
        station.add_argument('--map-package', required=True, help='Pinned source map archive')
        station.add_argument('--package', action='append', default=[],
                             help='Map/dependency archive or directory in LOW-HIGH order; include custom source once, omit installed game packages')
        station.add_argument('--base-fix', help='Optional pinned fuel-only base fix mounted above explicit map packages')
        station.add_argument('--game-dir', help='ATS installation; otherwise detected automatically')
        station.add_argument('--run-id', help='Run folder timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        if name.startswith('generate'):
            station.add_argument('--revision', type=int, default=0, help='Experiment revision; schema-2 generation requires at least 1')
            station.add_argument('--experimental', action='store_true')
    for name in ('analyze-map-stack', 'generate-map-stack'):
        stack = sub.add_parser(name, help=('Analyze the declared original map stack without writing mods'
                                           if name == 'analyze-map-stack' else
                                           'Generate the complete supported map replacement set'))
        stack.add_argument('--package', action='append', required=True,
                           help='Original map/resource package, repeat LOW-HIGH; omit generated fixes and installed game packages')
        stack.add_argument('--preset', choices=('broad', 'realistic'), default='realistic',
                           help='Combined fuel/parking policy (default: realistic)')
        stack.add_argument('--improve-existing-car-parking', action='store_true',
                           help='Opt in to safe improvements at native car-supported stations (realistic only; default OFF)')
        stack.add_argument('--improve-truck-parking', action='store_true',
                           help='Complete missing truck-rest regions at supported native-rest facilities; default OFF')
        stack.add_argument('--station-evidence-dir',
                           help='Private flat reviewed PIM/PIT directory; required for station_bays')
        stack.add_argument('--game-dir', help='ATS installation; otherwise detected automatically')
        stack.add_argument('--run-id', help='Run timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        if name.startswith('generate'):
            stack.add_argument('--revision', type=int, default=13)
            stack.add_argument('--experimental', action='store_true')
    for name in ('generate-map-fuel', 'generate-map-fix', 'analyze-map'):
        bulk = sub.add_parser(name, help=('Discover missing car fuel points in an entire source map'
                                          if name == 'generate-map-fuel' else
                                          'Report selected compatibility topics without creating a mod'
                                          if name == 'analyze-map' else
                                          'Generate selected map-wide Road Trip compatibility fixes'))
        bulk.add_argument('source', help='Source map .scs; known companion packages are resolved beside it')
        bulk.add_argument('--game-dir', help='ATS installation; otherwise ATS_GAME_DIR or detected Steam location')
        bulk.add_argument('--map-name', help='Short map name; inferred for known map families')
        if name != 'analyze-map':
            bulk.add_argument('--revision', type=int, default=2 if name == 'generate-map-fuel' else 9)
        bulk.add_argument('--run-id', help='Run folder timestamp YYYY-MM-DD_HH-MM-SS (Europe/Warsaw)')
        bulk.add_argument('--dependency', action='append', default=[], help='Explicit additional package, lowest priority first')
        bulk.add_argument('--petrol-reference', default=DEFAULT_REFERENCE,
                          help='Game-only mounted country path for the petrol/diesel fallback ratio')
        selection = bulk.add_mutually_exclusive_group()
        selection.add_argument('--fuel-policy', choices=('broad', 'realistic'),
                               help='Added car fueling: legacy broad coverage or conservative reviewed selection')
        selection.add_argument('--fuel-selection-json',
                               help='Strict source-pinned fuel policy JSON, including rules and uncertain-case behavior')
        if name != 'analyze-map':
            bulk.add_argument('--icon', help='Optional map-labelled JPEG 276x162')
            bulk.add_argument('--experimental', action='store_true')
        if name in ('generate-map-fix', 'analyze-map'):
            bulk.add_argument('--processor', action='append', required=True,
                              choices=[p.value for p in Processor],
                              help='Select fuel, rest, or analysis-only courier; repeat as needed')
            bulk.add_argument('--station-evidence-dir',
                              help='Private flat reviewed PIM/PIT directory; required for station_bays')
            bulk.add_argument('--parking-strategy', choices=('none', 'truck_areas', 'station_bays'),
                              help='Select one rest strategy; default is legacy truck_areas')
            bulk.add_argument('--improve-existing-car-parking', action='store_true',
                              help='Improve native car parking with rest and station_bays; default OFF')
            bulk.add_argument('--improve-truck-parking', action='store_true',
                              help='Complete native truck-rest coverage independently of car parking; default OFF')
            bulk.add_argument('--rest-radius', type=float, default=1000,
                              help='Straight-line rest search distance in map coordinate units (default: 1000)')
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
        if args.command in ('analyze-courier-eligibility', 'generate-courier-eligibility'):
            from .eligibility_run import analyze_courier_eligibility, generate_courier_eligibility
            options = dict(game_dir=args.game_dir, dependency=args.dependency,
                           run_id=args.run_id, extractor=args.extractor)
            if args.command.startswith('generate'):
                result = generate_courier_eligibility(args.config, revision=args.revision, icon=args.icon, **options)
            else:
                result = analyze_courier_eligibility(args.config, **options)
            _emit({'status': result['status'], 'output': result.get('output'),
                   'report_path': result['report_path'], 'work_dir': result['workflow']['work_dir'],
                   'coverage': result['planner'].get('coverage'),
                   'generated_mod_count': result['generated_mod_count']}, None)
            return 0
        if args.command in ('analyze-tank-upgrades', 'generate-tank-upgrades'):
            from .tank_run import run_tank_upgrades
            options = dict(game_dir=args.game_dir, dependency=args.dependency,
                           run_id=args.run_id, extractor=args.extractor)
            generate = args.command.startswith('generate')
            if generate:
                options.update(revision=args.revision, icon=args.icon)
            result = run_tank_upgrades(args.config, generate=generate, **options)
            _emit({'status': result['status'], 'output': result.get('output'),
                   'report_path': result['report_path'], 'work_dir': result['workflow']['work_dir'],
                   'coverage': result['planner'].get('coverage'),
                   'generated_mod_count': result['generated_mod_count']}, None)
            return 0
        if args.command in ('analyze-fuel-selection-batch', 'generate-fuel-selection-batch'):
            import logging
            logging.basicConfig(level=logging.INFO, format='%(message)s')
            from .fuel_selection.batch_workflow import run_fuel_selection_batch
            selection = (load_fuel_selection_config(args.fuel_selection_json) if args.fuel_selection_json
                         else FuelSelectionConfig(mode=args.fuel_policy))
            result = run_fuel_selection_batch(args.manifest, packages=args.package,
                game_dir=args.game_dir, extractor=args.extractor, run_id=args.run_id,
                generate=args.command.startswith('generate'), revision=getattr(args, 'revision', 1),
                experimental=getattr(args, 'experimental', False), fuel_selection=selection)
            _emit({'status': result['status'], 'output': result.get('output'),
                   'report_path': result['report_path'], 'work_dir': result['workflow']['work_dir'],
                   'coverage': result.get('planner', {}).get('coverage'),
                   'generated_mod_count': result['generated_mod_count']}, None)
            return 0
        if args.command in ('analyze-station-parking-batch', 'generate-station-parking-batch'):
            from .station_parking.batch_workflow import run_station_parking_batch
            generate = args.command.startswith('generate')
            result = run_station_parking_batch(args.manifest, packages=args.package,
                game_dir=args.game_dir, extractor=args.extractor, run_id=args.run_id,
                generate=generate, revision=getattr(args, 'revision', 1),
                experimental=getattr(args, 'experimental', False))
            _emit({'status': result['status'], 'output': result.get('output'),
                   'report_path': result['report_path'], 'work_dir': result['workflow']['work_dir'],
                   'coverage': result.get('planner', {}).get('coverage'),
                   'generated_mod_count': result['generated_mod_count']}, None)
            return 0
        if args.command in ('analyze-station-parking', 'generate-station-parking'):
            from .station_parking.workflow import run_station_parking
            generate = args.command.startswith('generate')
            result = run_station_parking(
                args.config, args.mesh, args.map_package, packages=args.package,
                base_fix=args.base_fix, game_dir=args.game_dir, run_id=args.run_id,
                extractor=args.extractor, generate=generate,
                revision=args.revision if generate else 0,
                experimental=getattr(args, 'experimental', False))
            _emit({'status': result['status'], 'output': result.get('output'),
                   'report_path': result['report_path'], 'work_dir': result['workflow']['work_dir'],
                   'coverage': result['planner'].get('coverage'),
                   'generated_mod_count': result['generated_mod_count']}, None)
            return 0
        if args.command in ('analyze-map-stack', 'generate-map-stack'):
            import logging
            logging.basicConfig(level=logging.INFO, format='%(message)s')
            from .map_stack import run_map_stack
            generate = args.command == 'generate-map-stack'
            result = run_map_stack(packages=args.package, preset=args.preset,
                game_dir=args.game_dir, extractor=args.extractor, run_id=args.run_id,
                generate=generate, experimental=getattr(args, 'experimental', False),
                revision=getattr(args, 'revision', 13),
                station_evidence_dir=args.station_evidence_dir,
                improve_existing_car_parking=args.improve_existing_car_parking,
                improve_truck_parking=args.improve_truck_parking)
            _emit({'status': result['status'], 'analysis_only': not generate,
                   'outputs': result.get('outputs', []),
                   'report_path': result.get('report_path'),
                   'work_dir': result.get('workflow', {}).get('work_dir'),
                   'coverage': result.get('planner', {}).get('coverage'),
                   'generated_mod_count': len(result.get('outputs', []))}, None)
            return 0
        if args.command in ('generate-map-fuel', 'generate-map-fix', 'analyze-map'):
            import logging
            logging.basicConfig(level=logging.INFO, format='%(message)s')
            from .bulk_run import analyze_map, generate_map_fix, generate_map_fuel
            options = dict(game_dir=args.game_dir, map_name=args.map_name,
                           run_id=args.run_id,
                           extractor=args.extractor, dependency=args.dependency,
                           petrol_reference=args.petrol_reference)
            if args.fuel_selection_json:
                options['fuel_selection'] = load_fuel_selection_config(args.fuel_selection_json)
            elif args.fuel_policy:
                options['fuel_selection'] = FuelSelectionConfig(mode=args.fuel_policy)
            if args.command in ('analyze-map', 'generate-map-fix'):
                if args.station_evidence_dir is not None:
                    options['station_evidence_dir'] = args.station_evidence_dir
                if args.parking_strategy is not None:
                    options['parking_strategy'] = args.parking_strategy
                if args.improve_existing_car_parking:
                    options['improve_existing_car_parking'] = True
                if args.improve_truck_parking:
                    options['improve_truck_parking'] = True
            if args.command == 'analyze-map':
                result = analyze_map(args.source, processors=args.processor,
                                     rest_radius=args.rest_radius, **options)
                _emit({'status': result['status'], 'analysis_only': True,
                       'report_path': result['report_path'],
                       'work_dir': result['workflow']['work_dir'],
                       'coverage': result['planner'].get('coverage'),
                       'generated_mod_count': 0}, None)
                return 0
            options.update(revision=args.revision, icon=args.icon)
            if args.command == 'generate-map-fuel':
                result = generate_map_fuel(args.source, **options)
            else:
                result = generate_map_fix(args.source,
                                          processors=args.processor,
                                          rest_radius=args.rest_radius, **options)
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
