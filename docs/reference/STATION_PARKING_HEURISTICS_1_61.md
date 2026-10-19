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

Ignored local-only baseline and initial effective plans: `local_outputs/work/2026-10-19_21-22-36/heuristic-baseline/`. The pre-change authored source is frozen there; actual schema-1 full reports, SVG and resource hashes compare identically after schema-2 additions. Required real marked-USA investigation is still in progress; no positive result is invented from material names.

## Implementation boundary

[ADR-0020](../architecture/decisions/ADR-0020-plan-parking-from-effective-model-state.md) records the effective-state interface. New access checks cover footprint and approach, both painted-bank entrances, pump and map-road proxy clearances, parked-vehicle locators and sampled visible model surfaces. Deterministic ranking exposes its components and stable tie break. Geometry-only proposals compare parallel/perpendicular layouts; no random free rectangle or truck-rest fallback exists. Suggested car heading is distinct from approach direction and is not an engine yaw requirement.

N2 remains the already user-confirmed independent navigation overlay above the active North America Background Map. TASK-0043 metadata/artwork remains deferred. The heuristic packages do not include N2 or modify a profile.

## Verification status

Actual marked case, final candidate selection, archive generation/audits and user handoff: pending. Runtime placement, fatigue, physical access and reload are unverified. User-confirmed A/B prompt availability and N2 icon visibility retain their original limited scope.
