# ADR-0008: Compose selected processors and apply rest eligibility locally

## Context

Date: 2026-10-18. The user requests independently selectable fuel, rest and future Courier Job processing. For rest, add car eligibility to a truck/bus area only if no existing car rest lies within one kilometre. The user explicitly selects straight-line distance in the game world rather than navigation distance.

**Observed locally — ATS 1.61.3.18:** prefab rest polygons name shared trigger actions; `hud_parking` permits truck/bus and `parking_car` permits cars, using the same `hud_activate` command and numeric parameter 3. Standalone map triggers also store action parameters. A global shared-action edit would bypass the requested local proximity test. Shared prefab descriptors are instantiated at multiple map locations; a global descriptor edit would also bypass per-location decisions.

## Decision

Introduce an explicit topic enum/configuration with `fuel`, `rest` and a reserved `courier` value. Reject `courier` until an implementation and acceptance criteria exist. Fuel encompasses both physical refueling access and country petrol-price repairs. Preserve the legacy fuel command/defaults; add a generic map-fix command requiring explicit topic selection. Canonical processing order is fuel then rest, independent of option order.

Plan all enabled processors before packaging. Rest consumes fuel's staged resources so its sector/descriptor edits retain fuel changes. Maintain source ownership separately from staged bytes. Reject conflicting resources or incomplete coverage rather than publishing a partial "complete" fix. Reports identify each processor, configuration, source provenance and blockers. Topic-specific package names distinguish fuel-only, rest-only and combined output. Do not automatically reuse gas-labelled artwork for rest-containing packages.

For rest, interpret the kilometre threshold as **1,000 map-world units in the horizontal XZ plane**, without route/map-scale conversion. Compare polygon-to-polygon minimum distance, with intersection/containment distance zero and an inclusive boundary: a car polygon exactly 1,000 units away suppresses generation. Build the proximity index from original effective car rest areas in the source sectors and a nearby sector halo. The user explicitly accepts extra car permissions caused by missing a neighbor beyond the inspected boundary; a full-world absence proof is not required. Newly generated car areas do not suppress other truck candidates in the same run. Keep separate map namespaces separate.

Decide per placed truck/bus rest polygon and modify only selected source-owned placements. Preserve original polygon geometry/topology and shared action definitions. Clone the reviewed rest action under a unique private name, retaining its truck/bus parameters and adding `car`; retarget only selected polygon/action references. A separate additive `trigger_action.<unique>.sii` registers the private action, following the installed definition file's modding instruction. Private prefab aliases separate selected placements from untouched instances of the same prefab. Validate topology, transforms and action semantics before changing a resource. Unsupported/ambiguous geometry needed for an actual source edit remains a blocker. Out-of-scope or unsupported neighbor-only data is reported as omitted; it may cause the boundary over-additions accepted by the user.

## Consequences

This is a straight-line availability heuristic. It does not establish a driveable route, physical access, matching elevation, map icons or successful fatigue recovery. User-requested proximity suppresses a truck-area addition even when a nearby car rest is hard to reach. Record these limits, preserve truck/bus behavior and retain a separate manual validation task.

Effective-stack scope is the explicitly supplied package order, not an inferred live profile. Other active mods may change the winning polygons/actions. Report bounded spatial scope, omitted neighbor data and standalone trigger interpretation explicitly; fuel service counts do not prove rest coverage. Full-world rest coverage is not claimed.

See [rest research](../../reference/PASSENGER_CAR_REST_RESEARCH.md), [TASK-0016](../../tasks/done/TASK-0016-prepare-rest-eligibility-experiment.md), and [TASK-0017](../../tasks/done/TASK-0017-compose-selectable-compatibility-processors.md).
