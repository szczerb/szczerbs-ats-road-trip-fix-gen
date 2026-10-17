# Workspace Agent Guide

## Goal and current boundary

Investigate and generate small ATS compatibility mods for Road Trip Courier Jobs and passenger-car refueling in map expansions and reworks. Both investigations have equal priority. Initialization and the first research/prototype milestone are complete; the user subsequently authorized map-wide fuel generation. Five experimental r1 map packages and a separate connector fix now have complete static target coverage; read the [batch result](docs/reference/FUEL_FIX_BATCH_1_61_R1.md), [connector findings](docs/reference/CONNECTOR_FUEL_FIXES.md), and [map-wide command guide](docs/reference/MAP_WIDE_FUEL_GENERATOR.md). A tested inspection/generation prototype now exists; the user reports successful car and truck refueling with Helena-area sample 2, while broader validation remains open. Read current state for its exact scope. ATS is the product target; ETS2 documentation supplies shared engine context only where applicable.

Workspace-authored documentation must be in English.

## Reading order

1. [README](README.md), [project brief](docs/project/PROJECT_BRIEF.md), and [current state](docs/project/CURRENT_STATE.md).
2. [Working agreements](docs/project/WORKING_AGREEMENTS.md) and [task workflow](docs/project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md).
3. The relevant task from the [task board](docs/tasks/README.md), related [ADRs](docs/architecture/decisions/README.md), and [incident evidence](docs/incidents/README.md).
4. Relevant references: [archives and definitions](docs/reference/SCS_ARCHIVES_AND_DEFINITIONS.md), [maps and compatibility](docs/reference/MAP_STRUCTURE_AND_COMPATIBILITY.md), [economy and Courier Jobs](docs/reference/ECONOMY_AND_COURIER_JOBS.md), [car refueling](docs/reference/PASSENGER_CAR_REFUELING.md), and [local inputs](docs/reference/LOCAL_INPUT_INVENTORY.md).

See also [installed baseline](docs/reference/RESEARCH_BASELINE.md), [courier findings](docs/reference/COURIER_RESEARCH_FINDINGS.md), [refueling findings](docs/reference/REFUELING_RESEARCH_FINDINGS.md), [tool usage](docs/reference/TOOLING.md), [validation handoff](docs/reference/VALIDATION_HANDOFF.md), [starter-area sample](docs/reference/STARTER_AREA_SAMPLE.md), [gameplay results](docs/reference/VALIDATION_RESULTS.md), and [same-position sample 2](docs/reference/OVERLAPPING_FUEL_SAMPLE.md).

Fuel package name, author, revision and icon requirements are in the [metadata contract](docs/reference/MOD_METADATA.md). Use an explicit short map name and retain the experimental suffix. See [original icon proposals](assets/mod-icons/README.md).

For combined-map fuel work, read [connector findings and confirmed source priority](docs/reference/CONNECTOR_FUEL_FIXES.md). Preserve explicit dependency order. Each fuel fix belongs directly above its own source; source-relative installation and the effective data needed during generation are separate checks.

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

- Treat `local_inputs/` as read-only. Do not extract into it, rename or edit supplied archives, or automatically remove sidecars or other untrusted adjacent metadata. Preserve sidecars unless the user explicitly requests a change. Preserve existing Git exclusions for `local_inputs/` and `local_outputs/`.
- Put all new scratch, extracted samples, reports, temporary archive staging, and expressly requested input-sidecar moves under `local_outputs/work/<YYYY-MM-DD_HH-MM-SS>/`, with the timestamp in Europe/Warsaw local time. Put generated mods under `local_outputs/generated/<YYYY-MM-DD_HH-MM-SS>/`, with human-readable filenames that identify the map and ATS/map version. Keep each run's work together; do not move or delete older outputs automatically.
- Keep newly created extracted assets, game/DLC files, large logs, reports, downloaded tools, and generated mods beneath ignored timestamped `local_outputs/` run directories. Existing historical artifacts, including tools outside the new layout, stay at their current paths; do not move or remove them automatically. Keep small authored summaries in documentation. See [workspace structure](docs/reference/WORKSPACE_STRUCTURE.md).
- Small original project-authored icon exports and prompts may be tracked under `assets/mod-icons/`; large generated originals stay under ignored `local_outputs/work/<YYYY-MM-DD_HH-MM-SS>/artwork/`.
- Do not commit supplied mods or copies of game assets. Do not extract whole archives for a metadata-only question. Record limitations when a format/tool is unavailable.
- No automatic installation into a live mod directory, profile modification, economy reset, or in-game validation is part of initialization. Future experiments must state their setup and preserve the user's profile.

## Commit messages

Commit coherent, verified milestones locally without asking for routine confirmation. This is currently a single-contributor repository with no remote; do not configure a remote or push. Use `master` directly for small documentation changes and stable milestones. Use a `codex/` branch for substantial or experimental tooling; use worktrees only where concurrent edits benefit from checkout isolation. Merge verified work locally, and preserve unvalidated experiments on a clearly reported branch. Prefer the existing checkout and share ignored original inputs read-only rather than copying archives into worktrees.

Use meaningful messages that let a future reader understand the change without opening the diff. Prefer a concise subject and a body for non-trivial commits. For broad, checkpoint, architectural, or first-project commits include:

- Major areas created or changed and why the change exists.
- Important user feedback, caveats, or direction that affects interpretation.
- Verification performed, when relevant.

Avoid vague subjects such as "scaffold foundation" unless the body explains what was scaffolded and why.
