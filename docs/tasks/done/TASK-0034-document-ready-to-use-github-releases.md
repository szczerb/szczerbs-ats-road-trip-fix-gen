---
id: TASK-0034
title: Document ready-to-use experimental GitHub releases
status: done
priority: medium
repositories: [.]
depends_on: [TASK-0033]
owner: shared
---

# Goal

Help players find the maintainer-uploaded tank and job-compatibility mods without running the generators.

# Context

**Documented — maintainer report, 2026-10-18:** the latest experimental gas-tank and job-compatibility builds were manually attached to GitHub Releases. The source-only README wording needs to distinguish downloadable release assets from the tracked Git tree.

# Scope

README, current state and task tracking only. No release upload/edit, push, visibility change, generated-package modification or new release-asset/gameplay audit.

# Implementation Plan

1. Add a prominent Releases link naming both ready-to-use mods and explaining mod assets, manual installation and generator-only Python/Extractor requirements.
2. Correct source-only statements while retaining local map-generation scope, version evidence and experimental status.
3. Delegate a bounded wording check to GPT-6 Luna/low, verify documentation, and commit locally.

# Acceptance Criteria

- README links to the Releases index and names reasonable gas tank upgrades and Job Types Compat Mustang.
- Readers can distinguish attached mod assets from automatic source archives and generator dependencies.
- No unverified release tag, asset hash, visibility, map-release or gameplay claim is introduced.

# Verification

Completed 2026-10-18. The private release page was unavailable to the anonymous browser, so availability is explicitly based on the maintainer's report and the stable Releases index is used instead of guessed asset/tag links. No private account credentials were accessed.

GPT-6 Luna/low independently reviewed the README diff read-only and found no wording or evidence-scope issue. Local Markdown targets/fragments, task schema/status and whitespace checks pass. Runtime tests were not rerun for this documentation-only change. Detailed checker output is local and ignored under `local_outputs/work/2026-10-18_21-50-00/`.

# Links

- [README download section](../../../README.md#download-ready-to-use-experimental-mods)
- [GitHub Releases](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases)
- [Current state](../../project/CURRENT_STATE.md)
- [Prior source audit](../../reference/PUBLIC_SOURCE_REAUDIT_2026_10_18.md)
