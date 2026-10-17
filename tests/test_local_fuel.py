from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from ats_road_trip.cli import main
from ats_road_trip.local_fuel import patch_local_pump, plan_local_fuel, token
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.sii import parse_units


def fixtures():
    def item(kind, uid):
        return struct.pack('<IQ10fIB', kind, uid, *([0.] * 5 + [10.] * 5), 0x80000000, 4)
    prefab = (item(4, 100) + struct.pack('<QQI', token('02003'), token('default'), 0)
              + struct.pack('<IQQIQ', 2, 201, 202, 1, 300))
    service = item(7, 300) + struct.pack('<QQI', 203, 100, 0)
    sector = struct.pack('<IQI', 907, token('euro2'), 3) + prefab + service + b'other sector bytes'
    header = [25, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0] + [96] * 5 + [132] * 7
    ppd = struct.pack('<24I', *header) + struct.pack('<7fII', 1, 2, 3, 1, 0, 0, 0, 3, 0) + b'opaque'
    recipe = {'schema_version': 1, 'game_version': '1.61.3.18',
              'sector': 'map/usa/sec-0016-0014.base',
              'sector_sha256': hashlib.sha256(sector).hexdigest(),
              'descriptor_sha256': hashlib.sha256(ppd).hexdigest(),
              'prefab_uid': '0x64', 'service_uid': '0x12c', 'location': {'city': 'test'}}
    return sector, ppd, recipe


class LocalFuelTests(unittest.TestCase):
    def test_minimal_mutation_and_reference_preservation(self):
        sector, ppd, _ = fixtures()
        changed, descriptor, report = patch_local_pump(sector, ppd, prefab_uid=100,
                                                       service_uid=300, alias='rtfsample')
        self.assertEqual(len(changed), len(sector))
        self.assertEqual(len(descriptor), len(ppd))
        start, service = report['prefab_item_offset'], report['service_item_offset']
        self.assertEqual(struct.unpack_from('<Q', changed, start + 57)[0], token('rtfsample'))
        self.assertEqual(struct.unpack_from('<I', changed, service + 52)[0], 0x80004000)
        restored = bytearray(changed)
        restored[start + 57:start + 65] = sector[start + 57:start + 65]
        restored[service + 52:service + 56] = sector[service + 52:service + 56]
        self.assertEqual(bytes(restored), sector)
        self.assertEqual(report['ppd_changed_byte_offsets'], [128])
        self.assertEqual(descriptor[:128] + b'\0' + descriptor[129:], ppd)
        self.assertEqual(report['ppd_before']['spawns'][0]['position'],
                         report['ppd_after']['spawns'][0]['position'])

    def test_wrong_map_layout_identity_parent_and_flags_are_rejected(self):
        source, ppd, _ = fixtures()
        _, _, report = patch_local_pump(source, ppd, prefab_uid=100, service_uid=300, alias='rtfsample')
        start, service = report['prefab_item_offset'], report['service_item_offset']
        for offset, fmt, value in ((0, '<I', 906), (4, '<Q', token('other')), (12, '<I', 4),
                                   (start + 57, '<Q', token('other')), (start + 65, '<Q', token('variant')),
                                   (service + 65, '<Q', 999), (service + 52, '<I', 0x80004000),
                                   (service + 73, '<I', 1)):
            bad = bytearray(source)
            struct.pack_into(fmt, bad, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                patch_local_pump(bytes(bad), ppd, prefab_uid=100, service_uid=300, alias='rtfsample')
        with self.assertRaises(ValueError):
            patch_local_pump(source + source[16:], ppd, prefab_uid=100, service_uid=300, alias='rtfsample')
        for prefab_uid, service_uid in ((-1, 300), (2 ** 64, 300), (100, 0), (100, 2 ** 64)):
            with self.assertRaises(ValueError):
                patch_local_pump(source, ppd, prefab_uid=prefab_uid, service_uid=service_uid, alias='rtfsample')

    def test_unsupported_locator_configuration_is_rejected(self):
        sector, source, _ = fixtures()
        for offset, value in ((0, 24), (4, 1), (20, 2), (36, 1), (124, 13), (128, 1)):
            bad = bytearray(source)
            struct.pack_into('<I', bad, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                patch_local_pump(sector, bytes(bad), prefab_uid=100, service_uid=300, alias='rtfsample')

    def test_cli_roundtrip_fingerprints_and_scope(self):
        sector, ppd, recipe = fixtures()
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as manager:
            root = Path(temporary)
            baseline, source_map = root/'game', root/'map'
            def put(base, name, data):
                target = base/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            put(baseline, 'prefab/gas/us_gas_station_trigger_only.ppd', ppd)
            put(baseline, 'prefab/gas/us_gas_station_trigger_only.pmd', b'opaque model')
            put(baseline, 'def/world/prefab.sii', b'''SiiNunit {
prefab_model : prefab.02003 {
name: "us gas / trigger only"
model_desc: "/prefab/gas/us_gas_station_trigger_only.pmd"
prefab_desc: "/prefab/gas/us_gas_station_trigger_only.ppd"
category: ""
}
}''')
            put(source_map, 'base/' + recipe['sector'], sector)
            recipe_path, output = root/'recipe.json', root/'sample.scs'
            recipe_path.write_text(json.dumps(recipe))
            arguments = ['generate-local-fuel', '--baseline', str(baseline), '--map', str(source_map),
                         '--recipe', str(recipe_path), '--output', str(output), '--game-version', '1.61.3.18',
                         '--map-name', 'Synthetic Map']
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    main(arguments)
                self.assertFalse(output.exists())
                self.assertEqual(main([*arguments, '--experimental']), 0)
            with zipfile.ZipFile(output) as archive:
                report = json.loads(archive.read('road_trip_fix_report.json'))
                self.assertEqual(len(report['generated_resources']), 3)
                self.assertFalse(report['in_game_verified'])
                self.assertIsNone(archive.testzip())
                manifest = parse_units(archive.read('manifest.sii').decode())[0]
                self.assertEqual(manifest.one('display_name'), "szczerb's Road Trip Gas Stations Fix for Synthetic Map")
                self.assertEqual(manifest.one('package_version'), '1.61-r0-experimental')
                self.assertEqual(manifest.one('author'), 'szczerb')
                definition_path = next(n for n in archive.namelist() if n.startswith('def/world/'))
                alias = parse_units(archive.read(definition_path).decode())[0]
                self.assertEqual(alias.name, report['alias'])
                self.assertIn(alias.one('prefab_desc').lstrip('/'), archive.namelist())
                self.assertEqual(len(archive.read(recipe['sector'])), len(sector))
            packages = [manager.enter_context(Package(p)) for p in (baseline, source_map)]
            stack = ResourceStack(packages)
            for bad in ({**recipe, 'sector_sha256': '0' * 64}, {**recipe, 'descriptor_sha256': '0' * 64},
                        {**recipe, 'schema_version': 2}, {**recipe, 'game_version': '1.61'},
                        {**recipe, 'unexpected': True}, {**recipe, 'prefab_uid': 100}, None):
                with self.assertRaises(ValueError):
                    plan_local_fuel(stack, bad, map_package=str(source_map), game_version='1.61.3.18')
            with self.assertRaises(ValueError):
                plan_local_fuel(stack, recipe, map_package=str(baseline), game_version='1.61.3.18')
            report, _ = plan_local_fuel(stack, recipe, map_package=str(source_map), game_version='1.61.3.18')
            alias_token = report['alias'].split('.')[1]
            put(source_map, f'base/def/world/prefab.{alias_token}.sii', b'SiiNunit {}')
            collision = manager.enter_context(Package(source_map))
            with self.assertRaises(ValueError):
                plan_local_fuel(ResourceStack([packages[0], collision]), recipe,
                                map_package=str(source_map), game_version='1.61.3.18')
            self.assertEqual((source_map/'base'/recipe['sector']).read_bytes(), sector)


if __name__ == '__main__':
    unittest.main()
