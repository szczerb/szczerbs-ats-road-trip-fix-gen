---
id: TASK-0038
title: Investigate missing passenger-car parking icons
status: active
priority: high
repositories: [.]
depends_on: []
owner: shared
---

# Goal

Identify why r8 passenger-car parking icons are absent in the reported Canadian/Alaskan areas and sparse in Montana; prepare a supported repair once the rendering mechanism is established.

# Context

**Documented — user clarification, 2026-10-18:** this is missing world-map icons, without a physical rest attempt. The user is in Mexico completing a job and questions the earlier late-night rest-success report. Preserve that earlier report as history, but reopen rest confidence. Refueling, jobs and tank acceptance are separate.

# Scope

- **Subsequent explicit goal authorization:** implement and test the supported repair, independently review code/archives, prepare local r9 replacements, update documentation and commit locally. Do not publish, push, install, launch ATS or modify a profile.
- Implementation evidence is under ignored `local_outputs/work/2026-10-18_23-37-08/` and delegated timestamped inventory/mechanism directories. Work branch: `codex/car-parking-icons`.

- Read-only installed r8/package/log inspection and screenshot review; investigate map-marker representation separately from rest eligibility.
- Preserve original inputs, outputs and live profile. No game launch, installation, save changes or immediate manual test request.
- New artifacts: ignored `local_outputs/work/2026-10-18_23-24-54/`.

# Implementation Plan

1. Check installed hashes, active source-relative priority and r7/r8 gameplay equality.
2. Review rest mutations and primary marker documentation. GPT-6 Luna / high owns read-only implementation/icon research; root owns integration and documentation.
3. Trace representative source marker/trigger pairs and determine ATS 1.61 car-mode filtering before proposing edits. Do not transfer the fuel `0x4000` hypothesis to parking.
4. Keep icon display and physical prompt/fatigue results separate; runtime verification may follow when convenient for the user.

# Acceptance Criteria

- Establish a supported explanation for missing car icons and record its scope.
- Verify any repair preserves original rest geometry, truck access, fuel and context resources.
- Do not label the issue fixed from archive counts or static eligibility alone.

# Verification

**Observed locally — subsequent implementation research:** root and GPT-6 Sol/high independently inspected the installed ATS executable (`c60e8ee02cc97b3cc6ef8c6298bb5c3c23c4ffd330b8185b646fb1b608a3c7b4`) without running/modifying it. Both prefab and standalone map-marker paths classify truck/bus before car, explaining why the mixed r8 action lacks a separate car category. Native action names are dynamically resolved; no overlay/fuel flag change is required. [ADR-0017](../../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md) records the now-supported replacement strategy.

Implementation in progress: separate car-only prefab groups and standalone Trigger twins preserve original geometry/actions; fresh UIDs, visibility/layer closure and fuel overlays are validated. Independent review identified and corrected mixed-mode proximity suppression and source tag preservation. GPT-6 Luna/medium owns paired source inventory, GPT-6 Luna/high owns bounded regression-test changes, GPT-6 Sol/high owns mechanism and independent review, root owns production/integration/docs/artifacts.

**Observed locally — 2026-10-18:** all seven installed map r8 archives match the delivered archives by SHA-256. Every `map/`, `prefab/` and `def/` resource is byte-identical to its r7 predecessor. The 22:49:31 game-log session lists all seven r8 fixes active in the expected source-relative sequence. This excludes an r7-to-r8 gameplay payload change; it does not exclude an earlier defect or uninspected effective-resource interaction.

**Observed locally:** embedded rest reports contain 31 Alaska, 202 Western Canada, 95 ProMods, 41 connector, 766 ATS Expansion and 119 Reforma additions. These count action edits per package, not visible icons or unique effective-world sites. OtherMaps is price-only. Private rest actions contain `hud_activate`, numeric parameter 3 and `truck`, `bus`, `car` strings.

**Observed locally:** root inspected `ats_20261018_232603_00.png` through WSL. **User-corrected geography:** the visible bed icons are in Washington, USA; none appear north of the Canadian border at the shown zoom. Root's initial southern-BC description was incorrect and has been corrected in the evidence. Alaska is outside this screenshot; it does not show all Montana.

**Observed locally:** second screenshot `ats_20261018_232848_00.png` shows dense Mexican icons. **Hypothesis — user:** the problem affects all fixes except Reforma. The source-plus-halo Reforma report contains 1,342 existing car rests and 961 truck polygons suppressed by existing neighbors, versus Alaska's zero existing car rests and all 31 truck polygons selected. This supports investigating native-versus-generated marker behavior; it does not identify the visible icons' provenance.

**Observed locally:** eleven logged higher-priority Workshop directory inventories and the opaque No DeadEnds archive have no exact r8 sector/private-resource collisions. This is a bounded path check, not a complete semantic runtime audit.

**Observed locally:** the saved log has five vehicle-mode rejection messages between session offsets 00:06:39 and 00:07:42. Both original and private actions share the label “Parking - Large vehicles”; these messages contain no trigger UID/location/token. They cannot be attributed to the screenshot, Canada, Alaska or a generated action.

**Observed locally — root review of delegate findings:** rest edits retarget action tokens; they do not create Parking services or Map Overlays. **Documented:** SCS distinguishes sleeping-area triggers from map-icon overlays. **Unknown:** whether generated private actions are recognized for car-map icon discovery, whether a separate marker is needed, and the exact ATS 1.61 vehicle-mode filter. Absence of explicit marker edits alone does not prove the cause. See the [evidence reference](../../reference/CAR_PARKING_ICON_INVESTIGATION.md).

2026-10-18: active investigation; no supported marker repair or in-game validation yet. Next work is a source/stock comparison of marker and action representations, not a requested interruption of the user's current job. No production/package changes or utility-test rerun for this documentation milestone.

Documentation QA: 11 changed/new documents, 270 relative links/heading fragments, seven installed/r7 equality results and seven scratch-evidence exclusions pass; `git diff --check` passes. Root preserved the original positive report with an explicit later qualification and updated current-facing acceptance language. Evidence: `documentation-qa.json` in the ignored run directory.

# Links

- [Icon investigation](../../reference/CAR_PARKING_ICON_INVESTIGATION.md)
- [Gameplay results](../../reference/VALIDATION_RESULTS.md)
- [Manual validation](TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [R8 handoff](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md)
