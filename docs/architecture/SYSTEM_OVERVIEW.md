# System Overview

## Current implementation

The Python prototype implements archive inspection/extraction, explicit virtual package order/mounts, include-aware SII reading, static courier coverage, and bounded experimental context/PPD generation and a pinned single-pump sector experiment. Outputs include deterministic packages and change/provenance reports; they are not installed or validated in game. See [tool usage](../reference/TOOLING.md).

## Prospective pipeline

The following stages describe the intended direction, subject to [research](../tasks/README.md). They do not select implementation modules, wire formats, or file-editing strategies.

| Stage | Intended result | Evidence needed before implementation |
| --- | --- | --- |
| Inspect inputs | Identify archives, versions, manifests, and relevant resources | ZIP/HashFS support and actual package layouts |
| Establish effective data | Understand resources visible with the selected game/DLCs/mod stack | Exact versions, DLC mounts, load order, and overridden paths |
| Diagnose compatibility | Explain missing courier/refueling support | Working/affected comparisons, relevant definitions/prefabs/sectors, and in-game evidence |
| Generate minimal overrides | Change only resources necessary for a supported fix | Proven mechanism, conflict behavior, and whether binary assets are involved |
| Package | Produce an identifiable compatibility mod | Valid package format, dependencies, version policy, and installation/load-order requirements |
| Validate | Demonstrate intended behavior and check regressions | Static checks plus controlled game tests for cars, trucks, and shared-profile behavior |

Courier and refueling research may lead to distinct mechanisms. Definition-only changes are a possibility, not a requirement that can currently be promised. Prefab or sector overrides may broaden conflicts and output size; their necessity must be established first.

## Open design decisions

[ADR-0002](decisions/ADR-0002-use-python-inspection-and-bounded-experimental-patches.md) selects Python, CLI behavior, external extraction, deterministic ZIP packaging, and bounded static patch rules. [ADR-0003](decisions/ADR-0003-allow-pinned-single-pump-sector-experiments.md) adds only a reviewed single-pump sector transformation. Stable public APIs, general map-sector editing, legacy PPD conversion, and automated gameplay validation remain open. [TASK-0005](../tasks/done/TASK-0005-design-first-generator-increment.md) reviews both investigation outcomes before choosing the first implementation target. Record durable choices as [ADRs](decisions/README.md).

## Data and documentation boundaries

Original archives remain in ignored `local_inputs/`; extracted/reference data and future generated packages belong in ignored `local_outputs/`. Commit authored source and small evidence summaries only. [Workspace structure](../reference/WORKSPACE_STRUCTURE.md) explains storage conventions; the [reference library](../README.md#technical-references) records supported facts and unknowns.
