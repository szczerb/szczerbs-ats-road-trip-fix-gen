"""Project licensed geography into a configurable, calibrated ATS XZ plane."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

import numpy as np
from pyproj import Proj
from scipy.interpolate import RBFInterpolator
import shapefile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_files(manifest: dict, cache: Path, *, download: bool = False) -> dict[str, Path]:
    """Verify pinned archives before reading; download only when requested.

    Never extract arbitrary archive paths or silently accept new upstream data.
    """
    cache.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, spec in manifest.items():
        if not name.replace('_', '').isalnum():
            raise ValueError('Unsafe dataset name')
        target = cache / (name + '.zip')
        if not target.exists() and download:
            if not spec['url'].startswith('https://'):
                raise ValueError('Source URL must use HTTPS')
            with urllib.request.urlopen(spec['url'], timeout=120) as response:
                data = response.read(64 * 1024 * 1024 + 1)
            if len(data) > 64 * 1024 * 1024 or digest(data) != spec['sha256']:
                raise ValueError(f'Unexpected downloaded dataset: {name}')
            with target.open('xb') as out:
                out.write(data)
        if not target.is_file() or digest(target.read_bytes()) != spec['sha256']:
            raise ValueError(f'Missing or changed dataset: {target}')
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Corrupt dataset: {name}')
            version = archive.read(name + '.VERSION.txt').decode().strip()
            if version != spec['version']:
                raise ValueError(f'Dataset version mismatch: {name}')
        result[name] = target
    return result


def features(path: Path):
    """Yield shapefile features directly from ZIP, avoiding filesystem extraction."""
    with zipfile.ZipFile(path) as archive:
        name = path.stem
        reader = shapefile.Reader(**{ext: io.BytesIO(archive.read(f'{name}.{ext}'))
                                     for ext in ('shp', 'shx', 'dbf')}, encoding='utf-8')
        for feature in reader.iterShapeRecords():
            yield feature.shape, feature.record.as_dict()


class Calibration:
    """Spherical LCC baseline plus a smooth, data-derived XZ correction.

    The engine's climate definition motivates LCC, but does not prove its exact
    earth model. A fitted affine transform accounts for scale/origin differences.
    Optional smooth thin-plate residuals account for compressed map geography.
    Held-out points never influence fitting. No third-party image is traced.
    """
    def __init__(self, config: dict, anchors: list[dict]):
        spec = config['projection']
        self.proj = Proj(**spec)
        self.scale = config['game_scale']
        fit = [p for p in anchors if p['role'] == 'fit']
        if len(fit) < 6:
            raise ValueError('At least six fitting anchors are required')
        self.points = self.baseline(np.array([[p['lon'], p['lat']] for p in fit]))
        self.targets = np.array([[p['x'], p['z']] for p in fit], dtype=float)
        design = np.c_[self.points / 100000, np.ones(len(fit))]
        if np.linalg.matrix_rank(design) != 3:
            raise ValueError('Degenerate calibration anchors')
        self.affine = np.linalg.lstsq(design, self.targets, rcond=None)[0]
        self.residual = None
        smoothing = config['correction_smoothing']
        if config['correction'] == 'thin_plate_spline':
            self.residual = RBFInterpolator(self.points / 100000,
                (self.targets - design @ self.affine) / 100000,
                smoothing=smoothing, kernel='thin_plate_spline', degree=1)
        elif config['correction'] != 'affine':
            raise ValueError('Unknown correction')

    def baseline(self, lonlat):
        lonlat = np.asarray(lonlat, dtype=float).reshape(-1, 2)
        x, y = self.proj(lonlat[:, 0].tolist(), lonlat[:, 1].tolist())
        result = np.column_stack((x, -np.asarray(y))) / self.scale
        if not np.isfinite(result).all():
            raise ValueError('Nonfinite projected geometry')
        return result

    def __call__(self, lonlat):
        points = self.baseline(lonlat)
        result = np.c_[points / 100000, np.ones(len(points))] @ self.affine
        if self.residual is not None:
            # Bounded batches avoid a large points-by-anchors temporary array.
            for start in range(0, len(points), 8192):
                result[start:start + 8192] += self.residual(points[start:start + 8192] / 100000) * 100000
        if not np.isfinite(result).all():
            raise ValueError('Nonfinite calibrated geometry')
        return result

    def report(self, anchors: list[dict]) -> dict:
        records = []
        for p in anchors:
            base = self.baseline([[p['lon'], p['lat']]])[0]
            xy = self([[p['lon'], p['lat']]])[0]
            target = np.array([p['x'], p['z']])
            records.append({**p, 'predicted_xz': xy.tolist(),
                'baseline_error_game_units': float(np.linalg.norm(base - target)),
                'error_game_units': float(np.linalg.norm(xy - target))})
        summary = {}
        for role in ('fit', 'check'):
            group = [p for p in records if p['role'] == role]
            errors = np.array([p['error_game_units'] for p in group])
            summary[role] = {'count': len(group), 'rms': float(np.sqrt(np.mean(errors**2))),
                             'median': float(np.median(errors)), 'max': float(errors.max())}
        return {'method': 'LCC -> affine -> optional smooth thin-plate residual',
                'units': 'game-world XZ units, not real-world meters',
                'fit_is_not_independent_validation': True,
                'summary': summary, 'references': records, 'affine': self.affine.tolist()}

    def jacobian_report(self, extent: list[float]) -> dict:
        """Detect local flips/implausible scale across the configured geography."""
        west, south, east, north = extent
        lon, lat = np.meshgrid(np.linspace(west, east, 70), np.linspace(south, north, 55))
        points = np.c_[lon.ravel(), lat.ravel()]
        step = 0.001
        p = self(points)
        a = (self(points + [step, 0]) - p) / step
        b = (self(points + [0, step]) - p) / step
        det = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
        base = self.baseline(points)
        ba = (self.baseline(points + [step, 0]) - base) / step
        bb = (self.baseline(points + [0, step]) - base) / step
        base_det = ba[:, 0] * bb[:, 1] - ba[:, 1] * bb[:, 0]
        ratio = det / base_det
        result = {'samples': len(points), 'min_area_ratio_to_baseline': float(ratio.min()),
                  'max_area_ratio_to_baseline': float(ratio.max()), 'flipped_samples': int((ratio <= 0).sum())}
        if (ratio <= 0).any() or ratio.min() < 0.15 or ratio.max() > 5:
            raise ValueError(f'Unsafe geographic deformation: {json.dumps(result)}')
        return result
