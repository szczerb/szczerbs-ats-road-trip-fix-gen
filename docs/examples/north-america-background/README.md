# Original North America background: reproducible inputs

**Latest revision:** [r1 reproduction and configuration](r1/README.md); the commands and inputs below preserve historical r0 reproduction.

**Observed locally — 2026-10-23, ATS 1.61.3.18:** the original generator is independent of map-fix generation. It needs licensed vector/font inputs, its configuration and the Python libraries below. It does not need the vanished Workshop background, N2, game/DLC assets or third-party map archives to reproduce this pinned r0 artwork. The factual calibration was obtained by read-only inspection of the installed stack. Recalibration after map changes requires new observations.

## Build

Run from the repository root with CPython 3.12 on Linux. Create a fresh Europe/Warsaw timestamp for every build. The examples use `2026-10-23_21-50-00`; replace it with an unused timestamp. Existing work/generated runs are never overwritten.

```bash
python3 -m venv local_outputs/work/2026-10-23_21-50-00/venv
local_outputs/work/2026-10-23_21-50-00/venv/bin/python -m pip install -r docs/examples/north-america-background/requirements.txt

PYTHONPATH=src local_outputs/work/2026-10-23_21-50-00/venv/bin/python -m ats_road_trip.background.fetch \
  --output local_outputs/work/2026-10-23_21-50-00/source-data

PYTHONPATH=src local_outputs/work/2026-10-23_21-50-00/venv/bin/python -m ats_road_trip.background \
  --config docs/examples/north-america-background/config.json \
  --data-dir local_outputs/work/2026-10-23_21-50-00/source-data \
  --font local_outputs/work/2026-10-23_21-50-00/source-data/DejaVuSans.ttf \
  --run-id 2026-10-23_21-50-00 --experimental
```

`python3 -m venv` requires the Python venv/ensurepip package on distributions that split it out. The actual local build used the ignored `local_outputs/work/2026-10-23_21-16-53/venv` environment after bootstrap because system ensurepip was unavailable. No system Python/package directories were changed.

The fetch step verifies hashes before writing. The source ZIPs are read in memory without archive extraction. Only the known TTF member is read from the pinned Debian font archive; no package scripts execute. Network is used only by the explicit fetch step or `--download-data`; the normal generator is offline and refuses missing/changed inputs. All downloaded sources and outputs remain ignored. Optional `pip install '.[background]'` installs the same direct library pins; the base inspector keeps its existing dependency-free installation.

The command prints the package path, hash, calibration summary and gallery. It writes one `.scs`, previews and `SHA256SUMS.txt` beneath `local_outputs/generated/<timestamp>/`. Detailed receipt/audit/calibration and the original PNG/icon are under `local_outputs/work/<timestamp>/north-america-background/`. The distributable contains no diagnostics, local paths, source archives or configuration reports. Read the [manual handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R0.md) before enabling it.

## Configuration and provenance

- `config.json`: palette, label sizes, target build, canvas/zoom settings, spherical Lambert inputs, affine/optional smooth correction, preview regions, font pin and validation limits. World XZ units are game meters; they are not direct physical-world distances.
- `anchors.json`: 52 factual CityArea node references and matching Natural Earth places, split into 34 fit / 18 check points. Each records the original provider basename, virtual sector/hash, item/node UIDs and Natural Earth ID. No protected sector bytes are included. The broadest CityArea represents cities with multiple regions; it is a designed region center, not a survey of downtown.
- `sources.json`: exact archive SHA-256, URLs and individual dataset versions. Natural Earth layers do not all share a version. Countries and province polygons are 5.1.1; internal lines 5.1.0; lakes 5.0.0; places 5.1.2.
- `font.json`: DejaVu Sans Book 2.37, pinned Debian package 2.37-8 and TTF member. The source binary and its hash differ from the host's installed font despite the same package-version label; use the downloaded pin. [Font permission notice](../../../assets/background-map/FONT-LICENSE.txt).
- `requirements.txt`: direct renderer versions. Receipts also record actual Python, FreeType, zlib and installed library versions. Byte reproducibility is tested in the recorded environment; an arbitrary OS/font/render-library combination is not promised identical rasterization.

Natural Earth [expressly places its vector/raster data in the public domain](https://www.naturalearthdata.com/about/terms-of-use/). [Country layer](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/), [province polygons and lines](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/), [lakes](https://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-lakes-reservoirs/) and [places](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/) provide primary provenance. Boundaries follow that dataset's conventions; the mod makes no independent boundary-status claim.

## Checks

```bash
PYTHONPATH=src python -m pytest tests/test_background.py -q
```

Use the prepared environment's Python for that command and install pytest there. The generator automatically checks finite configuration, power-of-two dimensions, eight-tier arrays, canvas/ref bounds, source/font drift, held-out limits, sampled deformation, exact archive allowlist/CRC, definition parsing, all custom material→TOBJ→DDS dependencies, exact stock icon masks, texture headers/opacity and encoded quadrant pixels. It never launches ATS or writes a profile/mod directory.

Fit and check assignments are explicit. The production affine model was selected after comparing it with a smooth thin-plate alternative on these check points; the check set is held out from fitting, but it is not an untouched final statistical test after model selection. Treat residuals as descriptive evidence for this configuration, not an accuracy guarantee for arbitrary roads or maps. Sparse eastern/northern geography has no independent calibration points.
