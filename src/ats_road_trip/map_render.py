"""Read-only selection, provenance and reporting for the map renderer."""

from contextlib import ExitStack
from datetime import datetime
import hashlib
import json
import lzma
import math
import os
from pathlib import Path
import re
from zipfile import BadZipFile
import zlib
from zoneinfo import ZoneInfo

from .archive import Archive, ArchiveError
from .bulk_run import REPO_ROOT, _BASE_PACKAGES, _game_directory
from .package import Package, PackageError, ResourceStack
from .sii import DefinitionError, parse_units

SECTOR = re.compile(r'map/([^/]+)/sec([+-]\d{4})([+-]\d{4})\.(base|aux|data|desc|layer|snd)')
MAP_DLC = re.compile(r'dlc_(?:[a-z]{2}|arizona|nevada)\.scs')
INPUT_ERRORS = (ArchiveError, PackageError, BadZipFile, OSError, ValueError)
SECTOR_ITEMS = {'base', 'aux'}


def _bounds(values):
    if not isinstance(values, (list, tuple)) or len(values) != 4 or any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        or not math.isfinite(value) for value in values
    ):
        raise ValueError('Bounds require four finite X/Z coordinates')
    x0, z0, x1, z1 = values
    if not (x0 < x1 and z0 < z1 and math.isfinite(x1 - x0) and math.isfinite(z1 - z0)):
        raise ValueError('Bounds must have a positive finite extent')
    return tuple(values)


def _sector(path):
    match = SECTOR.fullmatch(path)
    if match is None:
        return None
    namespace, x, z, member = match.groups()
    return namespace, (int(x), int(z)), member


def _name(value):
    """Keep report labels single-line and discard strings that look like host paths."""
    if not isinstance(value, str) or re.search(r'[/\\\x00-\x1f]', value):
        return None
    return value[:180]


def _filename(value):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', value).strip('.-')[:90] or 'map'


def _metadata(package, label):
    meta = {'name': label, 'title': label, 'version': None, 'sha256': None}
    if package.archive is not None:
        with package.path.open('rb') as stream:
            meta['sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        meta['format'] = package.archive.format
    else:
        meta['format'] = 'directory'
    if 'manifest.sii' not in package.files:
        return meta
    try:
        raw = package.read('manifest.sii', max_bytes=1024 * 1024)
        unit = next(unit for unit in parse_units(
            raw.decode('utf-8-sig'), source='manifest.sii',
        ) if unit.kind == 'mod_package')
        meta['title'] = _name(unit.one('display_name')) or label
        meta['version'] = _name(unit.one('package_version'))
    except (*INPUT_ERRORS, DefinitionError, StopIteration, RuntimeError, lzma.LZMAError, zlib.error):
        # Metadata is optional. A malformed manifest does not hide sector data.
        meta['manifest_status'] = 'unavailable'
    return meta


class MapRenderSession:
    """Reuse parsed sector and prefab data across views of the same archives."""

    def __init__(self, *, output, background, background_config, game_dir=None,
                 extractor=None, dlcs=(), long_edge=8192):
        from PIL import Image
        from .map_render_geometry import GeometryCache

        if not 512 <= long_edge <= 16384:
            raise ValueError('Image longest edge must be between 512 and 16384 pixels')
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.long_edge = long_edge
        self.extractor = extractor
        config = json.loads(Path(background_config).read_text(encoding='utf-8'))
        if not isinstance(config, dict):
            raise ValueError('Expected a background configuration object')
        self.atlas = _bounds(config.get('world_bounds'))
        size = config.get('texture_size')
        if type(size) is not int or not 1 <= size <= 16384:
            raise ValueError('Invalid configured background texture_size')
        # Generator atlases can exceed Pillow's generic decompression guard.
        # Check the declared size and format before decoding any pixels.
        pixel_limit = Image.MAX_IMAGE_PIXELS
        try:
            Image.MAX_IMAGE_PIXELS = size * size
            with Image.open(background, formats=('PNG',)) as raster:
                if raster.size != (size, size):
                    raise ValueError('Background must be the full PNG at the configured texture_size')
                if raster.mode == 'RGB':
                    raster.load()
                    self.raster = raster
                else:
                    self.raster = raster.convert('RGB')
        finally:
            Image.MAX_IMAGE_PIXELS = pixel_limit
        self.background = {
            'version': _name(config.get('version')),
            'world_bounds': self.atlas,
            'size': self.raster.size,
        }
        with Path(background).open('rb') as stream:
            self.background['sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        self.files = ExitStack()
        self.packages = {}
        self.identities = {}
        self.metadata = {}
        self.stock = []
        self.dlcs = tuple(dlcs)
        self.geometry = GeometryCache()
        self.index = 0
        if game_dir is not None or os.environ.get('ATS_GAME_DIR'):
            directory = _game_directory(game_dir)
            maps = [path for path in sorted(directory.glob('dlc_*.scs'))
                    if MAP_DLC.fullmatch(path.name) and (not dlcs or path.stem in dlcs)]
            if not dlcs:
                self.dlcs = tuple(path.stem for path in sorted(directory.glob('dlc_*.scs')))
            try:
                for path in [*(directory / name for name in _BASE_PACKAGES), *maps]:
                    self.stock.append(self._open(path))
            except INPUT_ERRORS:
                self.close()
                raise

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def close(self):
        self.files.close()
        self.raster.close()

    def _open(self, path):
        path = Path(path).resolve()
        if path not in self.packages:
            package = Package(path, extractor=self.extractor, dlcs=self.dlcs,
                              skip_invalid_deep_paths=True)
            self.packages[path] = package
            label = _name(path.name) or 'archive'
            duplicate = sum(value.split(' #', 1)[0] == label for value in self.identities.values())
            self.identities[package] = f'{label} #{duplicate + 1}' if duplicate else label
            if package.archive is not None:
                self.files.callback(package.archive.close)
        return self.packages[path]

    def render(self, targets, *, mode='standalone', dependencies=(), bounds=None,
               name=None):
        from .map_render_geometry import collect_geometry
        from .map_render_image import draw_map, footprint_bounds

        self.index += 1
        report = {
            'mode': mode, 'background': self.background, 'packages': [], 'images': [],
            'errors': [], 'warnings': [], 'stock_baseline': bool(self.stock),
        }
        result_name = _filename(name or f'{mode}-{self.index:02d}')
        summary = self.output / f'{result_name}.json'
        if summary.exists():
            raise FileExistsError(f'Output already exists: {summary.name}')

        def finish(status):
            report['status'] = status
            with summary.open('x', encoding='utf-8') as stream:
                json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
                stream.write('\n')
            return report, summary.name

        if mode not in ('standalone', 'comparison', 'effective'):
            raise ValueError('Unknown map rendering mode')
        if not targets or (mode == 'standalone' and len(targets) != 1):
            raise ValueError('Standalone mode requires exactly one archive')
        if bounds is not None:
            bounds = _bounds(bounds)

        def load(paths, role):
            loaded = []
            for path in paths:
                try:
                    package = self._open(path)
                    loaded.append(package)
                    if package.archive and package.archive.discarded_deep_path_count:
                        report['warnings'].append({
                            'archive': self.identities[package], 'role': role,
                            'reason': 'invalid_hashfs_deep_path_candidates_discarded',
                            'count': package.archive.discarded_deep_path_count,
                        })
                except INPUT_ERRORS as exc:
                    report['errors'].append({
                        'archive': _name(Path(path).name) or 'archive', 'role': role,
                        'reason': 'missing' if isinstance(exc, FileNotFoundError) else 'unreadable',
                        'error_type': type(exc).__name__,
                    })
            return loaded

        selected = load(targets, 'target')
        lower = list(dict.fromkeys([*self.stock, *load(dependencies, 'dependency')]))
        if len(set(selected)) != len(selected) or set(selected).intersection(lower):
            raise ValueError('Supply each archive once across target and dependency arguments')
        if not selected:
            return finish('failed')
        records = {}
        for package in selected:
            if package not in self.metadata:
                self.metadata[package] = _metadata(package, self.identities[package])
            record = self.metadata[package].copy()
            sectors = {path: sector for path in sorted(package.files)
                       if (sector := _sector(path)) is not None}
            record['sector_members'] = len(sectors)
            record['status'] = 'sector_geometry' if sectors else 'no_sector_geometry'
            records[package] = sectors
            report['packages'].append(record)
        namespaces = sorted({sector[0] for sectors in records.values() for sector in sectors.values()})
        if mode == 'effective' and report['errors']:
            return finish('failed')
        if not namespaces:
            return finish('partial' if len(selected) != len(targets) else 'no_sector_geometry')

        baseline = ResourceStack(lower)
        ordered = [*lower, *selected]
        stack = ResourceStack(ordered)
        views = [(stack, selected)]
        if mode == 'comparison':
            views = [(ResourceStack([*lower, *(other for other in selected if other is not package), package]),
                      [package]) for package in selected if records[package]]
        report['load_order'] = [self.identities[package] for package in ordered]
        shadow_candidates = set().union(*(record.keys() for record in records.values()))
        partial = bool(report['errors'] or any(w['role'] == 'target' for w in report['warnings']))
        for namespace in namespaces:
            tiles = {}
            preceding = {sector[1] for path in baseline.resources
                         if (sector := _sector(path)) is not None and sector[0] == namespace}
            for package in selected:
                tile_set = {sector[1] for sector in records[package].values()
                            if sector[0] == namespace}
                if not tile_set:
                    continue
                winning_tiles = tile_set
                if mode == 'effective':
                    winning_tiles = {sector[1] for path, sector in records[package].items()
                                     if sector[0] == namespace and stack.resources[path][0] is package}
                if winning_tiles:
                    tiles[self.identities[package]] = {
                        tile: tile in preceding for tile in sorted(winning_tiles)
                    }
                if mode == 'effective':
                    preceding.update(tile_set)
            crop = bounds or footprint_bounds(set().union(*(tile.keys() for tile in tiles.values())))
            x0, z0, x1, z1 = crop
            lines = []
            issues = []
            counts = []
            for view, draw_packages in views:
                context = {path: sector for path in view.resources
                           if (sector := _sector(path)) is not None
                           and sector[0] == namespace and sector[2] in SECTOR_ITEMS}
                draw_paths = []
                for path, (_, (x, z), _) in context.items():
                    owner = view.resources[path][0]
                    # Read all target members for complete accounting, including
                    # members outside explicitly requested comparison crops.
                    if owner in draw_packages:
                        draw_paths.append(path)
                    elif (mode == 'effective' and owner in self.stock
                          and (x + 1) * 4000 >= x0 and x * 4000 <= x1
                          and (z + 1) * 4000 >= z0 and z * 4000 <= z1):
                        draw_paths.append(path)
                geometry = collect_geometry(view, draw_paths, context_paths=context, cache=self.geometry)
                if mode == 'effective':
                    shadow_candidates.update(geometry.prefab_resources)
                counts.append({
                    'providers': [self.identities[package] for package in draw_packages],
                    'counts': geometry.counts,
                    'members': geometry.members,
                    'prefab_providers': {
                        path: self.identities[view.resources[path][0]]
                        for path in sorted(geometry.prefab_resources)
                    },
                })
                for issue in geometry.issues:
                    issues.append(issue)
                lines.extend((self.identities[owner] if owner in selected else None, line)
                             for line in geometry.lines
                             if (owner := view.resources[line.path][0]) in selected or owner in self.stock)
            partial |= bool(issues)
            providers = list(tiles)
            output = self.output / f'{result_name}-{_filename(namespace)}.png'
            first = report['packages'][0]
            title = (
                ' | '.join(dict.fromkeys(filter(None, (first['title'], first['version']))))
                if mode == 'standalone' else f'ATS map mod {mode}'
            )
            issue_tiles = {
                sector[1] for issue in issues if issue.get('role') != 'reference'
                and (sector := _sector(issue.get('path', ''))) is not None
                and sector[0] == namespace
            }
            size = draw_map(
                self.raster, self.atlas, crop, tiles, lines, providers, f'{title}  ·  {namespace}',
                long_edge=self.long_edge, mode=mode, issue_count=len(issues), issue_tiles=issue_tiles,
                baseline=bool(lower) or (mode == 'effective' and len(selected) > 1),
                stock=mode == 'effective' and bool(self.stock), output=output,
            )
            report['images'].append({
                'file': output.name, 'namespace': namespace, 'size': size, 'world_bounds': crop,
                'tile_counts': {provider: len(coverage) for provider, coverage in tiles.items()},
                'tiles': {provider: [[x, z, replaced] for (x, z), replaced in coverage.items()]
                          for provider, coverage in tiles.items()},
                'geometry': counts, 'geometry_issues': issues,
            })
        report['shadowed_resources'] = [
            {'member': path, 'providers': [self.identities[package] for package in providers],
             'winner': self.identities[stack.resources[path][0]]}
            for path in sorted(shadow_candidates)
            if len(providers := [package for package in ordered if path in package.files]) > 1
        ] if mode == 'effective' else []
        return finish('partial' if partial else 'rendered')


def run_render_map(args):
    """CLI adapter. Expected input failures use path-free diagnostics."""
    run_id = datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    output = Path(args.output_dir) if args.output_dir else REPO_ROOT / 'local_outputs/work' / run_id / 'map-render'
    old_root = Archive._work_root
    Archive.configure_work_root(REPO_ROOT / 'local_outputs/work' / run_id)
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        Archive.configure_work_root(old_root)
        print("Map rendering requires Pillow. Install the project's [background] extra.")
        return 1
    try:
        with MapRenderSession(
            output=output, background=args.background, background_config=args.background_config,
            game_dir=args.game_dir, extractor=args.extractor, dlcs=args.dlc, long_edge=args.long_edge,
        ) as session:
            report, summary = session.render(
                args.archives, mode=args.mode, dependencies=args.dependency,
                bounds=args.bounds, name=args.name,
            )
    except (*INPUT_ERRORS, Image.DecompressionBombError) as exc:
        print(f'Map rendering failed ({type(exc).__name__}). Check the inputs and output location.')
        return 1
    finally:
        Archive.configure_work_root(old_root)
    print(json.dumps({
        'status': report['status'], 'summary': summary,
        'images': [image['file'] for image in report['images']],
    }))
    return int(report['status'] == 'failed')
