"""Compose reviewed feature corrections without changing playable map data.

Landmark trajectories use a smooth compact velocity field integrated by RK4.
Small compact displacement steps follow the feature flow. Every cartographic
layer shares this mapping; inputs are factual controls and authored coefficients,
never textures or traced native map geometry.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist


def kernel(distance):
    return np.maximum(0, 1-distance)**4 * (4*distance+1)


def _grid_axes(lo, hi, spacing):
    return (np.arange(lo[0], hi[0]+spacing, spacing),
            np.arange(lo[1], hi[1]+spacing, spacing))


def _grid_chunks(lo, hi, spacing, chunk_size=8192):
    """Yield a rectangular sampling grid in bounded row-major batches."""
    xs, zs = _grid_axes(lo, hi, spacing)
    nx = len(xs)
    total = nx*len(zs)
    for start in range(0, total, chunk_size):
        indices = np.arange(start, min(start+chunk_size, total))
        yield np.column_stack((xs[indices % nx], zs[indices // nx]))


class CompactStep:
    def __init__(self, spec):
        if set(spec) != {'radius', 'centers_xz', 'weights_xz'}:
            raise ValueError('Invalid feature step fields')
        self.radius = float(spec['radius'])
        self.centers = np.asarray(spec['centers_xz'], dtype=float)
        self.weights = np.asarray(spec['weights_xz'], dtype=float)
        if (self.centers.ndim != 2 or self.centers.shape[1] != 2 or
                not 1 <= len(self.centers) <= 2000 or
                self.weights.shape != self.centers.shape or
                not np.isfinite(self.centers).all() or not np.isfinite(self.weights).all() or
                not 1000 <= self.radius <= 20000 or
                np.max(np.abs(self.centers)) > 400000 or
                np.max(np.abs(self.weights)) > 50000):
            raise ValueError('Unsafe feature step coefficients')
        self.tree = cKDTree(self.centers)
        self.lo = self.centers.min(axis=0)-self.radius
        self.hi = self.centers.max(axis=0)+self.radius

    def __call__(self, points):
        p = np.asarray(points, dtype=float).reshape(-1, 2)
        result = p.copy()
        # Sparse compact neighborhoods avoid a continent-size dense matrix.
        for start in range(0, len(p), 16384):
            batch = p[start:start+16384]
            distances = cKDTree(batch).sparse_distance_matrix(
                self.tree, self.radius, output_type='coo_matrix')
            basis = coo_matrix((kernel(distances.data/self.radius),
                               (distances.row, distances.col)), shape=distances.shape).tocsr()
            result[start:start+len(batch)] += basis @ self.weights
        return result

    def inverse(self, points):
        q = np.asarray(points, dtype=float).reshape(-1, 2)
        p = q.copy()
        for _ in range(48):
            nxt = q-(self(p)-p)
            if np.max(np.abs(nxt-p), initial=0) < 1e-7:
                return nxt
            p = nxt
        if np.max(np.abs(self(p)-q), initial=0) > 1e-4:
            raise ValueError('Feature step inverse failed to converge')
        return p


class LandmarkFlow:
    def __init__(self, spec):
        if set(spec) != {'radius', 'integration_steps', 'source_xz', 'target_xz'}:
            raise ValueError('Invalid landmark flow fields')
        self.p = np.asarray(spec['source_xz'], dtype=float)
        self.q = np.asarray(spec['target_xz'], dtype=float)
        self.radius = float(spec['radius'])
        self.steps = spec['integration_steps']
        if (self.p.ndim != 2 or self.p.shape[1] != 2 or self.q.shape != self.p.shape or
                not 2 <= len(self.p) <= 32 or not np.isfinite(self.p).all() or
                not np.isfinite(self.q).all() or not 1000 <= self.radius <= 20000 or
                not isinstance(self.steps, int) or not 64 <= self.steps <= 512 or
                np.max(np.abs(self.p)) > 400000 or np.max(np.abs(self.q)) > 400000 or
                np.max(np.linalg.norm(self.q-self.p, axis=1)) > 10000):
            raise ValueError('Unsafe landmark flow')
        delta = self.q-self.p
        times = np.linspace(0, 1, 2*self.steps+1)
        self.centers = self.p[None] + times[:, None, None]*delta[None]
        self.weights = []
        for centers in self.centers:
            gram = kernel(cdist(centers, centers)/self.radius)
            self.weights.append(np.linalg.solve(gram+np.eye(len(centers))*1e-10, delta))
        self.lo = self.centers.min(axis=(0, 1))-self.radius
        self.hi = self.centers.max(axis=(0, 1))+self.radius

    def velocity(self, points, time_index):
        return kernel(cdist(points, self.centers[time_index])/self.radius) @ self.weights[time_index]

    def _integrate(self, points, reverse=False):
        result = np.asarray(points, dtype=float).reshape(-1, 2).copy()
        keep = np.all((result > self.lo) & (result < self.hi), axis=1)
        # Outside the swept support the velocity is exactly zero.
        for start in range(0, int(keep.sum()), 8192):
            ids = np.flatnonzero(keep)[start:start+8192]
            p = result[ids].copy()
            h = (-1 if reverse else 1)/self.steps
            for step in range(self.steps):
                i = 2*self.steps-2*step if reverse else 2*step
                j = -1 if reverse else 1
                k1 = self.velocity(p, i)
                k2 = self.velocity(p+k1*h/2, i+j)
                k3 = self.velocity(p+k2*h/2, i+j)
                k4 = self.velocity(p+k3*h, i+2*j)
                p += h/6*(k1+2*k2+2*k3+k4)
            result[ids] = p
        return result

    def __call__(self, points):
        return self._integrate(points)

    def inverse(self, points):
        return self._integrate(points, reverse=True)


class RegionalTranslation:
    """Move a feature rigidly in a moving core, blending smoothly outside it.

    This is a shared coordinate flow, not a per-layer polygon translation.
    Source vertices inside the core retain all relative positions exactly.
    """
    def __init__(self, spec):
        if set(spec) != {'center_xz', 'delta_xz', 'inner_radius', 'outer_radius',
                         'integration_steps'}:
            raise ValueError('Invalid regional translation fields')
        self.center = np.asarray(spec['center_xz'], dtype=float)
        self.delta = np.asarray(spec['delta_xz'], dtype=float)
        self.inner = float(spec['inner_radius'])
        self.outer = float(spec['outer_radius'])
        self.steps = spec['integration_steps']
        if (self.center.shape != (2,) or self.delta.shape != (2,) or
                not np.isfinite(self.center).all() or not np.isfinite(self.delta).all() or
                np.max(np.abs(self.center)) > 400000 or np.linalg.norm(self.delta) > 5000 or
                not 100 <= self.inner < self.outer-500 or self.outer > 30000 or
                not isinstance(self.steps, int) or isinstance(self.steps, bool) or
                not 64 <= self.steps <= 512):
            raise ValueError('Unsafe regional translation')
        self.lo = np.minimum(self.center, self.center+self.delta)-self.outer
        self.hi = np.maximum(self.center, self.center+self.delta)+self.outer

    def velocity(self, points, t):
        distance = np.linalg.norm(points-(self.center+t*self.delta), axis=1)
        u = np.clip((distance-self.inner)/(self.outer-self.inner), 0, 1)
        # Quintic smootherstep has zero first/second derivatives at both joins.
        blend = 1-u*u*u*(10+u*(-15+6*u))
        return blend[:, None]*self.delta

    def _integrate(self, points, reverse=False):
        result = np.asarray(points, dtype=float).reshape(-1, 2).copy()
        ids = np.flatnonzero(np.all((result > self.lo) & (result < self.hi), axis=1))
        h = (-1 if reverse else 1)/self.steps
        for start in range(0, len(ids), 16384):
            use = ids[start:start+16384]
            p = result[use].copy()
            for step in range(self.steps):
                t = 1-step/self.steps if reverse else step/self.steps
                a = self.velocity(p, t)
                b = self.velocity(p+a*h/2, t+h/2)
                c = self.velocity(p+b*h/2, t+h/2)
                d = self.velocity(p+c*h, t+h)
                p += h/6*(a+2*b+2*c+d)
            result[use] = p
        return result

    def __call__(self, points):
        return self._integrate(points)

    def inverse(self, points):
        return self._integrate(points, reverse=True)


class FeatureAdjustment:
    def __init__(self, spec):
        fields = {'method', 'landmark_flows', 'compact_steps'}
        if (not fields <= set(spec) or set(spec)-fields-{'translation_flows'} or
                spec['method'] != 'landmark-flow-ground-steps-v1' or
                not 1 <= len(spec['landmark_flows']) <= 8 or
                not 1 <= len(spec['compact_steps']) <= 32 or
                len(spec.get('translation_flows', [])) > 8):
            raise ValueError('Invalid feature adjustment')
        self.flows = [LandmarkFlow(v) for v in spec['landmark_flows']]
        self.flows += [RegionalTranslation(v) for v in spec.get('translation_flows', [])]
        self.steps = [CompactStep(v) for v in spec['compact_steps']]

    def __call__(self, points):
        for correction in [*self.flows, *self.steps]:
            points = correction(points)
        return points

    def inverse(self, points):
        for correction in reversed([*self.flows, *self.steps]):
            points = correction.inverse(points)
        return points

    def report(self):
        """Numerical checks; these do not certify continuous invertibility."""
        rows = []
        for step in self.steps:
            min_det, max_det, max_grad, samples = np.inf, -np.inf, 0., 0
            for grid in _grid_chunks(step.lo, step.hi, 500):
                a = step(grid+[.5, 0])-step(grid-[.5, 0])
                b = step(grid+[0, .5])-step(grid-[0, .5])
                jac = np.stack((a, b), axis=2)
                det = np.linalg.det(jac)
                grad = np.linalg.svd(jac-np.eye(2), compute_uv=False)[:, 0]
                min_det = min(min_det, float(det.min()))
                max_det = max(max_det, float(det.max()))
                max_grad = max(max_grad, float(grad.max()))
                samples += len(grid)
            if min_det <= .5 or max_grad >= .75:
                raise ValueError('Unsafe compact feature step')
            rows.append({'samples': samples, 'min_determinant': min_det,
                         'max_determinant': max_det,
                         'max_displacement_gradient_norm': max_grad})

        # Existing flow coverage remains dense near flow support and landmark
        # controls. Stream each grid so closely spaced or broad inputs cannot
        # allocate a continent-sized point array.
        flow_grids = [(flow.lo, flow.hi, 100) for flow in self.flows]
        control_grids = []
        for flow in self.flows:
            # Closely spaced real-city controls can expand from country scale
            # toward the game's nearly real-size landmark models. Sample their
            # source neighborhood much more densely than the city-wide grid.
            if isinstance(flow, LandmarkFlow):
                lo, hi = flow.p.min(axis=0)-200, flow.p.max(axis=0)+200
                control_grids.append((lo, hi, 5))

        active_steps = [step for step in self.steps if np.any(step.weights != 0)]
        composed_bounds = None
        if active_steps:
            composed_lo = np.min([step.lo for step in active_steps], axis=0)
            composed_hi = np.max([step.hi for step in active_steps], axis=0)
            composed_bounds = (composed_lo, composed_hi)
            composed_grids = [(composed_lo, composed_hi, 500)]
        else:
            composed_grids = []

        # The compact-step chain can accumulate compression far from any
        # landmark-flow controls. Sample its complete union support after all
        # flows and steps have composed. Keep only per-batch arrays live.
        grid_sources = [
            ('flow', flow_grids),
            ('control', control_grids),
            ('composed_step', composed_grids),
        ]
        source_samples = {}
        min_det, max_det = np.inf, -np.inf
        max_stretch, min_stretch, max_cycle = 0., np.inf, 0.
        worst_det_point = None
        for source, specs in grid_sources:
            source_count = 0
            for lo, hi, spacing in specs:
                for grid in _grid_chunks(lo, hi, spacing):
                    a = self(grid+[.5, 0])-self(grid-[.5, 0])
                    b = self(grid+[0, .5])-self(grid-[0, .5])
                    jac = np.stack((a, b), axis=2)
                    det = jac[:, 0, 0]*jac[:, 1, 1]-jac[:, 0, 1]*jac[:, 1, 0]
                    singular = np.linalg.svd(jac, compute_uv=False)
                    local_min = float(det.min())
                    if local_min < min_det:
                        min_det = local_min
                        worst_det_point = grid[int(np.argmin(det))].tolist()
                    max_det = max(max_det, float(det.max()))
                    max_stretch = max(max_stretch, float(singular[:, 0].max()))
                    min_stretch = min(min_stretch, float(singular[:, 1].min()))
                    mapped = self(grid)
                    cycle = np.linalg.norm(self.inverse(mapped)-grid, axis=1)
                    max_cycle = max(max_cycle, float(cycle.max()))
                    source_count += len(grid)
            source_samples[source] = source_count

        sample_count = sum(source_samples.values())
        if (min_det <= .05 or max_det >= 500 or max_stretch >= 30 or
                max_cycle > .05):
            raise ValueError(f'Unsafe composed feature correction: det={min_det}..{max_det}, '
                             f'cycle={max_cycle}, minimum determinant source XZ={worst_det_point}')
        return {'step_checks': rows, 'feature_grid_spacing_units': 100,
                'feature_grid_samples': sample_count, 'sample_counts_by_region': source_samples,
                'sample_grids': {
                    'flow_support': {'spacing_units': 100, 'samples': source_samples['flow']},
                    'control_neighborhoods': {'spacing_units': 5, 'samples': source_samples['control']},
                    'composed_compact_step_support': {
                        'spacing_units': 500, 'samples': source_samples['composed_step'],
                        'active_steps': len(active_steps),
                        'bounds_xz':
                            ([float(composed_lo[0]), float(composed_lo[1]),
                              float(composed_hi[0]), float(composed_hi[1])]
                             if composed_bounds is not None else None)}},
                'composed_step_grid_spacing_units': 500,
                'composed_step_grid_samples': source_samples['composed_step'],
                'composed_step_count': len(active_steps),
                'composed_step_support_bounds_xz':
                    ([float(composed_lo[0]), float(composed_lo[1]),
                      float(composed_hi[0]), float(composed_hi[1])]
                     if composed_bounds is not None else None),
                'min_determinant': min_det,
                'max_determinant': max_det, 'max_linear_stretch': max_stretch,
                'min_linear_stretch': min_stretch,
                'control_neighborhood_grid_spacing_units': 5,
                'max_inverse_cycle_units': max_cycle,
                'continuous_invertibility_proven': False}
