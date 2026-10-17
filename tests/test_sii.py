import unittest

from ats_road_trip.sii import DefinitionError, parse_units


class DefinitionsTest(unittest.TestCase):
    def test_comments_quotes_and_arrays(self):
        units = parse_units('''SiiNunit {
        # data_context : context.fake { tags[]: wrong }
        data_context : context.prefab.example {
            target_data[]: prefab.sample
            tags[]: "warehouse" // trailing comment
            tags[]: factory
            note: "a { quoted } # // string"
            /* tags[]: ignored */
        }
        }''')
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].values('tags'), ('warehouse', 'factory'))
        self.assertEqual(units[0].one('note'), 'a { quoted } # // string')

    def test_relative_includes_and_fragments(self):
        sources = {'def/inc/fragment.sui': 'tags[]: warehouse\n@include "../more.sui"\n',
                   'def/more.sui': 'tags[]: factory\n'}
        text = 'SiiNunit {\ndata_context : context.test {\n@include "inc/fragment.sui"\n}\n}'
        unit = parse_units(text, source='def/data_context.sii', include_reader=sources.__getitem__)[0]
        self.assertEqual(unit.values('tags'), ('warehouse', 'factory'))

    def test_missing_reader_cycle_and_escape(self):
        for text in ('@include "x.sui"', '@include "../../x.sui"'):
            with self.assertRaises(DefinitionError):
                parse_units(text, source='def/root.sii')
        with self.assertRaises(DefinitionError):
            parse_units('@include "root.sii"', source='def/root.sii',
                        include_reader=lambda _: '@include "root.sii"')
        with self.assertRaises(DefinitionError):
            parse_units('@include "../../x.sui"', source='def/root.sii',
                        include_reader=lambda _: '')

    def test_rejects_unbalanced_and_duplicate_units(self):
        for text in ('SiiNunit {', 'SiiNunit {\nx : .a {}\nx : .a {}\n}'):
            with self.assertRaises(DefinitionError):
                parse_units(text)

    def test_does_not_interpret_header_inside_string(self):
        self.assertEqual(parse_units('note: "data_context : context.fake { }"'), [])

    def test_compact_real_company_shape_and_multiline_tuple(self):
        unit = parse_units('SiiNunit { company_def : .city { city: sample prefab: d_print } }')[0]
        self.assertEqual(unit.one('city'), 'sample')
        self.assertEqual(unit.one('prefab'), 'd_print')
        unit = parse_units('SiiNunit { x : .x { value: (1,\n2) note: "literal field: text" } }')[0]
        self.assertEqual(unit.one('value'), '(1,\n2)')
        self.assertEqual(unit.one('note'), 'literal field: text')

    def test_indexed_array_count_and_order(self):
        unit = parse_units('x : .x { tags: 2 tags[1]: second tags[0]: first }')[0]
        self.assertEqual(unit.values('tags'), ('first', 'second'))
        for text in ('x : .x { tags[1]: missing }',
                     'x : .x { tags[]: mixed tags[0]: mixed }'):
            with self.assertRaises(DefinitionError):
                parse_units(text)[0].values('tags')
        unit = parse_units('x : .x { tags: 3 tags[0]: first model_desc: "safe.pmd" }')[0]
        self.assertEqual(unit.one('model_desc'), 'safe.pmd')
        with self.assertRaises(DefinitionError):
            unit.values('tags')


if __name__ == '__main__':
    unittest.main()
