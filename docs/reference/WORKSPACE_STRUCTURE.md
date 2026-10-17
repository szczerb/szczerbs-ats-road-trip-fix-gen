# Workspace Structure

## Tracked entrypoints and documentation

| Location | Purpose |
| --- | --- |
| `README.md` | Short human entrypoint and milestone boundary |
| `AGENTS.md` | Canonical agent instructions and reading order |
| `docs/project/` | Intent, current state, working agreements, task/ADR workflow |
| `docs/tasks/backlog/`, `active/`, `done/` | Bounded work, with directory/status agreement |
| `docs/architecture/` | Prospective system overview and durable decisions |
| `docs/incidents/` | Separate evidence trails for reproducible failures |
| `docs/reference/` | Sourced technical references and small authored inventories |
| `docs/templates/` | Task, ADR, and incident templates |
| `.gitignore` | Existing exclusions for local input/output artifacts |

## Local artifacts

Both existing local directories are ignored by Git. Preserve these exclusions.

- `local_inputs/`: original supplied map archives; treat as immutable. Add future original reference inputs here with provenance recorded in a task.
- `local_outputs/`: disposable derived/reference artifacts and future outputs. Use named subdirectories such as `extracted/`, `game-reference/`, `tools/`, `reports/`, and `generated/` when needed; initialization does not create or populate them.

Keep game/DLC data, extracted mod assets, downloaded tools, large logs/reports, and generated mods out of tracked docs. Summarize findings in references or tasks with original internal paths and exact versions when known. Do not use a documentation link to require an ignored artifact that another checkout will not have; explain how to obtain/reproduce evidence.

## Future product code

No source/test package, runtime, CLI, or artifact schema has been selected. Create those locations only after the [first increment design](../tasks/backlog/TASK-0005-design-first-generator-increment.md) establishes a supported approach.
