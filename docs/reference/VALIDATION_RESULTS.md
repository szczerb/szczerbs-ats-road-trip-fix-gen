# Gameplay validation results

## 2026-10-19: r9 parking icons confirmed in Alaska and Canada

**Documented — first-hand maintainer report:** after the r9 handoff, the maintainer reports successful verification in Alaska and Canada, limited to **two towns**, and says the map is now also “pretty full.” This confirms the parking-icon repair in game at the reported scope and adds a broader visual observation of denser icon coverage. The maintainer explicitly authorizes committing and pushing the work.

The towns, exact installed hashes/running build, individual rest-prompt/fatigue-recovery steps, truck/bus controls and reload results were not enumerated. Do not infer complete regional coverage or those separate outcomes. The generation baseline remains ATS 1.61.3.18. The agent did not run ATS, install mods or modify a profile. Preserve the tested r9 artifacts and their generation-time reports unchanged; this dated record carries the subsequent user validation. [R9 handoff](MOD_REST_MARKERS_1_61_R9.md).

## 2026-10-19: r9 parking-marker repair statically verified; runtime pending

**Historical handoff status:** the subsequent [two-town user report](#2026-10-19-r9-parking-icons-confirmed-in-alaska-and-canada) above supersedes this section’s initial lack of runtime icon evidence. Other individually unreported outcomes remain separate.

**Observed locally — static implementation finding:** the map marker issue is traced to the mixed rest action being classified truck-first for marker discovery. Native car-rest sites use car-only `parking_car` actions. The r9 candidate adds those car twins while retaining the original truck triggers. Its static test suite reports **281 passing tests**.

**Observed locally — package verification:** final independent seven-archive and effective-stack audits pass; the local r9 batch is ready for a later game test. No game launch, installation or profile operation was performed for this work. At the time of that handoff, no r9 in-game icon, prompt, fatigue-recovery, truck-control or reload result had been reported; the subsequent two-town icon result above supersedes that status for icons. The [r9 marker handoff](MOD_REST_MARKERS_1_61_R9.md) records the audited output and technical evidence.

The later icon report continues to qualify the earlier general rest-success report below: physical rest remains unconfirmed. When convenient, test final audited r9 packages on a copied profile in Canada, Alaska and mod-covered Montana. At one selected location, record the car map icon, actual prompt and fatigue recovery separately; also check a truck parking control and repeat icon/access checks after reload. Do not interrupt the user's current job. Refueling access in Canada and Mexico remains independently user-confirmed; numerical prices, quantities and billing are not thereby inferred. Job Types Compat r3 and tank r0 are separate accepted packages and are unchanged by this rest work. The Western Canada ProMods Connections Mod Manager icon also remains runtime-unknown for its exact r9 package filename.

## 2026-10-18: missing car parking icons and qualified rest report

**Documented — subsequent first-hand user clarification:** car-mode world-map parking icons are missing in Canada and Alaska and sparse in Montana, despite installed r8. The user has not tested physical rest there and is completing a job in Mexico. They explicitly question the earlier late-night general rest-success report; rest confidence is reopened, without declaring a physical rest failure. Refueling, jobs and tank reports remain separate.

**Observed locally / corrected by user:** screenshot `ats_20261018_232603_00.png` shows bed icons in Washington, USA, and none north of the Canadian border at the shown zoom. The agent initially misidentified Washington as southern British Columbia; that reading is corrected. Montana's sparse icons help explain the misleading shape of the visible cluster; Alaska is offscreen.

**Observed locally:** second screenshot `ats_20261018_232848_00.png` shows dense icons across Mexico. **Hypothesis — user:** every fix except Reforma may be affected. Existing native car locations may contribute those icons; this does not validate generated Reforma rest additions or every other package's failure.

**Observed locally:** all seven installed r8 map archives match the delivered SHA-256 fingerprints, with gameplay resources identical to r7 and expected source-relative active order in the 22:49:31 log. These checks do not establish successful rest or icon display. [Investigation and remaining unknowns](CAR_PARKING_ICON_INVESTIGATION.md), [TASK-0038](../tasks/done/TASK-0038-investigate-missing-car-parking-icons.md). No immediate in-game test is requested and no profile/package was changed.

## 2026-10-18: updated job and tank packages work in game

**Documented — first-hand maintainer report:** after receiving the updated jobs r3 and tanks r0 publication packages, the maintainer manually updated the local installation, launched ATS and reported that they work. The report concerns the prepared copies recorded in [TASK-0036](../tasks/done/TASK-0036-prepare-report-free-publication-packages.md). The agent did not launch the game or inspect the live profile.

This confirms operation at the maintainer-reported scope. It does not enumerate the running build, active load order, installed-copy fingerprints, individual completed deliveries, cargo fit, measured capacity displays, billing or save/reload outcomes. The generation baseline remains ATS 1.61.3.18; it is not a newly measured runtime version. Prior tank acceptance and Canada/Mexico refueling confirmation remain valid; the later clarification above qualifies the rest report. More detailed checks retain their separate status in TASK-0007.

## 2026-10-18: refueling and rest confirmed in Canada and Mexico

**Later qualification:** the user questions the rest portion of this late-night report; [the subsequent icon report](#2026-10-18-missing-car-parking-icons-and-qualified-rest-report) is the current evidence. The original report below is retained as history.

**Documented — first-hand user report:** the user confirms that refueling and parking/rest also work in both Canada and Mexico. This adds positive runtime evidence for the generated map fuel/rest fixes in both regions. Following the user's internal-completion decision, the functional refueling-access and rest milestones are accepted at this reported scope; community testing can broaden coverage.

The prepared map handoff is [r8](MOD_METADATA_MAP_NAMES_1_61_R8_R3.md), but the exact installed filenames/hashes, individual stations/parking areas and running versions were not supplied with this report. It does not enumerate petrol prices, initial/filled quantities, charged amounts, truck/bus controls or save/reload. Do not turn the general success report into separate numerical billing validation or a claim that every location was tested. The earlier Canadian zero-price/invalid-quantity observation remains historical evidence; its detailed UI/accounting retest is not individually described here.

No agent gameplay run, installation or profile modification occurred. Existing packages and their generation-time reports remain unchanged. Tank upgrades already have separate user acceptance; courier delivery and the connector-icon result retain their existing status.

## 2026-10-18: tank upgrades accepted internally

**Documented — first-hand user report:** directly after the reasonable gas tank upgrades r0 handoff, the user confirms that everything works and explicitly considers it internally done. They plan to propose it to other people for testing. This closes internal tank validation; community feedback is a possible next stage rather than a blocker.

The prepared candidate is [reasonable gas tank upgrades r0](REASONABLE_GAS_TANK_UPGRADES.md#verified-r0-handoff), SHA-256 `95bf7495c1274917ac1eccd5b13b367ce66376b363a884629a649ce99b51dc5e`. The report does not enumerate tested models, measured capacities, saved-fuel migration, price/payment or save/reload results, and the installed copy was not independently fingerprinted. No additional agent gameplay test occurred. Preserve the tested package and its generation-time report unchanged. This acceptance concerns the tank mod; separate Canadian fuel-price, rest, courier and connector-icon checks retain their existing evidence/status.

## 2026-10-18: ongoing USA courier testing

**Documented — first-hand user report:** the user is still testing Job Types Compat Mustang in the USA and has noticed no problems so far. They will report when finished. This is an interim observation, not confirmation of completed new-job acceptance/delivery, all job families or a controlled live-offer comparison. Canada fuel quantities/prices/billing and car rest remain pending. No additional screenshot, installed-package fingerprint or agent gameplay test accompanied this report.

The user also reports an active 3x Ford fuel-capacity mod, which they intend to disable before the new [reasonable tank upgrade](REASONABLE_GAS_TANK_UPGRADES.md) test. Fuel observations during this courier session must retain that extra mod as a setup variable. No capacity-change runtime result has been reported; TASK-0007 remains active.

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

## 2026-10-18: Canadian r1 refueling and invalid quantity display

**Documented — first-hand user report:** after driving around Canada for approximately an hour and visiting many stations in both ProMods Canada and Western Canada areas, the user reports that passenger-car refueling works. The gallon display is invalid in Canada; returning to the USA restores a normal initial zero. This is broader reported runtime evidence for car station access, not a complete map-wide or truck-mode validation. No exact visited-station list, measured tank changes, payment changes or reload comparison was supplied.

**Observed locally — screenshot inspection:** `ats_20261018_001621_00.png` was read in place at original resolution through `<LOCAL_ATS_SCREENSHOT_DIR>/`. It shows a passenger-car cockpit at a branded forecourt, a refuel-button prompt, `Cena paliwa: $0,00`, `Galony: -nan(ind)` and `Suma: $0`. These are exact visible UI values. The image does not independently establish the fuel level, completed transaction amount, station UID or province/country unit. SHA-256: `c6a7baae037760f658b24f9b42af638c73b80a1f8b152af7ae6dd26d07c3aec7`.

**Observed locally — later-session context:** the available game log starts at 00:20:38, after the screenshot's 00:16:21 timestamp. It identifies ATS 1.61.3.18, records 29 active mods and confirms Western Canada ProMods Connections above ProMods Definitions. All six installed r1 fix archives match the delivered files byte-for-byte when inspected. This supports the later installed setup; it does not reconstruct the screenshot session exactly. No targeted price-attribute/NaN diagnostic appears in that log. Other active fuel/vehicle/UI-related mods have not all been inspected.

**Observed locally — source comparison:** ProMods Definitions 1.6.4 supplies `petrol_price: 1.502116` in `def/country/bc.sui`, but the higher-priority connection archive replaces that same file with a definition lacking `petrol_price`. Western Canada's six province definitions also omit it. The six generated r1 fixes contain no country or economy definition overrides. Exact values, source winners, primary references and competing hypotheses are in [the Canadian display research](CANADA_FUEL_DISPLAY_RESEARCH.md).

**Hypothesis, strong:** the omitted petrol prices explain the zero unit price and invalid calculation, separately from functioning station access. The exact engine default and arithmetic remain unverified. A same-station BC test adding only the existing ProMods petrol price to the winning connector definition can discriminate this explanation without changing station records or diesel prices. No experimental price patch was generated or installed during this research.

Ignored evidence snapshots and installed-output fingerprints are under `local_outputs/work/2026-10-18_01-04-41/canada-ui-root/`. Original screenshots, game files, logs, saves and historical generated artifacts were not modified. [TASK-0013](../tasks/done/TASK-0013-investigate-canadian-fuel-nan-display.md) records the completed research; [TASK-0014](../tasks/done/TASK-0014-audit-and-test-petrol-price-overrides.md) scopes the implementation/test follow-up. TASK-0007 remains active for runtime validation.

## 2026-10-19 Dawson single-station PoC interaction

**Documented — user report; observed locally — matching screenshot/log event:** the user installed both r0 alternatives but switched activation individually in Mod Manager. One trial showed a full-screen map icon without a found rest position; the second exposed an interaction on the building-side dark asphalt. The supplied `ats_20261019_182957_00.png` is explicitly recorded during the **painted_bays / A LINES** gameplay session, with small-vehicle parking actions shortly before capture. Both installed archive hashes match the original handoff. The image itself asks to switch off the engine; completed rest or fatigue recovery is not separately established.

The active Real companies visual mod replaces the base station model and lacks the detected car-bay marking cluster, so the algorithm's source-model lines should not be treated as visible painted bays in this profile. The geometry alternative's no-position-found outcome does not prove the trigger has no usable position anywhere. [Dated evidence, exact log chronology, model comparison and metadata-only labelled copies](GAS_STATION_CAR_REST_FEEDBACK_2026_10_19.md). No new fatigue/reload/fuel/truck result or coverage beyond this station is inferred.
