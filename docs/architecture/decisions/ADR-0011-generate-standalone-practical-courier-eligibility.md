# ADR-0011: Generate practical courier eligibility as a separate mod

## Context

Date: 2026-10-18. The user approves implementing the source-pinned cargo policy for their owned Mustang and excludes vehicle-transfer changes. The reviewed source contains 149 jobs; the default policy selects 58 additional cargo definitions and preserves all nine transfer definitions. Shared definitions may also affect Quick Jobs and other muscle-tagged cars.

## Decision

Use an explicit TOML policy with stable human cargo groups, exact family/cargo mappings, source/version hashes and job-ID digest. Runtime selection is deterministic and does not use an LLM or fuzzy titles. Group toggles determine selected totals; source-catalog assertions are independent of those toggles. The first supported addition is `muscle`; jobs already admitting either Mustang tag remain unchanged.

Offer a report-only command and a separate explicit experimental-generation command. Insert new vehicle-array entries without changing any original byte; reparse and compare every non-target attribute, all job IDs and transfer records before publishing. Replace the complete canonical `def/car_job_data.sii` at the same virtual path, preserving unselected units. Reject drift, unknown/ambiguous configuration, unsupported source forms and duplicate job IDs across effective additive resources.

Package this as a standalone courier mod using the generic `other` manifest category, preserving the writer's existing `map` default. Do not change Ford tags, ratings, rewards, cargos, distances, contexts or map sectors. Do not bundle this policy into map fixes or claim Dispatch-only/model-exclusive effects. Write timestamped reports and packages without installation, profile changes or economy resets.

## Consequences

A complete canonical-file override can conflict with other mods replacing that path and must be regenerated/reviewed when sources change. Extra additive job definitions stay outside the initial selection policy. Increased static class eligibility does not prove more live offers, physical cargo attachment or delivery success; the user will perform those controls later.

See [TASK-0023](../../tasks/done/TASK-0023-build-configurable-courier-eligibility-generator.md), [policy](../../examples/mustang-practical-courier.toml) and [initial plan](../../reference/COURIER_ELIGIBILITY_GENERATOR_PLAN.md).
