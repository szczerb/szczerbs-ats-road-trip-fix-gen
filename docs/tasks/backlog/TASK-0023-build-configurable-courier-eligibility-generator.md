---
id: TASK-0023
title: Build the configurable standalone courier eligibility generator
status: backlog
priority: high
repositories:
  - .
depends_on:
  - TASK-0022
owner: shared
---

# Goal

Implement the planned deterministic analysis/generation commands for a separate practical-cargo eligibility mod, starting with the reviewed Mustang profile.

# Context

The user requested a tooling plan and human cargo groups, with vehicle transfers unchanged and owned-car use as the goal. Planning is complete under TASK-0022; implementation has not started. Shared job definitions may also affect Quick Jobs and other muscle-tagged cars.

# Scope

- Validate the proposed TOML policy and pinned job/cargo source definitions.
- Add report-only analysis and explicit experimental generation with lossless targeted vehicle-array edits.
- Preserve all other fields, all job IDs and all nine transfer units; keep map generators separate.
- Use existing archive/stack/writer helpers with compatible metadata support and ignored timestamped artifacts.

# Implementation Plan

| Work | Proposed model / effort |
| --- | --- |
| Configuration, classification/reporting and authored fixtures | GPT-6 Luna / medium |
| Source-preserving patcher, CLI and writer integration | GPT-6 Sol / medium |
| Bounded review of uncertain resource overrides and field preservation | GPT-6.1 Sol / medium |

# Acceptance Criteria

- Example policy selects exactly its expected reviewed jobs, with unknown/drifting/conflicting inputs disclosed and generation blocked.
- Analysis writes no mod. Generation changes only permitted vehicle arrays and preserves complete canonical source resources and transfer records.
- Metadata identifies a separate courier mod; previous map packages/tests retain their behavior.
- Meaningful tests cover config selection, transfer guards, raw-byte preservation, ambiguity/source drift, analysis boundaries and deterministic packaging.
- A real pinned-source audit demonstrates exact selected additions and unchanged fields. Runtime Dispatch, attachment and delivery checks remain separate under TASK-0007.

# Verification

Not started. See the linked plan for the proposed CLI/configuration and initial coverage counts. No production implementation or mod was created during planning.

# Links

- [Generator plan](../../reference/COURIER_ELIGIBILITY_GENERATOR_PLAN.md)
- [Proposed policy](../../examples/mustang-practical-courier.toml)
- [Planning milestone](../done/TASK-0022-plan-practical-courier-eligibility-tooling.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
