"""Meaningful geometry regressions: inverses, support and unsafe input rejection."""
import pytest
np = pytest.importorskip('numpy')
pytest.importorskip('scipy')
from ats_road_trip.background.deformation import CompactStep, LandmarkFlow, RegionalTranslation


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


def test_regional_flow_moves_whole_feature_without_shrinking_it():
    flow = RegionalTranslation(dict(center_xz=[100, -200], delta_xz=[420, 530],
        inner_radius=1700, outer_radius=3000, integration_steps=96))
    # A lake-sized polygon, not merely its center, must retain shape and area.
    feature = np.array([[-900., -700], [900, -900], [1300, 300], [100, 900], [-800, 500]])
    moved = flow(feature)
    assert np.max(np.abs(moved-feature-[420, 530])) < 1e-6
    assert np.max(np.abs(np.diff(moved, axis=0)-np.diff(feature, axis=0))) < 1e-6
    points = np.r_[feature, [[2200, -300], [-2200, 700], [9000, 9000]]]
    assert np.array_equal(flow(points)[-1], points[-1])
    assert np.max(np.abs(flow.inverse(flow(points))-points)) < 1e-5
    x, z = np.meshgrid(np.arange(-3500, 4001, 250), np.arange(-3500, 4001, 250))
    grid = np.c_[x.ravel(), z.ravel()]
    a = flow(grid+[.5, 0])-flow(grid-[.5, 0])
    b = flow(grid+[0, .5])-flow(grid-[0, .5])
    assert np.min(a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0]) > .1


def test_regional_flow_rejects_unbounded_or_degenerate_support():
    spec = dict(center_xz=[0, 0], delta_xz=[100, 100], inner_radius=1700,
                outer_radius=3000, integration_steps=96)
    for change in ({'delta_xz': [np.nan, 0]}, {'delta_xz': [6000, 0]},
                   {'inner_radius': 2900}, {'integration_steps': True}):
        with pytest.raises(ValueError):
            RegionalTranslation({**spec, **change})
