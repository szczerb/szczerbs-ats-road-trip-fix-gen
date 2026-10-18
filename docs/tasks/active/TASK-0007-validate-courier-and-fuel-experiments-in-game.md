---
id: TASK-0007
title: Validate generated courier and refueling experiments in game
status: active
priority: high
repositories:
  - .
depends_on:
  - TASK-0006
owner: shared
---

# Goal

Determine whether the generated candidates produce usable courier work and passenger-car refueling in their actual map locations, preserving truck behavior and shared-profile progression.

# Context

Static analysis and package generation do not prove runtime behavior. Courier aliases require valid placed depots, routes, eligibility, and market state. Fuel PPDs have separate linked map services, so a descriptor change may require an editor rebuild. No such in-game/editor operation was performed during the overnight research.

# Scope

- **Accepted functional milestones, 2026-10-18:** the user confirms refueling and parking/rest work in Canada and Mexico. These internal functional checks are complete at the reported scope. Detailed UI/accounting and truck/reload controls were not individually enumerated. Courier and connector-icon validation remain separate; historical test instructions below do not reopen accepted milestones. [Dated evidence](../../reference/VALIDATION_RESULTS.md#2026-10-18-refueling-and-rest-confirmed-in-canada-and-mexico).

- Separate [reasonable tank r0](../../reference/REASONABLE_GAS_TANK_UPGRADES.md): **internally complete by user acceptance, 2026-10-18**. The user reports it works and may offer it for community testing. Detailed per-model/transition/reload checks remain optional community coverage; they are not open internal tank blockers. Other feature validation remains in this task.

- Current metadata handoff: [r8/r3](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md), with full Expansion labels and unchanged gameplay. Confirm the Western Canada ProMods Connections r8 picture after its shorter filename; [INC-0001](../../incidents/INC-0001-connector-icon-cache/README.md) remains open until that runtime result is reported. No automatic cache/settings changes.

- Current overnight handoff: seven r4 combined source-map/connector fixes plus the separate Practical Courier Jobs r0. Replace superseded fixes at the same source-relative priority. Follow the [manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md) for fuel quantities/payment, rest prompt/fatigue recovery, truck/garage/reload and owned-Mustang Dispatch pickup/completed delivery. The class edit preserves nine vehicle transfers statically; it is not a promise of 58 live offers. Check context-preserved WCE dealer aliases and shared Quick Jobs/logs separately. No more gameplay tests are expected tonight.

The older candidates below are historical controls; do not enable them together with their r4 replacements.

- The new [courier report](../../reference/COURIER_REPORTING.md) is static only. Later compare stock/mod company check-in positions and opened markets in both modes before an active job, then courier pickup and completed delivery. Collect working/affected city examples when this validation begins, not during the reporting milestone. Include the [14 WCE r3 alias-context controls](../../reference/COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk); runtime market regression is unknown.

- Historical rest candidate: WCE `1.61-r3-experimental` combines fuel/price fixes with 202 local car-rest additions. Replace only that source's r2 fix; keep the other maps' r2 fixes. Compare selected/rest-suppressed locations, engine-off prompt, fatigue recovery, truck behavior, icons and reload. The [processor guide](../../reference/COMPATIBILITY_PROCESSORS.md) records exact output/hash and accepted boundary over-additions. No gameplay test is expected tonight.

- Historical fuel/price handoff is [r2](../../reference/FUEL_FIX_BATCH_1_61_R2.md), retaining r1 station resources and adding sourced/estimated petrol prices. Follow the [manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md): finite positive price, finite initial and changing quantity, tank/payment, truck diesel, garage and reload controls. The user accepts implementation now and explicitly defers gameplay after putting the rig away; the one-time reminder is set for 2026-10-18 18:00 Europe/Warsaw. Do not mark runtime work done from static definition checks.
- [Rest research](../../reference/PASSENGER_CAR_REST_RESEARCH.md) found filtered polygon actions and actual truck-stop placements. No rest patch is included in r2. The separate WCE r3 candidate needs car prompt/fatigue recovery, map/discovery, retained truck and reload tests.

- Test [full-map fuel batch r1](../../reference/FUEL_FIX_BATCH_1_61_R1.md) with each fix directly above its source map and old r0 samples disabled. First check all four points at the nearer Helena station, then car/truck purchases on the other maps, garages (including ownership/prices) and reloads. Preserve the single-point user result; do not treat static coverage as gameplay proof.
- Include the [Western Canada–ProMods connector fuel fix](../../reference/CONNECTOR_FUEL_FIXES.md) directly above that connector in the screenshot-confirmed order. Test an affected connection-area station in both modes, including a garage and reload. Reforma OtherMaps has no station-interaction targets; its later r2/r4 package repairs country petrol fields.

- Use a disposable/copied profile with exact game/DLC/mod versions, priority, vehicle/class, rating, and baseline observations.
- Test [sample 2](../../reference/OVERLAPPING_FUEL_SAMPLE.md) at the same eastern Helena dispenser with sample 1 disabled: map visibility and actual refueling with both a truck and car, then reload/control checks.
- Retain the Helena-area sample-1 user results; broaden to the closer city station only after establishing preservation of both interactions.
- Confirm Great Falls HQ selection/access and compare the [single-pump sample](../../reference/STARTER_AREA_SAMPLE.md), including the converted pump and unchanged nearby truck controls.
- Test the narrow Ahorrara courier candidate separately from the wider alias experiment and the fuel descriptor experiment.
- Compare unmodified, candidate-only, and (only if necessary) separately editor-rebuilt fuel data.
- Record counterexamples, actual fuel changes and completed deliveries, logs, and truck regressions.
- Do not install into or reset the user's live profile as an incidental setup step.

# Implementation Plan

1. Follow [validation handoff](../../reference/VALIDATION_HANDOFF.md), confirm a safe test profile and expected source hashes, and collect actual working/affected examples.
2. Establish a reproducible control stack, isolating extra courier and fuel mods first.
3. Compare courier offers, pickup orientation/access, route completion, and delivery/rating results with matched market progression.
4. For the Helena sample, record the combined descriptor/service outcome, corrected baseline screenshot context, reported patched truck-map absence, and remaining physical truck/reload checks. Establish car and truck support at the same physical pump before broadening to the nearer multi-point city station; do not assume splitting dispensers is necessary. For the separate Reforma PPD-only candidate, compare actual fuel purchase and truck behavior; investigate editor rebuilding only if its own result requires it.
5. The user selected the exact-overlap experiment: TASK-0009 produces a standalone sample preserving truck records and adding a car twin. Test it before broadening to other locations; do not assume its generated structure establishes runtime success.
6. Update hypotheses with results and create the next implementation task only from demonstrated behavior.

# Acceptance Criteria

- Each tested candidate has explicit before/after evidence or a reproducible blocker with next evidence needed.
- Courier success requires an offer and completed usable delivery, not just a context entry.
- Refueling success requires a measurable fuel increase and preserved truck access, not just an added PPD record.
- Tests identify effective stack, source/output fingerprints, side effects, and whether map rebuilding is required.
- Live profile and original inputs remain preserved; negative results are recorded.

# Verification

2026-10-18: user-reported Canada/Mexico refueling and rest success closes those internal functional milestones. Do not infer individual price/quantity/payment values, exact tested sites or truck/reload results. GPT-6 Luna / low reviewed the evidence scope; root updated linked references and task status language. Documentation-only QA checks links, task metadata/status, immutable inputs, artifact exclusions and whitespace; no code/package changes require rerunning utility tests. Evidence: `local_outputs/work/2026-10-18_18-52-11/`. This broader task remains active for its other checks.

2026-10-18: [tank r0 user acceptance](../../reference/VALIDATION_RESULTS.md#2026-10-18-tank-upgrades-accepted-internally) closes that separate internal milestone. The report provides general success, without individual measurements. It does not close this broader courier/map validation task.

2026-10-18: the user reports functioning passenger-car refueling at many visited Canadian stations, but invalid gallon quantities in Canada and normal initial zero in the USA. The supplied screenshot also shows price `$0,00`. [Dated validation evidence](../../reference/VALIDATION_RESULTS.md#2026-10-18-canadian-r1-refueling-and-invalid-quantity-display) and [country-price research](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md) separate this expanded access result from the unresolved price/display cause. No numerical purchase/balance comparison or broad Canadian truck/reload result was supplied. TASK-0014 scopes the minimal sourced-price validation; this task remains active.

2026-10-17: partial runtime evidence received. The user created a disposable ATS Expansion test profile and reports that enabling the Helena-area sample made the eastern point available to cars and allowed successful refueling. Three inspected map screenshots support the icon change; a cockpit screenshot shows the nearer city forecourt, still reported truck-only. See [validation results](../../reference/VALIDATION_RESULTS.md) for exact attribution, screenshot filenames/provenance, candidate mapping, and limitations.

GPT-6 Luna / medium independently rechecked the existing read-only station inventory, descriptor and generator guards. Root inspected all four supplied PNGs through WSL, verified the v25 city descriptor's four GAS records and four linked services, and reviewed the distinction between model/recipe scope and inherent station risk. No source/archive, code, generated package, game, editor, or profile changes were made. The earlier city-token table's duplicate `.base` extension was corrected while updating the guide.

Documentation checks passed: 39 Markdown documents, 247 relative links, eight task metadata/status/dependency records, 20 corrected sector paths against the source ZIP, four original screenshot fingerprints, and `git diff --check`. These are the appropriate checks for this documentation-only update; gameplay was performed by the user, not the agent. Existing 43 code tests remain the prior static baseline and were not rerun for prose edits.

Follow-up, 2026-10-17: user recalls the original truck-map screenshot probably predates installing the sample, during the initial truck quick job. With the sample now active, the tested point is reported absent in Truck map mode and present only in Car mode. No actual truck-refueling failure is reported. The sample therefore lacks confirmed both-mode visibility, while physical truck fueling remains unknown. GPT-6 Luna / medium reviewed this distinction against the existing code/report; root updated the dated results and ignored evidence metadata. No code, package, game, or profile changes were made.

Follow-up, 2026-10-17: the user reports that overlapping sample 2 works with both a passenger car and a truck at the same pump. [Dated evidence](../../reference/VALIDATION_RESULTS.md#2026-10-17-sample-2-both-mode-refueling) records attribution and limits. This completes the first user-reported dual-vehicle refueling comparison; independent measurements, reload checks and broader locations remain open. The old sample remains unchanged; the new branded version has byte-identical gameplay payloads.

Still pending: exact runtime build/installed-sample fingerprints, numerical fuel/payment observations, reload/control regressions, multi-point city-station design/validation, Great Falls/Reforma tests, and courier offers/completed deliveries. A combined PPD/service success does not isolate each component's necessity. This task remains active; one successful user-reported fuel test does not satisfy all acceptance criteria.

A separate [sample-2 generation task](../done/TASK-0009-build-overlapping-fuel-pair.md) now implements the user-requested overlap experiment. Its static tests do not close this gameplay task.

# Links

- [Prototype](../done/TASK-0006-build-inspector-and-experimental-generators.md)
- [Validation handoff](../../reference/VALIDATION_HANDOFF.md)
- [Courier findings](../../reference/COURIER_RESEARCH_FINDINGS.md)
- [Refueling findings](../../reference/REFUELING_RESEARCH_FINDINGS.md)

- [User test results and selection review](../../reference/VALIDATION_RESULTS.md)
