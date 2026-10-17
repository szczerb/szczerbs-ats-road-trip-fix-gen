# Generated fuel mod metadata

Updated: 2026-10-17. Applies to this prototype's ATS 1.61 fuel packages. [ADR-0005](../architecture/decisions/ADR-0005-standardize-fuel-package-metadata.md) records the user-requested policy.

## Project contract

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

All three fuel generation commands require `--map-name`, accept `--revision` (default `0`) and optional `--icon <JPEG path>`. See [CLI examples](TOOLING.md). No stable/release mode or automatic revision increment is implemented. The program's own package version is independent of the generated mod version.

Names are encoded as quoted strings; empty/nonprintable map names, edge whitespace, negative/noninteger revisions and incorrectly framed/sized icons are rejected. JPEG validation checks framing and supported frame dimensions; it is not a full image decoder. Original artwork exports are separately decoded/inspected before handoff. Metadata paths are reserved against gameplay-resource collisions. The embedded report records title, author, version, map, revision and icon SHA-256 separately from the gameplay-resource list. Regeneration is deterministic and refuses to overwrite an existing file.

## Sources and limits

**Documented — SCS Modding Wiki, Mod manager, page edited 2025-10-17, inspected 2026-10-17:** [`mod_package` fields](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager) describe arbitrary display-name/author/version strings, root-relative JPEG icon with exact 276x162 dimensions, UTF-8 description, map category and compatibility/DLC fields. Narrow UI surfaces may truncate titles. This is shared ATS/ETS2 documentation predating Road Trip; it supports metadata format, not fuel mechanics or sample validation.

**Observed locally — user screenshot, 2026-10-17:** `Zrzut ekranu 2026-10-17 212256.png` shows the old sample-2 name, research author, `0.1.0-experimental` and default ATS artwork. The agent opened the original through its `<LOCAL_SCREENSHOT_PATH>` path. It documents old presentation, not a fuel transaction.

**Documented — user instruction, 2026-10-17:** the name, author, game-based revision convention and temporary experimental suffix are project requirements. The icon should show a simple pump/nozzle and passenger car(s), `GAS STATIONS FIX` at the top and map name below. The title describes the package family; the current handoff still changes only one reviewed station near Helena. Neither the title nor `1.61.*` expands the recipe's coverage.

Artwork provenance, prompts and proposals are recorded in the [icon asset guide](../../assets/mod-icons/README.md). Same-position payload details and reproduction are in the [sample-2 guide](OVERLAPPING_FUEL_SAMPLE.md).
