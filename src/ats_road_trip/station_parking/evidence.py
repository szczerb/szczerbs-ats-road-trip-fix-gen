"""Prepare portable, private station evidence from explicit ConverterPIX outputs.

This module copies only reviewed PIM/PIT files. It does not convert assets,
install mods, rewrite pins, or redistribute game content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .catalog import METADATA_PATH, load_reviewed_catalog, read_evidence, reviewed_metadata


def prepare_evidence(converted_dirs, output, *, metadata_path=None):
    """Verify all files before creating a new flat directory; never overwrite."""
    roots = [Path(path).expanduser().resolve() for path in converted_dirs]
    if not roots or any(not root.is_dir() for root in roots):
        raise ValueError('Supply existing --converted-dir directories')
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise FileExistsError('Evidence output already exists; use a new run directory')
    metadata = reviewed_metadata(metadata_path)
    selected = []
    for config in metadata['families']:
        family = config['family']
        for suffix, label in (('.pim', 'mesh'), ('.pit', 'mesh_state')):
            name = family + suffix
            candidates = sorted({p for root in roots for p in root.rglob(name) if p.is_file()})
            if not candidates:
                raise ValueError(f'Missing converted station evidence: {name}')
            # Duplicate names are allowed only when every candidate has the
            # reviewed identity, preventing silent selection across conversions.
            for candidate in candidates:
                read_evidence(candidate, config['fingerprints'][label], family, label)
            source = candidates[0]
            data = source.read_bytes()
            selected.append((name, data, {'name': name, 'source': str(source),
                'sha256': hashlib.sha256(data).hexdigest(),
                'normalized_text_sha256': config['fingerprints'][label]}))
    output.mkdir(parents=True, exist_ok=False)
    for name, data, _ in selected:
        with (output/name).open('xb') as stream:
            stream.write(data)
    # Re-read what was copied rather than trusting source path identities.
    load_reviewed_catalog(output, metadata_path=metadata_path)
    receipt = {'schema_version': 1, 'game_version': metadata['game_version'],
               'metadata_sha256': hashlib.sha256(Path(metadata_path or METADATA_PATH).read_bytes()).hexdigest(),
               'converter': metadata['converter'], 'files': [row for _, _, row in selected],
               'source_resource_validation': 'Binary model/material pins checked against the original mounted stack during planning',
               'redistribution_authorized': False}
    (output/'preparation.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--converted-dir', action='append', required=True,
                        help='Existing conversion output tree; repeat for separate model runs')
    parser.add_argument('--output', required=True, help='New private flat station evidence directory')
    args = parser.parse_args(argv)
    try:
        receipt = prepare_evidence(args.converted_dir, args.output)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'{exc}\n')
    print(json.dumps({'output': str(Path(args.output).resolve()), 'files': len(receipt['files'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
