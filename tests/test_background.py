"""Offline behavioral checks for standalone original background generation."""
from copy import deepcopy
import io
import json
from pathlib import Path
import struct
import zipfile

import pytest

pytest.importorskip('numpy')
pytest.importorskip('PIL')
pytest.importorskip('scipy')
pytest.importorskip('pyproj')
pytest.importorskip('shapefile')
import numpy as np
from PIL import Image, ImageDraw

from ats_road_trip.background.geography import Calibration, CompactDisplacement, source_files
from ats_road_trip.background.resources import (
    ARCHIVE_NAME, archive_name, build_resources, decode_texture, map_data,
    validate_package, write_package,
)
from ats_road_trip.background.__main__ import validate_inputs
from ats_road_trip.sii import parse_units

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def config():
    c=json.loads((ROOT/'docs/examples/north-america-background/config.json').read_text())
    c['texture_size']=64
    c['overview_size']=32
    return c


@pytest.fixture
def anchors(config):
    # An invented, exact affine game plane allows independent recovery checks.
    lonlat=[[-150,61],[-139,64],[-123,49],[-120,45],[-112,33],[-105,40],
            [-100,25],[-97,20],[-95,30],[-90,40],[-82,42],[-80,30],
            [-155,64],[-110,55],[-103,23],[-117,35],[-99,35],[-90,36]]
    p=Calibration.__new__(Calibration)
    from pyproj import Proj
    p.proj=Proj(**config['projection']);p.scale=20
    points=p.baseline(lonlat)
    result=[]
    for i,((lon,lat),(x,z)) in enumerate(zip(lonlat,points)):
        result.append({'name':f'Invented{i}','lon':lon,'lat':lat,
            'x':x*1.02+400,'z':z*0.99-200,'role':'fit' if i<12 else 'check',
            'country':('USA','CAN','MEX')[i%3],'region':'Alaska' if i==0 else 'fixture'})
    return result


def test_calibration_predicts_heldout_and_preserves_orientation(config,anchors):
    validate_inputs(config,anchors)
    c=Calibration(config,anchors)
    report=c.report(anchors)
    assert report['summary']['check']['max']<1e-6
    assert report['summary']['fit']['max']<1e-6
    assert c.jacobian_report(config['geographic_extent'])['flipped_samples']==0
    moved=deepcopy(anchors)
    moved[-1]['x']+=10000
    # Check points must not influence the fitted geographic transform.
    assert np.array_equal(c([[-90,36]]),Calibration(config,moved)([[-90,36]]))
    assert Calibration(config,moved).report(moved)['summary']['check']['max']>9999


def test_route_field_has_compact_support_and_composes_after_calibration(config,anchors):
    original=Calibration(config,anchors)
    center=original([[-112,33]])[0]
    field={'method':'route-normal-compact-v1','radius':10000,
           'centers_xz':[center.tolist()],'weights_xz':[[400,-200]]}
    config['road_adjustment']=field
    revised=Calibration(config,anchors)
    # A known displacement at the support center, and exact identity outside.
    assert np.allclose(revised([[-112,33]])-original([[-112,33]]),[[400,-200]])
    far=[[-155,64],[-80,30]]
    assert np.array_equal(revised(far),original(far))
    assert revised.jacobian_report(config['geographic_extent'])['flipped_samples']==0
    # Changing held-out survey targets still cannot change the reviewed field.
    moved=deepcopy(anchors);moved[-1]['z']+=2000
    assert np.array_equal(revised(far),Calibration(config,moved)(far))


@pytest.mark.parametrize('change',[
    {'radius':0}, {'centers_xz':[[1]]}, {'weights_xz':[[1,2],[3,4]]},
    {'weights_xz':[[float('inf'),0]]}, {'method':'unreviewed'}, {'extra':0},
])
def test_invalid_route_field_blocks(change):
    spec={'method':'route-normal-compact-v1','radius':10000,
          'centers_xz':[[0,0]],'weights_xz':[[100,200]]}
    spec.update(change)
    with pytest.raises(ValueError):CompactDisplacement(spec)


def test_route_field_fold_is_rejected_by_combined_jacobian(config,anchors):
    center=Calibration(config,anchors)([[-112,33]])[0]
    config['road_adjustment']={'method':'route-normal-compact-v1','radius':5000,
        'centers_xz':[center.tolist()],'weights_xz':[[15000,0]]}
    with pytest.raises(ValueError,match='Unsafe geographic deformation'):
        Calibration(config,anchors).jacobian_report(config['geographic_extent'])


@pytest.mark.parametrize('mutation',[
    lambda c,a:c['world_bounds'].__setitem__(2,float('nan')),
    lambda c,a:c.__setitem__('texture_size',63),
    lambda c,a:a.append(deepcopy(a[0])),
    lambda c,a:c['zoom_uplift'].__setitem__(7,-1),
    lambda c,a:c.__setitem__('game_scale',19),
])
def test_invalid_inputs_block(config,anchors,mutation):
    mutation(config,anchors)
    with pytest.raises(ValueError):validate_inputs(config,anchors)


def test_package_is_standalone_reproducible_and_quadrants_are_column_major(tmp_path,config):
    image=Image.new('RGB',(64,64))
    draw=ImageDraw.Draw(image)
    for box,color in [((0,0,31,31),'red'),((0,32,31,63),'green'),
                      ((32,0,63,31),'blue'),((32,32,63,63),'yellow')]:
        draw.rectangle(box,fill=color)
    resources=build_resources(image,Image.new('RGB',(276,162),'navy'),config,ROOT)
    for i,color in enumerate([(255,0,0),(0,128,0),(0,0,255),(255,255,0)]):
        tile=decode_texture(resources[f'material/ui/map/map{i}.dds'])
        assert tile.getpixel((16,16))==(*color,255)
    first,second=tmp_path/'one.scs',tmp_path/'two.scs'
    assert write_package(first,resources)==write_package(second,resources)
    audit=validate_package(first,config)
    assert audit['members']==22 and audit['resource_graph_closed']
    assert not audit['ford_dependency'] and not audit['in_game_verified']
    with pytest.raises(FileExistsError):write_package(first,resources)
    with zipfile.ZipFile(first) as z:
        manifest=z.read('manifest.sii')
        assert b'dlc_dependencies' not in manifest
        assert b'@include' not in z.read('def/map_data.sii')
        assert not any('report' in n or 'local_outputs' in n for n in z.namelist())


def test_package_revision_controls_filename_metadata_and_data_notice(tmp_path,config):
    assert archive_name(config)==ARCHIVE_NAME
    assert ARCHIVE_NAME.endswith('ats-1.61-r0-experimental.scs')
    r1=deepcopy(config)
    r1['version']='1.61-r1-experimental'
    r1['country_layer']='ne_10m_admin_0_countries'
    r1['lake_layer']='ne_10m_lakes'
    assert archive_name(r1)=='szczerbs-road-trip-north-america-background-map-ats-1.61-r1-experimental.scs'
    resources=build_resources(Image.new('RGB',(64,64),'teal'),Image.new('RGB',(276,162),'navy'),r1,ROOT)
    manifest=parse_units(resources['manifest.sii'].decode())[0]
    assert manifest.one('package_version')=='1.61-r1-experimental'
    notice=resources['DATA-NOTICE.txt'].decode()
    assert '10m countries 5.1.1' in notice and '10m lakes 5.0.0' in notice
    description=resources['mod_description.txt'].decode()
    assert all(term in description for term in ('Finer geographic detail','regional corrections',
                                                'closer shared far-zoom','await manual testing'))
    package=tmp_path/archive_name(r1)
    write_package(package,resources)
    validate_package(package,r1)
    with pytest.raises(ValueError,match='Metadata/dependency mismatch'):
        validate_package(package,config)
    invalid=deepcopy(r1)
    invalid['version']='1.62-r1-experimental'
    with pytest.raises(ValueError,match='Unsupported background package version'):
        archive_name(invalid)
    r2=deepcopy(r1)
    r2['version']='1.61-r2-experimental'
    r2_resources=build_resources(Image.new('RGB',(64,64),'teal'),Image.new('RGB',(276,162),'navy'),r2,ROOT)
    r2_description=r2_resources['mod_description.txt'].decode()
    assert 'Finer geographic detail, regional corrections and a closer shared far-zoom setting.' in r2_description
    assert 'than r0' not in r2_description


def test_missing_texture_and_changed_unrelated_mask_rejected(tmp_path,config):
    r=build_resources(Image.new('RGB',(64,64),'red'),Image.new('RGB',(276,162),'navy'),config,ROOT)
    r['material/ui/map/map0.tobj']=r['material/ui/map/map0.tobj'].replace(b'map0.dds',b'lost.dds')
    p=tmp_path/'missing.scs';write_package(p,r)
    with pytest.raises(ValueError,match='texture dependency'):validate_package(p,config)
    r=build_resources(Image.new('RGB',(64,64),'red'),Image.new('RGB',(276,162),'navy'),config,ROOT)
    r['def/map_data.sii']=r['def/map_data.sii'].replace(b'0x0F685FFF',b'0x03685FFF')
    p=tmp_path/'mask.scs';write_package(p,r)
    with pytest.raises(ValueError,match='icon mask'):validate_package(p,config)


def test_source_hash_drift_blocks_before_reading(tmp_path):
    (tmp_path/'invented.zip').write_bytes(b'not a dataset')
    with pytest.raises(ValueError,match='changed dataset'):
        source_files({'invented':{'sha256':'0'*64,'version':'1.0','url':'https://example.invalid/no'}},tmp_path)


def test_stock_navigation_inputs_are_serialized_completely(config):
    u=parse_units(map_data(config).decode())[0]
    assert len(u.values('map_area_color'))==9
    assert len(u.values('map_items_flags'))==8
    assert u.one('navigation_city_penalty')=='1.0'
    assert u.one('navigation_maximum_speed')=='30.6'
    assert u.values('player_size')==('15','35','120','500','90','350','900','2200')


def test_overlong_scs_unit_token_is_rejected(tmp_path,config):
    r=build_resources(Image.new('RGB',(64,64),'red'),Image.new('RGB',(276,162),'navy'),config,ROOT)
    r['manifest.sii']=r['manifest.sii'].replace(b'.szczerb.na_bcg',b'.szczerb.na_background')
    p=tmp_path/'overlong.scs';write_package(p,r)
    with pytest.raises(ValueError,match='unit-name token'):validate_package(p,config)
