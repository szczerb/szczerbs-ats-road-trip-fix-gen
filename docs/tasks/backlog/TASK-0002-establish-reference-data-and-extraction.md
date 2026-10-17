---
id: TASK-0002
title: Establish reference data and extraction workflow
status: backlog
priority: high
repositories:
  - .
depends_on: []
owner: shared
---

# Goal

Establish a reproducible, evidence-backed baseline for inspecting ATS and map-mod data that can support compatibility research and later generator design.

# Context

The project needs to compare original game data with mod data before proposing compatibility changes. The exact game build, DLC set, mod versions, load order, source archives, and usable HashFS extraction tools have not yet been recorded. Initialization should document candidates and requirements without installing tools or claiming an unverified extraction workflow.

# Scope

- Identify and record the exact ATS version/build, relevant DLCs, installed map-mod versions, and load order for the research setup.
- Locate original game data and identify archive contents relevant to courier jobs and passenger-car refueling.
- Identify HashFS inspection or extraction tools and verify their provenance, supported formats, and suitability for the recorded build before relying on them.
- Define a repeatable inventory and evidence-recording approach for original and modded data.
- Defer requests for specific working and affected city, company, or station examples until the dependent research tasks begin.
- Do not install tools or modify game or mod files as part of initialization.

# Implementation Plan

1. Record the ATS build and DLC context, map-mod versions, and load order available when the task starts.
2. Inventory original game data and relevant archives, noting paths, file identities, and provenance without altering them.
3. Research candidate HashFS tools, verify their source and compatibility claims, and document a reproducible inspection procedure.
4. Capture evidence and unresolved access or tooling limitations in the appropriate reference notes.

# Acceptance Criteria

- The baseline identifies the exact ATS build, relevant DLCs, map-mod versions, and load order, or records a specific blocker and the evidence needed to resolve it.
- Original data locations and relevant archive/file targets are recorded with enough detail for another researcher to reproduce the inventory.
- A HashFS tool and workflow are supported by verifiable evidence, or a documented blocker states what evidence or access is missing; no tool is represented as verified based only on an unsupported claim.
- The workflow distinguishes static archive inspection from in-game confirmation required by later tasks.
- No tool installation or game/mod data modification is performed in initialization.

# Verification

- Record source links, observed version/build identifiers, archive/file inventories, and tool compatibility evidence as work progresses.
- Mark an extraction or inspection step as verified only after performing it against the recorded setup; otherwise state what remains unverified.

# Links

- [SCS archives and definitions](../../reference/SCS_ARCHIVES_AND_DEFINITIONS.md)
- [Map structure and compatibility](../../reference/MAP_STRUCTURE_AND_COMPATIBILITY.md)
- [Economy and courier jobs](../../reference/ECONOMY_AND_COURIER_JOBS.md)
- [Passenger-car refueling](../../reference/PASSENGER_CAR_REFUELING.md)
- [Local input inventory](../../reference/LOCAL_INPUT_INVENTORY.md)
- [Courier compatibility research](TASK-0003-investigate-courier-compatibility.md)
- [Car refueling compatibility research](TASK-0004-investigate-car-refueling-compatibility.md)
- [First generator increment design](TASK-0005-design-first-generator-increment.md)
