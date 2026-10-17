from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from ats_road_trip.cli import main
from ats_road_trip.local_fuel import token
from ats_road_trip.overlap_fuel import patch_overlapping_pump
from ats_road_trip.ppd import inspect_ppd
from ats_road_trip.sii import parse_units


SECTOR_PATH = 'map/usa/sec-0015-0012.base'
PPD_PATH = 'prefab/gas/us_gas_station_trigger_only.ppd'
COMPANION_PATHS = [
    'map/usa/sec-0015-0012.data', 'map/usa/sec-0015-0012.aux',
    'map/usa/sec-0015-0012.desc', 'map/usa/sec-0015-0012.layer',
]


def _map_item(kind, uid):
    return struct.pack('<IQ10fIB', kind, uid, *([0.0] * 5 + [10.0] * 5), 0x80000000, 4)


def _node(uid, backward=0, forward=0, flags=0):
    return struct.pack('<Q3i4fQQI', uid, 256, 512, 768, 1.0, 0.0, 0.0, 0.0,
                       backward, forward, flags)


def _ppd():
    # One v25, two-node, flags-zero GAS locator plus an opaque trailing section.
    size = 96 + 36 + len(b'opaque-section')
    header = [25, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0] + [96] * 5 + [132] + [size] * 6
    return (struct.pack('<24I', *header)
            + struct.pack('<7fII', 1, 2, 3, 1, 0, 0, 0, 3, 0)
            + b'opaque-section')


def _fixtures():
    prefab = (_map_item(4, 100) + struct.pack('<QQ', token('02003'), 0)
              + struct.pack('<I', 0) + struct.pack('<IQQ', 2, 201, 202)
              + struct.pack('<IQ', 1, 300))
    service = _map_item(7, 300) + struct.pack('<QQI', 203, 100, 0)
    company_like_item = _map_item(6, 700) + b'opaque-variable-length-payload'.ljust(108, b'!')
    # Unknown bytes between supported items exercise preservation around opaque data.
    prefix = struct.pack('<IQII', 907, token('euro2'), 3, 3)
    opaque_gap = b'opaque-item-gap'
    node_table_offset = len(prefix) + len(prefab) + len(opaque_gap) + len(service) + len(company_like_item)
    sector = (prefix + prefab + opaque_gap + service + company_like_item + struct.pack('<I', 3)
              + _node(201) + _node(202) + _node(203, forward=300) + b'\0' * 4)
    ppd = _ppd()
    layout = {'node_count_offset': node_table_offset, 'node_count': 3,
              'item_count': 3, 'service_node_uid': '0xcb'}
    return sector, ppd, layout


def _companions():
    return {
        COMPANION_PATHS[0]: b'data companion',
        COMPANION_PATHS[1]: b'aux companion',
        COMPANION_PATHS[2]: bytes(range(40)),
        COMPANION_PATHS[3]: b'\x8b\x03\0\0\x61\x04\x75\0' + b'\0' * 8 + b'\xff' * 8,
    }


class OverlapFuelTests(unittest.TestCase):
    def test_pair_retains_truck_records_and_adds_reciprocal_car_records(self):
        sector, ppd, layout = _fixtures()
        changed, changed_ppd, report = patch_overlapping_pump(
            sector, ppd, prefab_uid=100, service_uid=300, alias='rtpsample', layout=layout,
            car_service_uid=1000, car_node_uid=1001)
        self.assertEqual(len(changed), len(sector) + 141)
        self.assertTrue(report['original_truck_service_preserved'])
        self.assertTrue(report['original_truck_node_preserved'])
        self.assertTrue(report['opaque_original_bytes_reconstructed'])
        self.assertEqual(report['slave_count_after'], 2)

        prefab = changed.find(struct.pack('<IQ', 4, 100))
        service = changed.find(struct.pack('<IQ', 7, 300))
        car_service = changed.find(struct.pack('<IQ', 7, 1000))
        source_service = sector.find(struct.pack('<IQ', 7, 300))
        self.assertEqual(changed[service:service + 77], sector[source_service:source_service + 77])
        self.assertEqual(struct.unpack_from('<I', changed, service + 52)[0], 0x80000000)
        self.assertEqual(struct.unpack_from('<I', changed, car_service + 52)[0], 0x80004000)
        self.assertEqual(struct.unpack_from('<Q', changed, service + 57)[0], 203)
        self.assertEqual(struct.unpack_from('<Q', changed, car_service + 57)[0], 1001)
        self.assertEqual(struct.unpack_from('<Q', changed, car_service + 65)[0], 100)
        # The parent still names both services; the old service bytes stay intact.
        self.assertEqual(struct.unpack_from('<I', changed, prefab + 97)[0], 2)
        self.assertEqual(struct.unpack_from('<QQ', changed, prefab + 101), (300, 1000))
        self.assertEqual(struct.unpack_from('<I', changed, report['node_count_offset_after'])[0], 4)
        original_node = sector[layout['node_count_offset'] + 4 + 2 * 56:
                               layout['node_count_offset'] + 4 + 3 * 56]
        new_node = changed[report['car_node_offset']:report['car_node_offset'] + 56]
        self.assertEqual(new_node[8:36], original_node[8:36])
        self.assertEqual(struct.unpack_from('<QQ', new_node, 36), (0, 1000))

        original_spawn = inspect_ppd(ppd)['spawns'][0]
        after_spawns = inspect_ppd(changed_ppd)['spawns']
        self.assertEqual([spawn['flags'] for spawn in after_spawns], [0, 1])
        self.assertEqual(changed_ppd[original_spawn['offset']:original_spawn['offset'] + 28],
                         ppd[original_spawn['offset']:original_spawn['offset'] + 28])
        self.assertEqual(changed_ppd[after_spawns[0]['offset']:after_spawns[0]['offset'] + 28],
                         changed_ppd[after_spawns[1]['offset']:after_spawns[1]['offset'] + 28])
        self.assertTrue(report['exact_same_world_node_transform'])
        self.assertTrue(report['exact_same_ppd_transform'])

    def test_rejects_unpinned_table_extent_trailer_or_owner(self):
        source, ppd, layout = _fixtures()
        cases = []
        cases.append((source, {**layout, 'node_count_offset': layout['node_count_offset'] + 1}))
        cases.append((source, {**layout, 'item_count': 2 ** 32 - 1}))
        bad = bytearray(source); bad[-1] = 1; cases.append((bytes(bad), layout))
        bad = bytearray(source); struct.pack_into('<Q', bad, layout['node_count_offset'] + 4 + 2 * 56 + 44, 999); cases.append((bytes(bad), layout))
        bad = bytearray(source); struct.pack_into('<I', bad, 16, 4); cases.append((bytes(bad), layout))
        for sector, metadata in cases:
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                patch_overlapping_pump(sector, ppd, prefab_uid=100, service_uid=300,
                                       alias='rtpsample', layout=metadata,
                                       car_service_uid=1000, car_node_uid=1001)

    def test_rejects_duplicate_or_colliding_generated_uids(self):
        source, ppd, layout = _fixtures()
        for service_uid, node_uid in ((300, 1001), (1000, 1000), (1000, 202)):
            with self.subTest(service_uid=service_uid, node_uid=node_uid), self.assertRaises(ValueError):
                patch_overlapping_pump(source, ppd, prefab_uid=100, service_uid=300,
                                       alias='rtpsample', layout=layout,
                                       car_service_uid=service_uid, car_node_uid=node_uid)
        duplicate = bytearray(source)
        node_start = layout['node_count_offset'] + 4
        struct.pack_into('<Q', duplicate, node_start + 56, 201)
        with self.assertRaises(ValueError):
            patch_overlapping_pump(bytes(duplicate), ppd, prefab_uid=100, service_uid=300,
                                   alias='rtpsample', layout=layout,
                                   car_service_uid=1000, car_node_uid=1001)

    def _put(self, package, path, data):
        target = self.root / package / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def _setup_packages(self):
        sector, ppd, layout = _fixtures()
        companions = _companions()
        self._put('baseline', PPD_PATH, ppd)
        self._put('baseline', 'prefab/gas/us_gas_station_trigger_only.pmd', b'opaque model')
        self._put('baseline', 'def/world/prefab.sii', b'''SiiNunit {
prefab_model : prefab.02003 {
name: "us gas / trigger only"
model_desc: "/prefab/gas/us_gas_station_trigger_only.pmd"
prefab_desc: "/prefab/gas/us_gas_station_trigger_only.ppd"
category: ""
}
}''')
        self._put('map', 'base/' + SECTOR_PATH, sector)
        for path, data in companions.items():
            self._put('map', 'base/' + path, data)
        recipe = {
            'schema_version': 2, 'game_version': '1.61.3.18', 'sector': SECTOR_PATH,
            'sector_sha256': hashlib.sha256(sector).hexdigest(),
            'descriptor_sha256': hashlib.sha256(ppd).hexdigest(),
            'prefab_uid': '0x64', 'service_uid': '0x12c', 'location': {'city': 'test'},
            'overlap': {'layout': layout, 'companion_sha256': {
                path: hashlib.sha256(data).hexdigest() for path, data in companions.items()}},
        }
        recipe_path = self.root / 'recipe.json'
        recipe_path.write_text(json.dumps(recipe))
        return sector, ppd, companions, recipe, recipe_path

    def _run_cli(self, arguments):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            try:
                status = main(arguments)
            except SystemExit as exc:
                status = exc.code
        return status, output.getvalue(), error.getvalue()

    def test_cli_generates_three_resources_and_pins_companions(self):
        sector, ppd, companions, recipe, recipe_path = self._setup_packages()
        output = self.root / 'overlap.scs'
        args = ['generate-overlap-fuel', '--baseline', str(self.root / 'baseline'),
                '--map', str(self.root / 'map'), '--recipe', str(recipe_path),
                '--output', str(output), '--game-version', '1.61.3.18']
        status, _, _ = self._run_cli(args)
        self.assertEqual(status, 2)
        self.assertFalse(output.exists())
        status, stdout, stderr = self._run_cli([*args, '--experimental'])
        self.assertEqual(status, 0, stderr)
        with zipfile.ZipFile(output) as archive:
            self.assertIsNone(archive.testzip())
            report = json.loads(archive.read('road_trip_fix_report.json'))
            self.assertFalse(report['in_game_verified'])
            self.assertEqual(len(report['generated_resources']), 3)
            self.assertFalse(any(name.endswith(('.data', '.aux', '.desc', '.layer')) for name in archive.namelist()))
            manifest = parse_units(archive.read('manifest.sii').decode())[0]
            self.assertEqual(manifest.one('display_name'), 'Road Trip Helena - truck + car at one pump (sample 2)')
            self.assertEqual(len(archive.read(SECTOR_PATH)), len(sector) + 141)
            self.assertEqual(archive.read(SECTOR_PATH).count(b'opaque-item-gap'), 1)
            self.assertEqual(archive.read(SECTOR_PATH).count(b'opaque-variable-length-payload'), 1)
            ppd_path = next(name for name in archive.namelist() if name.endswith('.ppd'))
            self.assertEqual([spawn['flags'] for spawn in inspect_ppd(archive.read(ppd_path))['spawns']], [0, 1])
            description = archive.read('mod_description.txt').decode()
            self.assertIn('sample 2', description.lower())
        self.assertEqual((self.root / 'map' / 'base' / SECTOR_PATH).read_bytes(), sector)
        for path, data in companions.items():
            self.assertEqual((self.root / 'map' / 'base' / path).read_bytes(), data)

    def test_cli_rejects_companion_drift_and_converted_sample_input(self):
        sector, ppd, companions, recipe, recipe_path = self._setup_packages()
        args = ['generate-overlap-fuel', '--baseline', str(self.root / 'baseline'),
                '--map', str(self.root / 'map'), '--recipe', str(recipe_path),
                '--output', str(self.root / 'bad.scs'), '--game-version', '1.61.3.18', '--experimental']
        # A sample-1 conversion has the same length but differs in the pinned source hash.
        converted = bytearray(sector)
        service = converted.find(struct.pack('<IQ', 7, 300))
        struct.pack_into('<I', converted, service + 52, 0x80004000)
        self._put('map', 'base/' + SECTOR_PATH, bytes(converted))
        status, _, _ = self._run_cli(args)
        self.assertEqual(status, 2)
        self.assertFalse((self.root / 'bad.scs').exists())
        self._put('map', 'base/' + SECTOR_PATH, sector)
        companion = next(iter(companions))
        self._put('map', 'base/' + companion, companions[companion] + b'changed')
        status, _, _ = self._run_cli(args)
        self.assertEqual(status, 2)
        self.assertFalse((self.root / 'bad.scs').exists())


if __name__ == '__main__':
    unittest.main()
