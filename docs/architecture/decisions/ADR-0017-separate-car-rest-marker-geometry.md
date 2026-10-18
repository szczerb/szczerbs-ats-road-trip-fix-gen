# ADR-0017: Give car rest its own native marker geometry

## Context

Date: 2026-10-18. [TASK-0038](../../tasks/done/TASK-0038-investigate-missing-car-parking-icons.md) investigates absent car-map parking icons with r8 despite its mixed truck/bus/car rest action. The user authorizes an implementation, automated verification and local r9 handoff, without launching ATS or changing a live profile.

**Observed locally — ATS 1.61.3.18:** read-only inspection of the installed executable, independently repeated by GPT-6 Sol/high, identifies a truck-first map-marker classification. Prefab trigger groups are tested for truck/bus mask 3 before car mask 4; a truck match selects marker category 7 and skips car category 25. Standalone Trigger items use the same truck-first decision across their action list. Thus adding `car` to one truck action, or adding a car action to the same standalone item, does not create an independent car marker. The action matcher resolves command/parameters dynamically; custom alias spelling is not the cause. The executable also identifies Parking overlays as obsolete in favor of parking triggers. Exact identity and bounded evidence are in the [investigation](../../reference/CAR_PARKING_ICON_INVESTIGATION.md).

This supersedes the mixed private-action implementation choice in [ADR-0008](ADR-0008-compose-processors-and-local-rest-polygons.md), and the action-only mutation choice in [ADR-0012](ADR-0012-preserve-irregular-source-rest-geometry.md). Their local distance policy, original-geometry preservation and conservative irregular-geometry proximity rules remain in force.

## Decision

- Keep original truck/bus triggers and shared action definitions unchanged. At each selected prefab placement, append a separate car-only polygon using native `parking_car`, a fresh group ID and remapped internal neighbor indices. Copy original per-vertex geometry, flags, range and activation parameters exactly. Retain placement-local private prefab aliases and context lineage.
- Clone each selected standalone trigger into a separate car-only Trigger item with fresh deterministic item/node UIDs. Preserve geometry, flags, radius and node order exactly; give the new nodes independent reciprocal ownership. Preserve source tags so existing tag-targeted activation controls can reach both twins, while copying no unrelated actions onto the car twin. Original items and nodes remain byte-identical.
- Extend explicit visibility and layer membership for standalone twins. Reject UID conflicts, unknown/unsafe geometry/action layouts or required visibility edits outside source ownership. Compose these changes on top of fuel output, including earlier layer edits.
- Keep the immutable original physical-car inventory and inclusive 1,000-unit XZ rule for expanding eligibility. Track car-only marker-capable locations separately. A source location already allowing truck/car may receive a same-geometry car-only twin to repair its marker when no original car-only marker lies within the radius; that operation does not expand physical eligibility. Report marker repairs separately from newly enabled car locations.
- Emit rest report schema 2 with `marker_strategy`, `car_action`, group-pair/standalone-twin evidence and separate permission/marker counters. Stop emitting mixed private trigger-action definitions. The generic map-fix command defaults to r9; legacy fuel-only stays r2 and courier stays r3.

## Consequences

Generated rest descriptors and sector topology grow; original truck geometry and source standalone records do not change. Two co-located independently filtered triggers replace one mixed interaction. The implementation remains source-specific, bounded by the same inspected sectors/halo, with no promise of stock-map-wide Montana coverage. Existing irregular shapes are cloned exactly, not repaired.

Static checks must prove independent native car-only classification, exact source geometry/truck preservation, graph links, visibility/layers, fuel/context composition and effective-stack resource winners. Actual icon rendering, fatigue recovery and tag/script behavior still need later game observation. No synthetic Parking service, guessed vehicle flag or obsolete overlay is introduced. Existing r8 and earlier packages remain historical artifacts and must be disabled when installing their r9 replacements.
