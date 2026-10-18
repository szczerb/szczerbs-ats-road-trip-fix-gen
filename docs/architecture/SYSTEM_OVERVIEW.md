# System Overview

## Current implementation

The Python prototype implements archive inspection/extraction, explicit virtual package order/mounts, include-aware SII reading, static courier coverage, and deterministic experimental packaging. Fuel generation includes source-map station interactions and country petrol-price repair. Selected compatibility processors compose independent fuel/rest analysis before a package is written; Courier Job generation remains reserved for later implementation. See [processor configuration and boundaries](../reference/COMPATIBILITY_PROCESSORS.md) and [tool usage](../reference/TOOLING.md).

`ResourceStack` establishes effective game/DLC/map data. `ProcessorConfig` selects enum topics. The pipeline runs fuel before rest; the rest planner reads fuel's staged resources while retaining original source ownership. All enabled coverage checks must pass. A single writer then creates a source-specific experimental `.scs` with topic metadata and a provenance report. Live profiles and game files are never output targets.

Rest proximity uses original effective car areas from source sectors and a bounded neighbor halo. The user accepts extra permissions caused by missed car neighbors beyond that perimeter. Decisions are local to placed truck/bus areas, not shared prefab definitions. A private truck/bus/car action and selected placement aliases retain geometry and original shared actions. The 1,000-unit XZ threshold is a straight-line heuristic, not a route or runtime usability guarantee. [ADR-0008](decisions/ADR-0008-compose-processors-and-local-rest-polygons.md).

## Prospective pipeline

The following stages describe the broader direction, subject to [research](../tasks/README.md). Implemented processors have bounded support; this table does not establish automatic-fix feasibility for every topic or map layout.

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

[ADR-0002](decisions/ADR-0002-use-python-inspection-and-bounded-experimental-patches.md) selects Python, CLI behavior, external extraction, deterministic ZIP packaging, and bounded static patch rules. Later ADRs record pinned fuel samples, map-wide fuel graph edits, price policy and processor composition. Stable public APIs, unrestricted map-sector editing, full rest-layout coverage and automated gameplay validation remain open. [TASK-0005](../tasks/done/TASK-0005-design-first-generator-increment.md) records the historical first-increment decision. Record durable choices as [ADRs](decisions/README.md).

## Data and documentation boundaries

Original archives remain in ignored `local_inputs/`; extracted/reference data and future generated packages belong in ignored `local_outputs/`. Commit authored source and small evidence summaries only. [Workspace structure](../reference/WORKSPACE_STRUCTURE.md) explains storage conventions; the [reference library](../README.md#technical-references) records supported facts and unknowns.
