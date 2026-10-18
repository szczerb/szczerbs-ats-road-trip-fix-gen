"""Create deterministic experimental packages without installing them."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile

from .package import virtual_path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or not value.isprintable():
        raise ValueError(f'{label} must be a nonempty printable string')
    return json.dumps(value, ensure_ascii=False)


def _validate_icon(data: bytes) -> None:
    """Check JPEG framing/dimensions without a runtime image dependency.

    This is metadata validation, not a JPEG decoder or a safety guarantee for
    arbitrary images. The game's documented icon canvas is exactly 276x162.
    """
    if not isinstance(data, bytes) or not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
        raise ValueError('Icon must be a JPEG with a complete SOI/EOI frame')
    offset = 2
    frames = {0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf}
    while offset < len(data) - 2:
        if data[offset] != 0xff:
            break
        while offset < len(data) and data[offset] == 0xff:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in (0xd9, 0xda):
            break
        if offset + 2 > len(data):
            break
        length = int.from_bytes(data[offset:offset + 2], 'big')
        if length < 2 or offset + length > len(data):
            break
        if marker in frames:
            if length < 8:
                break
            height, width = struct.unpack_from('>HH', data, offset + 3)
            components = data[offset + 7]
            if length != 8 + 3 * components or components not in (1, 3) or (width, height) != (276, 162):
                raise ValueError('Icon must be a 276x162 pixel grayscale or RGB JPEG')
            return
        offset += length
    raise ValueError('Icon has no supported JPEG frame header')


def write_mod(output: str | Path, resources: dict[str, bytes], report: dict,
              *, game_version: str, display_name: str | None = None,
              description: str | None = None, map_name: str | None = None,
              revision: int = 0, icon: bytes | None = None,
              fix_topics: tuple[str, ...] | None = None,
              category: str = 'map') -> dict:
    """Write a new ZIP_STORED .scs, with source/change report included.

    Existing outputs are never overwritten. Caller must explicitly acknowledge
    experimental generation before invoking this function.
    """
    output = Path(output)
    if category not in ('map', 'other'):
        raise ValueError('Supported manifest categories are map and other')
    if output.suffix.lower() != '.scs':
        raise ValueError('Output must have a .scs extension')
    if not re.fullmatch(r'1\.61(?:\.\d+)*', game_version):
        raise ValueError('This experimental prototype targets ATS 1.61 only')
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError('Revision must be a nonnegative integer')
    topic_titles = {frozenset({'fuel'}): 'Gas Stations Fix',
                    frozenset({'rest'}): 'Rest Stops Fix',
                    frozenset({'fuel', 'rest'}): 'Map Compatibility Fix'}
    if fix_topics is not None:
        if (not isinstance(fix_topics, tuple) or not fix_topics
                or any(not isinstance(topic, str) for topic in fix_topics)
                or len(set(fix_topics)) != len(fix_topics)
                or frozenset(fix_topics) not in topic_titles):
            raise ValueError('Fix topics must be a nonempty tuple of unique supported topics: fuel, rest')
        if map_name is None:
            raise ValueError('Fix topics require a map name')
    if map_name is not None:
        _manifest_text(map_name, 'Map name')
        if map_name != map_name.strip():
            raise ValueError('Map name must not have leading or trailing whitespace')
        if display_name is not None:
            raise ValueError('Specify map_name or display_name, not both')
        title = topic_titles[frozenset(fix_topics)] if fix_topics is not None else 'Gas Stations Fix'
        display_name = f"szczerb's Road Trip {title} for {map_name}"
    display_name = display_name if display_name is not None else 'Road Trip map compatibility experiment'
    display_literal = _manifest_text(display_name, 'Display name')
    package_version = '.'.join(game_version.split('.')[:2]) + f'-r{revision}-experimental'
    if icon is not None:
        _validate_icon(icon)
    if not resources:
        raise ValueError('No supported changes; no empty mod will be generated')
    safe: dict[str, bytes] = {}
    reserved = {'manifest.sii', 'mod_description.txt', 'road_trip_fix_report.json', 'mod_icon.jpg'}
    for name, data in resources.items():
        clean = virtual_path(name)
        if clean in reserved:
            raise ValueError(f'Reserved generated metadata path: {name}')
        if clean in safe:
            raise ValueError(f'Duplicate output path: {name}')
        safe[clean] = data
    metadata = {'display_name': display_name, 'author': 'szczerb',
                'package_version': package_version, 'map_name': map_name,
                'revision': revision}
    if fix_topics is not None:
        metadata['fix_topics'] = sorted(fix_topics)
    if category != 'map':
        metadata['category'] = category
    if icon is not None:
        metadata['icon'] = {'path': 'mod_icon.jpg', 'size': len(icon), 'sha256': sha256(icon)}
    final_report = {**report, 'experimental': True, 'in_game_verified': False,
                    'package_metadata': metadata,
                    'game_version_declared': game_version,
                    'generated_resources': [{'path': name, 'size': len(data), 'sha256': sha256(data)}
                                            for name, data in sorted(safe.items())]}
    manifest = f'''SiiNunit
{{
mod_package : .roadtrip_fix
{{
    package_version: {json.dumps(package_version)}
    display_name: {display_literal}
    author: "szczerb"
    category[]: {json.dumps(category)}
    compatible_versions[]: "1.61.*"
    dlc_dependencies[]: "dlc_rt_ford"
    description_file: "mod_description.txt"
}}
}}
'''
    if icon is not None:
        manifest = manifest.replace('    description_file:', '    icon: "mod_icon.jpg"\n    description_file:')
        safe['mod_icon.jpg'] = icon
    if description is None:
        description = ('Experimental generated compatibility candidate for ATS 1.61 / Road Trip Ford.\n'
                       'Not validated in game. Read road_trip_fix_report.json before testing.\n'
                       'Place above the source map/resource mods in a copied test profile.\n'
                       'PPD fuel candidates may require map spawn/service rebuilding and do not prove reachability.\n'
                       'Original archives, game installation, and profiles are not modified by this generator.\n')
    safe['manifest.sii'] = manifest.encode()
    safe['mod_description.txt'] = description.encode()
    safe['road_trip_fix_report.json'] = (json.dumps(final_report, indent=2, sort_keys=True) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED) as archive:
            created = True
            for name, data in sorted(safe.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    return final_report
