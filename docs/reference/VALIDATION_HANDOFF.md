# Research result and validation handoff

Date: 2026-10-17. The overnight milestone delivered research, usable inspection tooling, and generated experimental packages. It did not run the game/editor or modify a live profile. See [baseline](RESEARCH_BASELINE.md), [tool usage](TOOLING.md), and [validation task](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md).

## First external gameplay evidence

The [2026-10-17 user test](VALIDATION_RESULTS.md) reports successful refueling at the eastern Helena-area target. Its car-map icon appears in the patched screenshot; the nearer city station remains truck-only. This is a positive result for the combined single-pump descriptor/service sample, not validation of every experiment. A follow-up corrects the truck screenshot to a pre-installation baseline and reports that the patched target disappears from the truck map. Physical truck refueling is not yet tested. Resolve preservation of truck and car support at the same pump before broadening to the nearer city station; its four logical points also exceed the first generator's one-point scope.

## What the evidence supports

- **Observed locally:** courier jobs consume context tags and vehicle/rating/distance inputs. Most sampled ZIP-map company definitions already use classified prefabs. Several unclassified stock prefabs are intentionally excluded by SCS for spawning reasons; enabling everything would discard that evidence.
- **Hypothesis with exact-asset evidence:** Reforma's unclassified `ahorrara` prefab can inherit `retail` classification because its model/descriptor pair is shared with official `d_food_mkt5`, and neither supplied Reforma archive overrides that descriptor. A generated additive experiment targets eight company/city definitions. This does not prove any particular city lacked all jobs.
- **Hypothesis with paired-descriptor evidence:** GAS type 3, flags 1 selects car/petrol interaction. All 44 sampled official `_rt` station PPDs contain it; several Reforma stations lack it. The generated `mx9` descriptor retains the truck locator and adds a same-transform flags-1 locator.
- **Observed locally:** `mx9` has a real prefab instance linked to a separately serialized service item in a sampled Reforma sector. **Unknown:** whether that service is rebuilt at runtime from the changed PPD. A descriptor-only experiment may be ineffective until editor rebuilding, and co-located interactions still need testing.

## Reviewable local artifacts

All are ignored derived files, not committed/distributed mods. Their embedded report identifies resource changes, hashes, source packages, and experimental status.

| Output under `local_outputs/generated/` | Purpose | Changed gameplay payload |
| --- | --- | --- |
| `reforma-ahorrara-courier-poc.scs` | Narrow recommended first courier experiment | One 108-byte additive context file, one alias, eight definitions |
| `reforma-courier-aliases-poc.scs` | Broader static alias experiment | One 1,513-byte context file, 15 aliases across 33 effective definitions |
| `reforma-mx9-fuel-experiment.scs` | Single Reforma station-type experiment | One PPD, 1,700 → 1,736 bytes, original truck record preserved |

Use one courier context output at a time: they share an additive file path. The source station PPD SHA-256 is `558813136dc24c7e621d694420d4b9162544fe5d24215e39c3c9099e6e030139`; the modified candidate is `3a43be1aa465e349163705d4d06e9fb344d5c471f0591ca799f0689573cac059`.

## Easier ATS Expansion location

The [starter-area guide](STARTER_AREA_SAMPLE.md) adds separate Helena-area and Great Falls single-pump experiments. Prefer checking Helena HQ selection because its effective garage retains a standard class; Great Falls uses a custom garage, with a target about 94 map metres from that placed GaragePoint. It edits a private descriptor **and the existing map service**, preserving counts and transforms. Confirm Great Falls appears in the new-profile selector; custom garage presence does not prove eligibility. The sample converts one pump, can remove truck access there, and overrides a whole sector. This is distinct from the earlier Reforma PPD-only experiment.

## Next requested fuel test: sample 2

[Same-position sample 2](OVERLAPPING_FUEL_SAMPLE.md) preserves the original truck records and adds a car interaction at the same eastern Helena dispenser. Disable sample 1 and enable the new package above ATS Expansion. Compare actual refueling and map visibility in both modes at that exact point. This extends the experiment with a cloned service/node; its static verification does not establish runtime coexistence.

## Copied-profile experiment

1. Start from a disposable/copied profile, record exact ATS/DLC/map versions and priority, and keep the original profile unchanged. Confirm original source hashes and inspect each generated ZIP's embedded report. Place only the chosen candidate above its source maps/resources in that test profile.
2. First isolate official courier behavior. Record the effect of Food/Medical/Rideshare, Fuel X3, emergency-refuel, branding, ProMods, and compatibility packages separately rather than assuming the historical 23-mod stack is a clean baseline.
3. For Ahorrara, candidate city tokens are `loreto`, `cd_constit`, `rioverde`, `navojoa`, `maiz`, `santa_ana`, `ebano`, and `parras`. Confirm a placed accessible depot; company editor definitions alone do not prove a usable marker. A rating-0 official retail-origin job exists, but has route/destination constraints and sparse job-type coverage.
4. Compare matched copies with/without the courier patch. Record Quick Jobs and Dispatch Market separately, vehicle tags, rating, distances, destination contexts, discovery state, and market progression. Use ordinary time progression before considering a deliberate economy-reset experiment. Require an offer, usable pickup/orientation, drivable route, completed delivery/rating, and preserved truck loading behavior.
5. For fuel, locate a placed `prefab.mx9` instance and establish truck/car controls. The sampled sector `/map/usa/sec-0007+0015.base` contains prefab UID `0x5fea825300800001`; inspected bounds are approximately x -25889..-25872, z 63021..63036. These are static bounds, not a tested teleport instruction. Record approach, alignment, prompt, fuel before/after, and truck behavior.
6. Compare the PPD-only candidate first. If nothing changes, investigate a separate editor-rebuilt map experiment: new spawn locators can require linked service items. Do not blindly patch unknown sector flags or copy sectors from another version. Record all changed sector files and conflicts if rebuilding is needed.
7. Inspect logs for new conflicts, broken assignments, missing references, or services. Record negative outcomes as evidence. Remove candidates from the copied profile when done; do not broaden the rule just to force an apparent success.

## Remaining scope

A Helena-area user observation and four screenshots are now recorded in [validation results](VALIDATION_RESULTS.md); quantitative fuel/payment, truck/reload checks, other candidate outcomes, and courier observations remain open. Static experiments explain plausible mechanisms, not every issue in the full map combination. Legacy PPD conversion, arbitrary custom depots, placed car pickup positions, and map-service authoring remain outside this first PoC. Successful controlled game evidence is the gate for calling a candidate a verified fix or automating a broader transformation.
