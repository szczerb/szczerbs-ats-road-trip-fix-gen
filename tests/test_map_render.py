import json
import struct
from zipfile import ZipFile

import pytest

Image = pytest.importorskip('PIL.Image')

from ats_road_trip.cli import main
from ats_road_trip.local_fuel import token
from ats_road_trip.map_render import MapRenderSession
from ats_road_trip.map_render_image import _background, footprint_bounds


EMPTY = struct.pack('<IQ4I', 907, token('euro2'), 3, 0, 0, 0)


def _archive(directory, name, files):
    path = directory / name
    with ZipFile(path, 'w') as archive:
        for member, data in files.items():
            archive.writestr(member, data)
    return path


@pytest.fixture
def atlas(tmp_path):
    background = tmp_path / 'background.png'
    Image.new('RGB', (32, 32), (60, 100, 130)).save(background)
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'texture_size': 32, 'world_bounds': [-8000, -8000, 8000, 8000]}))
    return {'background': background, 'background_config': config, 'long_edge': 512}


def test_north_up_and_outside_atlas():
    image = Image.new('RGB', (32, 32), 'blue')
    image.paste('green', (0, 0, 32, 16))
    transformed = _background(image, (0, 0, 32, 32), (-16, 0, 32, 32), (48, 32))
    assert transformed.getpixel((7, 7)) == (55, 59, 64)
    assert transformed.getpixel((20, 7)) == (0, 128, 0)
    assert transformed.getpixel((20, 24)) == (0, 0, 255)
    assert footprint_bounds({(-2, 1), (0, -1)}) == (-9000, -5000, 5000, 9000)


def test_standalone_geometry_keeps_hole_and_multiple_namespaces(tmp_path, atlas):
    source = _archive(tmp_path, 'map.scs', {
        'map/usa/sec-0001-0001.base': EMPTY,
        'map/usa/sec-0001-0001.layer': b'',
        'map/usa/sec+0001-0001.base': EMPTY,
        'map/custom/sec+0000+0000.base': EMPTY,
    })
    with MapRenderSession(output=tmp_path / 'output', **atlas) as session:
        report, _ = session.render([source])
    assert report['status'] == 'rendered'
    custom, usa = report['images']
    assert custom['namespace'] == 'custom'
    assert usa['namespace'] == 'usa'
    assert usa['tiles'] == {'map.scs': [[-1, -1, False], [1, -1, False]]}
    assert usa['geometry'][0]['counts']['sector_members_decoded'] == 2
    for image in report['images']:
        with Image.open(tmp_path / 'output' / image['file']) as png:
            assert max(png.size) == 512
            assert png.info == {}


def test_effective_shadowing_is_per_member_and_comparison_preserves_both(tmp_path, atlas):
    base = 'map/usa/sec+0000+0000.base'
    aux = 'map/usa/sec+0000+0000.aux'
    lower = _archive(tmp_path, 'expansion.scs', {base: EMPTY, aux: EMPTY})
    higher = _archive(tmp_path, 'connector.scs', {base: EMPTY})
    with MapRenderSession(output=tmp_path / 'output', **atlas) as session:
        comparison, _ = session.render([lower, higher], mode='comparison')
        effective, _ = session.render([lower, higher], mode='effective')
    assert comparison['images'][0]['tiles'] == {
        'expansion.scs': [[0, 0, False]], 'connector.scs': [[0, 0, False]],
    }
    assert effective['images'][0]['tiles'] == {
        'expansion.scs': [[0, 0, False]], 'connector.scs': [[0, 0, True]],
    }
    assert effective['shadowed_resources'] == [{
        'member': base, 'providers': ['expansion.scs', 'connector.scs'],
        'winner': 'connector.scs',
    }]
    assert set(effective['images'][0]['geometry'][0]['members']) == {base, aux}


def test_cli_skip_missing_and_unsupported_are_distinct(tmp_path, atlas, capsys, monkeypatch):
    monkeypatch.delenv('ATS_GAME_DIR', raising=False)
    valid = _archive(tmp_path, 'truck.scs', {'def/truck.sii': b'fixture'})
    corrupt = _archive(tmp_path, 'old-map.scs', {'map/usa/sec+0000+0000.base': b'invalid'})
    output = tmp_path / 'output'
    flags = [
        '--background', str(atlas['background']), '--background-config', str(atlas['background_config']),
        '--output-dir', str(output), '--long-edge', '512',
    ]
    for target, name, status, code in [
        (valid, 'no-map', 'no_sector_geometry', 0),
        (tmp_path / 'missing.scs', 'missing', 'failed', 1),
        (corrupt, 'unsupported', 'partial', 0),
    ]:
        assert main(['render-map', str(target), '--name', name, *flags]) == code
        stdout = json.loads(capsys.readouterr().out)
        report = (output / stdout['summary']).read_text()
        assert str(tmp_path) not in report
        assert json.loads(report)['status'] == status
    assert len(list(output.glob('*.png'))) == 1

    assert main([
        'render-map', str(valid), '--name', 'non-map-with-missing-dependency',
        '--dependency', str(tmp_path / 'missing-dependency.scs'), *flags,
    ]) == 0
    stdout = json.loads(capsys.readouterr().out)
    result = json.loads((output / stdout['summary']).read_text())
    assert result['status'] == 'no_sector_geometry'
    assert result['errors'][0]['role'] == 'dependency'
