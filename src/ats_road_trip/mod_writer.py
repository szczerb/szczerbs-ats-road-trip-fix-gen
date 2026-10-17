"""Create deterministic experimental packages without installing them."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

from .package import virtual_path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_mod(output: str | Path, resources: dict[str, bytes], report: dict,
              *, game_version: str, display_name: str | None = None,
              description: str | None = None) -> dict:
    """Write a new ZIP_STORED .scs, with source/change report included.

    Existing outputs are never overwritten. Caller must explicitly acknowledge
    experimental generation before invoking this function.
    """
    output = Path(output)
    if output.suffix.lower() != '.scs':
        raise ValueError('Output must have a .scs extension')
    if not re.fullmatch(r'1\.61(?:\.\d+)*', game_version):
        raise ValueError('This experimental prototype targets ATS 1.61 only')
    if not resources:
        raise ValueError('No supported changes; no empty mod will be generated')
    safe: dict[str, bytes] = {}
    reserved = {'manifest.sii', 'mod_description.txt', 'road_trip_fix_report.json'}
    for name, data in resources.items():
        clean = virtual_path(name)
        if clean in reserved:
            raise ValueError(f'Reserved generated metadata path: {name}')
        if clean in safe:
            raise ValueError(f'Duplicate output path: {name}')
        safe[clean] = data
    final_report = {**report, 'experimental': True, 'in_game_verified': False,
                    'game_version_declared': game_version,
                    'generated_resources': [{'path': name, 'size': len(data), 'sha256': sha256(data)}
                                            for name, data in sorted(safe.items())]}
    manifest = '''SiiNunit
{
mod_package : .roadtrip_fix
{
    package_version: "0.1.0-experimental"
    display_name: "Road Trip map compatibility experiment"
    author: "ATS Road Trip compatibility research"
    category[]: "map"
    compatible_versions[]: "1.61.*"
    dlc_dependencies[]: "dlc_rt_ford"
    description_file: "mod_description.txt"
}
}
'''
    if display_name is not None:
        if not isinstance(display_name, str) or not 1 <= len(display_name) <= 120 or not display_name.isprintable():
            raise ValueError('Display name must be 1-120 printable characters')
        manifest = manifest.replace('display_name: "Road Trip map compatibility experiment"',
                                    'display_name: ' + json.dumps(display_name))
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
