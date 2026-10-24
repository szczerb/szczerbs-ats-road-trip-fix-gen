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


class FeatureAdjustment:
    def __init__(self, spec):
        if (set(spec) != {'method', 'landmark_flows', 'compact_steps'} or
                spec['method'] != 'landmark-flow-ground-steps-v1' or
                not 1 <= len(spec['landmark_flows']) <= 8 or
                not 1 <= len(spec['compact_steps']) <= 32):
            raise ValueError('Invalid feature adjustment')
        self.flows = [LandmarkFlow(v) for v in spec['landmark_flows']]
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
            gx, gz = np.meshgrid(np.arange(step.lo[0], step.hi[0]+500, 500),
                                 np.arange(step.lo[1], step.hi[1]+500, 500))
            grid = np.c_[gx.ravel(), gz.ravel()]
            a = (step(grid+[.5, 0])-step(grid-[.5, 0]))
            b = (step(grid+[0, .5])-step(grid-[0, .5]))
            jac = np.stack((a, b), axis=2)
            det = np.linalg.det(jac)
            grad = np.linalg.svd(jac-np.eye(2), compute_uv=False)[:, 0]
            if det.min() <= .5 or grad.max() >= .75:
                raise ValueError('Unsafe compact feature step')
            rows.append({'samples': len(grid), 'min_determinant': float(det.min()),
                         'max_determinant': float(det.max()),
                         'max_displacement_gradient_norm': float(grad.max())})
        # Dense local samples catch city expansion missed by the continental grid.
        checks = []
        for flow in self.flows:
            x, z = np.meshgrid(np.arange(flow.lo[0], flow.hi[0]+100, 100),
                               np.arange(flow.lo[1], flow.hi[1]+100, 100))
            checks.append(np.c_[x.ravel(), z.ravel()])
            # Closely spaced real-city controls can expand from country scale
            # toward the game's nearly real-size landmark models. Sample their
            # source neighborhood much more densely than the city-wide grid.
            lo, hi = flow.p.min(axis=0)-200, flow.p.max(axis=0)+200
            x, z = np.meshgrid(np.arange(lo[0], hi[0]+5, 5),
                               np.arange(lo[1], hi[1]+5, 5))
            checks.append(np.c_[x.ravel(), z.ravel()])
        grid = np.concatenate(checks)
        a = (self(grid+[.5, 0])-self(grid-[.5, 0]))
        b = (self(grid+[0, .5])-self(grid-[0, .5]))
        det = a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0]
        singular = np.linalg.svd(np.stack((a, b), axis=2), compute_uv=False)
        cycle = np.max(np.linalg.norm(self.inverse(self(grid))-grid, axis=1))
        if det.min() <= .05 or det.max() >= 500 or singular[:, 0].max() >= 30 or cycle > .05:
            raise ValueError(f'Unsafe composed feature correction: det={det.min()}..{det.max()}, cycle={cycle}')
        return {'step_checks': rows, 'feature_grid_spacing_units': 100,
                'feature_grid_samples': len(grid), 'min_determinant': float(det.min()),
                'max_determinant': float(det.max()), 'max_linear_stretch': float(singular[:, 0].max()),
                'min_linear_stretch': float(singular[:, 1].min()),
                'control_neighborhood_grid_spacing_units': 5,
                'max_inverse_cycle_units': float(cycle),
                'continuous_invertibility_proven': False}
