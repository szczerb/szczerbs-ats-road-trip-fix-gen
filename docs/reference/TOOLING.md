# Inspection and experimental generation CLI

Tested on 2026-10-17 in Linux/WSL with Python 3.12 against ATS 1.61.3.18 and the supplied inputs. Requires Python 3.11+. There are no runtime Python dependencies. From the repository root:

```bash
PYTHONPATH=src python3 -m ats_road_trip --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

`pyproject.toml` also defines the `ats-road-trip` entrypoint for environments that install the package. The source-tree invocation above is the tested path and avoids a package-install step.

## HashFS dependency

ZIP uses Python's standard library. HashFS uses the separate Linux x64 [sk-zk Extractor release 2026-07-29](https://github.com/sk-zk/Extractor/releases/tag/2026-07-29). Download its Linux x64 ZIP from that release, inspect the provenance, and place its executable at `local_outputs/tools/extractor-2026-07-29/extractor` with executable permissions. It is already present in this local workspace. Alternatively pass `--extractor /path/to/extractor` **before** the subcommand. Source/terms and observed hashes are in [the baseline](RESEARCH_BASELINE.md) and [notices](../../THIRD_PARTY_NOTICES.md).

The adapter lists HashFS metadata and extracts selected members through a subprocess. It does not implement HashFS itself. HashFS file sizes are unavailable through its listing adapter; per-member limits are checked after extraction into temporary ignored staging. This is not a pre-decompression disk quota. Header detection recognizes v1/v2, but live tests in this project covered v2. Directory packages need no extractor.

## Inspect and extract

```bash
PYTHONPATH=src python3 -m ats_road_trip inspect local_inputs/Alaska_Expansion_v1.2.3.scs --prefix def/company/ --output local_outputs/reports/alaska-inventory.json
PYTHONPATH=src python3 -m ats_road_trip extract local_inputs/Alaska_Expansion_v1.2.3.scs --path manifest.sii --output local_outputs/extracted/alaska-example
```

`inspect` writes JSON: detected format, total entry count, and selected physical member paths/sizes/directory flags. HashFS sizes may be null. `extract` requires explicit `--path` selections or `--prefix`; it does not implicitly extract a whole archive. Default limit is 16 MiB per member, configurable with `--max-bytes`. Existing destination members and report files are refused, and archive traversal/symlink members are rejected. Choose a fresh output directory for a new extraction. Source archives are never rewritten.

For a fresh official definition snapshot, substitute the installation path appropriate to the machine:

```bash
ATS_GAME='/mnt/c/Program Files (x86)/Steam/steamapps/common/American Truck Simulator'
PYTHONPATH=src python3 -m ats_road_trip extract "$ATS_GAME/def.scs" --prefix def/ --output local_outputs/extracted/reference-def
```

Selection is batched to keep subprocess arguments bounded. Re-extract after source updates; snapshots are not automatically freshness-checked against a live installation.

## Virtual packages and courier coverage

The newer [source-relative courier report](COURIER_REPORTING.md) uses `analyze-map SOURCE --processor courier` and inspects placed companies, nodes and descriptors as well as definitions. It does not require `--experimental` or create a mod. The older command below retains its narrower definition/context scope.

```bash
PYTHONPATH=src python3 -m ats_road_trip courier-audit --baseline local_outputs/extracted/game-def --map local_inputs/ATS_Expansion_v23.0_1.61.scs --map local_inputs/Alaska_Expansion_v1.2.3.scs --map local_inputs/Western_Canada_Expansion_v1.7.3.scs --output local_outputs/reports/courier-coverage.json
```

Repeated baseline packages are loaded first, followed by maps in the supplied order, **lowest priority first**. This is explicit research order, not an automatic reconstruction of the player's profile. Root assets and directory `base/` parts are supported; `dlc_<name>/` parts require the corresponding `--dlc dlc_<name>`. Nested conditional part ZIPs and within-package mounted-path collisions fail with a clear error rather than guessed precedence. Only selected map-owned company editor definitions are counted. HashFS text definitions are prefetched in batches; ZIP handles and metadata are cached.

The report distinguishes classified, explicitly excluded, and unclassified definition occurrences, with source paths, tags, matching job-definition IDs, and replaced virtual paths. It does **not** predict actual market offers. The reader handles comments, strings, compact attributes, includes with cycle/escape checks, and indexed/append arrays. It is not a complete engine serializer; ambiguous unused attributes are preserved as errors, and accessing one fails rather than inventing a value.

## Courier alias experiment

The conservative rule requires a map-used, unclassified prefab to reuse the same model and descriptor paths as an unambiguously classified baseline prefab. Referenced assets must be available in the declared stack, canonical definitions unchanged, and map overrides/exclusions absent. Path/asset provenance and fingerprints are recorded. This does not validate placed map objects.

The prepared `game-def` snapshot contains official definitions. The `courier-assets` snapshot contains eight original model/descriptor members, selected from `base.scs` for the independently identified candidate pairs. A complete alternative is to pass the original `base.scs` as another baseline, allowing its member inventory to supply those paths without extracting the whole archive.

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-context --baseline local_outputs/extracted/game-def --baseline local_outputs/extracted/courier-assets --map local_inputs/Reforma_MegaResources_v3_0_1_161.scs --map local_inputs/Reforma_3_0_1_161.scs --prefab ahorrara --output local_outputs/generated/ahorrara-example.scs --game-version 1.61.3.18 --experimental
```

`--prefab` restricts output to reviewed aliases and can be repeated; omitting it generates every alias satisfying the conservative rule for the supplied stack. This run found 15 qualifying aliases across 33 effective company-definition occurrences; the narrow Ahorrara example covers eight. Multi-tag ambiguity, missing assets, exclusions, and overrides are reported as skipped rather than broadened heuristically.

Only `def/data_context.rtfix.sii` is emitted as a gameplay resource. No company rename, sector edit, or baseline context/asset copy is included. A pre-existing input `data_context.rtfix.sii` or generated unit-name collision is refused. Do not stack multiple outputs using this same additive file path; choose one experiment at a time. The [courier findings](COURIER_RESEARCH_FINDINGS.md) explain evidence and remaining placement/market uncertainty.

## Fuel descriptor experiment

```bash
PYTHONPATH=src python3 -m ats_road_trip fuel-audit --package local_inputs/Reforma_MegaResources_v3_0_1_161.scs --path /prefab_mvs/gas/MVS_pemex_small.ppd --output local_outputs/reports/mx9-fuel.json
PYTHONPATH=src python3 -m ats_road_trip generate-fuel --package local_inputs/Reforma_MegaResources_v3_0_1_161.scs --path /prefab_mvs/gas/MVS_pemex_small.ppd --output local_outputs/generated/mx9-example.scs --game-version 1.61.3.18 --map-name Reforma --experimental
```

Repeated `--package` has the same low-to-high semantics. Select exact `--path` values or a `--prefix` to inspect PPDs below it. Leading `/` is accepted for virtual resource selectors; output paths remain filesystem paths. Inspection supports PPD versions 23–25. Generation supports v25 only, refuses unknown GAS flags, and duplicates flags-0 GAS records at the same transform with flags 1 while preserving originals and opaque sections. Already matching flags-1 transforms are skipped; repeating the transformation changes nothing.

This is an experiment: co-located locators, physical car access, fuel behavior, and map-service/spawn rebuilding are untested. It is not a generic map-sector repair. See [refueling findings](REFUELING_RESEARCH_FINDINGS.md).

## Pinned single-pump map experiment

`generate-local-fuel` accepts repeated `--baseline` packages, one `--map`, a reviewed `--recipe` JSON, `--output`, exact `--game-version 1.61.3.18`, required `--map-name 'ATS Expansion'` for the supplied recipe, and `--experimental`. The [starter-area guide](STARTER_AREA_SAMPLE.md#reproduce-generation) provides the complete command and authored Helena-area/Great Falls recipes. It requires exact source hashes, a supported single-GAS stock configuration, matching prefab/service identities, and no generated collisions. It emits a private prefab alias, same-size descriptor with one locator flag changed, and a same-size sector with the selected model token/service bit changed.

Unlike the descriptor-only experiment, this converts **one existing pump**; truck use at that pump may disappear. Nearby pumps retain their original data. A full sector override conflicts with other edits to that sector/companions. The service-bit interpretation, starting-city eligibility, and gameplay remain unverified. This is not general sector serialization or automatic fix discovery. See [ADR-0003](../architecture/decisions/ADR-0003-allow-pinned-single-pump-sector-experiments.md).

## Same-position truck/car pair

`generate-overlap-fuel` uses the same baseline/map/output/version/metadata/experimental arguments as `generate-local-fuel`, but requires a reviewed schema-2 recipe including source companion fingerprints and explicit node-table layout. See the [sample-2 guide](OVERLAPPING_FUEL_SAMPLE.md#reproduce) for the tested command. It retains the original truck records and adds a same-transform car locator, linked service and node, updates counted references/tables, and uses a distinct private prefab alias.

The reviewed fixture is map 907, stock `02003`, one original GAS/service, a local UID-sorted 56-byte node table, no visibility children and an empty layer. Unsupported layouts/companions, source changes or UID collisions fail. The description identifies sample 2; the mod manager name uses the supplied map name. Disable sample 1 before testing. A full-sector override and overlapping runtime interactions still need broader game comparison; this command does not generally serialize sectors or certify dual-vehicle support.

## Generated output contract

All generators require `--experimental` and a declared ATS 1.61 `--game-version`. Fuel generators additionally require a short `--map-name`, such as `ATS Expansion` or `Reforma`. Their manifest display name is `szczerb's Road Trip Gas Stations Fix for <map-name>`, the author is `szczerb`, and the package version is `1.61-r0-experimental` by default. Use `--revision N` for a new nonnegative revision, or `--icon /path/to/icon.jpg` for an optional 276x162 JPEG mod manager icon. These CLI metadata flags do not apply to `generate-context`; the shared writer still uses author `szczerb` and the game-based experimental version for that command, retaining its generic compatibility title. The user-selected ATS Expansion [icon C](../../assets/mod-icons/ats-expansion-c.jpg) can be supplied as `--icon assets/mod-icons/ats-expansion-c.jpg`. See the [metadata contract](MOD_METADATA.md). Generators refuse empty changes and existing outputs. The deterministic ZIP_STORED `.scs` contains generated/changed resources, `manifest.sii`, `mod_description.txt`, and `road_trip_fix_report.json` (plus `mod_icon.jpg` when supplied). The report carries the planner's schema version (currently 1 or 2), package metadata/icon fingerprint, provenance, transformations, limitations, generated resource hashes, and `in_game_verified: false`. These are prototype interfaces; they do not certify complete game compatibility. Errors exit with status 2.

Nothing is installed in the game or mod directory. Generated fuel descriptors contain modified source asset bytes and remain ignored local artifacts. Follow the [validation handoff](VALIDATION_HANDOFF.md) before treating any candidate as a working fix.

## Full source-map fuel generation

`PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/ATS_Expansion_v23.0_1.61.scs --experimental` discovers and patches complete supported fuel coverage without a per-station recipe. See the [map-wide guide](MAP_WIDE_FUEL_GENERATOR.md) for all five commands, automatic companion packages, timestamped audit/output paths, failure behavior, icons and required source-relative load order. The historical pinned commands above retain their narrower semantics.

## Standalone job eligibility

The [Practical Courier Jobs generator](PRACTICAL_COURIER_GENERATOR.md) is separate from map processors. `analyze-courier-eligibility --config PATH` writes a report only; `generate-courier-eligibility --config PATH --experimental` packages reviewed class-list additions after exact source/version/inventory checks. The preset enables 58 cargo units, disables 30 ambiguous candidates and preserves all nine vehicle transfers. No game/profile installation occurs. General map `courier` generation remains unsupported.

## Separate reasonable tank upgrades

Use `analyze-tank-upgrades --config docs/examples/reasonable-gas-tank-upgrades.toml` for a report, or `generate-tank-upgrades --config docs/examples/reasonable-gas-tank-upgrades.toml --experimental` for a standalone capacity mod. Both run under `PYTHONPATH=src python3 -m ats_road_trip`. [Automotive evidence, exact model policy, priority and manual checks](REASONABLE_GAS_TANK_UPGRADES.md). The default r0 changes only Mustang/F-150 capacities; it does not regenerate map or courier fixes.
