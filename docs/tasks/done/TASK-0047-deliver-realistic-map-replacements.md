---
id: TASK-0047
title: Deliver complete realistic fuel and dedicated-parking map replacements
status: done
priority: high
repositories: [.]
depends_on: [TASK-0045, TASK-0046]
owner: shared
---

# Goal

Deliver a complete, statically audited realistic replacement set for all seven supported r9 map fixes, with selective facility-level fuel and exclusive dedicated station parking. Supply usable packages for normal career play, not another finite test batch. The required stock-game/DLC companion supplies stock-owned additions and shared classification data.

# Context

**Documented — user objective, 2026-10-21:** G1 interactions work at six sites. Include G01/G02/G06 whole public stations; exclude additions at G03 logistics, G04 farm/equipment fuel and G05 truck garage. User accepts a short optional uncertainty list for ordinary play; no separate-profile tour, pump matrix or new game evidence is required before delivery. This explicit instruction supersedes the default disposable-profile experimentation agreement for the user handoff. No agent launches the game or edits profiles.

# Scope

Map-wide facility classification, configurable broad/realistic presets and independent fuel/parking strategies; source-owned composition preserving native facilities, prices, identifiers and contexts; supported dedicated-bay geometry and explicit no-candidate/unsupported skips. All seven replacement sources, the required base companion, exact installation, source coverage, 8–12 optional readable uncertain-site locators, reproducible configuration and independent actual-output audits. N2 presentation remains deferred. No main edits, merge, push, publication or installation.

# Implementation Plan

1. Revalidate original sources/current game and reuse cached map/model/action evidence.
2. Implement facility fuel rules and preset/exclusive parking configuration while retaining broad behavior.
3. Discover source-owned station placements and safely reuse reviewed effective geometry families; resolve existing activation/orientation/ownership issues before broad reuse.
4. Compose original-source fuel/parking/price/context resources into complete replacement packages, independent of r9 assets.
5. Inspect actual archives and the full declared source stack, package coverage and optional normal-play uncertainty handoff, update durable references and commit verified milestones.

# Acceptance Criteria

- Full seven-source replacement SCS set and ZIP, usable with all r9 and experimental overlays disabled.
- Revised user decisions implemented through reusable facility semantics, explicit uncertainty and unsupported-site reporting.
- Dedicated bays only; no generated truck-area car permission or fallback. Original/native interactions remain unchanged.
- Prices, contexts, source priority, cross-resource graph composition and stable identities preserved where unchanged.
- Meaningful tests plus independent full actual-artifact/effective-stack checks, source coverage and bounded uncertainty list.
- No fabricated runtime acceptance or requirement for a new tour. Goal scope audited item-by-item before completion.

# Verification

Initial state: clean research branch at `4c91271`, clean master at `445ef581886538465564a24be0b1199164e43272`. Complete goal copied unchanged under the ignored timestamped realistic-map-replacements run.

Initial assignments: `fuel_policy_core` (GPT-6.1 Sol/high) owns fuel selection/planner facility semantics and tests; `realistic_parking` (GPT-6.1 Sol/high) owns map-wide dedicated parking/catalog and station geometry tests; `batch_station_inventory` (GPT-6 Luna/high) owns bounded ignored inventory/uncertainty/attribution research. Root owns staged source composition, presets/workflow/CLI, final artifacts, documentation and integration. Finished-output audits were subsequently assigned independently, as recorded below. Explicit file ownership avoids concurrent edits.

Implementation verification checkpoint (2026-10-21): 507 unittest regressions pass, including real cross-sector source-owner composition, one final fuel→parking context chain, independent parking-only selection, unsafe global blocker rejection, high-provider price-priority rejection, CLI analysis/generation boundaries, resource overlay ownership, facility source/state/corridor counterexamples, no truck fallback, and recorded disk-cache reuse. At that checkpoint, original-stack generation and finished-archive inspection were in progress; the final audit below supersedes that status. An initial slow run was interrupted without outputs after repeated per-member HashFS reads were identified; exact descriptor/model/material inputs are now batch-prefetched, retaining the same selection policy. Historical scratch is preserved.


## Final acceptance and scope audit — 2026-10-21

| Goal requirement | Delivered evidence |
|---|---|
| Complete source replacements, no retained r9 gameplay baseline | Eight final SCS archives: seven exact-source replacements plus required stock companion, generated from 25 original game/DLC plus 12 original map/resource/visual packages. |
| Accepted public inclusions and three omissions | Independent actual service inspection: G01/G02/G06 five additions; four native car groups retained; G03/G04/G05 no additions. |
| Reusable facility policy and explicit uncertainty | Reviewed model/state/Company relationships, actual garage kind and narrow pinned field entrance; unknown facilities provisionally included. 3,073 additions, 208 policy omissions, two unsafe stock sites unchanged. |
| Independent presets, exclusive parking and legacy broad | 508 tests; realistic station bays versus broad truck-area strategy; no-candidate/unsupported skip without fallback. |
| Practical supported parking subset | 125 private car-only bays; 120 perpendicular curb-anchored and five individual marked. Wheelchair candidates eligible. P04/P09 skipped explicitly; Mexican broad activation attribution remains unknown. |
| Source/native/price/context/identity composition | Independent finished stack and parking receipts; 791 composed sectors, 3,073 service/node clones, 28 effective price repairs, complete private lineage, historical identity comparison and changed-source disclosure. |
| Complete installable handoff | Eight SCS, ZIP, README, exact source-relative load order, SHA list, coverage, grouped skips, reproducible source configuration and static receipts. |
| Bounded ordinary-play feedback | Eight optional locations with actual native-road red-ring overviews; two retained annotated screenshots copied unchanged with provenance. No prescribed route/profile/pump matrix. |
| Boundaries | Main clean/unchanged; ignored timestamped artifacts; sources/history preserved; no merge/push/publication/install/game/profile/reset. N2 byte-identical and separate, corrected to top priority above the conflicting OtherMaps map-data provider; tank/courier unchanged. |
| Static versus runtime | Full-set career/save/activation/fatigue/billing/collision outcomes remain unverified. No new driving is a delivery gate. |

Final production and metadata verification: 508 tests pass. The independent full-order audit caught OtherMaps shadowing the draft N2-below-maps placement; the delivered order and every description now put unchanged N2 above the complete listed stack. New immutable metadata copies preserve every other archive member, including all gameplay, reports, manifests and icons. Implementation milestone `9f897e7` records the original-stack workflow; the final delivery commit records metadata contract corrections and this handoff. The metadata finalization changes description text only: gameplay resources, manifests and icons are byte-identical to the first successful complete-stack candidates. All final SCS CRCs/hashes/inventories and ZIP contents were rechecked.

Material delegation: fuel_policy_core (GPT-6.1 Sol/high) implemented facility selection and independently audited finished fuel/source/identity/price/context bytes; realistic_parking (GPT-6.1 Sol/high) implemented map-wide parking and independently audited 125 finished private bay PPDs, 202 fuel PPD native trigger sections, 791 sector compositions and 7,708 native standalone triggers; batch_station_inventory (GPT-6 Luna/high) prepared ignored source inventory/family counts and the eight representative uncertainty entries, then reviewed the handoff links and coverage. Root reviewed findings, integrated presets/ownership/contexts, verified tests, rendered native-road locators, assembled/read-checked the bundle and documented scope. Delegate audit scripts do not invoke the planner or writer.

Audit-only assumptions corrected after original-source proof: inherited boundary-node copies may differ in backward links/flags and must be preserved per resource; SCS token identifiers are case-insensitive; 80 Reforma descriptor resolutions differ from historical r9 because ATS Expansion wins the full original stack. Receipts retain these findings. The actual price inventory is 28: 27 historical-identical repairs plus one newly covered stock Halloween field; all outside-petrol bytes are preserved.

Final [delivery reference](../../reference/REALISTIC_MAP_REPLACEMENTS_1_61_R10.md), [handoff README](../../../local_outputs/generated/2026-10-21_22-23-21/README.md), [independent fuel receipt](../../../local_outputs/generated/2026-10-21_22-23-21/receipts/fuel-stack-audit.json), [independent parking receipt](../../../local_outputs/generated/2026-10-21_22-23-21/receipts/parking-archive-audit.json). Large evidence and supplied resources remain ignored/local-only. A fresh checkout needs verified local artifacts/catalog inputs.

# Links

- [Accepted fuel feedback](../../reference/SELECTIVE_CAR_FUELING_FEEDBACK_2026_10_21.md)
- [Parking feedback](../../reference/STATION_PARKING_FORECOURT_TOUR_FEEDBACK_2026_10_21.md)
- [Exclusive parking strategies](../../architecture/decisions/ADR-0022-select-mutually-exclusive-car-parking-strategies.md)
- [Fuel selection](../../architecture/decisions/ADR-0023-select-car-fuel-additions-by-reviewed-pump-role.md)
