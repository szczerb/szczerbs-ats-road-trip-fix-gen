"""Propose parking from raised source-model pavement boundaries near UI walls.

The raised horizontal boundary is geometric evidence, not proof of a functional
curb or pedestrian route. Triangle winding is not a decoded surface normal.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math

from ..geometry import _contains, _xz
from ..mesh import sample_surface_height
from ...rest_stops import _point_segment

_WELD = .001
_BUFFER = .5
_MAX_TRIANGLES = 100_000
_MAX_BOUNDARY_EDGES = 4096
_MAX_CANDIDATES = 128


def _boundaries(mesh, excluded):
    """Remove shared top-triangle edges after a 1 mm positional weld."""
    counts = Counter()
    sources = {}
    interiors = {}
    points = {}
    if sum(len(p['triangles']) for p in mesh['pieces']) > _MAX_TRIANGLES:
        raise ValueError('Curb boundary inspection exceeds 100000 triangle budget')
    for piece in sorted(mesh['pieces'], key=lambda p: p['index']):
        # Material names bound the search only; elevation, source topology,
        # outside-ground samples and a matching UI wall still prove every cue.
        if piece['material'] in excluded or not any(hint in piece['material'].lower()
                for hint in ('curb', 'kerb', 'pavement', 'sidewalk')):
            continue
        positions = piece['positions']
        for index, triangle in enumerate(piece['triangles']):
            vertices = [positions[i] for i in triangle]
            if any(len(p) != 3 or any(not math.isfinite(v) for v in p) for p in vertices):
                raise ValueError('Curb inspection requires finite XYZ source vertices')
            if max(p[1] for p in vertices) - min(p[1] for p in vertices) > .025:
                continue
            a, b, c = vertices
            area2 = (b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])
            if abs(area2) < .001:
                continue
            keys = [tuple(round(v/_WELD) for v in p) for p in vertices]
            if len(set(keys)) != 3:
                continue
            for key, point in zip(keys, vertices):
                # Actual source coordinate, not a rounded replacement. Select
                # deterministically if several source vertices share a weld.
                points[key] = min(points.get(key, tuple(point)), tuple(point))
            for left, right in zip(keys, keys[1:]+keys[:1]):
                edge = tuple(sorted((left, right)))
                counts[edge] += 1
                sources.setdefault(edge, []).append([piece['index'], index, piece['material']])
                interiors.setdefault(edge, []).append([sum(p[k] for p in vertices)/3 for k in (0, 2)])
    if any(count > 2 for count in counts.values()):
        raise ValueError('Raised top mesh contains nonmanifold welded edges')
    edges = [{'points': [points[k] for k in edge], 'sources': sources[edge], 'interiors': interiors[edge]}
             for edge, count in sorted(counts.items()) if count == 1]
    if len(edges) > _MAX_BOUNDARY_EDGES:
        raise ValueError('Curb inspection exceeds 4096 top boundary edges')
    # Merge straight subdivisions. Interior diagonals have already disappeared;
    # only degree-two boundary joints can join, preserving corners and branches.
    changed = True
    while changed:
        changed = False
        joints = {}
        for i, edge in enumerate(edges):
            for p in edge['points']:
                joints.setdefault(tuple(round(v/_WELD) for v in p), []).append(i)
        for joint, incident in sorted(joints.items()):
            if len(incident) != 2:
                continue
            i, j = incident
            def other(edge):
                return next(p for p in edge['points'] if tuple(round(v/_WELD) for v in p) != joint)
            a, b = other(edges[i]), other(edges[j])
            mid = next(p for p in edges[i]['points'] if tuple(round(v/_WELD) for v in p) == joint)
            u, v = (a[0]-mid[0], a[2]-mid[2]), (b[0]-mid[0], b[2]-mid[2])
            scale = math.hypot(*u)*math.hypot(*v)
            if not scale or (u[0]*v[0]+u[1]*v[1])/scale > -math.cos(math.radians(1)):
                continue
            if max(a[1], b[1], mid[1])-min(a[1], b[1], mid[1]) > .025:
                continue
            merged = {'points': sorted([a, b]), 'sources': sorted(edges[i]['sources']+edges[j]['sources']),
                      'interiors': edges[i]['interiors']+edges[j]['interiors']}
            edges = [e for k, e in enumerate(edges) if k not in (i, j)] + [merged]
            edges.sort(key=lambda e: e['points'])
            changed = True
            break
    return edges


def propose_curb_anchored_candidates(mesh, geometry, *, ground, paint, parameters, edge_offset=_BUFFER):
    """Return physical 3x6-style layouts anchored .5 m off qualified edges.

    Width/depth/approach and search radius come from the explicit unmarked
    parameters. No native trigger or vehicle reference-point assumption selects
    dimensions. All candidates still require the normal downstream validators.
    """
    if isinstance(edge_offset,bool) or not isinstance(edge_offset,(float,int)) or not math.isfinite(edge_offset) or not .05<=edge_offset<=1.:
        raise ValueError('Curb edge offset must be finite and between .05 and 1 metre')
    if isinstance(ground, str) or isinstance(paint, str) or not ground:
        raise ValueError('Curb proposal requires explicit ground and paint alias collections')
    gas = [_xz([s['position']])[0] for s in geometry['gas_spawns']]
    if not gas:
        return []
    walls = []
    for p in sorted(geometry['polygons'], key=lambda p: p['id']):
        footprint = _xz(p['vertices'])
        if p['color'] != 2 or any(_contains(g, footprint) for g in gas):
            continue
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(footprint,footprint[1:]+footprint[:1]))
        if abs(area)<1e-9:continue
        for i, (a, b) in enumerate(zip(footprint, footprint[1:]+footprint[:1])):
            length = math.dist(a, b)
            if length > 1e-9:
                direction=((b[0]-a[0])/length,(b[1]-a[1])/length)
                outward=(direction[1],-direction[0]) if area>0 else (-direction[1],direction[0])
                walls.append((p['id'],i,a,b,outward,direction))
    if not walls:
        return []
    result = []
    for edge in _boundaries(mesh, set(ground)|set(paint)):
        a3, b3 = edge['points']
        a, b = (a3[0], a3[2]), (b3[0], b3[2])
        length = math.dist(a, b)
        if length < parameters.width:
            continue
        tangent = ((b[0]-a[0])/length, (b[1]-a[1])/length)
        middle = ((a[0]+b[0])/2, (a[1]+b[1])/2)
        matches = []
        for polygon_id, wall_index, c, d, outward, direction in walls:
            if abs(sum(tangent[k]*direction[k] for k in (0, 1))) < math.cos(math.radians(4)):
                continue
            distance = _point_segment(middle, c, d)
            if distance > 5.:
                continue
            # Require meaningful overlap along this boundary, not just a nearby
            # extension of an unrelated wall line.
            projections = [sum((p[k]-a[k])*tangent[k] for k in (0, 1)) for p in (c, d)]
            if min(length, max(projections))-max(0., min(projections)) < parameters.width:
                continue
            # Signed polygon winding gives the local exterior even when the
            # arithmetic vertex mean lies outside a concave building ring.
            normal=(-tangent[1],tangent[0])
            if sum(normal[k]*outward[k] for k in (0,1))<0:
                normal=tuple(-v for v in normal)
            # The proposed outside must be opposite the source top face,
            # preventing a rear/internal pavement edge from parking on the top.
            if any(sum((q[k]-middle[k])*normal[k] for k in (0, 1)) >= -1e-7 for q in edge['interiors']):
                continue
            if max(sum((g[k]-middle[k])*normal[k] for k in (0, 1)) for g in gas) <= 0:
                continue
            matches.append((distance, polygon_id, wall_index, normal))
        if not matches:
            continue
        distance, polygon_id, wall_index, normal = min(matches)
        ground_samples = []
        for fraction in (.1, .5, .9):
            xz = tuple(a[k]+fraction*(b[k]-a[k])+edge_offset*normal[k] for k in (0, 1))
            try:
                height = sample_surface_height(mesh, xz, ground)
            except ValueError:
                break
            top = a3[1]+fraction*(b3[1]-a3[1])
            ground_samples.append({'xz': list(xz), 'ground_y': height, 'top_y': top, 'rise': top-height})
        if len(ground_samples) != 3 or any(not .05 <= s['rise'] <= .25 for s in ground_samples):
            continue
        for layout, width, depth in [('perpendicular', parameters.width, parameters.depth),
                                      ('parallel', parameters.depth, parameters.width)]:
            if width > length:
                continue
            count = int((length-width)//max(parameters.edge_spacing, width)) + 1
            first = (length-(count-1)*max(parameters.edge_spacing, width))/2
            for index in range(count):
                origin = tuple(a[k]+(first+index*max(parameters.edge_spacing, width))*tangent[k] for k in (0, 1))
                def rectangle(n0, n1):
                    return [[origin[k]+s*tangent[k]+n*normal[k] for k in (0, 1)]
                            for s, n in [(-width/2, n0), (width/2, n0), (width/2, n1), (-width/2, n1)]]
                polygon = rectangle(edge_offset, edge_offset+depth)
                approach = rectangle(edge_offset+depth, edge_offset+depth+parameters.aisle_depth)
                center = tuple(sum(p[k] for p in polygon)/4 for k in (0, 1))
                if min(math.dist(center, g) for g in gas) > parameters.max_station_distance:
                    continue
                evidence = {'boundary_xyz': [list(a3), list(b3)], 'source_triangles': edge['sources'],
                            'building_map_polygon': polygon_id, 'building_edge': wall_index,
                            'wall_distance': distance, 'outside_ground_samples': ground_samples,
                            'edge_offset_m': edge_offset, 'weld_tolerance_m': _WELD,
                            'limits': 'Raised horizontal source faces corroborated by outside ground and UI wall; winding-independent, functional curb/pedestrian semantics and sufficient pedestrian clearance remain unknown.'}
                key = {'edge': evidence, 'layout': layout, 'polygon': polygon}
                uid = hashlib.sha256(json.dumps(key, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:16]
                heading = [-v for v in normal] if layout == 'perpendicular' else list(tangent)
                result.append({'id': uid, 'layout': layout, 'polygon_xz': polygon, 'approach_xz': approach if layout!='parallel' else None,
                               **({'direction_xz':heading} if layout=='parallel' else {'parking_heading_xz':heading}), 'source_edge_evidence': evidence,
                               'curb_anchor_evidence': True, 'rejection_reasons': [],
                               'height_status': 'raised_boundary_and_outside_ground_sampled',
                               'evidence': 'Hypothesis — parking anchored to an observed raised top boundary near a building UI proxy; access and occupancy checks pending'})
                if len(result) > _MAX_CANDIDATES:
                    raise ValueError('Curb parking proposal exceeds bounded 128-candidate budget')
    return sorted(result, key=lambda candidate: candidate['id'])
