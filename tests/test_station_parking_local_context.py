"""Bounded external-object checks use authored fixtures, never game assets."""
from copy import deepcopy
import math
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile
from types import SimpleNamespace

from ats_road_trip.package import Package, ResourceStack
from ats_road_trip.ppd import inspect_ppd
from ats_road_trip.station_parking.local_context import (
    evaluate_local_context, load_local_context,
)
from tests.test_bulk_fuel import PPD, SECTOR, resources as fuel_resources
from tests.test_station_parking import source_resources
from tests.test_station_geometry import station_descriptor


def non_gas_context_resources():
    """Use station UI polygons with two control nodes and no GAS locator."""
    contents = source_resources()
    target = fuel_resources(spawns=[])[PPD]
    header = list(struct.unpack_from('<24I', target))
    mapped = station_descriptor()
    mapped_header = struct.unpack_from('<24I', mapped)
    map_records = mapped[mapped_header[20]:mapped_header[21]]
    insertion = header[20]
    header[8] = mapped_header[8]
    for index in (21, 22, 23):
        header[index] += len(map_records)
    contents[PPD] = (struct.pack('<24I', *header) + target[96:insertion]
                      + map_records + target[insertion:])
    return contents


class LocalContextTests(unittest.TestCase):
    def test_footprint_and_approach_reject_recognized_external_proxy(self):
        context = {'objects': [
            {'id': 'near-building', 'kind': 4,
             'classification': 'obstacle_proxy',
             'extent_status': 'declared_conservative_proxy',
             'geometry_xz': [[4, -1], [6, -1], [6, 1], [4, 1]]},
        ], 'unassessed_objects': [], 'limits': ['fixture limit']}
        original = deepcopy(context)
        candidate = {'polygon_xz': [[0, 0], [2, 0], [2, 2], [0, 2]],
                     'approach_xz': [[3, 0], [5, 0], [5, 2], [3, 2]]}
        before = deepcopy(candidate)
        report = evaluate_local_context(candidate, context, margin=0.5)
        self.assertEqual(report['rejection_reasons'], ['intersects_external_map_object_proxy'])
        self.assertEqual(report['external_object_conflicts'][0]['regions'], ['approach'])
        self.assertEqual(candidate, before)
        self.assertEqual(context, original)

    def test_unknown_types_and_unknown_extents_are_disclosed_not_assumed_clear(self):
        context = {'objects': [
            {'id': 'unknown-shape', 'kind': 0x24, 'classification': 'unknown'},
            {'id': 'unknown-bounds', 'kind': 4, 'classification': 'obstacle_proxy',
             'extent_status': 'unknown'},
        ], 'unassessed_objects': [{'id': 'unresolved-prefab', 'kind': 4,
                                   'reason': 'effective_prefab_definition_unresolved'}],
           'unknown_item_kind_counts': {'0x24': 3}, 'limits': ['bounded only']}
        candidate = {'polygon_xz': [[0, 0], [2, 0], [2, 2], [0, 2]]}
        report = evaluate_local_context(candidate, context)
        self.assertEqual(report['rejection_reasons'], [])
        self.assertEqual(report['external_objects_checked'], 0)
        self.assertEqual(len(report['external_objects_unassessed']), 3)
        self.assertEqual(report['unknown_item_kind_counts'], {'0x24': 3})
        self.assertEqual(report['local_context_limits'], ['bounded only'])

    def test_extractor_transforms_neighbor_ui_polygon_from_effective_placement(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / 'authored-fixture.scs'
            contents = non_gas_context_resources()
            self.assertEqual(inspect_ppd(contents[PPD])['spawns'], [])
            with zipfile.ZipFile(archive_path, 'w') as archive:
                for path, data in contents.items():
                    archive.writestr(path, data)
            package = Package(archive_path)
            try:
                stack = ResourceStack([package])
                sector = contents[SECTOR]
                original = bytes(sector)
                context = load_local_context(stack, {SECTOR: sector}, 0x999,
                                             (100., 200.), search_radius=30.)
                self.assertTrue(context['objects'])
                self.assertTrue(context['descriptor_inputs'][PPD]['sha256'])
                self.assertEqual(context['sector_inputs'][0]['path'], SECTOR)
                self.assertEqual({row['path'] for row in context['source_resources']},
                                 {SECTOR, PPD, 'def/world/prefab.test.sii'})
                self.assertEqual(contents[SECTOR], original)
                self.assertTrue(all(row['classification'] == 'obstacle_proxy'
                                    and row['extent_status'] == 'declared_conservative_proxy'
                                    for row in context['objects']))
                # The fixture prefab's map geometry is rotated and translated by
                # its placed control nodes; it is not returned in source PPD space.
                from ats_road_trip.station_parking.local_context import _local_polygons
                local = _local_polygons(contents[PPD])
                local_building = next(p for p in local if p['color'] == 2)
                source_vertices = {tuple((p[0], p[2])) for p in local_building['vertices']}
                emitted_vertices = {tuple(p) for row in context['objects'] for p in row['geometry_xz']}
                self.assertFalse(source_vertices & emitted_vertices)
                self.assertTrue(all(math.isfinite(v) for row in context['objects']
                                    for point in row['geometry_xz'] for v in point))
                self.assertTrue(any('Generic map-item bounds have unknown semantics'
                                    in limit for limit in context['limits']))
            finally:
                package.close()

    def test_bad_candidate_geometry_fails_closed(self):
        context = {'objects': []}
        with self.assertRaises(ValueError):
            evaluate_local_context({'polygon_xz': [[0, 0], [1, 1], [0, 1], [1, 0]]}, context)
        with self.assertRaises(ValueError):
            evaluate_local_context({'polygon_xz': [[0, 0], [1, 0], [1, 1], [0, 1]],
                                    'approach_xz': [[0, 0], [math.inf, 0], [1, 1]]}, context)

    def test_sector_scope_and_generic_item_extent_are_never_guessed(self):
        with self.assertRaises(ValueError):
            load_local_context(None, {}, 1, (0, 0), max_sectors=26)
        with self.assertRaises(ValueError):
            load_local_context(None, {'../bad.base': b''}, 1, (0, 0))

    def test_conflicting_base_and_aux_node_uids_fail_closed(self):
        contents = source_resources()
        sector = contents[SECTOR]
        from ats_road_trip.map_sector import parse_sector
        parsed = parse_sector(sector)
        changed = bytearray(sector)
        first_node = parsed.nodes[0]
        struct.pack_into('<i', changed, first_node.offset + 8,
                         round(first_node.position[0] * 256) + 1)
        with self.assertRaisesRegex(ValueError, 'Conflicting duplicate node UID'):
            load_local_context(SimpleNamespace(resources={}), {SECTOR: sector,
                SECTOR.replace('.base', '.aux'): bytes(changed)}, 0x999, (100, 200))


if __name__ == '__main__':
    unittest.main()
