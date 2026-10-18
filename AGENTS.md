# Workspace Agent Guide

## Goal and current boundary

Investigate and generate small ATS compatibility mods for Road Trip Courier Jobs and passenger-car refueling in map expansions and reworks. Both investigations retain equal research priority unless the user directs the current work elsewhere. Initialization and prototypes are complete; map-wide fuel generation now includes the user-authorized missing petrol-price repair. Read the [current r2 batch](docs/reference/FUEL_FIX_BATCH_1_61_R2.md), historical [r1 result](docs/reference/FUEL_FIX_BATCH_1_61_R1.md), [connector findings](docs/reference/CONNECTOR_FUEL_FIXES.md), and [map-wide command guide](docs/reference/MAP_WIDE_FUEL_GENERATOR.md). The user reports sample-2 dual-vehicle refueling and broad Canadian car access; new price/billing behavior and rest eligibility remain manually unverified. Read current state for exact scope. ATS is the product target; ETS2 documentation supplies shared engine context only where applicable.

Workspace-authored documentation must be in English.

## Reading order

1. [README](README.md), [project brief](docs/project/PROJECT_BRIEF.md), and [current state](docs/project/CURRENT_STATE.md).
2. [Working agreements](docs/project/WORKING_AGREEMENTS.md) and [task workflow](docs/project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md).
3. The relevant task from the [task board](docs/tasks/README.md), related [ADRs](docs/architecture/decisions/README.md), and [incident evidence](docs/incidents/README.md).
4. Relevant references: [archives and definitions](docs/reference/SCS_ARCHIVES_AND_DEFINITIONS.md), [maps and compatibility](docs/reference/MAP_STRUCTURE_AND_COMPATIBILITY.md), [economy and Courier Jobs](docs/reference/ECONOMY_AND_COURIER_JOBS.md), [car refueling](docs/reference/PASSENGER_CAR_REFUELING.md), and [local inputs](docs/reference/LOCAL_INPUT_INVENTORY.md).

See also [installed baseline](docs/reference/RESEARCH_BASELINE.md), [courier findings](docs/reference/COURIER_RESEARCH_FINDINGS.md), [refueling findings](docs/reference/REFUELING_RESEARCH_FINDINGS.md), [tool usage](docs/reference/TOOLING.md), [validation handoff](docs/reference/VALIDATION_HANDOFF.md), [starter-area sample](docs/reference/STARTER_AREA_SAMPLE.md), [gameplay results](docs/reference/VALIDATION_RESULTS.md), and [same-position sample 2](docs/reference/OVERLAPPING_FUEL_SAMPLE.md).

Fuel package name, author, revision and icon requirements are in the [metadata contract](docs/reference/MOD_METADATA.md). Use an explicit short map name and retain the experimental suffix. See [original icon proposals](assets/mod-icons/README.md).

For combined-map fuel work, read [connector findings and confirmed source priority](docs/reference/CONNECTOR_FUEL_FIXES.md). Preserve explicit dependency order. Each fuel fix belongs directly above its own source; source-relative installation and the effective data needed during generation are separate checks.

The user reports broad Canadian car-refueling access, with a separate invalid quantity/zero-price issue. Read the [country-price research](docs/reference/CANADA_FUEL_DISPLAY_RESEARCH.md) before changing economy data. Station target coverage does not establish finite petrol prices or correct billing; preserve source price provenance and distinguish static omissions from tested engine behavior.

The user authorizes missing petrol-price repair now with manual confirmation later. Follow [ADR-0007](docs/architecture/decisions/ADR-0007-repair-missing-petrol-prices.md), the [manual checklist](docs/reference/MANUAL_TEST_CHECKLIST.md), and [rest-area research](docs/reference/PASSENGER_CAR_REST_RESEARCH.md). Remind the user of pending game tests at subsequent package handoffs; do not label pricing/billing or rest behavior confirmed from static checks. No more manual tests are expected during this night's work.

The user selects independent `fuel`/`rest` processors and a local rest rule: add car eligibility when no original car rest is found within 1,000 game-world units in straight-line XZ distance. Shared rest actions must remain unchanged; use selected placement-local references to a private truck/bus/car action. Read [processor configuration and coverage limits](docs/reference/COMPATIBILITY_PROCESSORS.md) and [ADR-0008](docs/architecture/decisions/ADR-0008-compose-processors-and-local-rest-polygons.md). Courier generation remains reserved/unimplemented. The user accepts extra permissions from missed car neighbors beyond the inspected source-area/halo boundary; report that limit instead of requiring a full-world scan. Never silently overwrite one processor's sector edits with another's or claim a whole-world absence proof from bounded inspection.

## Task and evidence rules

Courier's current increment is [analysis/reporting only](docs/reference/COURIER_REPORTING.md), through `analyze-map --processor courier`; generation remains unsupported. Read [company marker evidence](docs/reference/COURIER_MARKER_RESEARCH.md) before interpreting company nodes or raw spawn flags. Resolve editor definitions by semantic company/city/prefab data, including DLC-suffixed filenames; do not assume `<city>.sii` is the only valid path. Distinguish generic check-in, load/delivery positions, context matches and runtime offers. This processor must not emit courier resources or invoke the mod writer in analysis mode. Read [availability research](docs/reference/COURIER_JOB_AVAILABILITY_RESEARCH.md) before interpreting low offer counts: the discovered-city dilution rule is unproven, and stock vehicle/rating definition counts are not live offers. Existing private prefab aliases can change context inputs: [TASK-0019](docs/tasks/backlog/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md) records the proven WCE r3 static gap and unverified runtime effect. Do not equate preserved Company bytes with preserved courier classification.

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
