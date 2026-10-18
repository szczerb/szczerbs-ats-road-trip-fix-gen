---
id: TASK-0024
title: Deliver the overnight standalone courier and map compatibility test batch
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0019
  - TASK-0023
owner: shared
---

# Goal

Prepare the newly authorized morning test delivery: a standalone practical-cargo eligibility mod and updated fuel/price/rest fixes for all seven supplied map/connector source families, preserving original courier context classifications.

# Context

**Documented — user direction, 2026-10-18:** proceed unattended with implementation and prepare new mods for morning testing, incorporating the discussed features. This authorizes generation, not live installation, profile/economy changes or claims of successful gameplay.

# Scope

- Implement and exercise TASK-0019 and TASK-0023.
- Generate map revision 4 and standalone eligibility revision 0 in a new ignored timestamped run, retaining previous artifacts.
- Preserve explicit source/load order, original truck interactions and nodes, original shared rest actions, rating/economy fields outside the reviewed price policy and all transfer jobs.
- Independently inspect outputs and assemble one delivery ZIP with checksums, source-specific placement instructions and pending manual controls.
- General map courier repair and a global job-budget change remain unsupported hypotheses; do not invent them as part of the batch.

# Implementation Plan

| Assignment | Actual model / effort | Ownership |
| --- | --- | --- |
| Configurable byte-preserving courier eligibility core/tests | GPT-6 Sol / medium | courier_eligibility.py and its tests |
| Alias context preservation, processor integration and legacy rest-layout triage/tests | GPT-6 Sol / medium | prefab_contexts.py, processors.py, rest_stops.py and related tests |
| Input/order preparation, official category check and independent output review | GPT-6 Luna / medium | Ignored evidence only |
| Standalone workflow, CLI/writer integration, batch generation, handoff/docs and commit | Root | Remaining files and ignored run |

# Acceptance Criteria

- Supported complete-coverage packages are generated with distinct names/versions, source/config provenance and no unexpected resource or context-unit collisions.
- The standalone default changes 58 reviewed job definitions only; all nine transfer definitions and non-target bytes remain unchanged.
- Every generated prefab alias retains exact supported original classifications; original exclusions and unknowns are not reclassified by guessing.
- Truck fuel behavior is preserved structurally, petrol values are finite positive, and rest changes follow the accepted 1,000-unit XZ rule with unchanged geometry/shared actions.
- Automated tests, independent source/output checks, input immutability, metadata and documentation/task checks pass before delivery.
- The user receives one clear test handoff distinguishing static verification from manual car/truck purchases, billing, rest, reload and courier completion.

# Verification

2026-10-18: implementation and all eight candidates accepted statically. Full authored suite: **233 passing tests**, `local_outputs/work/2026-10-18_04-08-02/tests-final.log`. Independent per-package audits under `local_outputs/work/2026-10-18_03-47-10/batch-review/` verify CRC/resources, original nodes/services, unchanged r2 payloads, rest action-only/geometry invariants, actual private action parameters, original context units and petrol/non-petrol fields. Final ATS evidence is `ats-expansion-final-deep-verification.json`; courier evidence is `courier-verification-final.json`.

Seven r4 packages and standalone r0 are frozen in `local_outputs/work/2026-10-18_04-00-48/delivery-candidates.json`. The winning-stack graph passes across 583 effective paths: all **2,202** surviving generated truck targets have co-located car twins, and all **3,518** checked car services have reciprocal nodes. Namespace checks pass for **556** definition units and 1,047 definition/descriptor paths. WCE retains **380** Company records and accounts for all **14** company-parent classifications.

Delivery ZIP: `local_outputs/generated/2026-10-18_04-25-54/szczerbs-road-trip-test-batch-ats-1.61-map-r4-courier-r0-experimental.zip`, **68,147,151 bytes**, SHA-256 `11688bd8f64b2183615c803106c2f1fd13c4df513f1566e98ca6920cf5602902`. It contains eight mods, instructions, checksums and manifest; all embedded bytes match final reviewed packages and CRC checks pass. Shared source versions/identities and all 12 input/sidecar identities remain unchanged. Assets and outputs stay excluded from Git.

Initial blocked attempts remain retained. Legacy source layouts were triaged with exact geometry/flags preserved; [ADR-0012](../../architecture/decisions/ADR-0012-preserve-irregular-source-rest-geometry.md) records conservative action-only handling of one irregular ATS truck placement. No source defect was silently repaired or hidden.

Documentation checks pass for **85 Markdown files, 646 local links, 25 heading fragments, 24 tasks (23 done, one active), 12 input identities and 26 excluded artifacts**, with zero errors. They validate the reading path, links/fragments, task metadata/status/dependencies and exclusions. Final counts/log are in `local_outputs/work/2026-10-18_04-00-48/documentation-qa.json`. No game test, installation, profile edit or economy reset occurred. Manual TASK-0007 remains active; existing 18:00 Warsaw reminder is unchanged.

# Links

- [Current delivery and full handoff](../../reference/OVERNIGHT_TEST_BATCH_1_61_R4.md).

- [Context preservation](../done/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md)
- [Standalone generator](../done/TASK-0023-build-configurable-courier-eligibility-generator.md)
- [Planned policy](../../reference/COURIER_ELIGIBILITY_GENERATOR_PLAN.md)
- [Manual tests](../../reference/MANUAL_TEST_CHECKLIST.md)
