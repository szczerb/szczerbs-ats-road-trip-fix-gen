---
id: TASK-0051
title: Replace Dawson's tiny r10 bay with two user-reviewed parking areas
status: done
priority: high
repositories: [.]
depends_on: [TASK-0047]
owner: shared
---

# Goal

Deliver a localized Alaska replacement giving Dawson City two independent car-only rest areas/icons across the user's red-marked storefront and roadside strips. The user will verify this one station before any broader heuristic changes.

# Context

**Documented — user report, 2026-10-24:** while using r10 in normal play, the user found only one impractically small spot and did not repeat the precise maneuvers. Three top-down images define two areas; the roadside strip is shown in two overlapping views. Crooked red lines are sketches to regularize into straight-edged shapes. The user requests area-wide activation, not two individual car-sized bays. Do not claim the latest report includes a new failed trigger attempt.

# Scope

Only placed prefab `0x5ca1fea582800001`, Alaska Expansion Dawson. Preserve fueling, native truck/bus actions, other stations, sectors, alias lineage and all other r10 resources. Provide a full Alaska-only replacement, exact enable/disable instructions and inspectable two-area geometry. Retain supplied screenshots unchanged; no game launch, live installation, profile/reset, merge or push.

# Implementation Plan

1. Preserve/inspect image evidence and match landmarks to the retained effective mesh.
2. Replace only the known generated car polygon, starting from its exact fuel-preserving pre-parking descriptor; append two separately identified native car polygons.
3. Pin the reviewed geometry/source package and validate old suffix removal, distinct groups, native bytes and complete-package preservation.
4. Deliver the localized replacement and a clear plan; record static checks and leave runtime acceptance to the user.

# Acceptance Criteria

- Two straight-edged connected-area polygons with independent car-only groups/icon positions corresponding to the two user-marked regions; the old 3x6 polygon removed.
- Actual package audit proves fueling/native triggers, sector data, private definitions/contexts and all unrelated members unchanged.
- Readable leading variant metadata, replacement instructions and a source-pinned reproducible configuration.
- No generalization to other stations before the user's verification.

# Verification

Initial research checkout clean at `2d7394d`. The primary checkout is independently occupied by `codex/north-america-background` with unrelated dirty docs/TASK-0050; leave it unchanged. Reuse existing research worktree/branch.

Delegated read-only source inventory to `dawson_site_inventory` (GPT-6 Luna/high). Root owns geometry, code, packaging and documentation; a bounded independent finished-package audit follows generation.


## Delivery verification — 2026-10-24

Source-pinned full Alaska replacement built at `local_outputs/generated/2026-10-24_16-43-15/dawson-2-areas-alaska-expansion-1.2.3-ats-1.61-r11-experimental.scs`. It changes one gameplay resource plus versioned metadata/report only. Former tiny group is absent; two new groups have IDs 1/2, four vertices each, native car-only action, flags 4, range 3 and reset 0/0. Explicit user-defined areas override the earlier default's NPC/individual-bay selection preference for this site; no scenery/NPC is removed.

Root matched the sketches to retained mesh/PPD boundaries, regularized the storefront to 17 × 6.45 m and roadside to 23 × 2.6 m, checked 72 ground samples, integrated the source-pinned full-package workflow, rendered/inspected the plan, verified the handoff ZIP and preserved all screenshot bytes. `dawson_area_writer` (GPT-6.1 Sol/high) owned the bounded native PPD replacement/default-preserving flag API and eight regression tests. `dawson_site_inventory` (GPT-6 Luna/high) inventoried source aliases and independently passed 29 finished-ZIP/raw-PPD checks without invoking the writer. Explicit ownership kept concurrent edits disjoint.

All 516 tests pass. Final SCS SHA-256 `458f1fb3d250e42c3ee811911ef8258e6c16cccace85ec99ad6d460b32bd33ce`. Every sector, fuel/price/context/definition/other-station resource and icon is byte-identical to r10. The target private alias is referenced by exactly one placement and absent from other seven r10 inventories. Two separate trigger groups/centres are statically present; actual two icons, forgiving area activation, fatigue and reload remain unverified. User verification of this one station is the next step; no wider automatic heuristic change is delivered.

[Delivery/reference](../../reference/DAWSON_TWO_REVIEWED_PARKING_AREAS_1_61_R11.md), [README](../../../local_outputs/generated/2026-10-24_16-43-15/README.md), [independent audit](../../../local_outputs/generated/2026-10-24_16-43-15/independent-audit.json). Research remains isolated; no main checkout edits, merge, push, installation, game launch, profile edit or reset.

# Links

- [r10 delivery](../../reference/REALISTIC_MAP_REPLACEMENTS_1_61_R10.md)

Unchanged local-only image evidence:

- [ats_20261024_161834_00.png](../../../local_outputs/work/2026-10-24_16-30-59/dawson-two-parking-areas/screenshots/ats_20261024_161834_00.png)
- [ats_20261024_162020_00.png](../../../local_outputs/work/2026-10-24_16-30-59/dawson-two-parking-areas/screenshots/ats_20261024_162020_00.png)
- [ats_20261024_162030_00.png](../../../local_outputs/work/2026-10-24_16-30-59/dawson-two-parking-areas/screenshots/ats_20261024_162030_00.png)
- [Provenance](../../../local_outputs/work/2026-10-24_16-30-59/dawson-two-parking-areas/screenshot-provenance.json)
