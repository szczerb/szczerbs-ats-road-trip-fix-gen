---
id: TASK-0051
title: Recalibrate North America background to roads and shores and deliver r2
status: done
priority: high
repositories: [.]
depends_on: [TASK-0050]
owner: shared
---

## Goal

Deliver a meaningfully improved ATS 1.61-r2-experimental geographic background and usable job-market scale, verified against independent road/shore relationships in reported regions, with reproducible sources and a manual handoff. Continue until delivery or a genuine external blocker; finding suitable landmarks is part of the work.

## Context

**Documented — user goal, 2026-10-24:** r1 retains every practical coast/lake issue and crowded job markets. The supplied goal objective explicitly requires implementation, cheaper delegated native-object analysis, matched geographic landmarks, independent road checks and a new experimental package. Another diagnosis, missing first-pass matches or a failed model is not a stopping condition. [Previous diagnosis](../../reference/NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md) is starting evidence, not a complete causal proof.

## Scope

Southern/northern Baja; Los Angeles/San Diego and reported Pacific coast; Brownsville/Corpus Christi/Galveston/Lafayette/New Orleans; Chicago/Lake Michigan; Canadian lake belt; regression checks in previously corrected Canada/Alaska. Preserve accepted style, masks, unrelated truck/route behavior, standalone/no-Ford scope and r0/r1 fallbacks. Read-only native resources inform analysis; do not redistribute game/map assets or traced artwork. No live installation, game launch, profile/economy operation, push/publication or paid service.

## Implementation Plan

1. Inspect current files/evidence and preserve new work under `local_outputs/work/2026-10-24_17-09-42/`.
2. Delegate native water/terrain/shore object analysis to GPT-6 Luna/high (`water_landmarks`, scratch `water-analysis/`); route-marker/bridge/junction landmark analysis to Luna/high (`route_landmarks`, `route-analysis/`); market scale/usability measurement and later review to Luna/medium (`zoom_and_review`, `zoom-review/`). Main owns tracked integration, calibration mathematics and acceptance audit.
3. Identify and independently audit real geographic/game landmark matches; compare regularized global/regional models using independent regions and road relationships, not only settlement-point or water-pixel metrics.
4. Implement supported r2 correction and stronger justified market zoom; generate current-clock packages/previews and validate graph, dimensions, masks, bounds, geometry, regression and deterministic reproduction.
5. Commit code/configuration/provenance/reproduction/handoff and provide one authoritative SCS plus corresponding source bundle; label actual runtime behavior awaiting user acceptance.

## Acceptance Criteria

- Independent matching shore/road/intersection/bridge or peninsula/lake landmarks support the correction, with clear fit/check separation and confidence/provenance.
- Reported regions improve measurably on actual road/background relationships; legitimate water crossings remain distinguished and regressions/limits explicit. No arbitrary land painting or optimization solely for land coverage.
- Current r1 market crowding addressed with a stronger justified setting or independently exposed market control, with world-map tradeoff documented.
- Accepted palette/navigation masks/unrelated map behavior and standalone scope preserved; r0/r1 unchanged.
- One r2 SCS, overall/regional/native-road comparison previews, quantitative report, resource/texture/bounds/mask/regression checks, deterministic reproduction/source bundle and committed command/load order/manual handoff.
- Genuine blocker route only after available meaningful alternatives are exhausted; preserve independent work and exact missing external input. No research-only substitute for an achievable build.

## Verification

In progress. Goal file read at start; branch `codex/north-america-background`, clean HEAD `12c2a14`. Active goal remains full r2 delivery. Existing r1/runtime evidence and old immutable data/sector snapshots reused by reference. The preceding turn prepared the requested goal prompt; this turn starts execution.

**Observed locally — implementation checkpoint, 2026-10-24:** added typed read-only road fields to the structural sector reader. KDOP/UI flags are at item offsets 52–55 (city bit at 54, inverted UI-hide bit at 55); road flags at 57–60 are a different field, and the road-type token starts at 61. Main's serializer/parser review caught the delegates' offset confusion; old scratch classifications are superseded and are being regenerated. A deliberately contradictory header/payload fixture guards this error. No sector-writing behavior changed.

**Observed locally:** a configurable compact displacement component now composes after the existing calibration; schema, support identity, composition and sampled fold rejection have behavioral tests. Its coefficient candidates remain experimental: initial route-normal fits reduce selected curve distances but regress some actual coastal road relationships, so they are not accepted delivery candidates. Interpolation checks near fitting support are not spatial extrapolation tests. A delegate's proposed coordinate-slot bug was independently disproved and withdrawn; the actual implementation retains undeformed source coordinates.

**Observed locally — checkpoint verification:** `OPENBLAS_NUM_THREADS=1 PYTHONPATH=src:. local_outputs/work/2026-10-23_21-16-53/venv/bin/python -m pytest -q`: **304 passed**. No r2 SCS has been accepted or delivered yet. Natural Earth 4.1.0 road supplement and official SICT station tables support new road/corridor correspondence work, including distinguishing unnamed federal Baja corridors from same-number state roads. Main owns final matching/model acceptance; delegated work remains ignored scratch.

**Observed locally — r2 implementation/build milestone:** accepted the joint road/physical-ground compact candidate for an explicitly experimental trial. Versioned coefficients/provenance, [ADR-0028](../../architecture/decisions/ADR-0028-calibrate-background-with-roads-and-ground-constraints.md), reproduction instructions and [r2 handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R2.md) now record the implementation and limits. Main reviewed correspondence selection, rejected global/normal-only and urban-footprint models, inspected the native comparison panels, and confirmed production atlas pixels equal the selected candidate. Corrected native classification excludes hidden roads; no map resources are changed.

**Delegation and verification:** Luna/high `route_landmarks` supplied effective named-road/native geometry and expanded regional regression endpoints; Luna/high `water_landmarks` supplied typed physical-ground observations and independent final inverse/Jacobian/holdout-bias audit; Luna/medium `zoom_and_review` measured fixed-symbol spacing, audited r2 config, authored its reproduction README and independently audited the final archive. GPT-6 Sol/high `shore_geometry` resolved road graph/bridge correspondences and independently audited physical bridge depictions. Each worked in assigned ignored scratch; main owns coefficients, implementation acceptance and tracked integration. Two delegated interpretation errors (native flag offsets and an alleged coordinate-slot defect) were independently corrected/retracted rather than adopted.

**Observed locally:** 576 route-fit/135 local route-check observations; all 962 ground facts fit, never held out. Road-check RMS 699.1→565.6, with 49/135 worsening and interpolation/normal-only limitations; withheld Chicago junctions and Coronado diagnostic improve. Remaining Gulf/Canadian/north-Baja route/bridge regressions are explicit in the handoff. Final SCS built under `local_outputs/generated/2026-10-24_18-30-20/`, SHA `58cbfe4047113308bb82a0e5ed4d15e298515f22916bab8eb8b1fc403c521604`. Independent archive check passes; map-data bytes differ only at zoom tier 7 (100000→60000), all resource/mask/texture contracts pass. Full suite: **305 passed**. R0/r1 re-rendered with current code to their original exact package hashes. This was the implementation milestone; final verification follows.

**Observed locally — final delivery verification:** source commit `18e5f13c07d976fff4a7d6f2a91275a249a5b825` archived into the corresponding r2 source ZIP (SHA `caae49d67707abee84f62c650e9fb0359f90d0f1fdf9709327ef9d8e593c9dd2`). The 304-member archive excludes native assets and rebuilt in a separate source root to the exact authoritative SCS SHA above; code/config/source pins match production. No installed game input is needed for rendering. Final native comparison gallery includes all reported primary regions plus exact-window Mobridge, northern Pacific, Vancouver and Alaska regressions. Main caught a delegate's preliminary inverted water mask and required recomputation before using the final report; endpoint clipping and the production atlas are confirmed. Mild Mobridge/northern-Pacific shallow regressions, Vancouver mixed checks, unchanged sampled Alaska thresholds and support identity limits are recorded rather than hidden. New-document links and diff whitespace checks pass. Delivery scope is a verified experimental testing version, not universal geographic repair or runtime acceptance. No external blocker or game/profile/live-install/push action occurred.

## Links

- [R1](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R1.md)
- [Geometry diagnosis](../../reference/NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md)
- [Acceptance ADR](../../architecture/decisions/ADR-0027-check-backgrounds-against-road-and-shore-geometry.md)
