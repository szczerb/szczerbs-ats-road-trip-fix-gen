# Task Board

Use the [workflow](../project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md) and [task template](../templates/TASK_TEMPLATE.md). Status and directory must agree; IDs are stable, dependencies use IDs, and blockers belong inside tasks.

## Active


- [TASK-0007: Validate experiments in game](active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) — user reports successful car and truck refueling with overlapping sample 2; reload, other locations and courier validation remain open.

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

- [TASK-0009: Build overlapping fuel pair](done/TASK-0009-build-overlapping-fuel-pair.md) — source-pinned same-position truck/car candidate, original truck records preserved, 48 tests passed; runtime checks remain TASK-0007.

- [TASK-0010: Brand gas station fix packages](done/TASK-0010-brand-gas-station-fix-packages.md) — requested metadata, selected icon C, identical sample-2 gameplay payload and 51 passing tests.

- [TASK-0011: Generate map-wide fuel fixes](done/TASK-0011-generate-map-wide-fuel-fixes.md) — five complete r1 packages, 2,281 new car points, original truck records retained, 111 passing tests and independent full-output checks.

- [TASK-0012: Inspect and fix map connectors](done/TASK-0012-inspect-and-fix-map-connectors.md) — connector-derived 50-point Western Canada–ProMods fix, no station fix needed for OtherMaps, explicit source order and 116 passing tests.

Courier Jobs and car refueling retain equal research priority. Completed research and static tests do not complete the pending gameplay-validation task.
