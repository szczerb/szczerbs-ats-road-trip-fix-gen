---
id: TASK-0015
title: Investigate passenger-car rest eligibility in map mods
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0012
owner: agent
---

# Goal

Determine whether truck rest areas in the supplied maps lack car eligibility, identify the actual rest mechanism and a feasible bounded repair, or document the missing evidence.

# Context

**Documented — user report, 2026-10-18:** during Canadian testing the game issued fatigue warnings, but the user did not notice rest opportunities. Rest areas have map markers and an engine-off/action prompt, not an upright fuel-style world marker. The user has closed the game and will not test further tonight; no claim of manual repair validation is authorized.

# Scope

- Compare official large-vehicle/car rest actions, prefab polygons and relevant map items using versioned source evidence.
- Link selected actual mod placements to their rest-trigger descriptors rather than treating map-service counts as usability proof.
- Preserve original archives, profiles and historical fuel packages. No rest patch or automatic installation is part of this research task.

# Implementation Plan

1. GPT-6.1 Sol / high researches the action mechanism, official descriptors and safe experiment options; owns the canonical rest reference.
2. GPT-6 Luna / medium inventories map services and closes the placement-to-descriptor/action link for selected Canadian truck stops.
3. Root reviews findings, records the next bounded implementation and manual-test requirements, and integrates/commits documentation.

# Acceptance Criteria

- Distinguish fuel spawn flags, parking spawns/services, UI symbols and actual rest polygons/actions.
- Provide exact relevant game action definitions and at least one actual mod placement linked to an inspected rest action, or a concrete blocker.
- Separate static eligibility evidence from unknown prompt, fatigue recovery, discovery/icon, truck and reload behavior.
- Preserve a concrete next experiment and a later manual-test reminder; no fatigue reset or in-game test is assumed.

# Verification

2026-10-18: research complete, no rest patch or gameplay repair claimed. [Canonical source/mechanism/placement evidence](../../reference/PASSENGER_CAR_REST_RESEARCH.md) records all qualifications and next experiments.

- GPT-6.1 Sol / high inspected the cached official `def/world/trigger_action.sii`: `hud_parking` has `truck`/`bus`, `parking_car` has `car`; both use `hud_activate` and numeric parameter 3. The fields, not a guessed fuel bit, explain the separate eligibility mechanism.
- The same delegate parsed 194 selected official PPDs (191 gas plus three motels), checking exact trigger sections, finite geometry, reciprocal neighbors and groups. Found 31 `parking_car` and 23 `hud_parking` polygon groups. None has a Parking/type-10 spawn; the motels have no spawn records. These counts are descriptor sample groups, not physical placed parking totals.
- GPT-6 Luna / medium reused source-pinned full map scans and parsed the connector sectors. Parking-category service counts were 35/6/70/27/4/0 for ATS Expansion/Alaska/Reforma/Western Canada/ProMods/connector. These are not car-rest usability counts.
- The inventory delegate closed actual placement links: WCE `map/usa/sec-0018-0030.base`, prefab `0x57320980a1000001`, and connector `map/usa/sec-0020-0022.base`, prefab `0x5732207b9a800001`, both resolve inspected `prefab.us_gas_08` / `nm_truckstop1_chemron.ppd`, with four `hud_parking` vertices and no type-10 Parking spawn. The `_rt` alternative has a car polygon at different geometry, so swapping whole descriptors is unsupported.
- Root independently inspected the action definitions and both original r1 fuel-clone PPDs: private aliases `rtg253fcfb3` and `rtgb9a7dd96` each retain four `hud_parking` vertices and zero `parking_car`. Fuel generation did not change these rest filters.
- Source evidence is under `local_outputs/work/2026-10-18_01-22-17/rest-inventory/` and `local_outputs/work/2026-10-18_01-22-46/rest-research/`; root confirmation is `local_outputs/work/2026-10-18_01-27-24/fuel-fix-preserved-rest-polygons.json`. Primary SCS authoring docs and independent parser source are linked in the reference.
- No game/editor action, fatigue reset, source edit, global rest-definition override or generated rest package was performed. Exact user-visited rest polygons, map-icon behavior, prompt/fatigue recovery, truck control and reload remain pending. [TASK-0016](../backlog/TASK-0016-prepare-rest-eligibility-experiment.md) scopes the next bounded implementation.
- A one-time thread reminder is scheduled for **2026-10-18 18:00 Europe/Warsaw**. The [manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md) and agent instructions preserve reminders at subsequent handoffs; no further manual testing is expected tonight.

Final integration checked 62 Markdown files, 446 relative links, 18 heading fragments and 16 task metadata/status/dependency graphs with no errors. Twelve input identities remain unchanged, 25 artifact paths pass Git exclusion checks, no supplied/generated assets are tracked, and `git diff --check` passes. Evidence: `local_outputs/work/2026-10-18_01-27-24/documentation-qa.json`. The separate pricing implementation is verified independently; its tests do not establish rest behavior.

# Links

- [Rest research](../../reference/PASSENGER_CAR_REST_RESEARCH.md)
- [Runtime validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Source priority](../../reference/CONNECTOR_FUEL_FIXES.md)
- [Next bounded experiment](../backlog/TASK-0016-prepare-rest-eligibility-experiment.md)
