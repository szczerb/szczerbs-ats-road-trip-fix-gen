# ADR-0010: Preserve contexts when generating prefab aliases

## Context

Date: 2026-10-18. Static courier analysis found 14 Company-parent prefabs whose WCE r3 private rest aliases lacked the original `truck_dealer` classification. Runtime job loss was unverified. The user now authorizes implementation and a refreshed morning test batch.

## Decision

After selected fuel/rest plans compose their edits, trace each changed placed prefab UID through original, intermediate and final model identities. Every generated private prefab definition requires a proven lineage to an effective original definition. Copy exact supported original context tags to uniquely named additive units in a source/map-specific resource; do not infer classification from names or assets.

Block publication for missing lineage, conflicting effective tag sets, duplicate unit IDs, resource collisions, or disagreement between explicit exclusion comments and live classifications. Comment-only exclusions and unclassified originals remain untagged. An existing alias classification must match the original; it cannot silently add eligibility to an excluded/unclassified original. Do not treat documentation comments as runtime filters that justify dropping live tags.

Keep existing Company records, geometry and all fuel/rest payloads unchanged except their already selected edits. Courier report-only analysis still examines the original effective stack and emits no resources. Context preservation is an invariant of prefab cloning, not a new optional courier fix topic.

## Consequences

Generated map packages gain distinct additive context resources and a lineage/classification report. Source-specific fixes remain directly above their own sources; context resource paths and unit IDs must not collide across the complete batch. Static equality establishes preserved inputs, not runtime offers or completed courier deliveries.

See [TASK-0019](../../tasks/done/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md) and [marker evidence](../../reference/COURIER_MARKER_RESEARCH.md).
