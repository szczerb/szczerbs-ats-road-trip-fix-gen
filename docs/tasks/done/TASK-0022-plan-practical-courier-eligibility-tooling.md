---
id: TASK-0022
title: Plan configurable practical-cargo eligibility tooling for the Mustang
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0021
owner: shared
---

# Goal

Produce a concrete tooling plan and initial human-readable configuration for a separate mod expanding practical cargo jobs for the user's owned Mustang, preserving vehicle-transfer definitions.

# Context

**Documented — user direction, 2026-10-18:** plan tooling, group similar cargo from a human perspective and use ordinary real-world judgment for initial inclusion. Certificates, customs documents, keys, samples and small parts should be included. Focus on the owned car; leave vehicle transfers separate.

**Observed locally:** stock classification is class-based; adding `muscle` reaches the Mustang and other muscle-tagged cars. Shared definitions may also affect Quick Jobs; a Dispatch-only switch is unverified. Physical fit and increased live offers remain untested.

# Scope

- Plan, not production implementation or mod generation.
- Define explicit versioned cargo groups, defaults and exact source-family membership, with rationale and complete accounting of reviewed candidates.
- Specify deterministic analysis/generation, source preservation, metadata, conflict handling and validation; reuse existing archive/package helpers where suitable.
- Preserve all vehicle transfers, existing job fields, live profiles, input archives and previous outputs.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Tooling plan and proposed TOML defaults | GPT-6 Luna / medium, reused agent | COURIER_ELIGIBILITY_GENERATOR_PLAN.md and docs/examples/mustang-practical-courier.toml |
| Review, source/config coverage check, task/current-state integration and commit | Root | Remaining documentation and ignored checks |

Future implementation assignments must retain a task/model breakdown and reserve stronger models for uncertain engine/interface decisions.

# Acceptance Criteria

- The initial policy includes the user's clear small-cargo examples, separates comparable families from express/fragile/rating variants and explains uncertain defaults.
- Configuration uses explicit stable mappings, not LLM or fuzzy-title decisions at generation time.
- Owned-car intent, class-wide side effects, shared-market limitations and unchanged transfers are explicit.
- Proposed interfaces, supported source/version boundaries, minimal-edit invariants, metadata and meaningful verification are implementation-ready.
- TOML parses; mappings/counts are checked against pinned stock definitions; docs/task/link/artifact checks pass.

# Verification

2026-10-18: GPT-6 Luna / medium drafted and revised the plan and proposed TOML; root reviewed practical defaults, source-preserving edits, class/shared-market limits and metadata separation. No generator or mod was implemented.

The TOML parses with Python 3.11 `tomllib`. Root independently checked both pinned source hashes, all 149 source IDs/digest, all nine no-cargo transfer IDs, disjoint exact coverage of 46 cargo IDs across all 88 sedan-only cargo jobs, family/cargo agreement and each group's count. The default groups select 58 definitions (32 cargo IDs) and leave 30 (14 IDs) unchanged. Explicit group toggles determine totals dynamically; source-catalog assertions are independent of those toggles. The source-ID digest uses UTF-8 newline-separated sorted IDs with a trailing newline. The initial independent check is `local_outputs/work/2026-10-18_03-32-23/independent-config-check.json`; delegate evidence is `local_outputs/work/2026-10-18_03-33-59/proposed-config-static-coverage.json`. Final config checks and documentation QA are recorded in the root run directory.

The plan specifies analysis and explicit experimental generation, expected source drift/conflict failures, unchanged transfer units and non-target bytes, compatible writer metadata, meaningful authored tests and future manual Dispatch/cargo completion controls. TASK-0023 remains unstarted; physical fit, market output and Dispatch-only behavior are not established. Inputs, game/profile, utility source and existing packages remain unchanged. No utility tests were rerun for this planning-only milestone.

# Links

- [Cargo review](../../reference/MUSTANG_COURIER_CARGO_REVIEW.md)
- [Separate mod feasibility](../../reference/COURIER_VEHICLE_ELIGIBILITY_MOD.md)
- [Research milestone](../done/TASK-0021-research-mustang-cargo-and-eligibility-mod.md)

- [Tooling plan](../../reference/COURIER_ELIGIBILITY_GENERATOR_PLAN.md)
- [Proposed configuration](../../examples/mustang-practical-courier.toml)
- [Future implementation](../done/TASK-0023-build-configurable-courier-eligibility-generator.md)
