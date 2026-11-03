# R4: detailed texture-size repair only

R4 preserves the selected r3 artwork, geographic calibration, overview, map definition, navigation masks, materials, texture objects, icon, notices and description. Only the four detailed DDS files are downsampled from 8192 square to the working r2 size of 4096 square. The manifest revision changes to identify this separate package. No new texture quality, information layer, geographic or zoom changes are included.

## Reproduce from a source checkout

Run from the repository root on Linux/WSL. Use CPython 3.12 and the exact libraries in `../r3/requirements.txt`. The recorded byte-reproduction environment is Python 3.12.3, Pillow 12.0.0 with FreeType 2.14.1, zlib build/runtime 1.3, NumPy 2.3.4, SciPy 1.16.3, pyproj 3.7.2/PROJ 9.5.1 and PyShp 2.3.1. The pinned font is downloaded separately; an arbitrary installed font is not interchangeable. Other renderer/library environments may produce different bytes; the source pin intentionally refuses an unverified replacement.

No game installation, supplied map archive, private screenshot or dated research directory is needed. The fetch command verifies seven public geographic inputs and the font against the tracked source/font manifests. Data and fonts retain their own terms; do not bypass a failed hash check or assume a changed upstream response is equivalent. Both fetch and generator `--download-data` restrict the resolved download destination to this checkout's `local_outputs/work`; traversal and symlink escapes are rejected before writes or network access. Without `--download-data`, `--data-dir` can point to an existing cache anywhere and is read-only; missing offline cache directories are never created.

```sh
python3 -m pip install -r docs/examples/north-america-background/r3/requirements.txt
background_run=$(TZ=Europe/Warsaw date +%Y-%m-%d_%H-%M-%S)
background_data="local_outputs/work/$background_run/source-data"

PYTHONPATH=src python3 -m ats_road_trip.background.fetch \
  --config-dir docs/examples/north-america-background/r3 \
  --output "$background_data"

PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python3 -m ats_road_trip.background \
  --config docs/examples/north-america-background/r3/config.json \
  --data-dir "$background_data" --font "$background_data/DejaVuSans.ttf" \
  --run-id "$background_run" --experimental

background_repair_run=$(TZ=Europe/Warsaw date +%Y-%m-%d_%H-%M-%S)
PYTHONPATH=src python3 docs/examples/north-america-background/r4/resize_detail.py \
  --source "local_outputs/generated/$background_run/szczerbs-road-trip-north-america-background-map-ats-1.61-r3-experimental.scs" \
  --output "local_outputs/generated/$background_repair_run/szczerbs-road-trip-north-america-background-map-ats-1.61-r4-experimental.scs"
```

Use fresh timestamps for each run; outputs are never overwritten. R3 is the exact reproducible intermediate used by the surgical recipe, not the version to install. If already available locally, the historical r3 archive can be supplied directly instead of regenerating it. Its required SHA-256 is `8d29a9531e4ffab939f11891042e3a5fc2260310d7919eae83797f0329be9329`. The historical r4 output SHA-256 is `00e3932434dee49003fbf6f02da925f239939fd2997cbab78a54d5e305f013b4`. These hashes remain artifact fingerprints after the source-history cleanup; original source commit IDs in old receipts refer to the private pre-cleanup snapshots, as mapped in the [public-source review](../../../reference/NORTH_AMERICA_BACKGROUND_PUBLIC_SOURCE_REVIEW_2026_10_30.md).

## Exact checks and remaining boundary

The recipe refuses changed source bytes, an existing output, or the wrong revision filename. It checks that all 20 other resources stay byte-identical and uses the existing complete package validator. Each detailed DDS is 67109012 bytes (64 MiB pixels plus its 148-byte header). The separate 2048-square overview is copied exactly. The source atlas and all existing r3 calibration/source inputs stay unchanged. The [r3 source guide](../r3/README.md) explains the editable inputs, notices and calibration limits. Project-authored code remains AGPL-3.0-only; inherited data/font notices remain in the package.

Historical source ZIPs, SCS files, comparison images and logs remain ignored local artifacts. They are not public downloads or newly cleared release assets. This guide supplies the public-source reproduction path without publishing those artifacts.

[INC-0002](../../../incidents/INC-0002-r3-background-detailed-texture-loading/README.md) records the logged DirectStorage request-size failure. R4 requires the user's runtime confirmation of all four world-map zoom levels; offline checks cannot establish that result. The normal load order is unchanged: enable only the locally generated r4 background above other background/map-data overrides. The previously accepted job-market zoom remains untouched.
