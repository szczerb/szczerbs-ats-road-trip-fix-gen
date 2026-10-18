---
id: TASK-0021
title: Review Mustang cargo exclusions and standalone eligibility mod feasibility
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0020
owner: shared
---

# Goal

Determine whether jobs allowing the Crown Victoria but excluding the Mustang have evidence-backed cargo/vehicle reasons, and whether a separate vehicle-eligibility mod is feasible.

# Context

**Documented — user request, 2026-10-18:** investigate job names/titles and whether excluded cargo is too large for the Mustang; the user expects cargo fitting the Victoria may also fit the Mustang. Separately investigate editable vehicle/job matches as a possible scope extension, distinct from map fixes. The user asks for Luna because remaining main-model quota is low.

**Observed locally:** stock definition/rating comparisons show fewer entries listing Mustang tags, not measured live offers. Cargo titles alone do not establish physical capacity or compatible cargo attachments.

# Scope

- Inspect exact excluded stock job families, cargo definitions, localized names where available, and relevant allowed-job controls.
- Distinguish physical evidence, vehicle-transfer mechanics, class restrictions, plausibility and unknown runtime constraints.
- Research SII eligibility override semantics, smallest standalone design, source preservation, conflicts and validation needs.
- No generated mod, production-code changes, gameplay, profile/economy changes or source-archive mutation.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Cargo-fit and exclusion review | GPT-6 Luna / medium | MUSTANG_COURIER_CARGO_REVIEW.md and ignored evidence |
| Separate eligibility-modding review, sequential second pass | Same GPT-6 Luna / medium agent | COURIER_VEHICLE_ELIGIBILITY_MOD.md and ignored evidence |
| Bounded review, scope/task links and local commit | Root | Remaining documentation |

A second Luna instance was rejected by the app's thread limit. Reuse the successfully created Luna sequentially; do not substitute an expensive agent.

# Acceptance Criteria

- Job/cargo families and relevant names are identified without presenting template counts as offers.
- Mustang/Crown Victoria suitability conclusions distinguish observed game data from real-world guesses and untested geometry.
- Feasibility identifies actual editable fields, overwrite/collision boundaries and future runtime acceptance.
- Any standalone mod is clearly separate from map-fix generation; no implementation is implied by research completion.
- Documentation/task/link/exclusion checks pass; utility tests are unnecessary without utility changes.

# Verification

2026-10-18: both research passes completed using the explicitly configured GPT-6 Luna / medium agent `/root/mustang_cargo_fit`, sequentially after a second instance was rejected by the app thread limit. No expensive substitute was used. Root reviewed the notes and independently recomputed all class intersections with the existing parser, correcting a preliminary grouping error before handoff.

The 149 units partition into 52 sedan/Mustang-shared, 95 sedan-only and two Mustang-only entries. The 28-row sedan-only family table sums to 95: 88 cargo-bearing entries and seven no-cargo standard Car Jockey entries. Exact IDs, ratings, cargo references and source hashes are in `local_outputs/work/2026-10-18_03-23-44/sedan-only-courier-units.json`. Job source SHA-256 `4a62420d6bd79086fdf4fa1caa3e37a6bb53636a1c82d65b78ab7eb0049b2d28`; cargo source `230c1aef59446b944e02f138ca2802c3560d3e9c2663070120e6cbcd854f4ffa`. These are stock definition counts, not offers. Rendered UI titles and physical cargo fit remain unverified; semantic family names and localization keys are explicitly identified as such.

The separate feasibility note identifies editable class-level `vehicle_types[]` arrays and preserves cargo/rating/context/distance/other fields in its proposed experiment. Same-path complete resource overrides are distinguished from unsupported duplicate-unit merging across different files. Adding sedan globally to the Mustang is broader than editing reviewed jobs; adding muscle/veteran to jobs affects all cars carrying those tags. Installed additive courier files provide syntax evidence, not a guarantee of safe partial overrides or runtime loading/delivery.

Scope extension is recorded as research for a standalone vehicle-eligibility mod, separate from map fixes; no mod was generated. Cargo attachment, pickup, driving, completion, Quick Jobs/Dispatch differences and conflicts require later controlled gameplay. Utility source, game/profile, supplied archives and existing packages remain unchanged. Documentation/task/link/artifact checks are recorded in `local_outputs/work/2026-10-18_03-22-01/documentation-qa.json`; no utility tests were rerun for this documentation-only milestone.

# Links

- [Availability research](../../reference/COURIER_JOB_AVAILABILITY_RESEARCH.md)
- [Prior courier schema](../../reference/COURIER_RESEARCH_FINDINGS.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)

- [Cargo review](../../reference/MUSTANG_COURIER_CARGO_REVIEW.md)
- [Standalone eligibility assessment](../../reference/COURIER_VEHICLE_ELIGIBILITY_MOD.md)
