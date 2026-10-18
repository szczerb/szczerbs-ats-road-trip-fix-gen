# ADR-0009: Report courier inputs before generating fixes

## Context

Date: 2026-10-18. The user requests the first courier processor increment as analysis/reporting only, including whether company job-selection avatars have separate truck/car points. Existing context audits describe one input to courier job generation, while recent map parsing can now expose physical Company items and linked prefab/node data. An apparently shared check-in does not establish the complete Road Trip market algorithm.

## Decision

Separate processor operation mode from topic selection. `ProcessorMode.ANALYZE` permits the `courier` topic and writes a source-relative report through `analyze-map`; default `GENERATE` mode continues to reject courier. Fuel/rest generation interfaces, metadata and existing outputs remain unchanged. Analysis never invokes the mod writer, including when inspection is partial or another selected planner proposes resources.

The courier report inventories effective source-owned Company placements, resolves nearby prefab/node references and joins effective company editor definitions, actual prefab descriptors, context classification and static job-definition matches. Preserve differences between editor declarations and actual placed models. Report official exclusion evidence, raw unresolved fields and ambiguity explicitly. Keep physical selection nodes, generic PPD Company Point locators and loading/spawn arrays distinct.

Report inspection coverage separately from per-location unresolved links and runtime eligibility. A partial report is useful evidence and must not become an empty "already covered" mod result or proof that a city has no courier jobs. Do not synthesize tags, copy fuel flags, reset markets, inspect live profile state or generate courier overrides in this increment. The old context-only `courier-audit` and historical explicitly requested context experiment remain available with their original boundaries.

## Consequences

This provides a deterministic starting point for later company/city comparisons and reviewed patch design. It does not simulate market refresh, routing, rating, discovery, vehicle eligibility or offer delivery. Shared-marker conclusions must retain the distinction between observed data structure and an in-game controlled test. Versioned game/mod inputs and explicit package priority remain required.

See [TASK-0018](../../tasks/done/TASK-0018-report-courier-company-locations.md), [marker research](../../reference/COURIER_MARKER_RESEARCH.md), and [earlier courier findings](../../reference/COURIER_RESEARCH_FINDINGS.md).
