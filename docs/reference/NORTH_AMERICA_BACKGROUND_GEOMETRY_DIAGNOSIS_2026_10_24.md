# Background geometry diagnosis after r1 gameplay

Historical delivery artifacts, comparison images and supporting evidence cited here are private local evidence, absent from the source repository and not published. The identifiers below are local references only; no external release link or new upload is provided.

Inspection: **2026-10-24 afternoon**, ATS **1.61.3.18**, original background **1.61-r1-experimental**. [TASK-0050](../tasks/done/TASK-0050-diagnose-common-background-geometry-mismatch.md). No production code, mod package, live installation, game session or profile was changed during this investigation.

## Finding and strength of conclusion

**Observed locally:** the common implementation weakness is the calibration's choice of geometry and its acceptance test. Geographic settlement points were paired with representative **CityArea region centers**, then r1 improved those centers' errors/pixels. They are not matching road junctions, shoreline points or complete city footprints. The measurements can pass while the roads remain offshore. The user's r1 screenshots demonstrate that this acceptance test was insufficient for the requested road-aligned backdrop.

**Observed locally:** the sampled runtime texture-to-world mapping is working as authored. Independent native road endpoints placed using a transform recovered solely from the texture line up with the screenshot roads. The installed r1 is also the exact delivered archive at the expected priority. A hidden 1:19 map scale, stale r0 package, tile-scale mismatch or simple undisclosed image stretch has no supporting evidence in these checks.

**Hypothesis, supported but not uniquely proved:** representative-point calibration and the differently compressed/reworked regional road geometry are the dominant common reason the geography fails across coasts and lakes. Different coastline detail also contributes in some places. This does not establish one uniquely correct replacement projection, nor prove that city scale alone causes every screenshot offset.

A simple uniform enlargement cannot be recommended from this evidence. A 3% enlargement around the present canvas center improves southern California but substantially worsens Baja. Allowing a free translation, separate axis scales or shear still trades inspected regions against one another. No new SCS is presented as a repair on this basis. The next geometry repair needs geographically matched shore/road landmarks and independent road-footprint checks, replacing the city-center-only acceptance test.

## User evidence and actual installation

**Documented — user r1 gameplay report:** all original practical issues remain, perhaps slightly shifted. Job selection is still too far out in both truck/car modes. Baja roads/cities lie east of the peninsula, while Los Angeles/San Diego roads lie west of land. Gulf examples include Brownsville, Corpus Christi, Galveston, Lafayette and New Orleans. Chicago and the western Canadian lake belt still overlap water. The user proposed an overall size/projection issue and explicitly ended feedback collection before requesting this investigation.

Eighteen unique PNGs and a snapshot of the current game log are preserved under ignored `local_outputs/work/2026-10-24_16-17-05/`. Screenshot hashes (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/user-evidence/inventory.json`). The repeated `160711` attachment is one file. WSL access works despite the attachment-reader Windows-path failures. PNG widths vary because the supplied views are cropped; they are not evidence that the game's display aspect changed.

**Observed locally — read-only live archive/log inspection:** delivered and live SCS SHA-256 both equal `a10d9abcf32d9f469a819292c56e012919759775d48492dbf51ca6fd31e88033`. The log mounts r1 after the other active mods. No relevant map-data/material load error was found. Active map headers present in ProMods/ATS Expansion and the stock header retain **normal scale 20, city scale 3**. No effective 19-versus-20 factor was found. Inspection notes (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/runtime-mapping/findings.md`).

## Independent screen-space measurement

**Observed locally:** SIFT feature matching registered the actual generated 8192 atlas against the supplied screenshots, allowing scale, rotation and translation independently per cropped view. Robust matches span wide parts of the map, rather than just a menu label. The measurement used pinned OpenCV 4.12.0.88, NumPy/SciPy/Pillow in the recorded local environment; OpenCV is scratch-only, not a generator/distributable dependency.

Native kind-3 road endpoints were extracted separately from the effective source sectors by linking road UIDs to nodes' forward/backward item references. They were not part of the texture registration or the original calibration. Regional datasets contain 90,401 road records; expanded Baja/Canadian windows add 109,194 records with overlap, not a claim of unique whole-world road count. Every selected road has two linked endpoint nodes, with no selected-sector parse failures. Curves, prefab road polygons and complete map-line rendering were not reconstructed.

The texture-derived transform also predicts the independently extracted road endpoints:

| Screenshot / region | Texture matching inliers | Texture fit RMS, pixels | Native endpoints in road comparison | Median endpoint-to-visible-road-mask distance, pixels |
| --- | ---: | ---: | ---: | ---: |
| `155524`, Los Angeles/San Diego | 28 | 0.32 | 7,209 | 0.35 |
| `160643`, southern Texas | 71 | 0.46 | 4,573 | 0.40 |
| `160701`, Louisiana | 135 | 0.56 | 4,565 | 0.81 |
| `160711`, Chicago | 39 | 0.60 | 5,296 | 0.74 |
| `160740`, Canadian lake belt | 237 | 0.43 | 751 | 0.00 |

Additional nuisance fitting of the native-road overlay in these views yields scales about **0.9963–1.0001**, rather than a common 3–5% mismatch. This is corroboration, not a formal confidence interval or proof about all UI views.

Southern California native-node overlay (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/road-overlay-155524.png`): cyan points are native road endpoints positioned using the transform found from backdrop features. They follow the displayed roads, including roads crossing the geographic coast. Root visually checked the long-road and city patterns; a delegate independently reviewed the method/metrics. Texture registration (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/texture-registration.json`), road registration (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/road-registration.json`), independent audit (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/registration-evidence-audit.md`).

Limits: the road mask is derived from screenshot gray/yellow colors; native hidden roads, prefabs, text and legitimate bridges complicate correspondence. These are endpoint/mask distances, not full centerline reconstruction. Weak SIFT rows with few/repeated matches are excluded from the conclusions. The initial narrow-region `160814` road test had zero endpoints and is explicitly unsupported; its optimizer result is excluded. Expanded Canadian coverage is used separately for the geographic-size experiments.

## Test of an overall size correction

**Observed locally:** to distinguish a geography-sizing problem from a runtime mapping problem, inverse-sample the existing atlas with a uniform geographic enlargement while keeping native road coordinates fixed. The initial pivot is the current canvas center **(-20000, -40000)**. Test native endpoints visible within each registered screenshot, omitting tiny endpoint-to-endpoint segments below 100 game units. Count endpoints over water at least 50 game units from the nearest land/shore pixel:

| View | Current geometry | Geography enlarged 3% |
| --- | ---: | ---: |
| `155524`, Los Angeles/San Diego | 15.23% | **0.53%** |
| `155505`, southern Baja | 8.36% | **19.39%** |
| `155514`, northern Baja | 4.23% | **14.30%** |

This directly reproduces the directional conflict in the user's report. A center-based enlargement helps one coast and moves the peninsula farther the wrong way. All sampled scales/views (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/visible-uniform-geography-tests.json`).

A further bounded experiment fits (a) scale plus free translation, (b) independent axis scales plus translation, and (c) a full small affine correction. Fit/check splitting uses deterministic 1,000-unit spatial blocks. All candidates retain regional tradeoffs. For example, the axis candidate improves the held-out southern California water measure but worsens both Baja views; the full affine candidate improves many US views but worsens northern Baja and the dense Canadian view, and reaches its allowed shear bounds. Parameters and held-out results (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/common-layout-model-tests.json`).

These tests do not mathematically prove that no affine correction could ever help. They show that the tested global corrections are not established continent-wide repairs. Water coverage is also **one-sided diagnostic evidence**: real bridges can cross water, and arbitrarily enlarging land would reduce the score without producing correct geography. An optimizer score alone must not select the next package.

## Projection and reference checks

**Observed locally / documented independently:** base climate uses LCC parallels **33/45**, origin **39/-96**; Reforma climate uses **15/45**, origin **20/-96**. The latter affects weather-coordinate interpretation and is not proof of the UI's CRS. Controlled projection comparison followed by an affine fit gives r0 check RMS **2412 → 3210** when switching to Reforma's pair. A separate dense controlled comparison fitting all 59 `fit`-role references, without compact correction, gives **1549 → 2681** across 229 checks; this differs from the shipped r1's 34-point affine selection and is explicitly a model comparison. The alternative worsens Canada, Mexico, Alaska and the US groups. Comparison (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/runtime-mapping/lcc-anchor-model-comparison.md`).

The independent [TruckSim Maps converter](https://github.com/truckermudgeon/maps/blob/main/packages/libs/map/projections.ts) uses SCS factors times degree length, roughly 19.647/19.688 physical meters per world unit, rather than a raw divisor of 20. The current full affine can absorb those constant axis scales and origin changes; this is not evidence of an uncorrected remaining 1.6–1.8% size bug. [SCS CRS overlay investigation](https://github.com/nautofon/scs-crs) independently supports that stock-coordinate conversion, with geography/road-fit limits. These are community primary implementations, not engine source or proof that every map mod follows the same geographic layout.

**Observed locally — control semantics:** SCS CityArea records contain a city token, dimensions and a node. The parser/census framing is consistent; no node-coordinate parsing defect was found. A city can have many separate CityAreas. Distance from the chosen broad-region anchor to another same-city region reaches about **4102 game units at San Diego, 5073 at New Orleans and 4735 at Chicago**. These spreads are not measured geographic errors; they show why one city-region center cannot validate the full city. Effective city definitions' map X/Y offsets are label offsets, not independent geographic control points. SCS's [editor overview](https://modding.scssoft.com/wiki/Tutorials/Map_Editor/Introduction_to_the_Map_Editor/Basic_Editor_Functions) distinguishes city name/size items from map overlays. Control audit (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/control-audit/anchor-cityarea-distance-summary.json`).

The normal/city scale distinction and regional reworks explain why town-point equality cannot be extrapolated to road/shore equality. They do not authorize multiplying the entire map by 20/3, or assert that every road displacement is caused by city scale.

## Job-market observation

**Observed locally:** direct old/new capture matching finds 244 robust map-content matches, a relative similarity scale of **1.1998**, and RMS **0.84 pixels**. The newer capture's matched content is about 20% larger after allowing camera rotation/translation. Measurement (local-only evidence identifier: `local_outputs/work/2026-10-24_16-17-05/job-market-zoom-comparison.json`).

The captures show different market screens/crops, so this does **not** isolate `zoom_uplift[7]` causally or validate all job interfaces. The user's usability report takes precedence: selection remains too crowded. Job-camera usability and geographic road fitting are separate problems; scaling geography to fix coasts would not establish a correct job-market camera setting.

## Outcome and required repair boundary

The investigation identifies a shared calibration/validation flaw and rules out several attractive simple explanations. It does not yet establish a replacement continental transform. Preserve the positive r0 style/icon results and the exact r0/r1 artifacts, but keep the practical alignment and market complaints unresolved.

A defensible subsequent repair must use geographically matching road-intersection/bridge/shoreline or peninsula/lake-shape landmarks, explicitly account for expanded native city footprints and map-mod regional distortion, and evaluate roads and withheld shoreline regions. Reusing generic settlement-to-CityArea centers or accepting lower training RMS/center-pixel counts repeats the demonstrated failure. No new package is labeled fixed from the present one-sided experiments.
