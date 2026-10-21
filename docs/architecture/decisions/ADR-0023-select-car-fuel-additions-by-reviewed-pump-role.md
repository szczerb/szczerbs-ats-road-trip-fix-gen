# ADR-0023: Select added car fueling by reviewed pump-group suitability

## Context

**Documented — user objective, 2026-10-21:** keep broad compatibility and add an opt-in realistic selection policy that avoids indiscriminate car access to truck/fleet infrastructure. Fuel and parking remain independently configurable; [ADR-0022](ADR-0022-select-mutually-exclusive-car-parking-strategies.md) governs alternative generated parking strategies. [TASK-0046](../../tasks/done/TASK-0046-add-selective-passenger-car-fueling.md) implements this fuel-only increment.

**Observed locally — ATS 1.61.3.18:** native GAS flag/service correlations distinguish car and truck interaction groups, but no inspected field establishes public access rights or chemical fuel inventory. A public Gallon Oil layout uses “depot” in its filename and a Company parent, so neither is a private-fuel classifier. A Reforma freight-distribution layout has stronger combined evidence: same-parent Company, pumps inside its lot, enclosing fence and visible distribution/logistics signage. [Research and evidence](../../reference/SELECTIVE_CAR_FUELING.md).

## Decision

Keep broad behavior as the default. Add immutable `FuelSelectionConfig` with `broad` / `realistic` modes and explicit uncertain-case `skip` / `include` behavior. The delivered selective policy uses `skip` to avoid adding unsupported eligibility while retaining uncertainty in reports.

Classify each original truck-correlated GAS/service group after structural graph validation. Reviewed rules identify exact descriptor/model state and per-spawn suitability roles: `public_car`, `truck_lane`, `fleet_yard`, or `uncertain`, with confidence, reason and evidence. Descriptor SHA-256, variant, placement parts and definition additional-parts pins reject stale values of those fields. PMD/PMG/texture bytes are not general classifier pins; same-path visual overrides remain unvalidated unless separately checked for a concrete batch. Same-parent Company is context, not automatically private ownership; proximity is insufficient. A linked garage FuelPump provides an explicit truck-garage policy exclusion. Roles express suitability for our addition, not diesel-only proof.

Source-pinned layout rules generalize across placements of the same reviewed state; city names, coordinates and placement UIDs do not select suitability. The finite test manifest uses UIDs only to bound/reproduce experiments. Unreviewed layouts remain uncertain, not silently approved or branded private. The current classifier is a conservative reviewed-layout policy, not a universal geometric classifier.

Append car PPD locators only for approved source spawn indices and add only their required service/node twins. Include the subset in private-alias identity. Preserve original car/truck records, nodes, locator sections, price policy and courier context lineage. Intentional policy exclusions do not count as structural coverage failures; malformed source graphs still block even at skipped pumps. Existing car support is retained and reported when it prevents an effective exclusion.

The dedicated finite-site comparison mounts original maps/assets for planning. Reject known generated fuel/rest inputs. For selected policy-excluded groups, ship an explicit original-sector guard where needed, composed with any selected additions in that same sector. This prevents a retained lower broad fix from reintroducing excluded car interactions. State the consequence: other generated fuel/rest changes in those replaced sectors are temporarily omitted; original source features remain intact. This is fuel-only research, not the full realistic preset.

Record the original fuel service resource, service node and all resolved node resource paths in selective decisions. The finite workflow rejects skipped groups with services or required nodes outside their exact pinned parent resource; it does not claim to guard an unpinned neighbor. An actual adjacent-sector fixture must fail before archive output. The delivered six-site scope separately passes this conservative gate.

Keep source-relative general generation available through the existing commands with opt-in policy configuration. A general selective package replaces its same-source broad fix; it is not an automatic subtraction overlay. The finite comparison's protective guards are a separate explicit packaging behavior and its complete effective stack must be audited.

## Consequences

Selective coverage is intentionally narrower and depends on reviewed model states. Unknown cases can later be reviewed without changing source-native facilities. Drift errors fail closed and require an evidence update; an explicit uncertainty policy can include unreviewed points without relabeling them suitable.

Broad defaults, resource identities and legacy output remain compatible. Independent fuel-price repair runs under both policies. Selected source/private aliases retain original context classifications. N2 navigation visibility remains independent; no parking-placement improvements or game/profile changes belong to this increment.

Verify mixed-pump selection, subset aliases, native support, uncertainty, drift, source ownership, guarded effective exclusions, price/context preservation and legacy equivalence. Static success does not establish purchases, physical access, prices/billing or gameplay acceptance. Review separate goal requirements before marking TASK-0046 complete.

## Subsequent sample policy clarification — 2026-10-21

**Documented — user decision:** include whole stations G01/G02/G06 and omit added car support at G03/G04/G05. Individual-pump suitability distinctions are unnecessary for this sample; source truck-correlated flags do not by themselves justify withholding car support at the approved public stops. Keep granular selection internally, allowing all groups of an approved facility to be selected together. The historical G2 catalog/payload stays unchanged; revised reusable rules and broader coverage require subsequent implementation. [Evidence and readiness boundary](../../reference/SELECTIVE_CAR_FUELING_FEEDBACK_2026_10_21.md).
