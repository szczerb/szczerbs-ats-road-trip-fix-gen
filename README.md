# ATS Road Trip Map Compatibility Fix Generator

A research utility for American Truck Simulator map expansions and reworks: inspect archives, audit Road Trip courier context coverage, and generate bounded experimental compatibility mods for courier locations and passenger-car refueling.

**Current result:** [courier analysis/reporting](docs/reference/COURIER_REPORTING.md) now resolves placed companies, generic check-in nodes, separate loading/spawn arrays, semantic company definitions and actual prefab context inputs without writing a mod. Static evidence supports shared company check-in; mode-specific runtime activation remains unverified. The [selectable compatibility processors](docs/reference/COMPATIBILITY_PROCESSORS.md) separate `fuel` and `rest` analysis/generation. Rest adds car eligibility locally when no original car rest is found within 1,000 game-world units in straight-line XZ distance; private actions retain truck/bus support and parking geometry. Search is bounded to the source area and nearby sectors; the user accepts extra additions from missed neighbors at that boundary. Both processors compose their changes before packaging, and unsafe source edits block output. Courier generation remains explicitly unimplemented. All **194 tests pass**; an independently verified WCE r3 package includes 202 rest additions plus existing fuel/price fixes. Actual rest behavior still needs manual validation. A later [WCE r3 audit](docs/reference/COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk) found 14 company-linked aliases without their originals' context tags; the runtime effect is unknown and preservation is tracked separately.

The existing [r2 fuel/price batch](docs/reference/FUEL_FIX_BATCH_1_61_R2.md) contains seven packages, adding an OtherMaps price-only fix while retaining the six r1 station payloads. Positive petrol prices are restored from lower same-unit sources or estimated using a documented stock-game ratio; diesel and other country fields are preserved. The user reports working Canadian car refueling; the price/quantity/billing repair still needs [manual tests](docs/reference/MANUAL_TEST_CHECKLIST.md). Those r2 artifacts contain no rest changes.

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
PYTHONPATH=src python3 -m ats_road_trip --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The [tooling guide](docs/reference/TOOLING.md) documents archive inspection/extraction, explicit package order and mounts, context audits, dependencies, and experimental generation. The [map-wide guide](docs/reference/MAP_WIDE_FUEL_GENERATOR.md) documents automatic companions, timestamped work/output directories and required source-relative load priority. Outputs contain a manifest, map-labelled icon and provenance/change report; they are not automatically installed.

## Project navigation

- [Current state](docs/project/CURRENT_STATE.md) and [task board](docs/tasks/README.md).
- [Project brief](docs/project/PROJECT_BRIEF.md) and [architecture decisions](docs/architecture/decisions/README.md).
- [Documentation index](docs/README.md), [agent guide](AGENTS.md), and [third-party notices](THIRD_PARTY_NOTICES.md).

## Local artifacts and Git

`local_inputs/` contains immutable supplied map mods. `local_outputs/` holds ignored extracted/reference data, reports, tools, and generated experiments; the [inventory](docs/reference/LOCAL_INPUT_INVENTORY.md) and [baseline](docs/reference/RESEARCH_BASELINE.md) record provenance without committing source assets.

Verified milestones are committed locally. This single-contributor project has no remote; no push or remote setup is part of the workflow. Use branches for experiments and master for integrated verified work, as described in [working agreements](docs/project/WORKING_AGREEMENTS.md).
