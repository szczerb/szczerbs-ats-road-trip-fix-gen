# North America background — ATS 1.61 r2 testing handoff

**Observed locally — 2026-10-24, ATS 1.61.3.18:** r2 is a materially changed experimental calibration and a stronger job-market zoom adjustment. It improves selected actual road/background relationships, with independent checks and explicit regressions below. **Unknown:** its in-game result. No installation, game launch, profile/save/economy operation or push occurred.

## Authoritative testing package

- [Use this r2 SCS](../../local_outputs/generated/2026-10-24_18-30-20/szczerbs-road-trip-north-america-background-map-ats-1.61-r2-experimental.scs).
- SHA-256: `58cbfe4047113308bb82a0e5ed4d15e298515f22916bab8eb8b1fc403c521604`.
- [Native-road before/after gallery](../../local_outputs/generated/2026-10-24_18-30-20/previews/native-comparisons/index.html), [overall and regional previews](../../local_outputs/generated/2026-10-24_18-30-20/previews/index.html), [quantitative geometry report](../../local_outputs/generated/2026-10-24_18-30-20/geometry-validation.json).
- [Reproduction commands and editable source](../examples/north-america-background/r2/README.md); versioned [calibration provenance](../examples/north-america-background/r2/calibration-provenance.json).
- [Corresponding source ZIP](../../local_outputs/generated/2026-10-24_18-30-20/szczerbs-road-trip-north-america-background-1.61-r2-source.zip), implementation commit `18e5f13c07d976fff4a7d6f2a91275a249a5b825`, SHA-256 `caae49d67707abee84f62c650e9fb0359f90d0f1fdf9709327ef9d8e593c9dd2`.

Title/author remain **szczerb's Road Trip North America Background Map**, **szczerb**; version **1.61-r2-experimental**, ATS **1.61**, no Ford dependency. Enable **one** background: replace r0/r1 with r2. Put it above **all** background/map-data overrides, including Reforma OtherMaps Patch, ProMods definitions and Reforma ProMods Background Fix. Keep each separate fuel/rest/source patch in its existing source-relative order below it. Disable the former North America Background 5.3, all N1/N2 overlays and other background maps. Separate fuel/rest/courier/tank mods retain their roles. [Original detailed order](NORTH_AMERICA_BACKGROUND_1_61_R0.md#installation-and-priority).

The original r0/r1 archives remain unchanged fallbacks. Other r2 build directories are repeat/source-reproduction evidence, not additional mods to enable. The corresponding source ZIP is source, not a second mod. It contains the committed generator/configuration, excludes native assets, and rebuilds independently to the exact SCS hash above.

## Cause and implemented correction

**Observed locally:** exact r1 is mounted at the expected priority; sampled atlas/native-road registration agrees closely in the supplied screenshots. No hidden 1:19 scale was established. Enlarging the continent helps Los Angeles but worsens Baja; tested affine/projection changes trade errors elsewhere. The common weakness is calibrating geographic settlement representatives to designed CityArea centers, which cannot describe expanded city roads or regional map-mod distortion. This does not establish that every remaining offset has the same cause. [Earlier diagnosis](NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md).

R2 retains r1's LCC/affine/local mapping, then applies one compact vector field to **all geographic layers equally**. It uses named-road normal correspondences and typed fuel/rest/service ground-use facts; it does not paint land over roads or include native road artwork. The field has 865 coefficient pairs, 15,000-unit compact supports and 5,000-unit grid spacing. Native city roads remain where the game/map authors put them. Generalized source roads permit normal-distance matching with along-route sliding; tangential errors are consequently less constrained. [Decision and mathematical boundary](../architecture/decisions/ADR-0028-calibrate-background-with-roads-and-ground-constraints.md).

**Fit/check separation:** 576 same-route observations fit the field; 135 selected route observations check it, using a deterministic 4,000-unit cell split. They were prefiltered using r1 and are mainly nearby interpolation checks: 123/135 have same-route fit observations. They are not blind or spatial extrapolation validation. All 962 physical-ground observations were used for fitting; their residuals are training diagnostics. The ground inequality uses rendered r1 signed water distance with a 50-unit tolerance, not surveyed shore distance. Roughly 61-unit pixels, smoothing, coast strokes and text treated as non-water limit this mask's precision. No all-roads-must-be-land loss is used.

## Stronger market zoom

`zoom_uplift[7]` changes **100000 → 60000**; the other seven tiers and every other packaged map-definition byte are unchanged. Under the inverse-height hypothesis this is about **1.67× r1's apparent scale**, rather than another small adjustment. A fixed-icon simulation of the crowded screenshot found 16 detected overlaps at r1, 3 at 75000 and 0 at 60000; about 45% of source centers remain in the viewport at 60000. Detection, viewport and camera assumptions make this supporting evidence, not an in-game usability result.

The bounded resource inspection did not find a separate exposed job-market control. Earlier ATS community reports associate this tier with both markets and the farthest world-map zoom; [r1's source discussion](NORTH_AMERICA_BACKGROUND_1_61_R1.md#job-market-zoom) retains the evidence. Less geography may be visible at once; bounds remain unchanged and more panning may be needed. This follows the user's priority for usable city selection. Truck/car behavior and useful pan reach await the user's test.

## Geometry results and regressions

All distances below are **game-world units**, not real-world meters. Native endpoint diagnostics use only UI-visible roads, including city roads, with corrected KDOP visibility flags; hidden roads are excluded. They sample deduplicated endpoints of chords over 100 units in fixed screenshot-derived viewports, not complete road curves/prefab footprints. Water diagnostics include legitimate crossings and cannot be used as an all-land requirement.

| Check | r1 → r2 | Interpretation |
| --- | --- | --- |
| 135 local route checks | RMS **699.1 → 565.6**; median **402.3 → 232.2** | About 19% RMS improvement; **49/135 worsen**; mostly interpolation. |
| Chicago I-57/I-80 withheld 2D junction | **2143.7 → 1718.8** | Matching native route topology and geographic intersection; sizeable residual remains. |
| Chicago I-55/I-90 withheld crossing | **2379.4 → 2100.4** | Native grade-separated road crossing, not a CityArea point; sizeable residual remains. |
| Coronado bridge diagnostic | Geographic inventory point to native bridge road **1442.6 → 129.9** | Inventory point may represent bridge beginning, not mesh center; native bridge remains mostly over water (87%). |
| Southern Baja: endpoints >500 units into rendered water | **2.01% → 0%**, n=895 | Shallow-water fraction also falls 10.39%→5.47%. |
| Northern Baja: same diagnostic | **0.88% → 0%**, n=910 | Shallow fraction 4.73%→1.65%; **5 local route-check RMS regresses 1066.5→1166.6**. |
| LA/San Diego: same diagnostic | **4.15% → 0.95%**, n=3471 | About 77% reduction in deep overlap, not full coastal repair. |
| Brownsville/southern Texas: same diagnostic | **0.26% → 0%**, n=1940 | Remaining shallow overlap. |
| Corpus Christi/Galveston | No >500-unit samples either version, n=2524 | **Shallow fraction worsens 0.91%→2.26%**; do not call this uniformly repaired. |
| Lafayette/New Orleans: >500-unit diagnostic | **1.77% → 0%**, n=1810 | Shallow fraction falls 6.19%→5.47%. |
| Chicago: >500-unit diagnostic | **0.26% → 0%**, n=2286 | **Shallow fraction worsens 0.70%→1.18%**; lakefront is not exact. |
| Manitoba/Saskatchewan 160740 | Shallow fraction **1.80% → 0.14%**, n=724 | Strong local improvement; other Canadian views differ. |
| Split Lake 160750 | Shallow fraction unchanged **5.26%**, n=38 | Sparse sample; no established repair. |
| Canada 160801 / 160814 | Some shallow samples regress | Mean depth 3.06→3.44 / 0→2.43; latter is one of 71 endpoints. |
| Vancouver Island local route checks | Two-check RMS **894.2 → 1016.9** | Small, nonrepresentative check set; explicit regional regression. |

The Galveston causeway and an LA port bridge candidate remain rendered over land in both versions. Their legitimate channels were not fit as universal road-on-land targets; less aggregate water overlap does **not** establish correct harbor/bridge geography. The LA bridge identity is plausible from route/location, not proven by its generic model name. Keep these as known unresolved defects. Generalized coast/lake data, urban expansion, limited landmarks and normal-only fitting constrain further accuracy.

Additional exact-window native endpoint regression checks ([data](../../local_outputs/generated/2026-10-24_18-30-20/regional-regression.json), panels in the gallery):

| Region | Samples | Water >50 units, r1 → r2 | Water >500 units, r1 → r2 |
| --- | --- | --- | --- |
| mobridge-oahe | 374 | 0.00% → 1.34% | 0.00% → 0.00% |
| vancouver-island | 2064 | 9.74% → 8.96% | 2.76% → 1.60% |
| alaska-panhandle | 102 | 0.00% → 0.00% | 0.00% → 0.00% |
| alaska-yukon | 752 | 0.40% → 0.40% | 0.00% → 0.00% |
| pacific-sf-or-wa | 9885 | 1.31% → 1.61% | 0.08% → 0.09% |

Mobridge's shallow increase is five endpoints; it is not a proven lake/road repair. Northern Pacific capped mean water depth rises only 3.00→3.29 units, but its shallow fraction regression is explicit. Vancouver improves in this aggregate despite its two route-check regression above. The sampled Alaska thresholds do not regress; 10 of 12 historical Alaska reference mappings remain exactly identical, Ketchikan shifts 115.90 units and Petersburg 1.46 ([reference mapping audit](../../local_outputs/generated/2026-10-24_18-30-20/alaska-reference-regression.json)). Point checks do not establish every shoreline or rendered polygon.

## Offline verification

- **305 tests passed**, including corrected native header-vs-road flags, compact support identity, field composition/schema, sampled fold rejection and revision metadata.
- Combined mapping: **245,472 samples**, zero sampled flips, area ratio **0.192–3.740** relative to baseline. Sampling is not a continuous proof. An independent damped inverse check has maximum residual **0.102 units** after 32 steps.
- Historic CityArea references remain a secondary regression check: 229 excluded-reference RMS **1604.6 → 1531.7**, max unchanged **6381.0**. These approximate place references do not prove road fitting.
- Independent archive audit: **22 members**, closed MAT→TOBJ→DDS graph, no includes/sectors/diagnostics/protected source assets/local paths, no Ford dependency. Overview 2048², four 4096² opaque BGRA8 sRGB one-mip tiles; all quadrant/overview pixels match the production raster.
- Exact `def/map_data.sii` difference from r1 is only `zoom_uplift[7]`. MAT/TOBJ pairs, license files, bounds, masks, marker sizes, route colors/costs and navigation inputs are unchanged. User-confirmed car fuel/parking icon presentation is preserved by settings; no new in-game check is claimed.
- Current code reproduces r0 and r1 to their original exact SHA-256 values. Production r2 pixels equal the selected/audited candidate atlas. The extracted 304-member source ZIP rebuilt in a separate source root to the exact r2 SCS hash, using only pinned public data/font inputs; no installed game resources were needed. [Source-bundle reproduction receipt](../../local_outputs/generated/2026-10-24_18-30-20/source-bundle-reproduction.json).

[Build receipt](../../local_outputs/work/2026-10-24_18-30-20/north-america-background/receipt.json), [package audit](../../local_outputs/work/2026-10-24_18-30-20/north-america-background/audit.json), [independent calibration audit](../../local_outputs/generated/2026-10-24_18-30-20/independent-calibration-audit.md), [independent bridge audit](../../local_outputs/generated/2026-10-24_18-30-20/independent-bridge-audit.md), [independent package audit](../../local_outputs/generated/2026-10-24_18-30-20/independent-package-audit.md). The native-road gallery is local diagnostic evidence; neither it nor extracted native resources enters the mod/source ZIP.

## Manual trial

Compare Quick Jobs, Freight Market and External Contracts in truck and car modes where available: nearby cities should be easier to distinguish/select, panning should still reach useful edge locations, and the farthest world-map view should remain workable. Revisit reported coastal/lake spots during normal play, especially LA/San Diego, both Baja regions, Gulf ports and Chicago/Canadian lakes; assess actual shore/road relationships, including true bridges. Existing icon confirmation need not be repeated; report changes if noticed. Runtime acceptance remains the user's.

## Rights and sources

Project-authored generator/cartography/definitions/icon: **AGPL-3.0-only**. Natural Earth vectors, including North America roads **4.1.0** used for calibration: [public domain](https://www.naturalearthdata.com/about/terms-of-use/); source archive hash/version in calibration provenance. Federal Baja corridor identities use official SICT [Baja California 2014](https://www.sct.gob.mx/fileadmin/DireccionesGrales/DGST/Datos-Viales-2014/02_BAJA_CALIFORNIA.pdf) / [Baja California Sur 2015](https://www.sct.gob.mx/fileadmin/DireccionesGrales/DGST/Datos-Viales-2015/03_BAJA_CALIFORNIA_SUR.pdf) station facts. Independent bridge diagnostics consult [Caltrans State Highway Bridges](https://publish.data.ca.gov/dataset/state-highway-bridges), whose portal labels Creative Commons Attribution; its inventory is not a calibration input or bundled asset. Seven existing Canadian gazetteer references retain OGL–Canada attribution; two Alaska GNIS references remain public-domain federal data. DejaVu Sans notice remains separate. No game/map meshes, textures, native road artwork or protected definition files are redistributed.
