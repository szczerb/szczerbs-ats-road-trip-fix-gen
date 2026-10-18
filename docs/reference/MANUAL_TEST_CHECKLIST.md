# Pending manual game tests

Updated: 2026-10-18. The user has resumed manual testing. Earlier overnight deferral remains history; prices/billing, rest and job delivery stay unverified until results are reported. Remind the user at package handoffs while these checks remain open. Existing one-time reminder: **2026-10-18 18:00 Europe/Warsaw**; do not create duplicates.

**Interim user report, 2026-10-18:** Job Types Compat Mustang testing is ongoing in the USA with no problems noticed yet. The checklist is incomplete; the active 3x-capacity mod will be disabled for the new tank test.

## Reasonable tank upgrades: pending

Use the separate [reasonable gas tank upgrades candidate](REASONABLE_GAS_TANK_UPGRADES.md); disable Ford Fuel X3 and conflicting chassis/tank overrides first. Keep map r8/courier r3 unchanged.

- Existing Mustang: capacity 76 L, filling can exceed stock 61 L and stops at the new limit. Check the nominal 20-US-gallon capacity description.
- F-150: capacity 136 L instead of 98 L; nominal description 36 US gal.
- Crown Victoria/Bronco remain at stock 72/79 L; this mod packages neither chassis.
- Check fuel retained on transition from 3x (including any over-capacity value), finite gauge/range, normal payment, consumption and save/reload. Do not assume the engine automatically clamps or preserves saved fuel.
- No separate upgrade purchase is needed by this implementation; report if an owned vehicle does not refresh capacity. Do not edit the profile to force it.

## Petrol price and quantities: pending

Use the newest [r8 map/r3 courier packages](MOD_METADATA_MAP_NAMES_1_61_R8_R3.md), disable superseded r1/r0/sample versions, and keep each fix immediately above its own source. The OtherMaps price package also belongs above OtherMaps. Record the actual game/mod versions and station location. Use the same car/pump for comparisons where practical.

- In ProMods BC and Western Canada areas, the petrol price is positive and the initial quantity is finite zero, not `-nan(ind)`.
- While filling, the quantity increases with a finite value; fuel in the tank increases and the balance decreases consistently with the displayed price/amount. Do not judge success only by the initial zero.
- Check both ProMods' BC unit and Western Canada's separate province definitions where possible; a single BC success does not validate all provinces or the fallback policy.
- Repeat a US control, a truck diesel purchase, a garage case if used, and a save/reload. Existing diesel prices and truck access should be preserved.
- Alaska/Mexico definitions also receive missing fields where source-owned. Their price/billing behavior remains untested; inferred omissions are not prior user-reported failures there.

Price provenance: same-unit lower-source values are restored where available. Other new values use the recorded stock ATS petrol/diesel ratio and are estimates, not real-world price assertions. A positive definition alone does not establish that it completely repairs the reported UI problem.

## Rest areas: local processor implemented; runtime test pending

The rest investigation found vehicle-filtered actions and concrete truck-stop placements. The [rest processor](COMPATIBILITY_PROCESSORS.md) applies the local distance rule and retains shared truck actions. Combined fuel/rest behavior was first delivered in r4; current r8 retains those gameplay bytes and replaces earlier source-specific fixes at the same priority. Do not keep both versions enabled. The historical r2 fuel packages contain no rest changes. [Original mechanism](PASSENGER_CAR_REST_RESEARCH.md).

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

## Connector Mod Manager icon: pending r8 confirmation

- Replace the old connector fix with `szczerbs-road-trip-map-fix-western-canada-promods-connections-1.61-r8-experimental.scs`, disabling its older copy. Keep it directly above Western Canada ProMods Connections.
- Open Mod Manager and check its dedicated M2D image appears. The r7 log reported icon-cache creation failure despite a valid packaged JPEG; the shortened filename is a mitigation for a strong path-length hypothesis, not confirmed rendering.
- If missing, preserve the new game log and actual package filename/version. Do not delete cache or change Windows settings as an incidental step. [Incident evidence](../incidents/INC-0001-connector-icon-cache/README.md).
