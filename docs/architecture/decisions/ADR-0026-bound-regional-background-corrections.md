# ADR-0026: Bound regional background corrections and preserve the accepted baseline

## Context

**Documented — user feedback, 2026-10-24:** r0 renders, its style is liked, car fuel/parking icons display in navigation, and extra world zoom is appreciated. Fixed job markets are crowded; city selection takes precedence over extra world zoom. Coastal/lake cities and a northern port expose alignment/detail defects. [Feedback](../../reference/NORTH_AMERICA_BACKGROUND_FEEDBACK_2026_10_24.md).

**Observed locally — ATS 1.61.3.18, 2026-10-24:** the complete supplied-stack census has 2,910 CityAreas in 3,474 winning sector resources, 610 city tokens and no parse failures. Conservative semantic country/admin1/name matching yields 269 Natural Earth cities; retained reviewed references extend this to 279. Nine official CGNDB/GNIS references extend the evaluation to 288. All original 52 item/node coordinates remain effective; Jasper's effective connector provider supersedes the earlier WCE provenance without changing its coordinates. A full-world smooth fit can improve training errors while worsening excluded-city errors. Natural Earth 50m Lake Oahe contains its own Mobridge place point; the 10m outline excludes it. Shoreline detail and map-local distortion are separate problems.

## Decision

Retain the original 34-reference affine matrix exactly. Use configurable compact C2 radial residuals only around 26 reported-region controls, with 15,000 baseline-game-unit support. The kernel is `(1-r)^4 * (4r+1)` for normalized distance below one and zero otherwise. Solve the coupled kernel system for XZ residuals. No displacement is introduced outside the support disks.

Interpolate 24 selected references exactly. Soften Surrey and Nimpkish with diagonal regularization 0.3: forcing all municipality/community representative points to all game-designed region centers caused sampled folds. Keep all residuals visible; an exact fitting point is not independent accuracy evidence. Split Lake is excluded from local fitting because the official community point itself lies inside the Natural Earth 10m lake polygon; retain it as an explicit uncertain check instead of silently moving source data or inventing a shoreline.

Pin 10m country/coast and lake data for r1; preserve lake-island holes with feature-bounded masks over the country fill. Preserve r0 configuration/data defaults and archive-byte reproduction. Keep the accepted palette, texture dimensions, bounds, marker masks and all unrelated map settings. Change shared `zoom_uplift[7]` from 120000 to 100000 as the requested approximate 20% closer experiment. No separate exposed job-market zoom control was found in bounded current-resource inspection; the shared-setting inference is supported by SCS forum runtime reports, not a verified engine source implementation.

Evaluate correction controls separately from 229 references excluded from fitting. Check continental and dense local Jacobian samples; reject nonfinite values, folds, area ratios below 0.15 or above 5. Inspect actual raster pixels and previews as well as point RMS. Retain geographic detail, native city compression and finite texture resolution as separate limits.

## Consequences

The 26-reference fit improves strongly; the 229-reference RMS slightly worsens. This is a targeted regional repair, not a claim of improved all-world accuracy. Exact reference-center pixels do not establish that every road or city-area polygon is on land. Representative settlement coordinates can differ from designed game centers, and source water geometry can be wrong at a real point. Split Lake and residual Surrey/Nimpkish alignment remain explicit limitations requiring further evidence if conspicuous in game.

The package remains original backdrop artwork, without sectors, live installation or gameplay changes. Seven NRCan/CGNDB geographic facts use Open Government Licence–Canada attribution; two USGS/GNIS facts from the official Alaska mirror are public domain. Natural Earth, font and project-authored rights remain separately stated. This extends [ADR-0025](ADR-0025-generate-original-geographic-backgrounds.md); it does not rewrite the r0 evidence. [R1 handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R1.md).
