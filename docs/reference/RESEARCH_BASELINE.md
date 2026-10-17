# Installed research baseline

Inspected: 2026-10-17. Evidence label: **Observed locally**, except where explicitly marked otherwise. This records available reference data and a historical session, not a new game test or a complete reconstruction of the live profile.

## Game and source inputs

- Steam app `270880`, build ID `25952361`; installed directory `American Truck Simulator` in the Windows Steam library.
- Existing game log reports pack set `1.61.3.18` (game version `1.61.3.18s`). The log includes shutdown/unmount events; it is not a live-state API.
- Installed package files include `def.scs` (11,310,024 bytes), `base.scs` (9,482,216,747), `base_map.scs` (417,987,446), and `dlc_rt_ford.scs` (142,133,824). These have HashFS v2 headers. Seventy-six `.scs` files were present in the installation; presence alone is not a claim of owned/enabled DLC or current compatibility.
- The five immutable supplied map inputs remain recorded in [Local input inventory](LOCAL_INPUT_INVENTORY.md). Reforma internal definitions and selected descriptors have now been inspected; their initialization-era unknown status is superseded by the two findings documents.

The Windows installation used for this run was under `/mnt/c/Program Files (x86)/Steam/steamapps/common/American Truck Simulator`. Keep that external location read-only. Do not hard-code it as a required user installation path.

## Historical mod-stack evidence

The last explicit active-list marker in the existing log is `05:19:51.146`: 23 mods, comprising 11 local and 12 Workshop packages. The list spans two adjacent timestamps; matching only one exact timestamp would omit packages. Scan/mount events elsewhere are not equivalent to this active listing.

| Local package | Logged version |
| --- | --- |
| Mega Resources / Reforma | `3.0.1.161` each |
| ATS Expansion | `23.0` |
| Western Canada Expansion / its ProMods connections | `1.7.3` each |
| ProMods Canada models, assets, map, definitions | `1.6.4` each |
| Reforma OtherMaps Compatibility Patch | `40.161` |
| Alaska Expansion | `1.2.3` |

Relevant Workshop packages include Ford Fuel X3 `1.0.0`, Generous Emergency Refuel `1.0.0`, Food Courier `0.9.4`, Medical Courier `0.2.4`, Rideshare `0.9.1`, and Real companies/gas stations/billboards `4.02.01.`. The complete sanitized listing and archive size/mtime identities are recorded in ignored `local_outputs/reports/research-baseline.json`.

**Unknown:** the current active profile and exact UI priority semantics. The CLI therefore takes an explicit lowest-to-highest package order. The tested courier experiment uses official reference definitions/assets, then supplied MegaResources, then supplied Reforma; it does not claim to reproduce all 23 historical mods. ProMods, connection patches, and later overrides are further game-validation variables.

## Extraction method and provenance

The external [sk-zk Extractor release 2026-07-29](https://github.com/sk-zk/Extractor/releases/tag/2026-07-29) Linux x64 executable was used as a separate process. It remains in ignored `local_outputs/tools/extractor-2026-07-29/extractor`; it is not vendored into the project. See [third-party notices](../../THIRD_PARTY_NOTICES.md) and [tool usage](TOOLING.md).

| Artifact | SHA-256 |
| --- | --- |
| Downloaded Linux x64 ZIP | `8d6e046e2ac2a98d6ac3f11ea13ef049d3ac31526d7e8be129d5516ede3c5e88` |
| Extracted executable | `a9536ebf4f0225b886dcf82ab72b9e6ebb95d386dbc1aaafee3f2c83263c68b7` |

The ZIP hash and executable hash are different identities. This records observed downloads, not a claim that the upstream release publishes those checksums.

Verified operations: HashFS listing; selective reads; complete official `/def` extraction (34,970 files, zero failures); Reforma `/def` (2,240 files); MegaResources `/def` (2,967 files); 191 official gas PPDs (622,652 bytes total); selected Ford definitions, model/descriptor pairs, and 30 sampled Reforma sector files. No full `base.scs` extraction occurred.

Reference snapshots are under ignored `local_outputs/extracted/`. Recreate them from the recorded original archives after a game/mod update; snapshot paths alone do not prove freshness. Research artifacts and provenance are described in [courier findings](COURIER_RESEARCH_FINDINGS.md) and [refueling findings](REFUELING_RESEARCH_FINDINGS.md).
