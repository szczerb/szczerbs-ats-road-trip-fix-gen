# ATS Road Trip Map Compatibility Fix Generator

A project to investigate and eventually generate small compatibility mods that enable Road Trip Courier Jobs and passenger-car refueling in American Truck Simulator map expansions and reworks.

**Current milestone:** documentation and research preparation. No utility or fix mod exists yet, and neither reported problem has a confirmed cause. Courier Jobs and car refueling have equal research priority.

## Start here

- [Project brief](docs/project/PROJECT_BRIEF.md): intended users, goals, and boundaries.
- [Current state](docs/project/CURRENT_STATE.md): evidence, limitations, and next work.
- [Documentation index](docs/README.md): technical references and workflow guides.
- [Task board](docs/tasks/README.md): bounded research and implementation work.
- [Agent guide](AGENTS.md): instructions for contributors using agents.

## Local artifacts

`local_inputs/` contains supplied map mods and is immutable source material. `local_outputs/` is reserved for disposable extracted/reference data, reports, and future generated mods. Both directories are ignored by Git. The [input inventory](docs/reference/LOCAL_INPUT_INVENTORY.md) records metadata and representative internal paths without copying assets into the repository.

## Research before fixes

The [reference library](docs/README.md#technical-references) distinguishes official documentation, local observations, hypotheses, and unknowns. Missing courier markers and company-name prefixes are hypotheses to test. Refueling may involve a different mechanism. City-specific comparisons and in-game validation belong to later tasks.
