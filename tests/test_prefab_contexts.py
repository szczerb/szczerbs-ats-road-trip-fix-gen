"""Generated prefab aliases retain only proven effective context tags."""

from pathlib import Path
import hashlib
import struct
from tempfile import TemporaryDirectory
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.prefab_contexts import plan_prefab_contexts
from ats_road_trip.sii import parse_units
from tests.test_rest_stops import SECTOR, source as rest_source


def context(name='context.original', target='prefab.rest', tags=('truck_dealer',)):
    return ('data_context : ' + name + ' {\n target_data[]: ' + target + '\n' +
            ''.join(' tags[]: ' + tag + '\n' for tag in tags) + '}\n')


def alias(name):
    return ('SiiNunit\n{\nprefab_model : prefab.' + name + ' {\n'
            ' prefab_desc: "/prefab/rtfix/' + name + '.ppd"\n'
            ' model_desc: "/prefab/test/rest.pmd"\n}\n}\n').encode()


def model_change(data, name):
    changed = bytearray(data)
    prefab = parse_sector(data).prefabs[0]
    struct.pack_into('<Q', changed, prefab.offset + 57, token(name))
    return bytes(changed)


class ContextPreservationTests(unittest.TestCase):
    def plan(self, definitions, *, chain=('rtg12345678',), extra_resources=None,
             source_name='fixture-map', context_path='def/data_context.sii',
             collide_target=False):
        fixture = rest_source()
        if definitions is not None:
            fixture[context_path] = ('SiiNunit\n{\n' + definitions + '\n}\n').encode()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for path, contents in fixture.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(contents)
            with Package(root) as package:
                stack = ResourceStack([package])
                resources = {f'def/world/prefab.{name}.sii': alias(name) for name in chain}
                resources.update(extra_resources or {})
                if collide_target:
                    suffix = hashlib.sha256((source_name + '\0' + str(package.path)).encode()).hexdigest()[:12]
                    resources[f'def/data_context.rtf{suffix}.sii'] = b'occupied'
                steps = []
                before = fixture[SECTOR]
                for index, name in enumerate(chain):
                    after = model_change(before, name)
                    steps.append(('fuel' if index == 0 else 'rest', SECTOR, before, after))
                    before = after
                report, output = plan_prefab_contexts(stack, resources, steps,
                                                      source=str(package.path), map_name=source_name)
                return report, output

    def test_fuel_alias_copies_exact_effective_tags_with_provenance(self):
        report, output = self.plan(context(tags=('truck_dealer', 'service')))
        self.assertTrue(report['coverage']['complete'], report['blockers'])
        self.assertEqual(len(output), 1)
        path, body = next(iter(output.items()))
        self.assertRegex(path, r'^def/data_context\.rtf[a-f0-9]{12}\.sii$')
        unit = parse_units(body.decode())[0]
        self.assertEqual(unit.values('target_data'), ('prefab.rtg12345678',))
        self.assertEqual(unit.values('tags'), ('truck_dealer', 'service'))
        row = report['aliases'][0]
        self.assertEqual(row['original'], 'prefab.rest')
        self.assertEqual(row['original_contexts'][0]['resource'], 'def/data_context.sii')
        self.assertEqual(row['placements'][0]['prefab_uid'], '0x64')

    def test_rest_and_composed_chain_each_preserve_original(self):
        definitions = context()
        for chain in (('rtr12345678',), ('rtg12345678', 'rtr12345678')):
            with self.subTest(chain=chain):
                report, output = self.plan(definitions, chain=chain)
                self.assertTrue(report['coverage']['complete'], report['blockers'])
                self.assertEqual({row['original'] for row in report['aliases']}, {'prefab.rest'})
                self.assertEqual({u.values('target_data')[0] for u in parse_units(next(iter(output.values())).decode())},
                                 {'prefab.' + name for name in chain})

    def test_exclusion_and_unclassified_original_never_gain_tags(self):
        for definitions, status in (('# prefab.rest excluded\n', 'excluded'),
                                    ('', 'unclassified')):
            with self.subTest(status=status):
                report, output = self.plan(definitions)
                self.assertTrue(report['coverage']['complete'])
                self.assertEqual(output, {})
                self.assertEqual(report['aliases'][0]['status'], status)

    def test_exclusion_comment_conflicting_with_live_original_tags_blocks(self):
        report, output = self.plan('# prefab.rest excluded\n' + context())
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertEqual(report['aliases'][0]['status'], 'blocked')
        self.assertEqual(report['blockers'][0]['area'], 'exclusion_context_conflict')
        self.assertEqual(report['aliases'][0]['original_contexts'][0]['tags'], ('truck_dealer',))

    def test_existing_alias_context_for_excluded_or_unclassified_original_blocks(self):
        alias_context = context('context.alias', 'prefab.rtg12345678')
        for definitions in ('# prefab.rest excluded\n' + alias_context, alias_context):
            with self.subTest(definitions=definitions):
                report, output = self.plan(definitions)
                self.assertFalse(report['coverage']['complete'])
                self.assertEqual(output, {})
                self.assertEqual(report['aliases'][0]['status'], 'blocked')
                self.assertEqual(report['blockers'][0]['area'], 'alias_context_conflict')

    def test_identical_existing_target_needs_no_duplicate_and_conflict_blocks(self):
        same = context() + context('context.alias', 'prefab.rtg12345678')
        report, output = self.plan(same)
        self.assertTrue(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertEqual(report['aliases'][0]['status'], 'already_classified')
        conflict = context() + context('context.alias', 'prefab.rtg12345678', ('wrong',))
        report, output = self.plan(conflict)
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertEqual(report['blockers'][0]['area'], 'alias_context_conflict')

    def test_conflicting_original_definitions_and_unproven_alias_block(self):
        report, output = self.plan(context() + context('context.second', tags=('other',)))
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertEqual(report['blockers'][0]['area'], 'context_conflict')
        report, output = self.plan(context(), chain=('rtg12345678', 'rtr12345678'),
                                   extra_resources={'def/world/prefab.rtx12345678.sii': alias('rtx12345678')})
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertTrue(any(b['area'] == 'alias_coverage' for b in report['blockers']))

    def test_duplicate_context_unit_and_generated_path_collision_block(self):
        report, output = self.plan(context() + context())
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertEqual(report['blockers'][0]['area'], 'effective_definitions')
        report, output = self.plan(context(), collide_target=True)
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(output, {})
        self.assertTrue(any(b['area'] == 'resource_collision' for b in report['blockers']))

    def test_additive_resource_name_and_unit_differ_by_map(self):
        first, first_output = self.plan(context(), source_name='western-canada')
        second, second_output = self.plan(context(), source_name='other-map')
        self.assertNotEqual(first['generated_resource'], second['generated_resource'])
        self.assertNotEqual(parse_units(next(iter(first_output.values())).decode())[0].name,
                            parse_units(next(iter(second_output.values())).decode())[0].name)


if __name__ == '__main__':
    unittest.main()
