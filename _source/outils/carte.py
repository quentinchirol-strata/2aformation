#!/usr/bin/env python3
"""Prépare le fond de carte des départements (une seule fois).
Source : contours simplifiés IGN / Etalab (licence ouverte), via le projet france-geojson.
Produit contenu/carte_france.json : chemins SVG par département + centre pour l'étiquette."""
import json, math, os
ICI = os.path.dirname(os.path.abspath(__file__))
geo = json.load(open(os.path.join(ICI, 'departements.geojson'), encoding='utf-8'))
K = math.cos(math.radians(46.5))
def proj(lon, lat): return (lon * K, -lat)
pts = [proj(*c) for f in geo['features'] for poly in (f['geometry']['coordinates'] if f['geometry']['type'] == 'MultiPolygon' else [f['geometry']['coordinates']]) for ring in poly for c in ring]
minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
W = 1000; S = W / (maxx - minx); H = (maxy - miny) * S
def xy(c):
    x, y = proj(*c); return ((x - minx) * S, (y - miny) * S)
def dp(points, eps):
    if len(points) < 3: return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy) or 1e-9
    i, dmax = 0, 0
    for k in range(1, len(points) - 1):
        d = abs(dy * points[k][0] - dx * points[k][1] + x2 * y1 - y2 * x1) / n
        if d > dmax: i, dmax = k, d
    if dmax > eps: return dp(points[:i + 1], eps)[:-1] + dp(points[i:], eps)
    return [points[0], points[-1]]
out = {}
for f in geo['features']:
    code, nom = f['properties']['code'], f['properties']['nom']
    polys = f['geometry']['coordinates'] if f['geometry']['type'] == 'MultiPolygon' else [f['geometry']['coordinates']]
    d, area, cx, cy = [], 0, 0, 0
    for poly in polys:
        for j, ring in enumerate(poly):
            full = [xy(c) for c in ring]; m = len(full) // 2
            r = dp(full[:m + 1], 1.1)[:-1] + dp(full[m:], 1.1)
            if len(r) < 4: continue
            d.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in r) + 'Z')
            if j == 0:
                a = sum(r[k][0] * r[k + 1][1] - r[k + 1][0] * r[k][1] for k in range(len(r) - 1)) / 2
                if abs(a) > abs(area):
                    area = a
                    cx = sum((r[k][0] + r[k + 1][0]) * (r[k][0] * r[k + 1][1] - r[k + 1][0] * r[k][1]) for k in range(len(r) - 1)) / (6 * a)
                    cy = sum((r[k][1] + r[k + 1][1]) * (r[k][0] * r[k + 1][1] - r[k + 1][0] * r[k][1]) for k in range(len(r) - 1)) / (6 * a)
    out[code] = {'nom': nom, 'd': ''.join(d), 'cx': round(cx, 1), 'cy': round(cy, 1)}
json.dump({'largeur': W, 'hauteur': round(H, 1), 'departements': out}, open(os.path.join(ICI, '..', 'contenu', 'carte_france.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok', len(out), round(H), os.path.getsize(os.path.join(ICI, '..', 'contenu', 'carte_france.json')))
