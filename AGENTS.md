# Workspace Agent Guide

## Goal and current boundary

Investigate and generate small ATS compatibility mods for Road Trip Courier Jobs and passenger-car refueling in map expansions and reworks. Both investigations have equal priority. Initialization is complete; the authorized next milestone is autonomous research, archive inspection tooling, and an evidence-supported generator proof of concept. Read current state before assuming a diagnosis or generator exists. ATS is the product target; ETS2 documentation supplies shared engine context only where applicable.

Workspace-authored documentation must be in English.

## Reading order

1. [README](README.md), [project brief](docs/project/PROJECT_BRIEF.md), and [current state](docs/project/CURRENT_STATE.md).
2. [Working agreements](docs/project/WORKING_AGREEMENTS.md) and [task workflow](docs/project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md).
3. The relevant task from the [task board](docs/tasks/README.md), related [ADRs](docs/architecture/decisions/README.md), and [incident evidence](docs/incidents/README.md).
4. Relevant references: [archives and definitions](docs/reference/SCS_ARCHIVES_AND_DEFINITIONS.md), [maps and compatibility](docs/reference/MAP_STRUCTURE_AND_COMPATIBILITY.md), [economy and Courier Jobs](docs/reference/ECONOMY_AND_COURIER_JOBS.md), [car refueling](docs/reference/PASSENGER_CAR_REFUELING.md), and [local inputs](docs/reference/LOCAL_INPUT_INVENTORY.md).

## Task and evidence rules

- Use `TASK-XXXX-<slug>.md` with frontmatter `id`, `title`, `status`, `priority`, `repositories`, `depends_on`, `owner`; sections `Goal`, `Context`, `Scope`, `Implementation Plan`, `Acceptance Criteria`, `Verification`, `Links`. For this single repository, use `repositories: [.]`.
- Keep directory and status synchronized: `docs/tasks/backlog/` → `active/` → `done/`. Record blockers inside the task; move to done only after acceptance and verification. Preserve history and update links when tasks move.
- Record durable architecture/interface/workflow choices as ADRs. Use incidents for reproducible failures needing a separate evidence trail; ordinary planned research stays in tasks.
- Label substantive technical findings **Documented**, **Observed locally**, **Hypothesis**, or **Unknown**. Record source, applicable version, and inspection date. Prefer primary technical sources and flag old documentation's limits.
- Treat Gemini's missing-marker/prefix explanation as a hypothesis. Do not infer Courier Job support from traditional freight definitions, or assume refueling needs the same or a simpler fix.
- Update current state when evidence, blockers, priorities, or completion change. Keep canonical facts in references and link rather than duplicating detail.

## Orchestration and delegation

The user generally starts chats with a capable but expensive model. Delegate bounded tasks and choose cost-effective models and effort levels. Use lower-cost models for inventory and mechanical documentation; reserve stronger models for uncertain technical analysis and final integration. Give each delegate explicit file ownership when sharing a checkout and review its findings.

Whenever in Plan Mode, include a table breaking down tasks and the models/effort used or proposed. Distinguish actual assignments from future recommendations. Record material delegated work and verification in the task.

## Artifact handling

- Treat `local_inputs/` archives as immutable. Preserve existing Git exclusions for `local_inputs/` and `local_outputs/`.
- Keep extracted assets, game/DLC files, large logs, reports, downloaded tools, and generated mods beneath ignored `local_outputs/` subdirectories. Keep small authored summaries in documentation. See [workspace structure](docs/reference/WORKSPACE_STRUCTURE.md).
- Do not commit supplied mods or copies of game assets. Do not extract whole archives for a metadata-only question. Record limitations when a format/tool is unavailable.
- No automatic installation into a live mod directory, profile modification, economy reset, or in-game validation is part of initialization. Future experiments must state their setup and preserve the user's profile.

## Commit messages

Commit coherent, verified milestones locally without asking for routine confirmation. This is currently a single-contributor repository with no remote; do not configure a remote or push. Use `master` directly for small documentation changes and stable milestones. Use a `codex/` branch for substantial or experimental tooling; use worktrees only where concurrent edits benefit from checkout isolation. Merge verified work locally, and preserve unvalidated experiments on a clearly reported branch. Prefer the existing checkout and share ignored original inputs read-only rather than copying archives into worktrees.

Use meaningful messages that let a future reader understand the change without opening the diff. Prefer a concise subject and a body for non-trivial commits. For broad, checkpoint, architectural, or first-project commits include:

- Major areas created or changed and why the change exists.
- Important user feedback, caveats, or direction that affects interpretation.
- Verification performed, when relevant.

Avoid vague subjects such as "scaffold foundation" unless the body explains what was scaffolded and why.
