# North America background r1: reproducible inputs

**Observed locally — 2026-10-24, ATS 1.61.3.18:** r1 is an experimental correction of the original background. It refines geographic detail and selected regional alignment while retaining the r0 presentation and UI contract. Read the [r1 manual handoff](../../../reference/NORTH_AMERICA_BACKGROUND_1_61_R1.md) before enabling it. This generator does not launch ATS, modify a profile, or establish runtime fit for every road.

## Reproduce the build

Run from the repository root with CPython 3.12 on Linux. Pick a fresh, unused Europe/Warsaw timestamp for `RUN` each time; the example below uses `2026-10-24_03-45-00`.

```bash
RUN=2026-10-24_03-45-00
python3 -m venv "local_outputs/work/$RUN/venv"
"local_outputs/work/$RUN/venv/bin/python" -m pip install \
  -r docs/examples/north-america-background/r1/requirements.txt

PYTHONPATH=src "local_outputs/work/$RUN/venv/bin/python" -m ats_road_trip.background.fetch \
  --config-dir docs/examples/north-america-background/r1 \
  --output "local_outputs/work/$RUN/source-data"

OPENBLAS_NUM_THREADS=1 PYTHONPATH=src "local_outputs/work/$RUN/venv/bin/python" -m ats_road_trip.background \
  --config docs/examples/north-america-background/r1/config.json \
  --data-dir "local_outputs/work/$RUN/source-data" \
  --font "local_outputs/work/$RUN/source-data/DejaVuSans.ttf" \
  --run-id "$RUN" --experimental
```

The fetch step verifies pinned hashes before saving files. The normal generator then runs offline. The font binary is read from its pinned Debian package member; no package scripts execute. Keep downloaded inputs, generated previews, diagnostics, and the `.scs` beneath the ignored timestamped `local_outputs/` directories. The package contains the standalone map definition, authored map textures, metadata, and notices; it does not contain the source archives or build reports.

## What changed in r1

- The geographic reference set has 288 records: 59 fit references and 229 held-out checks. The affine baseline uses the same 34 original r0 references, preserving that fitted affine transform exactly.
- Twenty-six fit references contribute compact local corrections within a 15,000 game-world-unit radius. Twenty-four use their full correction. Surrey and Nimpkish use diagonal regularization 0.3 to keep the sampled mapping from folding locally. The result is a locally corrected map plane, not a surveyed road network.
- Split Lake's official geographic point falls inside a Natural Earth 10m lake polygon. It remains a held-out check and documented source-map mismatch, and is excluded from local fitting.
- R1 selects Natural Earth 10m countries and lakes instead of r0's 50m layers. Lake polygon holes retain the underlying country fill, preserving islands enclosed by lake rings.
- The palette, world bounds, texture dimensions, and map icon masks are unchanged from r0. Zoom tier 7 changes from 120,000 to 100,000. Under the inverse-camera-height hypothesis, that is about 20% closer for the shared far-zoom tier; it may reduce the farthest world-map extent. Runtime zoom behavior is still awaiting manual validation.

The `anchors.json` entries retain the observed map-provider/sector references for ATS positions. `geographic-references.json` records nine additional official gazetteer coordinates: seven Canadian records under the Open Government Licence - Canada and two USGS GNIS records whose source is public-domain federal data. These records document inputs and do not confer rights to third-party map content.

## Data and authorship

Natural Earth datasets are public domain under [Natural Earth's terms](https://www.naturalearthdata.com/about/terms-of-use/). R1 pins 10m countries 5.1.1, 10m states/provinces 5.1.1, 10m internal boundaries 5.1.0, 10m populated places 5.1.2, and 10m lakes 5.0.0. Exact URLs, sizes, versions, and SHA-256 values are in `sources.json`. The DejaVu Sans Book font pin and its separate notice are in `font.json` and the repository's [font license notice](../../../../assets/background-map/FONT-LICENSE.txt).

The cartographic composition and generator are original project work under AGPL-3.0-only. Consult the root [license](../../../../LICENSE) and the package notices. No SCS or third-party map artwork or definitions are included. Dataset boundaries follow Natural Earth's conventions; this work makes no separate boundary-status claim.

## Validation limits

The generator checks source and font hashes, fit/check error limits, and sampled Jacobian behavior, then audits the standalone package and texture dependencies. These checks do not prove that the background aligns with every road, that every sparse region is accurate, or that ATS renders it correctly. The closer shared zoom and all geographic changes await user testing in ATS 1.61. Do not describe the package as runtime-verified or as a road-accurate map replacement.
