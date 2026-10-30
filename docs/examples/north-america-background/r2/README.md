# North America background r2: reproducible inputs

**Observed locally — 2026-10-24, ATS 1.61.3.18:** r2 is an experimental geographic background revision. It adds a compact local correction guided by named-road geometry and typed ground observations, and changes the shared farthest zoom tier. Read the [r2 manual handoff](../../../reference/NORTH_AMERICA_BACKGROUND_1_61_R2.md) before enabling it. The generator does not launch ATS, modify a profile, or establish runtime fit for every road.

## Reproduce the build

Run from the repository root with CPython 3.12 on Linux. The config's calibration coefficients are the preferred editable source; rendering needs only this config and the hash-pinned inputs below. It does not require installed ATS/DLC archives or native map resources.

```bash
RUN=$(TZ=Europe/Warsaw date +%Y-%m-%d_%H-%M-%S)
python3 -m venv "local_outputs/work/$RUN/venv"
"local_outputs/work/$RUN/venv/bin/python" -m pip install \
  -r docs/examples/north-america-background/r2/requirements.txt

PYTHONPATH=src "local_outputs/work/$RUN/venv/bin/python" -m ats_road_trip.background.fetch \
  --config-dir docs/examples/north-america-background/r2 \
  --output "local_outputs/work/$RUN/source-data"

OPENBLAS_NUM_THREADS=1 PYTHONPATH=src "local_outputs/work/$RUN/venv/bin/python" -m ats_road_trip.background \
  --config docs/examples/north-america-background/r2/config.json \
  --data-dir "local_outputs/work/$RUN/source-data" \
  --font "local_outputs/work/$RUN/source-data/DejaVuSans.ttf" \
  --run-id "$RUN" --experimental
```

Use a fresh timestamp for each run. Fetch verifies source hashes; generation then runs offline. The pinned font is extracted from its Debian package without running package scripts. Keep downloads, previews, diagnostics and the `.scs` under the ignored timestamped `local_outputs/` directories. The archive contains the standalone map definition, authored textures, metadata and notices, not the source archives or calibration reports.

## What changed in r2

- R2 retains r1's projection, geographic extent, world bounds, palette, texture sizes, labels, font, marker sizes, navigation/icon masks, camera start and all zoom tiers 0–6. Four regional preview windows were added for Baja California Sur, southern California, the Gulf Coast, and Chicago/Lake Michigan.
- `zoom_uplift[7]` changes from 100,000 in r1 to 60,000. Under the inverse-camera-height hypothesis, that estimates 1.67× the map scale of r1. The setting is reported to be shared by the job-market view and the farthest world-map tier, so the world view may show less geography at once. Current ATS behavior and usable pan extent await manual validation.
- The r1-calibrated position mapping receives the editable `route-ground-compact-v1` correction in `config.json`: 865 support centers with a 15,000 game-world-unit radius. Natural Earth route geometry supplies 576 same-route normal-distance fit observations and 135 local road checks. Route fitting allows sliding along a generalized route instead of forcing every native point to a particular along-road coordinate.
- All 962 physical-ground observations were used as inequality constraints during fitting. Their diagnostic residuals are training evidence, not validation checks. Do not describe the ground observations as held out.
- On the 135 road checks, RMS normal-distance residual decreases from 699.059 to 565.559 game units (about 19%). These are local checks selected before final fitting, split by deterministic 4,000-unit cells; they are not a spatially independent or blind benchmark. The check data were prefiltered using r1, and generalized source roads are not exact gameplay centerlines.

R2 still has residual errors, including in the Canadian lake belt and shallow Gulf region. The source water/ground labels and rendered shoreline carry uncertainty, and bridge/port approaches do not imply that all road points should be forced onto land. This is a local correction, not a global alignment or an exact shoreline guarantee. See `calibration-provenance.json` for counts, selection rules, fit details and limits.

## Data and authorship

Natural Earth datasets are public domain under [Natural Earth's terms](https://www.naturalearthdata.com/about/terms-of-use/). R2 pins the same Natural Earth countries, states/provinces, boundaries, populated places and lakes used by r1; URLs, versions, sizes and hashes are in `sources.json`. The Natural Earth North America roads archive used for calibration is also public domain and is not rendered into the background. Read-only native map observations informed calibration coefficients but are not included in the source bundle or package. Additional official gazetteer references and their source terms are documented in `geographic-references.json`. The pinned DejaVu Sans notice is in `font.json` and the repository's [font license notice](../../../../assets/background-map/FONT-LICENSE.txt).

The cartographic composition, generator and project-authored definitions are licensed **AGPL-3.0-only**. Consult the root [license](../../../../LICENSE) and package notices. No SCS or third-party map artwork or definitions are included.

## Validation limits

The generator checks pinned input hashes, configured fit/check limits, sampled mapping behavior and package dependencies. These checks do not prove that the background aligns with every road, that every sparse region is accurate, or that ATS renders or pans as expected. The closer shared zoom and all r2 geographic changes await user testing in ATS 1.61. Do not describe the package as runtime-verified or road-accurate.
