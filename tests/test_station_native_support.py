"""Original authored fixtures for bounded functional station parking support."""
from pathlib import Path
import struct
import tempfile
import unittest

from ats_road_trip.local_fuel import token
from ats_road_trip.map_sector import parse_sector
from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.station_parking.native_support import classify_native_car_parking
from tests.test_bulk_fuel import PPD, SECTOR
from tests.test_map_sector import item, refs, sector
from tests.test_rest_stops import ACTIONS, DEFINITION, descriptor, placement, standalone, map_node
from tests.test_station_parking import source_resources


class NativeStationSupportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.packages = []
        self.addCleanup(lambda: [p.close() for p in self.packages])
        self.number = 0

    def classify(self, contents=None, *, cache=None):
        self.number += 1
        root = Path(self.temp.name)/str(self.number)
        for path, data in (contents or source_resources()).items():
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        package = Package(root)
        self.packages.append(package)
        stack = ResourceStack([package])
        return classify_native_car_parking(stack, SECTOR, 100, cache=cache)

    def replace_action(self, contents, action):
        raw = bytearray(contents[PPD])
        header = struct.unpack_from('<24I', raw)
        for i in range(header[9]):
            struct.pack_into('<Q', raw, header[21]+48*i+4, token(action))
        contents[PPD] = bytes(raw)

    def add_standalone(self, contents, *, x=100., z=185., path=SECTOR, uid=500, height=5., **kwargs):
        raw, ns = standalone(uid, x, z, **kwargs)
        # These synthetic stations stand 5m above world zero.
        lifted = []
        for node in ns:
            b = bytearray(node)
            struct.pack_into('<i', b, 12, round(height*256))
            lifted.append(bytes(b))
        parsed = parse_sector(contents[path]) if path in contents else None
        entries = [contents[path][i.offset:i.end] for i in parsed.items] if parsed else []
        nodes = [n.raw for n in parsed.nodes] if parsed else []
        contents[path] = sector(entries+[raw], nodes+lifted)

    def test_truck_rest_and_fuel_do_not_establish_car_parking(self):
        report = self.classify()
        self.assertEqual(report['state'], 'absent', report)
        self.assertFalse(report['evidence'])
        self.assertEqual(len(report['scope']['sector_paths']), 1)

    def test_original_car_only_action_belongs_to_whole_facility(self):
        contents = source_resources()
        self.replace_action(contents, 'parking_car')
        report = self.classify(contents)
        self.assertEqual(report['state'], 'present', report)
        self.assertEqual(report['evidence'][0]['relation'], 'selected_placement')

    def test_custom_mixed_car_action_counts_even_without_car_only_icon(self):
        contents = source_resources()
        contents['def/world/trigger_action.custom.sii'] = b'''SiiNunit
{
trigger_action : trig_action.custom_rest {
 command: hud_activate
 num_params[]: 3.0
 str_params[]: truck
 str_params[]: bus
 str_params[]: car
}
}
'''
        self.replace_action(contents, 'custom_rest')
        report = self.classify(contents)
        self.assertEqual(report['state'], 'present', report)
        self.assertEqual(report['evidence'][0]['vehicles'], ['bus', 'car', 'truck'])

    def test_non_rest_hud_action_and_icon_name_do_not_count(self):
        contents = source_resources()
        contents['def/world/trigger_action.sii'] = ACTIONS.replace(b'num_params[]: 3\n str_params[]: "car"',
                                                                b'num_params[]: 2\n str_params[]: "car"')
        self.replace_action(contents, 'parking_car')
        self.assertEqual(self.classify(contents)['state'], 'absent')

    def test_unresolved_or_unsafe_action_does_not_become_absent(self):
        for action, data in [('missing_rest', ACTIONS), ('parking_car', ACTIONS.replace(
                b'num_params[]: 3\n str_params[]: "car"', b'num_params[]: 3\n num_params[]: 1\n str_params[]: "car"'))]:
            with self.subTest(action=action):
                contents = source_resources()
                contents['def/world/trigger_action.sii'] = data
                self.replace_action(contents, action)
                report = self.classify(contents)
                self.assertEqual(report['state'], 'unknown', report)
                self.assertIn('rest_action_unresolved', str(report['reasons']))

    def test_associated_standalone_across_adjacent_aux_sector_counts(self):
        contents = source_resources()
        path = 'map/usa/sec+0001+0000.aux'
        self.add_standalone(contents, path=path)
        report = self.classify(contents)
        self.assertEqual(report['state'], 'present', report)
        self.assertEqual(report['evidence'][0]['path'], path)
        self.assertEqual(report['evidence'][0]['relation'], 'contained_in_station_lot')

    def test_unrelated_nearby_standalone_is_not_facility_support(self):
        contents = source_resources()
        self.add_standalone(contents, x=200., z=200.)
        report = self.classify(contents)
        self.assertEqual(report['state'], 'absent', report)

    def test_partial_overlap_is_unknown_instead_of_broad_radius_exemption(self):
        contents = source_resources()
        self.add_standalone(contents, x=130., z=188.)
        report = self.classify(contents)
        self.assertEqual(report['state'], 'unknown', report)
        self.assertIn('standalone_facility_association_ambiguous', str(report['reasons']))

    def test_explicit_slave_relation_associates_standalone_without_radius(self):
        contents = source_resources()
        data = contents[SECTOR]
        parsed = parse_sector(data)
        target = parsed.prefabs[0]
        changed = item(4, target.uid, struct.pack('<QQ', target.details['model'], 0)+refs()
                       +refs(*target.details['nodes'])+refs(*target.details['slaves'], 500)
                       +struct.pack('<QH', 0, target.details['origin'])
                       +bytes(len(target.details['nodes'])*12+8))
        contents[SECTOR] = sector([changed]+[data[i.offset:i.end] for i in parsed.items if i.uid != target.uid],
                                  [n.raw for n in parsed.nodes])
        self.add_standalone(contents, x=200., z=200.)
        report = self.classify(contents)
        self.assertEqual(report['state'], 'present', report)
        self.assertEqual(report['evidence'][0]['relation'], 'explicit_slave')

    def test_disabled_and_custom_parameter_standalones_are_not_assumed_functional(self):
        for kwargs, state in [({'flags': 0x1000c}, 'absent'), ({'flags': 0x08}, 'absent'),
                              ({'custom': True}, 'unknown')]:
            contents = source_resources()
            self.add_standalone(contents, **kwargs)
            report = self.classify(contents)
            self.assertEqual(report['state'], state, report)

    def test_standalone_custom_override_cannot_hide_rest_under_nonrest_hud_preset(self):
        contents = source_resources()
        contents['def/world/trigger_action.other.sii'] = b'SiiNunit\n{\ntrigger_action : trig_action.other_hud {\n command: hud_activate\n num_params[]: 2\n str_params[]: car\n}\n}\n'
        self.add_standalone(contents, action='other_hud', custom=True)
        report = self.classify(contents)
        self.assertEqual(report['state'], 'unknown', report)

    def test_missing_or_invalid_boundary_evidence_is_unknown(self):
        contents = source_resources()
        contents['map/usa/sec+0001+0000.base'] = b'invalid sector'
        report = self.classify(contents)
        self.assertEqual(report['state'], 'unknown', report)
        self.assertIn('sector_unresolved', str(report['reasons']))

    def test_other_station_and_unrelated_unresolved_descriptor_do_not_count(self):
        for missing in (False, True):
            contents = source_resources()
            raw, ns = placement(600, 300., 300.)
            parsed = parse_sector(contents[SECTOR])
            contents[SECTOR] = sector([contents[SECTOR][i.offset:i.end] for i in parsed.items]+[raw],
                                      [n.raw for n in parsed.nodes]+ns)
            if not missing:
                contents['def/world/prefab.rest.sii'] = DEFINITION
                contents['prefab/test/rest.ppd'] = descriptor([('parking_car', [(0.,0.),(10.,0.),(10.,10.),(0.,10.)])])
            report = self.classify(contents)
            self.assertEqual(report['state'], 'absent', report)

    def test_distant_bad_flags_and_missing_owner_links_do_not_poison_facility(self):
        contents = source_resources()
        self.add_standalone(contents, x=400., z=400., flags=0x80000000)
        parsed = parse_sector(contents[SECTOR])
        ns = []
        for node in parsed.nodes:
            raw = bytearray(node.raw)
            if node.forward == 500:
                struct.pack_into('<Q', raw, 44, 0)
            ns.append(bytes(raw))
        contents[SECTOR] = sector([contents[SECTOR][i.offset:i.end] for i in parsed.items], ns)
        self.assertEqual(self.classify(contents)['state'], 'absent')

    def test_standalone_at_another_elevation_does_not_serve_station(self):
        contents = source_resources()
        self.add_standalone(contents, height=50.)
        self.assertEqual(self.classify(contents)['state'], 'absent')

    def test_known_nonrest_standalone_does_not_create_parking_uncertainty(self):
        contents = source_resources()
        contents['def/world/trigger_action.sound.sii'] = b'SiiNunit\n{\ntrigger_action : trig_action.sound {\n command: sound\n}\n}\n'
        self.add_standalone(contents, x=130., z=188., action='sound', flags=0x80000000)
        self.assertEqual(self.classify(contents)['state'], 'absent')

    def test_compound_is_unknown_only_when_its_anchor_belongs_to_lot(self):
        for x, z, expected in [(400., 400., 'absent'), (100., 185., 'unknown')]:
            contents = source_resources()
            child, child_nodes = standalone(510, 0., 0.)
            compound = item(0x28, 800, struct.pack('<Q', 900)+struct.pack('<I', 1)+child
                            +struct.pack('<I', len(child_nodes))+b''.join(child_nodes))
            parsed = parse_sector(contents[SECTOR])
            contents[SECTOR] = sector([contents[SECTOR][i.offset:i.end] for i in parsed.items]+[compound],
                                      [n.raw for n in parsed.nodes]+[map_node(900, x, z, 800)])
            report = self.classify(contents)
            self.assertEqual(report['state'], expected, report)

    def test_generated_stack_is_rejected_and_shared_cache_is_stack_specific(self):
        cache = {}
        self.assertEqual(self.classify(cache=cache)['state'], 'absent')
        contents = source_resources()
        self.replace_action(contents, 'parking_car')
        self.assertEqual(self.classify(contents, cache=cache)['state'], 'present')
        contents['prefab/rtfix/old.ppd'] = b'old generated overlay'
        report = self.classify(contents)
        self.assertEqual(report['state'], 'unknown')
        self.assertIn('generated_fixes_in_original_stack', str(report['reasons']))


if __name__ == '__main__':
    unittest.main()
