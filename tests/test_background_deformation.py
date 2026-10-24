"""Meaningful geometry regressions: inverses, support and unsafe input rejection."""
import pytest
np = pytest.importorskip('numpy')
pytest.importorskip('scipy')
from ats_road_trip.background.deformation import CompactStep, LandmarkFlow


def test_compact_step_preserves_far_geometry_and_reverses_nearby_points():
    step = CompactStep(dict(radius=6000, centers_xz=[[0, 0], [3000, 0]],
                            weights_xz=[[200, -300], [-100, 50]]))
    points = np.array([[0., 0.], [500, 700], [9000, 9000]])
    mapped = step(points)
    assert np.array_equal(mapped[-1], points[-1])
    assert np.linalg.norm(mapped[0]-points[0]) > 100
    assert np.max(np.abs(step.inverse(mapped)-points)) < 1e-5


def test_landmark_flow_transports_landmarks_and_retains_orientation():
    flow = LandmarkFlow(dict(radius=6000, integration_steps=96,
                             source_xz=[[-200, 0], [200, 0]],
                             target_xz=[[-600, 200], [600, -100]]))
    points = np.array([[-200., 0.], [200., 0.], [9000., 9000.]])
    mapped = flow(points)
    assert np.max(np.abs(mapped[:2]-np.array([[-600, 200], [600, -100]]))) < .01
    assert np.array_equal(mapped[-1], points[-1])
    assert np.max(np.abs(flow.inverse(mapped)-points)) < .01
    x, z = np.meshgrid(np.arange(-2000, 2001, 200), np.arange(-2000, 2001, 200))
    grid = np.c_[x.ravel(), z.ravel()]
    a = flow(grid+[.5, 0])-flow(grid-[.5, 0])
    b = flow(grid+[0, .5])-flow(grid-[0, .5])
    assert np.min(a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0]) > 0


def test_bad_feature_coefficient_and_integration_limit_are_rejected():
    with pytest.raises(ValueError):
        CompactStep(dict(radius=6000, centers_xz=[[0, 0]], weights_xz=[[np.inf, 0]]))
    with pytest.raises(ValueError):
        LandmarkFlow(dict(radius=6000, integration_steps=2,
                          source_xz=[[0, 0], [1, 1]], target_xz=[[2, 2], [3, 3]]))
