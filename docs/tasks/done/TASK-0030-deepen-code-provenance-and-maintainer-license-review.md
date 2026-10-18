---
id: TASK-0030
title: Deepen implementation provenance and explain maintainer license choices
status: done
priority: high
repositories: [.]
depends_on: [TASK-0029]
owner: shared
---

**History note:** repository commit IDs in this document are pre-cleanup identifiers; use the [old-to-new mapping](../../reference/HISTORY_CLEANUP.md#commit-identifiers). Upstream object IDs and artifact checksums are unchanged.

# Goal

Provide a materially deeper technical source/provenance audit and a practical author-focused license comparison, correct the intentional Git identity assessment, and recommend license paths from the audit evidence.

# Context

**Documented — user correction, 2026-10-18:** `szczerb (legacy placeholder email)` is the user's deliberate pseudonym/placeholder identity. It is not a disclosed private mailbox and should not trigger a history rewrite. The user is an experienced developer new to maintaining public projects and wants practical differences from the author perspective.

The previous TASK-0029 source comparison was bounded; the user now requests broader and historical review. Authors already consulted upstream C# sources, so this cannot be described retroactively as a clean-room implementation. A technical audit is evidence for a licensing decision, not a legal independence certificate.

# Scope

- Complete map parser/planner comparison, helper/token/PPD/rest/parser provenance and all production-module coverage.
- Original introduction/history and exact upstream source-object identification, with expressive similarity distinguished from required format facts.
- Public Git identity practices and MIT/Apache/MPL/GPL choices, distribution/contribution obligations and practical maintainer consequences.
- No license assignment, source rewriting, Git identity changes, history rewriting, upstream contact or publication.

# Implementation Plan

| Assignment | Model / effort | File ownership |
| --- | --- | --- |
| Complete map parser and bulk fuel provenance | GPT-6 Sol / high | `DEEP_MAP_PARSER_PROVENANCE_REVIEW.md` |
| Helpers and remaining production-module provenance | GPT-6 Sol / high | `DEEP_HELPER_PROVENANCE_REVIEW.md` |
| Historical grants and maintainer license comparison | GPT-6 Sol / high | `MAINTAINER_LICENSE_CHOICES.md` |
| Git identity correction, legal-source framing and integration | Root model | Other documentation and final assessment |

Keep evidence and reference downloads beneath ignored `local_outputs/work/2026-10-18_19-28-19/`.

# Acceptance Criteria

- Deeper reports provide a coverage matrix, original/current source comparisons and specific source/provenance evidence rather than merely repeating the earlier disclaimer.
- Credible adaptations or review gaps are identified with concrete next actions; negative findings have bounded confidence and never claim a clean-room process.
- The Git placeholder-email finding is corrected throughout current guidance without changing user configuration/history.
- Practical license choices distinguish private use, distribution, closed forks, network use, patents, contributions and already granted rights. The recommendation follows the technical evidence.
- Sources and facts are dated and labelled; documentation/task/evidence checks pass and the verified milestone is committed locally.

# Verification

Completed 2026-10-18. Baseline `d2e7d9c`, 33 reachable commits, initially clean checkout.

- Three GPT-6 Sol/high delegates delivered the complete map/planner review, helper/all-module audit and maintainer license comparison. Root reviewed the scope and requested exact historical comparator checks instead of leaving missing-source assumptions.
- Map review covers the 393-line reader, every helper and 34 branches/35 item IDs, plus the 412-line fuel planner and original/later changes. Helper review inventories all 29 production modules and 25 test files, directly compares the high-risk functions and records differences and limitations.
- Root fetched 19 historical public GitHub blobs into ignored storage; every content identity matches the saved tree entry. Exact Token/Trigger source, LICENSE files, READMEs and project metadata close specific earlier evidence gaps. The historical GPLv2 grant is established; an operative later-version grant was not found. Containing commit IDs remain unknown but are not needed to identify the verified bytes.
- No obvious substantial translated routine was identified. Shared data layouts, source-observed behavior and the token formula are recorded. No clean-room or legal-independence certificate is claimed; unretained sources and legal classification remain explicit limits. No code rewrite is supported or performed by this review.
- Root verified the deliberate alias/placeholder across all 33 author/committer records and withdrew the false private-email inference. Git identity/configuration and history remain unchanged.
- The integrated recommendation now favors MIT for simple reuse, MPL for file-level reciprocity, or GPL for strong copyleft/actual applicable upstream obligations. The user has not selected a license; no root LICENSE, remote, publication or upstream message was added.
- Documentation checks cover links/fragments, task metadata/status/dependencies, 12 immutable input identities, ignored evidence and staged whitespace. No utility/game tests were rerun because only documentation changed. Reports and downloads: `local_outputs/work/2026-10-18_19-28-19/`.

This closes the requested deeper technical audit and explanation milestone; it does not select the user's reuse policy or certify publication rights.

# Links

- [Integrated implementation assessment](../../reference/IMPLEMENTATION_INDEPENDENCE_ASSESSMENT.md)
- [Complete map audit](../../reference/DEEP_MAP_PARSER_PROVENANCE_REVIEW.md)
- [Helper audit](../../reference/DEEP_HELPER_PROVENANCE_REVIEW.md)
- [Maintainer license choices](../../reference/MAINTAINER_LICENSE_CHOICES.md)
- [Git identity practices](../../reference/PUBLIC_GIT_IDENTITY_PRACTICES.md)

- [Earlier publication review](../done/TASK-0029-review-publication-rights-and-license-options.md)
- [Versioned-content review](../../reference/PUBLIC_REPOSITORY_REVIEW.md)
- [Earlier license recommendation](../../reference/OPEN_SOURCE_LICENSE_RECOMMENDATION.md)
