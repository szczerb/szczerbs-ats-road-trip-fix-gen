# ADR-0012: Preserve irregular standalone rest geometry during action-only edits

**Partially superseded by [ADR-0017](ADR-0017-separate-car-rest-marker-geometry.md):** retain conservative proximity and exact source geometry; clone separate car-only twins instead of changing the original action token.

## Context

Date: 2026-10-18. Broad rest generation found existing standalone map triggers with crossed edges or repeated XZ vertices. ATS Expansion has a truck/bus trigger with no vertex-proven car neighbor. These are original source bytes, not damage introduced by generation. The user wants local car permission while preserving trucks and accepts extra permissions from bounded proximity inspection. That instruction explicitly discussed map boundaries; applying a conservative proximity fallback to malformed source geometry is an implementation decision recorded here, not a new user quote.

## Decision

For an original standalone trigger whose finite vertices, activation flags and serialized rest action are independently supported, preserve every original geometry/node byte. An existing irregular car shape suppresses an addition only when a pair of original vertices proves separation within the configured radius. If no such neighbor is found for an irregular truck shape, add car permission by changing only the validated truck action token to the private truck/bus/car action. Do not repair its shape or guess its interior. Report the original defect and conservative proximity method explicitly; this may add an unnecessary car permission where a nearby car polygon interior was missed.

This support does not waive unknown activation flags, unsafe action layouts, nonfinite data, ambiguous definitions or unsupported placement transforms. Those remain blockers. Ordinary polygons retain exact minimum XZ shape-distance selection. Descriptor clones retain exact geometry/topology and raw flags; observed PPD partial activation bit `0x4` is preserved during token replacement.

## Consequences

An unrelated malformed source boundary no longer blocks an entire otherwise supported map package. Coverage means supported byte edits and a disclosed bounded/conservative proximity policy, not an exact absence proof around malformed areas. Original truck activation geometry is preserved; actual car activation and fatigue recovery remain manual tests. See [source triage](../../reference/REST_LEGACY_LAYOUT_TRIAGE.md), [processor limits](../../reference/COMPATIBILITY_PROCESSORS.md), and [TASK-0024](../../tasks/done/TASK-0024-deliver-overnight-test-mod-batch.md).
