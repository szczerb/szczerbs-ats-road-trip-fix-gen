# Courier compatibility research findings

Inspection date: 2026-10-17. Target: installed ATS 1.61.3.18s, pack set 1.61.3.18, Steam build 25952361. This is static research and analysis of an existing log; no controlled game experiment has been run. Sources are immutable supplied archives, the installed `def.scs` and `base.scs`, installed Workshop definitions, and a targeted read of `game.log.txt`. Large source data and scratch reports remain ignored beneath `local_outputs/`.

## Actual job definition mechanism

**Observed locally:** `def.scs:/def/car_job_data.sii` contains 149 `car_job_data` units. They reference `car_cargo_data` units through `cargos[]`, eligible vehicle classes through `vehicle_types[]`, origin/destination tags through `source_data_contexts[]` and `target_data_contexts[]`, a `company_distance` interval, and `required_courier_rating`. There are 29 units requiring rating 0, 42 requiring 2.6, 32 requiring 3.6, and 46 requiring 4.6. A job lacking `cargos[]` can represent a vehicle transfer; this must not be rejected by a future parser as incomplete cargo registration.

**Observed locally:** `def.scs:/def/data_context.sii` maps `prefab.*` unit identifiers to tags using `data_context` units, `target_data[]`, and `tags[]`. For example, `context.prefab.custom_depot` classifies all `prefab.d_cust_1` through `prefab.d_cust_8` as `custom_depot`. The job `car_job.bdoc_0` accepts that tag as both origin and destination, accepts the seven listed vehicle classes, has `company_distance: (40, 250)`, and requires rating 0. Its classes are pickup, suv, sedan, muscle, veteran, sport, and offroad.

**Observed locally:** `def.scs:/def/car_economy_data.sii` independently defines rating tier thresholds 0, 2.6, 3.6, and 4.6, and tier route limits 450, 630, 765, and 900 km. Thus a context match is only part of static eligibility; it does not establish a generated offer.

**Observed locally:** selective extraction of `dlc_rt_ford.scs:/def/vehicle/car` produced 751 definition files with zero extraction failures. Each Ford's `data.sii` uses `accessory_truck_data`, despite being in the car tree. Its `tags[]` values are `pickup` for `ford.f150_23`, `offroad` for `ford.bronco_24`, `sedan` for `ford.victoria_06`, and both `muscle` and `veteran` for `ford.mustang_67`. These names coincide with the job eligibility classes. Do not invent an `accessory_car_data` unit or `car_type` property in a future parser. The scratch extract is `local_outputs/research/courier/ford-def/`.

**Hypothesis, strong schema evidence:** prefab context classification is one editable part of courier eligibility. A definition-only patch could add a reviewed custom prefab to an existing tag without changing company names. Actual registration, offer generation, usable pickup/drop-off positions, and delivery completion still need game validation.

**Unknown:** the complete engine algorithm joining placed company items, prefab contexts, spawn points, vehicle availability, route distance, market refreshes, and profile state. These static files establish inputs, not the whole implementation.

## Installed positive schema samples

**Observed locally:** three installed Workshop packages are ordinary directories, so selective text inspection required no asset extraction. Their manifests/log identify the following versions:

| Workshop ID | Package | Version | Relevant virtual files |
|---|---|---|---|
| 3811536074 | Food Courier Jobs for Road Trip | 0.9.4 | `/def/car_job_data.food_courier.sii`, `/def/car_cargo.food_courier.sii`, `/def/data_context.food_courier.sii` |
| 3812885729 | Medical Courier Jobs for Road Trip | 0.2.4 | `/def/car_job_data.medical_courier.sii`, `/def/car_cargo.medical_courier.sii` |
| 3813173177 | Rideshare Jobs for Road Trip | 0.9.1 | `/def/car_job_data.rs_test.sii`, `/def/car_cargo.rs_test.sii` |

**Observed locally:** Food Courier's `context.prefab.food_market` adds a `food_market` tag to five official prefab identifiers; another unit tags three food plant prefabs. Its job definitions consume those tags alongside existing tags such as `retail` and `warehouse`. This is a concrete example of additive context and job files, rather than renamed traditional companies. It is a positive schema sample, not independently verified working gameplay.

**Observed locally:** the existing log includes an earlier active stack of 20 mods without these three courier packages, followed by a later active stack of 23 with all three. Package-discovery or temporary Mod Manager mount lines alone must not be treated as proof a package was active during gameplay. Future reproduction should use one explicitly recorded stack, and first isolate official jobs before adding these extra job types.

## ZIP map comparison

**Observed locally:** every `.sii` under the three ZIP archives' `def/company/*/editor/` paths was read selectively and its `city` and `prefab` token parsed. ATS Expansion's archive `base/` prefix was normalized for virtual paths; the existing log explicitly reports mounting that subdirectory. Each sampled editor file contained exactly one city and one prefab token. Counts below describe definition occurrences, not distinct placed depots or verified job locations.

The comparison ignores commented `target_data` lines in the official context file. It does not resolve other mods' later context overrides.

| Archive version | Editor files | Distinct cities | Distinct prefab tokens | Occurrences classified by baseline context | Unclassified occurrences |
|---|---:|---:|---:|---:|---:|
| ATS Expansion 23.0 | 616 | 191 | 33 | 579 | 37 |
| Alaska Expansion 1.2.3 | 49 | 16 | 28 | 45 | 4 |
| Western Canada Expansion 1.7.3 | 365 | 116 | 100 | 340 | 25 |

**Observed locally:** ATS Expansion uses `d_cust_1` through `d_cust_8` in 555 of its 616 editor definitions. All eight are already classified by the installed official context file and accepted by several official jobs. Examples include `/def/company/dr47/editor/ansley.sii` → `d_cust_2` and `/def/company/sysco/editor/ardmore.sii` → `d_cust_7`. A custom company name therefore does not, by itself, demonstrate missing prefab classification or justify renaming the company.

**Observed locally:** ATS Expansion's 37 unclassified occurrences are `d_food_str` (2), `dr47` (6), `dr477` (2), `driver47` (3), `gneck` (1), `gneckhcr` (2), `goose` (4), `kbhomes` (2), `kdgrain` (2), `kdhay` (3), `kdhay1` (6), `straw_l` (2), and `sysco` (2). The 12 custom tokens account for 35 occurrences. Their prefab model definitions were not found among that archive's small text definitions; they may come from another package. Do not invent descriptor paths for them.

**Observed locally:** Alaska's four unclassified occurrences are `d_aport_elp` (1), `d_food_mkt4` (2), and `d_hs_mkt` (1). All three are explicitly excluded in official context comments because a through-driving layout spawns the player in the wrong direction.

**Observed locally:** Western Canada's 25 unclassified occurrences are `d_aport_elp` (1), `d_food_mkt` (6), `d_food_mkt4` (4), `d_food_plnt` (1), `d_food_str` (4), `d_hs_mkt` (5), `d_train_st2` (1), `d_train_st4` (1), and `d_wd_pln` (2). All except `d_food_str` are explicitly excluded by those official comments. Reclassifying every missing token would therefore undo known official exclusions.

**Hypothesis:** an unclassified custom prefab with safe existing car positions could be a candidate for a small additive context patch. The counts identify candidates for investigation, not automatic fixes. Lack of a context match does not mean a whole city lacks jobs; other depots in that city can still qualify.

## Reforma comparison and concrete context candidate

**Observed locally:** selective `/def` extraction with the HashFS tool succeeded for Reforma and MegaResources, both declaring version 3.0.1.161 in the existing log. The Reforma tree contains 1,532 company editor files, 205 distinct city tokens, and 209 prefab tokens; 1,172 editor occurrences match official context classification and 360 do not. Of those 360, 123 use prefabs explicitly excluded by official context comments. MegaResources contains 37 company editor files across seven city tokens and 32 prefab tokens, with 33 classified occurrences and four unclassified occurrences. Neither extracted definition tree contains a `data_context` file. These counts do not represent the effective loaded union: later mods can override files and company editor definitions.

**Observed locally:** `/def/world/prefab.cmex.sii` in MegaResources defines `prefab.ahorrara` with the same model and descriptor paths as the official classified `prefab.d_food_mkt5`: `/prefab/depots/supermarket3/supermarket3.pmd` and `/prefab/depots/supermarket3/supermarket3.ppd`. Neither Reforma archive lists an override of that descriptor. The full prefab units differ in rendering attributes, so this is shared model/descriptor evidence, not byte-identical units. Official `data_context.sii` tags `d_food_mkt5` as `retail`; it does not mention `ahorrara`.

**Observed locally:** Reforma's eight `ahorrara` editor definitions refer to cities `loreto`, `cd_constit`, `rioverde`, `navojoa`, `maiz`, `santa_ana`, `ebano`, and `parras`. Their virtual paths are `/def/company/ahorrara/editor/<city>.sii`. Thus `ahorrara` is a resolved custom prefab with an exact official descriptor counterpart and missing classification; it is a stronger candidate than assigning tags from model names.

**Hypothesis, supported candidate rather than gameplay fix:** adding `target_data[]: prefab.ahorrara` with `tags[]: retail` in a uniquely named additive context unit should make the same retail job class available to these locations, subject to their placed map data, eligibility, routes, and market state. A minimal generated experimental file needs only this unit and its SII wrapper; it need not copy the supermarket descriptor, edit sectors, or rename companies. This has not been loaded in game.


**Observed locally:** two official job units accept retail origins: `car_job.retpack_0` and `car_job.retpack_e26`. The rating-0 unit targets `warehouse`, accepts all seven vehicle classes, and has distance interval `(40, 350)`. Several official jobs accept retail destinations, including `car_job.psmpl_0` at rating 0 and distance `(40, 450)`, originating at factory, agriculture, car dealer, warehouse, or vehicle logistics contexts. These are useful controlled candidate routes; retail context alone does not promise frequent departures from every supermarket.

**Observed locally:** several other unclassified Reforma prefab tokens resolve to the same official `us_custom_depot_base.ppd` as classified `d_cust_*`: `chelas`, `fletes_tlal`, `fierro`, `report`, `califa`, `air_gdl`, `construc`, `tres_presasb`, `usbbmx`, `dynamix`, and `alimentos`. MegaResources adds `tequilera` and `teq_01`. Because that generic descriptor has no spawn points, physical map placement remains especially relevant before enabling these candidates. The classification mechanism also admits exact descriptor aliases such as `conmex` and `air_gdl_b`; choosing a broader automatic rule requires load-order-aware resolution and review of exclusions.

## Physical placement limits

**Observed locally:** `def.scs:/def/world/prefab.sii` maps `d_cust_1`, `d_cust_2`, and `d_cust_6` to `/prefab/depots/custom/us_custom_depot_base.ppd`; `d_cust_3` and `d_cust_7` to `us_custom_depot_field.ppd`; and `d_cust_4` and `d_cust_5` to `us_custom_depot_road.ppd`. Selective extraction from `base.scs` found PPD version 25 in these three descriptors, each with zero prefab spawn points and zero trigger points. ATS Expansion contains no override PPD path for these generic custom depot descriptors.

**Hypothesis:** the functional points for these custom depot locations are supplied by map items rather than these generic descriptors. A context-only audit cannot validate those points. The upstream [TruckLib Company model](https://raw.githubusercontent.com/sk-zk/TruckLib/master/TruckLib/ScsMap/Company.cs) describes additional map nodes for parking/trailer spawn points; its applicability to new ATS 1.61 car semantics is **Unknown**.

**Observed locally:** the official `d_food_str` model points to `/prefab/depots/grain_elevator/tx_grain_elevator.ppd`. Its version-25 descriptor has one type-13 spawn and nine type-9 spawns, with no trigger points. It has no baseline context classification and no explanatory exclusion comment. In the ZIP samples it appears at ATS Expansion's Bovina and Texhoma definitions and Western Canada's Maple Creek, Minnedosa, Yorkton, and Assiniboia definitions.

**Unknown:** whether these grain elevator spawn flags permit safe Road Trip use. Trailer/company spawn presence is insufficient proof. Do not automatically add `agriculture` or another tag merely because the model name sounds appropriate.

## Existing log evidence

**Observed locally:** the existing `game.log.txt`, during two loads with different active stacks, reports invalid company item assignments for `dr47.roy`, `bm_con_pln.escobedo`, and `pt_trk_dlr.joplin`. It also reports missing generic trailer load/unload points and an invalid descriptor path for an ATS Expansion garage prefab. These errors predate this investigation; no claim is made that they were reproduced by the investigator.

**Observed locally:** 85 missing-target-map-link errors cover ten company/city pairs. The most frequent are `bn_live_auc.sheridan` (23), `bn_farm.jackson` (21), `bn_live_auc.billings` (19), and `flv_food_pln.ottumwa` (11). The remaining pairs are `pho_oil_gst.indio`, `mcc_frm_pln.iowa_city`, `gp_farm.emporia`, `nmq_min_pln1.butte`, `ven_whs.yuma`, and `gp_live_auc.mcalester`.

**Unknown:** whether any listed error caused a reported Courier Job absence. These are independent reasons to avoid treating all market failures as missing tags. The log contains no controlled before/after courier observation and does not establish a working or failing city pair.

## Generator boundary and candidate recipe

**Hypothesis:** the smallest schema-backed courier experiment is a new `def/data_context.<unique_suffix>.sii` with a uniquely named `data_context` unit, a reviewed `target_data[]: prefab.<token>`, and an existing `tags[]` value consumed by official jobs. It can leave original company/cargo definitions and map sectors untouched. A generator should reject already-classified tokens, official exclusions, unresolved prefab definitions, unknown spawn compatibility, and naming conflicts unless an explicit reviewed experimental mapping supplies the missing evidence.

A schema-backed experimental `ahorrara` patch could contain:

```sii
SiiNunit
{
data_context : context.rtcompat.ahorrara
{
    target_data[]: prefab.ahorrara
    tags[]: retail
}
}
```

**Hypothesis:** this additive file restores the missing classification. It does not certify map spawn placement, market offers, or completion. Generate the wrapper and manifest as authored text; retain the source archive/build fingerprint in the accompanying report.

**Unknown:** whether additive contexts classify the target as intended in every engine path, and whether the concrete `ahorrara` candidate is safe in its placed map locations. The installed Food Courier package supplies credible syntax evidence, but an emitted file must remain an unvalidated experiment until game validation passes. There is currently no evidence-supported automatic rule for renaming companies or creating new courier marker coordinates.

A safe first increment can audit context coverage and produce a provenance report, and can generate the explicitly reviewed `ahorrara` alias experiment while refusing unsupported patch inference. Refueling findings must be assessed independently before selecting an actual generated fix.

## Reproducibility and next experiment

**Observed locally:** scratch metadata reports are `local_outputs/research/courier/zip_company_inventory.json`, `zip_context_comparison.json`, `ppd_comparison.json`, `reforma_context_comparison.json`, `prefab_resolution.json`, `exact_model_descriptor_aliases.json`, and `log_map_link_counts.json`. Official selected definitions are under `local_outputs/extracted/courier-def/def/`; the shared full definition reference is under `local_outputs/extracted/game-def/def/`. JSON reports hold identifiers/counts and parsed binary metadata, rather than copies of full assets.

The next controlled game experiment should:

1. Use a disposable or copied profile with recorded ATS build, DLC versions, active mod order, car and vehicle class, Courier Rating, discovery state, and market time. Preserve the original profile. Start with official courier definitions; add Food/Medical/Rideshare only after that baseline is understood.
2. Pick one officially classified mod depot and one reviewed unclassified custom depot. Confirm physical access and capture the actual placed prefab/company item and its car pickup/drop-off positions. Include an official map depot as a control.
3. Record Quick Jobs and Dispatch Market separately. For each candidate job, check source/destination tags, distance interval, car class, rating, and whether valid reachable destination depots exist. Do not diagnose absent offers from a single refresh.
4. If a single safe context mapping is justified, compare matched profile copies with and without only that patch. Allow a controlled market refresh by normal game progression; any console economy reset is a separate deliberately authorized experiment, because it may affect profile state.
5. Accept an experiment only after the offer appears and a pickup, drivable route, and delivery complete correctly. Check orientation, collisions, customer completion, ratings, and relevant truck loading/unloading behavior. Inspect logs for new unit conflicts, assignment errors, or missing links.
6. Keep package provenance and before/after observations. If the patch changes no offers or breaks spawn behavior, retain that result as negative evidence and investigate map placement rather than broadening tags indiscriminately.
