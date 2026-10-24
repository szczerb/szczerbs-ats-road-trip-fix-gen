# Truck-rest coverage research

**Documented — user report, 2026-10-25:** three marked truck-parking clusters at the annotated North Platte, Nebraska facility provide only one functional rest region. Green annotations identify working coverage; red marks identify two missing clusters and an unmarked NPC-truck side parking position. Source identities and cause remain under investigation; do not infer a vanilla defect or active profile/load order from the images.

## Preserved local evidence

Paths below are relative to this document and refer to ignored unchanged copies in the retained research worktree:

- [Regional map and red arrow](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261025_002810_00.png).
- [Close map and coverage annotations](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261025_002825_00.png).
- [First top-down view](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261024_224558_00.png).
- [Complementary top-down and side position](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261024_224633_00.png).
- [Original provenance and hashes](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/evidence-manifest.json).

These files are local-only, excluded from Git, and must be supplied as verified copies in other checkouts. The originals remain unchanged. The overlapping camera views do not establish separate additional banks. NPC occupancy corroborates intended parking rather than proving a functional rest action.

[TASK-0054](../tasks/active/TASK-0054-complete-incomplete-truck-rest-lots.md), [ADR-0029](../architecture/decisions/ADR-0029-add-independent-truck-rest-coverage.md).

## Source identification and annotation interpretation

**Observed locally — original effective ATS 1.61.3.18 stack, 2026-10-25:** the North Platte lot is provided by `ATS_Expansion_v23.0_1.61.scs`. Its working green region is standalone Trigger `0x4f3027f3fdab0001` in `map/usa/sec-0005-0003.base`, with native flags `0x0d` and effective `hud_parking` eligibility `truck`/`bus`. Its visual layout is map-authored auxiliary geometry in the corresponding `.aux` sector, rather than a parking polygon embedded in the nearby fuel prefab.

**Documented — user clarification, 2026-10-25:** the two long banks face across a driving aisle; the inner long bank also has a shorter perpendicular row. These are three logical marked banks, plus the reviewed unmarked edge parking position. The shorter row is not an overlapping camera view of the long bank.

**Observed locally — source geometry, 2026-10-25:** two long banks use the original `parking_1line_truck_dirt_curve` model. Eight separate painted separators describe the shorter perpendicular row; native `traffic.parked.truck` items corroborate its tractor/bobtail dimensions. The parallel edge strip has native `traffic.parked.truck.trailer` items. Occupancy remains variable and unchanged. The short row is not presented as a full-length trailer bay; the long banks and edge strip retain their full-rig purpose.

Source pins and exact reviewed coordinates are in `truck_parking/catalog.py`; [the original geometry receipt](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/site/north-platte-original-receipt.json) retains original providers, UIDs, dimensions and hashes. Original native green bytes remain the preservation target. Its small geometric inset relative to the painted bank is not evidence for adding a duplicate marker.

## Inventory and native serialization evidence

**Observed locally — original effective 37-input stack, 2026-10-25:** an independent census parsed all **3,480** winning map-sector resources without decode failures. It found **26** truck/bus-rest-capable PPD families at **589** placements, containing **638** native groups, and **3,000** standalone truck/bus rest triggers. GAS association was not used as a discovery filter. These are source counts, not counts of repaired facilities. [Inventory](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/inventory/original-truck-rest-inventory.json).

**Observed locally — standalone bounds calibration, 2026-10-25:** 51 original truck polygons from 46 sectors and six providers support the five observed bounds axes, across 4–9 vertices and varied headings/world positions. The writer checks the source envelope before recomputing bounds, rounds new vertices to the native 1/256-unit grid, and rounds bounding floats outward. [Calibration evidence](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/writer/varied-native-bounds-calibration.json). This source-calibrated axis interpretation is not claimed as a published engine specification.

**Unknown:** the added regions' actual runtime rest activation, icon presentation and existing-save behavior have not been tested in game. Static serialization and preservation tests do not establish those outcomes.
