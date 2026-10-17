# Passenger-car refueling research findings

Inspected: 2026-10-17. Target: installed ATS 1.61.3.18, build 25952361, with `dlc_rt_ford.scs`. All local results below are static inspections. No game, editor, profile, or live mod-directory changes were performed.

## Result and boundary

**Observed locally:** official Road Trip station descriptors contain the existing GAS spawn type `3` with a new-to-this-investigation flags value `1`. Truck station GAS spawns use flags `0`. Reforma MegaResources includes actual station descriptors in supported PPD version 25 with flags `0` and no flags-`1` GAS spawns. This supports a small, reproducible binary descriptor experiment.

**Hypothesis, strong static evidence:** GAS flags `1` selects petrol/car refueling, while `0` selects the traditional truck/diesel interaction. This inference is supported by all 44 inspected official `*_rt.ppd` station descriptors and by mixed stations containing both values. It is not a published complete flag specification or an in-game confirmation.

**Unknown:** whether replacing the PPD alone updates existing map service items. A prefab locator can create a separate map service item, and SCS documents a spawn-rebuild editor command. The proof of concept therefore generates an **experimental candidate**, not a verified gameplay repair. Existing pump positions also do not establish physical car access or safe simultaneous interaction.

## Sources and version limits

| Source | What it establishes | Limit |
| --- | --- | --- |
| [SCS Blender Tools constants](https://github.com/SCSSoftware/BlenderTools/blob/master/addon/io_scs_tools/consts.py), `PrefabLocators.PSP.GAS_POS` | **Documented:** GAS spawn type is `3`; navigation-curve vehicle flags are a different field. | Retrieved master contains no current petrol spawn flag specification. |
| [SCS prefab locators](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators) | **Documented:** spawn points and general polygon/sphere trigger points are distinct locator types. | Page last edited 2025-08-06; not a complete 1.61 schema. |
| [TruckLib.Models SpawnPoint implementation](https://github.com/sk-zk/TruckLib.Models/blob/master/TruckLib.Models/Ppd/SpawnPoint.cs) and [PrefabDescriptor implementation](https://github.com/sk-zk/TruckLib.Models/blob/master/TruckLib.Models/Ppd/PrefabDescriptor.cs) | **Documented in the parser author's source:** supported PPD layout, versioned spawn record size, header counts and offsets. | Independent implementation, not an SCS format specification. Cross-checked against actual installed and supplied PPDs. |
| [TruckLib PrefabCreator implementation](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/PrefabCreator.cs) | **Documented in the parser author's source:** GAS spawn locators create separate service map items linked to a prefab. | Does not prove ATS 1.61 runtime rebuild behavior; its service creation does not interpret the new fuel flags. |
| [SCS editor commands](https://modding.scssoft.com/wiki/Documentation/Engine/Console/Commands/Editor) | **Documented:** `edit_build_spawns` rebuilds all spawn points in the editor. | No editor operation was run. |
| [SCS accessory_engine_data](https://modding.scssoft.com/wiki/Documentation/Engine/Units/accessory_engine_data) | **Documented:** engine `type` accepts `petrol` in 1.61. | Does not establish pump filtering rules by itself. |

## Exact local baseline

**Observed locally:** archive path inventory and selective extraction used the third-party `extractor` release 2026-07-29. Only 191 `/prefab/gas/**/*.ppd` assets were extracted from installed `base.scs`: 622,652 bytes total, all PPD version 25. Across them, GAS records had flags `0` (214 records) or `1` (125 records), with no other GAS flag values. Every one of the 44 filenames ending `_rt.ppd` contained at least one flags-`1` GAS record. The count applies to this selected directory, not the entire installed game or all DLCs.

Representative archive-relative paths:

| `base.scs` virtual path | Bytes | GAS spawn flags in record order | General trigger count |
| --- | ---: | --- | ---: |
| `/prefab/gas/us_gas_station_trigger_only.ppd` | 908 | `0` | 0 |
| `/prefab/gas/us_gas_station_trigger_only_rt.ppd` | 1256 | `1` | 0 |
| `/prefab/gas/us_gas_chemron_car_2rows_roof_trigger.ppd` | 1784 | `0, 1` | 0 |
| `/prefab/gas/us_gas_chemron_car_2rows_roof_trigger_rt.ppd` | 1748 | `1` | 0 |
| `/prefab/gas/us_gas_driver_truck_3rows_roof.ppd` | 1436 | `0, 0` | 0 |
| `/prefab/gas/us_gas_gp_car_2rows_roof.ppd` | 1748 | `1` | 0 |

**Observed locally:** the `_rt` chemron variant changes an existing pump position's GAS flags from `0` to `1`; other compared variants add spawns, AI curves, and semaphores. The PPDs are not universally equivalent apart from one flag. The GP two-row non-RT and RT descriptors already contain the same flags-`1` spawn, a counterexample to using filename suffix alone as a compatibility classifier.

**Observed locally:** installed `def.scs:/def/world/prefab.roadtrip.sii` registers Road Trip station definitions pointing to these `*_rt.ppd` resources. `/def/world/trigger_action.sii` defines vehicle-specific parking actions but no fuel/petrol action entry. Thus a general trigger-action rewrite is not supported by this evidence; zero general triggers in functional-looking official fuel descriptors is particularly useful counterevidence to that theory.

## Versioned binary layout used by the tool

**Documented in parser source and observed locally:** these PPD versions have a 96-byte, 24-little-endian-uint32 header. Relevant fields:

| Offset | Meaning |
| ---: | --- |
| 0 | PPD version (`23`, `24`, `25` inspected) |
| 20 | Spawn record count |
| 36 | General trigger count |
| 48–92 | Twelve section offsets |
| 64 | Spawn section start |
| 68 | Next section start, therefore spawn section end |

A spawn record begins with position (`3 × float32`), quaternion (`4 × float32`), then type (`uint32`, record offset 28). Version 23 records end there (32 bytes). Versions 24/25 add flags (`uint32`, record offset 32), making 36 bytes. The repository inspector checks ordered in-range section offsets, exact spawn extent, supported versions, and finite transforms. Other sections remain opaque; this is not full PPD semantic validation.

**Observed locally:** supplied ATS Expansion contains versions 23/24/25. Its `base/prefab/gas/gas_icon.ppd` is version 23, 808 bytes, with one type-`3` record and no flags field. Two garage descriptors (`recon_ama.ppd`, `recon_lubb.ppd`) also contain legacy GAS records. The archive's text definitions do not reference `gas_icon.ppd` as a prefab descriptor; a `gas_icon.pmd` model reference is used for a service icon. None of these observations alone establishes station placement or the effective winner in a combined mod stack. The generator refuses older-version mutation rather than assuming a version bump is safe.

## Reforma station candidates

**Observed locally:** selective inspection of 19 filename-selected PPDs from `local_inputs/Reforma_MegaResources_v3_0_1_161.scs` found all were version 25. The filename filter intentionally included two unrelated warehouse paths containing `bodegas`; it is an inventory filter, not a semantic station classifier. Four car-roof models and a totem have no spawn records. Fuel records in the remaining station candidates all use type `3`, flags `0`.

A narrow example is registered by `/def/world/prefab.mvs.sii`, unit `prefab.mx9`, whose descriptor is `/prefab_mvs/gas/MVS_pemex_small.ppd`. This is an actual station resource reference, rather than an unused path-name guess.

| Property | Value |
| --- | --- |
| Source bytes | 1700 |
| Source SHA-256 | `558813136dc24c7e621d694420d4b9162544fe5d24215e39c3c9099e6e030139` |
| Existing GAS record | offset 1000, type 3, flags 0 |
| Existing position | approximately `(-3.0587456, -0.000000735, 2.4338405)` in prefab space |
| Experimental added record | offset 1036, same transform, type 3, flags 1 |
| Candidate bytes | 1736 |
| Candidate SHA-256 | `3a43be1aa465e349163705d4d06e9fb344d5c471f0591ca799f0689573cac059` |

**Observed locally:** other registered examples include `prefab.mx2` (`/prefab_mvs/gas/MVS_gas_pemex.ppd`), `prefab.mx17` (`MVS_pemex_vallarta.ppd`), and `prefab.e11t` (`/prefab/gas/gas_icon.ppd`). The shared `gas_icon.ppd` path collides with ATS Expansion's older asset and needs effective load-order resolution. A package's declared prefab definition does not by itself establish a live, reachable map instance.

## Verified map instance and service linkage

**Observed locally:** the archive-tooling delegate selectively extracted the first 30 sorted `/map/usa/*.base` sectors from `Reforma_3_0_1_161.scs`, 15,367,223 bytes total, to test candidate use. An initial eight-byte token search was only a locator for further inspection. A bounded field parse using [TruckLib prefab serialization](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Serialization/PrefabSerializer.cs), [shared item serialization](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Serialization/MapItemSerializer.cs), and [service serialization](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Serialization/ServiceSerializer.cs) then cross-checked an actual instance:

- Sector `/map/usa/sec-0007+0015.base`, SHA-256 `22c427cbb847d4ac25fb6b45e53d801576e031abba0d6cf0b4aa53714dea025d`.
- Prefab record at byte 65769: item type `4`, UID `0x5fea825300800001`, model token `mx9` (numeric `15755`), two node references, one service slave reference.
- Linked service UID `0x66274276cd802e37`, record at byte 113419: item type `7`, parent UID matching that prefab, flags `0x80000000`, and no additional nodes.
- Prefab bounding ranges approximately x `[-25889.18, -25871.95]`, y `[24.76, 26.13]`, z `[63020.85, 63036.05]`. These are inspected bounds, not a tested teleport location.

**Documented in the token implementation:** [TruckLib.Core Token](https://github.com/sk-zk/TruckLib.Core/blob/master/TruckLib.Core/Token.cs) uses base 38 with a null character followed by digits, lowercase letters, and underscore; successive input characters have increasing powers. This was used to locate `mx9`, then independently checked against the surrounding item fields and its matching service-parent link. The script does not deserialize every sector item or establish the effective sector after other maps override it.

**Hypothesis:** the separately serialized service explains why adding a PPD locator may require rebuilding map spawns. The inspected sector contains one original service, while the candidate PPD contains two GAS locators. That mismatch is a concrete reason to test rebuild behavior before claiming a usable PPD-only fix.

## Experimental transformation and verification

**Observed locally:** `src/ats_road_trip/ppd.py` implements bounded inspection and an explicitly experimental version-25 transformation. It appends flags-`1` copies of type-`3`, flags-`0` records and adjusts the spawn count and seven following section offsets. All existing spawn records, indices, and opaque section bytes remain unchanged. Exact transforms already carrying a flags-`1` GAS record are skipped, making the transformation idempotent. Unknown GAS flags, unsupported versions, and inconsistent headers are rejected. No files are changed inside source archives.

**Hypothesis:** keeping the original flags-`0` record while adding a separate flags-`1` record could retain truck access and permit cars at the same pump. Official mixed stations place the two kinds at different positions, so same-transform coexistence remains an experiment, not an official authoring recipe. Physical access, trigger overlap, positioning radius, UI map markers, and price/fuel semantics need observation.

**Observed locally:** five focused synthetic unit tests cover versioned reading, preserved original records/opaque sections, offset changes, idempotence, and rejection of malformed or unsupported input. The inspector also processed all 191 official selected PPDs. Transformation plus a second idempotence pass succeeded for every applicable official descriptor. Those checks establish deterministic structural behavior only. No in-game refueling, editor rebuild, or truck regression test has occurred.

## Follow-up: existing service fuel bit

A later [ATS Expansion starter-area inspection](STARTER_AREA_SAMPLE.md) found service flags `0x80004000` correlated with car-oriented PPD locators, alongside `0x80000000` truck services. This provides a stronger, still unverified petrol-bit hypothesis and a separate Great Falls experiment converting an existing locator and its linked service. Counts/transforms are preserved, and the stock shared descriptor is not overridden globally. The earlier Reforma generator/results above remain unchanged. The new experiment is explicitly pinned to one sector/version and may remove truck access at the selected pump.

## Confounders and next experiment

**Observed locally:** the installed Ford DLC engine definitions for Bronco (`ford_27l_ecoboost.sii`), F-150 (`ford_tivct_32v_v8.sii`), Mustang (`challenger_289v8.sii`), and Crown Victoria (`v8_46l.sii`) each specify `type: petrol` and `adblue_consumption: 0.0` under `/def/vehicle/car/<vehicle>/engine/`. Thus petrol is actual local powertrain data, not solely an inference from the wiki. The player's effective engine still depends on overrides.

**Observed locally:** the historical `game.log.txt` under the ATS documents directory contains several mod-manager scan and active-session phases. Road Trip Ford Fuel X3 (Workshop ID `3811260729`, version 1.0.0) is present in the final active listing; its ZIP has four chassis definition overrides changing `tank_size` to 237, 294, 183, and 216. A linewise comparison against installed Ford DLC originals found only these tank changes in its four chassis files: Bronco 79→237, F-150 98→294, Mustang 61→183, and Crown Victoria 72→216. It contains no station, prefab, or map-sector fixes. Road Trip Zero Fuel Consumption appears in earlier mount/scan phases but is absent from the final active listing. Mount messages alone must not be treated as proof that a mod was active for the player's test. Generous Emergency Refuel also appears in the active listing.

**Observed locally:** the log's identified prefab error concerns `/model/mmbrown/ats_exp_prefab_01.ppd`, while ATS Expansion supplies its same-named descriptor in a nested directory. That error is a separate company-prefab path issue, not evidence of a fueling failure. No specific failed fuel interaction was reproduced or identified by a log error.

**Unknown:** exact affected/working station coordinates and effective vehicle definitions. A controlled experiment needs a copied/disposable profile and the exact active stack. Record the car/engine, fuel amount before and after, ability to enter and align at the pump, prompt behavior, station prefab, and a truck comparison. Compare the unmodified map, PPD-only candidate, and (if needed) a separate editor-rebuilt map candidate. Preserve the source sectors and live profile. If only the rebuilt candidate works, a practical generator must handle service-item/map-sector changes and their compatibility conflicts; PPD packaging alone is insufficient.

Ignored reproducibility artifacts are under `local_outputs/research/refueling/`: archive path lists, selective official/Reforma PPD extractions, `inspect_ppd.py`, `ppd_report.json`, and `candidate_report.json`, `inspect_sector_candidate.py`, and `sector_candidate_report.json`. Do not commit these game/mod assets or reports containing copied resources.
