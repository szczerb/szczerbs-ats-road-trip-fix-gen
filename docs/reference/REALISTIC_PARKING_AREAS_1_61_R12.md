# Realistic broad station parking areas — ATS 1.61 r12

**Observed locally — complete static delivery, 2026-10-24:** eight original-stack replacement packages provide **231 logical parking areas at 117 station placements**, with native-parking enhancements **OFF**. Fueling remains independently evaluated: **3073 added car fuel points, 208 policy omissions and 28 price resources**. [TASK-0052](../tasks/done/TASK-0052-generate-broad-station-parking-areas.md), [ADR-0028](../architecture/decisions/ADR-0028-plan-broad-parking-with-independent-service-eligibility.md).

## Local delivery and replacement

- [Complete eight-package ZIP](../../local_outputs/generated/2026-10-24_19-16-39/realistic-road-trip-map-fixes-1.61-r12-experimental.zip).
- [Installation README, individual SCS files and exact source-relative order](../../local_outputs/generated/2026-10-24_19-16-39/README.md).
- [Coverage by source and model family](../../local_outputs/generated/2026-10-24_19-16-39/coverage.json), [family counts](../../local_outputs/generated/2026-10-24_19-16-39/parking-family-counts.json), [fuel group decisions](../../local_outputs/generated/2026-10-24_19-16-39/fuel-group-counts.json).
- [Six optional ordinary-career observations and local locator images](../../local_outputs/generated/2026-10-24_19-16-39/optional-observations.md).
- [Reproduction and original input identities](../../local_outputs/generated/2026-10-24_19-16-39/reproduction.json), [public CLI reproduction driver](../../local_outputs/generated/2026-10-24_19-16-39/reproduce_r12.py), [hashes](../../local_outputs/generated/2026-10-24_19-16-39/SHA256SUMS.txt), [bundle verification](../../local_outputs/generated/2026-10-24_19-16-39/delivery-verification.json).

Enable all eight r12 packages. Disable the previous r9/r10 map fixes, the Alaska-only Dawson r11 replacement and earlier A/B/C/C2/E/F/G parking/fueling experiments. Keep each replacement directly above its own original source, retain the original resource stack and keep separate tank/courier packages unchanged. The required Base Game/DLC companion belongs below the external map/resource stack. OtherMaps remains price-only. The README lists exact archive names and order.

Artifacts and supplied game/map/image evidence are ignored local files in the retained research worktree, not distributed in Git. Other checkouts need verified copies of the original sources and the reviewed converted model evidence. No installation, game launch, profile edit, economy reset, merge, push or publication occurred.

## Behavior and coverage

| Source | Added fuel points | Fuel policy omissions | Native present | Native absent | Native unknown | Generated stations | Logical areas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base Game and DLC | 1007 | 73 | 50 | 80 | 1037 | 2 | 2 |
| Reforma | 900 | 54 | 78 | 76 | 1183 | 0 | 0 |
| ATS Expansion | 830 | 40 | 5 | 44 | 556 | 1 | 1 |
| Western Canada Expansion | 189 | 22 | 0 | 109 | 10 | 87 | 174 |
| ProMods Canada | 65 | 8 | 0 | 10 | 42 | 0 | 0 |
| Reforma OtherMaps Patch | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Western Canada ProMods Connections | 44 | 6 | 0 | 14 | 19 | 8 | 16 |
| Alaska Expansion | 38 | 5 | 0 | 24 | 0 | 19 | 38 |

These are source-owned placement/action counts from the original effective stack. Original native parking classification totals **133 present, 357 absent and 2847 unknown**. A native car-rest area exempts the whole associated station by default. Painted lines, NPCs, fuel points and map icons alone are not functional support evidence.

Absence is bounded evidence: original base/aux resources in a 3×3 sector neighborhood, facility links or lot-contained geometry, elevation and nearby-facility ambiguity. It is not proof of absence throughout the world. Unsupported lot/model interpretation and unresolved custom actions/parameters stay unknown or are skipped with reasons. The four reviewed model families do not represent every station layout. Coverage reports retain all unsupported/unsafe reasons; complete source processing is distinct from universal parking support.

New regions combine whole marked banks or contiguous curb/landscape strips, shortened or split around unsuitable geometry, pumps and circulation. Each logical area has an independent native car-only group and marker; emitted partial-contact flags are explicitly `0x4`. NPC parked positions are evidence of possible use, without removing scenery. Marked accessible bays may be included; adjacent access hatching remains excluded. Source truck/bus/car trigger geometry and parameters are preserved. Realistic mode adds no truck-area fallback.

**Documented — user acceptance:** Dawson's storefront and roadside regions were accepted in r11. R12 preserves the exact reviewed rectangles at placement `0x5ca1fea582800001`, sector `map/usa/sec-0029-0045.base`, with two independent groups and no old tiny polygon. The storefront is 17×6.45 m; the roadside is 23×2.6 m. The original placement is in Alaska Expansion, while the shared original descriptor is provided by `base.scs`. Original sector/descriptor pins were independently inspected instead of inheriting historical overlay hashes. [Exact authored geometry](../examples/station-parking-dawson-two-reviewed-areas.json), [accepted scope](DAWSON_TWO_REVIEWED_PARKING_AREAS_1_61_R11.md).

## Independent services and feature flag

`ProcessorConfig.improve_existing_car_parking = False` is the default, including the realistic preset. `--improve-existing-car-parking` is opt-in on stack commands; general map commands require rest plus `--parking-strategy station_bays`. Invalid, irrelevant or nonboolean combinations fail validation. Configuration, analysis, reports and reproduction carry the actual flag state.

ON reaches generation and permits safe disjoint enhancements with unambiguous native support in the placement's own PPD, preserving native groups. Externally associated/standalone rest or unresolved related evidence is explicitly skipped until the planner can clip against it. The normal delivered set is OFF; no second ON set is required.

Fuel runs independently before parking. Native-supported, unknown, disabled or skipped parking does not suppress eligible car fueling; existing car fueling does not exempt missing parking. The accepted realistic facility policy remains unchanged: G03 logistics, G04 agricultural and G05 truck-garage additions stay excluded, while G01/G02/G06 remain included. Existing original actions remain intact. 3044 fuel points remain provisionally included under that policy; 2 unsafe original station graphs remain unchanged. Decorative/nonoperational station activation remains outside this increment.

## Verification and limits

**Observed locally:** **557 tests pass**. Focused cases cover native car-only/custom/mixed actions, standalone/facility/cross-sector association, unknown evidence, default OFF and real ON output, flag propagation, both independent-service combinations, accepted fuel exclusions, multi-region geometry/contact flags, Dawson and legacy broad mode.

- [Independent finished-archive audit](../../local_outputs/generated/2026-10-24_19-16-39/receipts/independent-archive-audit.json): all eight CRCs/resource inventories, original/native PPD preservation, exact fuel/service/node and country-price preservation, emitted region groups/vertices/flags, guarded sector composition and exact two-area Dawson.
- [Independent effective context/namespace audit](../../local_outputs/generated/2026-10-24_19-16-39/receipts/independent-context-namespace-audit.json): source/provider ownership, alias lineage and classifications, original contexts, private namespaces and generated UID collision checks.
- [Original 36-archive fingerprints](../../local_outputs/generated/2026-10-24_19-16-39/receipts/original-archive-fingerprints.json), [557-test receipt](../../local_outputs/generated/2026-10-24_19-16-39/receipts/tests.log), [metadata-only verification](../../local_outputs/generated/2026-10-24_19-16-39/receipts/metadata-finalization.json). The remaining original input is the visual-resource directory, separately snapshot-pinned.

Substantive code work was delegated with explicit ownership: GPT-6.1 Sol/high implemented native classification and broad-area planning, and reviewed integration/context namespaces; GPT-6 Luna/high prepared independent raw archive and delivery audits and coordinated original-source regeneration. Root integrated the flag, independent service paths, original guards, final audits, delivery and documentation.

**Unknown:** new regions' runtime activation, marker behavior with actual vehicle shapes, fatigue, reload, billing and full-set save behavior await ordinary-career feedback. Static emitted-data checks do not establish those outcomes. Dawson retains the user's actual acceptance scope, without inferring itemized fatigue/truck/reload or other-station results. The six optional locators are incidental suggestions, not a required route, separate profile or pump matrix.

The work remains on `codex/gas-station-car-rest-research` in its isolated worktree. The primary checkout was not modified.
