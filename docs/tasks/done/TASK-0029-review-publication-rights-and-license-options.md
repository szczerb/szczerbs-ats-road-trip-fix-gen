---
id: TASK-0029
title: Review publication terms, versioned content and open-source license options
status: done
priority: high
repositories: [.]
depends_on: [TASK-0006, TASK-0023, TASK-0028]
owner: shared
---

**History note:** repository commit IDs in this document are pre-cleanup identifiers; use the [old-to-new mapping](../../reference/HISTORY_CLEANUP.md#commit-identifiers). Upstream object IDs and artifact checksums are unchanged.

# Goal

Provide a sourced publication-readiness review and a recommended open-source license, distinguishing generator source publication from distribution of generated SCS-derived mods. Completion permits specific unresolved rights questions with the evidence needed to resolve them; it does not certify legal compliance or authorize publication.

# Context

**Documented — user request, 2026-10-18:** use subagents to research terms for mods containing only SCS stock data, review anything already versioned that may be unsuitable for public release, and suggest an open license. Current code consults GPL-licensed TruckLib sources and invokes a separately downloaded extractor. The project has no selected root license. Earlier provenance notes must not be treated as a completed derivative-work assessment.

# Scope

- Primary SCS/Steam conditions relevant to stock job definitions and Ford DLC chassis overrides, including clear limits on available evidence.
- Tracked files and reachable Git history, code/fixture provenance, artwork, local/private information and excluded source/output assets.
- Version-specific license compatibility, attribution and a conditional recommendation; do not install a license without the user's selection.
- No GitHub publication, remote setup, messages to rights holders, history rewrite, source archive edits or artifact redistribution.

# Implementation Plan

| Assignment | Model / effort | File ownership |
| --- | --- | --- |
| SCS-derived mod publication terms | GPT-6 Sol / high | `SCS_MOD_PUBLICATION_TERMS.md` |
| Versioned content and history review | GPT-6 Sol / high | `PUBLIC_REPOSITORY_REVIEW.md` |
| Open-source license recommendation | GPT-6 Sol / high | `OPEN_SOURCE_LICENSE_RECOMMENDATION.md` |
| Source checks, integration and publication boundary | Root model | Task, index, current state, notices and integration |

Use ignored evidence directories under `local_outputs/work/2026-10-18_19-11-25/`. Review delegated conclusions and separate factual inventories from legal interpretation.

# Acceptance Criteria

- All three reviews exist with links, dated evidence, specific scope and unresolved questions.
- The source/history review identifies concrete findings rather than inferring clearance from `.gitignore` or a different implementation language.
- The recommendation checks the applicable GPL versions and distinguishes project licensing from rights in generated game/map resources.
- Report whether copied game/third-party assets, secrets or personal information were found; do not reproduce any sensitive values in tracked reports.
- No unselected license is applied and no publication occurs. Documentation links/status and evidence exclusions pass verification.

# Verification

Completed 2026-10-18. Baseline branch: `codex/overnight-test-mods`, HEAD `f7f05c2`, initially clean checkout. Completion means delivering the review, not clearing publication or applying a license.

- Three GPT-6 Sol/high agents wrote the separate SCS terms, versioned-content review and license recommendation. Root reviewed all reports and requested corrections for artwork badges, existing local generation support and Git tree/commit identity.
- Root independently opened the official SCS first post, scenario 3: a DLC-dependent, art-free DLC definition-property edit is accepted. The 2019 post is concrete policy evidence, not a bespoke ATS 1.61/Ford approval or a replacement for current upload terms. An ATS-specific EULA was not located; that is an evidence limit, not a prohibition.
- Versioned-content baseline: 205 paths, 32 reachable commits, 218 historical paths, 534 text blobs and 38 JPEG blobs. Credential patterns/commit messages and image metadata/contact-sheet checks found no likely secrets or supplied game/mod archives. The initial email concern was later withdrawn: the user deliberately uses an alias and reserved `.invalid` placeholder. Local account paths and Ford-like badges remain separate publication choices. A bounded side-by-side parser/source comparison found no obvious copied routine; legal independence remains unresolved.
- Root checked saved Git tree object identities, exact research-copy Git blob hashes (78 TruckLib, five Models, three Core local file instances), and the LICENSE blob against `/usr/share/common-licenses/GPL-2`: `d159169d1050894d3ea3b98e1c965c4058208fe1`. Historical “commit” terminology was corrected in canonical notices; exact operative later-version grants remain unverified.
- Recommendation: `GPL-2.0-only` as a conservative path after the listed notice/grant checks; MIT/Apache require confidence in independent code provenance. No license was chosen/applied, no remote/publication/contact/history rewrite occurred, and existing generated packages remain unchanged.
- Documentation QA checks relative links/fragments, task IDs/status/dependencies, 12 immutable input identities, artifact exclusions and staged whitespace. Utility/game tests were not rerun for this documentation-only milestone. Evidence: `local_outputs/work/2026-10-18_19-11-25/`.

Remaining release decisions are recorded in the three reports. They do not block completion of this requested research task.

Follow-up: [TASK-0030](../done/TASK-0030-deepen-code-provenance-and-maintainer-license-review.md) expands the implementation audit and corrects the placeholder-email assessment. No Git configuration/history change is needed for that address.

# Links

- [Task board](../README.md)
- [Third-party notices](../../../THIRD_PARTY_NOTICES.md)
- [SCS mod publication terms](../../reference/SCS_MOD_PUBLICATION_TERMS.md)
- [Versioned content and history review](../../reference/PUBLIC_REPOSITORY_REVIEW.md)
- [Open-source license recommendation](../../reference/OPEN_SOURCE_LICENSE_RECOMMENDATION.md)
- [Tank generator and source provenance](../../reference/REASONABLE_GAS_TANK_UPGRADES.md)
- [Job generator and source provenance](../../reference/PRACTICAL_COURIER_GENERATOR.md)
