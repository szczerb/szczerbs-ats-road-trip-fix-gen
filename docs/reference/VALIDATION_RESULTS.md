# Gameplay validation results

## 2026-10-17: Helena-area sample, first user test

**Documented — user-reported gameplay:** the user created a first disposable test profile with ATS Expansion as its only baseline mod, then compared it with the Helena-area sample enabled. The user owns all DLCs. The eastern station became available to passenger cars and the user successfully refueled there. The drive required a substantial detour. The station inside Helena near the garage remained visible only for trucks.

This is a first-hand user report, **not gameplay independently reproduced by the agent**. The generated reference baseline was ATS 1.61.3.18 / ATS Expansion 23.0; the running build, active package fingerprints, and numerical fuel/payment changes have not been independently captured for this test. The cockpit screenshot shows a passenger-car interior; it does not depict the successful refueling transaction at the eastern target.

**Observed locally — screenshot inspection:** the four supplied PNGs were successfully opened through `<LOCAL_SCREENSHOT_PATH>` despite the attachment loader's Windows-path errors. Ignoring the red/orange job route as requested:

| Original screenshot filename | Evidence visible / limit |
| --- | --- |
| `Zrzut ekranu 2026-10-17 200738 - ATS with Expansion - Helena - Gas Station for trucks.png` | Truck-map view shows a fuel icon in Helena and one on the road east of Helena. The user later recalled this was probably before sample installation, during the initial truck quick job; it is baseline evidence only. |
| `Zrzut ekranu 2026-10-17 200805 - ATS with Expansion - Helena - Gas Station for cars.png` | Baseline car-map view lacks both those fuel icons; other car fuel icons remain visible elsewhere. |
| `Zrzut ekranu 2026-10-17 201442 - ATS with expansion AND fix sample 1 - Helena - Gas stations for cars.png` | Patched car-map view adds the eastern icon while the city icon remains absent. Different crop/zoom prevents a literal pixel-diff comparison. |
| `ats_20261017_201959_00.png` | Passenger-car cockpit facing the city station forecourt and pumps. Physical-looking car access is visible; this frame alone does not prove a refueling interaction or exact prefab UID. |

Original images were read in place, not copied into Git. Ignored provenance report `local_outputs/research/validation/2026-10-17-helena-user-test.json` records paths, hashes, dimensions, captions, and limitations. The expected locally generated Helena-area sample SHA-256 is `05f3356ddccfd621c6c04407a384d3770893c75da1f15f8ad7525260c86ea97d`; the installed copy has not been fingerprinted. User captions and eastern map change agree with the prepared [Helena-area recipe](../../examples/helena-area-fuel-1.61.3.18.json).

### What this establishes

**Documented — user report plus screenshot comparison:** the first localized fuel experiment has a positive runtime result for one target. Its combined private-PPD/prefab/service modification is supported by an actual reported refuel, beyond merely adding a map icon. No separate editor operation was reported.

**Hypothesis strengthened:** PPD GAS flags `1` plus service bit `0x4000` are sufficient for the intended car interaction in this inspected single-pump case. The experiment changes both together; it does **not** establish that each individual change is necessary, that PPD-only modification fails, or that arbitrary stations can be fixed identically.

**Unknown / remaining validation:** measured fuel/payment change, truck behavior at the converted pump and unchanged controls, persistence after reload, exact effective runtime fingerprints, multi-pump conversion, other maps/versions, and courier behavior. Great Falls and Reforma candidates remain untested. A complete starting-city selector rule/list is still unknown; screenshots and a fresh profile near Helena are not an enumeration of that menu.

### Follow-up correction: patched truck-map visibility

**Documented — user correction, 2026-10-17:** the user recalls that the earlier truck-map screenshot was probably taken immediately after creating the profile, during the initial truck quick job before game-mode selection became available on that test profile. The sample had not yet been copied/installed. It must not be interpreted as evidence of truck visibility with the sample enabled.

The user now reports that **with the sample enabled, the tested eastern station is absent from the truck map and present only in the car map**. No additional truck-map screenshot or actual failed truck refueling was supplied with this correction. This is a user-reported follow-up observation, not an agent gameplay reproduction.

**Conclusion supported by the report:** the current sample changes map-mode classification/visibility rather than preserving visibility in both modes. It does not meet the desired both-mode visibility behavior. The original truck screenshot is consistent with the baseline; the car refueling success remains valid. **Unknown:** whether a truck can still physically interact/refuel at that point despite the missing icon. Do not convert icon absence into an observed fueling failure.

**Hypothesis strengthened:** overwriting the existing PPD GAS flags `0` → `1` and existing service flags `0x80000000` → `0x80004000` selects the car category for this target. Both fields were changed together, so their individual contributions remain unisolated. This still does not establish a universal fuel-flag specification.

The next experiment must aim for **car and truck service at the same physical pump**, not assume a forced division of the station's visible dispensers. First preserve this correction and separate map visibility from actual fueling. A bounded one-field-at-a-time experiment can investigate whether a shared setting exists; adding car interaction while retaining the original truck records is another unvalidated design option. Do not guess a new flag value or treat overlapping logical services as already supported. Keep transforms/physical pump positions unchanged and require successful refueling with both vehicles before calling a candidate dual-vehicle support.

### Requested next experiment: same-position pair

The user explicitly requested two interactions at exactly the same physical point, one for cars and one for trucks. [Sample 2](OVERLAPPING_FUEL_SAMPLE.md) now retains the original truck GAS/service/node and adds a car GAS/service/node with identical transform bytes. This is a new generated candidate; the positive car-refueling and truck-map-loss results above apply to sample 1 only. Runtime both-mode visibility/refueling remains pending in TASK-0007.

### Why the closer city station was not selected

**Observed locally:** the city station was recognized before this test and recorded as the unchanged truck control in the [starter-area guide](STARTER_AREA_SAMPLE.md). Its inspected fuel prefab is `1e00i`, UID `0x42dd66b86ad1d49f`, in `map/usa/sec-0016-0013.base`, approximately **344 map units** from the effective garage point. The PPD is `/prefab/gas/us_gas_gallonoil_truck_7rows_roof.ppd`, **version 25**, 2,204 bytes, with **four logical GAS locators, all flags 0**, and four matching linked service items, all flags `0x80000000`. These logical points are not a count of every visible dispenser in the whole forecourt. The screenshot's exact world coordinates were not supplied; assigning its visible car forecourt to an individual prefab/locator still needs a position check.

The selected eastern instance uses stock `02003`, a v25, 908-byte PPD with **one GAS locator and one linked service**. Its bounds centre is roughly 3,506 map units from the garage. The first generator explicitly supports only this reviewed single-point shape; its target was chosen by a pinned recipe, not by an automatic nearest-station search. See [implementation](../../src/ats_road_trip/local_fuel.py) and [design decision](../architecture/decisions/ADR-0003-allow-pinned-single-pump-sector-experiments.md).

**Selection limitation, not a diagnosed defect:** the nearer station was excluded to keep the first transformation unambiguous and leave a truck control. Its format is supported by the inspector; no older-format incompatibility or inherent inability to serve cars was demonstrated. Extending to multiple points requires associating the chosen locator(s) with the correct map service(s), maintaining instance-local scope, and explicitly preserving truck interactions at the other points. This requires separate design/verification, not blind conversion of every locator.

The original selection gave too much weight to prototype simplicity and too little to the user's driving route. Straight-line map proximity was documented but the actual road approach was not checked. The user's detour is now recorded evidence against calling the eastern target a convenient near-garage test. The city station is the next useful location after establishing how to retain truck service while adding car service. Match physical pumps, logical locators and map services, but do not assume that different physical dispensers must be reserved for different vehicle classes.

See active [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) for remaining comparisons. The original generated packages/reports are unchanged; their embedded `in_game_verified: false` describes generation-time status. This dated record carries subsequent external validation rather than rewriting the tested artifact.

## 2026-10-17: sample 2 both-mode refueling

**Documented — first-hand user report:** after the exact-overlap sample was supplied, the user stated that it works in both a passenger car and a truck. In this conversation this reports successful refueling at the already selected eastern Helena point. It supports the intended dual-vehicle behavior for this one fixture, superseding sample 2's earlier pending runtime status. It does not change the negative truck-map result for sample 1.

The expected supplied artifact is historical `ats-expansion-helena-overlapping-fuel-sample-2.scs`, SHA-256 `fe783c39547cb59980278db4e9c2314bf0c0983477480c47291f937b4c7b1347`, generated from ATS 1.61.3.18 / ATS Expansion 23.0. The installed copy and running build were not independently fingerprinted. Numerical fuel/payment changes, reload persistence and controls were not captured; no independent agent gameplay run occurred. The user-supplied `Zrzut ekranu 2026-10-17 212256.png` was inspected through WSL and shows sample-2 metadata in the mod manager, not a fuel transaction. Original images remain outside Git.

**Hypothesis supported for this fixture:** retaining the original truck locator/service/node and adding a car twin at identical transforms can provide both interactions at one physical dispenser. This is evidence for expanding the research, not proof of a universal multi-point or map-wide repair. Courier, Great Falls, Reforma and the nearer Helena city station remain untested.

The user then requested [consistent metadata and original icons](MOD_METADATA.md), selecting proposal C. The branded package's three gameplay resources are compared byte-for-byte to the historical tested sample. Subsequent metadata-only repackaging is an agent static check; the original user report remains attributed to the historical sample. Generated `in_game_verified: false` flags remain generation-time annotations and are not rewritten in tested historical outputs.
