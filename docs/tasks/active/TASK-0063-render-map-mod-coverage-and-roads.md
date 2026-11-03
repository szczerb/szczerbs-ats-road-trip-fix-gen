---
id: TASK-0063
title: Render ATS map-mod coverage and roads
status: active
priority: medium
repositories: [.]
depends_on: []
owner: shared
---

# Goal

Render high-resolution map-mod footprint and road images for individual archives, comparison on shared bounds, and a declared effective load order. Deliver source in a reviewable PR and local images from the active ATS setup.

# Context

**Documented** — The maintainer wants to spot visual gaps and overlaps among map extensions and connectors using the original North America background. The exact supplied sector grid preserves holes, detached tiles, and empty replacements.

**Observed locally** — The background branch was squash-merged into the default branch in PR #2. This feature uses a dedicated worktree based on the merged generator. The validation atlas is the full 16,384-pixel original artwork retained by r4.

# Scope

- Read local and Workshop archives and use exact active versions for the development validation.
- Draw supplied sector coverage, native road curves, hidden roads, supported prefab links, and nearby winning stock roads in the effective view.
- Keep all game data, validation images, logs, and machine-specific paths local. The renderer reads inputs without changing the game or profile.

# Implementation Plan

1. Integrate the renderer into the CLI with explicit comparison and effective-stack modes.
2. Use verified road curve and prefab map-point logic, and report unsupported or unresolved records.
3. Review the active stack and produce a local image index with overview and connector details.

# Acceptance Criteria

- Standalone PNG for every readable sector-bearing active mod and a recorded outcome for every active entry.
- Exact tiles, north-up atlas registration, per-resource precedence, readable overlap and stock context, and machine-readable diagnostics.
- Authored regression tests, path hygiene, and source-only PR ready for review.

# Verification

- GPT-6.1 Sol, medium effort, owns native geometry and tests. GPT-6 Luna, low effort, owns live log inventory and independent local validation. The lead owns CLI, image composition, integration, and review.
- **Observed locally** — The log inventory records 19 mounted local mods and 12 mounted Workshop mods on ATS 1.61.3.23s. The ProMods and Western Canada precedence controls agree with the active mount order.
- Live image and full suite verification are in progress.

# Links

- [Renderer usage](../../reference/MAP_MOD_RENDERER.md)
- [Background r4](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R4.md)
