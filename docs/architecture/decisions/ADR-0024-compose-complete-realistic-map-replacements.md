# ADR-0024: Compose complete realistic map replacements from original owners

- Status: accepted
- Date: 2026-10-21
- Task: [TASK-0047](../../tasks/active/TASK-0047-deliver-realistic-map-replacements.md)
- Supersedes: the finite G2 policy as the recommended realistic fuel policy; historical artifacts remain evidence
- Extends: [ADR-0022](ADR-0022-select-mutually-exclusive-car-parking-strategies.md), [ADR-0023](ADR-0023-select-car-fuel-additions-by-reviewed-pump-role.md)

## Context

**Documented — user direction, 2026-10-21:** provide all seven r9 replacements for ordinary career use, with optional incidental feedback rather than another prescribed tour. G01/G02/G06 are approved whole public facilities; G03/G04/G05 must not receive our car additions. Preserve native facilities, prices, source priority, identifiers and courier context. Station bays are an alternative to generated truck-area access, with no fallback.

## Decision

Provide `broad` and `realistic` presets while keeping fuel selection and parking strategy independently configurable. Historical single-source commands and the default broad planner retain their behavior. Realistic selects facility-level fueling with provisional inclusion of unreviewed plausible facilities, and dedicated station bays. Native car facilities remain regardless of our classification.

Mount the declared original game/DLC/map/resource stack once. Reject generated fixes as original inputs. Read staged payloads through an overlay that preserves original provider metadata. Process fuel before parking, and compose every boundary resource deliberately. Partition the final bytes by the winning original resource owner, rather than by whichever processor last touched them. A separate base-game/DLC companion owns stock sectors; it is required alongside the seven source replacements. Resource-only country definitions must be repaired in a replacement that actually loads above their provider; otherwise generation fails.

Preserve established broad fuel aliases/service IDs when the selected groups are unchanged. Partial group selections have distinct identities. Preserve original services/nodes/action data; newly added car interactions have separate identities. Audit complete prefab lineage once after all processors have run; do not ship per-site/per-map context previews alongside the final context file.

A reviewed public model/state includes all relevant original truck fuel groups, even if linked to a Company. Actual garage FuelPump records exclude our garage additions. The reviewed Castores distribution model requires its actual same-parent Company relationship. G04's generic trigger is classified only through a source-pinned Company field-layout relationship and a narrow, measured entrance corridor. That inference is provisional, not ownership, polygon containment or diesel-inventory proof. Other generic triggers and unreviewed models follow the reported uncertainty policy. Names, the word “depot”, original truck eligibility and nearby companies alone do not justify exclusions.

Parking discovers original source-owned GAS placements, rather than a finite site allowlist. Reviewed converted mesh/model/material/state families are gates, not universal geometry knowledge. Prefer individual eligible marked bays, including wheelchair-marked bays; reject hatching/access/circulation/occupancy conflicts through the existing validators. Otherwise consider validated curb-anchored proposals with a 0.15 m measured-curb gap and preference for safe perpendicular poses. Skip unsupported/unsafe/no-candidate locations without adding truck access. P04's reported unreliable addition is explicitly omitted; Mexican broad activation remains unattributed and source-native geometry is retained.

Unsafe per-station fuel transactions roll back completely. Unsupported compound fuel remains unchanged and explicitly reported. Global corruption, ambiguous ownership, conflicting identities or unsafe output must block delivery rather than masquerade as a harmless classification uncertainty. Classification uncertainty normally produces a provisional decision and a coverage row, not an exception. Finished archives and the declared effective stack require independent inspection.

## Consequences

Full replacement packaging is separate from universal station coverage. The supported bay subset and reasons for all skips are reported. Unknown public/private cases remain available provisionally, so the small reviewed catalog does not remove most existing fuel coverage. This intentionally leaves some plausible private facilities eligible until better evidence or ordinary career feedback supplies reusable rules.

The set is source-stack-specific. Changing source priority/version/model overrides requires regeneration. Structural preservation and stable IDs reduce unnecessary churn; static checks do not prove existing-save compatibility, fatigue recovery, billing, collision-free driving or every runtime marker. The user installs the result and reports issues during normal play. Agents do not launch the game, install packages or modify profiles. N2, the background dependency, tank and courier packages remain independent.
