---
id: TASK-0005
title: Design the first generator increment
status: backlog
priority: medium
repositories:
  - .
depends_on:
  - TASK-0003
  - TASK-0004
owner: shared
---

# Goal

Choose and specify an evidence-backed first implementation increment for a compatibility mod generator, based on the completed courier and passenger-car refueling investigations.

# Context

The first implementation target should follow demonstrated compatibility mechanisms and feasible minimal patches. Courier behavior and passenger-car refueling may rely on different data and validation paths, so the generator's initial scope and technical choices should remain open until both investigations report their outcomes.

# Scope

- Review the results and proposed patch feasibility from [TASK-0003](TASK-0003-investigate-courier-compatibility.md) and [TASK-0004](TASK-0004-investigate-car-refueling-compatibility.md).
- Select a bounded first implementation target using evidence, impact, and validation feasibility.
- Specify the initial generator interface and design, including language, CLI behavior, input schema, output layout, and validation approach as needed for the selected target.
- Identify assumptions, limitations, and follow-on work.
- Do not begin implementation in this design task.

# Implementation Plan

1. Summarize the evidence, uncertainties, and minimal patch feasibility from both prerequisite investigations.
2. Compare viable first increments and select one with a clear rationale; if neither is feasible, document the blocker and evidence needed to revisit the choice.
3. Define the smallest useful generator behavior, its inputs and outputs, and how it will validate generated data.
4. Record language and CLI choices, input schema, output structure, and validation boundaries based on the selected increment rather than preselecting them in advance.
5. Identify the next bounded implementation task and any architecture decision required by the selected design.

# Acceptance Criteria

- The design explicitly uses the completed outcomes of both prerequisite research tasks.
- It chooses an evidence-backed first target and explains its minimal patch feasibility, or documents why no target is currently feasible and the next evidence needed.
- For a selected target, the design specifies the generator's scope, language, CLI behavior, input schema, output layout, and validation approach sufficiently to create a bounded implementation task.
- Validation requirements distinguish static validation from in-game confirmation and preserve progression and truck behavior through disposable or copied profile use when in-game checks are needed.
- The design identifies meaningful limitations and produces a linked next implementation task or a documented blocker.

# Verification

- Confirm both prerequisite task outcomes are complete and link their evidence before making the target decision.
- Check that each proposed design choice follows from the selected evidence-backed target and that unresolved behavior is labeled as unverified.

# Links

- [Courier compatibility research](TASK-0003-investigate-courier-compatibility.md)
- [Car refueling compatibility research](TASK-0004-investigate-car-refueling-compatibility.md)
- [Establish reference data and extraction](TASK-0002-establish-reference-data-and-extraction.md)
- [SCS archives and definitions](../../reference/SCS_ARCHIVES_AND_DEFINITIONS.md)
- [Map structure and compatibility](../../reference/MAP_STRUCTURE_AND_COMPATIBILITY.md)
- [Economy and courier jobs](../../reference/ECONOMY_AND_COURIER_JOBS.md)
- [Passenger-car refueling](../../reference/PASSENGER_CAR_REFUELING.md)
- [Local input inventory](../../reference/LOCAL_INPUT_INVENTORY.md)
