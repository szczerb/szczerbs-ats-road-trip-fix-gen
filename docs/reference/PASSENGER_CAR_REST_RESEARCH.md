# Passenger-car rest-area research

Inspected: 2026-10-18. Target: installed ATS **1.61.3.18**, Steam build **25952361**, with Road Trip Ford. This is static research; no patch was generated, game session run, profile changed, or mod installed.

Subsequent implementation: the user selects a local 1,000-unit proximity rule instead of the global diagnostic proposed below. The [processor guide](COMPATIBILITY_PROCESSORS.md) and [ADR-0008](../architecture/decisions/ADR-0008-compose-processors-and-local-rest-polygons.md) describe private truck/bus/car actions and per-placement references. This research record's original "no patch" boundary remains historical; new static implementation checks do not establish runtime rest behavior.

[TASK-0015](../tasks/done/TASK-0015-investigate-passenger-car-rest-areas.md) records the completed investigation; [TASK-0016](../tasks/done/TASK-0016-prepare-rest-eligibility-experiment.md) scopes an independent diagnostic. That overnight deferral is historical. **Subsequent user report, 2026-10-18:** parking/rest works in Canada and Mexico, closing internal functional validation at that reported scope. [Dated result](VALIDATION_RESULTS.md#2026-10-18-refueling-and-rest-confirmed-in-canada-and-mexico); [additional regression coverage](MANUAL_TEST_CHECKLIST.md) remains optional.

## Result

**Observed locally:** ATS has separate large-vehicle and car parking/rest trigger actions. Existing truck rest areas can therefore lack car support even when their parking geometry exists. This is a different mechanism from fuel-spawn flags: the inspected official rest areas use general trigger polygons with vehicle-filtered actions.

**Hypothesis:** a mod-map rest polygon that references the large-vehicle action alone explains the user's missing car rest opportunities. The user's fatigue warning establishes that fatigue matters in their session; it does not identify the active rest polygon, its vehicle filter, or its physical bounds. A map icon alone is insufficient evidence of a usable car rest area. The user describes the actual interaction as parking and switching off the engine; do not interpret the absence of an upright world marker as failure.

## Installed action definitions

**Observed locally — `def.scs:/def/world/trigger_action.sii`:** the cached extraction from the recorded installed baseline contains:

| Unit | Editor label | Command | Numeric parameters | String parameters |
| --- | --- | --- | --- | --- |
| `trig_action.hud_parking` | Parking - Large vehicles | `hud_activate` | `3` | `truck`, `bus` |
| `trig_action.parking_car` | Parking - Small vehicles | `hud_activate` | `3` | `car` |

The command and numeric parameter agree; the vehicle list differs. The PPD trigger action tokens are `hud_parking` and `parking_car`, without the `trig_action.` namespace prefix. This is direct data evidence for a vehicle filter; the internal meaning of every `hud_activate` argument is not published here.

Cached definition: `local_outputs/research/refueling/def/def/world/trigger_action.sii`, SHA-256 `3242aa76e9667459a3cf80404761dca1198dd18b2bc1ca86ea7bdcdf0ca049f2`. The baseline extraction is dated 2026-10-17; the action data were inspected again on 2026-10-18. These cached observations must be refreshed after an installed-game update.

## What a rest area consists of

**Documented — shared engine authoring model:** SCS describes prefab trigger locators as polygon or sphere activation areas and specifically gives rest areas as an example. Spawn locators and trigger locators are separate types. The wiki was last edited 2025-08-06 and is not a full ATS 1.61 specification. [SCS prefab locator documentation](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators).

**Documented — numeric constants:** SCS Blender Tools lists `PARKING = 10`, `HOTEL = 8`, and `TRUCKSTOP_POS = 5` as spawn types. These numbers do not identify the action of a general trigger polygon. Its navigation-curve allowed-vehicle flags concern AI routing and must not be substituted for player rest filtering. [SCS Blender Tools constants](https://github.com/SCSSoftware/BlenderTools/blob/master/addon/io_scs_tools/consts.py).

**Documented in the independent parser's source:** TruckLib distinguishes `ServiceType.Parking = 4`, a service's low-byte category, from `OverlayType.Parking = 1`, the UI-map rest symbol. It can create a separate service from a Parking spawn locator. These are neither a count of all rest areas nor proof that a car can activate them. [TruckLib enums](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Enums.cs), [service creation](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/PrefabCreator.cs).

**Observed locally:** none of the **194** official descriptors inspected below has a Parking/type-10 spawn. Three motel descriptors have **no spawn records at all**, yet each contains two `hud_parking` polygons. Counting only type-4 map services would miss these actual rest-trigger resources.

## Official descriptor comparison

**Observed locally:** the bounded scan reused the previously extracted **191** `base.scs:/prefab/gas/**/*.ppd` files and selectively extracted three additional files, `/prefab/motel/ca_motel1.ppd`, `ca_motel2.ppd`, and `ca_motel3.ppd`. All 194 are PPD version 25. This is a selected resource sample, not all official prefabs, DLCs, map placements, or the user's effective mod stack.

| Trigger action | Vertex records | Groups identified by descriptor + trigger ID + action |
| --- | ---: | ---: |
| `parking_car` | 124 | 31 |
| `hud_parking` | 97 | 23 |
| `weight_check` | 4 | 1 |

The 191 gas descriptors alone contain 73 `hud_parking` vertices; the three motels add 24. Vertex counts are not rest-location counts. All trigger neighbors were checked for bounds, reciprocal links, matching group ID and action; numeric positions/ranges were checked for finiteness.

Representative `base.scs` members:

| Member | Rest actions | Evidence and limit |
| --- | --- | --- |
| `/prefab/gas/nm_truckstop1_chemron.ppd` | One four-vertex `hud_parking` polygon | Truck backlot; group ID 0, flags 0, range 3. |
| `/prefab/gas/nm_truckstop1_chemron_rt.ppd` | One four-vertex `parking_car` polygon | Different car-bay geometry, not a simple action-only variant. |
| `/prefab/gas/nm_truckstop1_depot_rt.ppd` | One car polygon and one large-vehicle polygon | Both actions coexist in a single official descriptor, in different areas. |
| `/prefab/motel/ca_motel1.ppd` | Two four-vertex `hud_parking` polygons | Zero spawn records; same result for motels 2 and 3. |

**Observed locally:** installed `/def/world/prefab.roadtrip.sii` registers the Chemron and depot `_rt` descriptors. Registration establishes an available resource, not a particular live placement. The Chemron truck polygon covers prefab-space x approximately `[-38.765, 36.999]`, z `[-138.465, -63.218]`; its `_rt` car polygon covers x `[16.923, 25.503]`, z `[-20.951, -13.951]`. Both have trigger flags 0 and range 3. Thus copying a whole `_rt` descriptor onto an old prefab would alter rest geometry and other content without proving access.

Pinned file identities:

| Member basename | Bytes | SHA-256 |
| --- | ---: | --- |
| `nm_truckstop1_chemron.ppd` | 5,980 | `92be3a4ee1a2788d32ca80bde50256c0e73032ee3caad2739df3d001b3715f91` |
| `nm_truckstop1_chemron_rt.ppd` | 5,288 | `d42842282ec855033017febdbff3875f98fdbc858bc35e40a5f15daafffcbe63` |
| `nm_truckstop1_depot_rt.ppd` | 5,972 | `0e7954cd155d6019d04c70dd73623ce7407a9378f742003a2a17026a5f400519` |
| `ca_motel1.ppd` | 3,360 | `5f09c328439c97d7cabb7b993a2414869514faf9e1c329d32ac7a25f739d43e9` |

## Placed Canadian-map evidence and existing fuel fixes

**Observed locally — supplied source sectors:** structural sector parsing and prefab-definition/resource links establish two actual placements of `prefab.us_gas_08`, whose installed `/def/world/prefab.sii` entry points to `/prefab/gas/nm_truckstop1_chemron.ppd`:

| Source package | Sector member | Prefab UID | Private alias in existing r1 fuel fix |
| --- | --- | --- | --- |
| Western Canada Expansion 1.7.3 | `map/usa/sec-0018-0030.base` | `0x57320980a1000001` | `rtg253fcfb3` |
| Western Canada–ProMods Connections 1.7.3 | `map/usa/sec-0020-0022.base` | `0x5732207b9a800001` | `rtgb9a7dd96` |

The source-sector SHA-256 values are respectively `d29b6ba0aecb2aa0f8c16d0f487e8fd1531081564597dc7bb11dec1ffc707ee3` and `106967cb7796fc81298040809d6564faf7cf6e101ebdc149f1317a0bc283fe37`. Both parsed sectors use map format `907/euro2/3`. Each source prefab has two linked type-7 **map items** with service category low byte **0** (gas), not category 4 parking services. The associated official descriptor contains the four-vertex `hud_parking` polygon described above, two GAS/type-3 spawns with flags 0, and no Parking/type-10 spawn.

**Observed locally — generated r1 fuel packages:** inspection of the private PPD referenced by each placement's fuel-fix alias found **four `hud_parking` vertices and zero `parking_car` vertices** in each. The existing fuel transformation therefore preserves these truck/bus-filtered rest polygons while adding car fuel support; it does not add car rest support. This is concrete static evidence of the requested distinction at real map placements.

**Unknown:** whether the user visited either exact placement, whether a separate nearby standalone trigger supplies car rest, and whether another enabled mod overrides the action definition or winning sector/resource. No parked-car engine-off/rest attempt at these identified polygons has been recorded. The static placements support the missing-car-rest explanation at identifiable candidates; they do not establish that every Canadian rest area is unavailable to cars.

The inventory delegate's exact UID/node/resource linkage evidence is in `local_outputs/work/2026-10-18_01-22-17/rest-inventory/placed-truckstop-trigger-links.json`. The integration review's checks of the two r1 private descriptors are in `local_outputs/work/2026-10-18_01-27-24/fuel-fix-preserved-rest-polygons.json`.

## Bounded inspection and generator feasibility

**Documented in parser source and cross-checked locally:** a version-25 PPD trigger record is 48 bytes: `uint32` group ID; 8-byte action token; three floats for range, reset delay and reset distance; flags; three position floats; two signed neighbor indices. Header word 9 contains trigger count; words 21 and 22 delimit the trigger section. The inspector checked exact section extent and interpreted records only after the existing PPD validator accepted the descriptor. [TruckLib.Models trigger reader](https://github.com/sk-zk/TruckLib.Models/blob/master/TruckLib.Models/Ppd/TriggerPoint.cs).

**Documented in parser source:** standalone map Trigger items have their own node polygon and action list. Their actions can carry custom parameters, so a future audit must inspect those parameters rather than just search tokens. [TruckLib trigger serializer](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Serialization/TriggerSerializer.cs), [action parameters](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/ActionBase.cs).

**Hypothesis — minimal diagnostic:** an override retaining `hud_parking`'s command, numeric parameter, and `truck`/`bus` entries while adding `car` could admit cars to existing large-vehicle rest polygons without replacing those polygons. This is a small definition experiment with global scope: it may affect stock and mod maps and does not isolate one location. The actual effect on UI icons, fatigue recovery, save/reload, and truck behavior needs a controlled game test. Loading the complete stock action-definition file with that one reviewed addition would avoid assuming duplicate unit IDs can be merged through a new additive definition file; the stock file itself warns that definitions share a namespace.

**Hypothesis — localized alternative:** clone a reviewed truck polygon as a separate `parking_car` polygon while preserving the original, assigning a new group ID and remapping neighbor indices. An analogous standalone map Trigger can retain its original action and gain a car action or separate co-located trigger, subject to actual parameter and action-activation rules. Neither approach has been implemented or validated here. Same-area dual actions are not established merely by the official depot's different-area coexistence.

**Unknown:** whether a PPD-only trigger addition takes effect immediately for existing placements, whether rest icons are generated independently or cached, whether standalone map triggers need parallel icon changes, and whether every truck parking area is physically usable by cars. Fuel service bit `0x4000` has no demonstrated role in rest filtering and must not be copied into parking services.

An implementation should connect a failed rest attempt to one identified placement in the winning mod stack; inspect both its PPD and standalone map triggers; compare an existing `parking_car` location; then test one reversible diagnostic on a copied profile. Acceptance requires car fatigue recovery after parking/engine-off, retained truck rest behavior, correct discovery/icons where applicable, and reload behavior. Placed truck-only polygon references are established above; their relationship to the user's visited locations and actual rest behavior remains untested. Broad absence in Canada remains a hypothesis.

## Reproduction artifacts

Ignored run directory: `local_outputs/work/2026-10-18_01-22-46/rest-research/` (Europe/Warsaw).

- `inspect_rest.py`: selective extraction and version-checked PPD trigger inspection, using the existing archive/PPD modules.
- `official-rest-report.json`: all parsed spawns and triggers, exact positions, neighbors, offsets, byte sizes and SHA-256 values.
- `official-selected/`: only the three newly extracted official motel descriptors.

The existing reference gas assets remain at their historical paths. No source archives were edited. This research does not imply an implemented rest generator or a verified repair.
