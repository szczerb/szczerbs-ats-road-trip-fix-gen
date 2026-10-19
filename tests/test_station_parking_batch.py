"""Finite station composition tests use original authored map/model fixtures."""
from copy import deepcopy
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from ats_road_trip.bulk_fuel import _alias_definition
from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.station_parking import plan_station_parking
from ats_road_trip.station_parking.batch import compose_station_plans, validate_manifest
from ats_road_trip.station_parking.trigger import append_car_parking_polygon
from tests.test_bulk_fuel import DEF, PPD, SECTOR, DEFINITION
from tests.test_map_sector import item, refs, sector
from tests.test_station_effective_planning import pit_text
from tests.test_station_parking import mesh_text, source_resources

SECOND_SECTOR = 'map/usa/sec+0001+0000.base'
VERSION = '1.61.3.18'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def clone_station(data, *, variant=0, model='02003'):
    """Clone an authored service graph to a second globally unique placement."""
    parsed = parse_sector(data)
    entries = []
    for source in parsed.items:
        d = source.details
        if source.kind == 4:
            payload = (struct.pack('<QQ', token(model), variant) + refs(*d['parts'])
                       + refs(*(uid + 1000 for uid in d['nodes']))
                       + refs(*(uid + 1000 for uid in d['slaves']))
                       + struct.pack('<QH', d['ferry'], d['origin'])
                       + data[source.end - len(d['nodes']) * 12 - 8:source.end])
        else:
            payload = struct.pack('<QQ', d['node'] + 1000, d['parent'] + 1000) + refs(*(uid + 1000 for uid in d['nodes']))
        entries.append(item(source.kind, source.uid + 1000, payload, flags=source.flags))
    nodes = []
    for source in parsed.nodes:
        raw = bytearray(source.raw)
        struct.pack_into('<Q', raw, 0, source.uid + 1000)
        struct.pack_into('<Q', raw, 36, source.backward + 1000 if source.backward else 0)
        struct.pack_into('<Q', raw, 44, source.forward + 1000 if source.forward else 0)
        nodes.append(bytes(raw))
    return entries, nodes


def manifest():
    return {'schema_version': 1, 'processor': 'station_parking_batch', 'batch_id': 'fixture-batch',
            'map_name': 'Curated Stations', 'game_version': VERSION, 'stations': [
                {'site_id': 'P02', 'source_package': 'source.scs', 'config': 'second.json', 'mesh': 'station.pim'},
                {'site_id': 'P01', 'source_package': 'source.scs', 'config': 'first.json', 'mesh': 'station.pim'}]}


class StationBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packages = []
        self.addCleanup(lambda: [p.close() for p in self.packages])
        self.mesh = mesh_text()

    def package(self, name, resources):
        path = self.root / name
        with zipfile.ZipFile(path, 'w') as archive:
            for virtual, data in resources.items():
                archive.writestr(virtual, data)
        package = Package(path)
        self.packages.append(package)
        return package

    def fixture(self, *, same_sector=True, different_state=False, baseline=False):
        original = source_resources()
        parsed = parse_sector(original[SECTOR])
        entries, nodes = clone_station(original[SECTOR], variant=token('city') if different_state else 0,
                                       model='02004' if different_state else '02003')
        if same_sector:
            original[SECTOR] = sector([original[SECTOR][p.offset:p.end] for p in parsed.items] + entries,
                                      [n.raw for n in parsed.nodes] + nodes)
        else:
            original[SECOND_SECTOR] = sector(entries, nodes)
        pit = pit_text()
        if different_state:
            variant = pit[pit.index('Variant {'):].replace('Name: "default"', 'Name: "city"', 1)
            pit = pit.replace('VariantCount: 1', 'VariantCount: 2') + variant
            second_ppd, _ = append_car_parking_polygon(original[PPD],
                [(-28., 0., -32.), (-23., 0., -32.), (-23., 0., -27.), (-28., 0., -27.)])
            original['prefab/test/second.ppd'] = second_ppd
            original['def/world/prefab.second.sii'] = DEFINITION.replace('prefab.02003', 'prefab.02004').replace('station.ppd', 'second.ppd').encode()
            original['def/data_context.sii'] = original['def/data_context.sii'].replace(b'target_data[]: prefab.02003', b'target_data[]: prefab.02003\n target_data[]: prefab.02004')
            original['prefab/test/station.pmd'] = b'Authored effective model identity'
            original['material/paint.tobj'] = b'Authored material identity'
        source = self.package('source.scs', original)
        mounted = [source]
        if baseline:
            alias = 'r9base'
            private = 'prefab/rtfix/r9base.ppd'
            base_sector = bytearray(original[SECTOR])
            for prefab in parse_sector(base_sector).prefabs:
                struct.pack_into('<Q', base_sector, prefab.offset + 57, token(alias))
            payload = {SECTOR: bytes(base_sector), private: original[PPD],
                       'def/world/prefab.r9base.sii': _alias_definition(DEFINITION[DEFINITION.index('prefab_model'):DEFINITION.rindex('}')], 'prefab.02003', alias, private),
                       DEF: b'SiiNunit\n{\n}\n',
                       'def/data_context.r9.sii': b'SiiNunit\n{\ndata_context : context.r9 { target_data[]: prefab.r9base\n tags[]: gas_station\n}\n}\n',
                       'prefab/rtfix/r9-unrelated.ppd': b'Authored unrelated baseline payload'}
            mounted.append(self.package('effective-r9.scs', payload))
        stack = ResourceStack(mounted)
        plans = []
        for index, uid in enumerate((100, 1100), 1):
            path = SECTOR if same_sector or index == 1 else SECOND_SECTOR
            descriptor = 'prefab/rtfix/r9base.ppd' if baseline else ('prefab/test/second.ppd' if different_state and index == 2 else PPD)
            config = {'schema_version': 2 if different_state else 1, 'processor': 'station_parking',
                      'station_id': f'station-{index}', 'map_name': 'Fixture Map', 'game_version': VERSION,
                      'method': 'painted_bays', 'sector': path, 'prefab_uid': hex(uid),
                      'model_geometry': 'prefab/test/station.pmg', 'mesh_materials': {'ground': ['asphalt'], 'paint': ['paint']},
                      'parameters': {}, 'fingerprints': {'source_archive': sha(source.path.read_bytes()),
                          'sector': sha(stack.read(path)), 'descriptor': sha(stack.read(descriptor)),
                          'model_geometry': sha(stack.read('prefab/test/station.pmg')), 'mesh': sha(self.mesh.encode())}}
            kwargs = {}
            if different_state:
                config['fingerprints'].update(model_definition=sha(stack.read('prefab/test/station.pmd')), mesh_state=sha(pit.encode()))
                config['material_resources'] = {'material/paint.tobj': sha(stack.read('material/paint.tobj'))}
                kwargs['mesh_state_text'] = pit
            report, resources = plan_station_parking(stack, config, self.mesh, map_package=str(source.path), game_version=VERSION, **kwargs)
            self.assertTrue(report['coverage']['complete'], report['coverage'])
            self.assertTrue(resources)
            plans.append((f'P{index:02}', report, resources))
        return stack, plans

    def compose(self, stack, plans):
        return compose_station_plans(stack, plans, batch_id='fixture-batch', map_name='Curated Stations', game_version=VERSION)

    def test_same_sector_keeps_both_station_aliases_and_all_other_bytes(self):
        stack, plans = self.fixture()
        untouched = deepcopy(plans)
        report, output = self.compose(stack, plans)
        baseline = stack.read(SECTOR)
        after = parse_sector(output[SECTOR])
        self.assertEqual([p.details['model'] for p in after.prefabs], [token(p[1]['private_alias']) for p in plans])
        ranges = report['changed_sectors'][0]['allowed_changed_byte_ranges']
        allowed = {index for start, end in ranges for index in range(start, end)}
        self.assertTrue(all(index in allowed for index, (a, b) in enumerate(zip(baseline, output[SECTOR])) if a != b))
        self.assertEqual(len(output[SECTOR]), len(baseline))
        self.assertEqual([n.raw for n in parse_sector(baseline).nodes], [n.raw for n in after.nodes])
        self.assertEqual(plans, untouched)
        self.assertEqual(report['station_count'], 2)
        self.assertFalse(report['in_game_verified'])
        self.assertEqual(len([path for path in output if path.endswith('.ppd')]), 2)

    def test_order_independent_reports_resources_and_multi_sector_composition(self):
        for same_sector in (True, False):
            with self.subTest(same_sector=same_sector):
                # Each fixture receives fresh package filenames.
                if self.packages:
                    for package in self.packages:
                        package.close()
                    self.packages.clear()
                stack, plans = self.fixture(same_sector=same_sector)
                result = self.compose(stack, plans)
                self.assertEqual(result, self.compose(stack, reversed(plans)))
                self.assertEqual(len(result[0]['changed_sectors']), 1 if same_sector else 2)

    def test_shared_model_different_ppd_and_placement_variant_remain_independent(self):
        stack, plans = self.fixture(different_state=True)
        self.assertEqual([p[1]['effective_model_state']['variant'] for p in plans], ['default', 'city'])
        self.assertNotEqual(plans[0][1]['configuration']['fingerprints']['descriptor'], plans[1][1]['configuration']['fingerprints']['descriptor'])
        report, output = self.compose(stack, plans)
        self.assertEqual(report['station_count'], 2)
        self.assertEqual(len([p for p in output if p.endswith('.ppd')]), 2)
        self.assertEqual([p.details['variant'] for p in parse_sector(output[SECTOR]).prefabs], [0, token('city')])

    def test_existing_r9_payload_remains_lower_dependency_and_sector_baseline_survives(self):
        stack, plans = self.fixture(baseline=True)
        before = {path: stack.read(path) for path in stack.resources}
        report, output = self.compose(stack, plans)
        self.assertEqual(set(output) & set(before), {SECTOR})
        self.assertNotIn('prefab/rtfix/r9base.ppd', output)
        self.assertNotIn('prefab/rtfix/r9-unrelated.ppd', output)
        self.assertEqual(before, {path: stack.read(path) for path in stack.resources})
        self.assertEqual(report['changed_sectors'][0]['source_sha256'], sha(before[SECTOR]))

    def test_partial_no_change_or_duplicate_site_is_rejected_atomically(self):
        stack, plans = self.fixture()
        for mutation in ('partial', 'blocked', 'empty', 'duplicate-site', 'duplicate-placement'):
            changed = deepcopy(plans)
            if mutation == 'partial':
                changed[1][1]['coverage']['complete'] = False
            elif mutation == 'blocked':
                changed[1][1]['coverage']['blockers'].append({'reason': 'fixture blocker'})
            elif mutation == 'empty':
                changed[1][2].clear()
            elif mutation == 'duplicate-site':
                changed[1] = ('P01', changed[1][1], changed[1][2])
            else:
                changed[1][1]['configuration']['prefab_uid'] = '0x64'
            frozen = deepcopy(changed)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.compose(stack, changed)
            self.assertEqual(changed, frozen)
        self.assertEqual(self.compose(stack, plans)[0]['station_count'], 2)

    def test_sector_drift_unexpected_bytes_false_patch_claim_and_wrong_alias_rejected(self):
        stack, plans = self.fixture()
        for mutation in ('source-hash', 'outside', 'inside', 'truncated', 'false-range', 'false-output-hash'):
            changed = deepcopy(plans)
            report, resources = changed[1][1:]
            if mutation == 'source-hash':
                report['configuration']['fingerprints']['sector'] = '0' * 64
            elif mutation == 'false-range':
                report['changed_sectors'][0]['allowed_changed_byte_range'] = [0, 8]
            elif mutation == 'false-output-hash':
                report['changed_sectors'][0]['output_sha256'] = '0' * 64
            else:
                sector_bytes = bytearray(resources[SECTOR])
                if mutation == 'truncated':
                    sector_bytes.pop()
                else:
                    index = 0 if mutation == 'outside' else report['changed_sectors'][0]['allowed_changed_byte_range'][0]
                    sector_bytes[index] ^= 1
                resources[SECTOR] = bytes(sector_bytes)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.compose(stack, changed)

    def test_different_effective_stack_and_model_material_drift_rejected(self):
        stack, plans = self.fixture(different_state=True)
        for path in (SECTOR, PPD, 'prefab/test/station.pmg', 'prefab/test/station.pmd', 'material/paint.tobj'):
            overlay = self.package('drift-' + path.rsplit('/', 1)[-1] + '.scs', {path: stack.read(path) + b'drift'})
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.compose(ResourceStack([*stack.packages, overlay]), plans)

    def test_new_resources_cannot_overwrite_baseline_or_smuggle_unexpected_payload(self):
        stack, plans = self.fixture()
        changed = deepcopy(plans)
        changed[1][2]['map/usa/unexpected.base'] = b'unexpected'
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            self.compose(stack, changed)
        private = next(path for path in plans[1][2] if path.endswith('.ppd'))
        overlay = self.package('namespace-collision.scs', {private: b'existing payload'})
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            self.compose(ResourceStack([*stack.packages, overlay]), plans)

    def test_conflicting_context_resource_and_duplicate_alias_rejected(self):
        stack, plans = self.fixture()
        changed = deepcopy(plans)
        first_path = changed[0][1]['context_preservation']['generated_resource']
        second_path = changed[1][1]['context_preservation']['generated_resource']
        changed[1][2][first_path] = changed[1][2].pop(second_path)
        changed[1][1]['context_preservation']['generated_resource'] = first_path
        with self.assertRaisesRegex(ValueError, 'conflicting nonsector'):
            self.compose(stack, changed)
        changed = deepcopy(plans)
        changed[1][1]['private_alias'] = changed[0][1]['private_alias']
        with self.assertRaisesRegex(ValueError, 'alias collision'):
            self.compose(stack, changed)

    def test_private_ppd_cannot_change_prior_bytes_or_native_car_parameters(self):
        stack, plans = self.fixture()
        for mutation in ('source-record', 'car-flags'):
            changed = deepcopy(plans)
            private = next(path for path in changed[1][2] if path.endswith('.ppd'))
            ppd = bytearray(changed[1][2][private])
            header = struct.unpack_from('<24I', ppd)
            index = 96 if mutation == 'source-record' else header[22] - 48 + 24
            ppd[index] ^= 1
            changed[1][2][private] = bytes(ppd)
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'source-preserving native car append'):
                self.compose(stack, changed)

    def test_effective_input_report_or_context_target_cannot_drift(self):
        stack, plans = self.fixture(different_state=True)
        for mutation in ('effective-input', 'context-target', 'context-path'):
            changed = deepcopy(plans)
            report, output = changed[1][1:]
            if mutation == 'effective-input':
                report['effective_inputs'][0]['sha256'] = '0' * 64
            elif mutation == 'context-path':
                report['context_preservation']['generated_resource'] = []
            else:
                path = report['context_preservation']['generated_resource']
                output[path] = output[path].replace(('prefab.' + report['private_alias']).encode(), b'prefab.02003')
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.compose(stack, changed)

    def test_distinct_source_map_names_are_allowed_and_game_mismatch_rejected(self):
        stack, plans = self.fixture()
        plans[1][1]['configuration']['map_name'] = 'Second Source Map'
        plans[1][1]['map_name'] = 'Second Source Map'
        self.assertEqual(self.compose(stack, plans)[0]['sites'][1]['map_name'], 'Second Source Map')
        plans[1][1]['configuration']['game_version'] = '1.61.3.19'
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            self.compose(stack, plans)


class BatchManifestTests(unittest.TestCase):
    def test_stable_explicit_site_order_and_no_mutation(self):
        original = manifest()
        reviewed = validate_manifest(original)
        self.assertEqual([row['site_id'] for row in reviewed['stations']], ['P01', 'P02'])
        self.assertEqual([row['site_id'] for row in original['stations']], ['P02', 'P01'])
        reviewed['stations'][0]['mesh'] = 'changed'
        self.assertEqual(original['stations'][1]['mesh'], 'station.pim')

    def test_unknown_duplicate_invalid_and_unbounded_manifests_rejected(self):
        for mutation in ('unknown', 'empty', 'too-many', 'duplicate-id', 'duplicate-config', 'invalid-id', 'source-path', 'missing-mesh'):
            changed = manifest()
            if mutation == 'unknown':
                changed['discover'] = True
            elif mutation == 'empty':
                changed['stations'] = []
            elif mutation == 'too-many':
                changed['stations'] *= 33
            elif mutation == 'duplicate-id':
                changed['stations'][1]['site_id'] = 'P02'
            elif mutation == 'duplicate-config':
                changed['stations'][1]['config'] = 'second.json'
            elif mutation == 'invalid-id':
                changed['stations'][1]['site_id'] = 'P00'
            elif mutation == 'source-path':
                changed['stations'][1]['source_package'] = '../source.scs'
            else:
                del changed['stations'][1]['mesh']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_manifest(changed)

    def test_explicit_absolute_and_shared_mesh_paths_are_workflow_owned(self):
        reviewed = manifest()
        reviewed['stations'][0]['mesh'] = '/shared/read-only/station.pim'
        reviewed['stations'][1]['mesh'] = '/shared/read-only/station.pim'
        reviewed['stations'][0]['config'] = '/reviewed/second.json'
        self.assertEqual(validate_manifest(reviewed)['stations'][1]['config'], '/reviewed/second.json')
