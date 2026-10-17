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

Both local directories are ignored by Git. Preserve those exclusions.

- `local_inputs/`: supplied original map archives and adjacent metadata. Treat this directory as read-only. Do not extract into it, rename files, remove sidecars, or perform automatic metadata cleanup. Preserve untrusted sidecars with their inputs unless the user explicitly requests a change. On 2026-10-17 the user requested two `:Zone.Identifier` sidecars be moved to the current run's `input-sidecars/`; the `.scs` archives were unchanged.
- `local_outputs/work/<YYYY-MM-DD_HH-MM-SS>/`: per-run scratch, extracted samples, reports, temporary archive staging, and input-sidecar storage when expressly requested. Build the timestamp in Europe/Warsaw local time. Keep each run's work together and retain it unless cleanup is explicitly requested.
- `local_outputs/generated/<YYYY-MM-DD_HH-MM-SS>/`: generated mod packages from that run. Use human-readable filenames that identify the map and ATS/map version, such as `ats-expansion-ats-1.61-map-23.0-experimental.scs`.
- Other existing `local_outputs/` directories such as `extracted/`, `reports/`, `tools/`, and `generated/` may contain historical artifacts. Do not move or delete them automatically; use the current timestamped run directories for new work.

Keep game/DLC data, extracted mod assets, downloaded tools, large logs/reports, scratch, and generated mods out of tracked docs. Summarize findings in references or tasks with original internal paths and exact versions when known. Do not use a documentation link to require an ignored artifact that another checkout will not have; explain how to obtain or reproduce evidence.

## Prototype code

- `src/ats_road_trip/`: archive adapter, virtual packages, read-only SII analysis, courier audit, PPD experiment, deterministic mod writer, and CLI.
- `tests/`: synthetic unit/integration tests; no copied game/mod assets.
- `pyproject.toml`: Python 3.11+ metadata and optional installed CLI entrypoint.
- `THIRD_PARTY_NOTICES.md`: external tool and format-research attribution.

Python caches, virtual environments, and build outputs are ignored in addition to the original artifact exclusions. Runtime/public interfaces and supported experimental boundaries are described in [tool usage](TOOLING.md) and [ADR-0002](../architecture/decisions/ADR-0002-use-python-inspection-and-bounded-experimental-patches.md).
