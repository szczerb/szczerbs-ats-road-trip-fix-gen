---
id: TASK-0032
title: Clean publication history and configure GitHub commit identity
status: done
priority: high
repositories: [.]
depends_on: [TASK-0031]
owner: shared
---

# Goal

Complete the sole contributor's explicitly authorized local history cleanup, preserving research provenance, functionality and AGPL-3.0-only while preparing account-attributable Git commit headers.

# Context

**Documented — user instruction, 2026-10-18:** an external full backup exists; additionally create and verify a local Git backup, remove unnecessary personal paths from tracked content/history, and replace the intentional legacy placeholder email with the supplied GitHub noreply address for both author and committer. Do not publish, configure a remote, push, run the game or modify original artifacts. This is separate authorization superseding earlier audit advice to retain the placeholder identity.

# Scope

- Preserve six branch names/topology and two Codex tree refs, with complete old-to-new commit mapping; retain the sole worktree.
- Neutralize only reviewed artifact/screenshot paths and the equal-length cache test fixture; preserve game VFS paths, branding, upstream hashes and artifact checksums.
- Update current guidance and label historical repository commit IDs; leave source consultation and audit limitations visible.
- Leave global Git settings, input files, pre-existing outputs, production modules, license and notices unchanged.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Historical/current path inventory and replacement review | GPT-6 Luna / medium | Read-only, no file ownership or mutations |
| Independent staged all-ref, topology, metadata and protected-file audit | Same GPT-6 Luna / medium agent | Read-only staging and backup comparison |
| Backup, mechanical rewrite, integration, documentation and final checks | Root model | Sole writer of history, refs and tracked documentation |

1. Inventory clean checkout, all refs/worktrees/configuration and immutable local files; make verified full Git archive and bundle.
2. Run git-filter-repo in an isolated copy; rebuild tree-valued Codex refs using identical content rules; compare all mapped commits before atomic integration.
3. Configure repository-local identity; document stable pre-cleanup mappings and superseded advice without changing provenance findings.
4. Verify tests, docs/tasks/links, complete reachable object graph, exclusions, artifacts and licenses; remove old live reflogs/unreachable history after backup validation; commit the final record locally.

# Acceptance Criteria

- All eight initial refs survive with sanitized reachable content; 35 commits map one-to-one with preserved messages, dates, names, parents and structure.
- Both commit-header emails use the supplied noreply address; global settings and any other identities remain unchanged.
- Concrete personal paths/former email are absent from every publication-eligible ref and the retained technical tree refs, with preserved generic engine-path evidence.
- Backup is verifiable, excluded and not connected to publishable refs; mapping is available locally and in tracked documentation without self-reference cycles.
- Production bytes, AGPL/notices/metadata, ignore rules and all pre-existing ignored files remain unchanged; relevant tests and documentation checks pass.

# Verification

Completed locally on 2026-10-18. No publication or game operation occurred.

**Observed locally — 2026-10-18:** clean baseline, six branches, two tree refs, one worktree and no tags/stashes/remotes. Full `.git` archive was extracted and fsck checked; every original ref matched. Bundle verification passed and backup SHA-256 values were recorded. Run directory: `local_outputs/work/2026-10-18_20-31-16/` (local/ignored, excluded from Git).

- Root mechanically verified all 35 mapped commits: exact messages, names, dates/timezones and mapped parents; all original paths/modes preserved. Forty-eight changed blob pairs match only the reviewed transformations. Reachable rewritten graph before the final record: 35 commits, 338 trees, 614 blobs.
- GPT-6 Luna/medium independently verified all six branch tips/two trees, all 35 messages and metadata/topology, 614 blobs and protected-file instances. All 705 production-file instances and license/notices/ignore blobs are exact; seven historical test-file instances contain only the equal-length synthetic account substitution. Root reviewed the delegate findings against the explicit user authorization.
- All eight refs were integrated atomically only after staging verification. No remote or live backup ref was created. The additional existing `ORIG_HEAD` pseudo-ref was found in administrative-file inspection and preserved with its mapped target, recorded in `pseudo-ref-map.json`. Local Git configuration selects the supplied identity; global configuration was not written.
- All 266 authored tests passed before rewriting (2.138 seconds) and after rewriting (2.144 seconds). No generator behavior changed.
- All 73,683 pre-existing files under ignored inputs/outputs were SHA-256 rehashed: contents, sizes, modification times and complete file path inventory are unchanged. Only the new ignored run directory is excluded from this comparison. No external backup was modified.
- After backup validation, original live reflogs were expired and unreachable objects garbage-collected. All 35 old commit objects are absent from the live object store; all mapped commits remain available. All stored blob/commit/tag objects, reachable filenames, current tracked/new authored files and reflogs pass the concrete personal-path/former-email scan. Full Git fsck passes; all eight ref names, the worktree and mapped ORIG_HEAD are preserved. No backup/original/replacement/remote refs exist.
- Exact current bytes of LICENSE, LICENSING.md, THIRD_PARTY_NOTICES.md, pyproject.toml and .gitignore match the original backup; production source is unchanged. Artifact paths/backups remain ignored and no input/output path is tracked.
- Local Markdown targets/fragments, task schema/status/dependencies, 35 mapped commit targets and historical-ID labels are checked by `check-docs.py`; `git diff --check` passes. Final post-commit validation is recorded in the ignored logs. Root reviewed the independent documentation audit and qualified stale historical licensing/no-rewrite wording without changing source evidence.

# Links

- [Cleanup scope, backup details and limitations](../../reference/HISTORY_CLEANUP.md)
- [Complete old-to-new commit map](../../reference/HISTORY_CLEANUP_COMMIT_MAP.tsv)
- [Identity practices and historical correction](../../reference/PUBLIC_GIT_IDENTITY_PRACTICES.md)
- [Publication review](../../reference/PUBLIC_REPOSITORY_REVIEW.md)
- [Current state](../../project/CURRENT_STATE.md)
- [License scope](../../../LICENSING.md)
