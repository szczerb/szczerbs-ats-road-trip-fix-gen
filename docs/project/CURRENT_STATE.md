# Current State

Updated: 2026-10-17. Initialization is complete; the overnight research and prototype milestone is complete and statically verified under [TASK-0006](../tasks/done/TASK-0006-build-inspector-and-experimental-generators.md).

## Available result

- A Python 3.11+ CLI inspects ZIP/HashFS, selectively extracts resources, resolves explicit package mounts/order and includes, audits courier context coverage, and generates two bounded experimental patch types. See [usage](../reference/TOOLING.md).
- Both investigations are documented: [courier findings](../reference/COURIER_RESEARCH_FINDINGS.md) and [refueling findings](../reference/REFUELING_RESEARCH_FINDINGS.md). Research preparation and first-increment design are complete; no live game/editor/profile operation occurred.
- Installed reference: ATS 1.61.3.18, Steam build 25952361, Road Trip Ford package, and five supplied map/resource archives. The existing log contains a historical 23-mod listing; analysis order is explicitly selected, not assumed to recreate the live profile. See [baseline](../reference/RESEARCH_BASELINE.md).

## Evidence and hypotheses

**Observed locally:** the public CLI reproduces independent coverage for 1,030 ZIP company definitions: 964 classified, 25 explicitly excluded by SCS, and 41 unclassified. Stock `d_cust_*` prefabs already have courier tags. Broad company-prefix or enable-everything fixes are unsupported.

**Hypothesis with exact alias evidence:** Reforma `ahorrara` shares the official supermarket model/descriptor pair and can receive an additive `retail` context. The narrow PoC emits a 108-byte gameplay definition for eight company/city occurrences. A broader conservative pass finds 15 aliases / 33 effective definitions. Neither count establishes usable placed locations or offers.

**Hypothesis with paired binary evidence:** GAS type 3 / flags 1 enables car/petrol interaction. The Reforma MX9 experiment changes a v25 PPD from 1,700 to 1,736 bytes while preserving its truck locator. A verified placed instance has a separately serialized map service; runtime rebuilding and physical interaction remain unknown.

## Verification boundary and next work

All 39 tests pass. Real archive/CLI runs, descriptor hashes, generated package contents, byte-identical regeneration, and source-preservation checks are recorded in TASK-0006. No task is active; gameplay validation is the next backlog item. All outputs remain experimental. [Validation handoff](../reference/VALIDATION_HANDOFF.md) identifies the artifacts and controlled comparisons.

Next: [TASK-0007](../tasks/backlog/TASK-0007-validate-courier-and-fuel-experiments-in-game.md), using a copied/disposable profile to observe actual offers/completed deliveries and measurable refueling, isolate other courier/fuel/map mods, and determine whether services need editor rebuilding. No confirmed fix for every map or city is claimed.
