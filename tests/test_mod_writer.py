from pathlib import Path
import json
import struct
import tempfile
import unittest
import zipfile

from ats_road_trip.mod_writer import write_mod
from ats_road_trip.sii import parse_units


class ModWriterTest(unittest.TestCase):
    def test_standalone_other_category_and_rejection(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'courier.scs'
            report = write_mod(output, {'def/example.sii': b'x'}, {}, game_version='1.61',
                               display_name='Courier experiment', category='other')
            with zipfile.ZipFile(output) as archive:
                manifest = parse_units(archive.read('manifest.sii').decode())[0]
                self.assertEqual(manifest.values('category'), ('other',))
                self.assertEqual(report['package_metadata']['category'], 'other')
            with self.assertRaises(ValueError):
                write_mod(Path(temporary) / 'bad.scs', {'x': b'x'}, {},
                          game_version='1.61', category='invalid')

    def test_selected_topics_have_accurate_branding(self):
        with tempfile.TemporaryDirectory() as temporary:
            for topics, title in ((('fuel',), 'Gas Stations Fix'),
                                  (('rest',), 'Rest Stops Fix'),
                                  (('fuel', 'rest'), 'Map Compatibility Fix')):
                output = Path(temporary) / ('-'.join(topics) + '.scs')
                report = write_mod(output, {'test': b'payload'}, {}, game_version='1.61',
                                   map_name='Test Map', revision=3, fix_topics=topics)
                with zipfile.ZipFile(output) as archive:
                    manifest = parse_units(archive.read('manifest.sii').decode())[0]
                    self.assertEqual(manifest.one('display_name'),
                                     f"szczerb's Road Trip {title} for Test Map")
                    self.assertEqual(report['package_metadata']['fix_topics'], sorted(topics))

    def test_fuel_branding_escaping_version_and_icon_manifest_agree(self):
        # This synthetic frame exercises metadata validation, not JPEG decoding.
        icon = (b'\xff\xd8\xff\xc0' + struct.pack('>HBHHB', 17, 8, 162, 276, 3)
                + b'\x01\x11\0\x02\x11\0\x03\x11\0\xff\xd9')
        with tempfile.TemporaryDirectory() as temporary:
            a, b = Path(temporary)/'a.scs', Path(temporary)/'b.scs'
            for target in (a, b):
                report = write_mod(target, {'map/usa/sample.base': b'unchanged-payload'}, {},
                                   game_version='1.61.3.18', map_name='Map "A" \\ test',
                                   revision=2, icon=icon)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as archive:
                unit = parse_units(archive.read('manifest.sii').decode())[0]
                self.assertEqual(unit.one('display_name'), "szczerb's Road Trip Gas Stations Fix for Map \"A\" \\ test")
                self.assertEqual(unit.one('package_version'), '1.61-r2-experimental')
                self.assertEqual(unit.one('author'), 'szczerb')
                self.assertEqual(unit.one('icon'), 'mod_icon.jpg')
                self.assertEqual(archive.read('mod_icon.jpg'), icon)
                self.assertEqual(archive.read('map/usa/sample.base'), b'unchanged-payload')
                self.assertEqual(len(report['generated_resources']), 1)
                self.assertEqual(report['package_metadata']['icon']['size'], len(icon))
                self.assertEqual(report, json.loads(archive.read('road_trip_fix_report.json')))

    def test_rejects_invalid_metadata_before_creating_output(self):
        icon = (b'\xff\xd8\xff\xc0' + struct.pack('>HBHHB', 17, 8, 162, 276, 3)
                + b'\x01\x11\0\x02\x11\0\x03\x11\0\xff\xd9')
        bad_size = bytearray(icon)
        struct.pack_into('>H', bad_size, 9, 512)
        cases = [{'revision': x} for x in (-1, True, 0.5, 'r0')]
        cases += [{'map_name': x} for x in ('', ' ', ' Map', 'Map\nInjected: true')]
        cases += [{'map_name': 'Map', 'display_name': 'ambiguous'}]
        cases += [{'map_name': 'Map', 'fix_topics': x}
                  for x in ((), ('courier',), ('rest', 'rest'), ['rest'], ('rest', 1))]
        cases += [{'fix_topics': ('rest',)}]
        cases += [{'icon': x} for x in (b'not-jpeg', icon[:-1], bytes(bad_size), b'\xff\xd8\xff\xc0\0\x02\xff\xd9')]
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)/'a.scs'
            for options in cases:
                with self.subTest(options=options), self.assertRaises(ValueError):
                    write_mod(target, {'x': b'x'}, {}, game_version='1.61', **options)
                self.assertFalse(target.exists())

    def test_deterministic_self_documenting_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary)/'a.scs', Path(temporary)/'b.scs'
            for target in (first, second):
                write_mod(target, {'def/data_context.example.sii': b'SiiNunit { }\n'},
                          {'analysis': 'synthetic'}, game_version='1.61.3.18')
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(len(archive.namelist()), 4)
                self.assertIsNone(archive.testzip())
                self.assertTrue(all(i.compress_type == zipfile.ZIP_STORED for i in archive.infolist()))
                report = json.loads(archive.read('road_trip_fix_report.json'))
                self.assertFalse(report['in_game_verified'])
                self.assertTrue(report['experimental'])
                self.assertEqual(report['generated_resources'][0]['size'], 13)
            with self.assertRaises(FileExistsError):
                write_mod(first, {'def/x.sii': b'x'}, {}, game_version='1.61')

    def test_rejects_unsafe_empty_and_unsupported_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)/'a.scs'
            for resources, version in (({}, '1.61'), ({'../bad': b'x'}, '1.61'),
                                       ({'x': b'x'}, '1.60'), ({'manifest.sii': b'x'}, '1.61'),
                                       ({'mod_icon.jpg': b'x'}, '1.61')):
                with self.assertRaises(ValueError):
                    write_mod(target, resources, {}, game_version=version)
                self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
