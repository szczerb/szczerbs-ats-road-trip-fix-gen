---
id: TASK-0016
title: Implement proximity-filtered car rest eligibility
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0015
owner: shared
---

# Goal

Implement deterministic localized car rest eligibility for source-map truck/bus polygons only where no existing car rest polygon lies within 1,000 game-world units in the XZ plane. Retain truck/bus behavior and explicitly defer manual confirmation.

# Context

**Observed locally:** `hud_parking` accepts `truck` and `bus`; `parking_car` accepts `car`, both using `hud_activate` numeric parameter 3. Concrete Western Canada/connector truck-stop placements retain `hud_parking` polygons even after fuel fixes. No player observation has yet identified an exact failed polygon or proved that missing map icons share the same filter.

# Scope

- **Documented — user instruction, 2026-10-18:** replace the previously proposed global action diagnostic with a local proximity rule. Use straight-line game-world distance, not navigation distance; no map-scale conversion is implied.
- Index original effective car rest areas in source-owned sectors and a nearby halo resolved through supplied baseline/dependencies. Use polygon distance, inclusive 1,000-unit boundary; generated car areas must not suppress other candidates in the same run. The user explicitly accepts extra permissions from missed neighbors beyond the inspected perimeter; no full-world scan is required.
- Preserve original shared truck/bus action definitions and polygon geometry/topology. Clone the reviewed action with its existing vehicle parameters plus `car`, then retarget only selected polygon references through private per-placement prefabs or standalone actions; do not modify every instance of a shared prefab.
- Compose with fuel-generated aliases/resources; block unsafe/unsupported source edits and disclose neighbor omissions and the bounded perimeter rather than claiming full-world coverage.
- Keep fatigue settings, profiles and input archives unchanged. No automatic game launch/install/save edit.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Rest geometry, effective spatial analysis, local cloning and regression tests | GPT-6.1 Sol / high | rest_stops.py and its tests |
| Independent coordinate/action/completeness review | GPT-6 Sol / medium | Read-only evidence review |
| Integration, metadata, documentation, real-input checks and local commit | Root | Shared integration and authored references |

# Acceptance Criteria

- Source hashes/order and the selected action mechanism are explicit, with no guessed reuse of fuel bit `0x4000`.
- Test the exact 1,000-unit boundary, intersecting/large polygons, cross-package and cross-sector car neighbors, unchanged source-snapshot decisions, and different decisions for two placements sharing one descriptor.
- Static checks prove original truck/bus/action parameters and other definitions are preserved, deterministic output and honest unsupported cases.
- Runtime work remains separate: prompt, actual car fatigue recovery, map/discovery icons, retained truck behavior and reload controls; record results or a bounded next step.
- The candidate remains optional and distinguishable from the petrol-price/station r2 packages.

# Verification

2026-10-18: deterministic implementation and static acceptance complete under the user-approved bounded search. Runtime acceptance remains in TASK-0007; the user has finished gameplay for tonight.

- GPT-6.1 Sol / high implemented the rest planner and 36 authored tests. GPT-6 Sol / medium independently audited activation flags, placement/action semantics and actual outputs. Root integrated metadata, documentation, real generation and verification. [Research evidence](../../reference/PASSENGER_CAR_REST_RESEARCH.md) remains distinct from implementation acceptance.
- Full suite: `PYTHONPATH=src python3 -m unittest discover -s tests -v`, **179 passed**. Cases cover polygon edges/interiors, inclusive radius, per-placement and per-group decisions, immutable car index, map namespaces, standalone polygons/spheres, source ownership, private action parameters, numeric HUD equivalents, flags/guards, boundary omissions, empty reservations, deterministic output, idempotence, source blockers and prior processor preservation.
- The first whole-world probe inspected 2,754 winning sector files and refused output on ordinary standalone activation flags. Primary Trigger.cs and a separate audit of 1,800 cached files established the correct flag mask and one two-node sphere among 6,478 cached triggers; these counts include lower-layer copies. Fixed the parser and adopted the user's explicit acceptance of boundary over-additions rather than retaining a global absence requirement.
- Actual WCE combined generation inspected **952 source + 52 halo** files, no omissions/blockers. Its bounded index has 99 original car areas; 206 truck/bus areas yield **202 additions across 198 placements**, with four suppressed by nearby car areas. Fuel retains 288 car interactions and six petrol fields. [Candidate and hashes](../../reference/COMPATIBILITY_PROCESSORS.md).
- Independent complete-package verification passed ZIP/metadata/resource hashes. All 179 private PPDs change only selected action tokens, preserving geometry/topology/spawns; selected sectors retain all original nodes and fuel services. Private action retains truck/bus and adds car; the shared action file is absent from output. Evidence: `local_outputs/work/2026-10-18_02-18-17/verification/`.
- Two source-pinned real WCE/connector fixture sectors independently pass rest and r2 fuel composition. A separately labelled synthetic car neighbor at 65.221 units suppresses generation. These bounded fixture observations are not real-map neighbor-absence evidence. Reports: `local_outputs/work/2026-10-18_02-03-10/rest-smoke/`.
- Original input identities and reused read-only extraction-cache hashes remain unchanged. No game launch, installation, profile edit, fatigue/economy reset or manual runtime test occurred. Scope omissions/boundary false positives remain disclosed; complete whole-world coverage is not claimed.

Final integration checked 65 Markdown files, 477 relative links, 18 heading fragments and all 17 task metadata/status/dependency graphs: no errors. Twelve input identities are unchanged, 16 artifact paths pass Git exclusions, no supplied/generated assets are tracked, and whitespace checks pass. QA: `local_outputs/work/2026-10-18_02-01-14/documentation-qa.json`. Later user tests must establish prompt, fatigue recovery, retained truck behavior, icons and reload; pending fuel price/billing checks remain separate.

# Links

- [Rest investigation](../done/TASK-0015-investigate-passenger-car-rest-areas.md)
- [Manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md)
- [Runtime validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
