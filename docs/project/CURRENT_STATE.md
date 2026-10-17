# Current State

Updated: 2026-10-17. Initialization is complete; the overnight research and prototype milestone is complete and statically verified under [TASK-0006](../tasks/done/TASK-0006-build-inspector-and-experimental-generators.md).

## Available result

- A Python 3.11+ CLI inspects ZIP/HashFS, selectively extracts resources, resolves explicit package mounts/order and includes, audits courier context coverage, and generates bounded context, PPD, and pinned single-pump sector experiments. See [usage](../reference/TOOLING.md).
- Both investigations are documented: [courier findings](../reference/COURIER_RESEARCH_FINDINGS.md) and [refueling findings](../reference/REFUELING_RESEARCH_FINDINGS.md). Research preparation and first-increment design are complete; no live game/editor/profile operation occurred.
- Installed reference: ATS 1.61.3.18, Steam build 25952361, Road Trip Ford package, and five supplied map/resource archives. The existing log contains a historical 23-mod listing; analysis order is explicitly selected, not assumed to recreate the live profile. See [baseline](../reference/RESEARCH_BASELINE.md).

## Evidence and hypotheses

**Observed locally:** the public CLI reproduces independent coverage for 1,030 ZIP company definitions: 964 classified, 25 explicitly excluded by SCS, and 41 unclassified. Stock `d_cust_*` prefabs already have courier tags. Broad company-prefix or enable-everything fixes are unsupported.

**Hypothesis with exact alias evidence:** Reforma `ahorrara` shares the official supermarket model/descriptor pair and can receive an additive `retail` context. The narrow PoC emits a 108-byte gameplay definition for eight company/city occurrences. A broader conservative pass finds 15 aliases / 33 effective definitions. Neither count establishes usable placed locations or offers.

**Hypothesis with paired binary evidence:** GAS type 3 / flags 1 enables car/petrol interaction. The Reforma MX9 experiment changes a v25 PPD from 1,700 to 1,736 bytes while preserving its truck locator. A verified placed instance has a separately serialized map service; runtime rebuilding and physical interaction remain unknown.

## Starter-area follow-up

**Observed locally:** A partial city-token-filtered pass found paired garage items for 20 city tokens across 270 ATS Expansion sectors; stock city tokens require a separate effective-data comparison. Great Falls has a single-GAS fuel interaction approximately 94 map metres from its GaragePoint. A pinned generator now produces isolated prefab/PPD and sector changes using the inferred petrol service bit. A second Helena-area sample is the stronger starting-profile candidate: its effective garage retains stock class `81`, unlike the custom Great Falls garage. Stock-only Missoula proximity was rejected after checking the winning mod data. See [sample and test guide](../reference/STARTER_AREA_SAMPLE.md). **Unknown:** fresh-profile HQ eligibility, physical access, runtime refueling, and garage substitution. All eight inspected Great Falls company editor definitions already carry courier contexts; no redundant courier-tag patch is generated.

## First user gameplay result

**Documented — user report, 2026-10-17:** a fresh test profile with ATS Expansion as its only baseline mod was compared with the Helena-area sample. The eastern station gained a car-map icon and the user successfully refueled there. The user reports a substantial road detour and the closer city station remaining truck-only. Four screenshots were inspected; actual refueling was reported by the user rather than reproduced by the agent. See [dated results and evidence limits](../reference/VALIDATION_RESULTS.md).

**Documented — user follow-up correction:** the original truck-map screenshot probably predates sample installation. With the sample now enabled, the eastern target is reported absent from the truck map and present only in car mode. This demonstrates a map-visibility regression against both-mode support; actual post-patch truck refueling remains untested. Next fuel experiment must preserve truck service while enabling cars at the same physical pump; a required physical dispenser split has not been established.

**Observed locally:** the nearer city station was already recognized as a truck control, approximately 344 map units from the garage. It has a v25 descriptor with four GAS locators/four services; the first generator deliberately supports only the single-locator/single-service `02003` shape. Its exclusion was a prototype limitation, not a diagnosed unsafe format. Next fuel target: that nearer station, with deliberate locator/service matching and truck preservation. Route convenience must be evaluated beyond straight-line distance.

## Same-position sample 2

**Observed locally:** the user-requested [sample 2](../reference/OVERLAPPING_FUEL_SAMPLE.md) is generated for the same eastern Helena point. It preserves the original truck GAS record/service/node and adds a car locator/service/node with byte-identical positions/rotations. Sector item/node counts and the parent service-reference list are updated; the original `.data`/`.aux`/`.desc`/`.layer` remain fingerprinted and unchanged. The separate `generate-overlap-fuel` command uses a schema-2 pinned recipe and a distinct private alias/display name.

**Unknown:** simultaneous/co-located runtime behavior, both-mode visibility, actual refueling and reload behavior. Disable sample 1 for this comparison. Multi-pump/city-station support is not broadened in this increment.

## Verification boundary and next work

All 48 tests pass, including five overlap-preservation/CLI/guard cases and the four original conversion cases. The original archive/CLI baseline is recorded in TASK-0006; [TASK-0009](../tasks/done/TASK-0009-build-overlapping-fuel-pair.md) records the overlap implementation, independent real-package review, hashes, retained source records, and byte-identical regeneration. [TASK-0008](../tasks/done/TASK-0008-prepare-starter-area-sample.md) completed the nearby ATS Expansion samples and their static verification. [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) is active with the first user-reported positive fuel result. Other samples, truck/reload regressions, multi-point support and courier behavior remain unverified. Outputs remain experimental; generated reports retain their generation-time validation flags. [Validation handoff](../reference/VALIDATION_HANDOFF.md) identifies the artifacts and controlled comparisons.

Next: [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md), using a copied/disposable profile to observe actual offers/completed deliveries and measurable refueling, isolate other courier/fuel/map mods, and determine whether services need editor rebuilding. No confirmed fix for every map or city is claimed.
