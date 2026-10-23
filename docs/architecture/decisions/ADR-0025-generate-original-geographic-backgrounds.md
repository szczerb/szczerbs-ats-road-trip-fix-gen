# ADR-0025: Generate original geographic backgrounds independently of map patches

## Context

**Documented — user objective, 2026-10-23:** replace the vanished North America Background Map 5.3 and its dependent N2 overlay with original standalone geographic artwork for ATS 1.61. The newer research checkout at `2d7394d` contains navigation and r10 map-fix evidence ahead of this checkout. Reading it does not authorize merging its unrelated experiments. Its N2 definition retains three external includes; no redistribution grant for that third-party definition/art was established.

**Observed locally — installed ATS 1.61.3.18, 2026-10-23:** the UI backdrop uses one overview and four geographic texture tiles with MAT/TOBJ/DDS dependencies. Stock DDS is BGRA8 sRGB DX10, one mip. The stock map header supplies a 20:1 normal scale; climate definitions specify Lambert conic, parallels 33/45 and origin 39/-96. These observations motivate a calibration, not an exact geographic engine model. [Research and reproducible evidence](../../reference/NORTH_AMERICA_BACKGROUND_RESEARCH.md).

## Decision

Create a separate optional Python background module and pinned configuration/data/font manifests. Build original cartography from Natural Earth public-domain vectors, with a fitted transform between geography and game XZ. Keep the uncorrected LCC baseline and optional smooth residual correction explicit and configurable. Select the simpler affine correction for r0 because it generalizes better to the held-out references than the inspected thin-plate candidate. Keep measured error and reference-centroid uncertainty visible.

Author a self-contained `def/map_data.sii`, the five material/texture chains, metadata and an original map-based icon. Preserve the stock route, road, marker and icon inputs, including all nine map-area color rows; stock local masks already include car fuel/rest categories. Adjust only geographic canvas/camera settings and the farthest world zoom. Do not import N2 or its background includes. Do not add a Ford dependency or map sectors.

Use the inspected DX10 BGRA8 sRGB layout and column-major tile order (northwest, southwest, northeast, southeast). Pin the font and renderer dependencies, produce a deterministic deflated ZIP `.scs`, and validate its allowlisted resource graph and actual encoded pixels. Keep diagnostics, source vectors and local paths outside the mod; generate previews and reports beside it. Require an explicit experimental build flag and refuse overwrites.

## Consequences

The background must win both definitions and materials above OtherMaps, Reforma and ProMods resources. It replaces older backgrounds/N1/N2, while source-relative gameplay fixes keep their existing order. The background supplies geography, not playable roads or eligibility changes.

The authored code/art/configuration uses AGPL-3.0-only; public-domain data and DejaVu font terms remain separately recorded. No third-party background or game image is redistributed. The generated raster has a finite resolution; local map distortion, city-region centroids and unmeasured eastern/northern locations limit fit claims. Static checks cannot establish UI camera mapping, GPU rendering, filter behavior or runtime acceptance. The user performs the in-game test. [TASK-0048](../../tasks/active/TASK-0048-build-original-north-america-background.md).
