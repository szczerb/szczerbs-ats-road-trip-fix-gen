"""Source-pinned r3 texture-size repair; leave its cartography and overview intact.

Run from the project root with the recorded r3 Python environment. The input is
project-authored r3 artwork; its complete editable source bundle remains linked
from the r3 handoff. No game or third-party map assets are required.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

from PIL import Image

from ats_road_trip.background.resources import (
    archive_name, decode_texture, texture, validate_package, write_package,
)

R3_SHA256 = '8d29a9531e4ffab939f11891042e3a5fc2260310d7919eae83797f0329be9329'
VERSION = '1.61-r4-experimental'
ROOT = Path(__file__).resolve().parents[4]
DETAILS = {f'material/ui/map/map{i}.dds' for i in range(4)}


def repair(source: Path, destination: Path):
    if hashlib.sha256(source.read_bytes()).hexdigest() != R3_SHA256:
        raise ValueError('Source drift: the exact delivered r3 archive is required')
    if destination.exists():
        raise FileExistsError(destination)
    config = deepcopy(json.loads((ROOT / 'docs/examples/north-america-background/r3/config.json').read_text()))
    config.update(version=VERSION, texture_size=8192)
    if destination.name != archive_name(config):
        raise ValueError('Use the exact r4 archive filename')
    with zipfile.ZipFile(source) as original:
        resources = {n: original.read(n) for n in original.namelist() if n not in DETAILS}
        for name in sorted(DETAILS):
            with decode_texture(original.read(name)) as image:
                if image.size != (8192, 8192):
                    raise ValueError('Unexpected source tile dimensions')
                with image.resize((4096, 4096), Image.Resampling.LANCZOS) as resized:
                    resources[name] = texture(resized)
            if len(resources[name]) != 148 + 4096 * 4096 * 4:
                raise ValueError('Unexpected corrected resource size')
        old_version = b'package_version: "1.61-r3-experimental"'
        if resources['manifest.sii'].count(old_version) != 1:
            raise ValueError('Unexpected source manifest')
        resources['manifest.sii'] = resources['manifest.sii'].replace(
            old_version, b'package_version: "1.61-r4-experimental"')
        unchanged = set(original.namelist()) - DETAILS - {'manifest.sii'}
        if any(resources[n] != original.read(n) for n in unchanged):
            raise ValueError('Unexpected non-texture change')
    package_sha = write_package(destination, resources)
    audit = validate_package(destination, config)
    return {
        'package': destination.name, 'sha256': package_sha,
        'source_sha256': R3_SHA256, 'runtime_verified': False,
        'changes': 'Four detailed DDS tiles resized 8192 to 4096 with LANCZOS; manifest revision only.',
        'unchanged_members': sorted(unchanged), 'validation': audit,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(repair(args.source, args.output), indent=2))


if __name__ == '__main__':
    main()
