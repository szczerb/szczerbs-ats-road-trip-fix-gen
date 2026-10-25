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

## Native-bank completion and clearance

A materially covered bank must not receive a colocated whole-bank twin. Complete a proven same-bank gap by taking the exact simple union of its original native polygon and the source paint footprint, retaining the source item/marker identity, all original node identities, flags, tags, action bytes and eligibility. Preserve concave boundaries instead of bridging maneuvering space with a convex hull. Native-grid intersections are rounded outward within the reported small serialization budget; original boundary intervals and vertical bounds remain retained. Original source coordinates and nonplanar boundary heights supply the height evidence; only newly added edges receive the project's conservative 10% grade guard. This guard is not an engine limit. Never extend a car-shared or unresolved action. Truck/bus source eligibility remains exact; completion intentionally serves that existing rest contract rather than changing a global vehicle policy.

Keep a source bank already covered to at least 99.5% by native geometry unchanged even without partial-contact activation; a paint-edge sliver is not a reason to duplicate a marker. Retain the existing 95% exception for proven native partial-contact banks. Partial regions otherwise receive constrained union planning or an explicit unsafe/unknown diagnosis, not a facility-wide exemption.

Inspect source static-model KDOP envelopes in the original 3x3 base/aux neighborhood. Parked traffic and ground/accessibility markings are not physical blockers. Interior permanent or unidentified model overlap blocks newly activated space. A small curbside prop may narrow an additive bank by at most 1.5m while retaining at least 20m of truck depth; report the original paint and exact refinement. These envelopes are conservative proxies, not a complete physics-mesh proof. Shared root node copies in other sectors block native mutation until a cross-sector extension contract is proven; original graph consistency takes precedence over silently changing one copy.

Cache immutable source classification/model records across owner partitions, without allowing staged car/fuel/new-truck additions to become original coverage. Source Company semantic cities provide approximate human locators; label them as nearest references, not road-access or city-boundary facts.
