---
id: TASK-0004
title: Investigate car refueling compatibility
status: backlog
priority: high
repositories:
  - .
depends_on:
  - TASK-0002
owner: shared
---

# Goal

Determine why passenger cars can or cannot refuel at selected stations in ATS map expansions or reworks, and assess whether a minimal compatibility patch is feasible.

# Context

Refueling failure may arise from physical station accessibility, interaction-trigger configuration, fuel or vehicle eligibility, or separate mechanisms working together. Investigate these possibilities independently before proposing a fix; do not assume a single simple cause.

# Scope

- Use the verified baseline and inspection workflow from [TASK-0002](TASK-0002-establish-reference-data-and-extraction.md).
- At task start, collect examples of working and affected stations and relevant map locations from the user or available evidence.
- Compare station geometry/access, interaction-trigger data, and fuel/vehicle eligibility data across working and affected examples.
- Identify which conditions are static-data properties and which require in-game observation.
- Assess a minimal evidence-supported patch and its feasibility, or document the blocker and next evidence needed.
- Keep implementation and generator design for a later task.

# Implementation Plan

1. Confirm baseline inputs and select representative working and affected stations.
2. Trace station access and interaction data for each example, keeping physical accessibility separate from trigger configuration.
3. Trace fuel definitions and vehicle eligibility data, checking whether the station and vehicle support the same fuel behavior.
4. Compare findings across examples, identify independent or interacting causes, and state remaining uncertainty.
5. Describe a minimal patch candidate and its feasibility, or document a concrete blocker and the next evidence needed.
6. Define safe in-game confirmation where static inspection cannot establish actual vehicle access or refueling behavior.

# Acceptance Criteria

- The task provides an evidence-backed explanation of refueling behavior for examined stations, or documents a concrete blocker and required next evidence.
- The analysis separately addresses physical accessibility, interaction triggers, and fuel/vehicle eligibility, and explains evidence linking these mechanisms.
- The result proposes a minimal compatibility patch with a feasibility assessment, or documents a concrete blocker and the next evidence needed to proceed.
- Findings distinguish static-data conclusions from behavior confirmed in game.
- Any in-game validation plan protects existing progression and truck behavior by using a disposable or copied profile and records relevant logs, vehicle/fuel context, prompts, and actual refueling outcomes. It does not prescribe an unsafe profile reset command.

# Verification

- Record compared file paths, station/location identifiers, observed data, and source provenance as the analysis proceeds.
- For in-game checks, record the game and mod setup, observations, and relevant logs; label unperformed checks as pending rather than verified.

# Links

- [Establish reference data and extraction](TASK-0002-establish-reference-data-and-extraction.md)
- [SCS archives and definitions](../../reference/SCS_ARCHIVES_AND_DEFINITIONS.md)
- [Map structure and compatibility](../../reference/MAP_STRUCTURE_AND_COMPATIBILITY.md)
- [Passenger-car refueling](../../reference/PASSENGER_CAR_REFUELING.md)
- [Local input inventory](../../reference/LOCAL_INPUT_INVENTORY.md)
- [First generator increment design](TASK-0005-design-first-generator-increment.md)
