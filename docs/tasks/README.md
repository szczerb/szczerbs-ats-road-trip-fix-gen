# Task Board

Use the [workflow](../project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md) and [task template](../templates/TASK_TEMPLATE.md). Status and directory must agree; IDs are stable, dependencies use IDs, and blockers belong inside tasks.

## Active

- [TASK-0007: Validate experiments in game](active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) — first Helena-area car-refueling success and patched truck-map disappearance reported by the user; physical truck/reload, both-vehicle support, other locations and courier validation remain open.

## Backlog

No backlog tasks. Follow-up multi-point work is scoped in active TASK-0007 pending design and comparison.

## Done

| Task | Outcome |
| --- | --- |
| [TASK-0001: Initialize project](done/TASK-0001-initialize-project.md) | Documentation, references, inventory, and workflow |
| [TASK-0002: Establish reference data/extraction](done/TASK-0002-establish-reference-data-and-extraction.md) | Installed baseline, provenance, and verified HashFS access |
| [TASK-0003: Investigate courier compatibility](done/TASK-0003-investigate-courier-compatibility.md) | Context mechanism, counterevidence, concrete alias candidate |
| [TASK-0004: Investigate car refueling](done/TASK-0004-investigate-car-refueling-compatibility.md) | GAS flag evidence, placed station/service, bounded descriptor experiment |
| [TASK-0005: Design first generator increment](done/TASK-0005-design-first-generator-increment.md) | Python inspection/experimental patch design and validation boundaries |

- [TASK-0006: Build inspector and experimental generators](done/TASK-0006-build-inspector-and-experimental-generators.md) — 39 tests and real-input static checks passed; experimental packages and handoff produced.

- [TASK-0008: Prepare starter-area samples](done/TASK-0008-prepare-starter-area-sample.md) — effective garage comparison, pinned single-pump generator, Helena-area/Great Falls packages, and 43 passing tests.

Courier Jobs and car refueling retain equal research priority. Completed research and static tests do not complete the pending gameplay-validation task.
