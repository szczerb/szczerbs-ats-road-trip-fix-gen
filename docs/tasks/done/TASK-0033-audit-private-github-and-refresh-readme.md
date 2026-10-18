---
id: TASK-0033
title: Audit the private GitHub source history and refresh the public README
status: done
priority: high
repositories: [.]
depends_on: [TASK-0032]
owner: shared
---

# Goal

Re-audit the complete source history already uploaded privately before the maintainer shares a public link, and make README clearly explain the utility, exact map/game baseline and evidence limits.

# Context

**Documented — user report, 2026-10-18:** the maintainer pushed all 37 commits to the private GitHub repository `szczerb/szczerbs-ats-road-trip-fix-gen`. The previous history cleanup is complete. This task authorizes an audit and local documentation updates, not another history rewrite, a push, a visibility change or sharing a Facebook post.

# Scope

- Compare advertised GitHub refs to the local audited graph via read-only SSH; inspect every reachable historical path, blob, commit and retained local tree ref.
- Review concrete secrets/privacy, excluded artifacts, binary metadata, license/notices, implementation provenance and remaining publication concerns.
- Refresh README with exact source versions, reproducible entry points, requirements and honest static/gameplay distinctions.
- Preserve inputs, existing outputs, generation behavior, AGPL-3.0-only and historical evidence. Do not run the game or change external repository settings.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Full current/history privacy and secret-pattern audit | GPT-6 Luna / medium | Read-only tracked content; new ignored `privacy/` reports only |
| README map/version/runtime evidence inventory | GPT-6 Luna / medium | Read-only; root owns README edits |
| Assets, code boundaries, package licensing and provenance | GPT-6 Luna / medium | Read-only tracked content; new ignored `content/` reports only |
| Remote comparison, independent verification, docs and integration | Root model | Sole writer of tracked documentation and local commit |

1. Record the clean baseline and verify advertised remote refs without publishing anything.
2. Enumerate and audit the complete reachable source object graph and current content; independently triage delegate findings.
3. Rewrite README around actual capabilities, exact inspected/generated map versions and separately attributed gameplay reports.
4. Record a dated audit, update current state/agent guidance for the existing private origin, verify docs, tests and exclusions, and commit locally.

# Acceptance Criteria

- Audit scope explicitly identifies the remote Git graph, local non-public refs and any inaccessible GitHub UI/metadata surfaces.
- All historical/current candidate disclosures and artifact/licensing findings are reviewed and classified; any remaining publication decisions are concrete and visible.
- README names ATS 1.61.3.18 and all five map/two connector source versions without asserting individual runtime validation not reported by the user.
- Runnable examples match the CLI; dependencies, generated outputs and installation order are understandable to a new user.
- Documentation links/tasks and relevant tests pass; production code, licenses and ignored original artifacts stay unchanged. No remote write occurs.

# Verification

Completed 2026-10-18 at uploaded `master` baseline `d2b7817ca3c4772610edcbd7a4fb7a9bb0a4721c`; the initial checkout was clean. All detailed scratch/logs remain local and excluded from Git under `local_outputs/work/2026-10-18_21-35-04/`.

- Read-only `git ls-remote --symref origin` confirms GitHub advertises master/HEAD at the exact local baseline. The advertised history has 37 commits, 347 trees and 630 blobs, exactly matching the audited local union. GitHub settings/releases/Actions/attachments and visibility itself were not authenticated through a web/API session; privacy is the user's report.
- Root independently enumerated all 235 historical path names, 222 current tracked files and nine local refs (six heads, origin/master and two Codex trees). All 630 blobs, 37 commit messages and 74 author/committer headers were checked. No actionable secret, personal home path, former email, source-owned asset, binary tool, log/profile/save or C# file was found. Intentional noreply/branding, source fingerprints and engine/cache examples remain. Root corrected the privacy delegate's initial eight-ref/five-head summary using exact enumeration.
- Three GPT-6 Luna/medium agents handled bounded read-only privacy, README evidence and content/provenance/runtime-boundary reviews. Root reviewed their evidence and repeated the source scan. README and final content/provenance changes received a second independent review; only the expected in-progress task status/link transition remained, resolved at closure.
- Re-viewed all 38 historical JPEGs in the prior contact sheet after hash-proving its source images equal current reachable image blobs. All 38 JPEG metadata scans show no APP/EXIF; FFmpeg encoder comments remain. Independent review of three current examples confirms the existing small Ford-like badge concern, not a newly cleared right.
- Corrected one production module docstring to disclose source-guided/tree provenance. AST comparison across all 29 production modules is exact after excluding the module docstring; no generator logic, output contract or prepared mod changed. Existing complete C# comparison remains applicable. License, LICENSING.md, THIRD_PARTY_NOTICES.md, pyproject.toml and .gitignore bytes match the uploaded baseline.
- Replaced ten active upstream source URLs using verified tree/blob IDs, preserving the old serialized courier-report URL as historical metadata with corrected references. All nine distinct replacement API endpoints returned HTTP 200 to read-only HEAD requests. Converted 17 ignored-artifact hyperlinks into explicit local evidence identifiers rather than public downloads.
- README now lists ATS 1.61.3.18/build 25952361, five maps/two connectors and exact companion versions, supported environment and separate runtime reports. Five README CLI invocations parse through the actual argument parser and all Bash blocks pass syntax checking; no generation was executed for the examples.
- All **266 tests pass** (2.077 seconds). Full Git fsck and whitespace checks pass. Markdown targets/fragments, exclusion-aware public links, task schema/status/dependencies, historical-ID notes and 35 mapped commit targets are checked by `check-docs.py`.
- All **77,241 pre-existing ignored files** under local_inputs/local_outputs were SHA-256 rehashed: content, size, mtime and complete path inventory match. Only this new run directory is excluded. No old run, source archive, sidecar, generated mod or external backup changed.
- No push, visibility change, remote/ref rewrite, account message, game run or profile modification occurred. The final documentation milestone is committed locally on master; the already uploaded history remains the audited baseline until the maintainer pushes the new commit.

Outcome: no tracked-content privacy or accidental-asset blocker identified. The source report preserves the existing artwork/third-party-rights questions and the separate generated-archive path/redistribution scope; this is not a new legal clearance or a GitHub account-security audit.

# Links

- [Post-upload source re-audit](../../reference/PUBLIC_SOURCE_REAUDIT_2026_10_18.md)

- [Previous source/history review](../../reference/PUBLIC_REPOSITORY_REVIEW.md)
- [History cleanup](../../reference/HISTORY_CLEANUP.md)
- [Input inventory](../../reference/LOCAL_INPUT_INVENTORY.md)
- [Gameplay results](../../reference/VALIDATION_RESULTS.md)
- [Current state](../../project/CURRENT_STATE.md)
- [Project license scope](../../../LICENSING.md)
