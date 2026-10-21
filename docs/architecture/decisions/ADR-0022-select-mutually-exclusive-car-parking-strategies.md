# ADR-0022: Select mutually exclusive car-parking strategies

**Implementation follow-up — 2026-10-21:** [ADR-0024](ADR-0024-compose-complete-realistic-map-replacements.md) and [realistic r10](../../reference/REALISTIC_MAP_REPLACEMENTS_1_61_R10.md) implement complete original-stack presets and exclusive station bays. The unimplemented/finite-policy wording below records the decision at its original increment. The complete realistic preset now follows accepted whole-facility decisions with provisional inclusion of unknown fuel facilities; retained G2 artifacts remain historical evidence.
## Context

**Documented — user direction, 2026-10-21:** derived station car bays are an alternative to enabling truck parking for cars. A generated mod should use either the simple truck-area approach or the dedicated car-bay approach. This clarifies the earlier possibility of later distance/density integration: combining both strategies is outside the currently requested behavior.

[ADR-0008](ADR-0008-compose-processors-and-local-rest-polygons.md) and [ADR-0017](ADR-0017-separate-car-rest-marker-geometry.md) define the existing local truck-area rest strategy. [ADR-0018](ADR-0018-isolate-source-pinned-station-parking-poc.md) isolates the station-bay research. [ADR-0021](ADR-0021-compose-explicit-station-parking-batches.md) deliberately retained standard r9 fixes beneath F BATCH r1. That historical test setup contains both kinds of generated parking; it is not the desired final alternative-mode packaging. See the [eight-site feedback](../../reference/STATION_PARKING_FORECOURT_TOUR_FEEDBACK_2026_10_21.md).

## Decision

Accept two mutually exclusive strategies for parking additions in a generated mod:

| Strategy | Generated parking additions |
|---|---|
| Existing truck-area access | Independent native car-only twins of qualifying original truck/bus rest areas, preserving the existing proximity policy and source geometry. No newly inferred station bays. |
| Dedicated station car bays | Painted or geometry-derived car-sized station parking selected by the station planner. No generated car eligibility/twins on truck rest areas. |

These are conceptual strategy names, not newly implemented CLI options. Fuel remains an independently selectable feature and may be composed with either strategy. Existing original/native car parking and original truck/bus actions remain preserved; exclusivity concerns our generated additions, not removing source-authored facilities.

**Consequence of exclusivity:** the dedicated-bay strategy must not silently fall back to enabling truck spaces at stations with no acceptable candidate. Report the skipped/rejected site and reason. Do not blend the two modes per station using distance or density rules under this decision. Previously discussed integration remains a separate future request.

An effective input stack can already contain generated truck-area car additions from r9. Layering a bay overlay above it does not remove those additions, and whole-sector load order does not merge independent fixes. Future dedicated-bay packaging must use an explicitly audited baseline/composition that excludes those generated additions while retaining selected fuel/price/context repairs and source-native actions. The exact implementation and user-facing selection interface remain follow-up work; this decision does not prescribe destructive edits to existing archives.

Validate incompatible selections before writing output. Package names/descriptions and reports must clearly identify the chosen strategy, dependencies and replacement instructions so that users do not accidentally enable both alternatives. Do not infer incompatibility solely from two filenames or rely on load priority to cancel parking resources.

## Consequences

This is an accepted product/interface requirement, **not an implemented generator change**. The existing `rest` processor and separate station commands retain their current behavior until a scoped implementation. No new CLI flag, regenerated mod or installation action is delivered here.

The original F BATCH/r9/N2 test setup and user results remain valid historical evidence. Its unchanged archive must not be relabeled as an exclusive dedicated-bay package, and the user need not change the current installation for this documentation update. The r9-retaining premise of ADR-0021 is superseded only for future exclusive-mode output; its batch composition, source pinning and geometry guards remain applicable.

Future verification must inspect the complete effective output/dependencies for generated truck-area additions in dedicated-bay mode, including standalone and prefab triggers. Test explicit rejection of both strategies together, no-candidate behavior without fallback, fuel/context preservation, and original car/truck action preservation. Gameplay usability and rest outcomes remain separate from structural exclusivity checks.
