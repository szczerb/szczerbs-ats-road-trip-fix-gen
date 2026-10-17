# Task Board

Use the [workflow](../project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md) and [task template](../templates/TASK_TEMPLATE.md). File directory and frontmatter status must agree. IDs are unique and stable across moves; blockers are recorded inside tasks. The required metadata is `id`, `title`, `status`, `priority`, `repositories`, `depends_on`, `owner`.

## Active

No active tasks.

## Backlog

| Task | Priority | Depends on |
| --- | --- | --- |
| [TASK-0002: Establish reference data and extraction](backlog/TASK-0002-establish-reference-data-and-extraction.md) | high | — |
| [TASK-0003: Investigate Courier Job compatibility](backlog/TASK-0003-investigate-courier-compatibility.md) | high | TASK-0002 |
| [TASK-0004: Investigate car refueling compatibility](backlog/TASK-0004-investigate-car-refueling-compatibility.md) | high | TASK-0002 |
| [TASK-0005: Design first generator increment](backlog/TASK-0005-design-first-generator-increment.md) | medium | TASK-0003, TASK-0004 |

Courier and refueling research have equal priority. Concrete city/station examples are collected when the relevant investigation begins.

## Done

- [TASK-0001: Initialize project](done/TASK-0001-initialize-project.md) — documentation, references, inventory, and verification completed on 2026-10-17.
