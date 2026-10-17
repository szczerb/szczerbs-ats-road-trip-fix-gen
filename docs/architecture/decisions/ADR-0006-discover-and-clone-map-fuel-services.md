# ADR-0006: Discover and clone map fuel services

## Context

Date: 2026-10-17. The user reports successful co-located truck/car fueling at the Helena sample and authorizes complete fuel packages for five supplied maps, using a deterministic command pointed at a source map. The original pinned single-point recipe cannot cover arbitrary station layouts. The user also requires read-only inputs and timestamped work/output directories.

## Decision

Add `generate-map-fuel SOURCE --experimental`. Resolve the installed ATS 1.61 baseline and known sibling resource/definition packages; explicitly record the generation order rather than claiming to inspect the live profile. Require complete supported coverage before publishing an archive. Use the approved metadata/icon family, initial full-map revision `r1`, descriptive filenames and Europe/Warsaw `YYYY-MM-DD_HH-MM-SS` run directories.

Independently implement a sequential map-907 structural reader from referenced binary layouts. Reach item boundaries by consuming every preceding record, rather than searching arbitrary bytes. Preserve uninterpreted payloads. Recognize only exact empty legacy 895/901/903 sectors; reject nonempty unknown formats. Inspect source `.base` and `.aux`, then resolve neighboring effective sectors for boundary-spanning parents, services and nodes. Report nested fuel as unsupported; decoration compounds may be inspected without retained geometry.

Associate GAS locators and fuel items using the prefab's Origin-adjusted control-node order, a validated horizontal placement rotation, measured bounded terrain grade and unique geometric matches. Permit incomplete car caches only when every truck matches uniquely and extra car items coincide with a truck. Preserve existing car records. Add missing flag-1 GAS locators and co-located car Service records/nodes, retain all original truck bytes, append reciprocal parent references and update structural counts. Preserve original node records while ordering the resulting table by UID. Extend explicit visibility references and nonzero layer membership where applicable.

A garage FuelPump (kind 35) retains its original record and gains an ordinary car Service (kind 7), following the inspected PrefabCreator order. This is an experimental extension, without a user garage test. Legacy v23/v24 PPDs may be upgraded to v25 only with zero semaphores; v23 spawn records receive their missing zero flags word and subsequent section offsets are updated. Other opaque sections are preserved.

One observed source truck FuelPump crosses into a stock garage whose slave list retains a different, missing historical UID. Accept this narrow case only after unique full geometric matching and ownership checks. Retain the old mismatch and all old references; append only the new car reference. Record the pre-existing inconsistency without claiming to repair it. Ordinary orphan Services and ambiguous cases remain blockers.

This supersedes the recipe-only restrictions of ADR-0003/ADR-0004 for the separate map-wide command. Preserve those historical commands and evidence. Every modification and resource copy is performed by code; no LLM authors binary overrides or per-station patch lists.

## Consequences

Coverage is a static logical-point inventory, not proof of physical car access or successful gameplay at every station. Multi-point stations, garages, legacy descriptors and other maps still need user tests. Reports must distinguish fuel prefab counts from physical station counts. Unsupported cases prevent a purported complete output.

Outputs replace whole sector files and must follow the source stack. Place each fix immediately above its own source map while retaining the relative priority of the maps; collecting all fixes above all maps can resurrect a lower-priority sector. Connection/compatibility patches are separate effective-data inputs and require regeneration if they replace the affected sectors.

HashFS v1 requires deep path discovery; batched disk-backed extraction avoids repeated launches and the definition cache's memory cap. Generated mod contents exclude run timestamps, which remain in external audits, so identical source stacks/settings/artwork can produce identical bytes across timestamped runs. See [generator reference](../../reference/MAP_WIDE_FUEL_GENERATOR.md) and [TASK-0011](../../tasks/done/TASK-0011-generate-map-wide-fuel-fixes.md).
