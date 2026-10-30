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
from scipy.spatial.distance import cdist
import shapefile


ROOT = Path(__file__).resolve().parents[3]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_download_cache(cache: Path) -> Path:
    """Resolve downloads beneath the checkout's work tree without creating it."""
    resolved = cache.resolve()
    # Do not resolve the work suffix: a redirected output tree must not turn
    # supplied inputs (or another location) into an allowed download root.
    allowed = ROOT.resolve() / 'local_outputs' / 'work'
    if not resolved.is_relative_to(allowed):
        raise ValueError('Downloads belong beneath this checkout local_outputs/work')
    return resolved


def source_files(manifest: dict, cache: Path, *, download: bool = False) -> dict[str, Path]:
    """Verify pinned archives before reading; download only when requested.

    Offline caches can be anywhere and are never created or changed here.
    Never extract arbitrary archive paths or silently accept new upstream data.
    """
    if download:
        cache = validate_download_cache(cache)
        cache.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, spec in manifest.items():
        if not name.replace('_', '').isalnum():
            raise ValueError('Unsafe dataset name')
        kind = spec.get('format', 'natural-earth-zip')
        if kind not in ('natural-earth-zip', 'gshhg-zip', 'geojson'):
            raise ValueError('Unsupported source format')
        target = cache / (name + ('.geojson' if kind == 'geojson' else '.zip'))
        limit = 160 * 1024 * 1024 if kind == 'gshhg-zip' else 64 * 1024 * 1024
        if not target.exists() and download:
            if not spec['url'].startswith('https://'):
                raise ValueError('Source URL must use HTTPS')
            with urllib.request.urlopen(spec['url'], timeout=120) as response:
                data = response.read(limit + 1)
            if len(data) > limit or digest(data) != spec['sha256']:
                raise ValueError(f'Unexpected downloaded dataset: {name}')
            with target.open('xb') as out:
                out.write(data)
        if not target.is_file() or digest(target.read_bytes()) != spec['sha256']:
            raise ValueError(f'Missing or changed dataset: {target}')
        if kind == 'geojson':
            document = json.loads(target.read_bytes())
            if (document.get('type') != 'FeatureCollection' or not document.get('features') or
                    document.get('exceededTransferLimit')):
                raise ValueError(f'Incomplete GeoJSON source: {name}')
            result[name] = target
            continue
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Corrupt dataset: {name}')
            if kind == 'natural-earth-zip':
                version = archive.read(name + '.VERSION.txt').decode().strip()
                if version != spec['version']:
                    raise ValueError(f'Dataset version mismatch: {name}')
            elif not all(v in archive.namelist() for v in
                         ('GSHHS_shp/h/GSHHS_h_L1.shp', 'LICENSE.TXT', 'COPYING.LESSERv3')):
                raise ValueError('Incomplete GSHHG source archive')
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
    Optional thin-plate or compact residuals account for compressed geography.
    Compact corrections preserve the affine exactly outside their support disks;
    selected uncertain place references may be softened to avoid folds.
    Held-out points never influence fitting. No third-party image is traced.
    """
    def __init__(self, config: dict, anchors: list[dict]):
        spec = config['projection']
        self.proj = Proj(**spec)
        self.scale = config['game_scale']
        fit = [p for p in anchors if p['role'] == 'fit']
        if len(fit) < 6:
            raise ValueError('At least six fitting anchors are required')
        affine_names = config.get('affine_reference_names')
        affine_fit = [p for p in fit if affine_names is None or p['name'] in affine_names]
        if len(affine_fit) < 6 or (affine_names is not None and len(affine_fit)!=len(affine_names)):
            raise ValueError('Missing or duplicate affine fitting references')
        if affine_names is not None:
            by_name = {p['name']:p for p in affine_fit}
            affine_fit = [by_name[name] for name in affine_names]
        self.points = self.baseline(np.array([[p['lon'], p['lat']] for p in affine_fit]))
        self.targets = np.array([[p['x'], p['z']] for p in affine_fit], dtype=float)
        design = np.c_[self.points / 100000, np.ones(len(affine_fit))]
        if np.linalg.matrix_rank(design) != 3:
            raise ValueError('Degenerate calibration anchors')
        self.affine = np.linalg.lstsq(design, self.targets, rcond=None)[0]
        self.residual = None
        self.local_points = None
        smoothing = config['correction_smoothing']
        if config['correction'] == 'thin_plate_spline':
            self.residual = RBFInterpolator(self.points / 100000,
                (self.targets - design @ self.affine) / 100000,
                smoothing=smoothing, kernel='thin_plate_spline', degree=1)
        elif config['correction'] == 'compact':
            names = config['local_reference_names']
            controls = [p for p in fit if p['name'] in names]
            if not controls or len(controls)!=len(names):
                raise ValueError('Missing or duplicate local fitting references')
            self.local_points = self.baseline([[p['lon'],p['lat']] for p in controls])
            self.local_radius = float(config['local_correction_radius'])
            if not np.isfinite(self.local_radius) or not 1000<=self.local_radius<=50000:
                raise ValueError('Invalid local correction radius')
            predicted = self._affine(self.local_points)
            residual = np.array([[p['x'],p['z']] for p in controls])-predicted
            kernel = self._kernel(cdist(self.local_points,self.local_points)/self.local_radius)
            overrides = config.get('local_reference_smoothing',{})
            if not isinstance(overrides,dict) or set(overrides)-set(names):
                raise ValueError('Unknown local smoothing reference')
            smoothing = np.array([float(overrides.get(p['name'],config.get('local_correction_smoothing',0)))
                                  for p in controls])
            if not np.isfinite(smoothing).all() or (smoothing<0).any() or (smoothing>5).any():
                raise ValueError('Invalid local correction smoothing')
            kernel += np.diag(smoothing)
            self.local_weights = np.linalg.solve(kernel,residual)
        elif config['correction'] != 'affine':
            raise ValueError('Unknown correction')
        self.road_adjustment = None
        if 'road_adjustment' in config:
            self.road_adjustment = CompactDisplacement(config['road_adjustment'])
        self.feature_adjustment = None
        if 'feature_adjustment' in config:
            from .deformation import FeatureAdjustment
            self.feature_adjustment = FeatureAdjustment(config['feature_adjustment'])

    @staticmethod
    def _kernel(distance):
        """C2 compact radial kernel, exactly zero outside the configured radius."""
        return np.maximum(0,1-distance)**4*(4*distance+1)

    def _affine(self, points):
        return np.c_[points/100000,np.ones(len(points))]@self.affine

    def _before_features(self, points):
        result = self._affine(points)
        for start in range(0,len(points),8192):
            batch = points[start:start+8192]
            if self.residual is not None:
                result[start:start+8192] += self.residual(batch/100000)*100000
            if self.local_points is not None:
                result[start:start+8192] += self._kernel(cdist(batch,self.local_points)/self.local_radius)@self.local_weights
        if self.road_adjustment is not None:
            result = self.road_adjustment(result)
        return result

    def _from_baseline(self, points):
        result = self._before_features(points)
        if self.feature_adjustment is not None:
            result = self.feature_adjustment(result)
        return result

    def baseline(self, lonlat):
        lonlat = np.asarray(lonlat, dtype=float).reshape(-1, 2)
        x, y = self.proj(lonlat[:, 0].tolist(), lonlat[:, 1].tolist())
        result = np.column_stack((x, -np.asarray(y))) / self.scale
        if not np.isfinite(result).all():
            raise ValueError('Nonfinite projected geometry')
        return result

    def __call__(self, lonlat):
        points = self.baseline(lonlat)
        result = self._from_baseline(points)
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
        return {'method': 'LCC -> affine -> optional smooth residual',
                'units': 'game-world XZ units, not real-world meters',
                'fit_is_not_independent_validation': True,
                'summary': summary, 'references': records, 'affine': self.affine.tolist()}

    def jacobian_report(self, extent: list[float]) -> dict:
        """Detect local flips/implausible scale across the configured geography."""
        west, south, east, north = extent
        lon, lat = np.meshgrid(np.linspace(west, east, 70), np.linspace(south, north, 55))
        points = np.c_[lon.ravel(), lat.ravel()]
        step = 0.001
        p = self._before_features(self.baseline(points))
        a = (self._before_features(self.baseline(points + [step, 0])) - p) / step
        b = (self._before_features(self.baseline(points + [0, step])) - p) / step
        det = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
        base = self.baseline(points)
        ba = (self.baseline(points + [step, 0]) - base) / step
        bb = (self.baseline(points + [0, step]) - base) / step
        base_det = ba[:, 0] * bb[:, 1] - ba[:, 1] * bb[:, 0]
        ratio = det / base_det
        if self.local_points is not None:
            # A continental grid can miss a local fold. Also sample dense squares
            # around every compact correction, directly in baseline game units.
            offsets = np.array([(x,z) for x in np.linspace(-self.local_radius,self.local_radius,81)
                                for z in np.linspace(-self.local_radius,self.local_radius,81)])
            local = np.concatenate([p+offsets for p in self.local_points])
            a = (self._before_features(local+[1,0])-self._before_features(local-[1,0]))/2
            b = (self._before_features(local+[0,1])-self._before_features(local-[0,1]))/2
            ratio = np.r_[ratio,a[:,0]*b[:,1]-a[:,1]*b[:,0]]
        if self.road_adjustment is not None:
            # Check the combined mapping on a separate uniform baseline grid.
            # This also covers the new field between old settlement supports.
            a0,b0,a1,b1 = self.road_adjustment.check_bounds
            gx,gz = np.meshgrid(np.arange(a0,a1+1000,1000),np.arange(b0,b1+1000,1000))
            local = np.c_[gx.ravel(),gz.ravel()]
            a = (self._before_features(local+[1,0])-self._before_features(local-[1,0]))/2
            b = (self._before_features(local+[0,1])-self._before_features(local-[0,1]))/2
            ratio = np.r_[ratio,a[:,0]*b[:,1]-a[:,1]*b[:,0]]
        result = {'samples': len(points), 'min_area_ratio_to_baseline': float(ratio.min()),
                  'max_area_ratio_to_baseline': float(ratio.max()), 'flipped_samples': int((ratio <= 0).sum())}
        result['samples'] = len(ratio)
        if (ratio <= 0).any() or ratio.min() < 0.15 or ratio.max() > 5:
            raise ValueError(f'Unsafe geographic deformation: {json.dumps(result)}')
        if self.feature_adjustment is not None:
            result['pre_feature_mapping'] = True
            result['feature_adjustment'] = self.feature_adjustment.report()
        return result


class CompactDisplacement:
    """A regularized road/physical-ground vector field in the calibrated game plane.

    Coefficients are authored calibration parameters, not native road artwork.
    The field acts on every geographic layer equally and is exactly zero beyond
    its supports. Package reproduction uses the reviewed, versioned coefficients;
    landmark selection and independent road checks remain a separate audit.
    """
    def __init__(self, spec):
        required = {'radius','centers_xz','weights_xz','method'}
        if (not isinstance(spec,dict) or set(spec)!=required or
            spec['method'] not in ('route-normal-compact-v1','route-ground-compact-v1')):
            raise ValueError('Unsupported road adjustment')
        self.radius = float(spec['radius'])
        self.centers = np.asarray(spec['centers_xz'],dtype=float)
        self.weights = np.asarray(spec['weights_xz'],dtype=float)
        if (self.centers.ndim!=2 or self.centers.shape[1]!=2 or
            not 1<=len(self.centers)<=1000 or self.weights.shape!=self.centers.shape or
            not np.isfinite(self.centers).all() or not np.isfinite(self.weights).all() or
            not np.isfinite(self.radius) or not 5000<=self.radius<=50000 or
            np.max(np.abs(self.centers))>400000 or np.max(np.abs(self.weights))>50000):
            raise ValueError('Invalid road adjustment coefficients')
        # Baseline and output coordinates differ slightly; include a generous
        # 15k halo when checking the composed mapping in baseline coordinates.
        a,b = self.centers.min(axis=0)-self.radius-15000
        c,d = self.centers.max(axis=0)+self.radius+15000
        self.check_bounds = (a,b,c,d)

    def __call__(self, points):
        points = np.asarray(points,dtype=float).reshape(-1,2)
        result = points.copy()
        for start in range(0,len(points),4096):
            batch = points[start:start+4096]
            result[start:start+4096] += Calibration._kernel(cdist(batch,self.centers)/self.radius)@self.weights
        return result
