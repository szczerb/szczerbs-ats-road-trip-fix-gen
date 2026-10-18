# Pending manual game tests

Updated: 2026-10-18. **Documented — user instruction:** the game is closed and the sim rig is put away; no more gameplay tests tonight. Implement the evident missing petrol-price correction now, but keep the symptom repair unverified until the user tests it. Remind the user at subsequent package handoffs/progress updates while these checks remain pending. A one-time thread reminder is scheduled for **2026-10-18 18:00 Europe/Warsaw**; do not create duplicates.

## Petrol price and quantities: pending

Use the newest delivered r4 combined packages, disable superseded r1/r0/sample versions, and keep each fix immediately above its own source. The OtherMaps price package also belongs above OtherMaps. Record the actual game/mod versions and station location. Use the same car/pump for comparisons where practical.

- In ProMods BC and Western Canada areas, the petrol price is positive and the initial quantity is finite zero, not `-nan(ind)`.
- While filling, the quantity increases with a finite value; fuel in the tank increases and the balance decreases consistently with the displayed price/amount. Do not judge success only by the initial zero.
- Check both ProMods' BC unit and Western Canada's separate province definitions where possible; a single BC success does not validate all provinces or the fallback policy.
- Repeat a US control, a truck diesel purchase, a garage case if used, and a save/reload. Existing diesel prices and truck access should be preserved.
- Alaska/Mexico definitions also receive missing fields where source-owned. Their price/billing behavior remains untested; inferred omissions are not prior user-reported failures there.

Price provenance: same-unit lower-source values are restored where available. Other new values use the recorded stock ATS petrol/diesel ratio and are estimates, not real-world price assertions. A positive definition alone does not establish that it completely repairs the reported UI problem.

## Rest areas: local processor implemented; runtime test pending

The rest investigation found vehicle-filtered actions and concrete truck-stop placements. The [rest processor](COMPATIBILITY_PROCESSORS.md) applies the local distance rule and retains shared truck actions. The r4 combined packages replace earlier fuel-only r2 and WCE r3 packages at the same source-relative priority. Do not keep both versions enabled. The historical r2 fuel packages contain no rest changes. [Original mechanism](PASSENGER_CAR_REST_RESEARCH.md).

When a complete-coverage rest candidate is prepared, compare car-mode map/discovery icons, the engine-off/rest prompt inside the actual polygon, successful fatigue recovery, truck/bus behavior where applicable and save/reload. Include a selected truck area with no car rest within 1,000 map-world units, an unchanged truck area with a nearby car rest, and a working stock car area. The absence of a fuel-style upright hologram is expected and is not the failure criterion. Do not copy the petrol service bit into parking records. Bounded static fixture outputs are not complete-map install candidates.

Keep [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) active until its runtime evidence is supplied. Record station, vehicle/mode, package version and observed price/quantity/tank/payment/rest results in [validation results](VALIDATION_RESULTS.md); never rewrite historical generated reports to claim later validation.

## Courier company check-in and alias controls: pending

The [read-only courier report](COURIER_REPORTING.md) generates no package and does not prove playable offers. Later compare an officially classified stock depot and a classified map-mod depot in truck/car modes: record the visible selection avatar, its activation position and the market it opens before any active job. Test a courier offer, reachable pickup and completed delivery separately; record game/mod versions, source order, rating/vehicle and job state. Collect the user's working/affected city examples when that investigation begins.

The existing WCE r3 candidate has a [static context-preservation risk at 14 company-linked prefab aliases](COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk). Before considering it validated for courier use, compare the same dealer/company locations with and without the candidate, and repeat after any future preservation repair. This is a risk requiring controls, not an observed gameplay failure. Fuel quantity/billing and rest checks above remain pending independently.

## Courier quantity and discovery: later controlled observation

Follow the [availability research controls](COURIER_JOB_AVAILABILITY_RESEARCH.md#low-risk-controlled-observations-for-a-later-game-session): record departures from fixed old cities and the total visible market separately, with car/rating/market/filters unchanged. Compare equal elapsed-time copied-profile runs with and without a new city discovery; natural market variation remains a confounder requiring repetition. If still using the Mustang, separately compare a broader-class car under matched conditions. Counts of stock job definitions are not live offers, and an observed rise in empty visible cities alone does not prove global dilution.

## Standalone Practical Courier Jobs: pending

Enable only the new standalone r0 candidate from the [generator guide](PRACTICAL_COURIER_GENERATOR.md), above any reviewed job-definition replacement. Record car, rating, current city, selected market, active filters, time elapsed, game version and exact enabled packages. Use an owned Mustang in Dispatch Market and a matched control without the mod. Existing offers may not change immediately; record natural market refresh rather than resetting the economy.

Check newly eligible practical cargo categories at sufficient rating, acceptance, reachable pickup, attached/carried cargo, driving and completed delivery/payment. Check at least one unchanged originally eligible job. Inspect Quick Jobs and logs separately because the same definitions are shared. Verify vehicle-transfer definitions remain unaffected in behavior where practical; their bytes are unchanged statically. Additional eligibility does not guarantee offers in every city, prove a discovery-budget mechanism or establish exact physical cargo fit.

R4 adds original classifications to private prefab aliases; compare the historical WCE dealer controls with and without r4. Static classification preservation does not close runtime courier testing.
