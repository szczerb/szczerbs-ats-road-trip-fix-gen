"""Author standalone ATS UI resources; never import third-party definitions."""
from __future__ import annotations

import io
import json
import re
import struct
import zipfile
from pathlib import Path

from PIL import Image

from ..sii import parse_units
from ..mod_writer import _validate_icon
from .geography import digest


TITLE = "szczerb's Road Trip North America Background Map"
ARCHIVE_NAME = 'szczerbs-road-trip-north-america-background-map-ats-1.61-r0-experimental.scs'
_PACKAGE_VERSION = re.compile(r'1\.61-r(?P<revision>\d+)-experimental\Z')


def package_version(config):
    version = config.get('version')
    match = _PACKAGE_VERSION.fullmatch(version) if isinstance(version, str) else None
    if match is None:
        raise ValueError('Unsupported background package version')
    return version, int(match.group('revision'))


def archive_name(config):
    """Return the versioned archive name; retain the historical r0 constant."""
    version, revision = package_version(config)
    if revision == 0:
        return ARCHIVE_NAME
    return f'szczerbs-road-trip-north-america-background-map-ats-{version}.scs'

# Numeric interoperability settings observed in ATS 1.61.3.18 stock definitions.
# Authored serialization below does not copy source comments or definition text.
COLORS = {
    'road_color': 0xFF707070, 'road_discovered_color': 0xFF20BCFF,
    'job_road_color': 0x50353535, 'job_road_discovered_color': 0xFF2B3436,
    'world_road_color': 0xFF707070, 'world_road_discovered_color': 0xFF20BCFF,
    'fleet_manager_road_color': 0xFF424242, 'fleet_manager_road_discovered_color': 0xFF424242,
    'prefab_color': 0xFF737373, 'prefab_obstacle_color': 0xFF333333,
    'prefab_grass_color': 0xFF737373, 'prefab_discovered_color': 0xFF98CAEB,
    'prefab_obstacle_discovered_color': 0xFF3BA2E0, 'prefab_grass_discovered_color': 0xFF95CAA9,
    'outline_color': 0xFF000000, 'navigation_color': 0xFF0C0CCF,
    'navigation_highlight_color': 0xFF0C42DF, 'navigation_fade_color': 0xFF07077C,
    'navigation_arrow_color': 0xFF06FB11,
}
AREA_COLORS = [
    ('Road', 0xFF707070, 0xFF20BCFF), ('Light', 0xFF737373, 0xFF98CAEB),
    ('Dark', 0xFF333333, 0xFF3BA2E0), ('Green', 0xFF737373, 0xFF95CAA9),
    ('Nav-Red', 0xFF787890, 0xFF000099), ('Nav-Green', 0xFF759076, 0xFF35A54D),
    ('Nav-Blue', 0xFF907576, 0xFFD9772F), ('Nav-Yellow', 0xFF778F90, 0xFF24D4EC),
    ('Nav-Purple', 0xFF827279, 0xFFA93E6E),
]
STOCK_MASKS = [0x0F685FFF]*4 + [0x0F685FAF, 0x0F685FAF, 0x0F685487, 0x0C481402]


def literal(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list):
        return '(' + ', '.join(literal(v) for v in value) + ')'
    return str(value)


def map_data(config):
    lines = ['SiiNunit', '{', 'map_data : .map.data', '{',
             ' # Original standalone background settings; ATS 1.61 numeric interoperability defaults.']
    for key, value in COLORS.items():
        lines.append(f' {key}: 0x{value:08X}')
    for name, original, discovered in AREA_COLORS:
        lines += [f' map_area_color_name[]: {json.dumps(name)}',
                  f' map_area_color[]: 0x{original:08X}',
                  f' map_area_discovered_color[]: 0x{discovered:08X}']
    for key in ('zoom_uplift','player_size','road_size_factor','full_detail',
                'icon_size','city_icon_size','company_icon_size','map_items_flags'):
        for i, value in enumerate(config[key]):
            lines.append(f' {key}[{i}]: {literal(value)}')
    x0,z0,x1,z1 = config['world_bounds']
    for i in range(8):
        margin = config['camera_margin'] if i >= 4 else 1000000
        lines += [f' camera_limits_min[{i}]: ({x0-margin}, {z0-margin})',
                  f' camera_limits_max[{i}]: ({x1+margin}, {z1+margin})']
    # ui_map_size is in real km; the map's normal scale maps it into world units.
    size = [(x1-x0)*config['game_scale']/1000, (z1-z0)*config['game_scale']/1000]
    center = [(x0+x1)/2, (z0+z1)/2]
    lines += [f' ui_map_center: {literal(center)}', f' ui_map_size: {literal(size)}',
              f' ui_map_camera_min: ({x0}, {z0})', f' ui_map_camera_max: ({x1}, {z1})',
              f' ui_map_camera_start: {literal(config["ui_map_camera_start"])}',
              ' ui_map_always_draw_city: true', ' map_3d_camera_pitch: 40.0',
              ' navigation_city_penalty: 1.0', ' navigation_slow_road_penalty: 5.0',
              ' navigation_maximum_speed: 30.6', '}', '}', '']
    return '\n'.join(lines).encode()


def material(name):
    return (f'effect : "ui.rfx" {{\n texture : "texture" {{\n  source : "{name}.tobj"\n'
            '  u_address : clamp\n  v_address : clamp\n  mip_filter : none\n }\n}\n').encode()


def tobj(path):
    """Serialize observed 2D UI TOBJ v1 fields, not a copied source asset."""
    raw = path.encode('ascii')
    header = bytearray(40)
    struct.pack_into('<I', header, 0, 0x70B10A01)
    header[20] = 1
    header[24] = 2
    header[26:29] = bytes([3,3,2])
    header[30:32] = bytes([2,2])
    header[37] = 1
    return bytes(header) + struct.pack('<II', len(raw), 0) + raw


def texture(image):
    """Serialize the observed DX10 BGRA8 sRGB 2D format, with one mip."""
    width, height = image.size
    values = [124, 0x21007, height, width, 0, 0, 1] + [0]*11
    values += [32,4,int.from_bytes(b'DX10','little'),0,0,0,0,0,0x1000,0,0,0,0]
    values += [91,3,0,1,0]  # B8G8R8A8_UNORM_SRGB, 2D, one texture
    return b'DDS ' + struct.pack('<36I',*values) + image.convert('RGBA').tobytes('raw','BGRA')


def decode_texture(data):
    """Decode our inspected BGRA8 sRGB layout without Pillow's DDS format limits."""
    if len(data)<148 or data[:4]!=b'DDS ' or data[84:88]!=b'DX10':
        raise ValueError('Not a supported DX10 DDS')
    height,width = struct.unpack_from('<II',data,12)
    if struct.unpack_from('<5I',data,128)!=(91,3,0,1,0) or len(data)!=148+width*height*4:
        raise ValueError('Unexpected DDS DXGI layout')
    return Image.frombytes('RGBA',(width,height),data[148:],'raw','BGRA')


def build_resources(image, mod_icon, config, root):
    version, revision = package_version(config)
    resources = {'def/map_data.sii': map_data(config)}
    # map is the low-resolution whole backdrop; map0..3 are high-resolution tiles.
    # Quadrant contract is independently inspected against installed UI resources.
    half = image.width//2
    boxes = [(0,0,half,half),(0,half,half,2*half),
             (half,0,2*half,half),(half,half,2*half,2*half)]
    for i, name in enumerate(('map','map0','map1','map2','map3')):
        tile = (image.resize((config['overview_size'],)*2, Image.Resampling.LANCZOS)
                if name == 'map' else image.crop(boxes[i-1]))
        base = 'material/ui/map/'+name
        resources[base+'.mat'] = material(name)
        resources[base+'.tobj'] = tobj('/'+base+'.dds')
        resources[base+'.dds'] = texture(tile)
    out = io.BytesIO()
    mod_icon.save(out, format='JPEG', quality=92, subsampling=0, optimize=False)
    resources['mod_icon.jpg'] = out.getvalue()
    resources['manifest.sii'] = (f'''SiiNunit
{{
mod_package : .szczerb.na_bcg
{{
 package_version: {json.dumps(version)}
 display_name: {json.dumps(TITLE)}
 author: "szczerb"
 category[]: "map"
 compatible_versions[]: "1.61.*"
 icon: "mod_icon.jpg"
 description_file: "mod_description.txt"
}}
}}
''').encode()
    description = b'''Original geographic background for ATS 1.61: contiguous USA, Alaska, Canada and Mexico.
Country/province borders, restrained labels, extended bounds and car fuel/rest navigation icons.
Experimental: runtime rendering and geographic fit await manual testing. No playable roads or map sectors.
Requires ATS 1.61; no Ford DLC dependency. Map expansions keep their own requirements.
HIGH priority: place above ALL map/background/map-data overrides, including Reforma OtherMaps Patch,
ProMods definitions and Reforma ProMods Background Fix. Keep map sources/fixes in their existing order below.
Disable the former North America Background Map 5.3, every N1/N2 overlay and other background maps.
Replaces the geographic background and N2 presentation fix; retain your separate fuel/rest/courier/tank mods.
Made with Natural Earth public-domain data. Original artwork/definitions: AGPL-3.0-only, szczerb, 2026.
Licenses and data attribution are included. No diagnostics or game/map assets included.
'''
    resources['LICENSE.txt'] = (root/'LICENSE').read_bytes()
    resources['FONT-LICENSE.txt'] = (root/'assets/background-map/FONT-LICENSE.txt').read_bytes()
    notice = b'''Made with Natural Earth. Geographic source datasets are public domain:
https://www.naturalearthdata.com/about/terms-of-use/
50m countries 5.1.1; 10m states/provinces 5.1.1; 10m internal boundaries 5.1.0;
50m lakes 5.0.0; 10m populated places 5.1.2.
Original cartographic composition, definitions and icon: Copyright (C) 2026 szczerb; AGPL-3.0-only.
Generator/preferred modification source: ats_road_trip.background with versioned configuration/data pins
in docs/examples/north-america-background. Provide these sources with redistributed authored artwork.
DejaVu Sans text is rendered into images; no font file is bundled. Its notice is in FONT-LICENSE.txt.
No CairamR/CAIRAM, SCS or third-party map artwork or definition files are copied into this package.
Names of games and maps identify compatibility and do not imply endorsement.
'''
    if revision > 0:
        text = notice.decode()
        country_layer = config.get('country_layer')
        lake_layer = config.get('lake_layer')
        if isinstance(country_layer, str) and country_layer.startswith('ne_10m_'):
            text = text.replace('50m countries 5.1.1', '10m countries 5.1.1')
        if isinstance(lake_layer, str) and lake_layer.startswith('ne_10m_'):
            text = text.replace('50m lakes 5.0.0', '10m lakes 5.0.0')
        if 'NRCan-CGNDB' in config.get('geographic_reference_sources',[]):
            text += ('\nSeven geographic calibration references: Natural Resources Canada, Canadian Geographical Names Database.\n'
                     'Contains information licensed under the Open Government Licence – Canada.\n'
                     'https://open.canada.ca/en/open-government-licence-canada\n')
        if 'USGS-GNIS' in config.get('geographic_reference_sources',[]):
            text += ('Two geographic calibration references: U.S. Geological Survey, Geographic Names Information System,\n'
                     'public-domain data retrieved from the official Alaska Department of Fish and Game GNIS mirror.\n'
                     'No official status or endorsement is implied. Reference IDs and retrieval provenance accompany the generator source.\n')
        notice = text.encode()
    resources['DATA-NOTICE.txt'] = notice
    if revision > 0:
        description = b'''Original geographic background for ATS 1.61: contiguous USA, Alaska, Canada and Mexico.
Finer geographic detail, regional corrections and a closer shared far-zoom setting.
Experimental: runtime rendering, geographic fit and zoom behavior await manual testing. No playable roads or map sectors.
Requires ATS 1.61; no Ford DLC dependency. Map expansions keep their own requirements.
HIGH priority: place above ALL map/background/map-data overrides, including Reforma OtherMaps Patch,
ProMods definitions and Reforma ProMods Background Fix. Keep map sources/fixes in their existing order below.
Disable the former North America Background Map 5.3, every N1/N2 overlay and other background maps.
Replaces the geographic background and N2 presentation fix; retain your separate fuel/rest/courier/tank mods.
Made with Natural Earth public-domain data. Original artwork/definitions: AGPL-3.0-only, szczerb, 2026.
Licenses and data attribution are included. No diagnostics or game/map assets included.
'''
    if revision == 2:
        description += (b'R2: shared far zoom is closer; all-layer road/ground calibration. Residual coastal/lake mismatches remain.\n'
                        b'Use the accompanying r2 handoff and comparison previews; in-game acceptance is pending.\n')
        resources['DATA-NOTICE.txt'] += (b'\nR2 calibration also uses Natural Earth North America roads 4.1.0 (public domain).\n'
            b'Official SICT Datos Viales Baja California (2014) and Baja California Sur (2015) station facts\n'
            b'identify federal route corridors; no source tables, native road geometry or bridge assets are bundled.\n'
            b'Calibration parameters and provenance: docs/examples/north-america-background/r2.\n')
    resources['mod_description.txt'] = description
    return resources


def write_package(path, resources):
    """Stable deflated ZIP .scs; reports remain outside it. Refuse overwrite."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, payload in sorted(resources.items()):
                info = zipfile.ZipInfo(name, date_time=(2026,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                info.create_system = 3
                archive.writestr(info, payload)
    return digest(path.read_bytes())


def validate_package(path, config):
    version, _revision = package_version(config)
    expected = {'def/map_data.sii','manifest.sii','mod_description.txt','mod_icon.jpg',
                'LICENSE.txt','FONT-LICENSE.txt','DATA-NOTICE.txt'}
    expected |= {f'material/ui/map/{name}.{ext}' for name in ('map','map0','map1','map2','map3')
                 for ext in ('mat','tobj','dds')}
    checks = {}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != expected or archive.testzip() is not None:
            raise ValueError('Archive integrity/allowlist failure')
        data = {n:archive.read(n) for n in names}
        units = parse_units(data['def/map_data.sii'].decode())
        if len(units) != 1 or units[0].name != '.map.data' or units[0].attribute_errors:
            raise ValueError('Invalid map definition')
        unit = units[0]
        if [int(v,0) for v in unit.values('map_items_flags')] != STOCK_MASKS:
            raise ValueError('Unrelated icon mask behavior changed')
        for i in range(4):
            if int(unit.values('map_items_flags')[i],0) & 0x03000000 != 0x03000000:
                raise ValueError('Car navigation mask absent')
        if '@include' in data['def/map_data.sii'].decode():
            raise ValueError('Standalone definition must not depend on includes')
        manifest_units = parse_units(data['manifest.sii'].decode())
        if len(manifest_units)!=1 or manifest_units[0].kind!='mod_package':
            raise ValueError('Expected one mod package unit')
        manifest = manifest_units[0]
        for parsed in [*units,manifest]:
            components = parsed.name.lstrip('.').split('.')
            if len(components)>10 or any(not re.fullmatch(r'[a-z0-9_]{1,12}',c) for c in components):
                raise ValueError('Invalid SCS unit-name token (12-character limit)')
        if (manifest.attribute_errors or manifest.values('dlc_dependencies')
                or manifest.one('display_name') != TITLE
                or manifest.one('author') != 'szczerb'
                or manifest.one('package_version') != version
                or manifest.values('compatible_versions') != ('1.61.*',)):
            raise ValueError('Metadata/dependency mismatch')
        if data['def/map_data.sii'] != map_data(config):
            raise ValueError('Map numeric configuration differs from validated input')
        _validate_icon(data['mod_icon.jpg'])
        for name in ('map','map0','map1','map2','map3'):
            base = 'material/ui/map/'+name
            for ref in re.findall(r'source\s*:\s*"([^"]+)"', data[base+'.mat'].decode()):
                if 'material/ui/map/'+ref not in data:
                    raise ValueError('Missing material dependency')
            obj = data[base+'.tobj']
            if len(obj) < 48 or struct.unpack_from('<I',obj)[0] != 0x70B10A01:
                raise ValueError('Invalid TOBJ')
            length,reserved = struct.unpack_from('<II',obj,40)
            referenced = obj[48:].decode('ascii').lstrip('/')
            if reserved or length != len(obj)-48 or referenced not in data:
                raise ValueError('Missing texture dependency')
            if obj != tobj('/'+base+'.dds'):
                raise ValueError('Unexpected TOBJ configuration')
            dds = data[referenced]
            size = config['overview_size'] if name == 'map' else config['texture_size']//2
            height,width = struct.unpack_from('<II',dds,12)
            if dds[:4] != b'DDS ' or (width,height) != (size,size) or dds[84:88] != b'DX10' or struct.unpack_from('<5I',dds,128) != (91,3,0,1,0):
                raise ValueError('Unexpected texture format/dimensions')
            if len(dds) != 148+size*size*4 or struct.unpack_from('<I',dds,20)[0] != 0 or struct.unpack_from('<I',dds,8)[0] != 0x21007 or struct.unpack_from('<I',dds,28)[0] != 1:
                raise ValueError('Invalid BGRA8 DDS length/pitch/mips')
            with decode_texture(dds) as image:
                image.load()
                if image.getextrema()[3] != (255,255):
                    raise ValueError('Unexpected transparency')
            checks[name] = {'dimensions':[size,size],'format':'DX10/B8G8R8A8_UNORM_SRGB','mips':1,
                            'sha256':digest(dds),'opaque':True}
    return {'archive_sha256':digest(path.read_bytes()),'members':len(names),
            'resource_graph_closed':True,'missing_includes':0,'ford_dependency':False,
            'scs_unit_name_tokens_valid':True,'stock_icon_masks_preserved':True,'car_fuel_and_parking_local_bits':True,
            'textures':checks,'in_game_verified':False,
            'member_sha256':{n:digest(v) for n,v in sorted(data.items())}}
