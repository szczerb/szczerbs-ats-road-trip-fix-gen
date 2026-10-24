# ADR-0029: Add independent truck-rest coverage to incomplete facilities

- Status: accepted
- Date: 2026-10-25
- Task: [TASK-0054](../../tasks/active/TASK-0054-complete-incomplete-truck-rest-lots.md)
- Extends: [ADR-0024](ADR-0024-compose-complete-realistic-map-replacements.md), [ADR-0028](ADR-0028-plan-broad-parking-with-independent-service-eligibility.md)

## Context

**Documented — user direction:** improve visually legitimate truck parking left outside a facility's functional rest regions. Native rest presence establishes a facility boundary for augmentation rather than exempting the entire lot. This differs from preserving originally car-supported stations by default and from enabling truck rest areas for cars.

## Decision

Add `improve_truck_parking` / `--improve-truck-parking` as an explicit independent rest policy. It defaults OFF for existing command behavior and is ON in the delivered realistic r13 build. It requires the rest processor. Rest with `parking_strategy=none` is valid only with truck improvement enabled, allowing truck-only analysis/generation without implicit car access. Native-car improvement remains OFF and independently validated.

Run truck planning after staged fueling and car-rest changes, against immutable original ownership/action evidence. Discover functional truck rest without a GAS requirement, classify individual logical parking-region coverage, and report unsupported/ambiguous prefab and standalone cases. Existing truck/car/bus support, fuel selection or any service's skip must not suppress the other services.

Prefer additive independently linked truck-capable car-free groups. Preserve existing native geometry/parameters; any deliberate truck-only extension must retain original coverage and be explicitly audited. Never expand shared car eligibility or globally replace original actions. PPD and standalone flags retain distinct contracts. Use private placed aliases, composed sectors and global context lineage.

Complete generation uses the declared original stack and emits eight source-relative replacements. R12 packages are audit comparators, not opaque generation inputs. Preserve accepted car regions, exact Dawson geometry, fuel identities and country-price provenance. Full discovery and safely supported coverage remain separate claims.

## Consequences

The reporting/configuration schema gains independent truck state and changed-region counts. A one-bank native trigger can coexist with new markers for missing banks. Native-car exemption and local truck-area-to-car proximity rules cannot serve as truck coverage gates. Final emitted archives require independent eligibility, geometry, original-preservation and context/namespace checks; normal career feedback remains the runtime gate.

For covered-bank association, preserve an existing useful native partial-contact marker when one native convex polygon covers at least 95% of its painted bank. Report the mathematical partial state and exact overlap rather than adding a duplicate marker for an inset edge. North Platte's source overlap is 98.0307%, with no far/end shortfall. This exception applies only to retaining an existing partial-contact source; it does not authorize shrinking new regions or ignoring material missing banks. Other partially covered banks remain separate candidates.

Unknown action aliases, per-instance HUD parameters, activation flags and unresolved geometric envelopes cannot establish absence. Retain their bounded uncertainty near candidates and leave overlapping areas unchanged. General additive coverage currently requires an unambiguous original standalone contract anchored through a shared authored compound; native prefab groups participate in coverage where their transforms are proven, and other layouts remain explicitly inventoried/unsupported.
