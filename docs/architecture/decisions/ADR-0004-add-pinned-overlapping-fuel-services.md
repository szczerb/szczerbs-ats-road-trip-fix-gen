# ADR-0004: Add pinned overlapping fuel services

## Context

Date: 2026-10-17. The first Helena conversion allows user-reported car refueling but removes the point from truck-map mode. The user explicitly requests truck and car interactions at exactly the same location. [Sample evidence and layout](../../reference/OVERLAPPING_FUEL_SAMPLE.md) establish that adding a locator alone would omit the corresponding serialized map service/node.

## Decision

Add separate `generate-overlap-fuel` with a schema-2 recipe for the original inspected single-pump fixture. Preserve the original truck GAS record, service and node, and append a car GAS record/service/node with byte-identical position/rotation transforms. Retain one placed prefab instance using a private alias and a private two-locator PPD. Add a second slave reference, update item/node counts and preserve all other original item/node bytes. Generate deterministic unique IDs and check the target sector/companions for collisions.

Require pinned `.base`/PPD and four companion hashes, reviewed map 907/node-table boundary/counts, the supported original `02003` configuration and one-service ownership, an empty layer, and a zero visibility-child trailer. Do not implement a general item serializer or infer unknown boundaries. `.data` is UID-keyed and services have no separate payload in the inspected parser; original prefab control-node count remains unchanged, so companions remain untouched.

This partially supersedes [ADR-0003](ADR-0003-allow-pinned-single-pump-sector-experiments.md)'s count/length preservation constraint only for this separate additive experiment. Existing conversion and descriptor-only commands retain their semantics. Package naming/display identifies sample 2 and directs the user to disable sample 1. No live installation or game/profile operation is authorized as an incidental generation step.

## Consequences

The new candidate tests both vehicle modes at the same physical dispenser while retaining original truck records, rather than partitioning visible dispensers. Runtime filtering/overlap, marker behavior, successful purchases and reload behavior remain unverified. Full-sector conflicts and source-version pinning still apply. Collision checks do not cover arbitrary objects outside the selected sector/companions. [.desc version and unknown payloads](../../reference/OVERLAPPING_FUEL_SAMPLE.md#why-companions-remain-unchanged) remain opaque and untouched.

[TASK-0009](../../tasks/done/TASK-0009-build-overlapping-fuel-pair.md) completes generation/static checks; [TASK-0007](../../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) remains the game-validation gate. Courier behavior and multi-pump/general-map support are outside this narrow increment.
