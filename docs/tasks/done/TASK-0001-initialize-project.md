---
id: TASK-0001
title: Initialize the ATS Road Trip compatibility project
status: done
priority: high
repositories:
  - .
depends_on: []
owner: root
---

# Goal

Create an English-language agent workspace, sourced reference library, local input inventory, and research backlog for Courier Jobs and passenger-car refueling, with equal research priority.

# Context

Approved initialization plan, 2026-10-17. The user reports missing courier opportunities and car refueling in map mods. The cause and automatic-fix feasibility are unconfirmed. The original workspace contained Git metadata, artifact exclusions, and local input/output directories.

# Scope

- Bootstrap and specialize documentation, task/ADR/incident conventions, and templates.
- Preserve user delegation/model-cost and commit-message instructions in AGENTS.md.
- Document primary sources, representative input observations, and uncertainty.
- Seed TASK-0002 through TASK-0005 with dependencies and equal courier/refueling priority.
- Exclude utility code, tool installation, full extraction, generated patches, city-specific diagnosis, and game/profile changes.

# Implementation Plan

1. Run the bootstrap generator in merge mode after its successful dry run; preserve existing exclusions.
2. Integrate root/project/workflow documentation and reference links.
3. Delegate technical references, read-only inventory, and backlog authoring with separate file ownership.
4. Review technical claims, relative links, schemas, dependencies, artifact handling, and task status consistency.
5. Record verification, then move this task to done and update the board/current state and incoming links.

# Acceptance Criteria

- Project intent, current limitations, equal research priorities, and reading order are explicit.
- All five technical reference topics and five supplied inputs are represented with evidence status, sources, versions where known, and inspection date.
- No unsupported claim establishes markers, prefixes, or a simple refueling fix as the cause.
- Four backlog tasks use consistent schemas, dependencies, concrete outcomes, and future validation boundaries.
- Relative links and task directory/status agreement pass checks; local artifact exclusions are preserved.
- Actual verification is recorded before completion; no assets, utility implementation, or in-game validation are claimed.

# Verification

Completed on 2026-10-17 after the following checks:

- Bootstrap generator ran in merge mode after the planning dry run; the original `.gitignore` remains byte-for-byte equal to `git show HEAD:.gitignore`.
- A standard-library Python documentation check passed for 26 Markdown files and 134 relative links/heading anchors. It checked required task metadata/sections, unique IDs, status/directory agreement, repository paths, dependency existence and cycles, and equal priority for TASK-0003 and TASK-0004.
- Inventory checks matched all five filenames and exact sizes against filesystem metadata, and ZIP compression/entry counts against central-directory metadata. Header reads confirmed three ZIP and two HashFS v2 inputs. Small manifest reads confirmed declared versus commented compatibility and the listed dependency tokens. No full extraction, whole-archive CRC scan, or full-file hash scan was performed.
- `git check-ignore` passed for an existing input archive and representative generated/extracted output paths. All 29 new paths were documentation or empty task-directory placeholders; no input/output assets entered the changed-file list.
- Trailing whitespace and final newlines were checked across every Markdown file, including untracked files; `git diff --check` also passed. No optional third-party layout references or directories were introduced.
- Root reviewed the authored documentation and technical source claims. A separate technical review confirmed historical-source caveats and identified two wording issues: inventory provenance and a project recommendation mislabeled as an SCS fact. Both were corrected.
- Final task-move verification checks incoming links and status agreement again after moving this record to done.

No utility tests or in-game validation apply to this documentation milestone. Runtime, interfaces, patch mechanism, actual game compatibility, and the reported defects remain unverified. No game/profile operation, tool installation, or generated fix was performed.

| Delegated work | Model | Effort | Ownership |
| --- | --- | --- | --- |
| Technical references and source verification | GPT-6 Sol | medium | Four technical reference files |
| Local input inventory | GPT-6 Luna | medium | Local input inventory reference |
| Research backlog | GPT-6 Luna | medium | TASK-0002 through TASK-0005 |

Root agent owns project/workflow documentation, integration, and final verification. The prior planning inspection also used GPT-6 Luna at medium effort.

# Links

- [Project brief](../../project/PROJECT_BRIEF.md)
- [Current state](../../project/CURRENT_STATE.md)
- [Reference library](../../README.md#technical-references)
- [Task board](../README.md)
