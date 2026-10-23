# AHX × Baxter Auto Group

Single-file landing page for Baxter Auto Group stores (Fight Fraud design system), built from the ahx-lithia template.

Data: AHX Internal `shipper_intelligence_detail` + `load_timeline` for the 13 Baxter shipper accounts with loads, pulled 2026-10-23 (586 loads, 846 VINs, Nov 2025 – Oct 2026).

## Refresh
1. Re-pull `shipper_intelligence_detail` (alltime) and `load_timeline` (routeMiles) per Baxter shipper into a scratch dir (`detail_*.json`, `timeline_*.json`).
2. `python3 tools/baxter_stats.py <dir>` prints headline stats and writes `<dir>/../baxter_loads.json`.
3. Put `geo/us-states.json` (PublicaMundi), `geo/USCities.json` (millbj92) and `geo/2023_Gaz_place_national.txt` (Census) in the parent dir, then run `python3 tools/build_map.py <parent dir>`.
4. Update the numbers in `tools/gen_baxter.py`, then run `python3 tools/gen_baxter.py ../ahx-lithia/index.html <parent>/map_svg.html index.html`.

Raw load data is not committed (public repo).
