# Truck-rest coverage research

**Documented — user report, 2026-10-25:** three marked truck-parking clusters at the annotated North Platte, Nebraska facility provide only one functional rest region. Green annotations identify working coverage; red marks identify two missing clusters and an unmarked NPC-truck side parking position. The source investigation below resolves the winning map and native geometry; screenshots alone do not establish a vanilla defect or active profile/load order.

## Preserved local evidence

Paths below are relative to this document and refer to ignored unchanged copies in the retained research worktree:

- [Regional map and red arrow](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261025_002810_00.png).
- [Close map and coverage annotations](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261025_002825_00.png).
- [First top-down view](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261024_224558_00.png).
- [Complementary top-down and side position](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/ats_20261024_224633_00.png).
- [Original provenance and hashes](../../local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/evidence-manifest.json).

These files are local-only, excluded from Git, and must be supplied as verified copies in other checkouts. The originals remain unchanged. The overlapping camera views do not establish separate additional banks. NPC occupancy corroborates intended parking rather than proving a functional rest action.

[TASK-0054](../tasks/done/TASK-0054-complete-incomplete-truck-rest-lots.md), [ADR-0029](../architecture/decisions/ADR-0029-add-independent-truck-rest-coverage.md).

## Source identification and annotation interpretation

**Observed locally — original effective ATS 1.61.3.18 stack, 2026-10-25:** the North Platte lot is provided by `ATS_Expansion_v23.0_1.61.scs`. Its working green region is standalone Trigger `0x4f3027f3fdab0001` in `map/usa/sec-0005-0003.base`, with native flags `0x0d` and effective `hud_parking` eligibility `truck`/`bus`. Its visual layout is map-authored auxiliary geometry in the corresponding `.aux` sector, rather than a parking polygon embedded in the nearby fuel prefab.

**Documented — user clarification, 2026-10-25:** the two long banks face across a driving aisle; the inner long bank also has a shorter perpendicular row. These are three logical marked banks, plus the reviewed unmarked edge parking position. The shorter row is not an overlapping camera view of the long bank.

**Observed locally — source geometry, 2026-10-25:** two long banks use the original `parking_1line_truck_dirt_curve` model. Eight separate painted separators describe the shorter perpendicular row; native `traffic.parked.truck` items corroborate its tractor/bobtail dimensions. The parallel edge strip has native `traffic.parked.truck.trailer` items. Occupancy remains variable and unchanged. The short row is not presented as a full-length trailer bay; the long banks and edge strip retain their full-rig purpose.

Source pins and exact reviewed coordinates are in `truck_parking/catalog.py`; [the original geometry receipt](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/site/north-platte-original-receipt.json) retains original providers, UIDs, dimensions and hashes. Original native green bytes remain the preservation target. Its small geometric inset relative to the painted bank is not evidence for adding a duplicate marker.

## Inventory and native serialization evidence

**Observed locally — original effective 37-input stack, 2026-10-25:** an independent census parsed all **3,480** winning map-sector resources without decode failures. It found **26** truck/bus-rest-capable PPD families at **589** placements, containing **638** native groups, and **3,000** standalone truck/bus rest triggers. GAS association was not used as a discovery filter. These are source counts, not counts of repaired facilities. [Inventory](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/inventory/original-truck-rest-inventory.json).

**Observed locally — standalone bounds calibration, 2026-10-25:** 51 original truck polygons from 46 sectors and six providers support the five observed bounds axes, across 4–9 vertices and varied headings/world positions. The writer checks the source envelope before recomputing bounds, rounds new vertices to the native 1/256-unit grid, and rounds bounding floats outward. [Calibration evidence](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/writer/varied-native-bounds-calibration.json). This source-calibrated axis interpretation is not claimed as a published engine specification.

**Unknown:** the added regions' actual runtime rest activation, icon presentation and existing-save behavior have not been tested in game. Static serialization and preservation tests do not establish those outcomes.

## Same-marker completion and wider source review

**Observed locally — 2026-10-25:** whole-bank twins would duplicate useful native markers in several mathematically partial cases. The implementation now takes the exact source/native polygon union and retains the original item/marker, flags, action bytes, tags and eligibility, with explicit node/geometry deltas. Concave boundaries retain maneuvering exclusions. Existing source vertical bounds are preserved; new edges use a separately stated project grade policy rather than the passenger-car height cap.

The original seven-candidate review exposed a real permanent obstruction in the nominal first-stall gap near Pecos/Fort Stockton. Original `or_trash_boxes1.pmd` geometry blocks that extension. The accessible stencil in the Mason City lot is a ground marking, not an automatic physical obstruction or an accessibility-policy exclusion. [Source comparison and diagrams](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/site/GENERAL_BANK_REVIEW.md).

**Observed locally — original-source serialization checks, 2026-10-25:** the reviewed Mason City, Boise and San Diego native-bank extensions serialize without adding markers; the trash-box case remains excluded by model clearance. [Actual-source receipts](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/writer/reviewed-extensions-smoke.json). A retained-census preview found four new regions and 156 bank-extension operations; those are pre-build planning results, not final package coverage or runtime outcomes.

The related diagonal-family inventory resolves all 370 original placements: 349 five-place diagonal truck curves and 21 two-line diagonal truck curves. Their mirrored/endcap part layouts remain a separately diagnosed geometry boundary; model asset bounds alone do not authorize filling their maneuvering space. [All placement layouts](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/inventory/diagonal-review/placement-source-layouts.json). Final coverage must distinguish inspected families from safely emitted geometry.

**Observed locally — native-shape precedent, 2026-10-25:** the original census contains **364 valid active nonconvex standalone truck-rest polygons**, with 4–26 vertices. These are original authored native shapes, not newly tested runtime outcomes. This evidence supports preserving concave exclusion boundaries instead of filling them with a convex hull. [Source examples and hashes](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/writer/original-concave-native-evidence.json).

**Observed locally — related diagonal coverage diagnosis, 2026-10-25:** all **370** diagonal truck-curve placements resolve to original models and source items. A conservative rendered-envelope check finds **9** already wholly covered by original standalone truck rest, **57** without a functional standalone reference in the inspected local visual scope, and **304** requiring a part/mirror-aware footprint before missing coverage can be established. The last group is uncertainty, not 304 confirmed defects; the check does not substitute a model bounding box for parking geometry and does not claim a whole-world absence proof. [Complete diagnosis and model-part evidence](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/inventory/diagonal-review/coverage-diagnosis.json).


**Observed locally — first actual r13 truck checkpoint, 2026-10-25:** 68 original Base Game/DLC native sources pass exact original-boundary containment. All 72 planned banks pass exact containment after independent nearest-grid rounding to 1/256 unit; the largest observed endpoint snap is 2.664 mm, below the 2.762 mm theoretical XZ bound. Continuous paint-bank rounding remains within the separately audited 0.01 m perimeter-area budget. Meaningful negative fixtures still reject native crops, 2 cm bank crops and aisle bridges. This is first-partition serialization evidence, not a complete-stack or gameplay result. [Quantitative receipt](../../local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/delivery/base-truck-grid-quantization-analysis.json).


## Completed static handoff

The complete original-source r13 delivery, actual coverage/counts, independently audited final archives and optional career feedback are recorded in [the canonical r13 handoff](TRUCK_REST_COVERAGE_1_61_R13.md). Earlier first-partition/preview receipts above retain their original scope; they do not replace the final archive evidence.
