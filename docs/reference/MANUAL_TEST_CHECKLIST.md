# Pending manual game tests

Updated: 2026-10-18. **Documented — user instruction:** the game is closed and the sim rig is put away; no more gameplay tests tonight. Implement the evident missing petrol-price correction now, but keep the symptom repair unverified until the user tests it. Remind the user at subsequent package handoffs/progress updates while these checks remain pending. A one-time thread reminder is scheduled for **2026-10-18 18:00 Europe/Warsaw**; do not create duplicates.

## Petrol price and quantities: pending

Use the newest r2 packages, disable superseded r1/r0/sample versions, and keep each fix immediately above its own source. The new OtherMaps price package also belongs above OtherMaps. Record the actual game/mod versions and station location. Use the same car/pump for comparisons where practical.

- In ProMods BC and Western Canada areas, the petrol price is positive and the initial quantity is finite zero, not `-nan(ind)`.
- While filling, the quantity increases with a finite value; fuel in the tank increases and the balance decreases consistently with the displayed price/amount. Do not judge success only by the initial zero.
- Check both ProMods' BC unit and Western Canada's separate province definitions where possible; a single BC success does not validate all provinces or the fallback policy.
- Repeat a US control, a truck diesel purchase, a garage case if used, and a save/reload. Existing diesel prices and truck access should be preserved.
- Alaska/Mexico definitions also receive missing fields where source-owned. Their price/billing behavior remains untested; inferred omissions are not prior user-reported failures there.

Price provenance: same-unit lower-source values are restored where available. Other new values use the recorded stock ATS petrol/diesel ratio and are estimates, not real-world price assertions. A positive definition alone does not establish that it completely repairs the reported UI problem.

## Rest areas: local processor implemented; runtime test pending

The rest investigation found vehicle-filtered actions and concrete truck-stop placements. The separate [rest processor and verified WCE r3 candidate](COMPATIBILITY_PROCESSORS.md) applies the user-selected local distance rule and retains the shared truck action. WCE r3 combines fuel and rest; replace its older WCE r2 fix at the same priority, keeping other maps' r2 fixes. The previously delivered r2 fuel packages contain no rest changes. [Original mechanism and source evidence](PASSENGER_CAR_REST_RESEARCH.md).

When a complete-coverage rest candidate is prepared, compare car-mode map/discovery icons, the engine-off/rest prompt inside the actual polygon, successful fatigue recovery, truck/bus behavior where applicable and save/reload. Include a selected truck area with no car rest within 1,000 map-world units, an unchanged truck area with a nearby car rest, and a working stock car area. The absence of a fuel-style upright hologram is expected and is not the failure criterion. Do not copy the petrol service bit into parking records. Bounded static fixture outputs are not complete-map install candidates.

Keep [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) active until its runtime evidence is supplied. Record station, vehicle/mode, package version and observed price/quantity/tank/payment/rest results in [validation results](VALIDATION_RESULTS.md); never rewrite historical generated reports to claim later validation.
