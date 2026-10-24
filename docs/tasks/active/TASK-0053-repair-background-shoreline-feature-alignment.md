---
id: TASK-0053
title: Repair background shoreline feature alignment and deliver r3
status: active
priority: high
repositories: [.]
depends_on: [TASK-0051, TASK-0052]
owner: shared
---

## Goal

Execute the complete [r3 goal](../../reference/NORTH_AMERICA_BACKGROUND_R3_GOAL_PROMPT.md): deliver a substantially better verified testing background with convincing per-defect coastal/lake improvement, or demonstrate a genuine external blocker after exhausting meaningful independent work.

## Context

**Documented — user goal/report, 2026-10-25:** r2 job-market zoom is fixed and usable; preserve its map definition byte-for-byte. Shoreline alignment remains unsatisfactory. All 25 new views require explicit accounting, and a modest aggregate score improvement is insufficient. Prior native/atlas registration, geographic sources and r2 fitting audits provide starting evidence, not acceptance of r2 geometry.

## Scope

All new screenshot defects plus earlier Baja, California/Pacific, Vancouver/northern ports, Gulf, Chicago, Canadian lakes, Mobridge and Alaska regression regions. Geographic calibration/rendering and offline native-data diagnostics only; no playable road edits, game launch, profile/save/economy changes, live installation, push or publication.

## Implementation Plan

1. Preserve r0/r1/r2 and inspect current clean `codex/north-america-background` checkout. New scratch root: `local_outputs/work/2026-10-25_00-36-35/` (Europe/Warsaw).
2. Delegate bounded tasks: Luna/high `r3_views` owns `views/` (all-view full-size defect catalogue and r2 registrations); Luna/high `r3_native_geometry` owns `native-geometry/` (curves/prefabs/bridges and two-axis correspondence); Luna/high `r3_landmarks` owns `landmarks/` (Baja/Canada/Chicago semantic landmark facts). Main owns tracked integration, clean vector shore model, fitting choices and acceptance. Follow-up independent audits will reuse economical delegates.
3. Predeclare material-improvement criteria by actual feature scale/uncertainty after identifying views but before candidate tuning. Withhold geographic/corridor groups and independently identified two-axis features; separate clean geometry from styled raster diagnostics.
4. Compare supported models, inspect original-scale and regional comparisons with fixed native geometry, and repair severe tradeoffs before delivery. Preserve true channels/approaches and topology.
5. Build r3 with identical r2 `def/map_data.sii`; verify package/resource/texture/mapping/deformation/regression invariants, deterministic repeat and extracted-source reproduction. Commit durable source/provenance/ADR/handoff and deliver one authoritative SCS/source ZIP.

## Acceptance Criteria

- All 25 views identified/grouped and reported with per-defect original/comparison/status/severity/uncertainty; no difficult view silently omitted.
- Convincing visual and quantitative improvement across a substantial majority of independent problem areas, including conspicuous road/coast conflicts; no unexplained new severe regression. Endpoint/threshold/training averages alone do not pass.
- Matched two-dimensional landmarks and independently withheld geographic/road/shore checks support final behavior; normal/tangential, clean mask, native footprint and source/detail uncertainty are explicit.
- Confirmed zoom and complete r2 map-data bytes preserved; accepted appearance/navigation and standalone/no-Ford scope maintained. Old artifacts unchanged.
- Complete testing package, per-view/region comparisons, truthful metrics/regressions, resource/deformation checks, exact corresponding-source reproduction, committed commands/load order/manual handoff.

## Verification

**Observed locally — start, 2026-10-25:** clean checkout at `003abd0`, branch `codex/north-america-background`; goal objective and AGENTS read. Prior turn completed evidence/prompt preparation (progress), not implementation. Active goal retains full r3 delivery scope. Three bounded Luna/high delegates dispatched with separate ignored scratch ownership. Finding landmarks and retiring failed models remain work, not blockers.

**Observed locally — evidence checkpoint:** current installed r2 SCS SHA matches the authoritative baseline and its game-log mount is recorded read-only. All 25 views have a full-size preliminary geographic/defect catalogue; atlas registration uses screen downsampling for close views, with weak/rejected cases explicit. Main caught and corrected the delegate's preliminary inverted world-Z audit and rejected a coarse proximity-only Chicago junction in favor of the verified native topology point. Native visibility data remains corrected.

**Observed locally:** exported 370,544 samples along connected native road-node chords (not invented exact curves), prefab ports and a larger typed company/fuel/rest/service point inventory. Main caught incomplete southern-Baja coverage and required a bounded extension; corrected inventory covers 1,836 effective sectors with zero parse failures. Bridge association zero means unclassified, not non-bridge. Source/polygon identity and semantic uncertainty remain explicit.

**Observed locally — source/model experiments, not accepted r3:** clean unstyled r2 land/water geometry confirms Galveston and LA port bridge corridors remain dry. Downloaded/pinned GSHHG 2.3.7 (LGPL-3.0-or-later) and compared fine coast/lake masks; GSHHG's Lake Michigan polygon incorrectly contains the known Shedd Aquarium coordinate, while both it and Natural Earth omit land at Centennial Wheel/Navy Pier. Higher vertex count is therefore insufficient. Testing a hybrid coastal source and finer primary hydrography. Main's sampled two-axis Chicago landmark-flow prototype improves independent wheel/interchange distances without sampled folds, but source shoreline omissions and very large city expansion remain unresolved; no candidate is accepted from those numerical results. Frozen feature-scale/release criteria are in ignored `acceptance-gate.json` before candidate selection. Work continues; no external blocker established.

## Links

- [Goal objective](../../reference/NORTH_AMERICA_BACKGROUND_R3_GOAL_PROMPT.md)
- [New feedback](../../reference/NORTH_AMERICA_BACKGROUND_FEEDBACK_2026_10_25.md)
- [R2 baseline](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R2.md)
- [ADR-0027](../../architecture/decisions/ADR-0027-check-backgrounds-against-road-and-shore-geometry.md)
- [ADR-0028](../../architecture/decisions/ADR-0028-calibrate-background-with-roads-and-ground-constraints.md)

**Observed locally — implementation checkpoint:** added the staged feature-adjustment API, sparse compact-step evaluation/inverse, dense feature deformation checks, and a detailed source-vector renderer. It batches source projection, retains lake holes, clips borders to actual land/water, and extends country coloring only into unclassified cells. Pinned LGPL GSHHG coast/USGS public-domain Lake Michigan sources and separate license texts accompany the working r3 configuration. The candidate physical-ground fitting was rerun using CC0 Wikidata feature points rather than City footprint-derived coordinates; source/target uncertainty remains explicit. Twenty-seven focused background tests pass, including meaningful inverse/orientation and integrated island/border composition checks. This is an implementation milestone, not r3 acceptance.

**Observed locally:** initial per-view manual label framing for LA/Chicago was invalid. Main rejected its apparent coastline regressions. The views delegate instead matched multiple disjoint native road/junction sets to screenshot roads, with independent subset translations agreeing within 1–2 screen pixels; main inspected the resulting overlays. Remaining weak views are being recovered using that method. The complete native road export now includes a sector halo: 2146 effective sectors, zero failures, 267531 clipped chord samples, no lost UIDs in shared old/new bounds. Lower sample totals reflect exact clipping rather than reduced coverage. Road curves remain a separately labeled evidence-informed Hermite candidate pending screenshot validation; straight chords are not runtime curves.

**Observed locally — candidate rejection:** the first complete working renderer produced an inspectable 16k atlas, and regional chord diagnostics improve notably in southern Baja/SoCal and Chicago. Gulf worst cases and Yellowknife remain unsatisfactory. Independent landmark checks also exposed a composition error in the fitting workflow: subsequent physical-ground steps moved the originally fitted Chicago landmarks, weakening the fountain check. Main rejected that candidate and is rerunning the small-step fit with the original two-dimensional fitting landmarks retained as constraints. This is not an external blocker. No source ZIP or authoritative r3 SCS has been selected.
