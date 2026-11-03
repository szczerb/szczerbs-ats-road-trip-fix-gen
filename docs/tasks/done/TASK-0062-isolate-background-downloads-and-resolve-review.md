---
id: TASK-0062
title: Isolate background downloads and resolve the Copilot review
status: done
priority: high
repositories: [.]
depends_on: [TASK-0061]
owner: shared
---

## Goal

Fix Copilot's valid PR #2 finding: downloads must not create caches or files in read-only supplied-input directories. Preserve unrestricted read-only offline caches. Push a verified fix, reply to the existing thread and resolve it after confirming the published fix.

## Context

**Documented — user, 2026-10-30:** implement the approved isolation plan, update the existing PR and explicitly reply/resolve the review. [Copilot's thread](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/pull/2#discussion_r4426960951) identifies the generator's unguarded `--download-data --data-dir` route. **Observed locally:** `source_files` also unconditionally created offline cache directories. The standalone fetch route already restricted destinations but resolved its allowed suffix, allowing a redirected work tree to weaken that policy.

## Scope

One shared resolved-path validator; both download entry points and the source loader use it before side effects. Offline cache loading creates no directories and remains unrestricted. Focused regressions, existing full tests, documentation and PR follow-up. No map/calibration/resource/zoom changes, release, merge, profile edit or live installation.

## Implementation Plan

1. Anchor the allowed work tree to the canonical checkout; reject traversal/symlink escapes before mkdir/network/write.
2. Validate the generator's selected/default cache before it creates its run directory; migrate fetch to the same helper.
3. Delegate tests in `tests/test_background_download_paths.py` to GPT-6 Luna/medium with exclusive ownership; main implements and independently reviews production/tests.
4. Run focused/full checks, record and push the reviewed fix, reply with the commit and actual verification, resolve the exact thread and verify remote/thread state.

## Acceptance Criteria

- Escaping download paths are rejected through both entry points and direct loader calls without cache/run creation or network activity.
- Allowed caches/default selection still work; offline external caches remain byte/mtime-identical and missing caches are not created.
- Hash/version/source guards and package generation remain unchanged; tests pass without real downloads or input mutations.
- The pushed PR contains the fix and truthful evidence; Copilot receives a direct reply and the existing thread is confirmed resolved.

## Verification

**Observed locally — 2026-10-30:** all 21 new mocked/synthetic isolation regressions pass; the full suite passes 713 tests in 12.23 seconds. Independent GPT-6 Luna/medium code review finds no concrete blocking issue in the scoped path/order semantics. Main independently verifies unchanged geographic definitions, rendering/resource/calibration bytes and the original r4 package SHA. The tests exercise both CLI routes and the direct loader, including traversal/cache-root symlink escapes and successful/default/offline cases, without real network downloads or supplied-input modifications. The fix is published as `0157548`; the direct reply and resolved thread have been verified through the GitHub API. Local-only scratch: `local_outputs/work/2026-10-30_19-17-43/`. Main owns production/documentation; GPT-6 Luna/medium owns the regression test file and its ignored `tests-review/` output. No game or real input-directory experiment is performed.

## Links

- [PR #2](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/pull/2)
- [Original finding](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/pull/2#discussion_r4426960951)
- [R4 runtime boundary](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R4.md)

**PR follow-up completed:** commit `0157548375ab4cbc019e3152d77f7cf04c385668` was pushed to the existing PR branch, and the PR head was verified to match before posting the reply. [Direct reply](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/pull/2#discussion_r4427110435) records the shared guard, offline behavior, 21 regression cases and 713 passing tests. The exact Copilot thread was then resolved, and an independent API read confirms `isResolved: true` and the reply's reference to the published fix. A documentation-only completion commit records this outcome; final remote/local identity is checked after pushing it. No merge, release, package upload or game/profile change occurred.
