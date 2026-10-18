---
id: TASK-0023
title: Build the configurable standalone courier eligibility generator
status: done
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

The user requested a tooling plan and human cargo groups, with vehicle transfers unchanged and owned-car use as the goal. Planning is complete under TASK-0022, and the standalone generator is implemented. Shared job definitions may also affect Quick Jobs and other muscle-tagged cars.

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

**Observed locally, 2026-10-18, ATS 1.61.3.18:** The source-pinned example resolved 149 canonical job IDs, including 95 sedan-only units. It selected 58 cargo jobs for `muscle`, left 30 cargo jobs disabled, and preserved all nine vehicle-transfer jobs. The planner reparsed the complete replacement, compared all fields, and reversed each inserted declaration to prove original bytes outside those insertions were unchanged. Report-only analysis emitted no mod; experimental generation emitted one standalone package and an audit. The independent package review checked its CRC, single canonical resource, 58 exact additions, and nine byte-identical transfer bodies. The package SHA-256 is `e2f3b803e27435aad3d9db74fcc227a91aff0863a406fc995c91638d510d883b`.

The core and workflow were split into bounded delegated implementation and parent integration/review. Authored tests cover TOML validation, toggle-derived selection, source drift, unknown cargo/empty jobs, duplicate IDs across effective resources, source priority, comments, CRLF/BOM/Unicode preservation, analysis-only behavior, and package metadata. A 224-test suite passed at the integration checkpoint; subsequent repository testing and final task closure are owned by the parent. The generated audit (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-56-10/practical-courier-jobs/audit.json`) and independent review (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-47-10/batch-review/courier-verification-final.json`) contain the exact source and changed-unit evidence. Game behavior remains unverified under TASK-0007.

Final acceptance, 2026-10-18: all **233** authored tests pass. Independent final-package verification proves 58 exact inserted declarations and all nine unchanged transfer bodies; the workflow explicitly requires `coverage.complete is True` before packaging. Source tags changed by third-party vehicle mods are an explicit external assumption in the guide. No game validation was performed or inferred.

# Links

- [Overnight delivery task](../done/TASK-0024-deliver-overnight-test-mod-batch.md).

- [Generator plan](../../reference/COURIER_ELIGIBILITY_GENERATOR_PLAN.md)
- [Implemented generator guide](../../reference/PRACTICAL_COURIER_GENERATOR.md)
- [Proposed policy](../../examples/mustang-practical-courier.toml)
- [Planning milestone](../done/TASK-0022-plan-practical-courier-eligibility-tooling.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
