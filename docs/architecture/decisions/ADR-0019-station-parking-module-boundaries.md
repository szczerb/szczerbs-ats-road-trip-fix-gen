# ADR-0019: Separate station-parking workflow, proposal, validation, and output responsibilities

## Status

Accepted for the bounded refactor in [TASK-0041](../../tasks/active/TASK-0041-refactor-station-parking-and-investigate-navigation-icons.md). The bounded package split and behavior-preservation verification are complete; navigation research remains separate.

## Context

The source-pinned station-parking proof of concept introduced station-specific analysis and generation alongside existing map processors. Before this refactor its responsibilities spanned modules such as `station_run.py`, `station_parking.py`, `station_mesh.py`, `station_geometry.py`, `station_trigger.py`, and `painted_parking.py`. Keeping these responsibilities legible will make the two explicit proposal methods and the write boundary easier to inspect without refactoring unrelated fuel, rest, courier, archive, or parser systems.

**Observed locally — 2026-10-19:** [ADR-0018](ADR-0018-isolate-source-pinned-station-parking-poc.md) and [TASK-0039](../../tasks/done/TASK-0039-research-gas-station-car-rest.md) establish source-pinned per-station inputs, explicit `painted_bays` / `unmarked_geometry` proposals, preservation safeguards, and a deliberate separation from the existing distance/density rest policy. The next work also investigates navigation marker display. That research may or may not justify a marker representation change; it must not silently introduce a parking-location policy change.

## Decision

- Keep station-parking implementation under `src/ats_road_trip/station_parking/`. Place workflow/resource acquisition at the orchestration edge; candidate proposal methods in focused method modules; shared validation and rejection reasons in shared checks; result selection in the planner; diagnostics and visualizations outside candidate selection; and native trigger serialization at the output boundary. Adapt the exact files to real responsibilities instead of creating placeholder layers.
- Use a small explicit data structure for a candidate and its validation outcomes where this clarifies the flow. Keep the flow understandable as effective station data → candidate proposals → checks and rejection reasons → selected result → trigger write.
- Keep the painted-bay and unmarked-geometry methods as proposal strategies. Do not build a plugin framework, refactor the project broadly, or turn this module into the existing map-wide rest processor.
- Preserve public CLI commands and argument meaning, configuration formats, deterministic selection, IDs, geometry, trigger actions, write/source protections, and correct output paths. Any `__file__`-relative paths must continue to resolve from the repository rather than the nested package directory. Setuptools and the current test runner must discover the package/tests.
- Keep geometry proposal/selection, shared validation, diagnostics, workflow orchestration, and trigger writing as distinct responsibilities. Navigation-icon research belongs in its own report and task evidence. It does not imply a new marker representation or a navigation solution; make such a change only after the research establishes it and preserve area and activation behavior.
- Verify and commit this structure-only refactor as a separate milestone before any icon-related code or package changes. Retain prior output artifacts and use pinned-input comparisons to detect unintended behavior changes.

## Consequences

The refactor has a bounded review surface and keeps the experiment's two proposal methods and source-writing safeguards visible. A focused module layout should make it easier to reason about the difference between proposal failure and write/validation failure.

The decision intentionally does not prescribe exact class names, helper counts, or a full target tree; code ownership and responsibilities determine the final layout. The `station_parking` path, unaffected external behavior, and separate commit ordering are fixed. This ADR does not resolve navigation visibility, prove either method usable in-game, or authorize geometry, proximity, density, package publication, profile, or mod-priority changes beyond documenting the tested handoff.

## Verification

**Observed locally — 2026-10-19:** the resulting package has focused `workflow`, `planner`, `validation`, `diagnostics`, `mesh`, `geometry`, `trigger` and `methods/{painted,unmarked}` modules. Its public package exports planning, rendering, config validation and workflow. The existing frozen parameter dataclasses remain; candidate/report JSON shapes are preserved rather than introducing new types solely for moving files. Legacy fuel/rest/archive helpers remain in their existing modules.

All 326 tests pass. The root independently checked all 57 moved function/class bodies with imports excluded: no behavior-body difference. Full CLI/analyze/generate help text is byte-identical. Setuptools discovers the package and its methods; `workflow.REPO_ROOT` equals the actual worktree. Three authored fixture cases (painted, unmarked, no-paint unmarked) produce byte-identical complete JSON snapshots, selected IDs/geometry, resource hashes, SVG and actual SCS archive bytes. Both real pinned Dawson inputs likewise produce byte-identical full report/resource/SVG snapshots, and each method's three planned resources match the original delivered archives exactly. Evidence and immutable pre-refactor authored source are retained under ignored `local_outputs/work/2026-10-19_19-33-14/reorganization-baseline/`. No marker behavior, heuristic, source input or old output was changed.
