# Missing passenger-car parking icons

Inspected: 2026-10-18. Baseline ATS 1.61.3.18; original supplied sources and r8 packages remain unchanged. [TASK-0038](../tasks/active/TASK-0038-investigate-missing-car-parking-icons.md) implements a source-specific r9 repair; in-game rendering remains unverified.

## Resolved static cause

**Observed locally — installed executable, independently confirmed:** both prefab and standalone parking marker builders prefer a truck/bus category when a rest action permits both large vehicles and cars. R8's private action lists `truck`, `bus`, `car`, so this marker path selects the large-vehicle category and does not create the separate car category. Physical car activation is checked separately; absent icons do not prove rest itself failed.

Root and GPT-6 Sol/high independently inspected `amtrucks.exe`, SHA-256 `c60e8ee02cc97b3cc6ef8c6298bb5c3c23c4ffd330b8185b646fb1b608a3c7b4`, without launching or modifying it. The prefab branch at virtual addresses `0x141004ee7`–`0x141004f39` checks mask 3 before mask 4, selecting marker category 7 before category 25. The standalone branch at `0x140fffe8b`–`0x140fffebc` has the same preference across the item's actions. The called vehicle matcher resolves HUD command/parameters dynamically, ruling against private action spelling as the cause. These addresses are evidence for this exact executable, not a portable patch interface.

The same binary labels Parking overlays obsolete and directs authors to parking triggers. Scans of the supplied sectors found no Parking overlays, further supporting a trigger-based repair. No vehicle bit is transferred from fuel services.

**Decision / implementation:** [ADR-0017](../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md) replaces the mixed-action approach with separate native `parking_car` twins. Original truck groups/items and shared definitions remain intact. Selected PPDs gain independent groups with new IDs and neighbors; standalone rest areas gain separate Trigger items/nodes with exact geometry, flags, radius and tags. Visibility/layer links are copied. The 1,000-unit rule still governs new permissions; repair of an already mixed car-enabled area is separately counted and adds no new physical eligibility.

**Unknown — runtime:** actual rendered car icons, fatigue recovery, truck controls and save/reload behavior after r9. Marker categories' exact UI assets were not symbolically identified; the classification follows verified mode branches. No game operation or live installation is part of this investigation.

## Concrete placed comparisons

**Observed locally — 2026-10-18, selectively read original source sectors:** these are actual placed Trigger items with resolved world nodes, not merely available descriptors. The two native examples use car-only `parking_car`; all listed actions use default definition parameters. The native examples illustrate the regional source data, without claiming an exact screenshot pixel match.

| Source / role | Sector under `map/usa/` | Trigger UID | Flags | Action / result |
| --- | --- | --- | --- | --- |
| Washington DLC, native car rest | `sec-0021-0017.base` | `0x5c1ffc1422050000` | `0x504` | `parking_car`; independent car-only marker category |
| Reforma 3.0.1.161, native car rest | `sec-0005+0016.base` | `0x5ed39864ee8b0000` | `0x0c` | `parking_car`; original neighbor 188.13 units from a reported truck rest |
| Western Canada Expansion 1.7.3, source truck rest | `sec-0009-0014.base` | `0x42dd66b82011660f` | `0x0d` | Original `hud_parking`; r8 kept geometry/UID but retargeted to mixed `rta428376f4`, triggering the truck-first marker branch |

Root reviewed GPT-6 Luna/medium's exact sector/record hashes, action parameters, node lists and coordinates in `placed-standalone-comparison.json`. Separate selected PPD comparisons cover Alaska prefab UID `0x5e6d3218a2000001` and WCE UID `0x5bd0c12d09800001`: their r8 polygons also carry mixed private actions with unchanged original shape/flags/range. The private prefab alias (`rtr...`) and private action alias (`rta...`) are distinct identities; the inventory's initial textual conflation was corrected against encoded tokens.

## Report and evidence correction

**Documented — user report:** no car-mode parking icons in Canada or Alaska, sparse Montana coverage, with r8 installed. The user has not visited those parking locations to test rest and is completing a job in Mexico. The earlier general rest-success report may have been a mistaken late-night check. Rest availability is therefore uncertain again; refueling and separate job/tank reports are not retracted.

**Observed locally / user-corrected geography:** screenshot `ats_20261018_232603_00.png` shows bed icons in Washington, USA, and none north of the Canadian border at the shown zoom. The initial agent description placing those icons in southern British Columbia was wrong. Alaska is offscreen, and the visible Montana fragment does not establish statewide coverage.

**Observed locally — second screenshot:** `ats_20261018_232848_00.png` shows dense bed icons across Mexico and substantial southern-US coverage. **Hypothesis — user:** all map fixes except Reforma may be affected. These images establish a regional contrast, not every package's failure or the provenance of each visible icon.

## Static checks

**Observed locally:** all seven installed r8 map archives match the delivered files by SHA-256. Their entire gameplay resource inventories (`map/`, `prefab/`, `def/`) match r7 byte-for-byte. The log created at 22:49:31 lists every r8 fix active in the expected source-relative order. This is evidence against an r8 payload regression, not proof the preceding rest implementation worked or that no higher mod affects rendering.

**Observed locally:** rest reports retain the expected per-package additions: Alaska 31, Western Canada 202, ProMods 95, connector 41, ATS Expansion 766, Reforma 119. These are modified rest polygons, not map symbols or unique surviving locations. Source ownership also limits coverage: stock Montana sectors are not automatically processed merely because ATS Expansion modifies other sectors in that state.

**Observed locally:** the Reforma rest report found 1,342 existing car rest locations within its source-plus-halo inventory and suppressed 961 truck-polygon edits because of nearby original car locations. Alaska's corresponding inventory found zero existing car rests and selected all 31 truck polygons. These are different inspection regions and include neighboring packages; they are not source-only or directly comparable regional densities. **Hypothesis:** native car-rest locations could account for visible Mexican icons even if our added permissions fail to acquire markers. The screenshot does not establish the 119 Reforma additions' visibility or successful rest.

**Observed locally:** a read-only scan of the eleven logged higher-priority Workshop package directories found no exact collisions with r8 sector paths, private descriptors or private definitions. The sole opaque `No DeadEnds!` archive was separately listed with the HashFS adapter and has no map/world/private-descriptor paths. This bounded path scan does not verify all underlying descriptor semantics or the engine's filtering behavior.

**Observed locally:** `rest_stops.py` changes selected PPD/standalone action tokens to private actions with `hud_activate`, parameter 3, and truck/bus/car strings. It preserves original geometry and does not explicitly create parking services or map overlays. Both stock and private actions retain the “Parking - Large vehicles” display label. Five log messages reject a parking action for car mode; without tokens, UIDs or coordinates they do not identify a failed generated location.

## Marker mechanism: established and unknown

**Documented — shared engine authoring model:** SCS describes Map Overlay items as map icons/landmarks/text and Trigger items as interaction regions, including sleeping areas. This 2024 editor overview does not specify ATS 1.61 car-mode filtering. [SCS editor documentation](https://modding.scssoft.com/wiki/Tutorials/Map_Editor/Introduction_to_the_Map_Editor/Basic_Editor_Functions).

**Documented — independent parser model, inspected 2026-10-18:** TruckLib distinguishes Parking overlays (type 1), Parking services (type 4) and prefab Parking spawns (type 10). Its overlay class exposes type, DLC guard, discovery and zoom fields, without a named car-mode property. This is not a complete engine specification. [MapOverlay source](https://raw.githubusercontent.com/sk-zk/TruckLib/master/TruckLib/ScsMap/MapOverlay.cs), [enums](https://raw.githubusercontent.com/sk-zk/TruckLib/master/TruckLib/ScsMap/Enums.cs), [service creation](https://raw.githubusercontent.com/sk-zk/TruckLib/master/TruckLib/ScsMap/PrefabCreator.cs).

**Observed locally — delegated recheck of historical inventory:** sampled supplied-map Parking services do not carry fuel's `0x4000` bit. Parking service counts are Alaska 6, ATS Expansion 35, Western Canada 27, Reforma 70, ProMods 4 and connector 0. These samples do not establish a parking visibility bit or all rest locations. The earlier [rest research](PASSENGER_CAR_REST_RESEARCH.md) explicitly cautions against transferring the fuel bit to parking.

**Historical hypothesis, now resolved statically above:** the action-only approach lacked a separate car-map marker classification. Custom action identity was investigated but is not the cause supported by the executable's dynamic matcher.

**Observed locally:** r7 and r8 share the defective mixed-action marker structure, so the problem predates r8's metadata refresh. **Unknown:** whether physical rest failed at a particular visited site, and final runtime rendering after the repair. Do not infer physical rest failure from marker classification alone.

## Reproduction artifacts

Ignored `local_outputs/work/2026-10-18_23-24-54/` contains the log snapshot, seven embedded reports, `package-audit.json`, `rest-coverage.json` and screenshot fingerprint/corrected observation. Original screenshot remains outside the repository. GPT-6 Luna / high performed bounded read-only implementation and primary-source research; root reviewed findings, exact archive equality, log and screenshot. No live installation, profile changes, game operation or replacement package was performed.

Subsequent authorized implementation evidence: root's `local_outputs/work/2026-10-18_23-37-08/engine-evidence.json` and bounded executable-inspection excerpts; independent GPT-6 Sol/high evidence under `local_outputs/work/2026-10-18_23-37-00/mechanism/`; paired inventory under `local_outputs/work/2026-10-18_23-37-37/parking-inventory/`; final generation/audits under `local_outputs/work/2026-10-18_23-48-10/`. Large binary excerpts and generated resources remain ignored.
