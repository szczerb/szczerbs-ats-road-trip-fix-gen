# Dawson: two user-reviewed car-rest areas — ATS 1.61 r11

**Documented — user feedback, 2026-10-24:** r10's single tiny Dawson bay is unsatisfactory. The user did not attempt more precise maneuvers in the latest visit. Three top-down sketches request two broad areas: storefront and roadside/grass edge, the latter shown in two overlapping views. Regularize the hand-drawn shapes into straight rectangles. Verify this one station before wider heuristic work.

**Observed locally — delivered candidate:** [TASK-0051](../tasks/done/TASK-0051-expand-dawson-to-two-reviewed-parking-areas.md) builds a full Alaska-only replacement on the research branch. It replaces exactly the previous generated 3 × 6 m group with two native car-only rest groups, IDs 1 and 2. Independent marker positions are distinct; runtime two-icon visibility and easy activation are pending the user's check. This is a manually reviewed, source-pinned station correction, not a claim that automatic inference has generalized.

## Download and install

- [SCS](../../local_outputs/generated/2026-10-24_16-43-15/dawson-2-areas-alaska-expansion-1.2.3-ats-1.61-r11-experimental.scs), [ZIP with plan/instructions/receipts](../../local_outputs/generated/2026-10-24_16-43-15/dawson-2-areas-alaska-1.2.3-ats-1.61-r11-experimental.zip).
- [README and exact swap instructions](../../local_outputs/generated/2026-10-24_16-43-15/README.md), [two-area plan](../../local_outputs/generated/2026-10-24_16-43-15/dawson-two-areas.png), [SVG](../../local_outputs/generated/2026-10-24_16-43-15/dawson-two-areas.svg).
- [Independent finished-archive audit](../../local_outputs/generated/2026-10-24_16-43-15/independent-audit.json), [build receipt](../../local_outputs/generated/2026-10-24_16-43-15/build-receipt.json), [516 tests](../../local_outputs/generated/2026-10-24_16-43-15/tests-516.log), [SHA-256](../../local_outputs/generated/2026-10-24_16-43-15/SHA256SUMS.txt).

Disable only the old **Alaska Expansion r10 fix** and enable **DAWSON 2 AREAS r11** in its place, directly above original `Alaska_Expansion_v1.2.3.scs`. Keep the other seven r10 packages, current highest-priority N2 r2/r3 navigation overlay, original resources and separate tank/courier mods unchanged. Do not enable both Alaska fixes or resurrect A/B/C/C2/E/F/G experiments. No profile reset, separate-profile tour, live installation or game launch is performed/requested.

## Exact reviewed geometry

The private placement is `0x5ca1fea582800001`, `map/usa/sec-0029-0045.base`, alias `prefab.rspa9d76084`. Coordinates below are **station-local metres**, not player navigation instructions.

| Area | X extent | Z extent | Size | Purpose |
|---|---|---|---|---|
| Storefront | 9 to 26 | −21.15 to −14.7 | 17 × 6.45 m | Cover the sketched asphalt strip alongside the building and native parked-car positions. |
| Roadside | −13 to 10 | 7.25 to 9.85 | 23 × 2.6 m | One continuous strip beside the grass, leaving both driveway ends outside it. |

**Observed locally:** sampled asphalt height across each 6 × 6 grid is approximately 0.139318 m; all 72 points have the reviewed ground material. The roadside edge follows the grass proxy near Z=9.87058 and stops clear of the canopy's Z≈5.97 front. Storefront Z starts beyond the raised building/side-terrace edge near −21.24. These are regularized approximations to the sketches, supported by retained effective mesh/PPD landmarks rather than calibrated screenshot photogrammetry. Native parked NPCs remain; users can occupy free parts of the area.

Both new groups explicitly set native PPD partial-contact flag `0x4`, intended to allow contact with the area rather than requiring the previous precise full-containment pose. Range remains 3, reset delay/distance 0; native/source group parameters stay unchanged. The engine-tested vehicle shape, boundary tolerance, exact runtime marker presentation and fatigue outcome remain unknown. No physical painted lines or scenery objects are added. See [prior engine-parameter evidence](STATION_PARKING_HEURISTICS_1_61.md#activation-evidence).

## Preservation and reproducibility

The source is the retained final Alaska r10 package, SHA-256 `d3588d328a0254c0eb2e67892ee04f5118944a88879bcb6398f1429eb61050f8`. The fuel-preserving intermediate `prefab/rtfix/rtg822b7379.ppd` is unchanged. The old target must reconstruct exactly as that baseline plus the known old four-vertex group; any source, suffix, fuel or additional-group drift is rejected. Build the new target from this verified baseline and append two independent four-vertex cycles. The final PPD is SHA-256 `6c484f98dd1e6deb1877ed9c6fa339ebf599af2b8935594f5c60ca081b5ab948`.

The independent audit compares actual ZIP inventories/CRCs/hashes and raw PPD headers/records without invoking the new writer. Every member except the target PPD, manifest, description and report is byte-identical to r10. All sectors/services/nodes, original truck/bus triggers, fuel/spawn sections, other parking descriptors, country prices, private definitions/context state and approved icon are preserved. The alias is private to this one placement and has no path conflict in the other seven r10 packages. Existing aliases/IDs are retained deliberately; no graph rewrite or other-map regeneration is needed.

[Reviewed configuration](../examples/station-parking-dawson-two-reviewed-areas.json) and the README's reproduction command use `python -m ats_road_trip.station_parking.reviewed_area_workflow --source ... --config ... --experimental`. It writes a fresh timestamped full package and refuses source/pin drift or existing outputs. Retained PIM evidence is a generation dependency, not a runtime requirement. `append_car_parking_polygon` defaults are unchanged; automatic map-wide selection still uses its former behavior until a future verified policy change.

All 516 tests pass, including two independent cycles, contact flags, baseline/native opaque-byte preservation, default equivalence and malformed/overlapping/touching/drift refusal. A separate delegate passes 29 actual-archive checks. Static success does not constitute new in-game acceptance.

## User check and evidence

For this station only: confirm two icons and stop in ordinary positions across each marked region to check for the rest/engine-off prompt. No need for another town tour or per-pump checks. Further station/family changes wait for this verification.

The unchanged three screenshots, original names and hashes are retained in the [task's relative evidence links](../tasks/done/TASK-0051-expand-dawson-to-two-reviewed-parking-areas.md). Large evidence and generated mods are ignored/local-only in the retained research worktree; another checkout needs verified copies. Originals remain untouched.
