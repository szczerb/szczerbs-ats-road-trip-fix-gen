# North America background 1.61-r3-experimental

**Observed locally, 2026-10-25:** r3 is ready for the user's manual testing. The offline gate finds material road/shore improvements in **8 of 11 independently catalogued problem groups**, with all 25 supplied views accounted for. This is a substantial partial repair, not a claim that every coastline is correct. Haida Gwaii, Gulf-delta and Texas/harbor relationships remain unresolved or mixed.

## Authoritative files

Enable only this SCS:

- [R3 testing mod](../../local_outputs/generated/2026-10-25_07-07-39/szczerbs-road-trip-north-america-background-map-ats-1.61-r3-experimental.scs) — SHA-256 `8d29a9531e4ffab939f11891042e3a5fc2260310d7919eae83797f0329be9329`.
- [Corresponding source ZIP](../../local_outputs/generated/2026-10-25_07-07-39/szczerbs-road-trip-north-america-background-1.61-r3-source.zip) — SHA-256 `e231a2e2f4dae05501e90b74cc0edc2d9041f3b7b8262e089fb8b3e4937ca2d9`; source snapshot `bd613b7d14580996d9ae26400bf8398d26185ec8`.
- [All 25 original/comparison views](../../local_outputs/generated/2026-10-25_07-07-39/comparisons/gallery.html), [overall/regional previews](../../local_outputs/generated/2026-10-25_07-07-39/previews/index.html), [per-view results](../../local_outputs/generated/2026-10-25_07-07-39/validation-summary.json), [checksums](../../local_outputs/generated/2026-10-25_07-07-39/SHA256SUMS.txt).

The source ZIP is source, not another mod. The repeat directory `2026-10-25_07-07-40` and extracted-source build are reproduction evidence. The earlier `06-22-47` r3 candidate is explicitly **not selected**. Historical r0/r1/r2 files remain unchanged fallbacks.

## Installation and manual trial

Place r3 above every background/map-data override, including Reforma OtherMaps Patch, ProMods definitions and Reforma ProMods Background Fix. Disable other background maps, the former North America Background Map 5.3, N1/N2 and older r0/r1/r2 background versions. Keep source maps and their separate fuel/rest/courier/tank fixes in their existing relative order below it. The background requires ATS 1.61 and introduces no Ford DLC dependency; map expansions retain their own requirements.

During normal play, revisit the reported coastal/lake areas and compare the main road/shore relationships. The largest visible gains include Los Barriles/Loreto, LA, Santa Cruz/SF, Newport, Chicago and the Canadian lake approaches. Some Vancouver-area approaches improve substantially while port/interchange loops still need work. Treat true bridges and piers separately from dry roads. Watch rendering and performance: the four 8192-square BGRA8 tiles contain **1 GiB uncompressed high-resolution pixel data**, four times r2's high-resolution payload. Actual engine memory use and performance are untested.

The user already confirmed usable r2 job-market zoom and car fuel/parking navigation icons. R3 preserves the **entire 4391-byte `def/map_data.sii` byte for byte**, including `zoom_uplift[7]=60000`, every other tier, camera/bounds data and navigation mask. Another initial zoom/icon confirmation is unnecessary. No game was launched, live mod installed, profile/save changed or economy reset during this work. Runtime acceptance remains the user's.

## Cause and repair

**Observed locally:** a single enlargement trades southern California against Baja. Settlement-to-CityArea calibration and route-normal matching cannot describe expanded urban footprints or regional map-mod distortion. Earlier large aggregate scores hid the same conspicuous source-road conflicts. This does not prove every remaining offset shares one cause.

R3 uses finer public GSHHG coast geometry and archived USGS NHD Lake Michigan geometry, coherent all-layer feature transport, and source-qualified street/site ground constraints. Five feature flows retain 17 fitting correspondences; seven semantic checks remain excluded from fitting. Four Galveston observations are retained as retired diagnostics: their former flow matched points while distorting the surrounding islands and flooding ordinary roads. A controlled ablation removed that failure.

The selected 64-stage compact composition preserves the successful 32-field global correction, adds 16 Puerto-only increments, then eight local increments at each of two existing FIT industrial points. A full global refit had regressed distant Texas roads, so the verified global mapping was frozen. The final Texas validation window is pixel-identical to the successful ablation, including all 60 listed point values. All geographic layers share the same mapping; playable roads and sectors are not edited, and no generic land buffer or traced native artwork is used.

The two industrial qualifications use actual source geometry: La Paz's point lies on an asphalt mesh triangle; Oakland's point follows a near-straight PPD vehicle-path chord with adjacent paved-road support, while no static model triangle directly covers that point. Final continuous-q edge distances are 8.30 game units water-side at Oakland and 8.52 land-side at La Paz. Neither is a surveyed shoreline. A separate floor-triangle centroid survey finds edge intersection at Oakland (36.21% area-weighted centroid proxy) and La Paz (1.02%); **whole-floor preservation is not claimed**. These are sampled area proxies, not exact polygon-overlap measurements; no new sampled centroid loss exceeded 150 units.

## Per-view result

Every original and paired view is linked from the gallery. Repeated images share 11 problem groups, so overlapping views do not count as independent wins. All 23 registered comparisons use unchanged canonical full-screen matrices and native image geometry; two weak frames use fixed native-world contexts, without invented screenshot transforms. Main inspected all 25 bounded comparisons plus full 447/524 frames. Raw-mask identity proves 21 registered viewports and both weak crops unchanged in the final refinement; main separately inspected the two changed full views/ROIs 340 and 506.

| View | Location | R3 result and remaining limit |
| --- | --- | --- |
| 000340 | La Paz–Los Barriles | **materially improved** — Los Barriles town/south road now land; La Paz paved spawn repaired to land. Harbor/island approaches remain uncertain. |
| 000349 | Ciudad Insurgentes–Ciudad Constitución–Puerto San Carlos | **materially improved** — Qualified Puerto central streets/approaches improve; 27 of 55 source-road points change water→land. Western port grid remains mixed; one held road point is 10.21 units water-side. |
| 000357 | Loreto | **materially improved** — Loreto coast road and curves largely mainland-side; Carmen remains a separate public source island. Small port parts remain uncertain. |
| 000407 | Bahía Tortugas–Guerrero Negro, Pacific coast of Baja California | **materially improved** — Bahia Tortugas central/south street grid gains land. Northern semicircular loop remains water; its entire footprint is not proven dry by the short qualified connector. |
| 000417 | San Felipe–Puerto Peñasco | **materially improved** — Fixed-world context shows Puerto Penasco city-grid gains; San Felipe remains mixed. Screenshot is unregistered; no screen-pixel score. |
| 000429 | Tijuana–Tecate | **materially improved** — Main Rosarito/Tijuana coastal curve gains land; several western local loops remain wet. |
| 000435 | San Diego | **materially improved** — Fixed-world context improves San Diego mainland approach; Coronado remains partly wet. Screenshot unregistered; bridge chord is not a bank survey. |
| 000441 | Los Angeles | **materially improved** — Large LA freeway/city area gains mainland. Harbor/deck/pier relationships remain partial; do not dry every crossing. |
| 000447 | Oxnard | **materially improved** — Full view, not empty-land frozen ROI, shows south Oxnard coast-road gains. Western coast freeway still partly wet. |
| 000500 | Santa Cruz | **materially improved** — Santa Cruz coast-parallel road now land where r2 was offshore. |
| 000506 | San Francisco–Oakland–San Jose | **materially improved** — Long southwest SF coastal route now land; bay/city compromise remains. Oakland access q stays 8.30 units raster-water; floor-area centroid proxy shows edge intersection, not full pavement preservation. |
| 000513 | Eureka | **unchanged** — Eureka harbor-side city grid remains wet/mixed; outline detail alone is not counted as repair. |
| 000520 | Newport, Oregon | **materially improved** — Newport coastal interchange/road now mainland-side rather than offshore. |
| 000524 | Astoria–Longview / Columbia River mouth | **uncertain** — Columbia estuary has new detail/approach changes, but bank/bridge/port relationships are not fully qualified; no repair counted from detail alone. |
| 000538 | Victoria–Port Angeles–Everett/Seattle | **materially improved** — Seattle/Everett site/approach gains retain independent markers and ground constraints; residual factory-edge/estuary conflicts remain. Site checks correlate with fitting features. |
| 000548 | Vancouver–lower mainland / Bellingham | **materially improved** — Northern Vancouver shore/city gains; western Delta/Surrey bay-road/crossing remains uncertain and partly wet. |
| 000553 | Nanaimo–Vancouver–Courtenay/Squamish overview | **materially improved** — Horseshoe Bay upper main approach gains land substantially. Central interchange/port loops remain water; not a full port repair. |
| 000606 | Port Clements | **unchanged** — Port Clements/Haida coast-parallel road remains a conspicuous held-out conflict. All its held road rows stay checks. |
| 000640 | Yellowknife / Great Slave Lake | **materially improved** — Large Yellowknife curve shifts from lake to mainland; a few qualified FIT road samples and upper port/floor parts remain wet. |
| 000655 | Split Lake–Sundance corridor | **materially improved** — Split Lake road is dry while lake shape/area is preserved. Rigid source placement is not a native wet-bank survey. |
| 000735 | Chicago / Lake Michigan | **materially improved** — Chicago lake-shore roadway/urban strip gains land; northern rest/wharfs and true piers remain separately uncertain. |
| 000748 | New Orleans / Lake Pontchartrain | **unchanged** — New Orleans freeway/interchanges still overlap lake. Some crossings may be bridges, but that does not qualify every interchange as water. |
| 000756 | Lafayette–Houma | **uncertain** — Lafayette/Houma industrial loops remain partly water; wetlands and possible decks are not a blanket ground exemption. |
| 000808 | Houston–Galveston | **uncertain** — Galveston failed flow retired. Qualified city-road window returns to ablation; some small edge losses remain and broader city/port/causeway mismatch persists. Not a group repair win. |
| 000817 | Corpus Christi | **unchanged** — Corpus bay turn/approach remains a held-out ground conflict; nearby bridge parts were excluded from dry-ground claims. |

## Checks, regressions and uncertainty

**Observed locally:** 326 tests pass. Independent archive/resource/texture, source-priority, role, native-mask and source-geometry audits support the offline result. The frozen 6432 source rows remain 5030 FIT/1402 CHECK: original 6057 retain 4760/1297; original 320 retain 232/88; late Puerto 55 retain 38/17. No CHECK was fitted or moved. The Puerto selection followed discovery of a regression, and multiple candidate/check results informed model selection, so these are reused diagnostics rather than blind validation. Everett/SeaTac site checks correlate with fitting landmarks; overlapping source windows limit geographic independence. The 60 Galveston street points were never passed to fitting.

Canonical mask distances use the unchanged native XZ, floor cell, continuous pixel coordinates and nearest 3×3 morphological-edge pixel, positive water/negative land. An earlier opposite-class-cell-center diagnostic was retired after main caught the discrepancy. At the final raster, 301 q rows change water→land and 27 land→water; only three losses exceed 50 units and none exceed 100/150. All six CHECK land→water changes are at most 30.52 units. This supports the visual gate; it is not an all-roads-must-be-land rule or a substitute for it.

Selected source polygons: 131 public island/lake shapes plus Split Lake remain valid, with no selected polygon area changing beyond 30%. A separate five-polygon local audit also remains valid. Split Lake area changes −0.0152%. These preserve source coherence, not observed native wet banks. The full feature guard samples 443329 points: determinant 0.0889–171.5965, maximum linear stretch 20.7314, maximum inverse cycle 0.000106 units. Independent physical-chain sampling covers 256851 points, determinant 0.4103–1.7107, maximum stretch 2.0793. These are sampled numerical checks, **not continuous proofs**.

Bounded earlier-region road screens still show regressions: Alaska/Yukon samples over 50/150 units change 33/7→55/13 (max 193→205); Brownsville 15/5→19/6 (max 183→186). These include unclassified crossing contexts and do not prove every sample should be dry. Mobridge improves 25→2 over 50 units (max 122→68); Canadian lake-belt 55→18; North Pacific/BC 852→377 over 150 units (max 1212→348); Yellowknife 27→6 (max 440→195). Alaska panhandle has no over 50/150 sample either version. Shallow/source-detail changes and incomplete regional coverage remain explicit.

Separate two-dimensional landmark errors improve in six of seven held semantic references; Port Angeles ferry worsens slightly. Important residuals remain even where the native point's raster cell is land. City/model centers and geographic site points are approximate correspondences, not surveyed banks. Bridge chord water fractions do not establish whole decks or land approaches; in particular Galveston and Coronado remain partial. See the machine-readable audits under `verification/` for individual values and sources.

## Integrity and reproduction

The selected SCS has 25 members, a closed MAT→TOBJ→DDS graph, a 2048-square overview and four 8192-square opaque DX10 BGRA8/sRGB one-mip tiles. Independent checks compare every encoded pixel with its production atlas quadrant/overview; bounds and world mapping remain unchanged. License notices match source texts; no protected game/map assets, native diagnostics, includes or Ford dependency enter the SCS. The map-definition SHA-256 is `3467c3d500ef31f13567983a06e6b54c6774a496f982c93ec0cbb42ae849a5f6`.

Two production builds and a rebuild from the extracted corresponding ZIP produce the exact SCS SHA above. The 305-member source ZIP contains 296 committed project files plus `SOURCE-BUILD.json` and eight pinned public inputs (seven geographic files and the font). It uses only bundled public data/font and the recorded Python environment; no installed game resources are needed to rebuild. The ZIP's project files byte-match source commit `bd613b7`. Source preferred inputs are editable generator code, configuration/coefficient fields, factual correspondence/provenance records, original public vectors and font. Calibration research inputs/diagnostics remain separate.

From the extracted source root, with CPython 3.12 and the exact `r3/requirements.txt` versions:

```sh
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m ats_road_trip.background \
  --config docs/examples/north-america-background/r3/config.json \
  --data-dir render-inputs --font render-inputs/DejaVuSans.ttf --experimental
```

[Repeat proof](../../local_outputs/generated/2026-10-25_07-07-39/repeat-build-verification.json), [source-ZIP rebuild proof](../../local_outputs/generated/2026-10-25_07-07-39/source-bundle-reproduction.json), [build receipt](../../local_outputs/generated/2026-10-25_07-07-39/build-receipt.json), [independent package audit](../../local_outputs/generated/2026-10-25_07-07-39/verification/final-package/final-package-audit-summary.md), [geometry/role audit](../../local_outputs/generated/2026-10-25_07-07-39/verification/qualified-ground-final-audit/audit-summary.md).

## Rights

Project-authored generator, configuration, definitions and composition: AGPL-3.0-only. Natural Earth and USGS NHD data are public domain; GSHHG 2.3.7 is LGPL-3.0-or-later, with original ZIP/full notices and GPL/LGPL texts supplied. DejaVu Sans retains its separate font notice. Wikidata structured points are CC0; historical NRCan facts retain OGL–Canada attribution. Additional source-specific factual references/uncertainty are recorded in the source configuration. Native game/map meshes, textures, sectors, road arrays, screenshots and diagnostic overlays are excluded from the SCS and source ZIP. The comparison gallery is private diagnostic evidence, not mod artwork or a licensing grant over native content.


[Editable r3 source guide](../examples/north-america-background/r3/README.md), [ADR-0029](../architecture/decisions/ADR-0029-compose-geographic-features-and-audit-complete-deformation.md), [completed task](../tasks/done/TASK-0053-repair-background-shoreline-feature-alignment.md).
