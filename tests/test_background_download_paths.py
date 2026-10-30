"""Regression coverage for background download-cache path isolation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

pytest.importorskip('numpy')
pytest.importorskip('PIL')
pytest.importorskip('scipy')
pytest.importorskip('shapefile')
pytest.importorskip('pyproj')

from ats_road_trip.background import __main__ as build_cli
from ats_road_trip.background import fetch, geography


MESSAGE = 'Downloads belong beneath this checkout local_outputs/work'


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    root = tmp_path / 'checkout'
    (root / 'local_outputs' / 'work').mkdir(parents=True)
    (root / 'local_inputs').mkdir()
    monkeypatch.setattr(geography, 'ROOT', root)
    monkeypatch.setattr(build_cli, 'ROOT', root)
    monkeypatch.setattr(fetch, 'ROOT', root)
    return root


def _geojson_source():
    payload = json.dumps({
        'type': 'FeatureCollection',
        'features': [{'type': 'Feature', 'geometry': None, 'properties': {}}],
    }).encode()
    manifest = {'fixture': {
        'format': 'geojson', 'url': 'https://example.invalid/fixture.geojson',
        'sha256': hashlib.sha256(payload).hexdigest(),
    }}
    return payload, manifest


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        assert limit >= len(self.payload)
        return self.payload


class _StopAfterSources(Exception):
    pass


def _write_cli_inputs(directory, payload, manifest, font_bytes=b'fixture font'):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'config.json').write_text(json.dumps({
        'font_sha256': hashlib.sha256(font_bytes).hexdigest(),
    }))
    (directory / 'anchors.json').write_text('[]')
    (directory / 'sources.json').write_text(json.dumps(manifest))
    font = directory / 'DejaVuSans.ttf'
    font.write_bytes(font_bytes)
    return font


@pytest.mark.parametrize('relative', [
    Path('outside/cache'),
    Path('local_inputs/cache'),
    Path('local_outputs/work/../../outside/cache'),
])
def test_source_download_rejects_external_paths_before_io(checkout, monkeypatch, relative):
    cache = checkout / relative
    calls = []
    monkeypatch.setattr(geography.urllib.request, 'urlopen', lambda *a, **k: calls.append(a))
    payload, manifest = _geojson_source()

    with pytest.raises(ValueError, match=MESSAGE):
        geography.source_files(manifest, cache, download=True)

    assert calls == []
    assert not cache.exists()


def test_source_download_rejects_cache_symlink_escape(checkout, tmp_path, monkeypatch):
    outside = tmp_path / 'outside'
    link = checkout / 'local_outputs' / 'work' / 'cache-link'
    link.symlink_to(outside, target_is_directory=True)
    calls = []
    monkeypatch.setattr(geography.urllib.request, 'urlopen', lambda *a, **k: calls.append(a))
    payload, manifest = _geojson_source()

    with pytest.raises(ValueError, match=MESSAGE):
        geography.source_files(manifest, link / 'nested', download=True)

    assert calls == []
    assert not outside.exists()


def test_source_download_rejects_symlinked_work_root(checkout, tmp_path, monkeypatch):
    outside = tmp_path / 'outside'
    work_link = checkout / 'local_outputs' / 'work'
    work_link.rmdir()
    work_link.symlink_to(outside, target_is_directory=True)
    calls = []
    monkeypatch.setattr(geography.urllib.request, 'urlopen', lambda *a, **k: calls.append(a))
    payload, manifest = _geojson_source()

    with pytest.raises(ValueError, match=MESSAGE):
        geography.source_files(manifest, work_link / 'cache', download=True)

    assert calls == []
    assert not outside.exists()


def test_allowed_download_cache_fetches_and_validates_geojson(checkout, monkeypatch):
    payload, manifest = _geojson_source()
    calls = []

    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        return _Response(payload)

    monkeypatch.setattr(geography.urllib.request, 'urlopen', fake_urlopen)
    cache = checkout / 'local_outputs' / 'work' / 'run' / 'source-data'
    result = geography.source_files(manifest, cache, download=True)

    assert calls == [(manifest['fixture']['url'], 120)]
    assert result['fixture'].read_bytes() == payload
    assert result['fixture'].parent == cache


def test_offline_loader_reads_external_cache_without_creating_directories(
        checkout, tmp_path, monkeypatch):
    payload, manifest = _geojson_source()
    external = tmp_path / 'external' / 'existing'
    external.mkdir(parents=True)
    source = external / 'fixture.geojson'
    source.write_bytes(payload)
    before = source.stat().st_mtime_ns

    original_mkdir = Path.mkdir

    def reject_mkdir(path, *args, **kwargs):
        raise AssertionError(f'offline loader attempted mkdir: {path}')

    monkeypatch.setattr(Path, 'mkdir', reject_mkdir)
    result = geography.source_files(manifest, external, download=False)
    monkeypatch.setattr(Path, 'mkdir', original_mkdir)

    assert result['fixture'] == source
    assert source.read_bytes() == payload
    assert source.stat().st_mtime_ns == before


def test_offline_loader_does_not_create_missing_external_cache(checkout, tmp_path):
    _, manifest = _geojson_source()
    missing = tmp_path / 'external' / 'absent'

    with pytest.raises(ValueError, match='Missing or changed dataset'):
        geography.source_files(manifest, missing, download=False)

    assert not missing.exists()
    assert not missing.parent.exists()


def _rejection_cache(checkout, tmp_path, route):
    if route == 'outside':
        return tmp_path / 'outside' / 'cache', tmp_path / 'outside'
    if route == 'local_inputs':
        return checkout / 'local_inputs' / 'cache', None
    if route == 'traversal':
        return checkout / 'local_outputs' / 'work' / '..' / '..' / 'outside' / 'cache', \
            checkout / 'outside'
    outside = tmp_path / 'outside'
    if route == 'cache_symlink':
        (checkout / 'local_outputs' / 'work' / 'cache-link').symlink_to(
            outside, target_is_directory=True)
        return checkout / 'local_outputs' / 'work' / 'cache-link' / 'cache', outside
    work = checkout / 'local_outputs' / 'work'
    work.rmdir()
    work.symlink_to(outside, target_is_directory=True)
    return work / 'cache', outside


@pytest.mark.parametrize('entrypoint', ['background', 'fetch'])
@pytest.mark.parametrize('route', [
    'outside', 'local_inputs', 'traversal', 'cache_symlink', 'work_symlink',
])
def test_download_cli_rejects_external_cache_before_reads_or_network(
        checkout, tmp_path, monkeypatch, entrypoint, route):
    cache, expected_outside = _rejection_cache(checkout, tmp_path, route)
    calls = []
    monkeypatch.setattr(geography.urllib.request, 'urlopen', lambda *a, **k: calls.append(a))
    args = []
    if entrypoint == 'background':
        args += ['--download-data', '--data-dir', str(cache),
                 '--font', str(checkout / 'missing-font.ttf'), '--experimental',
                 '--run-id', '2026-10-30_19-17-43']
        main = build_cli.main
    else:
        args = ['--output', str(cache),
                '--config-dir', str(checkout / 'missing-config')]
        main = fetch.main

    with pytest.raises(ValueError, match=MESSAGE):
        main(args)

    assert calls == []
    assert not cache.exists()
    if expected_outside is not None:
        assert not expected_outside.exists()
    assert not (checkout / 'local_outputs' / 'work' / '2026-10-30_19-17-43').exists()


def _stop_after_source_loading(monkeypatch):
    def stop(*args, **kwargs):
        raise _StopAfterSources
    monkeypatch.setattr(build_cli, 'validate_inputs', lambda *args: None)
    monkeypatch.setattr(build_cli, 'Calibration', stop)


def test_build_cli_downloads_to_default_cache(checkout, tmp_path, monkeypatch):
    payload, manifest = _geojson_source()
    config_dir = tmp_path / 'config'
    font = _write_cli_inputs(config_dir, payload, manifest)
    calls = []

    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        return _Response(payload)

    monkeypatch.setattr(geography.urllib.request, 'urlopen', fake_urlopen)
    _stop_after_source_loading(monkeypatch)
    run = '2026-10-30_19-17-43'
    with pytest.raises(_StopAfterSources):
        build_cli.main(['--config', str(config_dir / 'config.json'), '--font', str(font),
                        '--download-data', '--experimental', '--run-id', run])

    cache = checkout / 'local_outputs' / 'work' / run / 'north-america-background' / 'source-data'
    assert calls == [(manifest['fixture']['url'], 120)]
    assert (cache / 'fixture.geojson').read_bytes() == payload


def test_build_cli_forwards_external_offline_cache_without_mutation(
        checkout, tmp_path, monkeypatch):
    payload, manifest = _geojson_source()
    config_dir = tmp_path / 'config'
    font = _write_cli_inputs(config_dir, payload, manifest)
    cache = tmp_path / 'external' / 'cache'
    cache.mkdir(parents=True)
    source = cache / 'fixture.geojson'
    source.write_bytes(payload)
    before = source.stat().st_mtime_ns
    calls = []
    monkeypatch.setattr(geography.urllib.request, 'urlopen', lambda *a, **k: calls.append(a))
    _stop_after_source_loading(monkeypatch)

    with pytest.raises(_StopAfterSources):
        build_cli.main(['--config', str(config_dir / 'config.json'), '--font', str(font),
                        '--data-dir', str(cache), '--experimental', '--run-id',
                        '2026-10-30_19-17-43'])

    assert calls == []
    assert source.read_bytes() == payload
    assert source.stat().st_mtime_ns == before
    assert list(cache.iterdir()) == [source]


def test_fetch_cli_downloads_to_allowed_output_and_uses_cached_font(
        checkout, tmp_path, monkeypatch):
    payload, manifest = _geojson_source()
    config_dir = tmp_path / 'config'
    font_bytes = b'fixture font'
    _write_cli_inputs(config_dir, payload, manifest, font_bytes)
    (config_dir / 'font.json').write_text(json.dumps({
        'font_sha256': hashlib.sha256(font_bytes).hexdigest(),
        'url': 'https://example.invalid/font.deb',
    }))
    output = checkout / 'local_outputs' / 'work' / 'fetch-run'
    output.mkdir(parents=True)
    (output / 'DejaVuSans.ttf').write_bytes(font_bytes)
    calls = []

    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        return _Response(payload)

    monkeypatch.setattr(geography.urllib.request, 'urlopen', fake_urlopen)
    assert fetch.main(['--output', str(output), '--config-dir', str(config_dir)]) == 0
    assert calls == [(manifest['fixture']['url'], 120)]
    assert (output / 'fixture.geojson').read_bytes() == payload
    assert (output / 'DejaVuSans.ttf').read_bytes() == font_bytes
