---
id: TASK-0012
title: Inspect map connectors and generate source-preserving fuel fixes
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0011
owner: agent
---

# Goal

Determine whether the supplied Reforma OtherMaps Patch and Western Canada ProMods Connections override fuel data, and generate separate deterministic experimental fixes wherever needed, preserving the connector sector versions and truck interactions.

# Context

**Observed locally, 2026-10-17:** the user supplied both connectors after receiving five map-specific r1 fuel fixes. Earlier overlap checking compared exact changed-sector paths between those five outputs; it neither merged map geometry nor established connector compatibility. The connectors' effective sectors must be inspected before claiming coverage for the combined stack.

# Scope

- Read both new archives and inspect manifests, mounting, sector/resource paths and intersections with existing fixes.
- Extend source-family/dependency inference as needed; use connector versions as the highest source for their additional fix packages.
- Generate and statically verify supported missing car counterparts, retaining every original truck record and connector change.
- Keep original inputs, sidecars, game/profile data and historical outputs unchanged. Store work/output artifacts in ignored Warsaw timestamp directories.
- Record source order assumptions and gameplay boundaries. Do not claim a live profile order has been observed.

# Implementation Plan

1. GPT-6 Luna / medium: read-only connector inventory, metadata, sector intersections and a machine-readable ignored report.
2. GPT-6 Sol / high: connector family/dependency inference and focused workflow tests; own only `bulk_run.py` and `test_bulk_run.py`.
3. Root: review real dependencies, run deterministic generation, verify original/new records and output interactions, integrate documentation and commit.

# Acceptance Criteria

- Both connectors have accurate source metadata and an evidence-backed relevance decision.
- Each needed fix is reproducible with the source command; dependencies/order and required companion maps are explicit.
- Additional fixes retain source-sector contents and truck functionality at the static record level, with complete or honestly blocked coverage.
- Focused/full tests, actual output audits, relative documentation links and ignored-artifact checks pass.
- Runtime checks remain explicitly pending under TASK-0007; no live game/profile installation is performed.

# Verification

2026-10-17: completed for the two supplied connectors and the screenshot-derived supplied-map order. [Connector results](../../reference/CONNECTOR_FUEL_FIXES.md) record source metadata, actual order, output fingerprint, reproduction and runtime limits.

Actual delegation:

| Assignment | Model / effort | Reviewed result |
| --- | --- | --- |
| Read-only archive/definition inventory, inventory reference update, independent output and stock-neighbor review | GPT-6 Luna / medium | Eleven archives; exact definitions/sector scope; all 50 new services and original records verified |
| Connector family/dependency inference, explicit-order preservation, focused tests and cross-sector review | GPT-6 Sol / high | Distinct profiles/icons, no empty-mod requirement, authoritative caller order, 12 focused tests |
| Screenshot inspection, full-stack generation, composed graph validation, documentation and integration | Root | Source priority corrected from screenshots; generated connector-derived sectors; all surviving targets checked |

Checks performed:

- Read both screenshots through `<LOCAL_SCREENSHOT_DIR>/`; recorded the supplied source order rather than assuming ProMods/Western Canada priority from filenames.
- Reforma OtherMaps 40.161 has no map/prefab/PPD assets. All 367 definitions were selectively read; 19 country files change `fuel_price`, with no station-service definition overrides. The source command returned zero targets and no output. This does not establish coverage for unsupplied map families named in its description.
- Western Canada ProMods Connections 1.7.3: all 52 source `.base`/`.aux` files parse. The full explicit screenshot stack produced **50** new car services, including six garage points, across 31 changed prefab instances and **14 source-only sector overrides**, with zero blockers. Output is **2,661,218 bytes**, SHA-256 `3142a6ace997b5102200fc975fead2f34215d2d5a4fcc510380f4a3169de4cbd`.
- Independent archive/graph review passed ZIP CRC, metadata/icon/resource hashes, private alias collision checks, original item order and expected-only prefab/visibility edits. All 50 new service/node pairs have exact truck transforms and reciprocal ownership. All 11,307 original node records, 67 kind-7 and six FuelPump records are unchanged. Reports/scripts are in `local_outputs/work/2026-10-17_23-08-21/verification/`.
- Composed-map review checked 527 changed-sector paths at the confirmed source priority. **2,202** surviving generated truck targets have co-located car counterparts; **3,514** car services in winning fix sectors have valid reciprocal links. Four unrelated stock truck points carried in an edited neighbor sector were independently shown byte-identical to the stock source, outside all generated target lists. Preserve the expanded diagnostic; do not claim all stock points were targeted. The detailed composed report is `local_outputs/work/2026-10-17_23-08-21/verify_composed_graph.json`.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: **116 passed**. Focused coverage includes connector family isolation, distinct names/icons, missing/ambiguous companions, source repetition rejection, and preservation of full and partial explicit priority.
- Work was paused when the user requested time to supply screenshots; the running connection generation was interrupted. Its discarded partial run has no output. The final run uses the later explicit screenshot stack, under `2026-10-17_23-08-21`; the earlier OtherMaps no-output audit remains under `2026-10-17_23-01-39`.
- Final integration checks passed: 53 Markdown files, 362 relative links, 12 task metadata/status/dependency records (no cycles), and 14 input/work/output artifact exclusions. All eleven input archive and one sidecar size/mtime identities match the pre-run snapshot. `git diff --check` passes and no supplied/generated game assets are tracked. No game/profile installation or gameplay operation was performed. The two screenshot-listed higher-priority branding/traffic archives remain unavailable; static findings are limited accordingly.

The original five-map batch remains a historical per-source result. Overlapping package counters must not be added as unique combined coverage. Runtime purchases/access, garages and reloads remain TASK-0007.

# Links

- [Previous full-map generation](../done/TASK-0011-generate-map-wide-fuel-fixes.md)
- [Map-wide command](../../reference/MAP_WIDE_FUEL_GENERATOR.md)
- [Original r1 batch](../../reference/FUEL_FIX_BATCH_1_61_R1.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
