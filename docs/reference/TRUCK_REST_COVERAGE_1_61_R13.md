# Independent truck-rest coverage — ATS 1.61 r13

**Observed locally — completed static delivery, 2026-10-25:** eight complete realistic replacements add **4 truck-rest regions/icons** and complete **156 painted-bank footprints across 143 existing native regions**, retaining their markers. Changes are grouped into **143 authored site groups / 145 native source groups**. R12's **231 car areas at 117 placements**, accepted Dawson pair, **3073 car-fueling additions / 208 policy omissions / 28 price resources** are preserved. [TASK-0054](../tasks/done/TASK-0054-complete-incomplete-truck-rest-lots.md), [ADR-0029](../architecture/decisions/ADR-0029-add-independent-truck-rest-coverage.md).

## Local delivery

- [Complete eight-package ZIP](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental.zip).
- [Installation README and exact source-relative order](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/README.md).
- [Optional career checklist, North Platte first](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/career-test-checklist.md); [complete changed-location inventory](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/changed-location-inventory.json).
- [Actual emitted before/after diagrams](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/diagrams/index.md); [coordinate and archive-hash bindings](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/diagrams/diagram-coordinates.json).
- [Coverage and specific skip/uncertainty counts](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/coverage.json); [three optional uncertainty locators](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/uncertain-career-locators.md).
- [Reproduction/configuration](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/reproduction.json), [pinned public-CLI driver](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/reproduce_r13.py), [file hashes](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/SHA256SUMS.txt) and [independent final ZIP readback](../../local_outputs/generated/2026-10-25_03-46-07/delivery-verification.json).

Enable all eight r13 replacements. Disable the complete r12 set and older r9/r10/Dawson r11 and A/B/C/C2/E/F/G station experiments listed by exact filename in the README. Keep original game/map/resource inputs in their declared order; each replacement belongs directly above its own source. The Base Game/DLC companion belongs below the external stack. OtherMaps remains price-only. Separate tank/courier packages retain their positions. The new set is a full replacement, with no separate truck addon.

Artifacts, supplied screenshots and extracted resources are ignored local evidence in the retained research worktree. Git does not contain these archives or game/map assets. Another checkout needs verified copies of the declared inputs and converted model evidence. Documentation evidence links use project-local relative paths; [unchanged screenshot provenance](TRUCK_REST_COVERAGE_RESEARCH.md#preserved-local-evidence).

## North Platte regression case

**Documented — user report and clarification:** two long banks face across a driving aisle, with a short perpendicular bank beside the inner one and a legitimate unmarked side position. Only the green region originally offered rest. The user annotations express intended areas, not exact vertices.

**Observed locally — original ATS Expansion 23.0 / ATS 1.61.3.18:** standalone source `0x4f3027f3fdab0001` in `map/usa/sec-0005-0003.base` retains its exact item and node bytes. The source compound is `0x5269d91ea0100000` in the corresponding `.aux` sector; this layout is map-authored standalone geometry. Final output adds the opposite long bank, short perpendicular bank and parallel side strip: **one retained + three new = four regions/icons**. Driving aisles remain outside the generated polygons.

The long bank follows its original paint footprint with a reported approximately 0.73 m curbside inset around a permanent prop, retaining about **52.06 × 23.43 m**. The short row is about **23.81 × 9.70 m**, corroborated by native tractor/bobtail NPCs; it is not a full-length trailer bank. The parallel side strip is **51 × 5.6 m** and has original variable NPC rigs. Long banks and side parking retain their full-rig purpose. NPCs/scenery remain unchanged. Final diagram coordinates are read from the delivered SCS archives.

## Independent behavior and scope

`ProcessorConfig.improve_truck_parking` / `--improve-truck-parking` defaults **OFF** and is **ON** in this delivered realistic set. `improve_existing_car_parking` remains **OFF**. Truck work requires rest processing and is independent of GAS/fuel, native-car support and the 1,000-unit car-neighbor rule. Truck-only rest with `parking_strategy=none` is supported when the truck flag is enabled. Invalid/ignored combinations are rejected.

Missing logical banks receive independent car-free native rest groups. Materially partial banks receive constrained simple polygon unions, retaining their native item/marker, original node identities, action/parameters, flags, tags and truck/bus eligibility. Concave boundaries preserve maneuvering exclusions. Source-native covered area remains retained; new truck areas add no car eligibility. Fuel, car and truck changes compose in authoritative source-owned sectors.

Fully covered or useful near-complete native banks remain unchanged, avoiding duplicate colocated icons. Native partial-contact coverage of at least 95%, or native coverage of at least 99.5% for an edge sliver, preserves the existing useful marker with explicit diagnostics. Other gaps receive constrained completion or an unsafe/unknown result. No global shared action definition is rewritten.

| Source | Original standalone regions | Native PPD placements / groups | Reviewed paint banks | Added regions / icons | Native regions extended | Bank operations |
|---|---:|---:|---:|---:|---:|---:|
| Base Game and DLC | 1163 | 168 / 186 | 339 | 0 | 68 | 72 |
| Reforma | 922 | 140 / 158 | 120 | 0 | 20 | 24 |
| ATS Expansion | 819 | 89 / 97 | 179 | 4 | 53 | 58 |
| Western Canada Expansion | 12 | 133 / 137 | 1 | 0 | 1 | 1 |
| ProMods Canada | 59 | 13 / 13 | 8 | 0 | 1 | 1 |
| Reforma OtherMaps Patch | 0 | 0 / 0 | 0 | 0 | 0 | 0 |
| Western Canada ProMods Connections | 25 | 16 / 16 | 2 | 0 | 0 | 0 |
| Alaska Expansion | 0 | 30 / 31 | 0 | 0 | 0 | 0 |

**Observed locally — original-source discovery:** all **37 inputs** and **3480 winning base/aux resources** are inspected independently of fuel. Original native inventory contains **3000 standalone truck/bus triggers** and **26 PPD families / 589 placements / 638 groups**. The reviewed straight-bank rule reaches all **649** matching source placements; its per-placement outcomes and unsupported flags/parts/association/clearance remain reported. Original native region counts do not establish complete functional coverage of every visual bay.

Changed authored site groups follow paint-compound ancestry, with disconnected groups split over 200 m; native UID is the fallback. The coverage summary separately reports bounded visual candidate groups, covered/incomplete/uncertain source outcomes, native regions, added icons and extension operations. These are explicit source-backed grouping/counting rules, not a complete census of physical facilities or a claim every similar world lot is fixed.

**Observed locally — related-family boundary:** all **370** diagonal truck curves are resolved (349 five-place and 21 two-line). Conservative envelope diagnosis finds 9 already covered at that envelope level, 57 without a local functional standalone reference, and 304 requiring precise part/mirror-aware geometry. They remain unchanged; envelope overlap alone cannot establish a parking-stall outline or a defect. Native PPD rest is inventoried and contributes proven coverage; unreviewed layouts/transforms cannot authorize blanket additions.

Source static-model KDOP proxies exclude permanent/interior or unidentified obstructions from newly activated space. Variable parked traffic and ground/accessibility stencils are not permanent blockers. The Pecos trash-box gap is an explicit exclusion. Proxy clearance is bounded original 3×3-sector evidence, not a complete collision/terrain/access proof. Unproven shared root-node mutation contracts and unsafe metadata remain skips.

## Verification and runtime boundary

**Observed locally:** **633 authored tests pass**, covering actual truck ON and legacy OFF, separate fuel/car/truck gates, non-GAS discovery, native/custom/unknown support, compound/cross-sector association, truck-scale geometry, original eligibility, exact native unions, model clearance, composition, Dawson and legacy behavior. Scratch audit fixtures reject native/bank crops, aisle bridges, wrong source identities/owners/namespaces, UID collisions, stale cross-sector copies, malformed metadata and corrupt archives.

- [Independent finished-archive/native/UID audit](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/r13-independent-archive-audit.json): actual payloads versus r12 and original winners; only declared truck deltas may change native geometry. New IDs are checked against the complete original and r12 namespaces.
- [Effective source-relative context/namespace audit](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/r13-independent-context-audit.json): real winners, private aliases/lineage, original context classifications and generated namespace safety.
- [Independent original-bank reconstruction](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/r13-independent-source-bank-audit.json): original model hashes, curve endpoints/parts/compound namespaces, reviewed North Platte evidence and final ZIP polygons.
- [Cross-sector native-node consistency](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/r13-independent-cross-sector-node-audit.json): independently rebuilt occurrences for all original referenced truck nodes; actual moved nodes are checked across same-namespace original copies.
- [Final readback](../../local_outputs/generated/2026-10-25_03-46-07/delivery-verification.json): eight SCS and complete ZIP CRCs/hashes/inventories, metadata and actual raw/final gameplay-byte preservation, all diagram/locator links, North Platte four regions and exact green preservation, site/count reconciliation and flags.

The independent source UID baseline covers **18,823,372 distinct item/node/nested IDs** in all 3480 sectors. Source fingerprints match all **36 original archives (25,371,215,151 bytes)** and the **6689-file** visual-resource directory. Older generated packages are comparison evidence; generation starts from the original stack. Source code stayed frozen during regeneration; [code pins](../../local_outputs/generated/2026-10-25_03-46-07/realistic-road-trip-map-fixes-1.61-r13-experimental/r13-build-code-sha256.json) and reproduction record the actual build. Delivery metadata uses readable revision/source identities and preserves all gameplay members. The seven map packages retain their exact approved artwork; the Base Game/DLC companion retains the documented no-artwork exception.

Paint banks are reconstructed independently and compared on the native **1/256-unit** XZ grid. Original native containment remains exact; independently quantized paint-bank containment is exact. Continuous-source rounding retains the separately audited 0.01 m perimeter/area budget. Millimetre serialization rounding does not waive material crops or aisle-bridge checks. [Precision policy](../architecture/decisions/ADR-0029-add-independent-truck-rest-coverage.md#native-coordinate-audit-precision).

**Unknown:** newly generated rest activation, actual vehicle/trailer contact, icon behavior, fatigue recovery, reload and full-set career behavior await normal play. Static proof does not establish those results. The optional checklist is a short sample with feedback fields; neither its prioritized stops nor the complete inventory is a required tour or a separate-profile experiment. Dawson retains the user's previous acceptance scope. No installation, game/profile/economy operation, primary-checkout edit, merge, push or publication occurred. Work remains on `codex/gas-station-car-rest-research`.
