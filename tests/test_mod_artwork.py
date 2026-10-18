"""Selection rules for reviewed, map-labelled package artwork."""

from pathlib import Path
import tempfile
import unittest

from ats_road_trip.mod_artwork import courier_icon, map_icon


class MapArtworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.icons = self.root / 'assets' / 'mod-icons'
        self.icons.mkdir(parents=True)

    def put(self, relative):
        path = self.icons / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'fixture image')
        return path

    def test_combined_artwork_is_selected_by_exact_map_label(self):
        alaska = self.put('map-compatibility/alaska.jpg')
        western_canada = self.put('map-compatibility/western-canada.jpg')

        self.assertEqual(map_icon(self.root, 'Alaska', ('fuel', 'rest')), alaska)
        self.assertEqual(map_icon(self.root, 'Western Canada', ('rest', 'fuel')),
                         western_canada)

    def test_fuel_only_artwork_uses_its_map_specific_fuel_icon(self):
        alaska = self.put('alaska-c.jpg')
        self.assertEqual(map_icon(self.root, 'Alaska', ('fuel',)), alaska)

    def test_rest_only_does_not_reuse_fuel_artwork(self):
        fuel = self.put('alaska-c.jpg')
        self.assertIsNone(map_icon(self.root, 'Alaska', ('rest',)))
        self.assertTrue(fuel.is_file())

    def test_unknown_map_never_gets_another_maps_label(self):
        self.put('map-compatibility/ats-expansion.jpg')
        self.put('ats-expansion-c.jpg')
        self.assertIsNone(map_icon(self.root, 'Unlisted Map', ('fuel', 'rest')))
        self.assertIsNone(map_icon(self.root, 'Unlisted Map', ('fuel',)))


class CourierArtworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.icons = self.root / 'assets' / 'mod-icons'
        self.icons.mkdir(parents=True)

    def test_default_courier_artwork_is_optional_and_does_not_fall_back_to_map_art(self):
        self.assertIsNone(courier_icon(self.root))

        courier = self.icons / 'job-types-compat-mustang.jpg'
        courier.write_bytes(b'courier fixture')
        (self.icons / 'alaska-c.jpg').write_bytes(b'map fixture')

        self.assertEqual(courier_icon(self.root), courier)


if __name__ == '__main__':
    unittest.main()
