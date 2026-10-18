# Pending manual game tests

Updated: 2026-10-19. The user confirms functional refueling in Canada and Mexico and accepts tank upgrades internally. The subsequent r9 report confirms parking icons in Alaska and Canada after checking two towns, with denser map coverage. [Current result](VALIDATION_RESULTS.md#2026-10-19-r9-parking-icons-confirmed-in-alaska-and-canada). Individual physical-rest/fatigue steps were not enumerated. The static r9 marker repair has passed final package audits; use its [handoff](MOD_REST_MARKERS_1_61_R9.md). The user was completing a job in Mexico; do not interrupt for rest testing. Numerical billing controls, courier delivery and the connector icon retain separate evidence/status. Remind only about remaining checks. Existing one-time reminder: **2026-10-18 18:00 Europe/Warsaw**; do not create duplicates.

**Interim user report, 2026-10-18:** Job Types Compat Mustang testing is ongoing in the USA with no problems noticed yet. This interim report predates the subsequent tank and Canada/Mexico fuel/rest confirmations recorded below.

## Reasonable tank upgrades: internally complete; community checks optional

**Documented — first-hand user report, 2026-10-18:** the user confirms that everything works following the tank r0 handoff and explicitly accepts this mod as internally done. They may invite community testers. This closes the internal tank validation; the individual checks below remain useful optional regression coverage, not outstanding internal requirements. The report does not enumerate measurements or each test separately. [Acceptance evidence](VALIDATION_RESULTS.md#2026-10-18-tank-upgrades-accepted-internally).

Use the separate [reasonable gas tank upgrades candidate](REASONABLE_GAS_TANK_UPGRADES.md); disable Ford Fuel X3 and conflicting chassis/tank overrides first. Keep the map package set at its final audited r9 state, and keep courier r3 unchanged.

- Existing Mustang: capacity 76 L, filling can exceed stock 61 L and stops at the new limit. Check the nominal 20-US-gallon capacity description.
- F-150: capacity 136 L instead of 98 L; nominal description 36 US gal.
- Crown Victoria/Bronco remain at stock 72/79 L; this mod packages neither chassis.
- Check fuel retained on transition from 3x (including any over-capacity value), finite gauge/range, normal payment, consumption and save/reload. Do not assume the engine automatically clamps or preserves saved fuel.
- No separate upgrade purchase is needed by this implementation; report if an owned vehicle does not refresh capacity. Do not edit the profile to force it.

## Refueling: Canada/Mexico confirmed; detailed controls unreported

**Documented — user report, 2026-10-18:** refueling works in Canada and Mexico. General functional refueling is internally accepted. The following numerical/accounting and regression checks are not individually described by that report; they remain useful additional coverage rather than reopening functional access. [Dated evidence](VALIDATION_RESULTS.md#2026-10-18-refueling-and-rest-confirmed-in-canada-and-mexico).

Use the final audited r9 map packages with the unchanged [courier r3](MOD_METADATA_MAP_NAMES_1_61_R8_R3.md) package, disable superseded map/r1/r0/sample versions, and keep each fix immediately above its own source. The OtherMaps price package also belongs above OtherMaps. Record the actual game/mod versions and station location. Use the same car/pump for comparisons where practical. Tank r0 and courier r3 are separate, unchanged acceptance tracks.

- In ProMods BC and Western Canada areas, the petrol price is positive and the initial quantity is finite zero, not `-nan(ind)`.
- While filling, the quantity increases with a finite value; fuel in the tank increases and the balance decreases consistently with the displayed price/amount. Do not judge success only by the initial zero.
- Check both ProMods' BC unit and Western Canada's separate province definitions where possible; a single BC success does not validate all provinces or the fallback policy.
- Repeat a US control, a truck diesel purchase, a garage case if used, and a save/reload. Existing diesel prices and truck access should be preserved.
- Alaska/Mexico definitions also receive missing fields where source-owned. Mexico now has general user-reported refueling success; individual price/billing results for Mexico and Alaska were not supplied; inferred omissions are not prior user-reported failures there.

Price provenance: same-unit lower-source values are restored where available. Other new values use the recorded stock ATS petrol/diesel ratio and are estimates, not real-world price assertions. A positive definition alone does not establish that it completely repairs the reported UI problem.

## Passenger-car parking markers: r9 user-confirmed in two towns

**Documented — user report, 2026-10-19:** the initial Alaska/Canada parking-icon check is confirmed after tests in two towns, and the map shows denser icons. This supersedes the initial missing-icon status at that scope. Exact towns and individual prompt/fatigue/truck/reload steps were not supplied. See the [dated evidence](VALIDATION_RESULTS.md#2026-10-19-r9-parking-icons-confirmed-in-alaska-and-canada).

Static inspection identified the marker issue: the original mixed action is classified truck-first for the map marker, while native `parking_car` locations have car-only actions. The r9 repair adds reviewed car twins while retaining the original truck triggers. The static suite reported 281 passing tests; final package audits pass, and the later user report confirms icons at the two-town scope. See the [r9 marker handoff](MOD_REST_MARKERS_1_61_R9.md), [rest processor](COMPATIBILITY_PROCESSORS.md), and [original mechanism research](PASSENGER_CAR_REST_RESEARCH.md).

Additional coverage can use a copied profile and the as-delivered filenames when convenient. The initial Alaska/Canada icon check is complete; broader locations and mod-covered Montana remain separate coverage. At one selected affected location, verify the actual parking/rest prompt and fatigue recovery; separately confirm the original truck parking control still works, then reload and check the icon and access again. Record the map, sector/location, vehicle, mode, exact package filenames and observed result. Icon discovery, an interaction prompt, and successful fatigue recovery are three separate observations. Do not interrupt the user's current job, modify the live profile, or infer physical rest from static tests.

Keep [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) active for the remaining courier, r9 rest, detailed fuel-accounting and connector-icon evidence. Canada/Mexico refueling access remains user-confirmed and is not being reopened by the parking issue. Record station, vehicle/mode, package version and observed price/quantity/tank/payment/rest results in [validation results](VALIDATION_RESULTS.md); never rewrite historical generated reports to claim later validation.

## Courier company check-in and alias controls: pending

The [read-only courier report](COURIER_REPORTING.md) generates no package and does not prove playable offers. Later compare an officially classified stock depot and a classified map-mod depot in truck/car modes: record the visible selection avatar, its activation position and the market it opens before any active job. Test a courier offer, reachable pickup and completed delivery separately; record game/mod versions, source order, rating/vehicle and job state. Collect the user's working/affected city examples when that investigation begins.

The existing WCE r3 candidate has a [static context-preservation risk at 14 company-linked prefab aliases](COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk). Before considering it validated for courier use, compare the same dealer/company locations with and without the candidate, and repeat after any future preservation repair. This is a risk requiring controls, not an observed gameplay failure. The detailed fuel-accounting controls remain unreported; the earlier positive rest report is qualified by the later missing-icon report, and physical rest remains unconfirmed.

## Courier quantity and discovery: later controlled observation

Follow the [availability research controls](COURIER_JOB_AVAILABILITY_RESEARCH.md#low-risk-controlled-observations-for-a-later-game-session): record departures from fixed old cities and the total visible market separately, with car/rating/market/filters unchanged. Compare equal elapsed-time copied-profile runs with and without a new city discovery; natural market variation remains a confounder requiring repetition. If still using the Mustang, separately compare a broader-class car under matched conditions. Counts of stock job definitions are not live offers, and an observed rise in empty visible cities alone does not prove global dilution.

## Standalone Practical Courier Jobs: pending

Enable only the new standalone r0 candidate from the [generator guide](PRACTICAL_COURIER_GENERATOR.md), above any reviewed job-definition replacement. Record car, rating, current city, selected market, active filters, time elapsed, game version and exact enabled packages. Use an owned Mustang in Dispatch Market and a matched control without the mod. Existing offers may not change immediately; record natural market refresh rather than resetting the economy.

Check newly eligible practical cargo categories at sufficient rating, acceptance, reachable pickup, attached/carried cargo, driving and completed delivery/payment. Check at least one unchanged originally eligible job. Inspect Quick Jobs and logs separately because the same definitions are shared. Verify vehicle-transfer definitions remain unaffected in behavior where practical; their bytes are unchanged statically. Additional eligibility does not guarantee offers in every city, prove a discovery-budget mechanism or establish exact physical cargo fit.

R4 adds original classifications to private prefab aliases; compare the historical WCE dealer controls with and without r4. Static classification preservation does not close runtime courier testing.

## Connector Mod Manager icon: pending r9 filename confirmation

- Use the final r9 Western Canada ProMods Connections package filename, disable older copies, and keep it directly above that source.
- Open Mod Manager and check its dedicated M2D image appears. The r7 log reported icon-cache creation failure despite a valid packaged JPEG; the r8 shortened filename was a mitigation, not confirmed rendering.
- If missing, preserve the new game log and exact r9 package filename/version. Do not delete cache or change Windows settings as an incidental step. [Incident evidence](../incidents/INC-0001-connector-icon-cache/README.md).
