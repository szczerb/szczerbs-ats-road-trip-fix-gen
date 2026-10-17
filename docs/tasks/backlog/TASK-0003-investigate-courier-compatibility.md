---
id: TASK-0003
title: Investigate courier compatibility
status: backlog
priority: high
repositories:
  - .
depends_on:
  - TASK-0002
owner: shared
---

# Goal

Determine how Road Trip courier jobs are enabled in baseline game data and why they do or do not work in selected map expansions or reworks, then assess whether a minimal compatibility patch is feasible.

# Context

Courier compatibility may depend on map, economy, company, or other data relationships. A proposed Gemini marker or prefix has not been proven to be the relevant mechanism. Establish the cause from the reference setup and distinguish static data evidence from behavior confirmed in game.

# Scope

- Use the verified baseline and inspection workflow from [TASK-0002](TASK-0002-establish-reference-data-and-extraction.md).
- At task start, collect examples of working and affected cities, companies, and related locations from the user or available evidence.
- Compare relevant original and modded courier, economy, company, and map data for those examples.
- Investigate candidate Gemini markers, naming prefixes, or other mechanisms as hypotheses, not assumptions.
- Assess the smallest evidence-supported compatibility change and whether it can be generated safely.
- Keep implementation and generator design for a later task.

# Implementation Plan

1. Confirm baseline inputs and select representative working and affected examples.
2. Trace courier job data relationships in original and modded files, documenting each relevant reference and its source.
3. Test whether suspected markers or prefixes correlate with courier availability and identify alternative explanations where evidence permits.
4. Describe a minimal patch candidate and its feasibility, or document the specific blocker and next evidence needed.
5. State what static inspection establishes and what requires in-game confirmation, including any safe test setup.

# Acceptance Criteria

- The task produces an evidence-backed account of the courier availability mechanism for the examined cases, or documents a concrete blocker and required next evidence.
- The Gemini marker/prefix hypothesis is supported, rejected, or explicitly unresolved based on observed data; it is not treated as established without evidence.
- The result proposes a minimal compatibility patch with a feasibility assessment, or documents a concrete blocker and the next evidence needed to proceed.
- Findings identify which conclusions come from static data and which have been confirmed in game.
- Any in-game validation plan protects existing progression and truck behavior by using a disposable or copied profile, records relevant logs, and accounts for job-market refresh behavior when needed. It does not prescribe an unsafe profile reset command.

# Verification

- Record compared file paths, identifiers, relationships, and source provenance as analysis proceeds.
- For in-game checks, record the game and mod setup, observations, and relevant logs; label unperformed checks as pending rather than verified.

# Links

- [Establish reference data and extraction](TASK-0002-establish-reference-data-and-extraction.md)
- [SCS archives and definitions](../../reference/SCS_ARCHIVES_AND_DEFINITIONS.md)
- [Map structure and compatibility](../../reference/MAP_STRUCTURE_AND_COMPATIBILITY.md)
- [Economy and courier jobs](../../reference/ECONOMY_AND_COURIER_JOBS.md)
- [Local input inventory](../../reference/LOCAL_INPUT_INVENTORY.md)
- [First generator increment design](TASK-0005-design-first-generator-increment.md)
