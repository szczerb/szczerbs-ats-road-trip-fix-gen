---
id: TASK-0059
title: Diagnose r3 background loss at detailed world-map zooms
status: done
priority: high
repositories: [.]
depends_on: [TASK-0053]
owner: shared
---

## Goal

Analyze changes introduced by r3 that could explain the user's missing background at three detailed world-map zoom levels. Complete the bounded diagnosis with concrete archive/log evidence and a controlled corrective direction; runtime repair is a separate, pending outcome.

## Context

**Documented — user, 2026-10-25:** only maximum zoom out shows the background. This supersedes r3 runtime-unknown status for that defect. The previous accepted market zoom and navigation presentation remain requirements.

## Scope

Read-only r2/r3 archive/code and installed-file/log inspection; primary API documentation; preserved ignored diagnostics; incident and current-state updates. No source code, geographic model, generated package, live installation, profile, save, game or launch-setting changes.

## Implementation Plan

1. Preserve exact runtime evidence and compare actual delivered resources.
2. Delegate bounded resource/log checks; main independently verifies decisive claims.
3. Resolve the failure code, distinguish observed facts from inference and exclude unchanged settings.
4. Document a controlled correction and remaining runtime acceptance; commit the analysis locally.

## Acceptance Criteria

- Identify concrete last-revision resource deltas and unchanged presentation settings.
- Correlate the active installed package and runtime log without claiming an unperformed game reproduction.
- Explain primary error semantics, causal confidence and remaining unknowns.
- Preserve all source/package inputs and record a corrective experiment without presenting analysis as a fix.

## Verification

**Observed locally — 2026-10-25:** main independently verifies the installed r3 SHA against delivery, eleven unchanged map-data/MAT/TOBJ resources, DDS sizes/headers and exact DirectStorage log lines. R3 detailed pixels increase 64→256 MiB per tile; overview remains 16 MiB. Microsoft maps `0x89240008` to `E_DSTORAGE_REQUEST_TOO_LARGE`; the log explicitly names r3 but omits the member/chunk. A request-size failure is confirmed; the specific detailed member/staging threshold is inferred, not logged. No runtime fix is claimed.

Delegation: GPT-6 Luna/high owned `resource-audit/`, GPT-6 Luna/medium owned `log-audit/` under `local_outputs/work/2026-10-25_17-54-11/`. Main independently reviewed results and primary Microsoft sources, generated `main/verified-loading-delta.json` with reproducible inspection script, and authored the incident. Engine behavior was not simulated by tests; no implementation tests are needed for this documentation-only analysis. All local links in the six new Markdown files resolve; `git diff --check` passes. No corrective package or runtime test was performed.

## Links

- [INC-0002 diagnosis, evidence and proposed correction](../../incidents/INC-0002-r3-background-detailed-texture-loading/README.md)
- [R3 delivery](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R3.md)
- [R3 implementation task](TASK-0053-repair-background-shoreline-feature-alignment.md)
