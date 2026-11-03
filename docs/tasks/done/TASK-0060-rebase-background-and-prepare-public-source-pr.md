---
id: TASK-0060
title: Rebase background branch and prepare a public source PR
status: done
priority: high
repositories: [.]
depends_on: [TASK-0055]
owner: shared
---

## Goal

Implement the user-approved plan: retain and sanitize the unpublished background development history, rebase onto current origin/master, prepare accurate public-source documentation, and report whether the branch is ready for a later push/PR. This task does not publish anything.

## Context

**Documented — user, 2026-10-30:** preserve development commits while sanitizing personal paths, resolve task/ADR collisions without changing existing master IDs, retain both research tracks, and defer mod-package publication. The approved review identified 19 outgoing commits, host paths in their history and 71 clickable links to ignored local artifacts. R4 remains experimental and its in-game zoom confirmation remains pending.

## Scope

Branch-only history sanitation/rebase; documentation, identifier and reproduction guidance updates; complete combined tests, packaging smoke and privacy/artifact review. No background implementation/calibration, texture, zoom, navigation or gameplay changes. No pushes, PR creation, releases, visibility changes, live installation, game launch or profile edits.

## Implementation Plan

1. Preserve and verify an ignored recovery bundle and original artifact fingerprints.
2. Sanitize branch-only commit trees, preserving development milestones and author metadata; fetch/rebase onto current upstream, retaining both research tracks and package-data/dependency settings.
3. Resolve background-only task and ADR collisions; make local evidence status explicit and document reproducible r4 generation and pytest coverage.
4. Delegate independent validation/publication audits with exclusive scratch ownership; record findings and a precise readiness statement; commit verified integration locally.

## Acceptance Criteria

- All 19 development milestones retained above current origin/master; public upstream history and other local branches unchanged.
- Outgoing history contains no absolute host paths or detected credentials/protected assets; recovery bundle remains ignored.
- Background implementation, configuration, recipe and existing generated package bytes unchanged.
- Task/ADR identifiers are unique, affected references resolve, and new background documentation does not advertise ignored artifacts as public downloads.
- Combined tests and package/import smoke pass; both background and upstream station-parking package contents remain present.
- Remaining runtime/provenance limits are explicit. No publication action is taken.

## Verification

**Observed locally — completed, 2026-10-30:** the original tip is `ed0c16e`; a complete recovery bundle verifies successfully under ignored `local_outputs/work/2026-10-30_18-27-01/public-prep/`. Twenty-five existing background delivery artifacts are fingerprinted. Branch-only sanitation changes six historical document blobs across four final documents; all 19 milestone subjects and original author metadata are retained. Fetch confirms origin/master `c459b2a`; rebase retains the upstream parking work and background modules, including station catalog package data and optional background dependencies.

Actual delegation: GPT-6 Luna/medium owns only ignored `validation/` for code/calibration equality, combined tests and package/import smoke. GPT-6 Luna/medium owns eight background reference handoffs/feedback/diagnosis documents and ignored `docs-cleanup/` scratch for local-only artifact-link cleanup. Main owns history/rebase, ID mapping, navigation/reproduction guidance, this task and the review record. Final independent outgoing-history/docs checks follow integration.

## Links

- [Public-source preparation review](../../reference/NORTH_AMERICA_BACKGROUND_PUBLIC_SOURCE_REVIEW_2026_10_30.md)
- [R4 scope and runtime boundary](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R4.md)
- [Portable versioned paths](../../architecture/decisions/ADR-0030-use-portable-reviewed-evidence-and-versioned-paths.md)

**Final verification:** all 692 combined pytest tests pass (12.33 seconds), main/CLI/background help checks pass, and the wheel includes all eight background modules, the upstream station-parking reviewed catalog and license/notice files. Build-only setuptools/wheel dependencies were installed under the ignored verification run. Post-rebase r4 generation is byte-identical to the historical `00e39324…013b4` archive. All 25 pre-existing background artifact fingerprints match. The implementation/calibration/test/recipe comparison against original tip `ed0c16e` is byte-identical. Independent GPT-6 Luna/medium publication checks found no outgoing host-path, secret-pattern or protected/binary-payload blocker; IDs are unique and all 1575 checked non-artifact relative documentation targets resolve. Other branch refs and existing public history are unchanged. Current base remains `c459b2a`.

**Outcome:** the reviewed branch is ready for a subsequent public source push/PR with experimental/runtime and provenance caveats. No push, PR creation, release, visibility change or gameplay action was performed. R4 in-game confirmation and any later artifact publication remain separate.
