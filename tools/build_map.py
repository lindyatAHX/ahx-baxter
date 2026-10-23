"""Build the Baxter lane map SVG (Albers, parallels 29.5/45.5, lon0 -96) from baxter_loads.json.
usage: python3 build_map.py <scratchpad dir>  -> writes <dir>/map_svg.html and prints geocode report"""
import json, math, sys, collections

D = sys.argv[1]
loads = json.load(open(D + "/baxter_loads.json"))
states = json.load(open(D + "/geo/us-states.json"))
cities = json.load(open(D + "/geo/USCities.json"))

ST = {"Alabama":"AL","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE",
"District of Columbia":"DC","Florida":"FL","Georgia":"GA","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
"Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
"Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ",
"New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR",
"Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT",
"Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"}

# (city,state) and (county,state) -> mean lat/lng
acc, cacc = collections.defaultdict(list), collections.defaultdict(list)
for c in cities:
    try: c["latitude"], c["longitude"] = float(c["latitude"]), float(c["longitude"])
    except (TypeError, ValueError): continue
    acc[(c["city"].upper(), c["state"])].append((c["latitude"], c["longitude"]))
    if c.get("county"):
        cacc[(c["county"].upper(), c["state"])].append((c["latitude"], c["longitude"]))
# Census place gazetteer as a fallback for suburbs/CDPs missing from the ZIP list
gaz = {}
import re
for line in open(D + "/geo/2023_Gaz_place_national.txt", encoding="latin-1").readlines()[1:]:
    f = line.rstrip().split("\t")
    nm = re.sub(r" (city|town|village|CDP|borough|municipality|charter township|township|city and borough|urban county|consolidated government.*|metropolitan government.*|unified government.*)$", "", f[3])
    gaz.setdefault((nm.upper(), f[0]), (float(f[10]), float(f[11])))
def mean(p): return (sum(a for a, _ in p) / len(p), sum(b for _, b in p) / len(p))

def norm(name):
    return (name.upper().replace("SAINT ", "ST ").replace("ST. ", "ST ").replace(" TOWNSHIP", "")
            .replace(" TWP", "").replace("FT ", "FORT ").strip())

def geocode(place):
    city, st = [s.strip() for s in place.rsplit(",", 1)]
    st = ST.get(st.title(), st.upper())
    for key in (city.upper(), norm(city)):
        if (key, st) in acc: return mean(acc[(key, st)])
    if city.upper().endswith(" COUNTY"):
        k = (city.upper()[:-7].strip(), st)
        if k in cacc: return mean(cacc[k])
    alt = norm(city).replace("ST ", "SAINT ")
    if (alt, st) in acc: return mean(acc[(alt, st)])
    for key in (city.upper(), norm(city), city.upper().replace("MT. ", "MOUNT ").replace("MT ", "MOUNT "), city.upper().replace("NORTH GLENN", "NORTHGLENN")):
        if (key, st) in gaz: return gaz[(key, st)]
    return None

# Albers equal-area conic
phi1, phi2, lam0, phi0 = map(math.radians, (29.5, 45.5, -96, 37.5))
n = (math.sin(phi1) + math.sin(phi2)) / 2
C = math.cos(phi1) ** 2 + 2 * n * math.sin(phi1)
rho0 = math.sqrt(C - 2 * n * math.sin(phi0)) / n
def alb(lng, lat):
    p, l = math.radians(lat), math.radians(lng)
    rho = math.sqrt(C - 2 * n * math.sin(p)) / n
    t = n * (l - lam0)
    return rho * math.sin(t), rho0 - rho * math.cos(t)

feats = [f for f in states["features"] if f["properties"]["name"] not in ("Alaska", "Hawaii", "Puerto Rico")]
def rings(g):
    return g["coordinates"] if g["type"] == "Polygon" else [r for poly in g["coordinates"] for r in poly]
pts = [alb(x, y) for f in feats for r in rings(f["geometry"]) for x, y in r]
W, H, pad = 960.0, 600.0, 12
minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
s = min((W - 2 * pad) / (maxx - minx), (H - 2 * pad) / (maxy - miny))
ox = (W - s * (maxx - minx)) / 2; oy = (H - s * (maxy - miny)) / 2
def P(lng, lat):
    x, y = alb(lng, lat)
    return ox + (x - minx) * s, oy + (maxy - y) * s

state_paths = []
for f in feats:
    d = ""
    for r in rings(f["geometry"]):
        xy = [P(x, y) for x, y in r]
        d += "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in xy) + "Z"
    state_paths.append(f'<path class="st" d="{d}"/>')

miss = collections.Counter(); geo = {}
for l in loads:
    for k in ("origin", "destination"):
        if l[k] not in geo: geo[l[k]] = geocode(l[k])
        if geo[l[k]] is None: miss[l[k]] += 1

lanes = collections.Counter(); vol = collections.Counter(); skipped = 0
for l in loads:
    a, b = geo[l["origin"]], geo[l["destination"]]
    if not a or not b: skipped += 1; continue
    lanes[(l["origin"], l["destination"])] += l["vinCount"]
    vol[l["origin"]] += l["vinCount"]; vol[l["destination"]] += l["vinCount"]

arcs = []
for (o, d), v in sorted(lanes.items(), key=lambda kv: kv[1]):
    x1, y1 = P(geo[o][1], geo[o][0]); x2, y2 = P(geo[d][1], geo[d][0])
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy)
    if L < 1: continue
    k = 0.18 * L
    cx, cy = (x1 + x2) / 2 - dy / L * k, (y1 + y2) / 2 + dx / L * k
    w = 0.9 + 0.55 * math.log(v); op = min(0.85, 0.32 + 0.09 * math.log(v))
    arcs.append(f'<path class="arc" d="M{x1:.1f} {y1:.1f}Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" stroke-width="{w:.2f}" stroke-opacity="{op:.3f}"/>')

vmax = max(vol.values()); nodes = []
for name, v in vol.most_common():
    if v < 3 and len(nodes) >= 40: break
    x, y = P(geo[name][1], geo[name][0])
    r = 1.6 + 6.0 * math.sqrt(v / vmax)
    nodes.append(f'<circle class="nd" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" data-name="{name}" data-v="{v}"></circle>')

svg = (f'<svg id="mapSvg" viewBox="0 0 {W} {H}" role="img" aria-label="Map of the contiguous United States showing Baxter '
       f'vehicle lanes on Auto Hauler Exchange"><g class="states">{"".join(state_paths)}</g><g class="arcs">{"".join(arcs)}</g>'
       f'<g class="nodes">{"".join(reversed(nodes))}</g></svg>')
open(D + "/map_svg.html", "w").write(svg)
print("lanes drawn", len(arcs), "nodes", len(nodes), "loads skipped (ungeocoded)", skipped)
print("unmatched places", dict(miss))
