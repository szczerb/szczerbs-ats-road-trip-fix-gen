# Missing passenger-car parking icons

Inspected: 2026-10-18. Baseline ATS 1.61.3.18; supplied source versions and r8 handoff remain unchanged. [TASK-0038](../tasks/active/TASK-0038-investigate-missing-car-parking-icons.md) remains active.

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

**Hypothesis:** the generated action-only rest approach may lack a car-map discovery/marker component, or the engine may recognize original action identities differently from custom aliases. Neither cause is proven. Missing explicit marker edits does not establish how the engine derives every icon.

**Unknown:** exact vehicle-mode icon filtering, whether missing icons also mean unusable rest, and whether this behavior predates r8. A stock car-rest versus source/generated rest comparison must identify the relevant marker/action records before a supported change is possible. Do not add guessed flags or synthetic icons that imply unverified rest access.

## Reproduction artifacts

Ignored `local_outputs/work/2026-10-18_23-24-54/` contains the log snapshot, seven embedded reports, `package-audit.json`, `rest-coverage.json` and screenshot fingerprint/corrected observation. Original screenshot remains outside the repository. GPT-6 Luna / high performed bounded read-only implementation and primary-source research; root reviewed findings, exact archive equality, log and screenshot. No live installation, profile changes, game operation or replacement package was performed.
