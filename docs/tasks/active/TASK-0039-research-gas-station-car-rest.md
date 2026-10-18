---
id: TASK-0039
title: Research gas-station car rest areas
status: active
priority: medium
repositories:
  - .
depends_on: []
owner: shared
---

# Goal

Determine whether individually selected gas stations can receive safe passenger-car rest access, including both painted car parking bays and unmarked station geometry such as the reported Dawson City case. Produce a bounded, optional processor proof of concept only where source evidence supports it; otherwise document precise blockers and the next evidence needed.

# Context

**Documented — project boundary:** the existing rest processor adds car eligibility using a local 1,000 game-world-unit proximity rule. This research has a separate user direction: individual explicit station selection, no distance/density rule, no integration with existing rest policy, and no truck-geometry clone fallback. Existing shared rest actions and truck/bus behavior must remain outside this experiment.

**Unknown — 2026-10-19:** the ATS/map definitions for gas-station lots, painted bays and unmarked rest-compatible geometry have not yet been traced. Three user-provided screenshots show a Dawson City station/cafe and city-map context, but do not establish the underlying prefab geometry, rest actions, source version or runtime car-rest behavior.

# Scope

- Inspect the exact Dawson City station placement and nearby geometry, and separately research representation of painted car bays.
- Develop a separate deterministic, optional processor that acts only on explicitly selected individual stations, if evidence permits.
- Preserve source geometry and original truck/bus/shared rest actions; do not use the 1,000-unit or density rules, integrate the existing rest processor, or clone truck geometry as fallback.
- Record findings in [GAS_STATION_CAR_REST_RESEARCH.md](../../reference/GAS_STATION_CAR_REST_RESEARCH.md). Keep user screenshots as documentation evidence under `docs/reference/images/gas-station-car-rest/dawson-city/`.
- Do not install mods, modify profiles, or run the game. Provide a manual handoff for later user testing if a candidate is generated.

# Implementation Plan

1. Inventory the exact Dawson City station placement and potential geometry, with source/version provenance.
2. Identify how painted car bays are represented and whether a native car-only rest marker can be safely associated with a selected station.
3. Implement a separate deterministic optional processor only if both the source interfaces and safety checks are evidenced; otherwise specify blockers and a concrete geometry plan-view approach.
4. Add meaningful automated checks for station selection, source preservation, deterministic output and unsafe/unknown data, and document a manual test handoff.

Delegation for this task: station placement inventory — GPT-6 Luna/high, read-only exact Dawson placement; painted-bay representation research — GPT-6 Luna/high; initial documentation and screenshots — GPT-6 Luna/medium; implementation and integration — root agent. Each contributor owns only their assigned files; delegated findings require review before acceptance.

# Acceptance Criteria

- The report distinguishes documented, observed locally, hypothesis and unknown claims, and records source, version and inspection date where available.
- Both painted car bays and the Dawson unmarked-station case are addressed; the explicit-selection and no-fallback constraints are preserved.
- A real static proof of concept and meaningful tests exist if safe source evidence permits. If not, the report gives precise blockers, a plan-view geometry approach and next evidence required without claiming a fix.
- Any generated candidate has a manual handoff that tests car access and truck/bus/shared behavior separately; no game/profile/install operation is performed here.

# Verification

- **Pending:** exact station placement and painted-bay source inspections; implementation decision; any meaningful processor tests.
- **Observed locally — 2026-10-19:** copied the three user-supplied PNG screenshots from the main checkout into the assigned reference image directory and verified all three SHA-256 digests match. Screenshots are context evidence only and do not prove source geometry or runtime behavior.

# Links

- [Existing rest-area research](../../reference/PASSENGER_CAR_REST_RESEARCH.md)
- [Existing rest processor coverage and limits](../../reference/COMPATIBILITY_PROCESSORS.md)
- [Separate car-marker geometry decision](../../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md)
- [TASK-0038: Repair missing car parking markers](../done/TASK-0038-investigate-missing-car-parking-icons.md)
