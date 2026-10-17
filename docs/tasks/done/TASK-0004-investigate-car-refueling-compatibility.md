---
id: TASK-0004
title: Investigate car refueling compatibility
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0002
owner: root
---

# Goal

Determine why passenger cars can or cannot refuel at selected stations in ATS map expansions or reworks, and assess whether a minimal compatibility patch is feasible.

# Context

Refueling failure may arise from physical station accessibility, interaction-trigger configuration, fuel or vehicle eligibility, or separate mechanisms working together. Investigate these possibilities independently before proposing a fix; do not assume a single simple cause.

# Scope

- Use the verified baseline and inspection workflow from [TASK-0002](../done/TASK-0002-establish-reference-data-and-extraction.md).
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

Completed 2026-10-17. REFUELING_RESEARCH_FINDINGS.md records 191 official station PPDs (all 44 sampled _rt variants contain GAS flags 1), field layout and v23/v24/v25 limits, and real Reforma MX9 source/modified SHA-256 values. A bounded sector parse verified the actual prefab UID and linked service UID; this supports a service/spawn rebuilding limitation instead of a PPD-only runtime-success claim. Five PPD tests verify inspection, preservation, idempotence, and refusal cases; the experiment was also packaged through the real CLI. Physical access, fuel increase, and truck regression testing remain pending in TASK-0007.

# Links

- [Establish reference data and extraction](../done/TASK-0002-establish-reference-data-and-extraction.md)
- [SCS archives and definitions](../../reference/SCS_ARCHIVES_AND_DEFINITIONS.md)
- [Map structure and compatibility](../../reference/MAP_STRUCTURE_AND_COMPATIBILITY.md)
- [Passenger-car refueling](../../reference/PASSENGER_CAR_REFUELING.md)
- [Local input inventory](../../reference/LOCAL_INPUT_INVENTORY.md)
- [First generator increment design](../done/TASK-0005-design-first-generator-increment.md)
