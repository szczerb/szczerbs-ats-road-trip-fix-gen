import struct
import unittest

from ats_road_trip.ppd import PpdError, add_petrol_spawns, inspect_ppd


def descriptor(version=25, spawns=((3, 0),), trailer=b'opaque sections retained'):
    records = b''.join(struct.pack('<7fI', i * 2.0, 0, 0, 1, 0, 0, 0, kind)
                       + (struct.pack('<I', flags) if version >= 24 else b'')
                       for i, (kind, flags) in enumerate(spawns))
    end = 96 + len(records)
    h = [version, 0, 0, 0, 0, len(spawns), 0, 0, 0, 0, 0, 0]
    h += [96] * 5 + [end] * 7
    return struct.pack('<24I', *h) + records + trailer


class PpdTest(unittest.TestCase):
    def test_versioned_inspection(self):
        for version in (23, 24, 25):
            report = inspect_ppd(descriptor(version))
            self.assertEqual(report['spawns'][0]['type'], 3)
            self.assertEqual(report['spawns'][0]['flags'], None if version == 23 else 0)

    def test_preserves_existing_spawns_and_opaque_sections(self):
        source = descriptor(spawns=((3, 0), (13, 0), (3, 1)))
        patched, report = add_petrol_spawns(source)
        self.assertEqual(report['added_count'], 1)
        self.assertEqual(patched[96:204], source[96:204])
        self.assertEqual(patched[240:], source[204:])
        h = struct.unpack_from('<24I', patched)
        self.assertEqual(h[5], 4)
        self.assertEqual(h[17:], (240,) * 7)
        spawns = inspect_ppd(patched)['spawns']
        self.assertEqual(spawns[3]['position'], spawns[0]['position'])
        self.assertEqual((spawns[3]['type'], spawns[3]['flags']), (3, 1))

    def test_generation_is_idempotent(self):
        once, _ = add_petrol_spawns(descriptor())
        twice, report = add_petrol_spawns(once)
        self.assertEqual(once, twice)
        self.assertEqual(report['added_count'], 0)

    def test_rejects_old_versions_unknown_flags_and_no_fuel(self):
        for data in (descriptor(23), descriptor(24), descriptor(spawns=((3, 2),)),
                     descriptor(spawns=((13, 0),))):
            with self.assertRaises(PpdError):
                add_petrol_spawns(data)

    def test_rejects_bad_header_extent_and_nonfinite_transform(self):
        for offset, value in ((0, 26), (48, 20), (64, 9999), (20, 4), (96, 0x7f800000)):
            data = bytearray(descriptor())
            struct.pack_into('<I', data, offset, value)
            with self.assertRaises(PpdError):
                inspect_ppd(bytes(data))
        with self.assertRaises(PpdError):
            inspect_ppd(b'\0' * 95)


if __name__ == '__main__':
    unittest.main()
