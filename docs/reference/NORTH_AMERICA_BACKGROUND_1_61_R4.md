# North America background 1.61-r4-experimental

**Observed locally, 2026-10-25:** this is a texture-size repair only. It addresses the resource-size regression investigated in INC-0002; restoration in the running game awaits the user's test.

## Testing package

Enable [the r4 SCS](../../local_outputs/generated/2026-10-25_18-06-28/szczerbs-road-trip-north-america-background-map-ats-1.61-r4-experimental.scs) instead of r3, keeping the same load order above other background/map-data overrides. Keep separate map/fuel/rest/courier/tank mods in their existing order. No live installation or profile/settings changes were made.

SHA-256: `00e3932434dee49003fbf6f02da925f239939fd2997cbab78a54d5e305f013b4` ([checksum file](../../local_outputs/generated/2026-10-25_18-06-28/SHA256SUMS.txt)).

## Exact scope

Only four detailed DDS textures change from 8192 square to 4096 square, returning each to the working r2 budget: 64 MiB pixels plus the existing 148-byte DDS header. The existing DX10 BGRA8 sRGB format and single mip are retained. Their pixels are LANCZOS downsampling of the corresponding r3 quadrant. The manifest revision changes from r3 to r4 to identify the separate package.

All 20 other members are byte-identical to r3: the overview, map definition, zoom/navigation masks, bounds, materials, texture objects, icon, notices and description. R3's source artwork, calibration and shoreline geometry are retained; no geographic refit or additional information/quality feature is included. Old packages are unchanged.

## Verification and runtime boundary

Existing package/resource validation passes. Independent audit checks identical 25-member sets, the exact five-member change set, revision-only manifest edit, all 20 copied members, DDS structure/dimensions/opacity and ZIP CRC. [Build receipt](../../local_outputs/generated/2026-10-25_18-06-28/build-receipt.json), [repeat proof](../../local_outputs/generated/2026-10-25_18-06-28/repeat-build-verification.json), [independent audit](../../local_outputs/generated/2026-10-25_18-06-28/independent-audit/audit.md) and [focused package tests](../../local_outputs/generated/2026-10-25_18-06-28/package-tests.txt) record the checks. Repeat generation produces the same archive SHA. No game was launched.

After replacing r3 with r4 and fully restarting ATS, check that the background appears at all four world-map zoom levels. This is the outstanding runtime confirmation; the user-confirmed job-market zoom was not changed.

[Reproduction recipe](../examples/north-america-background/r4/README.md), [incident](../incidents/INC-0002-r3-background-detailed-texture-loading/README.md), [completed task](../tasks/done/TASK-0055-repair-r3-detailed-texture-size-only.md).
