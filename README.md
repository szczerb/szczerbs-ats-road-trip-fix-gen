# ATS Road Trip Map Compatibility Fix Generator

A research utility for American Truck Simulator map expansions and reworks: inspect archives, audit Road Trip courier context coverage, and generate bounded experimental compatibility mods for courier locations and passenger-car refueling.

**Current result:** working Python CLI, sourced research for both issues, and generated experimental `.scs` packages. Static tests pass; the user reports successful car and truck refueling at the same Helena-area pump with overlapping sample 2. Broader station, reload and courier validation remain open. Courier and refueling investigations have equal priority.

## Findings and first experiments

- Courier jobs select prefab context tags, not merely company-name prefixes. Most sampled ZIP-map company definitions are already classified; some omissions are intentional SCS exclusions. Reforma's `ahorrara` alias reuses an official supermarket model/descriptor but lacks its `retail` tag: [courier findings](docs/reference/COURIER_RESEARCH_FINDINGS.md).
- Official Road Trip gas-station descriptors consistently contain a GAS locator flag missing from selected Reforma stations. A v25 descriptor experiment adds that locator while preserving the truck record; separately serialized map services may also need rebuilding: [refueling findings](docs/reference/REFUELING_RESEARCH_FINDINGS.md).
- Neither experiment is a verified gameplay repair. See the [validation handoff](docs/reference/VALIDATION_HANDOFF.md) for generated artifacts, evidence, limits, and copied-profile testing.

[Helena-area and Great Falls samples](docs/reference/STARTER_AREA_SAMPLE.md) target individual ATS Expansion fuel interactions. Helena retains a standard garage class. The [first user test](docs/reference/VALIDATION_RESULTS.md) reports successful refueling at the eastern target and a substantial driving detour; the closer city station remains unchanged.

The new [sample 2](docs/reference/OVERLAPPING_FUEL_SAMPLE.md) retains the original truck interaction and adds a car interaction at exactly the same position/rotation. The user reports successful refueling in both modes for this fixture. Disable sample 1 when testing it. Fuel packages now use [consistent branding, game-based revision versions and original icons](docs/reference/MOD_METADATA.md); this title does not imply map-wide coverage.

## Run the tooling

Requires Python 3.11+; ZIP inspection has no third-party Python dependencies. HashFS uses a separately installed external extractor.

```bash
PYTHONPATH=src python3 -m ats_road_trip --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The [tooling guide](docs/reference/TOOLING.md) documents archive inspection/extraction, explicit package order and mounts, context audits, dependencies, and experimental generation. Outputs contain a manifest and provenance/change report; they are not automatically installed.

## Project navigation

- [Current state](docs/project/CURRENT_STATE.md) and [task board](docs/tasks/README.md).
- [Project brief](docs/project/PROJECT_BRIEF.md) and [architecture decisions](docs/architecture/decisions/README.md).
- [Documentation index](docs/README.md), [agent guide](AGENTS.md), and [third-party notices](THIRD_PARTY_NOTICES.md).

## Local artifacts and Git

`local_inputs/` contains immutable supplied map mods. `local_outputs/` holds ignored extracted/reference data, reports, tools, and generated experiments; the [inventory](docs/reference/LOCAL_INPUT_INVENTORY.md) and [baseline](docs/reference/RESEARCH_BASELINE.md) record provenance without committing source assets.

Verified milestones are committed locally. This single-contributor project has no remote; no push or remote setup is part of the workflow. Use branches for experiments and master for integrated verified work, as described in [working agreements](docs/project/WORKING_AGREEMENTS.md).
