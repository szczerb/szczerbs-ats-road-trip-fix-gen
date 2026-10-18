---
id: TASK-0036
title: Prepare report-free publication copies of jobs r3 and tanks r0
status: done
priority: high
repositories: [.]
depends_on: [TASK-0026, TASK-0028, TASK-0034]
owner: shared
---

# Goal

Prepare replacement downloadable mod archives without internal diagnostic reports, retaining the existing revisions and all accepted gameplay bytes.

# Context

**Documented — maintainer instruction, 2026-10-18:** the maintainer removed the two GitHub releases after report-path disclosure was identified, and requested new packages without those files and without revision changes. This authorizes local preparation, not a release upload or push.

**Observed locally:** `mod_writer.write_mod` unconditionally embeds `road_trip_fix_report.json`. The jobs/tank workflows supply local configuration, work-directory and source-package paths for internal traceability. These diagnostics were included in the earlier release assets. Neither package's custom player description refers to the report, and gameplay resources do not depend on it.

# Scope

Two new publication copies under ignored timestamped generated outputs. Remove only `road_trip_fix_report.json`; preserve every other member, filename, manifest version, description and icon exactly. Keep original archives unchanged. No source-generator change, map-package repack, game launch, profile edit, publication or new gameplay claim.

# Implementation Plan

1. Identify the exact original archives by their previously inspected release SHA-256 digests.
2. Write new `.scs` copies omitting only the diagnostic member, retaining jobs `1.61-r3-experimental` and tanks `1.61-r0-experimental`.
3. Verify member inventories/bytes, ZIP CRC, path absence, versions and original immutability; obtain an independent bounded review.

# Acceptance Criteria

- Both requested archives exist with unchanged filenames and version revisions.
- No report/audit file or previously identified personal path remains inside either deliverable.
- All retained members are byte-identical to the accepted originals.
- Original archives remain unchanged; verification evidence stays outside the downloadable `.scs` files.

# Verification

**Observed locally — 2026-10-18:** the only removed member in each archive is `road_trip_fix_report.json`. Jobs retains four members, tanks five. All retained member bytes, including the manifests, descriptions and icons, match the originals. CRC checks pass and the known personal-path prefixes are absent. The old source SHA-256 values, sizes and modification times remain unchanged.

Publication copies are local artifacts, excluded from Git, under `local_outputs/generated/2026-10-18_22-43-45/`:

| Package filename | Bytes | New SHA-256 |
| --- | ---: | --- |
| `szczerbs-road-trip-job-types-compat-mustang-1.61-r3-experimental.scs` | 122472 | `473467135df149f457c1832ae20040c333bc8eacd69e89da159ab127796b71af` |
| `szczerbs-road-trip-reasonable-gas-tank-upgrades-1.61-r0-experimental.scs` | 39344 | `14b6dfc1f393076337bb29c29967b53b468660052c5ae32b8009ebd0471daab1` |

The earlier whole-archive fingerprints remain valid for the historical originals. The new outer checksums differ because the report members were removed; no revision bump was made, as expressly requested. `SHA256SUMS` is beside the deliverables, outside both archives.

Root performed repackaging and exact-member verification. GPT-6 Luna/low independently reviewed the writer/workflow cause and both original descriptions, then checked the new archives. Detailed evidence and the one-run preparation script are ignored under `local_outputs/work/2026-10-18_22-43-45/`. Runtime tests were not rerun: no generator code or retained package content changed. The standard generators still embed diagnostic reports; these publication copies are a separate preparation step. License and third-party notices are unchanged.

# Links

- [Current state](../../project/CURRENT_STATE.md)
- [Jobs guide and historical handoff](../../reference/PRACTICAL_COURIER_GENERATOR.md)
- [Tank guide and original fingerprint](../../reference/REASONABLE_GAS_TANK_UPGRADES.md)
- [Generated-mod publication terms and limits](../../reference/SCS_MOD_PUBLICATION_TERMS.md)
