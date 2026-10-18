# System Overview

## Current implementation

The Python prototype implements archive inspection/extraction, explicit virtual package order/mounts, include-aware SII reading, static courier coverage, and deterministic experimental packaging. Fuel generation includes source-map station interactions and country petrol-price repair. Selected compatibility processors compose independent fuel/rest analysis before a package is written; general map Courier Job generation remains reserved; placed-company analysis is available through the report-only courier processor. See [processor configuration and boundaries](../reference/COMPATIBILITY_PROCESSORS.md) and [tool usage](../reference/TOOLING.md).

`ResourceStack` establishes effective game/DLC/map data. `ProcessorConfig` selects enum topics. The pipeline runs fuel before rest; the rest planner reads fuel's staged resources while retaining original source ownership. All enabled coverage checks must pass. A single writer then creates a source-specific experimental `.scs` with topic metadata and a provenance report. Before publication, generated private prefab identities must retain exact supported original context tags through traced sector transitions; conflicting or missing lineage blocks publication. [ADR-0010](decisions/ADR-0010-preserve-contexts-for-generated-prefab-aliases.md). Live profiles and game files are never output targets.

`ProcessorMode.ANALYZE` and `analyze-map` write an audit without invoking the package writer. Courier reads original effective inputs, exposes generic Company nodes and separate spawn arrays, joins semantic editor definitions and reports actual placed prefab contexts separately from editor contexts. It does not infer car-specific flags or runtime offers. Missing/ambiguous evidence remains visible. See [report semantics](../reference/COURIER_REPORTING.md) and [ADR-0009](decisions/ADR-0009-report-courier-inputs-before-generating-fixes.md).

Rest proximity uses original effective car areas from source sectors and a bounded neighbor halo. The user accepts extra permissions caused by missed car neighbors beyond that perimeter. Decisions are local to placed truck/bus areas, not shared prefab definitions. A private truck/bus/car action and selected placement aliases retain geometry and original shared actions. The 1,000-unit XZ threshold is a straight-line heuristic, not a route or runtime usability guarantee. [ADR-0008](decisions/ADR-0008-compose-processors-and-local-rest-polygons.md).

A separate source-pinned workflow implements reviewed job-class eligibility through `analyze-courier-eligibility` / `generate-courier-eligibility`. It reads game/Ford definition archives and declared dependencies, validates a TOML policy and exact source inventories, and inserts only reviewed `muscle` list entries. It uses the common writer with category `other`, without map processors. [Generator guide](../reference/PRACTICAL_COURIER_GENERATOR.md) and [ADR-0011](decisions/ADR-0011-generate-standalone-practical-courier-eligibility.md).

Known original irregular standalone rest shapes retain all geometry bytes, using disclosed conservative proximity and validated action-only retargets. Unknown action/flag/layout data still blocks. [ADR-0012](decisions/ADR-0012-preserve-irregular-source-rest-geometry.md).

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

Courier map diagnosis, standalone job-class eligibility, fuel interactions and rest actions have distinct scopes. The standalone eligibility mod changes one complete definition resource. Fuel/rest use private descriptors and whole-sector overrides, with their associated load-order conflicts; this does not establish a general map courier fix.

## Open design decisions

[ADR-0002](decisions/ADR-0002-use-python-inspection-and-bounded-experimental-patches.md) selects Python, CLI behavior, external extraction, deterministic ZIP packaging, and bounded static patch rules. Later ADRs record pinned fuel samples, map-wide fuel graph edits, price policy and processor composition. Stable public APIs, unrestricted map-sector editing, full rest-layout coverage and automated gameplay validation remain open. [TASK-0005](../tasks/done/TASK-0005-design-first-generator-increment.md) records the historical first-increment decision. Record durable choices as [ADRs](decisions/README.md).

## Data and documentation boundaries

Original archives remain in ignored `local_inputs/`; extracted/reference data and future generated packages belong in ignored `local_outputs/`. Commit authored source and small evidence summaries only. [Workspace structure](../reference/WORKSPACE_STRUCTURE.md) explains storage conventions; the [reference library](../README.md#technical-references) records supported facts and unknowns.
