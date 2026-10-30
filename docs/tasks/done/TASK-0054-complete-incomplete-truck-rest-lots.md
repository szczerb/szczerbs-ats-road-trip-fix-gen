---
id: TASK-0054
title: Complete missing truck-rest regions and deliver realistic r13 replacements
status: done
priority: high
repositories: [.]
depends_on: [TASK-0052]
owner: shared
---

# Goal

Repair incomplete functional truck-rest facilities, beginning with the North Platte three-bank lot and reviewed unmarked side space. Discover comparable original-source facilities and deliver eight complete realistic r13 replacement packages plus coverage, diagrams and an incidental-career checklist.

# Context

**Documented — user report, 2026-10-25:** only one of three visibly marked truck-parking clusters near North Platte, Nebraska offered rest. The user selected another legitimate cluster while overdue and had to move. Green annotations identify working coverage; red annotations identify two missing marked clusters and an unmarked NPC-truck side position. This is user-reported gameplay, not an agent reproduction. [Preserved local evidence](../../reference/TRUCK_REST_COVERAGE_RESEARCH.md).

The full objective is preserved under ignored `local_outputs/work/2026-10-25_00-36-28/truck-rest-goal-evidence/goal-prompt.md`. Original images/provenance remain unchanged. R12's 231 car areas / 117 placements, exact Dawson pair, independent realistic fueling and native-car improvement OFF remain the baseline.

# Scope

Use the existing research branch/worktree. Add independent explicit truck coverage, including non-GAS facilities and standalone diagnostics; complete missing logical regions without applying the car native-support gate or granting cars new truck access. Preserve native actions and explicitly audit intended truck geometry changes. Deliver full source-relative replacements, not a layered site addon. No primary-checkout edits, installation, game/profile/economy changes, merge, push or publication. The separate background/navigation topic is excluded.

# Implementation Plan

1. Resolve the exact North Platte effective source/placement/model/geometry and correlate all annotations.
2. Inventory original truck-capable facilities across the declared source stack, including non-fueling and standalone cases.
3. Implement a separate truck coverage module, guarded native truck writer and configuration/CLI propagation.
4. Compose fuel, car and truck edits with ownership/context lineage intact; test flag OFF and actual ON behavior.
5. Generate all eight r13 replacements from original sources; independently audit emitted geometry and effective stack.
6. Deliver ZIP, exact source-relative order, full changed-location inventory and a manageable prioritized checklist with diagrams/feedback fields.

# Acceptance Criteria

- North Platte working green region retained; both missing marked banks and reviewed side space covered, or a precise contradictory-source blocker remains open.
- One working region never exempts an incomplete facility; no generic 1,000-unit car rule or GAS-only discovery gate.
- Deterministic family rules reach every eligible effective placement; partial/unknown/unsupported cases are explicit.
- New truck geometry never adds car eligibility; existing car/bus/truck actions and unrelated geometry remain protected.
- Truck option enabled in the delivered set, native-car improvement OFF, independent fuel behavior unchanged.
- Eight complete original-source replacements, ZIP, README/order, checksums/reproduction/audits, full inventory and usable checklist.
- Existing r12 car regions/Dawson/fuel/price/context identities preserved; original native byte comparisons allow only explicitly intended truck changes.

# Verification

Started from clean research commit `1c401e1`. New scratch is `local_outputs/work/2026-10-25_01-01-52/truck-rest-r13/`. TASK-0053 is reserved by the separate primary-checkout project; this task uses the next unused ID.

Actual delegation: `truck_site_geometry` (GPT-6.1 Sol/high) owns North Platte source identification, geometry/catalog modules and related tests; `truck_trigger_writer` (GPT-6.1 Sol/high) owns native truck trigger writing, shared splice preservation and fixture tests; `truck_inventory_delivery` (GPT-6 Luna/high) owns original-source inventory and independent delivery/audit scripts only. Root owns configuration, processor/map-stack integration, final verification, documentation and delivery. No gameplay is run by agents.

Completion remains unproven until emitted archives, source ownership, native preservation, truck eligibility, namespace/UID queries and complete ZIP/checklist pass independent read-back. Static checks do not establish new runtime results.

# Links

- [R12 baseline](../../reference/REALISTIC_PARKING_AREAS_1_61_R12.md)
- [Independent truck coverage decision](../../architecture/decisions/ADR-0029-add-independent-truck-rest-coverage.md)

Progress: the independent original census parsed all 3,480 winning map-sector resources (37 inputs), finding 26 truck/bus PPD families / 589 placements / 638 groups and 3,000 standalone triggers. Exact North Platte original source/native UID and reviewed short-bank/edge geometry are identified. The user clarified the shorter perpendicular bank; native source bobtail models corroborate that arrangement. Native serializer bounds calibration passed 51 varied original polygons. The first integrated regression run passed 601 tests; final source smoke, implementation freeze and delivery remain pending.

Implementation freeze verification: **613 tests pass** in the complete authored suite; **62 focused truck/configuration/car-preservation tests pass** independently. Actual original-source North Platte serialization adds the three intended regions with flags 13 and 1/256-unit nodes while retaining the green item and nodes. Required reviewed targets block delivery if they cannot be emitted. Unknown action/activation/geometry contracts retain conservative coverage uncertainty. Full original-stack smoke and final archives remain pending, so this is an implementation milestone rather than goal completion.

Further verified implementation: exact concave native-bank unions preserve a single marker, original covered geometry/vertical bounds, action bytes, eligibility and original node IDs. Static-model clearance excludes genuine interior props while retaining accessible ground markings and variable NPC occupancy. The actual-source Mason City/Boise/San Diego extension smoke passes; the Pecos/Fort Stockton trash-box gap is excluded. The complete authored suite passes **632 tests**. A retained-census preview reports four additions and 156 bank-extension operations, pending fresh generation and independent final-archive proof. Original source fingerprints match all 36 archives (25,371,215,151 bytes) and the 6,689-file resource directory snapshot. Related diagonal placement inventory is complete but its part-layout generation remains explicitly unsupported.


Final source freeze: commit `5c284ce3b8072f50b0ac2a8c5b12804c7e7cafc9` passes **633 authored tests**. The first complete build was interrupted before archives were emitted; retained exact original-member caches are read-only inputs to a fresh build, not a generated gameplay baseline. The resumed run adds content-addressed per-processor checkpoints bound to original-source fingerprints, semantic source/configuration hashes and staged resource bytes. Final artifacts and read-back remain required.

Additional bounded delegation: `delivery_audit_repair` (GPT-6 Luna/high) reviews delivery/checklist/read-back and independently reconstructed source-bank evidence; `audit_actual_native_deltas` (GPT-6.1 Sol/high) reviews final-archive native deltas, sectors newly emitted relative to r12 and collision accounting. Both own ignored audit helpers only; product source remains frozen during generation. Root reviews and executes final audits. Optional career checks are capped at eight prioritized sites; the full machine inventory remains available without requiring a driving tour.


## Final verification — 2026-10-25

**Observed locally:** eight complete r13 replacements and ZIP pass all independent final audits and readback. Actual output adds 4 truck regions/icons and completes 156 banks across 143 native regions, grouped into 143 authored sites / 145 native source groups. North Platte retains its exact green region and adds all three required regions (four total). All 231/117 car areas/placements, exact Dawson pair, 3073 fuel additions, 208 omissions and 28 prices remain preserved. Truck improvement is ON; existing-car improvement is OFF. The source-only UID scan covers 3480 sectors / 18,823,372 distinct IDs. The all-source root-node index covers 13,934 referenced IDs / 13,938 occurrences; final moved-node/copy consistency passes.

All 633 authored tests pass. Independently reconstructed source geometry, actual SCS preservation/eligibility/ownership/UIDs, source-relative context/namespace, raw-versus-final metadata-only payloads, ZIP checksums and actual-coordinate diagrams pass. [Canonical handoff, receipts and optional career checklist](../../reference/TRUCK_REST_COVERAGE_1_61_R13.md). Full-set runtime behavior remains unverified and is explicitly left for normal career feedback, not a mandatory tour.

Additional actual delegation: `audit_cross_sector_nodes` (GPT-6 Luna/high) owns source-only occurrence indexing and independent final cross-sector consistency, including executable stale-copy/owner/namespace/source-tamper failures. Root reviews all receipts, corrects final inventory/source-label integration and verifies the complete delivery. No primary-checkout edit, merge, push, installation or game/profile/reset operation occurred.
