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
    for bank in report.get('proposal',{}).get('candidates',[]):
        for strip in bank.get('strips',[]):
            lines.append(poly(strip['polygon_xz'],'#fff','#222'))
    for candidate in candidates:
        if selected is not None and candidate['id']==selected['id']:continue
        lines.append(poly(candidate['polygon_xz'],'none','#bb6666' if candidate['rejection_reasons'] else '#b99d52'))
    if selected:
        if selected.get('approach_xz'):lines.append(poly(selected['approach_xz'],'#c5dcf0','#6688aa','fill-opacity="0.5"'))
        lines.append(poly(selected['polygon_xz'],'#4e97ca','#154775','fill-opacity="0.7"'))
        for bay in selected.get('bay_polygons_xz',[]):lines.append(poly(bay['polygon_xz'],'none','#fff'))
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
    if selected:
        # The complete truck-stop lot is long; retain a readable station inset.
        footprint=selected['polygon_xz']
        a=pt((min(p[0] for p in footprint)-12,min(p[1] for p in footprint)-15))
        b=pt((max(p[0] for p in footprint)+12,max(p[1] for p in footprint)+15))
        drawing=[line for line in lines if line.startswith(('<polygon ','<line ','<circle '))
                 or (line.startswith('<text ') and 'font-size="11"' in line)]
        lines.append('<text x="465" y="90" font-family="sans-serif" font-size="16">Selected area detail (same orientation)</text>')
        lines.append(f'<svg x="450" y="110" width="550" height="650" viewBox="{a[0]} {a[1]} {b[0]-a[0]} {b[1]-a[1]}">')
        lines.append(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" fill="#fcfcfa"/>')
        lines.extend(drawing)
        lines.append('</svg>')
    lines.extend(['<text x="30" y="835" font-family="sans-serif" font-size="13">Green dots = GAS; purple = original rest / parked locators; thin white strips = detected source paint.</text>',
                  '<text x="30" y="858" font-family="sans-serif" font-size="13">Experimental source/model geometry checks; game collision, fatigue, icons and reload remain unverified.</text>','</svg>'])
    return '\n'.join(lines)+'\n'
