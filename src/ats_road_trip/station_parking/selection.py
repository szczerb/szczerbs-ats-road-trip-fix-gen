"""Explainable, bounded access checks and ranking for schema-2 proposals.

UI polygons, pump radii and navigation corridors are conservative proxies.
These checks do not simulate a vehicle path or establish runtime activation.
"""
from __future__ import annotations

from copy import deepcopy
import math

from .geometry import _within, _xz
from ..rest_stops import polygon_distance


def _center(polygon):
    return tuple(sum(p[i] for p in polygon) / len(polygon) for i in (0, 1))


def _approaches(candidate, depth):
    if candidate.get('approach_xz'):
        return [deepcopy(candidate['approach_xz'])]
    direction = candidate.get('direction_xz')
    if direction is None or len(direction) != 2:
        raise ValueError('Candidate requires an approach or a bay direction')
    dx, dz = map(float, direction)
    length = math.hypot(dx, dz)
    if not math.isfinite(length) or length <= 1e-9:
        raise ValueError('Bay direction must be finite and nonzero')
    dx, dz = dx / length, dz / length
    if dx < -1e-12 or (abs(dx) <= 1e-12 and dz < 0):
        dx, dz = -dx, -dz
    nx, nz = -dz, dx
    polygon = candidate['polygon_xz']
    along = [x * dx + z * dz for x, z in polygon]
    across = [x * nx + z * nz for x, z in polygon]
    result = []
    for start, end in [(min(along) - depth, min(along)),
                       (max(along), max(along) + depth)]:
        result.append([[s * dx + t * nx, s * dz + t * nz]
                       for s, t in [(start, min(across)), (end, min(across)),
                                    (end, max(across)), (start, max(across))]])
    return sorted(result, key=lambda points: tuple(round(v, 9) for p in sorted(points) for v in p))


def evaluate_access(candidate, geometry, mesh, *, ground, paint,
                    pump_clearance=6., aisle_depth=4., road_clearance=3.5, obstacle_margin=.5, region_validator=None):
    """Check every approach alternative before choosing a deterministic survivor.

    Explicit ground/paint aliases refer to the effective, visible model. Both
    footprint and approach must avoid all disclosed operational exclusions.
    ``heading_xz`` points from approach to parking center; it is a suggested
    driving heading, not an engine-required yaw. Inputs are never mutated.
    """
    # Local import keeps this independent of planner/validation orchestration.
    from .validation import _mesh_checks

    for name, value in [('pump_clearance', pump_clearance), ('aisle_depth', aisle_depth), ('road_clearance',road_clearance), ('obstacle_margin',obstacle_margin)]:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{name} must be positive and finite')
    polygon = candidate['polygon_xz']
    accessible = [p for p in geometry['polygons'] if p['color'] == 1]
    obstacles = [p for p in geometry['polygons'] if p['color'] != 1]
    gas = [_xz([s['position']])[0] for s in geometry['gas_spawns']]
    alternatives = []
    for approach in _approaches(candidate, aisle_depth):
        regions = {'footprint': polygon, 'approach': approach}
        reasons = list(candidate.get('rejection_reasons', []))
        outside = [name for name, region in regions.items()
                   if not any(_within(region, _xz(p['vertices'])) for p in accessible)]
        if outside:
            reasons.append('footprint_or_approach_outside_accessible_map_proxy')
        obstacle_hits = [{'id': p['id'], 'regions': [name for name, region in regions.items()
                          if polygon_distance(region, _xz(p['vertices'])) <= obstacle_margin]}
                         for p in obstacles]
        obstacle_hits = [p for p in obstacle_hits if p['regions']]
        if obstacle_hits:
            reasons.append('footprint_or_approach_intersects_obstacle_proxy')
        pump_distances = [{'index': index, 'region': name,
                           'distance': polygon_distance(region, [position])}
                          for index, position in enumerate(gas) for name, region in regions.items()]
        clearance = min((p['distance'] for p in pump_distances), default=None)
        if clearance is None:
            reasons.append('no_gas_locator_for_access_check')
        elif clearance < pump_clearance:
            reasons.append('footprint_or_approach_too_close_to_gas_interaction')
        roads = [{'indices': road['indices'], 'regions': [name for name, region in regions.items()
                  if polygon_distance(region, _xz(road['vertices'])) < road_clearance]}
                 for road in geometry['roads']]
        roads = [r for r in roads if r['regions']]
        if roads:
            reasons.append('intersects_map_navigation_corridor_proxy')
        parked = []
        parked_distances=[]
        for locator in mesh['locators']:
            if '.parked.' not in locator['hookup']:
                continue
            radius = 10. if locator['hookup'].startswith('truck.') else 3.5
            position = _xz([locator['position']])[0]
            parked_distances.extend({'index':locator['index'],'region':name,
                                     'margin':polygon_distance(region,[position])-radius}
                                    for name,region in regions.items())
            hits = [name for name, region in regions.items()
                    if polygon_distance(region, [position]) < radius]
            if hits:
                parked.append({'index': locator['index'], 'hookup': locator['hookup'],
                               'exclusion_radius': radius, 'regions': hits})
        if parked:
            reasons.append('parked_vehicle_locator_exclusion')
        surface = None
        # Cheap proxy failures avoid potentially expensive surface sampling.
        if not reasons:
            surface = _mesh_checks(mesh, polygon, approach, ground, paint,report_clearance=True)
            reasons.extend(surface['rejection_reasons'])
        margins={'pump':None if clearance is None else clearance-pump_clearance,
            'parked_locator':min((row['margin'] for row in parked_distances),default=None),
            'obstacle_proxy':min((polygon_distance(region,_xz(p['vertices']))-obstacle_margin
                                 for p in obstacles for region in regions.values()),default=None),
            'navigation_corridor':min((polygon_distance(region,_xz(road['vertices']))-road_clearance
                                     for road in geometry['roads'] for region in regions.values()),default=None),
            'model_obstacle':None if not surface or surface.get('minimum_model_distance') is None
                             else surface['minimum_model_distance']-.15}
        external_checks=None
        if region_validator is not None:
            external_checks=region_validator({'polygon_xz':polygon,'approach_xz':approach})
            reasons.extend(external_checks['rejection_reasons'])
            external_margin=external_checks.get('minimum_clearance_margin_m')
            if external_margin is not None:
                margins['external_object']=external_margin
        minimum_margin=min((v for v in margins.values() if v is not None),default=None)
        a, b = _center(approach), _center(polygon)
        length = math.dist(a, b)
        heading = [(b[i] - a[i]) / length for i in (0, 1)] if length > 1e-9 else None
        if heading is None:
            reasons.append('approach_has_no_distinct_heading')
        approach_direction=heading
        if candidate.get('parking_heading_xz') is not None:
            direction=candidate['parking_heading_xz']
            if (not isinstance(direction,(list,tuple)) or len(direction)!=2
                    or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in direction)
                    or math.hypot(*direction)<1e-9):
                raise ValueError('Parking heading must be a finite nonzero XZ direction')
            heading=[v/math.hypot(*direction) for v in direction]
        alternatives.append({'approach_xz': approach, 'approach_direction_xz':approach_direction, 'heading_xz': heading,
                             'heading_degrees': math.degrees(math.atan2(heading[1], heading[0])) if heading else None,
                             'pump_clearance': clearance,'clearance_margins_m':margins,
                             'minimum_clearance_margin_m':minimum_margin,
                             'rejection_reasons': sorted(set(reasons)),
                             'model_surface_checks': surface,
                             'access_checks': {'outside_accessible_proxy': outside,
                                               'obstacle_proxy_conflicts': obstacle_hits,
                                               'pump_distances': pump_distances,
                                               'road_conflicts': roads,
                                               'parked_locator_conflicts': parked}})
        if external_checks is not None:
            alternatives[-1]['local_context_checks']=external_checks
    # Preserve the historical approach rule without external context. In batch
    # mode compare the minimum clearance of complete alternatives before pump
    # distance, so a locally obstructed end cannot hide a usable opposite end.
    def end_margin(row):
        value=row.get('minimum_clearance_margin_m')
        return round(min(max(value if value is not None else 0.,0.),2.),2)
    alternatives.sort(key=lambda row: (bool(row['rejection_reasons']),
                       *([-end_margin(row)] if region_validator is not None else []),
                       -min(row['pump_clearance'] if row['pump_clearance'] is not None else -1., 20.),
                       tuple(round(v, 9) for p in sorted(row['approach_xz']) for v in p)))
    chosen = deepcopy(alternatives[0])
    chosen['evaluation_work_units']=sum((row['model_surface_checks'] or {}).get('work_units',0) for row in alternatives)
    chosen['approach_alternatives'] = alternatives
    chosen['diagnostic_exclusions'] = {
        'pump_operational_radius': pump_clearance, 'navigation_corridor_radius': road_clearance,
        'obstacle_proxy_margin': obstacle_margin,
        'limits': 'Conservative map/model proxies and sampled render surfaces; no collision-complete vehicle path or runtime activation proof.'}
    return chosen


def rank_candidates(candidates):
    """Return copies with explicit lexicographic rank components and stable IDs."""
    ranked = []
    for candidate in candidates:
        row = deepcopy(candidate)
        clearance = row.get('pump_clearance')
        clearance = float(clearance) if isinstance(clearance, (int, float)) and math.isfinite(clearance) else 0.
        margin=row.get('minimum_clearance_margin_m')
        margin=margin if isinstance(margin,(int,float)) and math.isfinite(margin) else 0.
        components = {'minimum_margin_capped_2m_rounded_cm':round(min(max(margin,0.),2.),2),
                      'passes_checks': not bool(row.get('rejection_reasons')),
                      'curb_anchor_evidence': bool(row.get('curb_anchor_evidence')),
                      'separator_geometry_evidence': row.get('separator_count', 0) >= 3 and row.get('bay_count', 0) > 0,
                      'pump_clearance_capped_20': min(max(clearance, 0.), 20.),
                      'usable_bay_count': row.get('bay_count', 1), 'stable_id': row['id']}
        key = (not components['passes_checks'], not components['separator_geometry_evidence'], not components['curb_anchor_evidence'],
               -components['minimum_margin_capped_2m_rounded_cm'], -components['pump_clearance_capped_20'], -components['usable_bay_count'], row['id'])
        row['ranking_components'] = components
        row['ranking_key'] = list(key)
        ranked.append(row)
    return sorted(ranked, key=lambda row: row['ranking_key'])
