---
id: TASK-0039
title: Research gas-station car rest areas
status: done
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

**Observed locally — 2026-10-19:** a bounded static prototype now traces Dawson City's WCE v1.7.3 `us_gas_08` placement (`map/usa/sec-0029-0045.base`, UID `0x5ca1fea582800001`) and implements explicit `painted_bays` and `unmarked_geometry` methods. In this standalone WCE source/fuel-only baseline, both methods produce a candidate and preserve the existing descriptor records. The painted method identifies four parallel separators in the installed model and derives three spaces; the unmarked method derives a rectangle and approach from source map polygons and sampled model geometry. Neither result establishes runtime safety or gameplay behavior.

**Observed locally — combined-stack correction (2026-10-19):** the same Dawson UID/sector path is overridden by the higher-priority Alaska Expansion 1.2.3 source. Its archive SHA-256 is `d879c245c1bc8b88c9a884d88952ccaad88b58ce759f665832fd0b664a6200fb`. Consequently, the WCE-pinned policies and standalone outputs are diagnostic evidence, not the source-winning combined-stack fix. Both final Alaska-based alternatives have been generated through the public CLI and independently audited. The controlled-test configuration replaces Alaska r9 only; WCE r9 stays enabled at its own priority. Runtime car-rest behavior remains **Unknown**; ATS has not been launched and no profile or live mod installation was changed.

# Scope

- Inspect the exact Dawson City station placement and nearby geometry, and separately research representation of painted car bays.
- Develop a separate deterministic, optional processor that acts only on explicitly selected individual stations, if evidence permits.
- Preserve source geometry and original truck/bus/shared rest actions; do not use the 1,000-unit or density rules, integrate the existing rest processor, or clone truck geometry as fallback.
- Record findings in [GAS_STATION_CAR_REST_RESEARCH.md](../../reference/GAS_STATION_CAR_REST_RESEARCH.md). Keep user screenshots as documentation evidence under `docs/reference/images/gas-station-car-rest/dawson-city/`.
- Do not install mods, modify profiles, or run the game. Provide a manual handoff for later user testing if a candidate is generated.

# Implementation Plan

1. Inventory the exact Dawson City station placement and potential geometry, with source/version provenance.
2. Identify how painted car bays are represented and whether a native car-only rest marker can be safely associated with a selected station.
3. **Completed:** implement the separate deterministic optional processor with explicit station selection and method, source pinning, bounded geometry checks, and fail-closed behavior for unsupported variants/data.
4. **Completed:** add automated checks for painted separator extraction, mesh sampling/candidate exclusions, station selection, source preservation, deterministic output and unsafe inputs; document manual test steps.
5. **Completed:** rebase Dawson on the winning Alaska source plus its fuel-only baseline; audit complete supplied-stack precedence, actual generated package contents, fingerprints, original records and effective alias changes. Deliver both alternatives, plans and controlled-test instructions together.

Delegation and review: bounded placement inventory / CLI integration / planner tests used GPT-6 Luna with high effort; painted-bay/model-format research and sample inspection used GPT-6 Luna with high effort; initial documentation and later independent package/preservation audits used GPT-6 Luna with medium effort. Each assignment had explicit file ownership. The root reviewed findings, implementation diffs, source-priority correction, sample limitations, and independent audit evidence before integration. Final review identified and corrected empty-paint input support and missing visible rejection explanations in the SVGs. The root owns final integration; no agent installed or ran the game.

# Acceptance Criteria

- [x] The report distinguishes documented, observed locally, hypothesis and unknown claims, and records source, version and inspection date where available.
- [x] Both painted car bays and the Dawson unmarked-station case are addressed; the explicit-selection and no-fallback constraints are preserved.
- [x] A separate, source-pinned processor, meaningful tests and two actual Alaska-based packages exist. Full supplied-stack and independent package audits establish bounded static preservation. The WCE outputs are retained only as standalone diagnostic evidence.
- [x] Any generated candidate has a manual handoff that tests car access and truck/bus/shared behavior separately; no game/profile/install operation is performed here.

# Verification

- **Observed locally — 2026-10-19:** `PYTHONPATH=src python3 -m unittest discover -s tests -q` passed 324 tests at implementation milestone `4aaeea8` and all **326 tests** after final integration; targeted painted-parking detector tests passed after bank-spacing, bay-width and transitive-cluster validation was strengthened. WCE standalone painted and unmarked samples were exercised at Dawson and a second transformed placement of the same model. A distinct Chemron three-row station uses the default variant plus five additional parts and is blocked before proposal; direct geometry diagnostics yielded no accepted bank/proposal. These bounded samples do not establish support for other prefab families.
- **Observed locally — 2026-10-19:** final painted/unmarked runs `2026-10-19_02-02-32` and `2026-10-19_02-04-49` each passed **38 independent package checks**: archive integrity, source pinning, exactly selected model-token change, original node/item/service and descriptor record preservation, fresh native car-only geometry, alias targets, and context coverage. Alaska r2 versus canonical final r9 has identical 114 service records across 18 sector paths and identical country payload. Both source paint and geometry-only plans were rendered and visually inspected, including candidate IDs/rejection causes and a detail inset. An asphalt-only authored fixture proves geometry-only planning without paint or parked locators. All archive hashes and reproduction commands are in the handoff. The local bundle has two SCS alternatives, plans/previews, pinned configs, audits and instructions; CRC and every member byte/hash were checked. Runtime rest prompt, fatigue recovery, reload behavior, physical collision and access remain untested and are reserved for the user's later manual test.
- **Observed locally — 2026-10-19:** copied the three user-supplied PNG screenshots from the main checkout into the assigned reference image directory and verified all three SHA-256 digests match. Screenshots are context evidence only and do not prove source geometry or runtime behavior.

# Links

- [Final package handoff, fingerprints and reproduction](../../reference/GAS_STATION_CAR_REST_POC_HANDOFF.md)
- [Research and screenshots](../../reference/GAS_STATION_CAR_REST_RESEARCH.md)
- [Independent processor decision](../../architecture/decisions/ADR-0018-isolate-source-pinned-station-parking-poc.md)

- [Existing rest-area research](../../reference/PASSENGER_CAR_REST_RESEARCH.md)
- [Existing rest processor coverage and limits](../../reference/COMPATIBILITY_PROCESSORS.md)
- [Separate car-marker geometry decision](../../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md)
- [TASK-0038: Repair missing car parking markers](../done/TASK-0038-investigate-missing-car-parking-icons.md)
