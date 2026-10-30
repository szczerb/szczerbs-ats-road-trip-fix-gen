---
id: TASK-0056
title: Clean research history and prepare a public PR
status: done
priority: high
repositories: [.]
depends_on: [TASK-0054]
owner: codex
---

# Goal

Remove disclosed host paths from the research branch history, make reviewed parking evidence configurable, scope the North Platte supplement correctly, and push the cleaned branch with an open PR targeting master. Do not merge the PR.

# Context

**Documented — user authorization, 2026-10-30:** rewrite only the research branch, preserve master and other branches, add a relative-path rule, fix the reviewed portability issues, and publish the branch through a PR. Source archives, existing generated packages and game/profile state remain unchanged. The repository is public; squash merging alone does not hide an uploaded branch history.

# Scope

- Verified local Git backup, branch-only history transformation and independent publication review.
- Explicit reviewed station-model evidence input, reproducible local preparation, missing-input diagnostics and original fingerprint gates.
- Apply the North Platte supplement only to its selected source partition.
- Relative-path working rules, whitespace cleanup, regression verification and a source-only PR.

# Implementation Plan

1. Verify ignored recovery backups, rewrite historical local-path references and preserve author/date/message/topology evidence.
2. Update agent rules and working agreements; resolve portable evidence configuration and selected-source supplement gating.
3. Verify regression coverage, full historical publication inventory and unchanged unrelated refs/resources.
4. Push only the reviewed branch, create and attach an open PR; do not merge it.

Delegation: GPT-6.1 Sol/high owns evidence configuration/preparation, CLI plumbing, authored catalog metadata, related tests and its reference. GPT-6 Luna/high independently audits backup/history/publication invariants. The parent owns history rewrite, truck gating, instructions, integration, task/current-state documentation and publication. Delegates share the research checkout with separate file ownership.

# Acceptance Criteria

- All affected branch-only historical document versions are sanitized; unrelated historical bytes and commit metadata remain exact.
- No absolute host paths are newly introduced into versioned material or messages.
- Realistic generation accepts explicitly prepared local evidence and clearly diagnoses missing evidence; broad mode needs no converted models.
- Unrelated truck processing succeeds without ATS Expansion while applicable reviewed-source drift still blocks.
- Full tests, whitespace and independent publication checks pass; only the cleaned branch is pushed and its PR remains open.

# Verification

**Observed locally — 2026-10-30:** the original branch tip had 41 commits beyond master. The ignored Git archive was compared member-by-member with the live common Git directory; the full bundle verifies and both backup SHA-256 values are recorded. Working evidence: `local_outputs/work/2026-10-30_16-50-51/public-pr-cleanup/`. Independent historical verification passes for all 41 mapped commits, exact seven blob replacements and unchanged unrelated refs. It scanned 106 reachable commits and 1263 distinct text blobs, with zero removed-path or credential/private-key pattern hits. The final 30-file workingtree review found no new host path literals, credentials or binary/source-asset payloads. Independent receipts are in the adjacent ignored `local_outputs/work/2026-10-30_16-50-51/publication-audit/` directory.

**Observed locally — final implementation verification, 2026-10-30:** all **644 tests pass** (`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q`, 4.831 seconds); the focused truck/source-gating suite passes 37 tests. Checks cover missing/changed/ambiguous evidence, all four CLI forwarding paths, early failure, broad defaults, provider/hash drift and unrelated stock-sector processing. Whitespace checks are clean. Root independently compares the new catalog with the original loader: every semantic field, source/material/state pin and both accepted Dawson areas are identical, excluding evidence locations. Setuptools package-data checks prove the metadata is included and usable without checkout documentation. Preparation imports and validates eight retained PIM/PIT files into a new directory; no fresh conversion or gameplay result is claimed.

Root rehashes all eight existing r13 SCS archives against their audited delivery checksums and verifies the existing ZIP SHA-256 remains `d683759ae42e65f3de631164d75c91e5225aa5e4db0d805fc0d0e91d5a917d2c`. No existing generated package changes. The latest remote master still matches the unchanged local base; no existing research-branch PR or remote branch was found. **Observed remotely — 2026-10-30:** the sanitized research branch was created on origin without a force push. [PR #1](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/pull/1) is OPEN, targets master and is MERGEABLE with CLEAN merge status; automatic merge is disabled. The initial remote head matches reviewed implementation commit `e1f5334bc288251160b6a9887e20fea59857f886`. The PR is attached to the chat. This final documentation closure is pushed to the same PR branch; the PR remains open for a subsequent squash merge. No master update, generated-mod upload or game/profile operation occurred.


**Observed locally — PR review follow-up, 2026-10-30:** Copilot identified a concave-lot containment gap where an edge leaves and re-enters through boundary vertices away from its midpoint. The shared containment check now tests intervals split at boundary contacts, including collinear overlaps, while retaining boundary-inclusive behavior. Regression coverage includes the reproduced notch, reversed winding, crossing, tangency, shared boundaries, nonfinite inputs and the station access caller. All **647 tests pass** and `git diff --check` is clean. An independent GPT-6 Luna/medium review found no actionable defect in the revised algorithm for valid simple polygons; the parent integrated the change and verification. No new gameplay or generated-package validation is implied.

# Links

- [Working agreements](../../project/WORKING_AGREEMENTS.md#portable-versioned-paths)
- [Current cleanup and commit mapping](../../reference/RESEARCH_BRANCH_PUBLICATION_2026_10_30.md)
- [Portable evidence](../../reference/STATION_PARKING_EVIDENCE.md)
- [Historical cleanup precedent](../../reference/HISTORY_CLEANUP.md)
- [R13 handoff](../../reference/TRUCK_REST_COVERAGE_1_61_R13.md)
