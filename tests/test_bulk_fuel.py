"""End-to-end graph-edit tests with original authored map/PPD fixtures."""
from pathlib import Path
import struct
import tempfile
import unittest

from ats_road_trip.bulk_fuel import plan_map_fuel
from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_layer, parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.ppd import inspect_ppd
from tests.test_fuel_matching import fixture as matching_fixture
from tests.test_map_sector import HEADER, item, refs, sector


SECTOR = 'map/usa/sec+0000+0000.base'
PPD = 'prefab/test/station.ppd'
DEF = 'def/world/prefab.test.sii'
DEFINITION = '''SiiNunit
{
prefab_model : prefab.02003 {
 prefab_desc: "/prefab/test/station.ppd"
 model_desc: "/prefab/test/station.pmd"
 category: "fixture"
 opaque_vector: (1.0, 2.0, 3.0)
 additional_parts[]: "first"
 additional_parts[]: "second"
}
}
'''


def resources(spawns=None, *, garage=False, visibility=False, legacy=False, semaphore=False):
    if spawns is None:
        spawns = [((2., 0., 3.), 0)]
    ppd, prefab, nodes, services = matching_fixture(spawns)
    if legacy:
        h = list(struct.unpack_from('<24I', ppd))
        start, end = h[16:18]
        h[0] = 23
        converted = b''.join(ppd[start + 36*i:start + 36*i + 32] for i in range(h[5]))
        for i in range(17, 24):
            h[i] -= 4 * h[5]
        ppd = struct.pack('<24I', *h) + ppd[96:start] + converted + ppd[end:]
    if semaphore:
        h = list(struct.unpack_from('<24I', ppd))
        insertion = h[16]
        h[4] = 1
        for i in range(16, 24):
            h[i] += 68
        ppd = struct.pack('<24I', *h) + ppd[96:insertion] + bytes(68) + ppd[insertion:]
    pf = item(4, prefab.uid, struct.pack('<QQ', token('02003'), 0) + refs()
              + refs(*prefab.details['nodes']) + refs(*(s.uid for s in services))
              + struct.pack('<QH', 0, prefab.details['origin']) + bytes(len(prefab.details['nodes']) * 12 + 8))
    entries = [pf]
    for s in reversed(services):
        kind = 35 if garage and not s.flags & 0x4000 else 7
        entries.append(item(kind, s.uid, struct.pack('<QQ', s.details['node'], s.details['parent'])
                            + refs(), flags=s.flags))
    if visibility:
        entries.append(item(0x30, 500, struct.pack('<Qff', 200, 10., 10.) + refs(300)))
    node_bytes = []
    for n in nodes.values():
        node_bytes.append(struct.pack('<Q3i4fQQI', n.uid, *(round(p * 256) for p in n.position),
                                      *n.rotation, n.backward, n.forward, n.flags))
    result = {SECTOR: sector(entries, node_bytes, (300,) if visibility else ()),
              PPD: ppd, DEF: DEFINITION.encode()}
    if visibility:
        result[SECTOR.removesuffix('.base') + '.layer'] = HEADER + struct.pack('<QB', 300, 2) + b'\xff' * 8
    return result


class BulkFuelTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.packages = []
        self.addCleanup(self.temporary.cleanup)
        self.addCleanup(lambda: [p.close() for p in self.packages])

    def package(self, name, contents):
        root = self.root / name
        root.mkdir()
        for path, data in contents.items():
            file = root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        package = Package(root)
        self.packages.append(package)
        return package

    def plan(self, contents, *, before=()):
        package = self.package('map', contents)
        stack = ResourceStack([*before, package])
        return package, plan_map_fuel(stack, map_packages={str(package.path)}, map_name='fixture')

    def assert_complete(self, report):
        self.assertTrue(report['coverage']['complete'], report['coverage']['blockers'])

    def test_uppercase_declared_prefab_resolves_lowercase_map_token(self):
        source = resources()
        source[DEF] = source[DEF].replace(b'prefab.02003', b'prefab.Ab12')
        changed = bytearray(source[SECTOR])
        struct.pack_into('<Q', changed, 20 + 57, token('ab12'))
        source[SECTOR] = bytes(changed)
        _, (report, output) = self.plan(source)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertEqual(report['static_validation']['truck_points_with_car_counterparts'], 1)

    def test_repeated_planning_from_identical_sources_is_deterministic(self):
        package = self.package('map', resources([((2.,0.,3.),0), ((8.,0.,3.),0)]))
        stack = ResourceStack([package])
        options = {'map_packages': {str(package.path)}, 'map_name':'fixture'}
        first = plan_map_fuel(stack, **options)
        second = plan_map_fuel(stack, **options)
        self.assert_complete(first[0])
        self.assertEqual(first, second)

    def test_four_shuffled_points_and_original_records_preserved(self):
        original = resources([((x, 0.02, 2.), 0) for x in (-18., -6., 6., 18.)])
        _, (report, output) = self.plan(original)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 4)
        before = parse_sector(original[SECTOR])
        after = parse_sector(output[SECTOR])
        self.assertEqual(len(after.services), 8)
        self.assertEqual([n.uid for n in after.nodes], sorted(n.uid for n in after.nodes))
        for old in before.services:
            new = next(i for i in after.services if i.uid == old.uid)
            self.assertEqual(original[SECTOR][old.offset:old.end], output[SECTOR][new.offset:new.end])
        old_nodes = {n.uid: n.raw for n in before.nodes}
        self.assertTrue(all(n.raw == old_nodes[n.uid] for n in after.nodes if n.uid in old_nodes))
        old_by_pos = {n.position for n in before.nodes if n.forward in {s.uid for s in before.services}}
        new_nodes = [n for n in after.nodes if n.uid not in old_nodes]
        self.assertEqual({n.position for n in new_nodes}, old_by_pos)
        changed_ppd = next(data for name, data in output.items() if name.endswith('.ppd'))
        self.assertEqual(inspect_ppd(changed_ppd)['fuel']['flags_one_count'], 4)

    def test_existing_car_at_one_of_two_points_is_not_duplicated(self):
        _, (report, output) = self.plan(resources([((2., 0., 3.), 0), ((2., 0., 3.), 1), ((8., 0., 3.), 0)]))
        self.assert_complete(report)
        self.assertEqual(report['coverage']['already_supported'], 1)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertEqual(len(parse_sector(output[SECTOR]).services), 4)

    def test_existing_car_locator_without_cached_service_adds_only_service(self):
        source = resources()
        source[PPD] = resources([((2., 0., 3.), 0), ((2., 0., 3.), 1)])[PPD]
        _, (report, output) = self.plan(source)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertEqual(len(parse_sector(output[SECTOR]).services), 2)
        self.assertFalse(any(path.endswith('.ppd') for path in output))

    def test_existing_car_service_without_locator_adds_only_locator(self):
        source = resources([((2., 0., 3.), 0), ((2., 0., 3.), 1)])
        source[PPD] = resources()[PPD]
        _, (report, output) = self.plan(source)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 0)
        self.assertEqual(len(parse_sector(output[SECTOR]).services), 2)
        ppd = next(data for path, data in output.items() if path.endswith('.ppd'))
        self.assertEqual(inspect_ppd(ppd)['fuel']['flags_one_count'], 1)

    def test_effective_stack_is_idempotent_when_generated_package_is_targeted(self):
        package, (report, output) = self.plan(resources())
        self.assert_complete(report)
        generated = self.package('generated', output)
        second, changes = plan_map_fuel(ResourceStack([package, generated]),
                                        map_packages={str(package.path), str(generated.path)}, map_name='fixture')
        self.assert_complete(second)
        self.assertEqual(second['coverage']['added_car_points'], 0)
        self.assertEqual(second['coverage']['already_supported'], 1)
        self.assertEqual(changes, {})

    def test_only_declared_source_map_is_targeted(self):
        unrelated = resources()
        unrelated['map/usa/sec+0020+0020.base'] = unrelated.pop(SECTOR)
        unrelated.pop(DEF)
        stock = self.package('stock', unrelated)
        _, (report, output) = self.plan(resources(), before=[stock])
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertNotIn('map/usa/sec+0020+0020.base', output)

    def test_target_prefab_follows_service_in_adjacent_stock_sector(self):
        source = resources()
        parsed = parse_sector(source[SECTOR])
        prefab = parsed.prefabs[0]
        service = parsed.services[0]
        source_bytes = source[SECTOR]
        source[SECTOR] = sector([source_bytes[prefab.offset:prefab.end]],
                                [n.raw for n in parsed.nodes if n.forward == prefab.uid])
        neighbor_path = 'map/usa/sec+0001+0000.base'
        stock = self.package('stock', {
            neighbor_path: sector([source_bytes[service.offset:service.end]],
                                  [n.raw for n in parsed.nodes if n.forward == service.uid]),
        })
        _, (report, output) = self.plan(source, before=[stock])
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertIn(neighbor_path, output)

    def test_missing_definition_is_an_explicit_coverage_blocker(self):
        contents = resources()
        del contents[DEF]
        _, (report, _) = self.plan(contents)
        self.assertFalse(report['coverage']['complete'])
        self.assertTrue(report['coverage']['blockers'])

    def test_garage_adds_regular_car_service_retaining_truck_fuelpump(self):
        original = resources(garage=True)
        _, (report, output) = self.plan(original)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['garage_car_points'], 1)
        after = parse_sector(output[SECTOR])
        self.assertEqual([(s.kind, bool(s.flags & 0x4000)) for s in after.services], [(35, False), (7, True)])
        old = parse_sector(original[SECTOR]).services[0]
        same = next(s for s in after.services if s.uid == old.uid)
        self.assertEqual(original[SECTOR][old.offset:old.end], output[SECTOR][same.offset:same.end])

    def orphan_garage_packages(self, *, mismatched_position=False):
        source = resources(garage=True)
        original = source[SECTOR]
        parsed = parse_sector(original)
        prefab, pump = parsed.prefabs[0], parsed.services[0]
        # Reproduce a map override with a newer stock parent retaining an old,
        # unavailable FuelPump UID alongside its two ordinary Garage slaves.
        raw_parent = original[prefab.offset:prefab.end]
        start = prefab.details['slave_count_offset'] - prefab.offset
        end = prefab.details['slave_insert_offset'] - prefab.offset
        raw_parent = raw_parent[:start] + refs(700, 701, 999) + raw_parent[end:]
        garages = [item(22, uid, struct.pack('<QIQQ', 0, buy, 500 + buy, prefab.uid) + refs())
                   for uid, buy in ((700, 0), (701, 1))]
        parent_nodes = [n.raw for n in parsed.nodes if n.forward == prefab.uid]
        parent_nodes.extend(struct.pack('<Q3i4fQQI', node_uid, 0, 0, 0,
                                        1., 0., 0., 0., 0, owner, 0)
                            for node_uid, owner in ((500, 700), (501, 701)))
        pump_node = bytearray(next(n.raw for n in parsed.nodes if n.forward == pump.uid))
        if mismatched_position:
            x = struct.unpack_from('<i', pump_node, 8)[0]
            struct.pack_into('<i', pump_node, 8, x + 10 * 256)
        source[SECTOR] = sector([original[pump.offset:pump.end]], [bytes(pump_node)])
        stock_path = 'map/usa/sec+0000+0001.base'
        stock = self.package('stock', {stock_path: sector([raw_parent, *garages], parent_nodes)})
        return source, stock, stock_path, original[pump.offset:pump.end], bytes(pump_node)

    def test_source_orphan_fuelpump_with_unique_geometry_adds_only_car_reference(self):
        source, stock, parent_path, original_pump, original_node = self.orphan_garage_packages()
        _, (report, output) = self.plan(source, before=[stock])
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertEqual(report['stations'][0]['preexisting_unlisted_fuel_uids'], [hex(300)])
        after = parse_sector(output[SECTOR])
        old = next(s for s in after.services if s.uid == 300)
        car = next(s for s in after.services if s.flags & 0x4000)
        self.assertEqual(output[SECTOR][old.offset:old.end], original_pump)
        self.assertEqual(next(n.raw for n in after.nodes if n.forward == 300), original_node)
        slaves = parse_sector(output[parent_path]).prefabs[0].details['slaves']
        self.assertEqual(slaves, (700, 701, 999, car.uid))
        self.assertNotIn(300, slaves)  # The pre-existing truck mismatch is preserved.
        self.assertEqual(car.kind, 7)

    def test_source_orphan_fuelpump_with_mismatched_geometry_remains_blocked(self):
        source, stock, _, _, _ = self.orphan_garage_packages(mismatched_position=True)
        _, (report, _) = self.plan(source, before=[stock])
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(report['coverage']['added_car_points'], 0)
        self.assertTrue(any('unique fuel matches' in b['reason'] for b in report['coverage']['blockers']))

    def test_orphan_exception_does_not_accept_unobserved_regular_service_case(self):
        source, stock, _, _, _ = self.orphan_garage_packages()
        changed = bytearray(source[SECTOR])
        struct.pack_into('<I', changed, 20, 7)
        source[SECTOR] = bytes(changed)
        _, (report, _) = self.plan(source, before=[stock])
        self.assertFalse(report['coverage']['complete'])
        self.assertEqual(report['coverage']['added_car_points'], 0)
        self.assertTrue(any('outside the observed truck FuelPump case' in b['reason']
                            for b in report['coverage']['blockers']))

    def test_definition_preserves_opaque_typed_and_array_attributes(self):
        _, (report, output) = self.plan(resources())
        self.assert_complete(report)
        definition = next(data.decode() for name, data in output.items() if name.startswith('def/'))
        self.assertIn('opaque_vector: (1.0, 2.0, 3.0)', definition)
        self.assertIn('additional_parts[]: "first"', definition)
        self.assertIn('additional_parts[]: "second"', definition)
        self.assertIn('model_desc: "/prefab/test/station.pmd"', definition)

    def test_nonempty_visibility_references_and_layers_follow_service_clone(self):
        _, (report, output) = self.plan(resources(visibility=True))
        self.assert_complete(report)
        after = parse_sector(output[SECTOR])
        car = next(s for s in after.services if s.flags & 0x4000)
        self.assertEqual(after.visibility_children, (300, car.uid))
        vis = next(i for i in after.items if i.kind == 0x30)
        self.assertEqual(vis.details['children'], (300, car.uid))
        layer = parse_layer(output[SECTOR.removesuffix('.base') + '.layer'])
        self.assertEqual(layer, {300: 2, car.uid: 2})

    def test_v23_zero_semaphore_upgrade_preserves_opaque_sections(self):
        original = resources(legacy=True)
        _, (report, output) = self.plan(original)
        self.assert_complete(report)
        ppd = next(data for path, data in output.items() if path.endswith('.ppd'))
        self.assertEqual(inspect_ppd(ppd)['version'], 25)
        self.assertEqual(inspect_ppd(ppd)['fuel']['flags_one_count'], 1)
        self.assertEqual(report['stations'][0]['descriptor_upgrade']['from_version'], 23)
        self.assertEqual(ppd[96:304], original[PPD][96:304])

    def test_legacy_semaphore_is_an_explicit_blocker(self):
        _, (report, _) = self.plan(resources(legacy=True, semaphore=True))
        self.assertFalse(report['coverage']['complete'])
        self.assertTrue(any('semaphore' in b['reason'] for b in report['coverage']['blockers']))

    def test_unknown_sector_layout_is_an_explicit_blocker(self):
        contents = resources()
        contents[SECTOR] = sector([item(0x77, 100)])
        _, (report, output) = self.plan(contents)
        self.assertFalse(report['coverage']['complete'])
        self.assertTrue(any('Unsupported map item type' in b['reason'] for b in report['coverage']['blockers']))
        self.assertEqual(output, {})


if __name__ == '__main__':
    unittest.main()
