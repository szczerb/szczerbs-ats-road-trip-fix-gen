---
id: TASK-0009
title: Build a same-position truck and car fuel experiment
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0008
owner: agent
---

# Goal

Generate a new Helena-area test mod with a truck interaction and a car interaction at exactly the same position/orientation, preserving the original truck records. Complete the implementation and static verification; actual coexistence is validated separately in TASK-0007.

# Context

**Documented — user report:** sample 1 allows car refueling but removes the target from the truck map. The user explicitly requests two overlapping interactions, one for each mode. A second PPD locator alone is insufficient as an implementation assumption: the placed prefab also owns a serialized service and map node.

# Scope

- Use the same pinned eastern Helena single-pump fixture and immutable original ATS Expansion data.
- Establish the reviewed map-sector and companion-data layout before adding any records.
- Generate a separate deterministic experimental package, with original truck interaction retained and a car interaction at identical coordinates/rotation.
- Keep source archives, generated assets and research reports ignored. No installation, game/editor or profile operations.

# Implementation Plan

1. GPT-6.1 Sol / high: bounded binary-map/source research and design review, read-only tracked files, ignored research outputs only.
2. GPT-6 Luna / medium: bounded sector/companion inventory and UID/record cross-checks, same read-only ownership.
3. Root: implement guarded generation, structural tests, sample packaging and documentation. Reuse the current experimental branch.
4. Verify counts, links, unique UIDs, exact transforms, retained original records, source hashes, package integrity and deterministic regeneration. Runtime overlap/filtering remains TASK-0007.

# Acceptance Criteria

- A new test package is produced from fingerprinted original data; it does not depend on sample 1 being installed.
- Original truck locator/service/node are preserved; added car interaction has exactly matching position/orientation.
- All affected record counts/references and companion data are accounted for with source evidence and bounded validation.
- Unsupported/mismatched layouts or collisions fail clearly; tests and documentation checks pass.
- Test instructions specify replacement of earlier samples, load priority and both-mode icon/refueling checks without claiming unperformed success.

# Verification

Completed generation/static milestone, 2026-10-17, ATS 1.61.3.18 / ATS Expansion 23.0:

- GPT-6.1 Sol / high researched pinned TruckLib map/node/service/payload sources, independently checked world-transform agreement with the source PPD (error below 1/256 fixed-point increment), reviewed implementation and the actual ZIP, and reported no remaining correctness findings. Source/evidence files remain ignored under `local_outputs/research/overlap/`.
- GPT-6 Luna / medium inventoried the selected sector and companions, identifying original service/node/reference bytes and hashes. The same delegate owned only `tests/test_overlap_fuel.py`, adding five bounded structural/CLI/guard cases. Root reviewed/extended its assertions and integrated all implementation/documentation.
- Added `generate-overlap-fuel`, schema-2 recipe, guarded service/node duplication and sample-specific mod-manager metadata. A source-layout check caught an incorrect assumption about the final item being a service; the real source ends with a 165-byte Company. The implementation preserves opaque items and does not assume a final item type.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: **48 tests passed**, including five overlap cases covering exact transforms, original truck/opaque preservation, reciprocal references/counters, table/UID/owner rejection, companion drift, sample-1 input rejection, experimental gate and three-resource packaging.
- Real generated sample: 105,307-byte ZIP, three gameplay resources, private alias `rtp1f50062a`, original 77-byte truck service and 56-byte truck node retained, original full 22,176-byte node table and final Company retained, two identical-transform GAS records with flags 0/1. Sector grows by 141 bytes to 95,085; item/node counts become 320/397. All source/companion/resource fingerprints, CRC, alias references and precise cloned-record differences passed independent and root checks.
- A second CLI generation from identical snapshot/package paths was byte-identical (SHA-256 `fe783c39547cb59980278db4e9c2314bf0c0983477480c47291f937b4c7b1347`). The four source companions remain unchanged and absent from the generated ZIP. No input archive, generated sample 1, profile, game installation or mod-directory file was modified.
- Documentation reading path, 42 Markdown files / 282 relative links, nine task metadata/status/dependency records, recipe references and Git exclusions checked; `git diff --check` passed. Sources, downloaded references, original images and generated packages remain outside tracked changes.

Runtime boundary: no game/editor validation occurred for sample 2. The user must disable sample 1, enable sample 2 above ATS Expansion, and compare both-mode icons plus actual truck/car refueling at the same dispenser. Overlap/filtering/marker/reload behavior remains TASK-0007; no dual-vehicle gameplay success is claimed.

# Links

- [Previous generator](../done/TASK-0008-prepare-starter-area-sample.md)
- [Active gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [User test evidence](../../reference/VALIDATION_RESULTS.md)
- [Single-pump design](../../architecture/decisions/ADR-0003-allow-pinned-single-pump-sector-experiments.md)

- [Sample 2 and reproducible test instructions](../../reference/OVERLAPPING_FUEL_SAMPLE.md)
- [Additive experiment decision](../../architecture/decisions/ADR-0004-add-pinned-overlapping-fuel-services.md)
