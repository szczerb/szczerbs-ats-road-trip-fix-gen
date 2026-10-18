"""Player-facing metadata should accurately describe the generated package."""

import unittest

from ats_road_trip.mod_descriptions import courier_description, map_description


class MapDescriptionTests(unittest.TestCase):
    def test_each_known_fix_marks_only_its_own_source_pair(self):
        pairs = (
            ('Alaska', 'Alaska Expansion'),
            ('Western Canada ProMods Connections', 'Western Canada ProMods Connections'),
            ('Reforma OtherMaps Patch', 'Reforma OtherMaps Patch'),
            ('ProMods Canada', 'ProMods Canada Map Package'),
            ('Western Canada', 'Western Canada Expansion'),
            ('ATS Expansion', 'ATS Expansion'),
            ('Reforma', 'Reforma'),
        )
        for fix, source in pairs:
            with self.subTest(fix=fix):
                lines = map_description(fix).splitlines()
                marker = f'{fix} fix (THIS MOD)'
                self.assertEqual(lines.count(marker), 1)
                self.assertEqual(lines.count('(THIS MOD)'), 0)
                self.assertEqual(sum('(THIS MOD)' in line for line in lines), 1)
                self.assertEqual(lines[lines.index(marker) + 1], source)
                self.assertLess(lines.index('Job Types Compat Mustang'), lines.index(marker))

    def test_stack_keeps_sources_and_promods_components_in_documented_order(self):
        text = map_description('Western Canada')
        ordered = (
            'Alaska fix', 'Alaska Expansion',
            'Western Canada ProMods Connections fix',
            'Reforma OtherMaps Patch fix', 'ProMods Canada Definition Package',
            'ProMods Canada fix', 'ProMods Canada Map Package',
            'ProMods Canada Assets Package', 'ProMods Canada Models Package',
            'Western Canada fix (THIS MOD)', 'Western Canada Expansion',
            'ATS Expansion fix', 'ATS Expansion',
            'Reforma fix', 'Reforma', 'Reforma Mega Resources',
        )
        positions = [text.index(line + '\n') for line in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('Enable only fixes for maps and connectors you use', text)

    def test_fuel_and_rest_claims_follow_selected_topics(self):
        fuel = map_description('Alaska', ('fuel',))
        rest = map_description('Alaska', ('rest',), rest_radius=750)
        both = map_description('Alaska')
        self.assertIn('Lets passenger cars refuel', fuel)
        self.assertIn('original truck interactions', fuel)
        self.assertIn('experimental estimate', fuel)
        self.assertNotIn('rest access where', fuel)
        self.assertNotIn('fatigue recovery', fuel)
        self.assertIn('rest access where', rest)
        self.assertIn('750 game-world units', rest)
        self.assertIn('truck and bus rest access stays in place', rest)
        self.assertNotIn('refueling beside', rest)
        self.assertNotIn('billing', rest)
        self.assertIn('Lets passenger cars refuel', both)
        self.assertIn('passenger-car rest access', both)

    def test_othermaps_is_price_only_even_with_default_topics(self):
        text = map_description('Reforma OtherMaps Patch')
        self.assertIn('missing petrol prices', text)
        self.assertIn('no fuel station or rest area edits', text)
        self.assertNotIn('Adds passenger-car', text)
        self.assertNotIn('fatigue recovery', text)

    def test_unknown_map_has_safe_placement_without_false_stack_marker(self):
        text = map_description('Custom Map', ('fuel',))
        self.assertIn('Place (THIS MOD) directly above Custom Map.', text)
        self.assertIn('supplied map combination as an example', text)
        self.assertEqual(text.count('(THIS MOD)'), 1)
        self.assertNotIn('Alaska fix (THIS MOD)', text)

    def test_invalid_topics_rejected(self):
        with self.assertRaises(ValueError):
            map_description('Alaska', ())
        with self.assertRaises(ValueError):
            map_description('Alaska', ('courier',))


class CourierDescriptionTests(unittest.TestCase):
    def test_counts_and_scope_come_from_arguments(self):
        text = courier_description(42, 7)
        self.assertNotIn('Practical Courier Jobs', text)
        self.assertIn('42 additional reviewed courier job types', text)
        self.assertIn('All 7 vehicle-transfer jobs stay unchanged', text)
        self.assertNotIn('58 additional', text)
        self.assertIn('your own Mustang', text)
        self.assertIn('other cars in the same vehicle class and Quick Jobs', text)
        self.assertIn('this mod does not change their eligibility rules', text)
        self.assertIn('Driver rating and job-list refresh', text)
        self.assertIn('North America Background Map (if used)\nJob Types Compat Mustang (THIS MOD)', text)
        self.assertIn('replacing the base-game car job list require a compatibility check', text)


if __name__ == '__main__':
    unittest.main()
