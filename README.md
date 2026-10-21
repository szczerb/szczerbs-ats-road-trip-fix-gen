# szczerb’s ATS Road Trip Fix Generator

A small personal project for making experimental **American Truck Simulator: Road Trip** fixes from your own game files and map mods. It started with passenger-car fuel stops and courier jobs, and now also covers rest areas and modest fuel-tank upgrades.

You can download the ready-to-use mods below or run the Python tools locally to generate your own `.scs` files. Game files, third-party map archives, generated packages and local research artifacts are excluded from the Git source history; downloadable builds are attached separately to GitHub Releases. Development is driven by the maintainer’s own setup and community feedback; compatibility is limited to the evidence below.

## Download ready-to-use experimental mods

The maintainer has published experimental builds on the [GitHub Releases page](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases):

- **[Reasonable gas tank upgrades — ATS 1.61 r0](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases/tag/reasonable-gas-tank-upgrades-1.61-r0-experimental)** — the separate Mustang/F-150 tank-capacity mod.
- **[Job Types Compat Mustang — ATS 1.61 r3](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases/tag/job-types-compat-mustang-1.61-r3-experimental)** — the separate courier job-eligibility mod.

Download the attached mod asset from the relevant release (`.scs`, or extract it from a supplied release ZIP), install the `.scs` in your ATS mod directory and enable it in Mod Manager. Read that release’s notes for the supported game version, DLC requirements and installation instructions. Python and the Extractor are only needed if you want to run the generators yourself; the downloadable mods are ready to use. GitHub’s automatic **Source code** archives contain the project sources.

These are experimental builds for community testing. The map/connector fixes described below remain available through local generation from your own source maps.

## What can it do?

| Tool | What it changes |
| --- | --- |
| **Map fuel/rest fixes** | Add passenger-car fuel interactions while retaining original truck interactions; enable car rest areas where the local proximity rule calls for them; repair missing petrol-price fields. |
| **Selective fuel PoC** | Opt-in reviewed pump-group suitability, explicit uncertainty and separate G1/G2 finite-site comparison. Broad behavior remains the default; this is not the completed realistic parking preset. [Policy and local test handoff](docs/reference/SELECTIVE_CAR_FUELING.md). |
| **Job Types Compat Mustang** | Add the `muscle` vehicle class to 58 reviewed cargo job definitions. Other muscle-tagged cars and Quick Jobs may also be affected; all nine vehicle-transfer definitions stay unchanged. |
| **Reasonable gas tank upgrades** | Change the Mustang from 61 to 76 L and the non-hybrid 5.0 V8 F-150 from 98 to 136 L. Crown Victoria and Bronco stay unchanged. Disable conflicting tank mods, including the old 3× override. |
| **Inspection and reports** | Inspect archives and report map-company/context data to investigate courier compatibility. General map courier generation remains unsupported. |

Fuel and rest are independently selectable. Rest uses a 1,000 game-world-unit straight-line XZ search within the inspected source sectors and a bounded neighboring area; existing geometry and shared actions are retained. [Processor behavior and limits](docs/reference/COMPATIBILITY_PROCESSORS.md).

## Game and map versions checked

**Research and generation baseline:** ATS **1.61.3.18** (existing game log: `1.61.3.18s`), Steam build **25952361**, with **Road Trip: Ford** and the installed map DLCs. The maintainer owns all DLCs; follow each source mod’s own DLC requirements. Tooling was exercised on **Linux/WSL with Python 3.12**. Python 3.11+ is required.

The following exact supplied sources were inspected, used for generation and checked structurally against that baseline. **This table records static/package verification; it does not claim every map or location was tested in game.**

| Map or connector | Source version | Source archive | Generated fix scope |
| --- | --- | --- | --- |
| ATS Expansion | **23.0** | `ATS_Expansion_v23.0_1.61.scs` | Fuel + rest |
| Reforma | **3.0.1.161** | `Reforma_3_0_1_161.scs` | Fuel + rest + missing petrol prices |
| ProMods Canada | **1.6.4** | `promods-ats-map-v164.scs` | Fuel + rest |
| Western Canada Expansion | **1.7.3** | `Western_Canada_Expansion_v1.7.3.scs` | Fuel + rest + missing petrol prices |
| Alaska Expansion | **1.2.3** | `Alaska_Expansion_v1.2.3.scs` | Fuel + rest + missing petrol prices |
| Western Canada ProMods Connections | **1.7.3** | `Western_Canada_Promods_Connections_v1.7.3.scs` | Connector-specific fuel + rest + missing petrol prices |
| Reforma OtherMaps Compatibility Patch | **40.161** | `Reforma_OtherMaps_Patch_40_161.scs` | Missing petrol prices only; this source has no station/rest sectors |

Reforma generation also uses **Mega Resources 3.0.1.161** (`Reforma_MegaResources_v3_0_1_161.scs`). ProMods uses its **1.6.4 assets, models and definitions** packages alongside the map. The Western Canada connector uses Western Canada Expansion 1.7.3 and the ProMods Canada 1.6.4 set. OtherMaps’ manifest says 40.161 while its description still says 39.161; the manifest and exact supplied archive identify the inspected input.

These Expansion names identify the specific sources above. They do not imply support for every map covering Alaska or western Canada. OtherMaps naming other maps in its description does not establish testing of those maps. Exact input metadata, dependencies and historical observations are in the [input inventory](docs/reference/LOCAL_INPUT_INVENTORY.md) and [research baseline](docs/reference/RESEARCH_BASELINE.md).

The latest local generated candidates are **map fixes r9**, **Job Types Compat Mustang r3** and **reasonable tank upgrades r0**. R9 gives selected car rest areas independent native parking triggers so the marker classifier can recognize them; the maintainer confirms parking icons in Alaska and Canada after checking two towns, with denser map coverage. Individual fatigue/truck/reload checks were not enumerated. Revision numbers identify generated packages, separately from source-map versions. Their [map handoff](docs/reference/MOD_REST_MARKERS_1_61_R9.md), [courier guide](docs/reference/PRACTICAL_COURIER_GENERATOR.md) and [tank guide](docs/reference/REASONABLE_GAS_TANK_UPGRADES.md) record the checks and local fingerprints. See GitHub Releases above for the published tank and job-compatibility downloads and their release-specific details.

## What has been tried in game?

**Maintainer-reported results, 17–19 October 2026:**

- The ATS Expansion Helena-area sample enabled car refueling at its selected target. The later same-position sample worked for both a truck and a car.
- Car refueling works in **Canada and Mexico** at the maintainer-reported scope. The earlier rest-success report is now qualified: the maintainer reports missing car-map parking icons in Canada/Alaska and sparse Montana coverage, without a physical rest check. [Rest/icon investigation and repair](docs/reference/CAR_PARKING_ICON_INVESTIGATION.md).
- **19 October 2026:** the maintainer confirms the **r9 parking-icon repair in Alaska and Canada**, after checks in two towns, and reports denser icon coverage on the map. [Dated result](docs/reference/VALIDATION_RESULTS.md#2026-10-19-r9-parking-icons-confirmed-in-alaska-and-canada).
- The reasonable tank-upgrade mod works and is accepted as internally complete.
- Job Types Compat Mustang testing in the USA is ongoing, with no problems noticed so far; completed newly eligible deliveries have not been reported.

Detailed fuel quantities/prices/billing, remaining truck/bus and reload controls, courier delivery and the connector’s Mod Manager icon retain their individual verification status. A valid package or a new map icon does not establish those gameplay results. [Dated gameplay evidence](docs/reference/VALIDATION_RESULTS.md) · [Remaining manual checks](docs/reference/MANUAL_TEST_CHECKLIST.md).

## Getting started

1. Obtain your own ATS/Road Trip installation and the source maps/resources you want to inspect. Keep the supplied map archives together under `local_inputs/`.
2. Use Python **3.11+** in Linux/WSL. The project has **no third-party runtime Python dependencies**.
3. Install the separate Linux x64 [sk-zk Extractor, release 2026-07-29](https://github.com/sk-zk/Extractor/releases/tag/2026-07-29) for HashFS archives. This includes installed game packages, even when the source map itself is ZIP. Place its executable at `local_outputs/tools/extractor-2026-07-29/extractor`, with executable permission, or pass `--extractor /path/to/extractor` before the subcommand. The executable is not bundled here.
4. Point the tool at your actual ATS installation using `--game-dir` or `ATS_GAME_DIR`.

Run commands from the repository root. Replace the game-directory placeholder with the path on your machine:

```bash
export ATS_GAME_DIR='/path/to/American Truck Simulator'

PYTHONPATH=src python3 -m ats_road_trip --help

# Generate a combined fuel/rest fix for one source map.
PYTHONPATH=src python3 -m ats_road_trip generate-map-fix \
  local_inputs/ATS_Expansion_v23.0_1.61.scs \
  --processor fuel --processor rest --experimental

# Inspect courier inputs without generating a map mod.
PYTHONPATH=src python3 -m ats_road_trip analyze-map \
  local_inputs/ATS_Expansion_v23.0_1.61.scs --processor courier

# Generate the separate source-pinned job-eligibility mod.
PYTHONPATH=src python3 -m ats_road_trip generate-courier-eligibility \
  --config docs/examples/mustang-practical-courier.toml --experimental

# Generate the separate source-pinned tank-upgrade mod.
PYTHONPATH=src python3 -m ats_road_trip generate-tank-upgrades \
  --config docs/examples/reasonable-gas-tank-upgrades.toml --experimental
```

Known source families resolve required companion archives beside the source. For a combined map setup, supply the relevant `--dependency` archives **from lowest to highest priority**, with the target source highest. Generation inputs and Mod Manager installation order are separate: the tool does not read or reconstruct your live profile. Follow the [map generation guide](docs/reference/MAP_WIDE_FUEL_GENERATOR.md), [processor guide](docs/reference/COMPATIBILITY_PROCESSORS.md) and [confirmed connector/dependency order](docs/reference/CONNECTOR_FUEL_FIXES.md) for the full setup.

Generation writes packages under `local_outputs/generated/<timestamp>/` and audits/staging under `local_outputs/work/<timestamp>/`. Both directories are ignored by Git. Unsafe or unsupported inputs stop generation; source/version drift requires re-review, especially for the exact-hash job and tank presets. Reports and generated packages can record local source paths: review those separately before sharing them.

## Installing your generated fixes

- Use a copied/disposable test profile while checking a new setup. The tool writes outputs for manual installation and does not install mods, launch ATS or edit profiles.
- Put **each map fix directly above its own source mod** in Mod Manager, retaining the source mods’ relative order. Keep the appropriate connector fix with its connector source.
- Replace older copies of a fix instead of stacking revisions. Whole-sector overrides do not merge automatically; follow the documented generation dependencies and load order.
- Install the job and tank packages separately as described in their guides. A job-class change does not guarantee a live offer or a successful delivery.

## Tests, feedback and research

Run the authored test suite:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

For useful feedback, include the ATS version, exact source-map and fix revisions, relevant load order, location and observed behavior. Review logs and reports for personal paths before posting them. Do not attach paid game/DLC or map files.

[Command reference](docs/reference/TOOLING.md) · [Current state](docs/project/CURRENT_STATE.md) · [Documentation index](docs/README.md) · [Task board](docs/tasks/README.md)

## License and provenance

Copyright (C) 2026 szczerb. Project-authored materials use **AGPL-3.0-only**: [LICENSE](LICENSE), [scope and contribution terms](LICENSING.md). This is an unofficial personal project; third-party names and artwork subjects do not imply endorsement.

The parsers were informed by format research including TruckLib C# sources. [Third-party notices](THIRD_PARTY_NOTICES.md) and the [implementation assessment](docs/reference/IMPLEMENTATION_INDEPENDENCE_ASSESSMENT.md) preserve the sources and review limits. Game/DLC files, map mods and generated resources retain separate rights; the project license does not itself authorize redistribution of those resources. See the [source publication re-audit](docs/reference/PUBLIC_SOURCE_REAUDIT_2026_10_18.md) and the separate [generated-mod publication research](docs/reference/SCS_MOD_PUBLICATION_TERMS.md).
