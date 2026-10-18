"""Synthetic Ford definitions verify source pins and exact byte edits."""

import hashlib
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.tank_upgrades import plan_tank_upgrades, validate_tank_upgrade_config


VEHICLES = {
    "ford.mustang_67": ("rwd.sii", "rwd.ford.mustang_67.chassis", 61, "16 @@gal@@"),
    "ford.victoria_06": ("rwd.sii", "rwd.ford.victoria_06.chassis", 72, "19 @@gal@@"),
    "ford.f150_23": ("4doors_55_awd.sii", "4d55_awd.ford.f150_23.chassis", 98, "26 @@gal@@"),
    "ford.bronco_24": ("4doors_awd.sii", "4d_awd.ford.bronco_24.chassis", 79, "20 @@gal@@"),
}


def source(unit, liters, info, *, crlf=False, bom=False, siblings=False):
    text = ('SiiNunit\n{\n'
            f'accessory_chassis_data : {unit}\n{{\n'
            '    # tank_size: 999\n'
            '    name: "tank_size: 999, info[]: \\"fake\\""\n'
            f'    info[]: "{info}" // actual stock text\n'
            '    info[]: "@@chassis@@"\n'
            f'    tank_size: {liters} // actual capacity\n'
            '    label: "café"\n'
            '@include "sound.sui"\n'
            '}\n')
    if siblings:
        for index in range(4):
            text += (f'vehicle_animation_data : .susp_{index}\n{{\n'
                     f'    name: "animation {index}, tank_size: 999"\n'
                     f'    speed: {index + 1}\n'
                     '}\n')
    text += '}\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    return (b'\xef\xbb\xbf' if bom else b'') + text.encode('utf-8')


def fixture():
    files = {}
    entries = []
    for model, (name, unit, stock, info) in VEHICLES.items():
        path = f'def/vehicle/car/{model}/chassis/{name}'
        raw = source(unit, stock, info, crlf=model == 'ford.mustang_67', bom=model == 'ford.mustang_67')
        files[path] = raw
        files[f'def/vehicle/car/{model}/chassis/sound.sui'] = b'# included sound\n'
        entries.append({"model": model, "path": path, "unit": unit,
                        "sha256": hashlib.sha256(raw).hexdigest(), "stock_liters": stock,
                        "target_liters": stock + 20, "stock_info": info,
                        "target_info": f"{stock + 20} @@l@@", "rationale": "Synthetic range test",
                        "sources": ["https://example.com/source"]})
    return files, {"schema_version": 1, "profile_id": "synthetic", "game_version": "1.61.3.18",
                   "vehicles": entries}


def stack(root, files, name="source.zip"):
    archive = root / name
    with zipfile.ZipFile(archive, 'w') as output:
        for path, raw in files.items():
            output.writestr(path, raw)
    return Package(archive)


class TankUpgradeTest(unittest.TestCase):
    def test_exact_byte_edits_preserve_comments_strings_bom_crlf_and_includes(self):
        files, policy = fixture()
        with TemporaryDirectory() as tmp:
            mounted = ResourceStack([stack(Path(tmp), files)])
            report, resources = plan_tank_upgrades(mounted, policy, game_version="1.61.3.18")
        self.assertTrue(report['coverage']['complete'], report['coverage']['blockers'])
        self.assertEqual(report['changed_count'], 4)
        self.assertEqual(len(resources), 4)
        for entry in policy['vehicles']:
            row = next(v for v in report['vehicles'] if v['model'] == entry['model'])
            self.assertEqual(row['output_sha256'], hashlib.sha256(resources[entry['path']]).hexdigest())
            self.assertEqual(row['stock_info'], entry['stock_info'])
            self.assertEqual(row['target_info'], entry['target_info'])
            self.assertEqual(row['rationale'], entry['rationale'])
            self.assertEqual(row['sources'], entry['sources'])
            original = files[entry['path']]
            expected = original.replace(f'info[]: "{entry["stock_info"]}"'.encode(),
                                        f'info[]: "{entry["target_info"]}"'.encode(), 1)
            expected = expected.replace(f'tank_size: {entry["stock_liters"]} // actual'.encode(),
                                        f'tank_size: {entry["target_liters"]} // actual'.encode(), 1)
            self.assertEqual(resources[entry['path']], expected)

    def test_noop_still_validates_all_four(self):
        files, policy = fixture()
        for entry in policy['vehicles']:
            entry['target_liters'] = entry['stock_liters']
            entry['target_info'] = entry['stock_info']
        with TemporaryDirectory() as tmp:
            report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                   game_version="1.61.3.18")
        self.assertTrue(report['coverage']['complete'], report['coverage']['blockers'])
        self.assertEqual(report['changed_count'], 0)
        self.assertEqual(resources, {})
        self.assertEqual({v['status'] for v in report['vehicles']}, {'unchanged'})

    def test_four_sibling_animation_units_are_preserved_for_each_vehicle(self):
        files, policy = fixture()
        for entry in policy['vehicles']:
            raw = source(entry['unit'], entry['stock_liters'], entry['stock_info'], siblings=True,
                         crlf=entry['model'] == 'ford.mustang_67',
                         bom=entry['model'] == 'ford.mustang_67')
            files[entry['path']] = raw
            entry['sha256'] = hashlib.sha256(raw).hexdigest()
        with TemporaryDirectory() as tmp:
            report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                   game_version='1.61.3.18')
        self.assertTrue(report['coverage']['complete'], report['coverage']['blockers'])
        self.assertEqual(len(resources), 4)
        for entry in policy['vehicles']:
            original = files[entry['path']]
            edited = resources[entry['path']]
            sibling_marker = b'vehicle_animation_data : .susp_0'
            self.assertEqual(edited[edited.index(sibling_marker):],
                             original[original.index(sibling_marker):])

    def test_sibling_drift_and_second_chassis_unit_block_output(self):
        files, policy = fixture()
        last = policy['vehicles'][-1]['path']
        files[last] += b'\nvehicle_animation_data : .susp_0 { speed: 1 }\n'
        with TemporaryDirectory() as tmp:
            report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                   game_version='1.61.3.18')
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(resources, {})
        self.assertIn('hash differs', report['coverage']['blockers'][0])

        policy['vehicles'][-1]['sha256'] = hashlib.sha256(files[last]).hexdigest()
        files[last] += b'\naccessory_chassis_data : extra.ford.bronco_24.chassis { tank_size: 1 }\n'
        policy['vehicles'][-1]['sha256'] = hashlib.sha256(files[last]).hexdigest()
        with TemporaryDirectory() as tmp:
            report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                   game_version='1.61.3.18')
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(resources, {})
        self.assertIn('chassis unit', report['coverage']['blockers'][0])

    def test_effective_winner_is_hashed_and_partial_edits_are_discarded(self):
        files, policy = fixture()
        last = policy['vehicles'][-1]['path']
        altered = {last: files[last].replace(b'tank_size: 79', b'tank_size: 80')}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            mounted = ResourceStack([stack(root, files), stack(root, altered, 'override.zip')])
            report, resources = plan_tank_upgrades(mounted, policy, game_version="1.61.3.18")
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('hash differs', report['coverage']['blockers'][0])
        self.assertEqual(resources, {})
        self.assertEqual(report['changed_count'], 0)
        self.assertEqual(len(report['vehicles']), 3)  # Late failure did not publish earlier edits.

    def test_corrupt_policy_and_version_fail_closed(self):
        files, policy = fixture()
        bad = dict(policy)
        bad['vehicles'] = [dict(item) for item in policy['vehicles']]
        bad['vehicles'][0]['target_liters'] = 999
        with self.assertRaisesRegex(ValueError, '1.6x'):
            validate_tank_upgrade_config(bad)
        with TemporaryDirectory() as tmp:
            mounted = ResourceStack([stack(Path(tmp), files)])
            report, resources = plan_tank_upgrades(mounted, bad, game_version="1.61.3.18")
            self.assertFalse(report['coverage']['complete'])
            self.assertEqual(resources, {})
            report, resources = plan_tank_upgrades(mounted, policy, game_version="1.62.0.0")
            self.assertFalse(report['coverage']['complete'])
            self.assertEqual(resources, {})
        bad['vehicles'][0]['target_liters'] = 81
        bad['vehicles'][0]['unit'] = 'other'
        with self.assertRaisesRegex(ValueError, 'canonical'):
            validate_tank_upgrade_config(bad)

    def test_invalid_types_missing_models_and_unescaped_info_are_rejected(self):
        _, policy = fixture()
        for invalid in (True, 61.0, math.inf, -1):
            bad = {**policy, 'vehicles': [dict(v) for v in policy['vehicles']]}
            bad['vehicles'][0]['target_liters'] = invalid
            with self.assertRaisesRegex(ValueError, 'capacities'):
                validate_tank_upgrade_config(bad)
        bad = {**policy, 'vehicles': [dict(v) for v in policy['vehicles'][:-1]]}
        with self.assertRaisesRegex(ValueError, 'exactly four'):
            validate_tank_upgrade_config(bad)
        bad['vehicles'].append(dict(bad['vehicles'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate_tank_upgrade_config(bad)
        for invalid in ('wrong\\escape', 'a"quoted"value', 'line\nbreak'):
            bad = {**policy, 'vehicles': [dict(v) for v in policy['vehicles']]}
            bad['vehicles'][0]['target_info'] = invalid
            with self.assertRaisesRegex(ValueError, 'single plain SII string'):
                validate_tank_upgrade_config(bad)
        bad = {**policy, 'vehicles': [dict(v) for v in policy['vehicles']]}
        bad['vehicles'][0]['target_liters'] = bad['vehicles'][0]['stock_liters']
        with self.assertRaisesRegex(ValueError, 'unchanged capacity'):
            validate_tank_upgrade_config(bad)

    def test_missing_or_duplicate_live_tank_and_wrong_unit_are_blocked(self):
        cases = (
            (b'tank_size: 61 // actual', b'#tank_size: 61 // actual'),
            (b'tank_size: 61 // actual', b'tank_size: 61\r\n    tank_size: 61 // actual'),
            (b'accessory_chassis_data : rwd.ford.mustang_67.chassis',
             b'accessory_chassis_data : wrong.ford.mustang_67.chassis'),
        )
        for original, replacement in cases:
            files, policy = fixture()
            first = policy['vehicles'][0]['path']
            files[first] = files[first].replace(original, replacement)
            policy['vehicles'][0]['sha256'] = hashlib.sha256(files[first]).hexdigest()
            with TemporaryDirectory() as tmp:
                report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                       game_version='1.61.3.18')
            self.assertFalse(report['coverage']['complete'], replacement)
            self.assertEqual(resources, {})

    def test_missing_include_blocks_even_when_hash_matches(self):
        files, policy = fixture()
        first = policy['vehicles'][0]['path']
        files[first] = files[first].replace(b'@include "sound.sui"', b'@include "missing.sui"')
        policy['vehicles'][0]['sha256'] = hashlib.sha256(files[first]).hexdigest()
        with TemporaryDirectory() as tmp:
            report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                   game_version='1.61.3.18')
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(resources, {})

    def test_semantic_drift_is_blocked_even_with_updated_hash(self):
        files, policy = fixture()
        first = policy['vehicles'][0]['path']
        files[first] = files[first].replace(b'tank_size: 61 // actual', b'tank_size: 61\r\n    tank_size: 61 // actual')
        policy['vehicles'][0]['sha256'] = hashlib.sha256(files[first]).hexdigest()
        with TemporaryDirectory() as tmp:
            report, resources = plan_tank_upgrades(ResourceStack([stack(Path(tmp), files)]), policy,
                                                   game_version="1.61.3.18")
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(resources, {})


if __name__ == '__main__':
    unittest.main()
