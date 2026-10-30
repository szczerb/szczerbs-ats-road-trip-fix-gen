"""Explainable whole-facility policy for realistic added car fueling.

Reviewed families use original descriptor/model/state pins. Contextual yard
inferences combine a real Company edge, semantic layout and pump containment;
company names and mere proximity never decide suitability. UI polygons are
map proxies, not access-law, fuel-inventory or collision proofs.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math

# Versioned local evidence: SELECTIVE_CAR_FUELING_FEEDBACK_2026_10_21.md and
# SELECTIVE_CAR_FUELING.md. These are reusable resource families, never sites.
_REVIEWED = {
    ('/prefab/gas/nm_gas_station1_chemron.pmd', '3d986bd488fb034f21043540bf9cca3f5966503d8715c6e70612bb722dea5fca'):
        ('public_station', 92136531712),
    ('/prefab/gas/nm_truckstop1_depot.pmd', '0e7954cd155d6019d04c70dd73623ce7407a9378f742003a2a17026a5f400519'):
        ('public_truck_stop', 97903579674243),
    ('/prefab/gas/nm_gas_station1_chemron.pmd', 'e0a9084f767216f1611b30ec1f8729dd00a490ad520fc2002072527b5edc4d8b'):
        ('public_station', 92136531712),
    ('/prefab/empresas/cedis/castores1.pmd', 'b130fdfb51503158d55b06cae22a7f603f23269f1cedf5ea50c83236cdb1d79d'):
        ('logistics_yard', 92136531712),
}
_GENERIC_TRIGGER = '/prefab/gas/us_gas_station_trigger_only.pmd'
_FIELD_LOT = '/prefab/depots/custom/us_custom_depot_field.pmd'
_FIELD_PPD_SHA256 = '6387b090f84b102ef80b7e2c64c0590926ce6778b638cd2e517566a26c435992'
_FIELD_VARIANT = 30421486  # semantic model variant token: field
_FIELD_APPROACH_DEPTH = (0.5, 15.0)
_FIELD_APPROACH_HALF_WIDTH = 3.0


@dataclass(frozen=True)
class CompanyLotEvidence:
    company_uid: int
    prefab_uid: int
    model_desc: str
    descriptor_sha256: str
    matched_spawn_indices: tuple[int, ...]
    polygon_ids: tuple[int, ...]
    evidence: str
    variant: int | None = None
    parts: tuple[int, ...] = ()
    additional_parts: tuple[str, ...] = ()
    relationship: str = 'inside_accessible_polygon'
    provider: str = ''
    entrance_world_xyz: tuple[float, ...] = ()
    approach_axis_xz: tuple[float, ...] = ()
    pump_measurements: tuple[tuple, ...] = ()


@dataclass(frozen=True)
class FacilityContext:
    company_lots: tuple[CompanyLotEvidence, ...] = ()
    unavailable_evidence: tuple[str, ...] = ()
    native_car_locator_count: int = 0


def classify_facility_groups(config, *, descriptor, descriptor_sha256, model_desc,
                             variant, parts, additional_parts, gas_trucks,
                             company_uids=(), garage_indices=(), context=None,
                             reviewed_rule_drift=False):
    """Use accepted whole stations, graph facilities and explicit uncertainty."""
    context = context or FacilityContext()
    reviewed = _REVIEWED.get((model_desc, descriptor_sha256))
    indices = {spawn['index'] for spawn in gas_trucks}
    field_lots = [lot for lot in context.company_lots
                  if lot.model_desc == _FIELD_LOT and indices <= set(lot.matched_spawn_indices)
                  and lot.descriptor_sha256 == _FIELD_PPD_SHA256 and lot.variant == _FIELD_VARIANT
                  and not lot.parts and not lot.additional_parts]
    facility, confidence, provisional = 'uncertain', 'low', True
    reason = 'Unreviewed facility; preserve plausible station coverage under the configured provisional policy'
    evidence = 'Unknown: public/private suitability; no ownership or diesel-only claim'
    if reviewed_rule_drift:
        reason = 'Reviewed rule source/state drift; stale suitability rule not applied'
        evidence = 'Observed locally: descriptor/model/state no longer matches the supplied reviewed rule'
    elif garage_indices:
        facility, confidence, provisional = 'truck_garage', 'high', False
        reason = 'Whole-facility truck-garage policy excludes added car fueling'
        evidence = 'Observed locally: actual garage FuelPump item kind 0x23; Documented: accepted garage exclusion, 2026-10-21'
    elif reviewed and reviewed[1] == variant and not parts and not additional_parts:
        if reviewed[0] != 'logistics_yard' or company_uids:
            facility, confidence, provisional = reviewed[0], 'high', False
            if facility == 'logistics_yard':
                confidence = 'medium'
                reason = 'Reviewed distribution-yard model and same-parent Company: omit added car fueling'
                evidence = 'Observed locally: source-pinned Castores lot/fence/logistics signage; Documented: accepted whole-facility exclusion, 2026-10-21'
            else:
                reason = 'Reviewed public facility: enable all original truck fuel groups while retaining native cars'
                evidence = 'Documented: accepted whole-station gameplay suitability, 2026-10-21; observed source model/descriptor/state pins match'
    elif model_desc == _GENERIC_TRIGGER and field_lots:
        facility, confidence, provisional = 'agricultural_equipment', 'low', True
        if all(lot.relationship == 'inside_accessible_polygon' for lot in field_lots):
            reason = 'Generic fuel trigger lies inside a source-pinned Company field-depot map polygon; provisionally treat as agricultural/equipment supply'
        else:
            reason = 'Generic fuel trigger occupies the bounded entrance approach of a source-pinned Company field-depot layout; provisionally omit agricultural/equipment car additions'
        evidence = 'Observed locally: actual Company-to-field-prefab edge, exact source layout/state and measured geometry; Documented: user ranch observation supports this narrow inference. This is not containment/ownership/diesel proof'
    selected = facility in ('public_station', 'public_truck_stop') or (facility == 'uncertain' and config.unknown == 'include')
    lots = [{'company_uid': hex(lot.company_uid), 'prefab_uid': hex(lot.prefab_uid),
             'model_desc': lot.model_desc, 'descriptor_sha256': lot.descriptor_sha256,
             'matched_spawn_indices': list(lot.matched_spawn_indices),
             'polygon_ids': list(lot.polygon_ids), 'evidence': lot.evidence,
             'variant': lot.variant, 'parts': list(lot.parts), 'additional_parts': list(lot.additional_parts),
             'relationship': lot.relationship, 'provider': lot.provider,
             'entrance_world_xyz': list(lot.entrance_world_xyz), 'approach_axis_xz': list(lot.approach_axis_xz),
             'pump_measurements': [{'spawn_index': row[0], 'depth_before_entrance': row[1],
                                    'lateral_offset': row[2], 'height_delta': row[3]} for row in lot.pump_measurements],
             'approach_bounds': {'depth_before_entrance': list(_FIELD_APPROACH_DEPTH),
                                 'absolute_lateral_max': _FIELD_APPROACH_HALF_WIDTH, 'height_delta_max': 2.0}} for lot in field_lots]
    return [{'spawn_index': spawn['index'],
             'role': 'public_car' if facility.startswith('public_') else 'uncertain' if facility == 'uncertain' else 'fleet_yard',
             'facility_class': facility, 'confidence': confidence, 'provisional': provisional,
             'reason': reason, 'evidence': evidence, 'selected_for_addition': selected,
             'decision': 'include' if selected else 'skip', 'rule_id': None,
             'same_parent_company_uids': [hex(uid) for uid in company_uids],
             'contextual_company_lots': lots,
             'context_evidence_unavailable': list(context.unavailable_evidence),
             'native_car_locator_count': context.native_car_locator_count,
             'reviewed_rule_drift': reviewed_rule_drift} for spawn in gas_trucks]


def field_approach_measurements(entrance, inner_control, pumps):
    """Measure a narrow finite entrance corridor, without asserting lot ownership.

    The reviewed custom-field layout defines the entrance/inner control order.
    Source/state pins must be checked by the caller before using this inference.
    """
    values = (*entrance, *inner_control, *(value for point in pumps.values() for value in point))
    if not all(isinstance(value, (int,float)) and not isinstance(value,bool) and math.isfinite(value) for value in values):
        raise ValueError('Nonfinite field approach geometry')
    dx, dz = inner_control[0]-entrance[0], inner_control[2]-entrance[2]
    length = math.hypot(dx,dz)
    if not 9.9 <= length <= 10.1:
        raise ValueError('Reviewed field control span drift')
    axis = (dx/length,dz/length)
    matches, measurements = [], []
    for index, point in sorted(pumps.items()):
        x,z = point[0]-entrance[0],point[2]-entrance[2]
        depth = -(x*axis[0]+z*axis[1])
        lateral = x*axis[1]-z*axis[0]
        height = point[1]-entrance[1]
        measurements.append((index,depth,lateral,height))
        if (_FIELD_APPROACH_DEPTH[0] <= depth <= _FIELD_APPROACH_DEPTH[1]
                and abs(lateral) <= _FIELD_APPROACH_HALF_WIDTH and abs(height) <= 2.0):
            matches.append(index)
    return tuple(matches),tuple(measurements),axis


class FacilityContextIndex:
    """Use the already inspected source/halo graph; never scan the whole world."""
    def __init__(self, stack, items, definitions, node_for):
        self.stack, self.items, self.definitions, self.node_for = stack, items, definitions, node_for
        self.companies = []
        self.geometry = {}
        for uid, (path, item) in items.items():
            if item.kind != 6 or item.details['prefab'] not in items:
                continue
            parent_path, parent = items[item.details['prefab']]
            if parent.kind != 4:
                continue
            entry = definitions.get(parent.details['model'])
            if entry is None or entry[0].one('model_desc', '') != _FIELD_LOT:
                continue
            self.companies.append((path, item, parent_path, parent, entry[0]))
        descriptors = {unit.one('prefab_desc', '').lstrip('/') for _,_,_,_,unit in self.companies}
        for package in stack.packages:
            names = [name for name in descriptors if name in stack.resources and stack.resources[name][0] is package]
            if names:
                from ..archive import Archive
                package.prefetch(names, disk_cache=Archive._scratch_root().parent / 'package-cache' / hashlib.sha256(str(package.path).encode()).hexdigest()[:12])

    def for_station(self, *, model_desc, gas_trucks, mapping, native_car_locator_count):
        if model_desc != _GENERIC_TRIGGER:
            return FacilityContext(native_car_locator_count=native_car_locator_count)
        from ..station_parking.local_context import _local_polygons
        from ..rest_stops import _placed_vertices
        from ..station_parking.geometry import _contains
        pumps = {}
        for spawn in gas_trucks:
            path, service = self.items[mapping[spawn['index']]]
            pumps[spawn['index']] = self.node_for(service.details['node'], path).position
        lots, missing = [], []
        for path, company, parent_path, parent, unit in self.companies:
            descriptor = unit.one('prefab_desc', '').lstrip('/')
            try:
                anchor = self.node_for(company.details['node'], path).position
                if not any(math.hypot(point[0] - anchor[0], point[2] - anchor[2]) <= 150 for point in pumps.values()):
                    continue
                if descriptor not in self.geometry:
                    data = self.stack.read(descriptor)
                    from ..ppd import upgrade_fuel_descriptor
                    supported, _ = upgrade_fuel_descriptor(data)
                    self.geometry[descriptor] = (data, supported, _local_polygons(supported))
                data, supported, polygons = self.geometry[descriptor]
                if (hashlib.sha256(data).hexdigest() != _FIELD_PPD_SHA256
                        or parent.details['variant'] != _FIELD_VARIANT
                        or parent.details['parts'] or unit.values('additional_parts')):
                    missing.append(f'{descriptor}: reviewed field source/state drift')
                    continue
                nodes = {uid:self.node_for(uid, parent_path) for uid in parent.details['nodes']}
                contained, ids = set(), set()
                for polygon in polygons:
                    if polygon['color'] != 1:
                        continue
                    world = _placed_vertices(supported, parent, nodes, polygon['vertices'])
                    xz = world
                    for index, point in pumps.items():
                        if _contains((point[0], point[2]), xz):
                            contained.add(index); ids.add(polygon['id'])
                from ..fuel_matching import _control_positions
                local_controls = list(_control_positions(supported))
                control_xz = _placed_vertices(supported, parent, nodes, local_controls)
                refs, origin = parent.details['nodes'], parent.details['origin']
                controls = [(point[0], nodes[refs[(index-origin) % len(refs)]].position[1], point[1])
                            for index, point in enumerate(control_xz)]
                corridor, measurements, axis = field_approach_measurements(controls[0], controls[1], pumps)
                if contained or corridor:
                    relationship = ('inside_accessible_polygon' if set(pumps) <= contained
                                    else 'bounded_entrance_corridor')
                    eligible = contained if relationship == 'inside_accessible_polygon' else set(corridor)
                    lots.append(CompanyLotEvidence(company.uid, parent.uid, unit.one('model_desc'),
                        hashlib.sha256(data).hexdigest(), tuple(sorted(eligible)), tuple(sorted(ids)),
                        'Observed locally: real Company/field-layout relationship and measured map-proxy geometry; not collision/access-law proof',
                        variant=parent.details['variant'], parts=tuple(parent.details['parts']),
                        additional_parts=unit.values('additional_parts'), relationship=relationship,
                        provider=str(self.stack.resources[descriptor][0].path),
                        entrance_world_xyz=tuple(controls[0]), approach_axis_xz=axis,
                        pump_measurements=measurements))
            except (ValueError, KeyError, IndexError) as exc:
                missing.append(f'{descriptor}: {exc}')
        return FacilityContext(tuple(lots), tuple(sorted(set(missing))), native_car_locator_count)
