# North America background — ATS 1.61 r1 manual handoff

**Subsequent user gameplay, 2026-10-24 afternoon:** all original coast/lake issues remain, perhaps shifted; job markets remain too far out in both truck/car mode. R1 is not accepted as a practical repair. The [common-geometry investigation](NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md) finds the representative-city calibration/acceptance test insufficient for road fitting and tests runtime scale/projection alternatives. The offline delivery evidence below remains historical.

**Observed locally — 2026-10-24:** r1 is ready for another manual trial. It refines shorelines and selected regional placement, and tries the requested approximately 20% closer job-market view. It preserves the accepted palette, geographic extent, texture sizes and navigation masks. **Unknown:** the revised package's actual in-game result. No game launch, installation, profile modification or push occurred.

## Authoritative package

- [Use this r1 SCS](../../local_outputs/generated/2026-10-24_03-10-27/szczerbs-road-trip-north-america-background-map-ats-1.61-r1-experimental.scs).
- SHA-256: `a10d9abcf32d9f469a819292c56e012919759775d48492dbf51ca6fd31e88033`.
- [Preview gallery](../../local_outputs/generated/2026-10-24_03-10-27/previews/index.html), [overall](../../local_outputs/generated/2026-10-24_03-10-27/previews/overall.png), [Mobridge/Lake Oahe](../../local_outputs/generated/2026-10-24_03-10-27/previews/mobridge-oahe.png), [Vancouver Island/lower mainland](../../local_outputs/generated/2026-10-24_03-10-27/previews/vancouver-island.png), [Alaska panhandle](../../local_outputs/generated/2026-10-24_03-10-27/previews/alaska-panhandle.png), [Manitoba lakes](../../local_outputs/generated/2026-10-24_03-10-27/previews/manitoba-lakes.png).
- [Reproduction commands and input policy](../examples/north-america-background/r1/README.md). [Corresponding source ZIP](../../local_outputs/generated/2026-10-24_03-10-27/szczerbs-road-trip-north-america-background-1.61-r1-source.zip), implementation commit `f02c313`, SHA-256 `fb8a4d1eb7ed627c965413bb1d79cd44e87dfc4d808ae7811f177695a111a084`. It rebuilds to the exact SCS hash above; it is source, not another mod to enable.

Title/author stay **szczerb's Road Trip North America Background Map**, **szczerb**; version **1.61-r1-experimental**, ATS **1.61**, no Ford dependency. Replace r0 with this package; enable one background. Use the [same exact source-relative load order as r0](NORTH_AMERICA_BACKGROUND_1_61_R0.md#installation-and-priority): this background above all map-data/background/material overrides, including OtherMaps, Reforma and ProMods; keep existing source fixes/connector relationships beneath it. Disable vanished North America Background 5.3, N1/N2 and other backgrounds. Separate fuel/rest/courier/tank packages retain their roles.

All earlier r1 development runs are superseded or repeat-build evidence, not additional packages to enable. R0 remains an unchanged fallback.

## What caused the reported problems

**Documented — user report:** r0 generally works and looks good; truck navigation seems fine; a short car-mode check confirms both fuel and parking icons in car navigation. These accepted presentation checks remain recorded. No fueling/rest transaction or billing/reload result is inferred. [Full feedback and screenshot inventory](NORTH_AMERICA_BACKGROUND_FEEDBACK_2026_10_24.md).

**Observed locally — source geometry:** the old Natural Earth 50m Lake Oahe outline contains the dataset's own Mobridge settlement coordinate. The 10m outline excludes it, about 321 real meters from the bank. Homer and Churchill settlement points similarly change from outside the coarse country land to inside the fine country land. Coast detail therefore contributed independently of calibration. R1 pins 10m countries/lakes and preserves lake-island holes instead of painting them water. The 8192 atlas still has about 61 game units per pixel; coast strokes and city compression remain visible at close zoom.

**Observed locally — effective map comparison:** a complete census found 2,910 CityAreas across 3,474 winning sector resources, 610 city tokens and zero parse errors. Conservative city definition/name/country/admin1 matching yielded 269 unique Natural Earth matches; retained reviewed references and nine official geographic records extend evaluation to 288. No ambiguous global name match was silently selected. All 52 original item/node/XZ references remain effective. Jasper's winning provider is the higher connector; its coordinates are unchanged and r1 corrects the provenance. Complete stock packages have no duplicate sector resource paths in this inventory, so their tie order changes no selected points.

A single affine cannot follow all local shifts. Fitting a continental smooth correction to many city centers worsened excluded-city results. R1 instead retains r0's 34-point affine exactly, then applies compact corrections around 26 reported-region references. Twenty-four are interpolated exactly. Surrey and Nimpkish are softened because forcing all representative place points onto designed game centers caused local folds. These two remain substantial residuals. Split Lake's official community point is itself inside the 10m lake polygon, so it remains an uncertain check rather than a correction control. Geographic place representatives and CityArea centers are not surveyed matching landmarks.

## Job-market zoom

**Observed locally:** bounded inspection of ATS 1.61 UI/definition resources and reflected executable names found no separate exposed job-market zoom setting. Firsthand SCS forum reports associate fixed job-market scale with `zoom_uplift[7]`: [ATS discussion](https://forum.scssoft.com/viewtopic.php?t=286155), [additional report](https://forum.scssoft.com/viewtopic.php?p=1716571), [map-setting discussion](https://forum.scssoft.com/viewtopic.php?p=1894377). These reports support the shared-setting inference; absence from a bounded search does not prove an independent control is impossible.

**Hypothesis / experiment:** change only tier 7 from **120000 to 100000**, giving approximately **1.2 times apparent scale** if camera height controls inverse map scale. The other seven zoom entries are identical. This also reduces the furthest world-map view, following the user's stated priority for usable job-city selection. Do not change `ui_map_size` to accomplish this: it controls artwork mapping. Actual scale in Quick Jobs, Freight Market and External Contracts awaits runtime confirmation.

## Offline verification and limits

| Check | Result |
| --- | --- |
| Selected regional controls | 26; RMS 1,373 → **504 game units**. Twenty-four exact fits are training results, not independent validation. |
| References excluded from fitting | 229; RMS 1,571 → **1,605**, median 1,012 → 1,021, max unchanged 6,381 at Fairbanks. Slight broad regression is explicit. |
| Remaining softened-reference errors | Surrey about 1,903; Nimpkish about 1,726 game units. Source/place-center and local distortion uncertainty remain. |
| Sampled deformation | **174,436** continental/local samples, no flips; area ratio 0.244–3.393 relative to baseline. Sampling does not prove behavior between points. |
| Raster reference pixels | All 26 selected centers are land/shoreline rather than pure water; five were pure water in r0. This does not prove whole road/city areas are on land. |
| Definition changes from r0 | Only `zoom_uplift[7]`; bounds, masks, sizes, route colors/costs and truck/navigation inputs unchanged. |
| Archive/resources | 22 allowlisted members; closed MAT→TOBJ→DDS graph, no includes/sectors/diagnostics/local paths, no Ford dependency; correct opaque BGRA8 sRGB tiles and quadrant pixels. |
| Regression suite | **295 tests passed** with the recorded environment. |
| Reproducibility | Final r1 repeated byte-identically, including a build from the extracted source ZIP; updated code reproduces original r0 SHA `913ff62169b2dd7729fe16a0074d4d099d9cdd795c2b785a83a7adf32e32bac4`. |

[Build receipt](../../local_outputs/work/2026-10-24_03-10-27/north-america-background/receipt.json), [calibration](../../local_outputs/work/2026-10-24_03-10-27/north-america-background/calibration.json), [archive audit](../../local_outputs/work/2026-10-24_03-10-27/north-america-background/audit.json), [before/after measurement](../../local_outputs/work/2026-10-24_02-39-28/revision-comparison.json). Reference-check results informed selection; they are excluded from fitting, not a blind benchmark.

No universal border/road correction is claimed. The Canada/Mexico screenshots did not establish one uniform offset vector, and r1 preserves the baseline outside selected support regions. Split Lake, compressed lower-mainland city geometry, sparse distant regions and close-zoom coastline pixels remain limitations. Further precise repair of those local road/water relationships needs matching landmarks or more suitable shoreline geometry rather than forcing a settlement representative into a bad fit.

## Next manual check

During your next ordinary play session, compare city selection in Quick Jobs, Freight Market and External Contracts, then the furthest world-map view. Revisit Mobridge, the lower mainland/Vancouver Island, the northern port/panhandle and Manitoba lake locations when convenient. Report remaining conspicuous coast/road offsets, especially Split Lake and Surrey/Nimpkish, with map view and location. No repeat initial car-icon tour or fuel/rest transaction is requested; report icon changes only if noticed. R1's revised geography and zoom remain unverified until your report.

## Rights and source

Original authored code/cartographic composition/definitions/icon: **AGPL-3.0-only**. Natural Earth vectors: public domain. Seven additional Canadian coordinate references: Natural Resources Canada / Canadian Geographical Names Database, **Open Government Licence – Canada**. Two additional Alaska references: USGS GNIS federal public-domain data, retrieved through the official Alaska ADF&G mirror. DejaVu Sans notice remains separate. The package includes the required attribution; [versioned geographic records and primary URLs](../examples/north-america-background/r1/geographic-references.json) and [ADR-0026](../architecture/decisions/ADR-0026-bound-regional-background-corrections.md) document scope. No copied map/game/background artwork is included and no endorsement is implied.
