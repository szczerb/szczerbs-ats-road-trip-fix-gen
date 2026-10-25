# R4: detailed texture-size repair only

R4 preserves the selected r3 artwork, geographic calibration, overview, map definition, navigation masks, materials, texture objects, icon, notices and description. Only the four detailed DDS files are downsampled from 8192 square to the working r2 size of 4096 square. The manifest revision changes to identify this separate package. No new texture quality, information layer, geographic or zoom changes are included.

Use the r3 pinned Python dependencies and the exact delivered r3 SCS (SHA-256 `8d29a9531e4ffab939f11891042e3a5fc2260310d7919eae83797f0329be9329`). From the project root, with a new Europe/Warsaw timestamp directory:

```sh
PYTHONPATH=src python docs/examples/north-america-background/r4/resize_detail.py \
  --source local_outputs/generated/2026-10-25_07-07-39/szczerbs-road-trip-north-america-background-map-ats-1.61-r3-experimental.scs \
  --output local_outputs/generated/YYYY-MM-DD_HH-MM-SS/szczerbs-road-trip-north-america-background-map-ats-1.61-r4-experimental.scs
```

The recipe refuses changed source bytes, an existing output, or the wrong revision filename. It checks that all 20 other resources stay byte-identical and uses the existing complete package validator. Each detailed DDS is 67109012 bytes (64 MiB pixels plus its 148-byte header). The separate 2048-square overview is copied exactly. The source atlas and all existing r3 calibration/source inputs stay unchanged.

The original editable r3 artwork inputs and renderer are supplied by the [r3 source bundle and reproduction guide](../r3/README.md). This surgical recipe operates on the deterministic r3 package produced by those sources. It does not rerender geography or require a game installation. Its project-authored code remains AGPL-3.0-only; inherited data/font notices remain in the package.

[INC-0002](../../../incidents/INC-0002-r3-background-detailed-texture-loading/README.md) records the logged DirectStorage request-size failure. R4 requires the user's runtime confirmation of all four world-map zoom levels; offline resource checks cannot establish that result. The normal load order remains unchanged: enable only this background revision above other background/map-data overrides. The previously accepted job-market zoom remains untouched.
