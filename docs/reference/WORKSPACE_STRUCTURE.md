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
| `assets/mod-icons/` | Small original icon JPEG exports and exact generation prompts; selected design C |
| `.gitignore` | Existing exclusions for local input/output artifacts |

## Local artifacts

Both existing local directories are ignored by Git. Preserve these exclusions.

- `local_inputs/`: original supplied map archives; treat as immutable. Add future original reference inputs here with provenance recorded in a task.
- `local_outputs/`: disposable derived/reference artifacts and future outputs. Use named subdirectories such as `extracted/`, `game-reference/`, `tools/`, `reports/`, and `generated/` when needed; initialization does not create or populate them.

Keep game/DLC data, extracted mod assets, downloaded tools, large logs/reports, and generated mods out of tracked docs. Summarize findings in references or tasks with original internal paths and exact versions when known. Do not use a documentation link to require an ignored artifact that another checkout will not have; explain how to obtain/reproduce evidence.

## Prototype code

- `src/ats_road_trip/`: archive adapter, virtual packages, read-only SII analysis, courier audit, PPD experiment, deterministic mod writer, and CLI.
- `tests/`: synthetic unit/integration tests; no copied game/mod assets.
- `pyproject.toml`: Python 3.11+ metadata and optional installed CLI entrypoint.
- `THIRD_PARTY_NOTICES.md`: external tool and format-research attribution.

Python caches, virtual environments, and build outputs are ignored in addition to the original artifact exclusions. Runtime/public interfaces and supported experimental boundaries are described in [tool usage](TOOLING.md) and [ADR-0002](../architecture/decisions/ADR-0002-use-python-inspection-and-bounded-experimental-patches.md).
