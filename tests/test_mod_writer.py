from pathlib import Path
import json
import tempfile
import unittest
import zipfile

from ats_road_trip.mod_writer import write_mod


class ModWriterTest(unittest.TestCase):
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
                                       ({'x': b'x'}, '1.60'), ({'manifest.sii': b'x'}, '1.61')):
                with self.assertRaises(ValueError):
                    write_mod(target, resources, {}, game_version=version)
                self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
