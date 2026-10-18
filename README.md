# ATS Road Trip Map Compatibility Fix Generator

A research utility for American Truck Simulator: inspect map archives, report Road Trip courier inputs, generate passenger-car fuel/rest map fixes, and separately broaden reviewed courier job eligibility.

A separate [reasonable gas tank upgrades mod](docs/reference/REASONABLE_GAS_TANK_UPGRADES.md) now selects researched Mustang (61 → 76 L) and F-150 (98 → 136 L) capacities; Crown Victoria and Bronco remain stock. The user confirmed it works and accepts it as internally complete; community testing may follow. Disable the old 3x-capacity mod when using it.

**Current implementation:** selectable `fuel` and `rest` map processors, automatic missing petrol-price repair, and preservation of original prefab context classifications when cloning. A separate [Job Types Compat Mustang generator](docs/reference/PRACTICAL_COURIER_GENERATOR.md) enables 58 reviewed cargo definitions for muscle-tagged cars, preserving all vehicle-transfer jobs. The [r8 map / r3 courier handoff](docs/reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md) uses the exact names Alaska Expansion and Western Canada Expansion for their source-specific fixes. The [r7/r3](docs/reference/MOD_METADATA_RENAME_1_61_R7_R3.md) and older batches remain historical. [Current state](docs/project/CURRENT_STATE.md) tracks verification and manual tests.

Rest uses the user-selected 1,000 game-world-unit XZ proximity rule and a bounded source-sector/halo search. Original truck interactions, parking geometry and shared actions are preserved. [Courier map reporting](docs/reference/COURIER_REPORTING.md) remains read-only; general map courier generation is unsupported. Definition eligibility does not guarantee live offers or completed deliveries. The user confirms refueling and rest work in Canada and Mexico. Detailed price/billing controls and courier delivery retain their [validation status](docs/reference/MANUAL_TEST_CHECKLIST.md).

## Findings and first experiments

- Courier jobs select prefab context tags, not merely company-name prefixes. Most sampled ZIP-map company definitions are already classified; some omissions are intentional SCS exclusions. Reforma's `ahorrara` alias reuses an official supermarket model/descriptor but lacks its `retail` tag: [courier findings](docs/reference/COURIER_RESEARCH_FINDINGS.md).
- Official Road Trip gas-station descriptors consistently contain a GAS locator flag missing from selected Reforma stations. A v25 descriptor experiment adds that locator while preserving the truck record; separately serialized map services may also need rebuilding: [refueling findings](docs/reference/REFUELING_RESEARCH_FINDINGS.md).
- Neither experiment is a verified gameplay repair. See the [validation handoff](docs/reference/VALIDATION_HANDOFF.md) for generated artifacts, evidence, limits, and copied-profile testing.

[Helena-area and Great Falls samples](docs/reference/STARTER_AREA_SAMPLE.md) target individual ATS Expansion fuel interactions. Helena retains a standard garage class. The [first user test](docs/reference/VALIDATION_RESULTS.md) reports successful refueling at the eastern target and a substantial driving detour; the closer city station remains unchanged.

The historical [sample 2](docs/reference/OVERLAPPING_FUEL_SAMPLE.md) retains the original truck interaction and adds a car interaction at exactly the same position/rotation. The user reports successful refueling in both modes for this fixture. Disable sample 1 when testing it. Fuel packages now use [consistent branding, game-based revision versions and original icons](docs/reference/MOD_METADATA.md); this title does not imply map-wide coverage.

## Run the tooling

Requires Python 3.11+; ZIP inspection has no third-party Python dependencies. HashFS uses a separately installed external extractor.

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/ATS_Expansion_v23.0_1.61.scs --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-map-fix local_inputs/Western_Canada_Expansion_v1.7.3.scs --processor fuel --processor rest --rest-radius 1000 --experimental
PYTHONPATH=src python3 -m ats_road_trip analyze-map local_inputs/ATS_Expansion_v23.0_1.61.scs --processor courier
PYTHONPATH=src python3 -m ats_road_trip generate-courier-eligibility --config docs/examples/mustang-practical-courier.toml --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-tank-upgrades --config docs/examples/reasonable-gas-tank-upgrades.toml --experimental
PYTHONPATH=src python3 -m ats_road_trip --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The [tooling guide](docs/reference/TOOLING.md) documents archive inspection/extraction, explicit package order and mounts, context audits, dependencies, and experimental generation. The [map-wide guide](docs/reference/MAP_WIDE_FUEL_GENERATOR.md) documents automatic companions, timestamped work/output directories and required source-relative load priority. Combined map packages now default to r8 with shorter `szczerbs-road-trip-map-fix-...` filenames; Job Types Compat Mustang remains r3 and the legacy fuel command remains r2. Outputs contain a manifest, icon, player description and provenance/change report; they are not automatically installed.

## Publication status

Research covers [SCS definition-mod sharing](docs/reference/SCS_MOD_PUBLICATION_TERMS.md), [tracked files and Git history](docs/reference/PUBLIC_REPOSITORY_REVIEW.md), and [open-source license options](docs/reference/OPEN_SOURCE_LICENSE_RECOMMENDATION.md). A root license has not been selected. The [deeper source assessment](docs/reference/IMPLEMENTATION_INDEPENDENCE_ASSESSMENT.md) and [maintainer license comparison](docs/reference/MAINTAINER_LICENSE_CHOICES.md) now inform that decision; [public Git identity notes](docs/reference/PUBLIC_GIT_IDENTITY_PRACTICES.md) explain the intentional alias/placeholder. Public source release and generated game/map-resource distribution have separate terms; the tool license cannot grant rights to those source-owned resources.

## Project navigation

- [Current state](docs/project/CURRENT_STATE.md) and [task board](docs/tasks/README.md).
- [Project brief](docs/project/PROJECT_BRIEF.md) and [architecture decisions](docs/architecture/decisions/README.md).
- [Documentation index](docs/README.md), [agent guide](AGENTS.md), and [third-party notices](THIRD_PARTY_NOTICES.md).

## Local artifacts and Git

`local_inputs/` contains immutable supplied map mods. `local_outputs/` holds ignored extracted/reference data, reports, tools, and generated experiments; the [inventory](docs/reference/LOCAL_INPUT_INVENTORY.md) and [baseline](docs/reference/RESEARCH_BASELINE.md) record provenance without committing source assets.

Verified milestones are committed locally. This single-contributor project has no remote; no push or remote setup is part of the workflow. Use branches for experiments and master for integrated verified work, as described in [working agreements](docs/project/WORKING_AGREEMENTS.md).
