---
id: TASK-0010
title: Brand gas station fix packages and prepare icon proposals
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0009
owner: agent
---

# Goal

Give fuel compatibility packages consistent user-requested metadata and offer three simple pump/car icon designs before broader generation.

# Context

2026-10-17: the user reports successful refueling with both vehicles using overlapping sample 2. The old manifest uses a research author, sample-specific title, prototype version and no custom icon. Metadata changes must preserve the tested gameplay payload.

# Scope

- Fuel package name `szczerb's Road Trip Gas Stations Fix for <short map name>`, author `szczerb`, version `<game major.minor>-r<revision>-experimental`, initially `1.61-r0-experimental`.
- Explicit short map name, revision and icon CLI inputs; deterministic root metadata/icon packaging and provenance.
- Three original raster proposals with `GAS STATIONS FIX` above pump/nozzle and passenger cars, map name below. Small authored JPEG exports may be tracked; generated originals and `.scs` packages remain ignored.
- Record both-mode user validation without claiming broader station, courier or reload validation. No mass generation, gameplay changes or profile installation.

# Implementation Plan

1. Confirm icon and manifest requirements against SCS documentation.
2. Delegate icon proposals to GPT-6 Luna / medium; ownership only ignored artwork outputs. Delegate CLI wiring/tests/tooling guide to GPT-6 Sol / medium with explicit file ownership. Root implements metadata serialization, integrates and reviews.
3. Package a branded version of the same pinned sample, compare gameplay payload hashes, verify metadata, JPEG canvas, determinism and documentation links.
4. Offer the proposals for preference; a provisional icon choice is reversible and does not hold up metadata implementation.

# Acceptance Criteria

- Fuel commands emit exact requested title, author and experimental revision format, with explicit map name.
- Icon exports meet the documented JPEG 276x162 canvas and use original artwork, not the ATS logo.
- Three proposals are available with prompts/provenance. The user-selected design C is clearly identified.
- Branded sample retains all three tested gameplay resources byte-for-byte. Old sample remains unchanged.
- Tests, documentation checks and artifact exclusions pass; local commit records the result.

# Verification

2026-10-17: completed. Primary [SCS Mod manager documentation](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager) checked for metadata fields, truncation and exact JPEG canvas. GPT-6 Luna / medium generated three separate original icon proposals with built-in imagegen; root inspected the originals and final JPEG exports. The user explicitly selected C. Prompts and three small exports are tracked; raw originals remain ignored.

GPT-6 Sol / medium implemented CLI wiring and focused tests, updated the tooling guide, then independently reviewed the final package and root writer integration. Root implemented safe metadata serialization, JPEG frame/dimension validation and report fields, reviewed all delegates' changes and updated evidence/navigation.

- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: **51 passed**, including metadata string escaping, custom revision, absent/invalid map name, invalid revision, invalid icon framing/dimensions, reserved icon collision, deterministic archive/report agreement and existing gameplay guards.
- Branded sample generated twice from original snapshots/map/recipe with explicit map name, revision 0 and selected C icon. Both outputs byte-identical: 134,087 bytes, SHA-256 `235d00057939c1074bf434e11a3f8503093bd7179a269c6ff9178f7b7f1e40e3`. All three gameplay resources exactly equal historical sample 2; historical package SHA-256 remains `fe783c39547cb59980278db4e9c2314bf0c0983477480c47291f937b4c7b1347`.
- All three JPEGs decoded using FFmpeg and visually inspected at 276x162. Packaged `mod_icon.jpg` matches selected C bytes, SHA-256 `5fc8e0d416a338cdc8d4aa3b2ebb00cc71ee593a2c90771eebd8a1d40a9d6ea8`. ZIP CRC, stored entries, manifest/report agreement and unchanged payload hashes passed root and independent checks.
- Documentation reading path, relative links, ten task records/status/dependencies, no dependency cycles and Git exclusions checked; `git diff --check` passed. All five original inputs, generated archives, PNG originals, extracted assets and reports remain ignored. No original archive, game/mod installation or profile was modified.

The both-mode runtime result is attributed to the user's historical sample-2 test in [validation results](../../reference/VALIDATION_RESULTS.md); it is not an agent gameplay run or a claim of map-wide coverage. Reload, controls, multi-point and courier checks remain TASK-0007. Metadata and artwork choices are in [ADR-0005](../../architecture/decisions/ADR-0005-standardize-fuel-package-metadata.md).

# Links

- [Overlapping sample](../done/TASK-0009-build-overlapping-fuel-pair.md)
- [Remaining gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Metadata decision](../../architecture/decisions/ADR-0005-standardize-fuel-package-metadata.md)
