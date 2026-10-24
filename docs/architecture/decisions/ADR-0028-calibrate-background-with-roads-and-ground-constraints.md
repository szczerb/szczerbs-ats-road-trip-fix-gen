# ADR-0028: Calibrate the background with roads and physical-ground constraints

## Context

**Documented — user goal, 2026-10-24:** deliver a better r2 testing package, including stronger market zoom, after r1 retained the practical road/water defects. [ADR-0027](ADR-0027-check-backgrounds-against-road-and-shore-geometry.md) requires actual road/shore evidence. **Observed locally — ATS 1.61.3.18:** runtime atlas registration is consistent; a global enlargement trades southern California improvement for Baja regression. Generic settlement-to-CityArea correspondences cannot describe expanded urban road footprints.

## Decision

Preserve r1's LCC/affine/local baseline and compose a regularized compact vector field in its output XZ plane. Apply it equally to countries, lakes, borders and labels. R2 stores 865 editable coefficient pairs on a 5,000-unit grid, using a 15,000-unit Wendland C2 support radius. Outside all supports the additional field is exactly zero. Source vectors retain their geometry; no native roads, traced shore artwork, land buffers or hand-painted coastline patches enter the delivered artwork.

Fit normal distance to geographically identified Natural Earth routes, permitting along-route sliding. Distinguish federal Mexican roads from same-number state roads using official SICT corridor facts. Use typed native fuel/rest/service positions as physical-ground **class inequalities**, not exact geographic correspondences or an all-roads-on-land objective. All 962 such facts influence fitting. The fitting mask comes from r1's rendered exact water color, with one-pixel smoothing and a 50-unit tolerance: text/strokes and roughly 61-unit raster cells limit its precision. These class residuals are training diagnostics.

Use 576 route observations for fitting and 135 selected local route observations for checking. A deterministic 4,000-unit cell split reduces immediate duplication, but most check routes also have nearby fit observations and were prefiltered using r1. Do not claim blind or geographically independent generalization. Require additional withheld two-dimensional intersections, physical bridge diagnostics, actual native road endpoints and explicit regional regressions. Neither lower normal-distance error nor fewer water pixels alone establishes correct geometry. Legitimate bridges remain water diagnostics, never universal land constraints.

Bound coefficient input and sample the combined mapping for flips/implausible area ratios, including dense old supports and a 1,000-unit grid covering the new field. This is a sampled guard, not a continuous invertibility proof. Keep r0/r1 byte-reproducible.

Set shared `zoom_uplift[7]` to 60,000 instead of 100,000; leave the other seven tiers and the remaining map definition unchanged. No independent exposed market control was established. The user prioritizes selectable market cities over the farthest world-map extent. Fixed-icon spacing simulation supports this stronger experiment; runtime behavior remains for the user to test.

## Consequences

**Observed locally:** local road-check RMS falls about 19%; two withheld Chicago intersections and the Coronado bridge diagnostic improve. Actual deep-water endpoint overlap falls in several reported regions. Shallow Gulf overlaps, sparse Canadian lakes, the Galveston causeway and LA port bridge remain explicit limitations; normal-only fitting cannot constrain tangential displacement. No universal projection fix, exact shoreline fit or in-game success is claimed.

The versioned coefficients are preferred editable source for deterministic rendering without proprietary game inputs. Calibration provenance and limits accompany them. Ignored native observations and investigation images remain local evidence, outside both SCS and corresponding source ZIP. [R2 handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R2.md), [configuration](../../examples/north-america-background/r2/README.md), [TASK-0051](../../tasks/done/TASK-0051-recalibrate-background-to-roads-and-shores.md).
