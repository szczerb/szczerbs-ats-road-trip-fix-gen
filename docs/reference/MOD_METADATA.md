# Generated mod metadata

Updated: 2026-10-18. Applies to this prototype's ATS 1.61 map and Practical Courier Jobs packages. [ADR-0005](../architecture/decisions/ADR-0005-standardize-fuel-package-metadata.md) records the original fuel policy; [ADR-0013](../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md) covers topic-specific artwork and player descriptions. The [r6/r1 handoff](MOD_METADATA_REFRESH_1_61_R6.md) records the current bundle and package comparison; the [r5/r1 refresh](MOD_METADATA_REFRESH_1_61_R5.md) remains historical.

The general [processor command](COMPATIBILITY_PROCESSORS.md) uses `Gas Stations Fix` for fuel-only, `Rest Stops Fix` for rest-only, and `Map Compatibility Fix` for fuel plus rest, retaining `szczerb's Road Trip ... for <short map name>` and author `szczerb`. Its current default is `1.61-r6-experimental`; the legacy fuel command remains r2. The report records selected `fix_topics`. Combined packages use the user-selected M2D four-Ford map-specific 276x162 JPEG icons from `assets/mod-icons/map-compatibility/<map-slug>.jpg` for the seven supplied map/connector names. Fuel-only packages retain historical artwork selection; rest-only packages have no automatic icon. An explicit valid `--icon` overrides the default. [ADR-0008](../architecture/decisions/ADR-0008-compose-processors-and-local-rest-polygons.md).

The standalone [Practical Courier Jobs](PRACTICAL_COURIER_GENERATOR.md) package uses `szczerb's Road Trip Practical Courier Jobs`, author `szczerb`, category `other`, default `1.61-r1-experimental`, and a descriptive `...practical-courier-jobs-muscle-1.61-r1-experimental.scs` filename. It uses `assets/mod-icons/practical-courier-jobs.jpg` by default and accepts `--icon`; it does not imply a source map dependency. The existing J1B-based r1 archive is reused byte-for-byte in the r6 bundle. J3B is the user's favorite preview, with a key-fob reservation; no courier icon swap has been approved.

The new UTF-8 descriptions use short player-facing paragraphs and actual line breaks. Map packages explain only their selected fuel/rest behavior, source-relative load order and pending in-game checks. The supplied map combination lists all seven fixes directly above their own sources, including the four ProMods components and Reforma Mega Resources; optional background and job mods are labelled. Exactly one line identifies the current package with `[THIS MOD]`. The OtherMaps fix explicitly says it changes country petrol prices only. Unknown custom maps receive a direct-above-own-source instruction and the known combination as an example. The courier description explains the reviewed stock jobs, unchanged transfers, shared Quick Jobs and muscle-class effects, separate Food/Medical/Rideshare resources, and the remaining runtime checks.

## Historical fuel-package contract

| Field | Value / rule |
| --- | --- |
| Display name | `szczerb's Road Trip Gas Stations Fix for <short map name>` |
| Initial map name | `ATS Expansion` (omit the source mod's version from the short label) |
| Author | `szczerb` |
| Package version | `1.61-r0-experimental` initially; major/minor derived from declared ATS version, revision explicit |
| Compatible versions | `1.61.*`; a UI gate, not a claim that source-pinned sector recipes support every patch |
| Category | `map` |
| DLC dependency | `dlc_rt_ford` for the currently investigated Road Trip baseline |
| Icon | Optional root `mod_icon.jpg`, JPEG, exactly 276x162 pixels |
| Description | UTF-8 `mod_description.txt`, including experimental scope and source-map load priority |

The three historical fuel generation commands require `--map-name`, accept `--revision` (default `0`) and optional `--icon <JPEG path>`. The [map-wide command](MAP_WIDE_FUEL_GENERATOR.md) infers known map names and icons and writes timestamped paths automatically. The first full-map packages used revision `1`; the current missing-price increment defaults to **revision `2`** and produces `1.61-r2-experimental`. The default is a deliberate increment choice, not automatic revision counting. See [CLI examples](TOOLING.md). No stable/release mode or automatic revision increment is implemented. The program's own package version is independent of the generated mod version.

## Handoff filenames

User-facing fuel archives must identify the package family, map and version in the filename as well as the manifest. The historical r0 sample used `szczerbs-road-trip-gas-stations-fix-ats-expansion-1.61-r0-experimental.scs`. Follow `szczerbs-road-trip-gas-stations-fix-<map-slug>-<version>.scs` for subsequent fuel-only handoffs. The CLI accepts an explicit output path; the agent must supply this descriptive name. Combined map packages use `szczerbs-road-trip-map-compatibility-fix-<map-slug>-<version>.scs`.

Keep new regeneration copies and their reports in ignored `local_outputs/work/<timestamp>/verification/package-rechecks/`, with descriptive filenames ending in `-recheck.scs` or `-recheck-report.json`. Do not place an ambiguously named verification archive such as `branded-fuel-recheck.scs` beside the deliverable. The historical r0 verification copy was relocated without changing its bytes to `local_outputs/verification/package-rechecks/`; that historical sample remains in `local_outputs/generated/`. New deliverables use `local_outputs/generated/<timestamp>/` under the newer user-requested run-directory convention.

Names are encoded as quoted strings; empty/nonprintable map names, edge whitespace, negative/noninteger revisions and incorrectly framed/sized icons are rejected. JPEG validation checks framing and supported frame dimensions; it is not a full image decoder. Original artwork exports are separately decoded/inspected before handoff. Metadata paths are reserved against gameplay-resource collisions. The embedded report records title, author, version, map, revision and icon SHA-256 separately from the gameplay-resource list. Regeneration is deterministic and refuses to overwrite an existing file.

## Sources and limits

**Documented — SCS Modding Wiki, Mod manager, page edited 2025-10-17, inspected 2026-10-17:** [`mod_package` fields](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager) describe arbitrary display-name/author/version strings, root-relative JPEG icon with exact 276x162 dimensions, UTF-8 description, map category and compatibility/DLC fields. Narrow UI surfaces may truncate titles. This is shared ATS/ETS2 documentation predating Road Trip; it supports metadata format, not fuel mechanics or sample validation.

**Observed locally — user screenshot, 2026-10-17:** `Zrzut ekranu 2026-10-17 212256.png` shows the old sample-2 name, research author, `0.1.0-experimental` and default ATS artwork. The agent opened the original through its `<LOCAL_SCREENSHOT_PATH>` path. It documents old presentation, not a fuel transaction.

**Documented — user instructions, 2026-10-17/18:** the name, author, game-based revision convention and temporary experimental suffix are project requirements. The original fuel-only icon should show a simple pump/nozzle and passenger car(s), `GAS STATIONS FIX` at the top and map name below. The historical sample changed only one reviewed station near Helena. Neither its title nor `1.61.*` expanded that recipe's coverage. Combined-map r5 used the M2 navy frame, pump, parking symbol and three cars. The user selected corrected M2D with four Ford cars for r6 across all seven map presets. The separate courier headline is `JOB TYPES COMPAT`; J1B remains provisional.

Artwork provenance, prompts and proposals are recorded in the [icon asset guide](../../assets/mod-icons/README.md). Same-position payload details and reproduction are in the [sample-2 guide](OVERLAPPING_FUEL_SAMPLE.md).
