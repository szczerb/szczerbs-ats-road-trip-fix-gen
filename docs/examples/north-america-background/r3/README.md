# North America background r3 reproduction

This directory contains the selected editable r3 cartographic sources for ATS 1.61. Offline geometry is experimental; runtime acceptance remains with the user. The authoritative archive/reproduction receipts are identified by the delivery handoff. It preserves the r2 map definition, including the user-confirmed job-market zoom and navigation masks. The archived r0/r1/r2 builds are unchanged fallbacks.

## Rendering

Use CPython 3.12 and the exact versions in `requirements.txt`. Install them into a separate virtual environment. The corresponding source ZIP supplies the seven original licensed rendering inputs and the pinned DejaVu Sans font under `render-inputs/`; no game installation or supplied map archives are needed to reproduce the SCS.

From the extracted source root:

```sh
python -m pip install -r docs/examples/north-america-background/r3/requirements.txt
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m ats_road_trip.background \
  --config docs/examples/north-america-background/r3/config.json \
  --data-dir render-inputs --font render-inputs/DejaVuSans.ttf --experimental
```

Each run uses a fresh Europe/Warsaw timestamp under ignored `local_outputs/work/` and `local_outputs/generated/`. The package bytes are deterministic for the recorded runtime/data/font combination; paths and timestamps in external diagnostic receipts need not match. The source ZIP is source, not a second mod to enable.

The editable preferred sources are the renderer, all-layer mapping implementation, `config.json` coefficients, `anchors.json`, `feature-controls.json`, pinned `sources.json`, and original public vector inputs. Changing coefficients or sources and running the same command rebuilds the artwork. The fitted physical coefficients are explicitly recorded; re-running the private native-data investigation is not required for package reproduction. No native game/map mesh, texture, sector, road array or screenshot is distributed as rendering source.

## Mapping and fitting evidence

The r2 LCC/affine/local mapping remains the country-scale baseline. Shared feature stages then map Chicago, San Francisco, Seattle and two British Columbia ferry corridors, followed by a coherent Split Lake translation, 32 fixed global ground-fitting increments and 16 bounded Puerto San Carlos increments and 16 local industrial-site increments. All geographic layers use the same composition. The model does not move native roads or paint per-road land buffers.

`feature-controls.json` records 17 fitting correspondences, seven frozen semantic checks and four retired Galveston diagnostics, with source versions, identity, coordinates, allowances and exact flow wiring. Named model centers and ferry activation nodes are feature/site proxies, not surveyed shoreline positions. San Francisco has authored fitting targets reconciled within declared correspondence allowances; these targets remain separate from observed native coordinates. The former Galveston fitting targets/observations are retained as retired diagnostics: a controlled ablation showed that their flow distorted the source islands and moved qualified street ground into water. They are no longer fitting controls or independent checks. Geographic meter radii and native game-unit allowances are different quantities.

The native-data derivation uses 6432 rows: 5030 fitting and 1402 checking. The original 6057 retain 4760/1297 roles; 320 later source-qualified road/factory facts retain 232/88. Selection, interpolation, overlapping source windows and earlier use in r2 limit independence. Everett/SeaTac ground checks share sites with fitting landmarks. Check results inspected during model selection are reused diagnostic checks, not a fresh blind test. A late Puerto San Carlos supplement adds 55 street-grid rows (38 fitting/17 checking) after a missed visual regression was found. These are explicitly late and selection-biased, not blind validation. The original 6377 role and mainland-mask classifications are unchanged. No check was promoted to fitting during this revision.

The fixed global fit uses eight 8000-unit-support / 3000-unit-grid increments, then 24 4000-unit-support / 2000-unit-grid increments. Retain those exact 32 fields after removing the rejected Galveston feature flow: a full global refit moved unrelated Texas ground back into water. Append 16 compact Puerto-only increments (4000-unit support, 1500-unit grid) using 38 late FIT road points plus nearby original FIT rows. Their support is bounded by XZ [-91000,63500] to [-75500,85000]. The fixed Texas comparison window is pixel-identical to the successful no-Galveston ablation. No Galveston validation point is fitted. Two existing FIT company locations were then checked against actual native geometry: a La Paz asphalt floor triangle and an Oakland vehicle-path chord with adjacent paved-road support. Eight additional local increments per site refine these existing fitting points while preserving all prior 48 fields and nearby fitting landmarks. All 6432 row roles/coordinates and original mainland classifications remain unchanged. The final chain has 64 fields. Oakland still lies about 8.3 game units on the water side of the raster edge; La Paz is about 8.5 units on land. These are within one high-resolution texel, not exact coast surveys. Regularization penalizes accumulated displacement and strain. Public island/lake source outlines regularize shape while allowing rigid translation/rotation; they are not observations of native water. The deterministic source-feature selection protects small public polygons near fitting land rows within the existing dry margin. The signed source mask is positive in water and negative on land. Split Lake has a separately identified rigid placement and outline prior. Bridge interiors have separate wet-context diagnostics.

## Sources and rights

The five Natural Earth archives retain the r2 versions and public-domain status. `sources.json` pins exact download URLs and hashes. GSHHG 2.3.7 high-resolution L1 coastline is **LGPL-3.0-or-later**, not public domain; its original source ZIP, notices and full LGPL/GPL texts accompany the corresponding source. GSHHG lakes are not used. USGS NHD Lake Michigan waterbody OBJECTID 8439286, GNIS 01623080, supplies 104803 vertices/168 rings and is public-domain archived hydrography, not a current shoreline survey. Other lakes retain Natural Earth.

Wikidata point facts are CC0; NRCan/CGNDB legacy facts retain Open Government Licence–Canada attribution. ASCE, WSDOT, Texas Historical Commission, Texas Tech University and USGS GNIS provide separately identified feature/site facts. Full facts/provenance and uncertainty are in `feature-controls.json` and the handoff. No protected native model or map art is copied into the background. Project-authored code/configuration/cartographic composition remains AGPL-3.0-only; DejaVu Sans has its separate notice.

## Resource and validation limits

The high-resolution atlas is 16384 square, encoded as four 8192-square opaque BGRA8 sRGB tiles with one mip, plus the unchanged 2048-square overview size. The four tiles contain 1 GiB of uncompressed pixel payload. Actual memory use and runtime performance require the user's test; the inspected GPU has 24516 MB but that does not establish a runtime pass. World bounds and quadrant mapping remain unchanged.

The offline configuration caps the composed chain at 64 increments to support a fixed global chain followed by regional corrections; all deformation thresholds remain unchanged. Numerical guards sample the country baseline, feature supports at 100-unit spacing, semantic control neighborhoods at 5-unit spacing, and full composed physical supports at 500-unit spacing. They bound determinant, linear stretch and inverse cycles. They do not prove continuous invertibility. Source polygon validity/area/perimeter, actual rendered masks, independent native relationships and all supplied screenshot views are checked separately. A smoother coast, passing guard or lower average water overlap alone does not establish repair.

Enable one background version above every background/map-data override, including Reforma OtherMaps Patch, ProMods definitions and Reforma ProMods Background Fix. Disable the former background, other backgrounds and N1/N2 overlays. Preserve source-map/fix order below it and keep separate fuel/rest/courier/tank packages. No Ford DLC dependency is introduced. Do not install the source ZIP. Final runtime acceptance remains the user's.
