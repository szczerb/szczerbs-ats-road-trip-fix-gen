"""Reproducible original background build: python -m ats_road_trip.background."""
from __future__ import annotations

import argparse
from datetime import datetime
import importlib.metadata
import json
import math
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

import numpy as np

from .geography import Calibration, digest, source_files
from .render import render, icon, previews
from .resources import TITLE, archive_name, build_resources, validate_package, write_package, decode_texture

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT/'docs/examples/north-america-background/config.json'


def _finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Nonfinite configuration value')
    if isinstance(value, (list, dict)):
        for child in (value.values() if isinstance(value,dict) else value):
            _finite_tree(child)


def validate_inputs(config, anchors):
    _finite_tree(config)
    _finite_tree(anchors)
    if config['schema_version'] != 1 or config['title'] != TITLE or not isinstance(config['version'],str) or not re.fullmatch(r'1\.61-r\d+-experimental',config['version']):
        raise ValueError('Unsupported background identity/schema')
    if config['author'] != 'szczerb' or not re.fullmatch(r'1\.61(?:\.\d+)*', config['target_game']):
        raise ValueError('Unsupported author/game')
    if config['game_scale'] != 20:
        raise ValueError('This UI mapping requires the inspected ATS map scale 20')
    for key, allowed in (('country_layer',('ne_50m_admin_0_countries','ne_10m_admin_0_countries')),
                         ('lake_layer',('ne_50m_lakes','ne_10m_lakes'))):
        if key in config and config[key] not in allowed:
            raise ValueError('Unsupported geographic layer')
    if 'preserve_lake_islands' in config and not isinstance(config['preserve_lake_islands'],bool):
        raise ValueError('Lake-island policy must be boolean')
    for key in ('texture_size','overview_size'):
        v = config[key]
        if not isinstance(v,int) or isinstance(v,bool) or v < 32 or v > 16384 or v & (v-1):
            raise ValueError('Texture dimensions must be bounded powers of two')
    if config['overview_size'] > config['texture_size']//2:
        raise ValueError('Overview exceeds tile size')
    x0,z0,x1,z1 = config['world_bounds']
    if not x1 > x0 or not z1 > z0 or abs((x1-x0)-(z1-z0)) > 0.001:
        raise ValueError('World bounds must describe a positive square')
    if config['correction_smoothing'] < 0 or not 0 < config['camera_margin'] <= 100000:
        raise ValueError('Invalid smoothing/camera margin')
    for key in ('zoom_uplift','player_size','road_size_factor','full_detail','icon_size',
                'city_icon_size','company_icon_size','map_items_flags'):
        if len(config[key]) != 8:
            raise ValueError(f'Exactly eight {key} entries required')
    if any(v <= 0 for v in config['zoom_uplift']):
        raise ValueError('Zoom heights must be positive')
    if config['zoom_uplift'][:4] != sorted(config['zoom_uplift'][:4]) or config['zoom_uplift'][4:] != sorted(config['zoom_uplift'][4:]):
        raise ValueError('Zoom tiers must be ordered within each UI surface')
    for key in ('icon_size','city_icon_size','company_icon_size'):
        if any(len(v)!=2 or min(v)<0 for v in config[key]):
            raise ValueError('Invalid icon dimensions')
    for bounds in config['regions'].values():
        a,b,c,d = bounds
        if not (x0<=a<c<=x1 and z0<=b<d<=z1):
            raise ValueError('Preview region outside world bounds')
    ids = set()
    for p in anchors:
        if p['name'] in ids or p['role'] not in ('fit','check'):
            raise ValueError('Duplicate reference or unknown role')
        ids.add(p['name'])
        if not (-190<=p['lon']<=-45 and 7<=p['lat']<=84):
            raise ValueError('Reference outside geographic scope')
        if not (x0<p['x']<x1 and z0<p['z']<z1):
            raise ValueError('Reference outside world bounds')
    for role in ('fit','check'):
        if sum(p['role']==role for p in anchors) < config['validation']['minimum_'+role]:
            raise ValueError(f'Too few {role} references')
    for country in ('USA','CAN','MEX'):
        if not any(p['country']==country and p['role']=='check' for p in anchors):
            raise ValueError('Each target country needs held-out validation')
    if not any(p.get('region')=='Alaska' for p in anchors):
        raise ValueError('Alaska reference required')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--data-dir',type=Path)
    parser.add_argument('--download-data',action='store_true')
    parser.add_argument('--font',type=Path,required=True,help='Pinned DejaVuSans.ttf (see reproduction guide)')
    parser.add_argument('--run-id',default=None)
    parser.add_argument('--experimental',action='store_true',required=True)
    args = parser.parse_args(argv)
    run = args.run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d\d-\d\d_\d\d-\d\d-\d\d',run):
        parser.error('run-id must be a Europe/Warsaw timestamp YYYY-MM-DD_HH-MM-SS')
    config = json.loads(args.config.read_text())
    anchors_path = args.config.parent/'anchors.json'
    anchors = json.loads(anchors_path.read_text())
    manifest_path = args.config.parent/'sources.json'
    manifest = json.loads(manifest_path.read_text())
    validate_inputs(config,anchors)
    if digest(args.font.read_bytes()) != config['font_sha256']:
        raise ValueError('Font drift: use the exact recorded DejaVu Sans input')
    work = ROOT/'local_outputs/work'/run/'north-america-background'
    generated = ROOT/'local_outputs/generated'/run
    if work.exists() or generated.exists():
        raise FileExistsError('Run already exists; use a fresh timestamp')
    work.mkdir(parents=True)
    sources = source_files(manifest,args.data_dir or work/'source-data',download=args.download_data)
    calibration = Calibration(config,anchors)
    report = calibration.report(anchors)
    report['jacobian'] = calibration.jacobian_report(config['geographic_extent'])
    for role in ('fit','check'):
        if report['summary'][role]['max'] > config['validation']['max_'+role+'_error']:
            raise ValueError(f'{role} calibration error exceeds configured limit: {report["summary"][role]}')
    image,counts = render(config,sources,calibration,args.font)
    # Texture source image is retained for review/modification, never placed in the .scs.
    image.save(work/'original-background.png')
    previews(image,config,calibration,anchors,args.font,generated/'previews')
    mod_icon = icon(image,args.font)
    mod_icon.save(work/'icon.png')
    resources = build_resources(image,mod_icon,config,ROOT)
    package = generated/archive_name(config)
    sha = write_package(package,resources)
    audit = validate_package(package,config)
    # Exercise actual encoded DDS tiles, including their geographic quadrant order.
    from PIL import Image
    import io
    from PIL import ImageChops
    reconstructed = Image.new('RGB',(2048,2048))
    half = image.width//2
    for i,(x,y) in enumerate([(0,0),(0,half),(half,0),(half,half)]):
        tile = decode_texture(resources[f'material/ui/map/map{i}.dds']).convert('RGB')
        expected = image.crop((x,y,x+half,y+half))
        if ImageChops.difference(tile,expected).getbbox() is not None:
            raise ValueError('Encoded tile differs from its source quadrant')
        reconstructed.paste(tile.resize((1024,1024),Image.Resampling.LANCZOS),
                            (x*2048//image.width,y*2048//image.width))
    audit['dds_exact_quadrant_pixels'] = True
    reconstructed.save(generated/'previews/encoded-textures.png')
    report['cartography_counts'] = counts
    report['world_units_per_high_res_pixel'] = (config['world_bounds'][2]-config['world_bounds'][0])/config['texture_size']
    from PIL import features as pillow_features
    import zlib
    code_hashes = {str(p.relative_to(ROOT)):digest(p.read_bytes())
                   for p in sorted((ROOT/'src/ats_road_trip/background').glob('*.py'))}
    receipt = {'package':package.name,'sha256':sha,'runtime_verified':False,
        'configuration_sha256':digest(args.config.read_bytes()),'anchors_sha256':digest(anchors_path.read_bytes()),
        'source_manifest_sha256':digest(manifest_path.read_bytes()),'font_sha256':digest(args.font.read_bytes()),
        'source_data':manifest,'dependencies':{p:importlib.metadata.version(p) for p in ('Pillow','numpy','scipy','pyshp','pyproj')},
        'python':sys.version,'zlib':zlib.ZLIB_RUNTIME_VERSION,
        'freetype':pillow_features.version('freetype2'),'code_sha256':code_hashes,'work_directory':str(work),'calibration':report,'archive_audit':audit}
    for name,value in [('audit.json',audit),('calibration.json',report),('receipt.json',receipt)]:
        (work/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    (generated/'SHA256SUMS.txt').write_text(f'{sha}  {package.name}\n')
    print(json.dumps({'package':str(package),'sha256':sha,'preview':str(generated/'previews/index.html'),
                      'work':str(work),'calibration':report['summary']},indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
