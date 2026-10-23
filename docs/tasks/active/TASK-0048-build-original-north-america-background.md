---
id: TASK-0048
title: Build an original standalone North America background for ATS 1.61
status: active
priority: high
repositories: [.]
depends_on: []
owner: shared
---

## Goal

Deliver an original, reproducibly generated geographic backdrop and one statically verified experimental package for manual ATS 1.61 testing.

## Context

User goal objective, 2026-10-23: replace vanished North America Background Map 5.3 and the dependent N2 overlay. Read newer retained research branch without merging unrelated station-parking work. No game launch, installation, profile edits, push or publication is authorized.

## Scope

Original land/water/borders/labels for contiguous USA, Alaska, Canada and Mexico; configurable game-coordinate calibration; standalone material/texture/definition graph; Road Trip icon visibility; precise priorities and licensing. No playable map sectors, vehicle data or Ford dependency.

## Implementation Plan

1. Inspect actual installed resource formats, effective source priorities and geographically distributed anchors.
2. Pin public-domain geography and permitted font/tool inputs; implement deterministic renderer and package validator.
3. Calibrate, quantify residuals and inspect overall/regional previews.
4. Verify reproducibility, resource closure and regressions; commit command/provenance and prepare manual handoff.

Delegation (actual): GPT-6 Luna/medium owns read-only source/priority inventory and ignored calibration-inspection scratch; GPT-6 Luna/high owns read-only engine resource research and ignored engine-inspection scratch. Main agent owns tracked implementation and integration. All independent findings are reviewed before incorporation.

## Acceptance Criteria

- One authoritative standalone .scs with requested title/author/version; original artwork, no external background/N2 includes or Ford dependency.
- Reproduction command, versioned configuration, source hashes/licenses and calibration error evidence.
- Overall/regional alignment previews examined by an agent.
- All meaningful offline checks pass; runtime acceptance explicitly remains with user.

## Verification

**Observed locally — 2026-10-23:** all four implementation milestones completed for the offline experimental handoff. Starting branch: `codex/north-america-background` from master `445ef58`; inspected newer research at `2d7394d` read-only without merging unrelated work.

- Root implemented the original background module, source/font fetcher, pinned configurations, renderer, deterministic ZIP/resource validation, original icon and reproduction/manual-test documentation.
- GPT-6 Luna/medium inventoried actual source/DLC priorities, identified the ProMods-over-WCE Vancouver override, and supplied/rechecked 52 actual effective CityArea references. Root reviewed geographic joins and corrected same-name ambiguity before integration. A second independent pass verified every source sector hash, item/node UID and XZ, and every Natural Earth ID/coordinate, with zero discrepancies.
- GPT-6 Luna/high inspected stock MAT/TOBJ/embedded DDS/map-header contracts, source collisions and sector rectangles; root reviewed its raw evidence and corrected an intermediate sign error in the sector-rectangle report. Final installed/supplied bounds pass. Both root and delegate inspected overall and all five regional previews.
- Luna/high independently audited the final 22-member archive: exact allowlist, CRC, custom dependency closure, stock texture fields, dimensions, masks and manifest ID. Root's final engine-schema pass caught a 13-character internal manifest token missed by the generic parser; changed it to `.szczerb.na_bcg` and added a dedicated rejection test. Earlier 21:38/21:42 builds are explicitly superseded, not for testing. Final archive differs only in that manifest member; pixel previews remain identical.
- Authoritative run `2026-10-23_21-48-34`, archive SHA-256 `913ff62169b2dd7729fe16a0074d4d099d9cdd795c2b785a83a7adf32e32bac4`. A full repeated build at `21-49-32` matches the complete archive bytes. Both builds use the freshly re-downloaded, verified cache, not just the earlier downloads.
- The fetch command passes from an empty ignored cache for all five data archives and the pinned font package/member. No system packages, source inputs, game installations or profiles were changed.
- `PYTHONPATH=src <run-venv>/bin/python -m pytest -q`: **292 tests**, including 11 background cases. Full log retained beneath `local_outputs/work/2026-10-23_21-16-53/`. A semantic current-stock comparison permits only geographic camera/size/zoom groups to change; every unrelated field remains equivalent.
- Calibration: 34 fit / 18 check, selected affine check RMS 2,412 units, maximum 6,381 Fairbanks. The optional thin-plate alternative generalizes worse; neither model supplies a physical survey or a blind final accuracy test. Sparse uncalibrated regions and runtime UI behavior remain explicit limitations.

Large inputs/reports/tools/PNG/artifact staging remain ignored in the timestamped work/generated runs. Runtime testing is an explicit handoff boundary, not an acceptance claim. No game launch/install, live-profile edit, push, publication or history rewrite occurred.

## Links

- [Current state](../../project/CURRENT_STATE.md)
- [Authoritative package and manual handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R0.md)
- [Engine/data/calibration research](../../reference/NORTH_AMERICA_BACKGROUND_RESEARCH.md)
- [Reproduction configuration/command](../../examples/north-america-background/README.md)
- [ADR-0025](../../architecture/decisions/ADR-0025-generate-original-geographic-backgrounds.md)
- Goal objective attachment supplied by user on 2026-10-23.
