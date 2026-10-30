"""Source-pinned full-package replacement for one explicitly reviewed station.

Run with ``python -m ats_road_trip.station_parking.reviewed_area_workflow``.
This does not feed the automatic map-wide heuristic or install any files.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import zipfile
from zoneinfo import ZoneInfo

from ..local_fuel import token
from ..map_sector import parse_sector
from ..mod_writer import write_mod
from ..sii import parse_units
from .mesh import read_station_mesh, sample_surface_height
from .reviewed_areas import replace_reviewed_car_parking_areas

ROOT = Path(__file__).resolve().parents[3]


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def build_reviewed_replacement(source, config_path, *, experimental=False, run_id=None):
    """Copy the complete pinned package; change one private PPD and metadata."""
    if not experimental:
        raise ValueError('Reviewed area generation requires --experimental')
    source, config_path = Path(source), Path(config_path)
    config_bytes = config_path.read_bytes()
    c = json.loads(config_bytes)
    if c['schema_version'] != 1:
        raise ValueError('Unsupported reviewed-area configuration schema')
    if _sha(source.read_bytes()) != c['source_package_sha256']:
        raise ValueError('Reviewed source package SHA-256 drift')
    with zipfile.ZipFile(source) as z:
        if z.testzip() or len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('Source ZIP CRC or duplicate-member failure')
        original = {n: z.read(n) for n in z.namelist()}
    old_report = json.loads(original['road_trip_fix_report.json'])
    old_metadata = old_report['package_metadata']
    if (old_metadata['map_name'] != c['map_name']
            or old_report['game_version_declared'] != c['game_version']
            or old_metadata['revision'] >= c['revision']):
        raise ValueError('Source map/game identity or replacement revision differs')
    expected = {row['path']: row['sha256'] for row in old_report['generated_resources']}
    metadata_names = {'manifest.sii', 'mod_description.txt', 'road_trip_fix_report.json', 'mod_icon.jpg'}
    resources = {n: b for n, b in original.items() if n not in metadata_names}
    if set(resources) != set(expected) or any(_sha(b) != expected[n] for n, b in resources.items()):
        raise ValueError('Source resource inventory/hash drift')
    for name, digest in c['resource_sha256'].items():
        if _sha(resources[name]) != digest:
            raise ValueError('Reviewed resource SHA-256 drift: ' + name)
    sector = parse_sector(resources[c['sector']])
    target = next((p for p in sector.prefabs if p.uid == int(c['prefab_uid'], 16)), None)
    if target is None or target.details['model'] != token(c['private_alias']):
        raise ValueError('Reviewed station placement no longer uses the pinned private alias')
    definition = 'def/world/prefab.' + c['private_alias'] + '.sii'
    units = parse_units(resources[definition].decode())
    matching = [u for u in units if u.name == 'prefab.' + c['private_alias']]
    if len(matching) != 1 or matching[0].one('prefab_desc').lstrip('/') != c['descriptor']:
        raise ValueError('Reviewed private definition does not resolve the target descriptor')
    placements = [(path, hex(p.uid)) for path, b in resources.items()
                  if re.fullmatch(r'map/usa/sec[+-]\d{4}[+-]\d{4}\.(?:base|aux)', path)
                  for p in parse_sector(b).prefabs if p.details['model'] == token(c['private_alias'])]
    if placements != [(c['sector'], c['prefab_uid'])]:
        raise ValueError('Private descriptor is not exclusive to the reviewed station')
    mesh_path = ROOT / c['mesh_project_relative']
    mesh_text = mesh_path.read_text(encoding='utf-8-sig')
    if _sha(mesh_text.encode()) != c['mesh_sha256']:
        raise ValueError('Reviewed mesh SHA-256 drift')
    mesh = read_station_mesh(mesh_text)
    surface_checks = []
    for area in c['areas']:
        points = area['vertices'];xs=[p[0] for p in points];zs=[p[2] for p in points]
        heights = [sample_surface_height(mesh, (min(xs)+(max(xs)-min(xs))*i/5,
                                               min(zs)+(max(zs)-min(zs))*j/5),
                                         set(c['ground_materials']))
                   for i in range(6) for j in range(6)]
        if max(abs(h-points[0][1]) for h in heights) > .1:
            raise ValueError('Reviewed area differs from its sampled asphalt surface')
        surface_checks.append({'id':area['id'],'samples':len(heights),'height_min':min(heights),'height_max':max(heights)})
    modified, correction = replace_reviewed_car_parking_areas(
        resources[c['baseline_descriptor']], resources[c['descriptor']],
        previous_vertices=c['previous_vertices'], areas=c['areas'])
    resources[c['descriptor']] = modified
    stamp = run_id or datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y-%m-%d_%H-%M-%S')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', stamp):
        raise ValueError('Run ID must be a Warsaw YYYY-MM-DD_HH-MM-SS timestamp')
    work = ROOT/'local_outputs/work'/stamp/'reviewed-station-areas'
    output = ROOT/'local_outputs/generated'/stamp
    if work.exists() or output.exists():
        raise ValueError('Refuse to overwrite an existing output run')
    work.mkdir(parents=True)
    filename = ('dawson-2-areas-alaska-expansion-' + c['source_map_version'] +
                '-ats-1.61-r' + str(c['revision']) + '-experimental.scs')
    description = (c['variant_label'] + ' | Dawson City | EXPERIMENTAL\n'
        'Full Alaska Expansion replacement for REALISTIC r10.\n'
        'Two broad car-rest areas: beside the storefront and along the grass/roadside edge.\n'
        'Replaces the tiny Dawson car bay; partial-contact activation is enabled for both areas.\n'
        'Native truck/bus parking, all car fueling, prices and every other station remain unchanged.\n'
        'Disable the Alaska Expansion r10 fix; enable THIS MOD in the same position directly above Alaska_Expansion_v1.2.3.scs.\n'
        'Keep the other seven r10 packages, original sources and separate tank/courier mods.\n'
        'Keep the current N2 navigation fix highest, including above OtherMaps; N2 r2/r3 gameplay is unchanged.\n'
        'Disable the old A/B/C/C2/E/F/G experiments and never combine this with the old Alaska r10 fix.\n'
        'Only this Dawson placement is revised. Two groups/marker positions are statically verified; in-game activation and icons await user verification.\n')
    source_order = original['mod_description.txt'].decode().split('Required order, LOWEST to HIGHEST', 1)
    if len(source_order) != 2:
        raise ValueError('Pinned source has no complete load-order description')
    order = source_order[1].replace('REALISTIC r10 replacement for Alaska Expansion (THIS MOD)',
                                    c['variant_label'] + ' replacement for Alaska Expansion (THIS MOD)')
    order = order.replace('N2 NAV PARKING FUEL r2', 'N2 navigation fix (current r2/r3)')
    description += '\nRequired order, LOWEST to HIGHEST' + order
    if description.count('(THIS MOD)') != 1:
        raise ValueError('Replacement description must identify exactly one current package')
    report = {'analysis':'reviewed_station_area_replacement','source_package':{'name':source.name,'sha256':c['source_package_sha256']},
              'configuration':c,'configuration_sha256':_sha(config_bytes),
              'correction':correction,'surface_checks':surface_checks,
              'only_changed_gameplay_resource':c['descriptor'],
              'preserved_resources':{n:_sha(b) for n,b in resources.items() if n!=c['descriptor']},
              'original_resource_count':len(resources),'automatic_heuristic_unchanged':True,
              'station_placement_and_all_service_node_identities_unchanged':True,
              'runtime_verification':'Pending user check of this station only; no game/profile/install operation performed'}
    final = write_mod(output/filename, resources, report, game_version=c['game_version'],
                      map_name=c['map_name'], revision=c['revision'], fix_topics=('fuel','rest'),
                      variant_label=c['variant_label'], description=description,
                      icon=original.get('mod_icon.jpg'))
    with zipfile.ZipFile(output/filename) as z:
        if z.testzip():raise ValueError('Output CRC failure')
        changed = [n for n,b in original.items() if z.read(n)!=b]
        if set(z.namelist())!=set(original) or set(changed)!={c['descriptor'],'manifest.sii','mod_description.txt','road_trip_fix_report.json'}:
            raise ValueError('Output changes more than target PPD and versioned metadata')
    receipt={'status':'passed','archive':str(output/filename),'sha256':_sha((output/filename).read_bytes()),
             'changed_members':sorted(changed),'station':c['prefab_uid'],'areas':correction['areas'],
             'source_package_sha256':c['source_package_sha256'],'same_member_inventory':True}
    (work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (work/'report.json').write_text(json.dumps(final,indent=2)+'\n')
    (output/'reviewed-areas.json').write_bytes(config_bytes)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--experimental',action='store_true')
    args=parser.parse_args()
    print(json.dumps(build_reviewed_replacement(args.source,args.config,experimental=args.experimental),indent=2))


if __name__=='__main__':main()
