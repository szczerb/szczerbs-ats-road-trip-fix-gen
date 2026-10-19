from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from ats_road_trip import navigation_icons as nav
from ats_road_trip.sii import parse_units
from ats_road_trip.package import Package, ResourceStack


def _source_files(map_data=None):
    return {
        nav.MAP_DATA: map_data if map_data is not None else (
            b'// preserve this source comment\r\n'
            b'map_items_flags[0]: 0x00685FFF  // tier zero\r\n'
            b'map_items_flags[1]:\t0x00685FFF\r\n'
            b'map_items_flags[2]: 0x00685FFF\r\n'
            b'map_items_flags[3]: 0x00685FFF\r\n'
            b'map_items_flags[4]: 0x01685FFF // world tier 4\r\n'
            b'map_items_flags[5]: 0x01685FFF\r\n'
            b'map_items_flags[6]: 0x01685FFF\r\n'
            b'map_items_flags[7]: 0x01685FFF\r\n'
            b'other_setting: keep-me\r\n'
        ),
        'def/map_data/colour_data.sui': b'// authored colour include\ncolour: unchanged\n',
        'def/map_data/full_detail_config.sui': b'// authored detail include\nconfig: unchanged\n',
        'def/map_data/zoom_uplift_config.sui': b'// authored zoom include\nconfig: unchanged\n',
    }


def _hashes(files):
    return {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}


def _write_source(root, files):
    for name, data in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


class NavigationIconsTests(unittest.TestCase):
    def test_token_edit_preserves_every_other_byte_and_only_changes_local_tiers(self):
        source = _source_files()[nav.MAP_DATA]
        result = nav.enable_local_car_parking(source)
        expected = source.replace(
            b'0x00685FFF', b'0x02685FFF', 4
        )
        self.assertEqual(result, expected)
        self.assertIn(b'// preserve this source comment\r\n', result)
        self.assertIn(b'// tier zero\r\n', result)
        self.assertEqual(result.count(b'\r\n'), source.count(b'\r\n'))
        self.assertNotIn(b'\n', result.replace(b'\r\n', b''))
        for index in range(8):
            before = int(_source_files()[nav.MAP_DATA].split(
                f'map_items_flags[{index}]:'.encode(), 1)[1].splitlines()[0].split(b'//')[0].strip(), 16)
            after = int(result.split(f'map_items_flags[{index}]:'.encode(), 1)[1].splitlines()[0].split(b'//')[0].strip(), 16)
            expected_value = before | nav.CAR_PARKING_BIT if index < 4 else before
            self.assertEqual(after, expected_value)
        self.assertTrue(all((int(result.split(f'map_items_flags[{i}]:'.encode(), 1)[1].splitlines()[0].split(b'//')[0].strip(), 16)
                             & (1 << 24)) == (int(source.split(f'map_items_flags[{i}]:'.encode(), 1)[1].splitlines()[0].split(b'//')[0].strip(), 16)
                                                & (1 << 24)) for i in range(8)))

    def test_token_edit_rejects_missing_duplicate_malformed_and_noop_masks(self):
        source = _source_files()[nav.MAP_DATA]
        cases = (
            source.replace(b'map_items_flags[7]: 0x01685FFF\r\n', b''),
            source + b'map_items_flags[0]: 0x00685FFF\r\n',
            source.replace(b'map_items_flags[2]: 0x00685FFF', b'map_items_flags[2]: not_hex'),
            source.replace(b'map_items_flags[1]:\t0x00685FFF', b'map_items_flags[1]: 0x02685FFF'),
        )
        for malformed in cases:
            with self.subTest(source=malformed[-64:]):
                with self.assertRaises(ValueError):
                    nav.enable_local_car_parking(malformed)

    def test_n2_changes_only_candidate_fuel_bit_in_addition_to_n1(self):
        source = _source_files()[nav.MAP_DATA]
        n1 = nav.enable_local_car_parking(source)
        n2 = nav._enable_local_categories(
            source, mask=nav.CAR_PARKING_BIT | nav.FUEL_CANDIDATE_BIT,
            label='parking/fuel candidate')
        expected = source.replace(b'0x00685FFF', b'0x03685FFF', 4)
        self.assertEqual(n2, expected)
        self.assertNotEqual(n1, n2)
        for index in range(8):
            old = int(source.split(f'map_items_flags[{index}]:'.encode(), 1)[1]
                      .splitlines()[0].split(b'//')[0].strip(), 16)
            one = int(n1.split(f'map_items_flags[{index}]:'.encode(), 1)[1]
                      .splitlines()[0].split(b'//')[0].strip(), 16)
            two = int(n2.split(f'map_items_flags[{index}]:'.encode(), 1)[1]
                      .splitlines()[0].split(b'//')[0].strip(), 16)
            if index < 4:
                self.assertEqual(two ^ one, nav.FUEL_CANDIDATE_BIT)
            else:
                self.assertEqual(two, one)
        with self.assertRaisesRegex(ValueError, 'already set'):
            nav._enable_local_categories(n2, mask=nav.CAR_PARKING_BIT | nav.FUEL_CANDIDATE_BIT,
                                         label='parking/fuel candidate')

    def test_planner_pins_declared_version_and_all_source_includes(self):
        files = _source_files()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_source(root, files)
            with patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                with nav.Package(root) as package:
                    with self.assertRaisesRegex(ValueError, 'reviewed only'):
                        nav.plan_navigation_icons(package, game_version='1.62')
                    report, resources = nav.plan_navigation_icons(package, game_version=nav.GAME_VERSION)
            self.assertEqual(set(resources), {nav.MAP_DATA})
            self.assertEqual(resources[nav.MAP_DATA], nav.enable_local_car_parking(files[nav.MAP_DATA]))
            self.assertEqual({entry['path'] for entry in report['source_members']}, set(files))
            self.assertTrue(report['world_tiers_4_to_7_unchanged'])
            self.assertTrue(report['fuel_category_bit_24_unchanged'])
            self.assertFalse(report['in_game_verified'])

    def test_n2_planner_reports_candidate_bit_and_exact_local_delta(self):
        files = _source_files()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_source(root, files)
            with patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                with nav.Package(root) as package:
                    report, resources = nav.plan_navigation_icons(
                        package, game_version=nav.GAME_VERSION, variant='parking-fuel')
                    with self.assertRaisesRegex(ValueError, 'Unknown navigation variant'):
                        nav.plan_navigation_icons(package, game_version=nav.GAME_VERSION, variant='both')
            self.assertEqual(resources[nav.MAP_DATA],
                             files[nav.MAP_DATA].replace(b'0x00685FFF', b'0x03685FFF', 4))
            self.assertEqual(report['experiment'], 'N2 NAV PARKING + FUEL')
            self.assertEqual(report['candidate_fuel_category_bit_24'], True)
            self.assertEqual(report['fuel_category_bit_24_unchanged'], False)
            self.assertEqual([row['after'] for row in report['changed_tiers']],
                             ['0x03685FFF'] * 4)
            self.assertTrue(report['world_tiers_4_to_7_unchanged'])
            self.assertTrue(report['all_other_source_bytes_preserved'])
            self.assertFalse(report['in_game_verified'])

    def test_planner_refuses_drifted_or_missing_includes_and_post_read_drift(self):
        files = _source_files()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_source(root, files)
            changed_include = files['def/map_data/colour_data.sui'] + b'updated\n'
            with patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                (root / 'def/map_data/colour_data.sui').write_bytes(changed_include)
                with nav.Package(root) as package:
                    with self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                        nav.plan_navigation_icons(package, game_version=nav.GAME_VERSION)
                (root / 'def/map_data/colour_data.sui').write_bytes(files['def/map_data/colour_data.sui'])
                (root / 'def/map_data/zoom_uplift_config.sui').unlink()
                with nav.Package(root) as package:
                    with self.assertRaisesRegex(ValueError, 'member is missing'):
                        nav.plan_navigation_icons(package, game_version=nav.GAME_VERSION)

            _write_source(root, files)

            class DriftingPackage:
                path = root
                def __init__(self):
                    self.files = {name: name for name in files}
                    self.read_counts = {}

                def read(self, name, *, max_bytes):
                    self.read_counts[name] = self.read_counts.get(name, 0) + 1
                    data = (root / name).read_bytes()
                    if name == nav.MAP_DATA and self.read_counts[name] > 1:
                        return data + b'// changed after planning\n'
                    return data

            with patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                with self.assertRaisesRegex(ValueError, 'changed during planning'):
                    nav.plan_navigation_icons(DriftingPackage(), game_version=nav.GAME_VERSION)

    def test_generation_writes_auditable_single_resource_archive_without_touching_input(self):
        files = _source_files()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'background-map'
            _write_source(source, files)
            original = {name: (source / name).read_bytes() for name in files}
            with patch.object(nav, 'REPO_ROOT', root), patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                with self.assertRaisesRegex(ValueError, 'acknowledge-experimental'):
                    nav.run_navigation_icons(source, game_version=nav.GAME_VERSION, run_id='2026-10-19_20-00-00')
                result = nav.run_navigation_icons(source, game_version=nav.GAME_VERSION,
                                                  acknowledge_experimental=True,
                                                  run_id='2026-10-19_20-00-01')
                output = Path(result['output'])
                self.assertTrue(output.name.startswith('n1-nav-parking-'))
                self.assertIn('r1-experimental', output.name)
                with zipfile.ZipFile(output) as archive:
                    names = set(archive.namelist())
                    self.assertEqual(names, {nav.MAP_DATA, 'manifest.sii', 'mod_description.txt',
                                             'road_trip_fix_report.json'})
                    payload = archive.read(nav.MAP_DATA)
                    self.assertEqual(payload, nav.enable_local_car_parking(original[nav.MAP_DATA]))
                    manifest = parse_units(archive.read('manifest.sii').decode())[0]
                    self.assertTrue(manifest.one('display_name').startswith('N1 NAV PARKING'))
                    self.assertIn('1.61-r1-experimental', manifest.one('package_version'))
                    description = archive.read('mod_description.txt').decode()
                    self.assertTrue(description.startswith('N1 NAV PARKING:'))
                    self.assertIn('N1 ABOVE North America Background Map', description)
                    report = json.loads(archive.read('road_trip_fix_report.json'))
                    self.assertFalse(report['in_game_verified'])
                    self.assertEqual({entry['path'] for entry in report['generated_resources']}, {nav.MAP_DATA})
                self.assertEqual({name: (source / name).read_bytes() for name in files}, original)
                with self.assertRaises(FileExistsError):
                    nav.run_navigation_icons(source, game_version=nav.GAME_VERSION,
                                             acknowledge_experimental=True,
                                             run_id='2026-10-19_20-00-01')

    def test_n2_generation_has_distinct_metadata_and_rejects_invalid_variant_before_writes(self):
        files = _source_files()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'background-map'
            _write_source(source, files)
            with patch.object(nav, 'REPO_ROOT', root), patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                with self.assertRaisesRegex(ValueError, 'Unknown navigation variant'):
                    nav.run_navigation_icons(source, game_version=nav.GAME_VERSION,
                                             acknowledge_experimental=True, run_id='2026-10-19_20-00-02',
                                             variant='parking-and-fuel')
                self.assertFalse((root / 'local_outputs').exists())
                result = nav.run_navigation_icons(
                    source, game_version=nav.GAME_VERSION, acknowledge_experimental=True,
                    run_id='2026-10-19_20-00-03', variant='parking-fuel')
            output = Path(result['output'])
            self.assertEqual(output.name, nav.N2_FILENAME)
            self.assertTrue(output.name.startswith('n2-nav-parking-fuel-'))
            self.assertEqual(result['generated_mod_count'], 1)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.read(nav.MAP_DATA),
                                 files[nav.MAP_DATA].replace(b'0x00685FFF', b'0x03685FFF', 4))
                manifest = parse_units(archive.read('manifest.sii').decode())[0]
                self.assertTrue(manifest.one('display_name').startswith('N2 NAV PARKING + FUEL'))
                self.assertIn('1.61-r2-experimental', manifest.one('package_version'))
                description = archive.read('mod_description.txt').decode()
                self.assertTrue(description.startswith('N2 NAV PARKING + FUEL:'))
                self.assertIn('N2 replaces N1', description)
                self.assertIn('Put N2 ABOVE North America Background Map and every other map-data provider.', description)
                self.assertIn('fuel category bit', description)
                self.assertIn('remain unverified', description)
                report = json.loads(archive.read('road_trip_fix_report.json'))
                self.assertTrue(report['candidate_fuel_category_bit_24'])
                self.assertFalse(report['fuel_category_bit_24_unchanged'])
                self.assertFalse(report['in_game_verified'])

    def test_variant_archives_are_whole_file_alternatives_with_explicit_priority(self):
        files = _source_files()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'background-map'
            _write_source(source, files)
            with patch.object(nav, 'REPO_ROOT', root), patch.object(nav, 'SOURCE_HASHES', _hashes(files)):
                n1 = nav.run_navigation_icons(source, game_version=nav.GAME_VERSION,
                                             acknowledge_experimental=True, run_id='2026-10-19_20-01-00')
                n2 = nav.run_navigation_icons(source, game_version=nav.GAME_VERSION,
                                             acknowledge_experimental=True, run_id='2026-10-19_20-01-01',
                                             variant='parking-fuel')
            with Package(source) as background, Package(n1['output']) as one, Package(n2['output']) as two:
                high_n1 = ResourceStack([background, two, one])
                high_n2 = ResourceStack([background, one, two])
                self.assertEqual(high_n1.read(nav.MAP_DATA), one.read(nav.MAP_DATA))
                self.assertEqual(high_n2.read(nav.MAP_DATA), two.read(nav.MAP_DATA))
                self.assertNotEqual(high_n1.read(nav.MAP_DATA), high_n2.read(nav.MAP_DATA))
                self.assertEqual(high_n2.read('def/map_data/colour_data.sui'),
                                 files['def/map_data/colour_data.sui'])
            self.assertIn('N2 replaces N1', nav.N2_DESCRIPTION)
            self.assertIn('enable only one at a time', nav.N2_DESCRIPTION)

    def test_module_cli_exposes_the_narrow_experimental_command(self):
        env = dict(os.environ)
        src = str(Path(nav.__file__).resolve().parents[1])
        env['PYTHONPATH'] = src + os.pathsep + env.get('PYTHONPATH', '')
        result = subprocess.run([sys.executable, '-m', 'ats_road_trip.navigation_icons', '--help'],
                                check=False, capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--source-package', result.stdout)
        self.assertIn('--game-version', result.stdout)
        self.assertIn('--acknowledge-experimental', result.stdout)
        self.assertIn('--variant', result.stdout)
        self.assertIn('parking-fuel', result.stdout)


if __name__ == '__main__':
    unittest.main()
