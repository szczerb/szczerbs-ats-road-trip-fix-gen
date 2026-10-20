"""End-to-end graph-edit tests with original authored map/PPD fixtures."""
from pathlib import Path
import struct
import tempfile
import unittest

from ats_road_trip.bulk_fuel import plan_map_fuel
from ats_road_trip.fuel_selection import FuelSelectionConfig
from tests.test_fuel_selection import config, rule, group
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


def duplicate_placement(source, *, delta=1000, separate_sector=None):
    """Add a second authored placement sharing the original PPD and definition."""
    parsed = parse_sector(source[SECTOR])
    entries, nodes = [], []
    for original in parsed.items:
        raw = bytearray(source[SECTOR][original.offset:original.end])
        struct.pack_into('<Q', raw, 4, original.uid + delta)
        if original.kind == 4:
            raw = item(4, original.uid + delta, struct.pack('<QQ', token('02003'), 0) + refs()
                       + refs(*(uid + delta for uid in original.details['nodes']))
                       + refs(*(uid + delta for uid in original.details['slaves']))
                       + struct.pack('<QH', 0, original.details['origin'])
                       + bytes(len(original.details['nodes']) * 12 + 8))
        else:
            struct.pack_into('<QQ', raw, 57, original.details['node'] + delta, original.details['parent'] + delta)
        entries.append(bytes(raw))
    for original in parsed.nodes:
        raw = bytearray(original.raw)
        struct.pack_into('<Q', raw, 0, original.uid + delta)
        struct.pack_into('<QQ', raw, 36, original.backward + delta if original.backward else 0,
                         original.forward + delta if original.forward else 0)
        nodes.append(bytes(raw))
    if separate_sector is not None:
        return {**source, separate_sector: sector(entries, nodes)}
    originals = [source[SECTOR][entry.offset:entry.end] for entry in parsed.items]
    return {**source, SECTOR: sector(originals + entries, [node.raw for node in parsed.nodes] + nodes)}


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

    def selective_plan(self, source, selection):
        package = self.package('map', source)
        return plan_map_fuel(ResourceStack([package]), map_packages={str(package.path)},
                             map_name='fixture', fuel_selection=selection)

    def test_explicit_broad_is_identical_to_legacy(self):
        package = self.package('map', resources())
        stack = ResourceStack([package])
        args = {'map_packages': {str(package.path)}, 'map_name': 'fixture'}
        self.assertEqual(plan_map_fuel(stack, **args),
                         plan_map_fuel(stack, **args, fuel_selection=FuelSelectionConfig()))

    def test_selective_mixed_layout_adds_only_reviewed_public_pump(self):
        source = resources([((2., 0., 3.), 0), ((8., 0., 3.), 0)])
        selected = config(rule(source[PPD], roles=('public_car', 'truck_lane')))
        report, output = self.selective_plan(source, selected)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['policy_skipped_truck_points'], 1)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertEqual(report['static_validation']['truck_points_with_car_counterparts'], 1)
        after = parse_sector(output[SECTOR])
        self.assertEqual(len(after.services), 3)
        ppd = next(data for name, data in output.items() if name.endswith('.ppd'))
        spawns = inspect_ppd(ppd)['spawns']
        self.assertEqual(len(spawns), 3)
        self.assertEqual(spawns[-1]['position'], spawns[0]['position'])
        original = parse_sector(source[SECTOR])
        for service in original.services:
            new = next(item for item in after.services if item.uid == service.uid)
            self.assertEqual(source[SECTOR][service.offset:service.end], output[SECTOR][new.offset:new.end])
        nodes = {node.uid: node.raw for node in after.nodes}
        self.assertTrue(all(nodes[node.uid] == node.raw for node in original.nodes))

    def test_unknown_skip_is_complete_and_emits_no_changes(self):
        report, output = self.selective_plan(resources(), config())
        self.assert_complete(report)
        self.assertEqual(output, {})
        self.assertEqual(report['coverage']['uncertain_skipped_points'], 1)
        self.assertEqual(report['stations'][0]['status'], 'policy_skipped')

    def test_unknown_include_is_explicitly_reported(self):
        report, output = self.selective_plan(resources(), config(unknown='include'))
        self.assert_complete(report)
        self.assertEqual(report['coverage']['uncertain_included_points'], 1)
        self.assertEqual(report['coverage']['added_car_points'], 1)

    def test_native_car_support_is_retained_at_rejected_and_separate_pumps(self):
        source = resources([((2., 0., 3.), 0), ((2., 0., 3.), 1), ((8., 0., 3.), 1)])
        report, output = self.selective_plan(source, config(rule(source[PPD], roles=('truck_lane',))))
        self.assert_complete(report)
        self.assertEqual(output, {})
        self.assertEqual(report['coverage']['native_car_services_retained'], 2)
        self.assertEqual(report['coverage']['native_car_locators_retained'], 2)
        self.assertEqual(report['coverage']['skipped_points_with_native_car_support'], 1)
        details = report['stations'][0]['fuel_selection']
        self.assertEqual(details['native_car_spawn_indices'], [1, 2])
        self.assertTrue(details['groups'][0]['native_support_prevents_exclusion'])

    def test_rejected_native_locator_is_not_given_new_cached_service(self):
        source = resources()
        source[PPD] = resources([((2., 0., 3.), 0), ((2., 0., 3.), 1)])[PPD]
        report, output = self.selective_plan(source, config())
        self.assert_complete(report)
        self.assertEqual(output, {})
        self.assertEqual(report['coverage']['skipped_points_with_native_car_support'], 1)
        self.assertEqual(report['coverage']['added_car_points'], 0)

    def test_garage_is_excluded_even_with_uncertain_include(self):
        report, output = self.selective_plan(resources(garage=True), config(unknown='include'))
        self.assert_complete(report)
        self.assertEqual(output, {})
        self.assertEqual(report['stations'][0]['fuel_selection']['groups'][0]['role'], 'fleet_yard')

    def test_drift_is_a_blocker_and_skipping_does_not_hide_invalid_source(self):
        source = resources()
        report, output = self.selective_plan(source, config(rule(source[PPD], descriptor_sha256='0' * 64)))
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('SHA256 drift', report['coverage']['blockers'][0]['reason'])
        self.assertEqual(output, {})

    def test_unknown_skip_does_not_hide_unsupported_legacy_semaphore(self):
        report, output = self.selective_plan(resources(legacy=True, semaphore=True), config())
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('semaphore', report['coverage']['blockers'][0]['reason'])
        self.assertEqual(output, {})

    def test_policy_skip_does_not_hide_invalid_fuel_node_ownership(self):
        source = resources()
        parsed = parse_sector(source[SECTOR])
        service = parsed.services[0]
        fuel_node = next(node for node in parsed.nodes if node.uid == service.details['node'])
        changed = bytearray(source[SECTOR])
        struct.pack_into('<Q', changed, fuel_node.offset + 36, 123)
        source[SECTOR] = bytes(changed)
        report, output = self.selective_plan(source, config())
        self.assertFalse(report['coverage']['complete'])
        self.assertIn('ownership', report['coverage']['blockers'][0]['reason'])
        self.assertEqual(output, {})

    def test_car_only_native_facility_is_counted_and_unchanged(self):
        source = resources([((2., 0., 3.), 1)])
        report, output = self.selective_plan(source, config())
        self.assert_complete(report)
        self.assertEqual(output, {})
        self.assertEqual(report['coverage']['native_car_services_retained'], 1)
        self.assertEqual(report['stations'][0]['fuel_selection']['native_car_spawn_indices'], [0])

    def test_legacy_unknown_skip_does_not_emit_upgrade_only_alias(self):
        report, output = self.selective_plan(resources(legacy=True), config())
        self.assert_complete(report)
        self.assertEqual(output, {})

    def test_same_descriptor_two_placements_use_distinct_subset_aliases(self):
        source = resources([((2., 0., 3.), 0), ((8., 0., 3.), 0)])
        parsed = parse_sector(source[SECTOR])
        entries = [source[SECTOR][item.offset:item.end] for item in parsed.items]
        nodes = [node.raw for node in parsed.nodes]
        for original in parsed.items:
            raw = bytearray(source[SECTOR][original.offset:original.end])
            struct.pack_into('<Q', raw, 4, original.uid + 1000)
            if original.kind == 4:
                # Rebuild the independent placement using the same model/state.
                raw = item(4, original.uid + 1000, struct.pack('<QQ', token('02003'), 0) + refs()
                           + refs(*(uid + 1000 for uid in original.details['nodes']))
                           + refs(*(uid + 1000 for uid in original.details['slaves']))
                           + struct.pack('<QH', 0, original.details['origin'])
                           + bytes(len(original.details['nodes']) * 12 + 8))
            else:
                struct.pack_into('<QQ', raw, 57, original.details['node'] + 1000, original.details['parent'] + 1000)
            entries.append(bytes(raw))
        for original in parsed.nodes:
            raw = bytearray(original.raw)
            struct.pack_into('<Q', raw, 0, original.uid + 1000)
            struct.pack_into('<QQ', raw, 36, original.backward + 1000 if original.backward else 0,
                             original.forward + 1000 if original.forward else 0)
            nodes.append(bytes(raw))
        entries.append(item(6, 900, struct.pack('<4Q', token('city'), 1100, token('company'), 0) + refs()))
        source[SECTOR] = sector(entries, nodes)
        selected = config(rule(source[PPD], roles=('public_car', 'truck_lane'), company_linked=False),
                          rule(source[PPD], id='company-layout', roles=('truck_lane', 'public_car'), company_linked=True))
        report, output = self.selective_plan(source, selected)
        self.assert_complete(report)
        self.assertEqual(report['coverage']['added_car_points'], 2)
        self.assertEqual(len([name for name in output if name.endswith('.ppd')]), 2)
        self.assertEqual(len({station['private_alias'] for station in report['stations']}), 2)
        self.assertEqual([station['fuel_selection']['groups'][0]['same_parent_company_uids']
                          for station in report['stations']], [[], ['0x384']])

    def test_bounded_scope_mutates_only_target_of_two_shared_descriptor_placements(self):
        source = duplicate_placement(resources())
        package = self.package('map', source)
        report, output = plan_map_fuel(ResourceStack([package]), map_packages={str(package.path)},
                                      map_name='fixture', target_prefab_uids=frozenset({100}),
                                      source_sector_paths=frozenset({SECTOR}))
        self.assert_complete(report)
        self.assertEqual(report['analysis'], 'bounded_missing_car_fuel')
        self.assertEqual(report['scope']['target_prefab_uids'], ['0x64'])
        self.assertEqual(report['coverage']['added_car_points'], 1)
        before, after = parse_sector(source[SECTOR]), parse_sector(output[SECTOR])
        originals = {entry.uid: source[SECTOR][entry.offset:entry.end] for entry in before.items}
        for entry in after.items:
            if entry.uid in originals and entry.uid != 100:
                self.assertEqual(output[SECTOR][entry.offset:entry.end], originals[entry.uid])
        parents = {entry.uid: entry for entry in after.prefabs}
        self.assertNotEqual(parents[100].details['model'], token('02003'))
        self.assertEqual(parents[1100].details['model'], token('02003'))
        self.assertEqual(source[PPD], package.read(PPD))
        self.assertNotIn(PPD, output)
        self.assertEqual(len([service for service in after.services if service.flags & 0x4000]), 1)

    def test_scope_paths_bound_the_source_inventory(self):
        other = 'map/usa/sec+0004+0000.base'
        source = duplicate_placement(resources(), separate_sector=other)
        package = self.package('map', source)
        report, output = plan_map_fuel(ResourceStack([package]), map_packages={str(package.path)},
                                      map_name='fixture', source_sector_paths=frozenset({SECTOR}))
        self.assert_complete(report)
        self.assertEqual(report['sectors_inspected'], 1)
        self.assertEqual(report['coverage']['added_car_points'], 1)
        self.assertNotIn(other, output)
        self.assertEqual(report['scope']['source_sector_paths'], [SECTOR])

    def test_unknown_or_outside_scope_target_is_a_blocker(self):
        source = duplicate_placement(resources(), separate_sector='map/usa/sec+0004+0000.base')
        package = self.package('map', source)
        for uid in (999, 300, 1100):
            with self.subTest(uid=uid):
                report, output = plan_map_fuel(ResourceStack([package]), map_packages={str(package.path)},
                                              map_name='fixture', target_prefab_uids=frozenset({uid}),
                                              source_sector_paths=frozenset({SECTOR}))
                self.assertFalse(report['coverage']['complete'])
                self.assertEqual(report['coverage']['blockers'][0]['area'], 'scope')
                self.assertEqual(output, {})

    def test_explicit_none_scope_is_identical_to_legacy(self):
        package = self.package('map', resources())
        stack = ResourceStack([package]); arguments = {'map_packages': {str(package.path)}, 'map_name': 'fixture'}
        self.assertEqual(plan_map_fuel(stack, **arguments), plan_map_fuel(stack, **arguments,
                            target_prefab_uids=None, source_sector_paths=None))

    def test_invalid_scope_and_ineligible_provider_are_rejected(self):
        package = self.package('map', resources())
        stack = ResourceStack([package]); arguments = {'map_packages': {str(package.path)}, 'map_name': 'fixture'}
        for value in (frozenset(), {100}, frozenset({True}), frozenset({0}), frozenset({'100'}), frozenset({2**64})):
            with self.subTest(targets=value), self.assertRaises(ValueError):
                plan_map_fuel(stack, **arguments, target_prefab_uids=value)
        for value in (frozenset(), {SECTOR}, frozenset({True}), frozenset({'/' + SECTOR}),
                      frozenset({'map/../sec+0000+0000.base'}), frozenset({'map/usa/sec+0008+0000.base'})):
            with self.subTest(paths=value), self.assertRaises(ValueError):
                plan_map_fuel(stack, **arguments, source_sector_paths=value)
        with self.assertRaisesRegex(ValueError, 'eligible source'):
            plan_map_fuel(stack, map_packages=set(), map_name='fixture', source_sector_paths=frozenset({SECTOR}))
        override = self.package('override', {SECTOR: resources()[SECTOR]})
        with self.assertRaisesRegex(ValueError, 'eligible source'):
            plan_map_fuel(ResourceStack([package, override]), **arguments,
                          source_sector_paths=frozenset({SECTOR}))

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

    def test_expansion_display_renames_preserve_established_fuel_payload(self):
        package = self.package('map', resources(visibility=True))
        stack = ResourceStack([package])
        for old_name, public_name in [('Alaska', 'Alaska Expansion'),
                                      ('Western Canada', 'Western Canada Expansion')]:
            with self.subTest(map=public_name):
                old_report, old_output = plan_map_fuel(
                    stack, map_packages={str(package.path)}, map_name=old_name)
                report, output = plan_map_fuel(
                    stack, map_packages={str(package.path)}, map_name=public_name)
                self.assert_complete(report)
                self.assertEqual(report['map_name'], public_name)
                self.assertEqual(output, old_output)
                self.assertTrue(any(path.endswith('.ppd') for path in output))
                self.assertEqual(report['coverage'], old_report['coverage'])

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
