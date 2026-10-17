---
id: TASK-0016
title: Prepare a bounded car rest-eligibility experiment
status: backlog
priority: high
repositories:
  - .
depends_on:
  - TASK-0015
owner: shared
---

# Goal

Prepare a reversible experimental rest-eligibility candidate from the observed vehicle-filtered action mechanism, retaining truck/bus behavior and explicitly deferring manual confirmation.

# Context

**Observed locally:** `hud_parking` accepts `truck` and `bus`; `parking_car` accepts `car`, both using `hud_activate` numeric parameter 3. Concrete Western Canada/connector truck-stop placements retain `hud_parking` polygons even after fuel fixes. No player observation has yet identified an exact failed polygon or proved that missing map icons share the same filter.

# Scope

- Establish the effective trigger-action definition in the intended source stack and inspect relevant standalone map action parameters.
- Prefer a separately packaged one-field/action diagnostic retaining `truck`/`bus` and adding `car` to the effective `hud_parking` string parameters. Preserve all other actions; explicitly label its global scope. Do not assume duplicate unit declarations in a new file merge.
- Compare a localized polygon/private-action alternative if global definition override would erase another mod's changes or fails the cache/icon experiment.
- Keep fuel packages, fatigue settings, profiles and source geometry unchanged. No automatic game launch/install/save edit.

# Implementation Plan

1. GPT-6 Sol / medium implements a source-preserving bounded planner and tests.
2. GPT-6.1 Sol / high reviews effective-source safety and any polygon/cache uncertainty.
3. Root prepares the independent experimental artifact and later manual-test handoff without claiming runtime success.

# Acceptance Criteria

- Source hashes/order and the selected action mechanism are explicit, with no guessed reuse of fuel bit `0x4000`.
- Static checks prove original truck/bus/action parameters and other definitions are preserved, deterministic output and honest unsupported cases.
- Runtime work remains separate: prompt, actual car fatigue recovery, map/discovery icons, retained truck behavior and reload controls; record results or a bounded next step.
- The candidate remains optional and distinguishable from the petrol-price/station r2 packages.

# Verification

Not started. Research and selected placement evidence are in [the rest reference](../../reference/PASSENGER_CAR_REST_RESEARCH.md). A later user test is required; the user has finished gameplay for tonight.

# Links

- [Rest investigation](../done/TASK-0015-investigate-passenger-car-rest-areas.md)
- [Manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md)
- [Runtime validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
