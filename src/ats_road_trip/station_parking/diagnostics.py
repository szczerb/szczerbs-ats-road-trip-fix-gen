"""Local SVG diagnostics for station-parking proposals."""
from __future__ import annotations

from html import escape

def render_station_plan(report):
    """Render source proxies, separators and candidate decisions as a local SVG."""
    import textwrap
    geometry=report.get('geometry',{})
    polygons=geometry.get('polygons',[])
    candidates=report.get('candidates',[])
    selected=report.get('selected')
    points=[(p[0],p[2]) for poly in polygons for p in poly['vertices']]
    points.extend(tuple(p) for c in candidates for p in c['polygon_xz'])
    if not points: points=[(0,0),(10,10)]
    xmin,xmax=min(p[0] for p in points)-5,max(p[0] for p in points)+5
    zmin,zmax=min(p[1] for p in points)-5,max(p[1] for p in points)+5
    scale=min(900/max(xmax-xmin,1),700/max(zmax-zmin,1))
    def pt(p):return (50+(p[0]-xmin)*scale,85+(p[1]-zmin)*scale)
    def poly(points,fill,stroke,extra=''):
        coordinates=' '.join(f'{x:.3f},{y:.3f}' for x,y in map(pt,points))
        return f'<polygon points="{coordinates}" fill="{fill}" stroke="{stroke}" stroke-width="1.2" {extra}/>'
    decisions=[]
    for index,candidate in enumerate(candidates,1):
        state='SELECTED' if selected and candidate['id']==selected['id'] else ('REJECTED' if candidate['rejection_reasons'] else 'accepted alternative')
        decisions.append(f"{index}. {candidate['id']} — {state}")
        reasons=candidate['rejection_reasons'] or ['passes current static checks']
        for reason in reasons:
            decisions.extend(textwrap.wrap(str(reason).replace('_',' '),width=78,initial_indent='  ',subsequent_indent='    '))
        if candidate.get('ranking_components'):
            r=candidate['ranking_components']
            decisions.append(f"  rank: paint={r['separator_geometry_evidence']} curb={r.get('curb_anchor_evidence',False)} margin={r.get('minimum_margin_capped_2m_rounded_cm',0):.2f}m pump={r['pump_clearance_capped_20']:.2f}m bays={r['usable_bay_count']}")
            decisions.append('  layout: '+candidate.get('layout','paint-derived bank'))
        decisions.append('')
    height=max(880,110+18*len(decisions))
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="{height}" viewBox="0 0 1800 {height}">',
           f'<rect width="1800" height="{height}" fill="#fcfcfa"/>',
           f'<text x="30" y="30" font-family="sans-serif" font-size="20">{escape(report.get("station_id","Station"))} / {escape(report.get("method","diagnostic"))}</text>',
           '<text x="30" y="54" font-family="sans-serif" font-size="13">Local XZ metres; grey = building/canopy proxy, green = inaccessible proxy, red = rejected, blue = selected</text>']
    for row in polygons:
        fill={1:'#e7e4dd',2:'#aaa69f',4:'#bdd1b2'}.get(row['color'],'#e0c1cf')
        lines.append(poly([(v[0],v[2]) for v in row['vertices']],fill,'#777'))
    for road in geometry.get('roads',[]):
        a,b=map(pt,[(p[0],p[2]) for p in road['vertices']])
        lines.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#aa9c6e" stroke-width="2"/>')
    if report.get('effective_model_state'):
        features=report.get('model_features',{})
        rows=[*features.get('curb_evidence',{}).get('features',[]),
              *features.get('entrance_clearance',{}).get('proxies',[]),
              *features.get('obstacles',{}).get('features',[])]
        for feature in rows:
            colors={'low_raised_edge_surface_proxy':'#4c6270','entrance_keep_clear_proxy':'#dc7934','model_obstacle_triangle':'#83705b'}
            lines.append(poly(feature['polygon_xz'],'none',colors.get(feature['kind'],'#777'),
                              'stroke-dasharray="2 2"'))
        seen_edges=set()
        for candidate in candidates:
            edge=candidate.get('source_edge_evidence',{}).get('boundary_xyz')
            if edge and tuple(map(tuple,edge)) not in seen_edges:
                seen_edges.add(tuple(map(tuple,edge)))
                a,b=[pt((p[0],p[2])) for p in edge]
                lines.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#e49a16" stroke-width="2"/>')
        radius=next((c.get('diagnostic_exclusions',{}).get('pump_operational_radius') for c in candidates
                     if c.get('diagnostic_exclusions')),6.)
        for spawn in geometry.get('gas_spawns',[]):
            x,y=pt((spawn['position'][0],spawn['position'][2]))
            lines.append(f'<circle cx="{x}" cy="{y}" r="{radius*scale}" fill="none" stroke="#216c43" stroke-dasharray="4 3"/>')
    for bank in report.get('proposal',{}).get('candidates',[]):
        for strip in bank.get('strips',[]):
            lines.append(poly(strip['polygon_xz'],'#fff','#222'))
    for candidate in candidates:
        if selected is not None and candidate['id']==selected['id']:continue
        lines.append(poly(candidate['polygon_xz'],'none','#bb6666' if candidate['rejection_reasons'] else '#b99d52',
                          'data-layer="candidate-alternative"' if report.get('effective_model_state') else ''))
    if selected:
        if selected.get('approach_xz'):lines.append(poly(selected['approach_xz'],'#c5dcf0','#6688aa','fill-opacity="0.5"'))
        lines.append(poly(selected['polygon_xz'],'#4e97ca','#154775','fill-opacity="0.7"'))
        for bay in selected.get('bay_polygons_xz',[]):lines.append(poly(bay['polygon_xz'],'none','#fff'))
        if selected.get('activation_polygon_xz'):
            lines.append(poly(selected['physical_parking_polygon_xz'],'none','#f4b942'))
            center=[sum(p[i] for p in selected['polygon_xz'])/len(selected['polygon_xz']) for i in (0,1)]
            heading=selected.get('heading_xz')
            if heading:
                a=pt([center[i]-heading[i]*2 for i in (0,1)]);b=pt([center[i]+heading[i]*2 for i in (0,1)])
                lines.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#fff" stroke-width="3"/>')
                # Two wings mark the suggested nose; yaw is not an engine predicate.
                for sign in (-1,1):
                    wing=pt([center[0]+heading[0]-sign*heading[1]*.6,center[1]+heading[1]+sign*heading[0]*.6])
                    lines.append(f'<line x1="{b[0]}" y1="{b[1]}" x2="{wing[0]}" y2="{wing[1]}" stroke="#fff" stroke-width="3"/>')
    for index,candidate in enumerate(candidates,1):
        center=[sum(p[i] for p in candidate['polygon_xz'])/len(candidate['polygon_xz']) for i in (0,1)]
        x,y=pt(center)
        lines.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="sans-serif" font-size="11" fill="#111">{index}</text>')
    lines.append('<text x="1055" y="85" font-family="sans-serif" font-size="17">Candidate decisions (numbers match the plan)</text>')
    for index,line in enumerate(decisions):
        lines.append(f'<text x="1055" y="{112+18*index}" font-family="monospace" font-size="12">{escape(line)}</text>')
    for spawn in geometry.get('gas_spawns',[]):
        x,y=pt((spawn['position'][0],spawn['position'][2]));lines.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#216c43"/>')
    for group in report.get('original_rest_groups',[]):
        lines.append(poly([(p[0],p[2]) for p in group['vertices']],'none','#9c64a0','stroke-dasharray="5 4"'))
    for locator in report.get('mesh_summary',{}).get('locators',[]):
        if '.parked.' in locator['hookup']:
            x,y=pt((locator['position'][0],locator['position'][2]));lines.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#9c64a0"/>')
            if report.get('effective_model_state'):
                radius=10. if locator['hookup'].startswith('truck.') else 3.5
                lines.append(f'<circle cx="{x}" cy="{y}" r="{radius*scale}" fill="none" stroke="#9c64a0" stroke-dasharray="3 3"/>')
    if selected:
        # The complete truck-stop lot is long; retain a readable station inset.
        footprint=selected['polygon_xz']
        a=pt((min(p[0] for p in footprint)-12,min(p[1] for p in footprint)-15))
        b=pt((max(p[0] for p in footprint)+12,max(p[1] for p in footprint)+15))
        drawing=[line for line in lines if line.startswith(('<polygon ','<line ','<circle '))
                 or (line.startswith('<text ') and 'font-size="11"' in line)]
        if report.get('effective_model_state'):
            drawing=[line for line in drawing if 'candidate-alternative' not in line
                     and not (line.startswith('<text ') and 'font-size="11"' in line)]
        lines.append('<text x="465" y="90" font-family="sans-serif" font-size="16">Selected area detail (same orientation)</text>')
        lines.append(f'<svg x="450" y="110" width="550" height="650" viewBox="{a[0]} {a[1]} {b[0]-a[0]} {b[1]-a[1]}">')
        lines.append(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" fill="#fcfcfa"/>')
        lines.extend(drawing)
        lines.append('</svg>')
    if report.get('effective_model_state'):
        lines.append('<text x="30" y="810" font-family="sans-serif" font-size="12">Dashed green: pump clearance proxy; gold: physical proposal; blue: activation polygon; arrow: suggested nose. Engine pose envelope UNKNOWN.</text>')
    lines.extend(['<text x="30" y="835" font-family="sans-serif" font-size="13">Green dots = GAS; purple = original rest / parked locators; thin white strips = detected source paint.</text>',
                  '<text x="30" y="858" font-family="sans-serif" font-size="13">Experimental source/model geometry checks; game collision, fatigue, icons and reload remain unverified.</text>','</svg>'])
    return '\n'.join(lines)+'\n'
