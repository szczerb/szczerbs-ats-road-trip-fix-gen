# Courier company check-in and physical location research

Inspected: 2026-10-18. Target: installed ATS Steam build `25952361`, with the existing log identifying game `1.61.3.18s`. The Steam manifest still reports that build on the inspection date. Map sample: ATS Expansion `23.0`, declaring ATS `1.61.*`, compared with installed Montana map data. This is static analysis/reporting only. No game, profile, map archive, or live mod directory was changed; no courier fix was generated or validated in game.

## Direct answer: common selection point or separate truck/car points?

**Observed locally:** the inspected company records have **one company check-in node per depot**, distinct from the depot's loading/unloading spawn-node array. Four inspected stock depot descriptors each have one generic Company Point/type-13 locator, with flags zero; they contain neither a second car-labelled company locator nor a general trigger polygon for job selection. The bounded placed comparison finds the same single-node structure in 23 stock and 59 ATS Expansion company items.

**Hypothesis, supported by these static structures:** the ordinary company job-selection avatar is based on a common company check-in location, with the appropriate market/interaction selected by game mode and job state. The inspected data does **not** support a rule that every mod depot needs a second car-specific selection marker. Do not create or duplicate markers from that premise.

**Unknown:** whether ATS 1.61 actually activates the identical point in truck and car modes at each inspected depot, which visible avatar it draws, and how it handles active courier pickup/delivery interactions. There was no controlled runtime comparison. A single generic point in the serialized company record is strong structural evidence, not proof that every runtime courier interaction reuses it. In particular, missing context classification can prevent eligible jobs even when a physical company point exists.

## Keep four layers separate

| Layer | Evidence and interpretation |
| --- | --- |
| Company job selection/check-in | **Documented:** SCS's locator guide calls Company Point the point used to select a delivery. **Observed locally:** one separate node reference on each inspected Company item. |
| Loading, parking, and delivery positions | **Documented in parser source:** Company `SpawnPoints` is an additional node list. Its flags describe load/unload, difficulty and trailer constraints. **Unknown:** exact ATS 1.61 car endpoint selection/fallback semantics. |
| Courier offer classification | **Observed locally:** `data_context` maps prefab identifiers to tags; `car_job_data` consumes origin/destination contexts, vehicle classes, distance intervals and minimum rating. A tag is not a placed marker. |
| Market and runtime state | **Observed locally:** car economy definitions contain rating tiers and distance limits. **Unknown:** full engine joining, discovery/refresh/state rules and marker visibility. Static coverage is not a promise of offers. |

**Documented — official, older shared-engine explanation:** the [SCS prefab locator guide](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators#Spawn_Point) distinguishes the Company Point used for delivery selection from an Unload point used for trailer parking. Its example is ETS2 and the page was last edited on 2025-08-06, before the installed Road Trip release; it establishes the generic distinction, not new car behavior. SCS's [Blender Tools constants](https://github.com/SCSSoftware/BlenderTools/blob/master/addon/io_scs_tools/consts.py) assign `COMPANY_POS = 13` and `CUSTOM = 9`. Their navigation-curve small/large-vehicle flags concern AI routing and supply no player courier permission rule.

## Company serialization and the third-party parser

The source identifier below is an inspected Git tree, not a verified upstream commit. Exact file links use the blob IDs from that tree. Older generated reports retain the original tree-as-commit URL as historical metadata; use these corrected references to inspect the sources.

**Documented in third-party parser source, cross-checked against complete local sectors:** TruckLib inspected tree `c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0` models [Company](https://api.github.com/repos/sk-zk/TruckLib/git/blobs/a340cdfe6b28da18ee5f1793a7647b426c7c1d48) as a prefab slave with one inherited Node and additional spawn points. Its [Company serializer](https://api.github.com/repos/sk-zk/TruckLib/git/blobs/33d1096d5cbb6a35224ca9d7cbe5149cf6449c92) stores the city token, parent prefab UID, company token, main node UID, then spawn-node references and their flags. The [prefab creator](https://api.github.com/repos/sk-zk/TruckLib/git/blobs/c6d94eaca86c6feb118d70d85eab36ebd5340d68) constructs the main Company node from CompanyPoint and puts trailer, unload and Custom locators into the additional list. This is a third-party model of the format, not SCS engine implementation.

**Observed locally:** for supported map format `907 / euro2 / 3`, Company item type is `6`. After its 57-byte common item header, offsets relative to the start of the item are: city token `+57`, prefab UID `+65`, company token `+73`, main node UID `+81`, spawn count `+89`, then `count` 8-byte node UIDs from `+93`, followed by `count` 4-byte flags. These offsets were inspected only after the structural parser consumed the entire sector successfully; arbitrary byte matches are insufficient.

**Documented in third-party parser source:** [CompanySpawnPoint](https://api.github.com/repos/sk-zk/TruckLib/git/blobs/004cf556f3c45f704112f457bba28f33f806219e) interprets bits 0–1 as difficulty, bit 2 as load versus unload, bits 4–7 as trailer length, and bits 16–19 as trailer type. It exposes no car eligibility bit. This older decoder does not establish that all remaining bits are unused by ATS 1.61. Preserve raw flags and leave unproven semantics unknown. Fuel's observed locator flag `1` and service bit `0x4000` must not be transferred to company items or their spawn arrays.

The fetched CompanySpawnPoint source matches Git blob `004cf556f3c45f704112f457bba28f33f806219e`, SHA-256 `b33e62204ba47f44749d53a754601f6e4edf56598c1cd14ddc5177855c06da62`. Cached CompanySerializer and PrefabCreator match their pinned tree blobs `33d1096d5cbb6a35224ca9d7cbe5149cf6449c92` and `c6d94eaca86c6feb118d70d85eab36ebd5340d68` respectively.

## Bounded stock and mod placement comparison

**Observed locally:** inspect the first 12 lexically sorted cached Montana `.base` sectors in `local_outputs/research/starter-area/stock-mt-bases/map/usa/`. Ten same-name sectors exist in the cached ATS Expansion extraction; two absent override files are not counted. All 22 cached sector byte streams were compared with current original sources: fresh selective `dlc_mt.scs` extraction and direct immutable ATS Expansion ZIP member reads. Every stream matches. This sample is a convenience sample from earlier Montana research, not a whole-map inventory or a controlled working/failing courier comparison.

| Original source | Sectors | Root-level Company items | Resolved main nodes and parent prefabs | Duplicate Company items per inspected parent prefab |
| --- | ---: | ---: | ---: | ---: |
| Installed `dlc_mt.scs` | 12 | 23 | 23 | 0 |
| `ATS_Expansion_v23.0_1.61.scs`, `base/map/usa/…` | 10 | 59 | 59 | 0 |

**Observed locally:** in `map/usa/sec-0008-0013.base`, stock Sidney `bn_live_auc`/`d_farm_mkt1` has main node UID `7341529620183066059` at XZ `(-31543.16796875, -50840.515625)` and six additional spawn nodes. The same winning ATS Expansion sector contains Sidney `mcsb`/`d_cust_2`, main node UID `6098220435869007874` at XZ `(-31565.53515625, -50821.83203125)`, with three spawn nodes and raw flags `245, 241, 242`. These are separate source placements, not a coordinate correspondence or a selected courier destination.

**Observed locally:** all three stock generic custom-depot descriptors inspected have no spawn or trigger records, but ATS Expansion's placed custom companies have resolved main and spawn nodes. Thus an empty PPD is not evidence that the world lacks a company selection point. Conversely, a valid company text definition is not evidence of a placed point. Inspect both layers and retain unresolved references explicitly.

**Unknown:** car suitability, collisions, orientation, reachability and active job behavior of every sampled node. Existing map items, matching context and generic truck loading flags do not establish these properties.

## Seven selectively re-extracted stock descriptors

**Observed locally:** these seven files were freshly extracted from current installed `base.scs`, rather than relying on snapshot path freshness. All are PPD version 25 and have zero trigger points. Types and flags below describe prefab resources, not the number of placed locations. Four depot resources have exactly one type-13/flags-0 Company Point. Their ordinary trailer/unload locators provide no car-specific Company Point.

| `base.scs` virtual path | Spawn records | SHA-256 |
| --- | --- | --- |
| `prefab/depots/supermarket3/supermarket3.ppd` | 6; one type 13/flags 0 | `bb3766d6dd3da05f6c4b48e6e67a655f920ece7e37a6ca25661464779c77f406` |
| `prefab/depots/cement_works/ks_cement_works_01.ppd` | 7; one type 13/flags 0 | `37f1a3a8bd1cd35ded3abe828f31fb2a1d6ae9464890e00713ccb93094e182ea` |
| `prefab/depots/an_124/an_124_depot.ppd` | 6; one type 13/flags 0 | `8e86684e83e97e03383e4a078cda5400bf47e36e401a6aacd9caa2b794084b1c` |
| `prefab/depots/grain_elevator/tx_grain_elevator.ppd` | 10; one type 13/flags 0 and nine type 9 | `196571833f12a0edaee8b6952bf7faf477813fd448643b2ec3a6b6234de58808` |
| `prefab/depots/custom/us_custom_depot_base.ppd` | 0 | `e9f3bfffe1b819ffb8b1925bf7f00b98e851ae2ae14b871b5ee62836be6696c9` |
| `prefab/depots/custom/us_custom_depot_field.ppd` | 0 | `6387b090f84b102ef80b7e2c64c0590926ce6778b638cd2e517566a26c435992` |
| `prefab/depots/custom/us_custom_depot_road.ppd` | 0 | `13d48907847d638524daecdbabbe4030af32d7768424ce3f745208f4b46ddf89` |

## Actions and offer definitions

**Observed locally:** fresh reads of five official definition files match their earlier extracted snapshots. The inspected `/def/world/trigger_action.sii` defines separate small/large-vehicle rest actions, but contains no company/courier job-selection action. The four stock company descriptors above contain zero trigger points despite having Company Points. This identifies company selection as structurally different from the rest-polygon action mechanism in these samples; it does not prove no other courier trigger mechanism exists anywhere.

**Observed locally:** `/def/data_context.sii`, `/def/car_job_data.sii` and `/def/car_economy_data.sii` express eligibility inputs already described in [courier findings](COURIER_RESEARCH_FINDINGS.md). They do not supply a second per-company physical selection coordinate. The existing reviewed `ahorrara` descriptor-alias candidate remains a context candidate; it is not a marker repair or a tested courier fix.

Current installed `def.scs` SHA-256: `1cc5d3ceb70c86e14b4e481ec297fc0788b0f7201d4db4ac4f129530a89eba17`.

| `def.scs` virtual path | SHA-256 |
| --- | --- |
| `def/world/trigger_action.sii` | `3242aa76e9667459a3cf80404761dca1198dd18b2bc1ca86ea7bdcdf0ca049f2` |
| `def/world/prefab.sii` | `8b9b470d42bcfb540624d61e03909f75c796996249b46268ddeff6812f60340e` |
| `def/data_context.sii` | `a284552331adb943515bc25a02f198c5b4bb622c52df49efa66a010d1959c524` |
| `def/car_job_data.sii` | `4a62420d6bd79086fdf4fa1caa3e37a6bb53636a1c82d65b78ab7eb0049b2d28` |
| `def/car_economy_data.sii` | `5454103676ecca3c3935b82a8ca173e60ccab55fccb95a7424229b1af06c09f3` |

## Reporting boundary and next evidence

**Project decision for this analysis increment:** report generic main/check-in nodes, additional spawn nodes and raw flags, prefab/company/city linkage, context matches and unresolved references. Do not interpret truck flags as courier support, add contexts from names alone, or serialize marker changes. Report car pickup/delivery suitability as unknown. Nested compound companies, cross-sector references and overridden resources require explicitly recorded inspection coverage; bounded absence is not whole-world absence.

### Editor filename is not company identity

**Documented:** the [SCS company_def reference](https://modding.scssoft.com/wiki/Documentation/Engine/Units/company_def) says units are *usually* stored as `/def/company/<company>/editor/<city>.sii`; it defines the semantic `city` and `prefab` fields. The [company_permanent reference](https://modding.scssoft.com/wiki/Documentation/Engine/Units/company_permanent) says `city_names` and `prefab_names` are generated from the `company_def` units in that company's editor directory. The first page was last edited in 2017 and the second in April 2026; neither makes an exact `<city>.sii` basename the unit's identity or documents the full Road Trip engine algorithm.

**Observed locally, 2026-10-18:** a fresh read-only listing of installed `dlc_ok.scs` contains `def/company/hs_mkt/editor/mcalester.dlc_ok.sii`. An audit that requests only `def/company/hs_mkt/editor/mcalester.sii` therefore reports an artificial absence. The suffix is part of the resource filename; semantic matching must inspect the contained unit's `city` and `prefab`, while preserving the containing company directory and effective mounted resource precedence. This listing did not extract or validate the member's unit contents, and it does not change the 82-record physical sample above.

**Project decision:** index all applicable effective `.sii` files in each relevant company editor directory and match parsed units, including include resolution. Report multiple conflicting semantic matches and missing evidence explicitly. Do not diagnose absent Courier Jobs from a failed exact-filename lookup. **Unknown:** whether a genuinely absent semantic company link in an incompletely inspected stack is missing at runtime, and whether such an absence prevents a specific courier interaction. The documented generation of company arrays gives those units a real role; it does not justify calling them unnecessary.

**Unknown requiring later manual observation:** at one officially classified stock depot and one officially classified mod depot, record the activation location and opened market in truck and car modes before any active job. Then observe a courier pickup and delivery independently of job selection. Record whether the visible avatar moves or changes with job state, and whether a context-classified custom depot with existing generic nodes can complete the route. A safe copied-profile test would distinguish UI appearance, shared check-in use and actual endpoint suitability. No further manual test is required during this night's authorized analysis.

## Existing generated prefab aliases: a static cross-feature risk

**Observed locally, 2026-10-18:** a read-only comparison of the existing Western Canada combined fuel/rest r3 package with its original WCE 1.7.3 ZIP identifies a separate compatibility risk. In the 123 sector files carried by r3, 195 placed prefab model tokens change. Fourteen of those prefabs are parents of root-level Company items in the same inspected sectors. Their original identifiers have the official `truck_dealer` context tag; their private `rtr…` replacements have no matching context target in the inspected official context, source archive, or generated package. The generated package contains no `def/data_context*.sii` resources. All 14 Company item records themselves remain byte-identical, and all relevant parent references resolve within the compared sectors.

| Original classified prefab | Company-linked placements changed to unclassified aliases |
| --- | ---: |
| `prefab.43c` | 5 |
| `prefab.43d` | 4 |
| `prefab.d_ws_dlr` | 5 |

**Observed locally:** example `kw_trk_dlr` / `kwinnipeg`, Company UID `0x65ba78ac98006c91`, parent prefab UID `0x5b9460d292800001`, in `map/usa/sec-0001-0016.base`: the actual placed model changes from `43c` to `rtr914ca443`; the original has `truck_dealer`, the alias has no inspected context tags. These are rest-prefab aliases in the combined package. The sample proves a change to the static context inputs around existing company placements, even though no courier processor was selected.

**Hypothesis — possible regression, not observed gameplay failure:** if the engine looks up courier context using the actual placed prefab's new identifier, these locations could lose their original classification. **Unknown:** whether the engine instead obtains the relevant prefab identity through a company/editor link or another runtime path. No offers, pickups or deliveries were compared with and without r3. An external active mod could also add context mappings absent from this bounded source/patch check. Do not report these 14 locations as confirmed broken jobs.

**Project decision for this reporting-only increment:** retain and report this risk without modifying or regenerating an existing fix. A future authorized repair/review should consider context preservation for cloned prefab identifiers across fuel/rest processors, including original exclusions and additive-context conflicts; a courier generator must not silently conceal the change by counting the old editor identity as the actual placed model.

Evidence: `local_outputs/work/2026-10-18_02-28-11/courier-marker-research/alias-audit/wce-r3-context-alias-audit.json`, SHA-256 `2e981e145e4e2a842efca11199b5cc6b8308bd01f1789c4959c211e02608142a`. It records every compared sector hash, every changed model, all 14 Company records and the exact context source. Original WCE archive SHA-256: `b90a2ec0210b1ca40c95c413089b3da098574040c39c7e03261d6cb2c9c76713`. Existing r3 SHA-256: `49ade9be22ea02d0ba73335352a4495c2a71430aff183249b366dd84d61a64ec`. Inputs, existing generated archives and their metadata were read only.

## Reproducibility artifacts

Ignored run root: `local_outputs/work/2026-10-18_02-28-11/courier-marker-research/`. Extraction used the existing [pinned external Extractor](RESEARCH_BASELINE.md); selected PPDs passed the project's version/section checks, and selected sectors passed full structural parsing with no trailing bytes before offsets were inspected. No whole archive extraction or game validation occurred.

| Artifact | SHA-256 |
| --- | --- |
| `placed-company-samples.json` — exact 22 paths, original-source comparisons, per-company node data | `4bb6985b8d21cd425bce8dea93d8a18f1beac55e8ee80a0c11386c29e4ec2b48` |
| `descriptor-provenance.json` — exact descriptor hashes and decoded records | `1edd4608ffb23051093b86792dccbeffadc565f0395c5deb581609e2122ce59c` |
| `definition-provenance.json` — exact definition hashes and cache/current comparisons | `cdc638cc7f4b150bc4275e44dfc248eda1e66ba53ebec3cc6e913ce2a704bc50` |

Supporting bounded text inventory: `local_outputs/work/2026-10-18_02-28-11/childinventory/courier_marker_inventory.md`, SHA-256 `18bc6834405db248ee04664645ebc9b24b312db2fdedc79a5333769bb7b55950`. That search alone could not identify the physical endpoint; the binary company/descriptor inspection supplies the additional evidence above. See [installed baseline](RESEARCH_BASELINE.md), [courier findings](COURIER_RESEARCH_FINDINGS.md), and [map structure](MAP_STRUCTURE_AND_COMPATIBILITY.md) for prior scope and provenance.
