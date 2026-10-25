"""Download pinned licensed geographic data and a permitted font into an ignored run.

Usage: python -m ats_road_trip.background.fetch --output local_outputs/work/TIMESTAMP/source-data
No tools, font binaries or geographic archives are added to the source repository.
"""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
import tarfile
import urllib.request

from .geography import digest, source_files

ROOT = Path(__file__).resolve().parents[3]


def font_from_deb(data, member):
    if not data.startswith(b'!<arch>\n'):
        raise ValueError('Expected Debian ar archive')
    offset = 8
    while offset < len(data):
        header = data[offset:offset+60]
        if len(header)!=60 or header[58:60]!=b'`\n':
            raise ValueError('Invalid ar header')
        size = int(header[48:58])
        name = header[:16].decode().strip().rstrip('/')
        payload = data[offset+60:offset+60+size]
        if len(payload)!=size:
            raise ValueError('Truncated ar member')
        if name.startswith('data.tar'):
            with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
                entry = archive.getmember(member)
                if not entry.isfile() or entry.size>4*1024*1024:
                    raise ValueError('Unexpected font member')
                return archive.extractfile(entry).read()
        offset += 60+size+(size%2)
    raise ValueError('Debian archive has no data member')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--config-dir',type=Path,default=ROOT/'docs/examples/north-america-background')
    args=parser.parse_args(argv)
    output=args.output.resolve()
    allowed=(ROOT/'local_outputs/work').resolve()
    if not output.is_relative_to(allowed):
        raise ValueError('Downloads belong beneath this checkout local_outputs/work')
    source_files(json.loads((args.config_dir/'sources.json').read_text()),output,download=True)
    spec=json.loads((args.config_dir/'font.json').read_text())
    font=output/'DejaVuSans.ttf'
    if font.exists():
        if digest(font.read_bytes())!=spec['font_sha256']:
            raise ValueError('Cached font drift')
    else:
        with urllib.request.urlopen(spec['url'],timeout=120) as response:
            data=response.read(4*1024*1024+1)
        if digest(data)!=spec['archive_sha256']:
            raise ValueError('Font archive drift')
        data=font_from_deb(data,spec['member'])
        if digest(data)!=spec['font_sha256']:
            raise ValueError('Font member drift')
        with font.open('xb') as out:
            out.write(data)
    print(str(output))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
