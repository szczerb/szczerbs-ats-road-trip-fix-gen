# ADR-0027: Check background calibration against road and shore geometry

## Context

**Documented — user r1 gameplay, 2026-10-24:** all original coast/lake placement problems remain, perhaps shifted. R1's lower regional point RMS and land/shore pixels at selected city references did not establish practical alignment. **Observed locally:** the delivered texture and independently extracted native road endpoints register consistently in the supplied screenshots; global scale and projection experiments trade errors between regions. [Diagnosis and measured limits](../../reference/NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md).

## Decision

Treat settlement-to-CityArea center calibration as approximate exploratory evidence. It cannot establish alignment of roads, shoreline relationships or complete city footprints. An exact fitting point, a non-water center pixel, archive validity and deterministic reproduction remain useful checks, but none is sufficient evidence that a reported road/water defect is repaired.

For a further geometry correction, require geographically matching shore/peninsula/lake or road-intersection/bridge landmarks, independent fit/check regions and road-footprint evidence that tests the user's actual defect. Separate texture-to-screen implementation mapping from geography-to-game calibration. Account for expanded city geometry and map-specific regional distortions rather than applying the city/normal scale ratio to the continent.

Keep one-sided road-on-land objectives diagnostic: bridges may legitimately cross water and expanding land indiscriminately can improve a numerical score while corrupting geography. Do not select a new package from that objective alone. Exclude unsupported image-registration rows and distinguish inferred correspondence from surveyed/identified matching landmarks.

## Consequences

R0/r1 source/artifact and static-test evidence remain historical and reproducible. User reports now establish that the practical geometry issues remain. The tested global transforms are not accepted as replacement geometry, and no speculative r2 is issued by this investigation. Finding/obtaining reliable matched landmarks is the next repair stage; the correct continent-wide/regional transform remains unknown.

This refines the verification boundary of [ADR-0025](ADR-0025-generate-original-geographic-backgrounds.md) and [ADR-0026](ADR-0026-bound-regional-background-corrections.md), without rewriting their historical choices. [TASK-0050](../../tasks/done/TASK-0050-diagnose-common-background-geometry-mismatch.md) records the research and its explicit remaining uncertainty.
