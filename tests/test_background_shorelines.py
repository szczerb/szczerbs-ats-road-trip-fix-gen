"""Regressions for finer shoreline data and lake-island preservation."""
from types import SimpleNamespace
from pathlib import Path

import pytest
pytest.importorskip('numpy')
pytest.importorskip('PIL')
pytest.importorskip('pyproj')
pytest.importorskip('scipy')
pytest.importorskip('shapefile')
import numpy as np
from PIL import ImageFont
from ats_road_trip.background import render as module


def test_selected_layers_preserve_land_inside_a_lake(monkeypatch):
    # Outer rings clockwise, inner rings counterclockwise, as in source shapefiles.
    country=SimpleNamespace(parts=[0],points=[(0,0),(0,100),(100,100),(100,0),(0,0)],bbox=[0,0,100,100])
    lake=SimpleNamespace(parts=[0,5],points=[(20,20),(20,80),(80,80),(80,20),(20,20),
        (40,40),(60,40),(60,60),(40,60),(40,40)],bbox=[20,20,80,80])
    country.points=[(x-100,y) for x,y in country.points]
    country.bbox=[-100,0,0,100]
    lake.points=[(x-100,y) for x,y in lake.points]
    lake.bbox=[-80,20,-20,80]
    seen=[]
    def features(path):
        seen.append(path)
        if path=='countries10':return iter([(country,{'ADM0_A3':'USA'})])
        if path=='lakes10':return iter([(lake,{})])
        return iter([])
    monkeypatch.setattr(module,'features',features)
    font=ImageFont.load_default()
    monkeypatch.setattr(module.ImageFont,'truetype',lambda *a,**k:font)
    config=dict(texture_size=100,world_bounds=[-100,0,0,100],geographic_extent=[-100,0,0,100],
        country_layer='ne_10m_admin_0_countries',lake_layer='ne_10m_lakes',preserve_lake_islands=True,
        palette=dict(water='#0000ff',land='#00ff00',USA='#00ff00',coast='#ffffff',province_border='#ffffff'),
        label_size=10,country_label_size=10,country_labels=[],suppress_labels=[],label_overrides={})
    image,_=module.render(config,{'ne_10m_admin_0_countries':'countries10','ne_10m_lakes':'lakes10',
        'ne_10m_admin_1_states_provinces':'states','ne_10m_admin_1_states_provinces_lines':'lines'},
        lambda p:np.asarray(p),Path('unused.ttf'))
    assert image.getpixel((10,50))==(0,255,0)
    assert image.getpixel((30,50))==(0,0,255)
    assert image.getpixel((50,50))==(0,255,0)
    assert 'countries10' in seen and 'lakes10' in seen


def test_local_corrections_retain_baseline_and_do_not_fit_check_points():
    import json
    from copy import deepcopy
    from ats_road_trip.background.geography import Calibration
    root=Path(__file__).resolve().parents[1]/'docs/examples/north-america-background'
    old_config=json.loads((root/'config.json').read_text())
    old_anchors=json.loads((root/'anchors.json').read_text())
    config=json.loads((root/'r1/config.json').read_text())
    anchors=json.loads((root/'r1/anchors.json').read_text())
    original=Calibration(old_config,old_anchors)
    current=Calibration(config,anchors)
    assert np.array_equal(current.affine,original.affine)
    far=[[-170,70],[-65,30],[-100,25]]
    assert np.array_equal(current(far),original(far))
    controls=[p for p in anchors if p['name'] in config['local_reference_names']]
    expected=[[p['x'],p['z']] for p in controls]
    current_errors=np.linalg.norm(current([[p['lon'],p['lat']] for p in controls])-expected,axis=1)
    original_errors=np.linalg.norm(original([[p['lon'],p['lat']] for p in controls])-expected,axis=1)
    assert np.sqrt(np.mean(current_errors**2)) < np.sqrt(np.mean(original_errors**2))*0.4
    assert current_errors.max()<2000
    changed=deepcopy(anchors)
    next(p for p in changed if p['role']=='check')['x']+=10000
    assert np.array_equal(current(far),Calibration(config,changed)(far))
    jacobian=current.jacobian_report(config['geographic_extent'])
    assert jacobian['samples']>30000 and jacobian['flipped_samples']==0
    assert config['zoom_uplift'][:7]==old_config['zoom_uplift'][:7]
    assert config['zoom_uplift'][7]*1.2==old_config['zoom_uplift'][7]
    for key in ('palette','map_items_flags','icon_size','city_icon_size','company_icon_size','world_bounds'):
        assert config[key]==old_config[key]


def _feature_adjustment(compact_steps, dense_control_groups=None, source_xz=None):
    from ats_road_trip.background.deformation import FeatureAdjustment
    if source_xz is None:
        source_xz=[[50000,50000],[50010,50000]]
    flow={'source_xz':source_xz,'target_xz':source_xz,
          'radius':1000,'integration_steps':64}
    if dense_control_groups is not None:
        flow['dense_control_groups']=dense_control_groups
    return FeatureAdjustment({'method':'landmark-flow-ground-steps-v1',
        'landmark_flows':[flow],'compact_steps':compact_steps})


def test_feature_report_checks_safe_composed_step_chain():
    # This mild nonzero step composes safely with an identity landmark flow.
    step={'radius':1000,'centers_xz':[[0,0]],'weights_xz':[[100,0]]}
    report=_feature_adjustment([step]).report()
    assert report['min_determinant']>.05
    assert report['composed_step_count']==1
    assert report['composed_step_grid_spacing_units']==500
    assert report['composed_step_grid_samples']>0
    assert report['sample_counts_by_region']['flow']>0
    assert report['sample_counts_by_region']['control']>0


def test_dense_control_groups_sample_each_declared_source_bbox():
    step={'radius':1000,'centers_xz':[[0,0]],'weights_xz':[[100,0]]}
    controls=[[50000,50000],[50010,50000],[50020,50000],[60000,60000]]
    groups=[[0,1,2],[3]]
    report=_feature_adjustment([step],groups,controls).report()
    rows=report['sample_grids']['control_neighborhoods']['groups']
    assert [row['source_indices'] for row in rows]==groups
    assert rows[0]['bounds_xz']==[49800.0,49800.0,50220.0,50200.0]
    assert rows[1]['bounds_xz']==[59800.0,59800.0,60200.0,60200.0]
    assert all(row['samples']>0 for row in rows)
    assert sum(row['samples'] for row in rows)==report['sample_counts_by_region']['control']
    assert report['sample_grids']['control_neighborhoods']['spacing_units']==5
    assert report['sample_grids']['flow_support']['spacing_units']==100
    assert report['sample_grids']['composed_compact_step_support']['spacing_units']==500


@pytest.mark.parametrize('groups',[
    [],                         # no groups
    [[]],                       # empty group
    [[0]],                      # missing source index
    [[0,1,2]],                  # out-of-range and missing index
    [[0,0],[1]],                # duplicate within a group
    [[0],[1],[1]],              # duplicate across groups and missing index
    [[True],[1]],               # bool is not an integer index here
    [[0],[1.0]],                # non-integer index
])
def test_dense_control_groups_reject_invalid_membership(groups):
    from ats_road_trip.background.deformation import LandmarkFlow
    with pytest.raises(ValueError,match='dense control groups'):
        LandmarkFlow({'source_xz':[[0,0],[10,0]],'target_xz':[[0,0],[10,0]],
                      'radius':1000,'integration_steps':64,
                      'dense_control_groups':groups})


def test_default_dense_control_group_preserves_combined_bbox_sampling():
    step={'radius':1000,'centers_xz':[[0,0]],'weights_xz':[[100,0]]}
    report=_feature_adjustment([step]).report()
    control=report['sample_grids']['control_neighborhoods']
    # Previously all controls in this flow shared this exact source bbox and grid.
    assert control['groups']==[{
        'flow_index':0,'group_index':0,'source_indices':[0,1],
        'bounds_xz':[49800.0,49800.0,50210.0,50200.0],
        'samples':6723}]
    assert control['samples']==6723
    assert report['sample_counts_by_region']['control']==6723


def test_feature_report_rejects_cumulative_compression_between_flows():
    # A symmetric pair of controls keeps the origin fixed while each step
    # contracts its X axis by about 10%. Each step passes its own limits, but
    # the 32-step chain has determinant below the composed .05 guard at 0,0.
    step={'radius':1000,'centers_xz':[[-500,0],[500,0]],
          'weights_xz':[[40,0],[-40,0]]}
    individual=_feature_adjustment([step]).report()
    assert individual['step_checks'][0]['min_determinant']>.5
    assert individual['step_checks'][0]['max_displacement_gradient_norm']<.75
    chain=_feature_adjustment([step.copy() for _ in range(32)])
    with pytest.raises(ValueError,match=r'minimum determinant source XZ=\[0.0, 0.0\]'):
        chain.report()
