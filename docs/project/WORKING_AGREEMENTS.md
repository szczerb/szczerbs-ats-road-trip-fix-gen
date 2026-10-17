# Working Agreements

## Documentation and evidence

Write all workspace-authored documentation in English. Keep root documents navigational, stable evidence in references, current work in tasks, durable decisions in ADRs, and reproducible failure evidence in incidents. Update current state whenever findings or priorities change.

Use these labels for substantive technical findings:

| Label | Meaning and required evidence |
| --- | --- |
| **Documented** | Supported by a linked primary source; record applicable game/tool version and inspection date. |
| **Observed locally** | Seen in a named archive/file or experiment; record source path, version when available, date, and method. |
| **Hypothesis** | A possible explanation, its origin, and the comparison or experiment that could test it. |
| **Unknown** | Evidence is missing or insufficient; state what must be collected next. |

Treat old wiki pages as evidence for the described behavior, not proof of the complete ATS 1.61/Road Trip schema. Distinguish shared ATS/ETS2 engine concepts from ATS-specific behavior. Metadata declarations are not tested compatibility, and static file observations are not in-game validation. User reports must be attributed as reports; do not relabel them as reproduced local observations.

## Tasks and decisions

Follow the [task/ADR workflow](HOW_TO_WORK_WITH_TASKS_AND_ADRS.md) and templates. Use `backlog`, `active`, and `done` statuses only; keep location synchronized. Record dependencies, blockers, uncertainty, acceptance criteria, and actual verification. Keep Courier Job and refueling research at equal priority unless the user changes direction.

## Delegation and cost

Delegate independent bounded work using explicit file ownership in shared checkouts. Select an economical model and effort for routine inventory/documentation; use a stronger model where technical uncertainty or integration warrants it. Review delegated claims, source quality, and links. Every Plan Mode plan must contain a task/model/effort breakdown; distinguish work already performed from proposed assignments. Record actual contributors and material checks in the task.

## Artifacts and experiments

Treat input archives as immutable. Keep local artifacts under the existing ignored input/output directories and preserve their exclusions. Use selective metadata/text reads before considering full extraction. Keep large logs, game/mod assets, downloaded tools, and generated packages out of tracked docs. See [workspace structure](../reference/WORKSPACE_STRUCTURE.md).

Future in-game experiments must use a disposable or copied profile and record exact build, DLCs, mod versions, load order, observation method, and logs. Do not prescribe a market reset or modify a live save without establishing its effects and the experiment's authorization. Initialization performs no in-game experiments.

## Commits

The user authorizes routine local commits at coherent, verified milestones. There is one contributor and no remote; do not add one or push. Small documentation changes and stable work can go directly on `master`. Isolate substantial/experimental tooling in `codex/` branches; use worktrees when parallel edits need independent checkouts. Merge verified milestones locally and report any experiments retained on branches. Use existing immutable inputs by absolute path when working from another checkout.

Use a meaningful concise subject and a body for non-trivial changes. Broad, checkpoint, architectural, and first-project commits must explain major areas changed, purpose, relevant user feedback/caveats/direction, and verification. Avoid vague subjects whose meaning requires opening the diff. The canonical instructions are in [AGENTS.md](../../AGENTS.md#commit-messages).
