---
id: TASK-0040
title: Identify the Dawson runtime result and label experiment variants
status: done
priority: high
repositories: [.]
depends_on: [TASK-0039]
owner: shared
---

# Goal

Identify which Dawson r0 variant produced the user-reported rest interaction, explain the paint/geometry evidence and enlargement limits, and make alternative packages visibly distinguishable in Mod Manager. Record the variant-identity rule in project instructions.

# Context

**Documented — user report, 2026-10-19:** both archives were installed together but enabled separately through Mod Manager. Identical descriptions and truncated titles obscured their identities. The first trial showed a full-screen map icon but no usable rest position was found; the second allowed a rest interaction at the building-side dark asphalt strip. Screenshot `ats_20261019_182957_00.png` records the reported left boundary. The user sees no painted car bays and proposes extending left along the building while retaining pump access. These statements do not establish fatigue recovery or every load/reload/truck control.

# Scope

- Preserve the existing branch/worktree isolation and gameplay geometry during this follow-up.
- Inspect the screenshots and read-only current game log; compare exact package identities and source-model geometry.
- Record active visual-model overrides as evidence rather than assuming the supplied source stack equals the user's entire profile.
- Correct leading display-name/filename/description variant labels and deliver audited metadata-only copies.
- Record a universal experimental-variant identification rule in AGENTS, working agreements and metadata documentation.
- Assess enlargement as a proposed next experiment; do not change the parking footprint from screenshot evidence alone.

# Implementation Plan

1. Read supplied screenshots, preserve ignored evidence with hashes, compare candidate coordinates and inspect actual active-model parts.
2. Correlate the exact screenshot log event with persistent gameplay mounts and small-vehicle parking trigger events, ignoring temporary Mod Manager preview mounts.
3. Add A LINES/B GEOMETRY identity through one production metadata helper; retain exact source names, r0 and experimental scope.
4. Repackage original archives with that helper, audit all gameplay bytes and descriptions, run meaningful workflow checks, and document the result.

Delegation: GPT-6 Luna/high owns read-only geometric/model/log investigation; GPT-6 Luna/medium owns `station_run.py` metadata and its existing workflow tests. Root owns documentation, instruction changes, artifact repackaging, audit and integration. Root reviews delegated findings and diffs. No game/profile operation is authorized or performed.

# Acceptance Criteria

- [x] Exact runtime attribution is supported by screenshot/log chronology or explicitly remains uncertain.
- [x] Visible image content, reported interaction, static geometry, and unknown fatigue/collision behavior are distinguished.
- [x] Both alternatives are recognisable at the start of title, filename and description, with a clear one-at-a-time instruction.
- [x] Corrected archives preserve every gameplay member and keep original r0 archives untouched.
- [x] Instructions, dated feedback, current state and local handoff are updated, and relevant checks pass.

# Verification

- **Observed locally:** both supplied UI screenshots and the gameplay screenshot were opened; copies and SHA-256 records are under `local_outputs/work/2026-10-19_18-49-11/dawson-user-feedback/`.
- **Observed locally:** installed original PoC hashes match the previously delivered painted/unmarked r0 archive hashes. The current game log is retained read-only in that same ignored run directory.
- **Observed locally — exact attribution:** the preserved log mounts painted at `00:07:19.388`, records repeated small-vehicle parking actions through `00:12:22.604`, and records the exact supplied screenshot at `00:12:30.136`/written `00:12:33.251`. Geometry's next mount is `00:13:11.284`, after capture. Persistent gameplay mounts and explicit unmounts were independently reviewed; transient manager preview mounts were excluded. The successful screenshot therefore belongs to A / painted_bays.
- **Observed locally — effective model:** the active Real companies 4.02.01 PMG/PMD differs from the base model originally inspected. Selective conversion shows the original car-bank separator cluster absent; the detector returns no painted banks in the replacement model. Both relevant parts are visible, and two parked-car locators occupy the successful strip. B's static surface check still passes; its no-position-found result remains a runtime observation rather than an established geometry failure. The root reviewed model hashes, parsed the active mesh and reran the detector.
- **Observed locally — corrected deliverables:** metadata helper and real SCS manifests, filenames and descriptions distinguish A/B from their first characters. Both labelled copies retain all 25 gameplay resources byte-for-byte and the 28-member set; only manifest, description and internal report change. Both ZIP CRCs, all member comparisons, original archive hashes and final bundle hashes pass. `PYTHONPATH=src python3 -m unittest tests.test_station_run -q` passes six tests; full discovery passes all 326. Whitespace checks and 249 documentation-link checks pass; branch integration retains the clean main checkout. Neither parking polygon was enlarged and no installed mod/profile was edited.

# Links

- [Original bounded research](../done/TASK-0039-research-gas-station-car-rest.md)
- [Feedback and attribution](../../reference/GAS_STATION_CAR_REST_FEEDBACK_2026_10_19.md)
- [Metadata contract](../../reference/MOD_METADATA.md#experimental-variant-identity)
