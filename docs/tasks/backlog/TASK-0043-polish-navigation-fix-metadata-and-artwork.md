---
id: TASK-0043
title: Polish navigation-fix metadata and artwork
status: backlog
priority: low
repositories:
  - .
depends_on:
  - TASK-0042
owner: shared
---

# Goal

Prepare the user-tested N2 navigation visibility fix as a clearly presented experimental package, with final player-facing metadata and dedicated topic artwork, while preserving its reviewed gameplay payload.

# Context

**Documented — user report, 2026-10-19:** both fuel and parking icons are visible in Mustang navigation with N2 at the reported test context. The exact interface, location, zoom and profile were not itemized. N2 is the source-pinned navigation overlay documented in [CAR_PARKING_NAVIGATION_ICONS.md](../../reference/CAR_PARKING_NAVIGATION_ICONS.md), not a parking-generation or map-sector fix.

N1 and N2 already carry experiment-identifying metadata. The remaining work is final player-facing presentation and dedicated artwork, not adding the first metadata to otherwise unidentified experiments. The applicable metadata contract requires a JPEG `mod_icon.jpg` at exactly 276 × 162 pixels and is documented in [MOD_METADATA.md](../../reference/MOD_METADATA.md) and [ADR-0013](../../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md).

# Scope

- Review and finalize the player's display title, description, revision/version, dependency fields and load-order instructions for the N2 overlay, following the metadata contract and clearly distinguishing it from N1 and map-sector fixes.
- Create dedicated 276 × 162 JPEG artwork appropriate to the parking and fuel navigation-visibility topic, then package the reviewed metadata and image with N2.
- Confirm the final package retains the source pins and runtime-accepted navigation-mask gameplay member byte-for-byte; retain the established background-map dependency and precedence.
- Do not change map-sector resources, parking geometry, services, triggers, prices or the navigation heuristic. Do not generate the artwork, edit a metadata package, or issue a new revision while this task remains in backlog. Do not publish or release the package.

# Implementation Plan

1. Re-read the N2 handoff, metadata contract and ADR-0013; decide the final player-facing fields and explicit dependency/load-order text.
2. Produce and inspect the dedicated 276 × 162 JPEG artwork, then prepare a new experimental package without overwriting historical N1/N2 artifacts.
3. Compare gameplay members and source pins against the accepted N2 handoff; record package checks and any remaining user-facing caveat.

# Acceptance Criteria

- The completed package has clear, distinct player-facing title and description, correct version/revision and dependency fields, and explicit load order above North America Background Map and other map-data providers.
- It includes topic-specific 276 × 162 JPEG artwork and meets the metadata contract.
- The only gameplay payload remains the reviewed N2 `def/map_data.sii` change; all other packaged gameplay data, if any, is byte-identical to the accepted N2 package.
- No map-sector, parking-generation, fuel-service or economy behavior changes are introduced, and no public release occurs as part of this task.

# Verification

- **Pending — task not started (2026-10-19):** metadata/package comparison, image dimensions/decoding review and source-pin checks will be recorded when the task moves to active.
- No artwork generation, metadata edit, package revision or publication has been performed for this deferred task.

# Links

- [N2 navigation-icon handoff](../../reference/CAR_PARKING_NAVIGATION_ICONS.md#n2-analogous-fuel-visibility-candidate)
- [Metadata contract](../../reference/MOD_METADATA.md)
- [ADR-0013: topic artwork and player descriptions](../../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md)
- [TASK-0042: test the analogous local-navigation fuel icon mask](../done/TASK-0042-test-local-navigation-fuel-icon-mask.md)
