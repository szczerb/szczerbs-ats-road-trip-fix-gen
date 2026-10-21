import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.resource_overlay import OverlayResourceStack

class OverlayTests(unittest.TestCase):
    def test_staged_payload_retains_original_owner_and_resolves_new_resources(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'old.sii').write_bytes(b'original')
            with Package(root) as package:
                raw=ResourceStack([package]); staged=OverlayResourceStack(raw,{'old.sii':b'composed','new.sii':b'private'})
                self.assertIs(staged.resources['old.sii'][0],package)
                self.assertEqual(staged.read('old.sii'),b'composed')
                self.assertEqual(staged.resources['new.sii'][0].read('new.sii'),b'private')
                self.assertEqual(raw.read('old.sii'),b'original')
                self.assertEqual(staged.matching(r'.*\.sii'),['new.sii','old.sii'])
                staged.prefetch(r'.*\.sii')
                nested=OverlayResourceStack(staged,{'new.sii':b'later'})
                self.assertEqual(nested.read('new.sii'),b'later')
                self.assertEqual(nested.read('old.sii'),b'composed')
                with self.assertRaises(ValueError):staged.read('new.sii',max_bytes=1)
    def test_noncanonical_and_nonbyte_overrides_rejected(self):
        with TemporaryDirectory() as tmp, Package(tmp) as package:
            for values in ({'../escape':b'x'},{'new.sii':'text'}):
                with self.assertRaises(ValueError):OverlayResourceStack(ResourceStack([package]),values)
