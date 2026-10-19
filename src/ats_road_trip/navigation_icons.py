"""Source-pinned N1 parking visibility experiment, independent of map geometry.

Run with ``python -m ats_road_trip.navigation_icons --help``. This narrow recipe
is for North America Background Map 5.3, not a generic map-data replacement.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from .mod_writer import sha256, write_mod
from .package import Package

REPO_ROOT = Path(__file__).resolve().parents[2]
GAME_VERSION = '1.61.3.18'
MAP_DATA = 'def/map_data.sii'
CAR_PARKING_BIT = 1 << 25
SOURCE_NAME = 'North America Background Map 5.3 (Workshop 3348711188)'
SOURCE_HASHES = {
    MAP_DATA: '4d8d9bce1c8a73c387b10bc191fbde5249b7f4ea1ecacb912e5ffe1b08c4b189',
    'def/map_data/colour_data.sui': '5e10afde98bba2b8ac8a27a78675460db4adb1616b6b1b38d1b25f15f4a20d68',
    'def/map_data/full_detail_config.sui': 'a40907d58d685f485c43962078c649f53d5f41c60c5589ea4a91d09765eb9662',
    'def/map_data/zoom_uplift_config.sui': 'e96c5384c23509e349242fcc5e777a36c724fad3aa5753b29ffb0325e3d3bb73',
}
TITLE = "N1 NAV PARKING - szczerb's Road Trip for North America Background Map 5.3 (experimental)"
FILENAME = 'n1-nav-parking-north-america-background-5.3-ats-1.61-r1-experimental.scs'
DESCRIPTION = '''N1 NAV PARKING: experimental car-parking icons for local navigation views.

Compare with N0 CONTROL: this mod disabled. N0 is a test state, not another file.
This is a candidate for testing, not a confirmed phone/dashboard navigation fix.
It may reveal car-parking icons throughout the map; it adds no parking places.

Requires North America Background Map 5.3 (Workshop 3348711188), ATS 1.61 and
Road Trip Ford DLC. Prepared against ATS 1.61.3.18; other inputs are unreviewed.
Put N1 ABOVE North America Background Map and every other map-data provider.
Keep the background map enabled. Enable only one navigation experiment at once.

For Dawson testing, keep exactly one existing A LINES or B GEOMETRY PoC enabled
at its usual position above Alaska Expansion, replacing Alaska r9 only.
Keep WCE r9 and other source fixes in their existing positions. Do not separately
add the old Alaska r2 baseline. N1 works ALONGSIDE that selected PoC; it replaces
neither the PoC nor an Alaska/WCE fix. Keep other profile settings unchanged.

Compare the same vehicle, location and zoom with N1 disabled and then enabled:
full-screen map, phone OR built-in navigation as fitted, then the existing rest
prompt separately. Check a known native car-parking icon too if one is available.
No new location search is required. Existing rest areas and actions are unchanged.

ATS 1.61-r1-experimental. In-game visibility and rest regression remain untested.
'''


def enable_local_car_parking(data: bytes) -> bytes:
    """Edit four literal tokens only; the caller must pin the complete source.

    This is deliberately not an SII serializer. Full-source fingerprints in the
    planner establish the reviewed unit/includes; these checks guard the edit.
    """
    pattern = re.compile(rb'(?m)^[ \t]*map_items_flags\[([0-7])\]:[ \t]*(0x[0-9A-Fa-f]+)(?=[ \t\r\n]|$)')
    matches = list(pattern.finditer(data))
    if len(matches) != 8 or sorted(int(m[1]) for m in matches) != list(range(8)):
        raise ValueError('Expected exactly one literal map-items mask for each tier 0..7')
    replacements = []
    for match in matches:
        index, value = int(match[1]), int(match[2], 16)
        if index < 4:
            if value & CAR_PARKING_BIT:
                raise ValueError('Local car-parking bit is already set; no reviewed change')
            replacements.append((match.start(2), match.end(2), f'0x{value | CAR_PARKING_BIT:08X}'.encode()))
    for start, end, replacement in reversed(replacements):
        data = data[:start] + replacement + data[end:]
    return data


def plan_navigation_icons(package: Package, *, game_version: str) -> tuple[dict, dict[str, bytes]]:
    """Reject source/version drift before emitting the single-resource overlay."""
    if game_version != GAME_VERSION:
        raise ValueError(f'N1 is reviewed only against declared ATS {GAME_VERSION}')
    sources = {}
    for name, expected in SOURCE_HASHES.items():
        if name not in package.files:
            raise ValueError(f'Required N1 source member is missing: {name}')
        data = package.read(name, max_bytes=64 * 1024)
        if sha256(data) != expected:
            raise ValueError(f'N1 source fingerprint mismatch: {name}; review updated inputs first')
        sources[name] = data
    before = sources[MAP_DATA]
    after = enable_local_car_parking(before)
    report = {
        'experiment': 'N1 NAV PARKING', 'control': 'N0: N1 disabled, same existing A or B',
        'source': SOURCE_NAME, 'source_package': str(package.path),
        'source_members': [{'path': name, 'sha256': sha256(data), 'size': len(data)}
                           for name, data in sorted(sources.items())],
        'reviewed_game_version': GAME_VERSION,
        'version_check': 'Caller-declared build; this command does not inspect or run the game.',
        'operation': 'OR car-parking category bit 25 into map_items_flags[0..3] only',
        'changed_tiers': [{'index': i, 'before': '0x00685FFF', 'after': '0x02685FFF'} for i in range(4)],
        'world_tiers_4_to_7_unchanged': True,
        'all_other_source_bytes_preserved': True,
        'geometry_or_trigger_resources_changed': False,
        'fuel_category_bit_24_unchanged': True,
        'scope': 'Global local-map category visibility; no new parking or sector resources.',
        'required_provider': SOURCE_NAME,
        'priority': 'N1 above all map-data providers; keep source background and one A/B enabled.',
        'unresolved': ['Exact phone/dashboard tier consumers',
                       'Reported B world-map visibility despite omitted category in source masks',
                       'Native positive navigation control, A navigation visibility and zoom dependence'],
        'in_game_verified': False,
    }
    # Workshop updates may occur during generation; verify every pinned member
    # again rather than reading a different source after computing the patch.
    for name, data in sources.items():
        if package.read(name, max_bytes=64 * 1024) != data:
            raise ValueError(f'N1 source changed during planning: {name}')
    return report, {MAP_DATA: after}


def run_navigation_icons(source_package: str | Path, *, game_version: str,
                         acknowledge_experimental: bool = False, run_id: str | None = None) -> dict:
    if acknowledge_experimental is not True:
        raise ValueError('N1 generation requires --acknowledge-experimental')
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('Run ID must use YYYY-MM-DD_HH-MM-SS')
    work = REPO_ROOT / 'local_outputs/work' / stamp / 'navigation-icons'
    output = REPO_ROOT / 'local_outputs/generated' / stamp / FILENAME
    audit = work / 'audit.json'
    if audit.exists() or output.exists():
        raise FileExistsError('N1 run already exists; choose another run ID')
    # The source is a reviewed unpacked virtual root, e.g. Workshop .../universal.
    # Limiting to directories keeps this small recipe independent of extractors.
    source = Path(source_package).expanduser().resolve()
    if not source.is_dir():
        raise ValueError('Use the unpacked background package virtual root (universal directory)')
    with Package(source) as package:
        plan, resources = plan_navigation_icons(package, game_version=game_version)
    final = write_mod(output, resources, plan, game_version=game_version,
                      display_name=TITLE, description=DESCRIPTION, revision=1)
    result = {'output': str(output), 'sha256': sha256(output.read_bytes()),
              'report_path': str(audit), 'generated_mod_count': 1,
              'in_game_verified': False, 'package': final}
    work.mkdir(parents=True, exist_ok=True)
    with audit.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-package', required=True, help='Background Map 5.3 virtual root (universal)')
    parser.add_argument('--game-version', required=True, help='Declared installed build; reviewed: ' + GAME_VERSION)
    parser.add_argument('--acknowledge-experimental', action='store_true')
    parser.add_argument('--run-id', help='Optional new YYYY-MM-DD_HH-MM-SS Warsaw run ID')
    args = parser.parse_args(argv)
    try:
        result = run_navigation_icons(args.source_package, game_version=args.game_version,
                                      acknowledge_experimental=args.acknowledge_experimental,
                                      run_id=args.run_id)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
