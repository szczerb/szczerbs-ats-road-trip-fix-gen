---
id: TASK-0055
title: Repair detailed texture-size regression without other map changes
status: done
priority: high
repositories: [.]
depends_on: [TASK-0054]
owner: shared
---

## Goal

Deliver a separate r4 testing package fixing only r3's oversized detailed textures. The user explicitly defers zoomed-in quality and additional information layers; retain all other r3 resources and behavior.

## Context

**Documented — user, 2026-10-25:** fix the texture-size regression only. **Observed locally:** INC-0002 correlates an archive-specific DirectStorage request-too-large failure with detailed DDS growth from 4096 to 8192 square. The exact engine request/buffer threshold remains unknown. The working r2 tile budget is the controlled repair target.

## Scope

Resize only the four original r3 detailed textures to 4096 square using the pinned Pillow environment; update only the manifest revision to distinguish the r4 package. Copy all 20 remaining members unchanged, including the overview, map definition, materials, texture objects, icon, description and license notices. Add a reproducible source-pinned recipe and delivery documentation. No geometry fitting, quality redesign, new layers, engine/settings/profile/live-install changes or game launch.

## Implementation Plan

1. Use a surgical postprocess of the exact delivered r3 package, preserving all previous artifacts.
2. Validate actual DDS sizes/pixels/resources and byte-identical non-target members; repeat the build.
3. Delegate independent archive/pixel comparison to GPT-6 Luna/medium, owning only `local_outputs/work/2026-10-25_18-06-28/independent-audit/`.
4. Record authoritative output, source recipe, verification and runtime boundary; commit locally.

## Acceptance Criteria

- Exactly four detailed DDS members and the manifest revision differ from r3.
- Each detailed texture is 4096 square, DX10 BGRA8 sRGB, one mip, opaque, 67109012 bytes.
- Output pixels equal deterministic LANCZOS downsampling of the corresponding original r3 quadrant; overview and all other members are exact copies.
- Existing package validation and a repeated identical build pass; old files stay unchanged.
- In-game restoration is explicitly pending user confirmation; no unrelated changes are included.

## Verification

**Observed locally — 2026-10-25:** the authoritative r4 SCS under `local_outputs/generated/2026-10-25_18-06-28/` has SHA-256 `00e3932434dee49003fbf6f02da925f239939fd2997cbab78a54d5e305f013b4`. The source-pinned recipe resizes the four original r3 detailed DDS files and changes exactly the manifest revision token. All 20 remaining resources are copied unchanged. Existing complete package validation and two focused package tests pass. Repeated generation produces exactly the same SCS hash. Full member/header/CRC/pixel comparison is independently recorded by GPT-6 Luna/medium in its owned audit directory. Main reviews the audit, checks delivery/source links and whitespace before committing. The source r3 archive and geometry inputs remain unchanged. No runtime test, game launch, live installation, settings or profile change was performed; runtime confirmation remains pending.

## Links

- [INC-0002](../../incidents/INC-0002-r3-background-detailed-texture-loading/README.md)
- [Diagnosis](TASK-0054-diagnose-r3-detailed-map-background-loss.md)
- [Source-pinned repair recipe](../../examples/north-america-background/r4/README.md)

- [R4 testing handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R4.md)
