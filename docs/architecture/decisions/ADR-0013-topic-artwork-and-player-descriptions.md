# ADR-0013: Package topic artwork and readable player descriptions

## Context

**Documented — user requests, 2026-10-18:** fuel/rest fixes lost their fuel-only image when rest was added. The user wants fuel/parking imagery, separate Mustang job art, readable paragraphs and the complete known map priority list with the current fix clearly marked in parentheses. [TASK-0025](../../tasks/active/TASK-0025-refresh-mod-icons-and-player-descriptions.md).

**Observed locally — ATS 1.61 project, inspected 2026-10-18:** r4 map and r0 courier packages have no icon field. Omitting fuel-only art was deliberate under [ADR-0008](ADR-0008-compose-processors-and-local-rest-polygons.md), but combined-scope replacement artwork was missing. The user is testing those payloads independently; metadata changes should preserve that experiment.

## Decision

Accepted 2026-10-18. Extend [ADR-0005](ADR-0005-standardize-fuel-package-metadata.md) and supersede ADR-0008's combined-art omission once suitable art is available.

- Select reviewed 276x162 JPEGs by exact known map label and selected topics. Combined `fuel`/`rest` uses fuel/parking art; fuel-only keeps the historical C preset; rest-only has no automatic preset yet. Unknown maps receive no other map's labelled artwork. Explicit valid icons remain supported.
- The separate courier generator uses its own preset and accepts `--icon`. Its new headline is `JOB TYPES COMPAT`; actual display name and gameplay scope remain Practical Courier Jobs.
- Store original authored small exports and exact image prompts in Git. Store large originals under ignored run directories. Runtime packaging reuses static bytes and never calls an LLM or edits embedded labels.
- Render English descriptions in a dedicated module. Include paragraphs, actual selected topics, dynamic courier counts and the confirmed full map/source sequence, with exactly one `(THIS MOD)` marker. Describe OtherMaps as price-only. State effects and placement without turning static checks into gameplay promises.
- Advance current map/courier defaults to r5/r1 so the refreshed release can be distinguished from r4/r0. Keep legacy fuel r2. Revision is explicit, not automatically incremented.
- For this handoff, repackage the accepted eight candidates with only metadata changes. Require exact resource-path, byte, hash and inventory equality against r4/r0; retain old archives. Incrementing versions does not authorize gameplay changes.

## Consequences

The user initially selected M2's navy fuel/parking scene, then explicitly selected the corrected four-Ford M2D variant for map r6. Earlier proposals remain as history. J1B courier art is provisional pending selection. [Art guide and prompts](../../../assets/mod-icons/README.md). Shared fuel/rest family artwork on OtherMaps does not imply station or rest changes; its description states the narrower scope.

The priority list describes this supplied combination. Other replacements and unknown combinations still require review; no automatic profile inspection is implied. Human descriptions and artwork must be maintained when supported topics or the known combination change.

The [current r6/r1 handoff](../../reference/MOD_METADATA_REFRESH_1_61_R6.md) and historical [r5/r1 handoff](../../reference/MOD_METADATA_REFRESH_1_61_R5.md) record hashes and verification. Fuel billing, rest and new job acceptance/delivery still require the existing manual tests. No live mod installation or profile edit is included.
