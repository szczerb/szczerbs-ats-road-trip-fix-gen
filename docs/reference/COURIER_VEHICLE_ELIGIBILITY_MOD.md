# Feasibility: expanding Mustang courier eligibility

Inspected: 2026-10-18. Target: installed ATS 1.61.3.18s. This is a static modding assessment, not a generated package or a gameplay test.

## Finding

**Observed locally:** the stock Ford definition tags `ford.mustang_67` as `muscle` and `veteran`, while `ford.victoria_06` is tagged `sedan`. The 149 parsed `car_job_data` units yield 147 units listing `sedan`, 54 listing either Mustang tag, 52 shared, 95 sedan-only, and 2 Mustang-only. The job unit's `vehicle_types[]` field is the direct static eligibility switch. The cargo definitions do not contain per-car cargo-fit rules.

**Documented:** SCS describes SII units as objects with named units and attributes; arrays are represented by repeated indexed/array attributes. SCS also advises avoiding unit-name collisions. See the [SCS Engine Units reference](https://modding.scssoft.com/wiki/Documentation/Engine/Units). This supports editing job eligibility at the definition level, but it does not document the ATS 1.61 Road Trip offer allocator.

## Narrowest plausible design

**Hypothesis:** a standalone experimental eligibility mod could patch a small, reviewed subset of stock `car_job_data` units in a source-pinned copy of the complete canonical file and add `muscle` and/or `veteran` to those units' `vehicle_types[]`. Keep the existing `sedan` and every other field: cargo IDs, source/target contexts, distance interval, rating, priorities, and any other attributes. Select parcel/paperwork/sample or parts families individually based on the intended experiment. Leave all other stock jobs unchanged.

These are class-level matches, not exact vehicle-model IDs. Adding `muscle` or `veteran` also affects other current/future vehicles carrying that tag; no inspected evidence establishes a supported per-model whitelist. Record that scope in any future mod.

Do not change the Mustang's Ford tags to `sedan` globally. That broadens the class for all sedan jobs (including transfer and cargo families with no direct Mustang evidence), obscures the game’s intended class distinction, and affects any other system using those tags. Adding the class to selected job definitions is the narrower test of the specific whitelist hypothesis.

**Unknown:** whether `car_job_data.<unique_suffix>.sii` plus a newly named `car_job_data` unit is recognized and combined in ATS 1.61. Some installed Road Trip courier add-ons use separate suffixed files such as `/def/car_job_data.food_courier.sii`; this is local schema evidence, but their actual merge/runtime effect was not validated in this review. The [SCS 1.4 modding guide](https://modding.scssoft.com/wiki/Games/ETS2/Modding_guides/1.4.1) documents additive suffixed files only for a specific list of resource categories, and `car_job_data` is not on that list. Therefore do not assume a suffixed file will register these jobs.

For an initial experiment, a higher-priority replacement of canonical `/def/car_job_data.sii` is the definition-level path with the clearest file replacement semantics, but it must carry the complete, current file and alter only selected fields. It risks overwriting changes from other mods that replace the same file, and becomes stale when the game updates. A test must inspect the effective loaded definitions and logs. A new suffixed file is preferable only after proving that this ATS build merges it correctly. Do not reuse an existing SCS unit name for a separate additive unit; the SCS unit reference warns of collisions.

**Documented:** the SCS mod manager loads packages as mods and supports priority in the UI, but the reviewed official source does not establish field-wise merging of duplicate `car_job_data` units. Resource priority establishes replacement of the same virtual file path; it does not establish safe replacement of a duplicate unit name across different files. Do not rely on either field-wise or whole-unit merging of duplicate IDs in independent resources. Never assume that defining only `vehicle_types[]` will preserve omitted stock fields.

## Runtime limits and test boundary

The two Mustang-only units are `car_job.prem_46` and `car_job.prem_e46`: both require rating 4.6, use `car_dealer` at source and destination, have no `cargos[]`, and use `@@cjob_premium_allocation@@` as the name token. They admit veteran/sport/muscle. This is evidence for a separate premium vehicle-transfer family, not proof the Mustang can complete the normal Car Jockey workflow. Conversely, seven sedan-only standard Car Jockey units (including express variants) have no cargo definitions. Keep those transfer cases out of any cargo-size conclusion.

**Documented:** SCS's Road Trip preview says courier rating affects job types and route limits, vehicle type affects contracts, and Quick Jobs versus Dispatch use different vehicle arrangements. See [SCS Road Trip courier preview](https://blog.scssoft.com/2026/09/road-trip-quick-jobs-freight-market.html). A class whitelist change could therefore affect candidate eligibility in both markets, but the preview does not promise identical offers or prove that an altered job becomes available.

**Unknown:** whether the vehicle class is the only runtime restriction. Physical load/attachment support, pickup/drop-off access, destination availability, route, job rating, market refresh, profile state, and any hidden Road Trip checks remain untested. No cargo-volume parameter or explicit car cargo-fit check appeared in the inspected `car_job_data.sii` / `car_cargo.sii`; that does not prove the engine has none. A successful test needs a copied/test profile, fixed active mod stack, recorded rating/car/market and a matched control. Confirm visibility, start, cargo attachment, driving, delivery completion, and absence of new log errors separately.

## Evidence and sources

- **Observed locally:** `local_outputs/extracted/game-def/def/car_job_data.sii`, SHA-256 `4a62420d6bd79086fdf4fa1caa3e37a6bb53636a1c82d65b78ab7eb0049b2d28`; `car_cargo.sii`, SHA-256 `230c1aef59446b944e02f138ca2802c3560d3e9c2663070120e6cbcd854f4ffa`.
- Parser-based IDs and family counts: ignored sedan-only unit inventory (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-23-44/sedan-only-courier-units.json`).
- Existing vehicle-tag and courier schema findings: [COURIER_RESEARCH_FINDINGS.md](COURIER_RESEARCH_FINDINGS.md); availability limits: [COURIER_JOB_AVAILABILITY_RESEARCH.md](COURIER_JOB_AVAILABILITY_RESEARCH.md).
- **Documented — SCS:** [Engine Units](https://modding.scssoft.com/wiki/Documentation/Engine/Units), [ETS2 1.4 modding guide on additive file categories](https://modding.scssoft.com/wiki/Games/ETS2/Modding_guides/1.4.1), [Mod manager](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager), and [Road Trip courier preview](https://blog.scssoft.com/2026/09/road-trip-quick-jobs-freight-market.html). General engine/file-combination material is older and does not specify `car_job_data` support in ATS 1.61.
