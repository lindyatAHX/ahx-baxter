"""Generate ~/Developer/ahx-baxter/index.html from the Lithia page template + Baxter data.
usage: python3 gen_baxter.py <lithia index.html> <map_svg.html> <out index.html>"""
import re, sys

src, mapf, out = sys.argv[1:4]
h = open(src).read()
svg = open(mapf).read()

def sub(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f"expected {count} of {old[:70]!r}, found {n}"
    h = h.replace(old, new)

def resub(pat, new):
    global h
    h, n = re.subn(pat, lambda m: new, h, flags=re.S)
    assert n == 1, f"pattern {pat[:60]!r} matched {n}"

# ---- head ----
sub("<title>Auto Hauler Exchange for Lithia Stores</title>", "<title>Auto Hauler Exchange for Baxter Stores</title>")
sub('content="48 Lithia stores already move their inventory on Auto Hauler Exchange. See the speed, the support, and how much your store could save vs. its current transport partner."',
    'content="13 Baxter Auto Group stores already move their inventory on Auto Hauler Exchange. See the speed, the support, and how much your store could save vs. its current transport partner."')

# ---- hero ----
resub(r'<div class="badge">.*?</div>', '<div class="badge">For Baxter Auto Group stores</div>')
sub('<h1>48 Lithia stores already move their vehicles <span class="accent">here.</span></h1>',
    '<h1>13 Baxter stores already move their vehicles <span class="accent">here.</span></h1>')
sub("Here is what other Lithia rooftops have actually paid, and how fast they got their units.",
    "Here is what other Baxter rooftops have actually paid, and how fast they got their units.")
sub('<div class="stat"><span class="n">48</span><span class="l">Lithia dealer locations on AHX</span></div>',
    '<div class="stat"><span class="n">13</span><span class="l">Baxter stores shipping on AHX</span></div>')
sub('<div class="stat"><span class="n">9,199</span><span class="l">Vehicles moved for Lithia stores</span></div>',
    '<div class="stat"><span class="n">846</span><span class="l">Vehicles moved for Baxter stores</span></div>')
sub('<span class="n">5.4<span class="unit">days</span>', '<span class="n">5.8<span class="unit">days</span>')
sub('<span class="n">$0.85<span class="unit">/mi</span>', '<span class="n">$0.94<span class="unit">/mi</span>')

# ---- pillars ----
sub('<span class="big">5.4 days</span>', '<span class="big">5.8 days</span>')
sub("<p>Median is 4.0 days, across 6,133 delivered orders. Once a carrier is on it, transit averages under two days.",
    "<p>Averaged across 584 delivered Baxter loads. Once a carrier picks it up, transit averages about two days.")
sub('<span class="big">$0.85<span', '<span class="big">$0.94<span')
sub("<p>Across 9,199 vehicles moved for Lithia stores &mdash;", "<p>Across 846 vehicles moved for Baxter stores &mdash;")

# ---- calculator ----
sub("Built from 6,175 Lithia loads shipped since February 2023.", "Built from 586 Baxter loads shipped since November 2025.")
sub('<span id="ticketId">AHX-LITHIA</span>', '<span id="ticketId">AHX-BAXTER</span>')
sub('id="saveTotal" style="color:var(--orange)">Save $240</div>', 'id="saveTotal" style="color:var(--orange)">Save $186</div>')
sub('<div class="out-sub" id="saveNote">32% below what you pay now.</div>', '<div class="out-sub" id="saveNote">25% below what you pay now.</div>')
sub('id="ahxPer">$510</div>', 'id="ahxPer">$564</div>')
sub('id="ahxSub">$510 per vehicle &middot; typical range $434 &ndash; $587</div>',
    'id="ahxSub">$564 per vehicle &middot; typical range $479 &ndash; $649</div>')
sub("for Lithia stores across 6,175 loads shipped since February 2023 (lifetime to date)",
    "for Baxter stores across 586 loads shipped since November 2025 (lifetime to date)")
sub("const RATE=0.85, LO=0.85, HI=1.15;", "const RATE=0.94, LO=0.85, HI=1.15;")
sub("/* ---------- lane estimator (flat $0.87 / vehicle mile) ---------- */", "/* ---------- lane estimator (flat $0.94 / vehicle mile) ---------- */")
sub("'AHX-LITHIA-'", "'AHX-BAXTER-'")

# ---- map ----
sub("Every line is a real Lithia lane moved on AHX &mdash; 6,175 loads reaching 48 states coast to coast since February 2023.",
    "Every line is a real Baxter lane moved on AHX &mdash; 586 loads reaching 44 states since November 2025.")
resub(r'<svg id="mapSvg".*?</svg>', svg)
sub('Lithia lane on AHX</span>', 'Baxter lane on AHX</span>')

# ---- testimonial: Lee Brown only ----
resub(r'<div class="eyebrow">From inside Lithia</div>.*?<div class="quotes">.*?</div>\s*</div>\s*</section>',
      '''<div class="eyebrow">From inside Baxter</div>
    <h2>Hear it from<br>Baxter&rsquo;s own.</h2>
    <div class="vids one">
      <div class="vid">
        <div class="frame"><iframe src="https://www.youtube.com/embed/R5LMemFMfP8" title="Lee Brown on Auto Hauler Exchange" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
        <div class="cap"><strong>Lee Brown</strong><span>Pre-Owned Operations Manager &middot; Baxter Auto Group</span></div>
      </div>
    </div>
  </div>
</section>''')
sub(".vid .frame{", ".vids.one{grid-template-columns:1fr;max-width:820px}\n.vid .frame{")

# ---- FAQ ----
sub("<h2>The questions other<br>Lithia rooftops asked first.</h2>", "<h2>The questions stores<br>ask first.</h2>")
resub(r'<details><summary>Are we set up already, or do we need approval\?</summary>.*?</details>',
      '<details><summary>Does each store need its own account?</summary><p>Yes. Each store opens its own account, which takes a few minutes.</p></details>')

# ---- CTA + footer ----
sub("Forty-eight Lithia stores have already done exactly that.", "Thirteen Baxter stores already ship on AHX.")
resub(r'<div class="contact-item">\s*<span class="contact-k">Dealer support</span>.*?</div>\s*<!-- TEMP:[^>]*-->',
      '<div class="contact-item">\n        <span class="contact-k">George Iliev &middot; Enterprise Sales Director</span>\n        <a href="mailto:giliev@autohaulerx.com" data-cta="contact-email">giliev@autohaulerx.com</a>\n      </div>\n      <!-- TEMP: AHX main line -->')
sub('<span>Dealer support: <a href="mailto:lithiadealer@autohaulerx.com">lithiadealer@autohaulerx.com</a></span>',
    '<span>George Iliev, Enterprise Sales Director: <a href="mailto:giliev@autohaulerx.com">giliev@autohaulerx.com</a></span>')
resub(r'<p class="data-note">.*?</p>',
      '<p class="data-note">Figures reflect loads for 13 Baxter Auto Group stores on Auto Hauler Exchange, lifetime to date (November 2025 &ndash; October 2026): 586 loads and 846 vehicles. Costs are all-in (carrier rate plus AHX platform fee) and stated per vehicle. The lane estimator is a modeled estimate, not a quote.</p>')

# ---- iframe height reporter ----
sub("Webflow at /lithia", "Webflow at /baxter")
sub("ahxLithiaHeight", "ahxBaxterHeight")

left = [m.start() for m in re.finditer("lithia", h, re.I)]
assert not left, [h[i-60:i+40] for i in left]
open(out, "w").write(h)
print("ok", len(h))
