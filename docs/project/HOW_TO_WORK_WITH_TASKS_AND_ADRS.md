# How To Work With Tasks and ADRs

## Start a bounded task

1. Read the [project brief](PROJECT_BRIEF.md), [current state](CURRENT_STATE.md), and [task board](../tasks/README.md). Prefer an existing task over duplicating work.
2. Allocate the next unused `TASK-XXXX` number across all three status directories. Copy the [task template](../templates/TASK_TEMPLATE.md) to `docs/tasks/backlog/TASK-XXXX-<slug>.md`.
3. Fill every frontmatter field and required section. `repositories: [.]` identifies this repository; `depends_on` contains task IDs, not filenames. Use `owner: shared` until assigned.
4. Define an outcome, evidence to collect, acceptance criteria, and a verification method. Investigation completion may be a documented blocker and next evidence, where the task explicitly permits it; it must not imply that the defect is fixed.
5. Move to `active/` when work starts, change `status` to `active`, and assign an owner. Resolve dependencies first, or explicitly record why independent work is possible.

## Maintain status and evidence

Keep task status limited to `backlog`, `active`, or `done`. A blocked active task stays in `active/`; add a dated blocker, the missing evidence/action, and a next step. Do not create a fourth directory or silently mark blocked research complete.

During work, update the implementation plan when direction changes and record actual commands, observations, source versions, dates, and outcomes under Verification. Follow the [evidence labels](WORKING_AGREEMENTS.md#documentation-and-evidence). Record delegated assignments with model/effort and clear ownership. In Plan Mode, include the task/model breakdown in the plan itself.

When acceptance criteria are met and verification is recorded, move the task to `done/`, change its status, and update the task board, current state, and all affected links. Dependency IDs stay stable. Keep completed history; do not rewrite an investigation outcome as an implemented fix.

## Architecture decisions

Use an ADR for a durable choice affecting architecture, repository/workflow conventions, data flow, or interfaces. Allocate `ADR-XXXX-<slug>.md` in [decisions](../architecture/decisions/README.md) using the [template](../templates/ADR_TEMPLATE.md). Record context, decision, and consequences; link affected tasks and evidence. If superseded, create a new ADR and cross-link both rather than rewriting history.

Routine observations and temporary implementation details stay in tasks/references. Do not create an ADR selecting a language, CLI, or patch strategy before research supports the choice.

## Incidents

Create an [incident](../incidents/README.md) for a reproducible failure that needs a separate evidence trail. Use the [incident template](../templates/INCIDENT_TEMPLATE.md), link it from the active task, and keep large logs/assets in ignored output directories. Planned research without a reproduced failure remains in its task. Incident notes do not redefine product intent.
