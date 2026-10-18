---
id: TASK-0031
title: Apply AGPLv3 and explain local-path publication implications
status: done
priority: medium
repositories: [.]
depends_on: [TASK-0030]
owner: shared
---

# Goal

Apply the user's AGPL license choice consistently and explain the concrete local paths previously flagged for public repository review.

# Context

**Documented — user direction, 2026-10-18:** start with AGPL after discussing strong copyleft and later relicensing. The user also requests a fuller explanation of local paths. The earlier audit and recommendations are complete; the maintainer's preference supersedes the MIT policy recommendation without changing provenance evidence.

# Scope

- Unmodified official AGPLv3 text, AGPL-3.0-only copyright/scope notice, Python distribution metadata/notices, current guidance and a durable ADR.
- Read-only local-path inventory and explanation of disclosure, portability and history. Do not sanitize paths, change Git identity, rewrite history, publish, rebuild gameplay mods, modify inputs or change profiles.
- Preserve separate upstream/game/map/mark rights. Root licensing does not relicense generated `.scs` contents automatically.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Bounded tracked local-path scan | GPT-6 Luna / medium | Read-only; no shared-file edits |
| License text, scope, metadata, documentation and verification | Root model | License, project metadata and documentation |

# Acceptance Criteria

- Full official AGPL version 3 text and explicit AGPL-3.0-only notice are present and consistent with package metadata.
- Built Python distributions include LICENSE, LICENSING.md and THIRD_PARTY_NOTICES.md.
- Current guidance records the user's decision; historical audit outcomes remain identifiable as historical.
- Local-path explanation uses verified examples and separates path strings, linked artifact contents, runtime defaults and historical commits.
- Documentation/task/metadata checks pass; no input/artifact, runtime source, Git identity or generated-mod changes are committed.

# Verification

Completed 2026-10-18, baseline `da76a0f`. Evidence remains ignored under `local_outputs/work/2026-10-18_19-56-58/`.

- Downloaded the official full text from `https://www.gnu.org/licenses/agpl-3.0.txt`; root LICENSE is byte-identical, 34,523 bytes, SHA-256 `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`. The official appendix remains unmodified; LICENSING.md and package metadata explicitly select AGPL-3.0-only.
- Added copyright/scope/warranty/contribution terms, preserved external rights and source-provenance limits, recorded ADR-0016 and updated current guidance. No per-file source edits or gameplay-package rebuilds were needed.
- Built a source distribution using installed setuptools 68.1.2 in an ignored staging copy. Inspected PKG-INFO: License is AGPL-3.0-only, all three License-File records are present, and LICENSE/LICENSING.md/THIRD_PARTY_NOTICES.md contents match exactly. No game/mod/output artifacts enter the distribution. An initial pip wheel invocation was unavailable because system Python lacks pip/wheel; a wheel was not built. Source-package validation passed without installing dependencies.
- GPT-6 Luna/medium performed the read-only bounded path/default review. Root independently enumerated baseline blobs, correcting the initial delegate count to 22 prefix matches on 19 lines in 15 files. Examples and scope are recorded in the linked identity/path guide. The test fixture's length-sensitive purpose was inspected; no source paths, ignored artifacts or history were modified.
- Documentation checks cover links/fragments, task IDs/status/dependencies, unchanged 12 local input identities and excluded artifacts. TOML/package metadata and license notices were checked directly; Git whitespace checks pass. Runtime/game tests were not rerun because runtime code and generated packages are unchanged.

This milestone applies the license and explains path disclosure. It does not sanitize history, publish the repository or certify third-party redistribution rights.

# Links

- [Scope and contribution terms](../../../LICENSING.md)
- [License decision](../../architecture/decisions/ADR-0016-license-project-under-agpl-v3.md)
- [Local-path explanation](../../reference/PUBLIC_GIT_IDENTITY_PRACTICES.md#local-paths-in-the-publication-review)
- [Deeper audit](../../reference/IMPLEMENTATION_INDEPENDENCE_ASSESSMENT.md)
- [Preceding task](../done/TASK-0030-deepen-code-provenance-and-maintainer-license-review.md)
