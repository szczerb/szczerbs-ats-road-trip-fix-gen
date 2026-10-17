# System Overview

## Current implementation

This repository contains project documentation and a research backlog. There is no utility or generated compatibility mod. The input inventory is a static authored record, not a public API or an executable inspector.

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

Programming language, CLI/UI, public API, input/output schemas, extraction integration, patch algorithm, packaging format, unsupported-case behavior, and validation automation remain undecided. [TASK-0005](../tasks/backlog/TASK-0005-design-first-generator-increment.md) reviews both investigation outcomes before choosing the first implementation target. Record durable choices as [ADRs](decisions/README.md).

## Data and documentation boundaries

Original archives remain in ignored `local_inputs/`; extracted/reference data and future generated packages belong in ignored `local_outputs/`. Commit authored source and small evidence summaries only. [Workspace structure](../reference/WORKSPACE_STRUCTURE.md) explains storage conventions; the [reference library](../README.md#technical-references) records supported facts and unknowns.
