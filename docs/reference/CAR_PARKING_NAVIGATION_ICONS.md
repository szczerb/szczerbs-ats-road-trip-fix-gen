# Passenger-car parking icons in vehicle navigation

**Status — candidate prepared for manual test, 2026-10-19.** ATS baseline: 1.61.3.18, executable SHA-256 `c60e8ee02cc97b3cc6ef8c6298bb5c3c23c4ffd330b8185b646fb1b608a3c7b4`. The candidate changes only the winning `def/map_data.sii` parking-category mask at the four close/far 3D-map/minimap tiers. It is not a confirmed navigation fix: the phone/dashboard tier binding and runtime result remain unknown.

## Evidence and surface boundaries

**User-reported — 2026-10-19:** variant B (`unmarked_geometry`) showed a parking icon on the full-screen map, but the user did not find a working rest position and did not see the icon in vehicle navigation. The earlier successful interaction is attributed to A (`painted_bays`). Whether A's icon appeared in either vehicle-navigation interface was not reported. The user's r9 full-screen-map icon confirmation in Alaska and Canada after checking two towns remains a separate, accepted result; this investigation does not revise it.

**Observed locally — installed ATS 1.61.3.18:** `def/map_data.sii` names indices 0–3 as close/far 3D map and minimap tiers; indices 4–7 are world-map tiers. The car-parking category is bit 25 (`0x02000000`). The category is enabled in cached stock data at indices 0–6 and omitted at index 7. The final active provider in the logged A session (also mounted after B at 00:03:44.865) is North America Background Map 5.3 (Workshop ID `3348711188`), whose `universal/def/map_data.sii` SHA-256 is `4d8d9bce1c8a73c387b10bc191fbde5249b7f4ea1ecacb912e5ffe1b08c4b189`. It sets indices 0–3 to `0x685FFF`, which omits bit 25; OR-ing only bit 25 produces `0x02685FFF`. The winning file also authors `player_size` and `road_size_factor`; these fields match the cached stock values and are not part of the proposed edit.

The logged mount order and active-resource inventory are in [the bounded map-data audit](../../local_outputs/work/2026-10-19_19-35-50/mapdata-inventory/active-map-data-inventory.md). That report's finding that the NA Background Map is the final textual provider is specific to the logged A session; the candidate generator verifies the pinned members of the supplied source directory, but does not inspect the live profile or establish the active provider on another session. Static masks do not prove which tier each navigation interface consumes.

**Observed locally — engine and UI resource inventory:** the installed executable contains map-filter and GPS UI strings plus references to separate large/small parking and gas materials. Stock trigger definitions map an independent `parking_car` action to the car marker category; mixed truck/bus/car triggers are classified truck/bus-first. These findings establish marker classification and available materials, not surface-specific visibility rules. Selective UI-path scans found no matching active mod UI-definition paths. Read-only notes and source limits are in [the UI-source review](../../local_outputs/work/2026-10-19_19-32-43/nav-icon-investigation/navigation-ui-source-notes.md).

The candidate does not alter marker actions, trigger records, locations, geometry, map sectors, prefab data, filters, or UI assets. Fuel uses a separate category bit (bit 24), which remains unchanged. Existing full-screen map results and original truck/bus interactions should therefore retain their current inputs, but only in-game comparison can confirm behavior.

**Unknown:** whether phone navigation or dashboard/infotainment GPS uses indices 0–3, what tier/zoom and category-filter state were active in the B report, whether native car parking appears in either interface, and whether A's marker appeared there. No positive native phone/GPS control has been reported. A visible icon does not establish physical access, a rest prompt, or fatigue recovery.

## Candidate and scope

**Hypothesis — targeted candidate, not proven cause:** the logged winner disables category 25 in all four local map/minimap tiers, despite stock enabling it. This setting could suppress car-parking markers on an interface that consumes one of those tiers. The engine evidence does not establish that phone or dashboard navigation does so, so N1 tests this possibility rather than diagnosing the cause. The user's B report that the icon appeared on the full-screen world map is also unresolved: the logged source masks omit category 25 at world tiers 4–7, although the exact tier used in the reported full-screen view is unknown. The user's observed visibility does not identify a confirmed tier or mechanism and is not explained by N1.

The prepared variant is **N1 NAV PARKING r1**: [generated archive](../../local_outputs/generated/2026-10-19_19-47-49/n1-nav-parking-north-america-background-5.3-ats-1.61-r1-experimental.scs), SHA-256 `97e36da9a440299ebe2f9e07b4aba65bd5f92dfda6e9b94a221865dbfd32c362`. It packages only `def/map_data.sii`, editing `map_items_flags[0..3]` in North America Background Map 5.3's `universal/def/map_data.sii`, changing each `0x00685FFF` value to `0x02685FFF`. The generated member is 3,236 bytes, SHA-256 `06d894fa5a64194f1af49ece89774045f07efb8d0f73eda171a7c8a11188c8ad`. The audit confirms indices 4–7 and all other source bytes are unchanged. The three SUI includes remain supplied by the original background map and are hash-pinned during generation; they are not copied into N1:

| Pinned source member | SHA-256 |
| --- | --- |
| `def/map_data.sii` | `4d8d9bce1c8a73c387b10bc191fbde5249b7f4ea1ecacb912e5ffe1b08c4b189` |
| `def/map_data/colour_data.sui` | `5e10afde98bba2b8ac8a27a78675460db4adb1616b6b1b38d1b25f15f4a20d68` |
| `def/map_data/full_detail_config.sui` | `a40907d58d685f485c43962078c649f53d5f41c60c5589ea4a91d09765eb9662` |
| `def/map_data/zoom_uplift_config.sui` | `e96c5384c23509e349242fcc5e777a36c724fad3aa5753b29ffb0325e3d3bb73` |

Fuel category bit 24 and geometry/trigger resources are unchanged. The generator pins these four source-member hashes and rejects source/version drift. Full package metadata and checks are in the [generation audit](../../local_outputs/work/2026-10-19_19-47-49/navigation-icons/audit.json).

Reproduce with the reviewed unpacked Workshop package root and declared build:

```bash
PYTHONPATH=src python3 -m ats_road_trip.navigation_icons \
  --source-package "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/270880/3348711188/universal" \
  --game-version 1.61.3.18 \
  --acknowledge-experimental
```

The command creates a new timestamped run; it refuses to overwrite an existing run. `--game-version` is caller-declared and does not inspect or launch the game.

Because the category mask is global, N1 may reveal category-25 parking icons throughout the map at those tiers, including native locations and r9 markers; it is not a Dawson-only change. It does not change the Alaska or WCE r9 resources. Enable N1 above North America Background Map, alongside exactly one unchanged station control package:

- **N0 control:** unchanged A LINES or B GEOMETRY, with the existing map stack and no N1.
- **N1 trial:** the same unchanged A LINES or B GEOMETRY and the same stack, plus N1 above North America Background Map.

For Dawson, A or B continues to replace Alaska r9 at Alaska's existing source-relative priority; WCE r9 stays directly above WCE. Alaska r2 is not a separate active package. The N1 overlay has the highest `map_data.sii` priority. A and B are alternatives because their sector edits replace the same Alaska sector; do not enable both. N1 can be tested with either unchanged control.

## Minimal manual comparison

Use the same copied/disposable profile, vehicle, location, zoom and category-filter state for each pass. Do not search elsewhere around the station. First capture N0 with the selected unchanged A or B control; then enable N1 in the stated position and repeat. Record phone navigation or built-in/dashboard navigation as available; these interfaces are distinct observations, and testing both is not required.

1. At the same location, inspect the full-screen map and the available vehicle-navigation interface (phone or built-in/dashboard GPS). Record each surface separately, including icon visibility at close and the next available zoom level, plus any parking-category filter state.
2. Record A or B icon visibility separately from the existing rest-interaction observation. If an interaction prompt appears during the controlled comparison, record it; do not conduct a new search for a B prompt. Do not infer rest access from the icon.
3. If a known native `parking_car` location is already convenient, record it as an optional positive control; no additional search is required.
4. Record any change to gas icons as a comparison only. The fuel-category bit is unchanged by N1.

If N1 changes visibility on a specific surface, that supports the relevance of the close-tier parking mask but still does not establish that every screen uses the same tier or that the candidate is suitable as a general fix. If no surface changes, the proposed mask is not sufficient evidence for a fix; preserve the interface/zoom/filter observations before investigating further.

## Source notes and limits

- **Documented:** SCS's [Basic Editor Functions](https://modding.scssoft.com/wiki/Tutorials/Map_Editor/Introduction_to_the_Map_Editor/Basic_Editor_Functions) distinguishes map overlays from trigger areas, but does not document ATS 1.61 phone/GPS tier selection.
- **Observed locally:** the earlier UI/source review used installed stock definitions and found no safe targeted change from that evidence alone. The later effective-provider inventory found the North America Background Map override, so that initial no-patch conclusion is superseded for this experiment by the specific N1 candidate. Neither static review maps phone/dashboard to a tier. Active session ordering and the background-map hashes are from the logged A-session inventory linked above. The supplied eleven-map sample was not the full runtime stack; the inventory checked active mod archives and the logged Workshop directory. It found no relevant UI-definition path, but filename scans cannot rule out engine behavior or assets under unrelated names.
- **Observed locally:** active Real Companies, Gas Stations & Billboards 4.02.01 replaces the tested station model. The replacement lacks the four base-model separators and includes locators for parked cars. The original supplied map set was not the complete runtime stack. This affects interpretation of station geometry and appearance, not evidence for the navigation mask.
- **Unknown:** precise phone/dashboard tier mapping, any shared filter state, and whether N1 changes the reported symptom. No game was launched, no mod installed, and no profile changed during static research or artifact preparation.


## Offline verification and completion boundary

**Observed locally — 2026-10-19:** all **332 tests** pass, including six navigation tests using original authored fixtures. Actual-archive inspection by GPT-6 Luna/high and a repeated root audit confirm four unique members and valid CRC; the only gameplay member is `def/map_data.sii`. Reversing its four token edits exactly recovers every original source byte. Both effective background + A/B + N1 stacks retain all 25 gameplay members per selected A/B control and all three included SUI resources byte-for-byte. Root parsed the effective SII with those includes: unit identity and all non-mask attributes are unchanged, with no attribute errors. [Executable payload check and results](../../local_outputs/work/2026-10-19_19-47-49/navigation-icons/payload-audit.json), [full-test output](../../local_outputs/work/2026-10-19_19-47-49/navigation-icons/full-tests.txt).

The source-only reorganization is separately committed as `7eea2cf`; its exact-input comparisons remain unchanged. [TASK-0041](../tasks/done/TASK-0041-refactor-station-parking-and-investigate-navigation-icons.md) closes the static restructuring/research/candidate handoff. [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) retains runtime follow-up. No confirmed navigation fix, geometry improvement, new parking area or full-map coverage result is claimed.
