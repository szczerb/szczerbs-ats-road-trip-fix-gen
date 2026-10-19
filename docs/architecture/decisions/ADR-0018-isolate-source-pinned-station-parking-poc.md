# ADR-0018: Isolate source-pinned station-parking experiments

## Context

Date: 2026-10-19. [TASK-0039](../../tasks/done/TASK-0039-research-gas-station-car-rest.md) follows the user's request for natural car parking near station buildings, including painted bays and unmarked forecourts. Existing `rest` expands eligibility on original truck geometry under a 1,000-unit rule; that is a different selection policy. The user explicitly requires a separate branch and worktree and individual-station experiments before future distance/density integration.

**Observed locally — ATS 1.61.3.18:** the selected Dawson City WCE placement combines a source PPD with no native car rest and a model containing four parallel paint strips around three car-sized bays. The matching native Road Trip descriptor provides a useful comparison, but is not the input geometry for generation. The model also provides surfaces and parked-truck locators; source UI-map polygons are coarser building/lot proxies. See [research evidence and limits](../../reference/GAS_STATION_CAR_REST_RESEARCH.md).

## Decision

- Keep `station_parking` outside the map-wide `Processor` enumeration and proximity pipeline for this increment. Expose explicit `analyze-station-parking` and `generate-station-parking` commands with exactly one source-pinned station configuration each.
- Require explicit selection of `painted_bays` or `unmarked_geometry`. Paint proposals come from repeated coplanar mesh separators; unmarked proposals come from building/lot geometry proxies corroborated against selected model surfaces and obstacles. Neither uses original truck-rest geometry to construct the candidate.
- Pin source archive, effective sector/descriptor, PMG, converted PIM and optional fuel-baseline hashes. Unknown versions, variants, malformed geometry, uncertain resource lineage and exhausted computation budgets block output.
- Consume reviewed ConverterPIX PIM text through an independently authored bounded reader. ConverterPIX remains an external research tool, with its exact version and executable hash recorded; no converter source or executable enters the repository.
- Append a separate native `parking_car` polygon and retarget only the selected placement to a fresh private descriptor. Preserve original trigger records, shared actions and all other original sector bytes, including nodes and fuel services.
- A generated test package may replace a fuel/rest map fix using a pinned fuel-only baseline. Preserve baseline payload, audit its aliases against the original effective source and restore original context classifications before the new station edit. This does not apply the old rest policy. Other source-specific fixes retain their source-relative load order.
- Keep static geometry proposals, structural validation and gameplay outcomes distinct. Retain no whole-world absence or collision-complete claim from a bounded model inspection. The user performs later in-game tests; this workflow does not install mods or change profiles.
- Keep all work on `codex/gas-station-car-rest-research` in its separate worktree. No merge, push or publication is part of this increment.

## Consequences

The first handoff contains alternatives to test individually rather than a universal station classifier. Painted-bay thresholds and material roles are explicit reviewed policy; their applicability is limited to inspected models. The unmarked method depends on UI-map geometry that can omit details and checks sampled render surfaces; external objects, traffic behavior and maneuverability remain manual questions.

Whole-sector overrides still do not merge in the game. The supplied combined stack resolves Dawson's sector to Alaska Expansion, overriding its WCE copy. Replacing the Alaska combined fix with an Alaska fuel-plus-station PoC temporarily removes that fix's generated car permissions on truck backlots across its payload; native source rest and original truck/bus interactions remain. WCE r9 stays enabled at its own lower source-relative position. The handoff must name this scope and retain all other source fixes in their original priority positions.

Integrating either method with the map-wide rest policy, introducing distance/density rules, handling composite stations whose lot and GAS locator belong to different prefabs, and automating broad map selection require separate evidence and follow-up work.
