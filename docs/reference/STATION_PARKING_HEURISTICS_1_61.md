# Effective station-parking heuristics — ATS 1.61

Research date: 2026-10-19. Implementation and actual-case verification are in progress in [TASK-0044](../tasks/active/TASK-0044-improve-effective-station-parking-heuristics.md), on the retained station research worktree. This is a local research record, not a runtime usability claim.

## Activation evidence

**Documented — primary authoring source:** polygon Range is vertical; Sphere Trigger instead uses it as radius. Partial Activation allows border contact. [SCS prefab trigger locator documentation](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators), inspected 2026-10-19, last edited 2025-08-06; shared engine authoring documentation does not specify the complete ATS 1.61 vehicle test. The PPD partial flag is bit `0x4`; standalone Trigger flags use a different schema. [TruckLib PPD reader](https://github.com/sk-zk/TruckLib.Models/blob/master/TruckLib.Models/Ppd/TriggerPoint.cs).

**Observed locally — ATS 1.61.3.18:** A/B use polygon flags 0, range 3, reset 0/0. The retained native inventory contains 124 car vertices / 31 groups with those same parameters. Native Chemron `_rt` is approximately 8.579 × 7 units; old B is 3 × 6. No explicit yaw field is emitted in these PPD records. A wider valid-pose window under full containment is a hypothesis, not proof of the vehicle shape.

**Unknown:** the tested vehicle point/shape, containment tolerance, detailed vertical plane semantics and any heading dependence beyond shape projection. The three B images and action log show nearby prompt transitions, but no calibrated vehicle coordinates. They do not prove a center, bumper, wheel or whole-body test. Source hashes, bounded executable trace addresses and evidence limits are in ignored local-only `local_outputs/work/2026-10-19_21-21-05/activation-research/activation-findings.md`.

Minimal later diagnostic: compare old B with an otherwise byte-preserving alternative setting only PPD partial bit `0x4` on its four new vertices. Stop at each step across a long and short edge, then repeat 180° and 90° headings with a stable vehicle reference; retain N2 and the same stack/vehicle. A larger contact window would support contact-versus-containment, while heading dependence could indicate an extended shape. Speed, engine and fatigue gates must remain controlled. This flag is not the default usability fix.

## Effective Dawson baseline

**Observed locally:** schema-2 planning pins the actual Real Companies 4.02.01 PMD/PMG/PIM/PIT, visible parts and reviewed ground/paint/door/pavement resources. The same painted-bank detector finds zero banks in this effective model; stock A's source marks are absent. Old A/B remain unchanged controls. Initial new checks evaluate 13 perpendicular/parallel proposals; eight fail the combined footprint/approach pump-clearance check. Before further curb-based work, the selected survivor remains old B's exact 3 × 6 rectangle. This is a stronger validation result, not a placement improvement claim.

The diagnostic model-feature reader reports 12 raised-pavement triangle proxies away from the cited frontage, three door hypotheses away from that frontage, and 7,579 obstacle-band triangles (512 shown, 7,067 omitted). Render checks still inspect all relevant triangles per candidate; the drawing cap is not the collision-check scope. External signboard objects, complete physics and functional doorway semantics remain unresolved. Empty frontage is not evidence of pump access.

Ignored local-only baseline and initial effective plans: `local_outputs/work/2026-10-19_21-22-36/heuristic-baseline/`. The pre-change authored source is frozen there; actual schema-1 full reports, SVG and resource hashes compare identically after schema-2 additions. This is the frozen initial stage before raised-boundary work; the confirmed marked operational control is recorded below.

## Implementation boundary

[ADR-0020](../architecture/decisions/ADR-0020-plan-parking-from-effective-model-state.md) records the effective-state interface. New access checks cover footprint and approach, both painted-bank entrances, pump and map-road proxy clearances, parked-vehicle locators and sampled visible model surfaces. Deterministic ranking exposes its components and stable tie break. Geometry-only proposals compare parallel/perpendicular layouts; no random free rectangle or truck-rest fallback exists. Suggested car heading is distinct from approach direction and is not an engine yaw requirement.

N2 remains the already user-confirmed independent navigation overlay above the active North America Background Map. TASK-0043 metadata/artwork remains deferred. The heuristic packages do not include N2 or modify a profile.

## Verification status

The actual marked operational control is verified without output. Final C r2 archive audit, diagnostic visual review and handoff are pending. Runtime placement, fatigue, physical access and reload are unverified. User-confirmed A/B prompt availability and N2 icon visibility retain their original limited scope.

## Raised-boundary and clearance refinement

**Observed locally — implementation:** the new curbside method welds candidate raised top surfaces at 1 mm, removes interior triangle edges and merges straight boundary subdivisions. Material names only bound the search; a candidate boundary also needs a nearby parallel building proxy and three sampled outside-ground rises of 0.05–0.25 m. Signed building-ring winding determines the exterior, including concave rings; the resulting bay remains orthogonal to the actual source boundary. The explicit 0.5 m edge offset is a geometric policy, not proof of pedestrian or wheel clearance. Both 3 × 6 orientations use appropriate approaches: perpendicular from the open side, parallel from either longitudinal end. Final access, surface, obstacles, parked locators, doors and pump/road checks still apply.

The effective Dawson refinement initially evaluates 39 proposals (13 UI-derived plus 26 raised-boundary proposals). Its first full-stack C r1 candidate passed the checks but sat only approximately 0.116 m beyond a conservative parked-car exclusion radius. C r1 is retained as an intermediate local artifact, not the recommended handoff. Ranking was then refined without changing hard exclusions: after evidence class, prefer the minimum surplus over checked clearances (capped at 2 m and rounded to centimetres to avoid floating-point noise), then excess pump clearance capped at 20 m, capacity and stable ID. The minimum includes pump, map-road, obstacle-proxy, parked-locator and sampled render-obstacle margins where available. Missing/partial evidence is disclosed, not a complete collision proof. C r2 generation and final audits are in progress.

**Observed locally — marked operational control:** `prefab.us_gas_09_rt`, UID `0x6032dc12c1350001`, `map/usa/sec-0010+0008.base`, is supplied by `base_map.scs` within the checked installed-game/eleven-map set. Variant `default` is token `0x1573c3e700`; `city` is `0x1dfa1f`. Its effective Real Companies `nm_gas_station1_chemron` model is a different family from Dawson. Three separators form two approximately 3.5 × 4.99 m spaces, distinct from nearby access/hatch markings. All three GAS spawns match service children; native car group 1 fully contains the line bank. Current schema 2 reports `already_covered`, complete static coverage and zero resources. Three original native car groups survive untouched. Schema 1 also produces no resources, but calls the candidate rejected for occupancy/native overlap instead of explicitly reporting the covered control. No new D mod is needed.

The marked-case actual report, both schema comparisons, source hashes and model-plane world corners are under ignored local-only `local_outputs/work/2026-10-19_21-53-22/native-control-validation/`. The inventory and rejected GP hazard/metal-atlas interpretation are in `local_outputs/work/2026-10-19_21-19-20/marked-station-inventory/verified-marked-case.md`. The winning line atlas comes from ATS Expansion in the declared stack; a converter-produced DDS byte hash is not its source archive-member hash. Source geometry and effective texture provenance were checked separately.

## Deferred nonoperational-station work

**Documented — user clarification, 2026-10-19:** nonfunctional stations can look entirely valid in game. A missing linked fuel graph does not establish a broken visual model. Detecting inactive stations and adding fuel-action markers is a potential future, separate feature; it is not authorized implementation in this increment. Current generation remains limited to stations with verified existing GAS/service relationships. The unlinked regular Chemron placement remains useful geometry evidence and partial diagnostics, but receives no generated interaction. A future detector must also distinguish separate/composite service prefabs before concluding a station is inactive.

## Contact-only diagnostic

E CONTACT r1 retains the exact old B geometry. Independent byte comparison verifies 25 gameplay members: 24 identical and four changed bytes in the remaining private PPD, setting only the four car-group flags from 0 to 4. All geometry, actions, IDs, ranges/reset fields, fuel payload and other groups remain byte-identical. It is a discriminating parameter test, not the default geometry solution. Independent report: `local_outputs/work/2026-10-19_21-58-02/e-contact-independent-audit/audit.json`.
