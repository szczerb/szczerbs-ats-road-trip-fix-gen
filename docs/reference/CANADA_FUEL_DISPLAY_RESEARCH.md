# Canadian car-refueling quantity display

Inspected: 2026-10-18. Applies to installed ATS **1.61.3.18**, the eleven supplied archives, and the source priority in [connector findings](CONNECTOR_FUEL_FIXES.md). This investigates the purchase panel separately from station access and actual tank replenishment. [TASK-0013](../tasks/done/TASK-0013-investigate-canadian-fuel-nan-display.md) records the investigation and delegation. [TASK-0014](../tasks/done/TASK-0014-audit-and-test-petrol-price-overrides.md) scopes a proposed audit and minimal diagnostic; no patch was generated here.

Subsequent user authorization, 2026-10-18: implement the evident missing field now and keep gameplay confirmation pending. The [r2 batch](FUEL_FIX_BATCH_1_61_R2.md) and [ADR-0007](../architecture/decisions/ADR-0007-repair-missing-petrol-prices.md) record source-priority restoration and an explicit game-ratio fallback for other missing values. This page preserves the original research and proposed one-field comparison, not the later implementation status. **Subsequent user report:** refueling and rest work in Canada and Mexico; [dated evidence](VALIDATION_RESULTS.md#2026-10-18-refueling-and-rest-confirmed-in-canada-and-mexico) closes functional access/rest checks. Exact price, quantity and billing retest values remain unreported. The original causal hypothesis below is preserved rather than presented as an isolated measured proof.

## Finding and confidence

**Observed locally:** an updated petrol price exists in ProMods Canada Definitions 1.6.4, but the higher-priority Western Canada ProMods Connections 1.7.3 replaces its British Columbia country file with an older definition containing only the diesel price. Western Canada's own province definitions also omit `petrol_price`. This is a concrete data incompatibility and the strongest explanation for the Canadian panel's zero price and invalid quantity.

**Hypothesis, strong:** a missing effective petrol price supplies an unusable zero to the car-refueling price/display calculation. A calculation such as purchase cost divided by unit price would then encounter `0 / 0` before filling starts, producing an indefinite NaN. Neither the engine's default for omitted `petrol_price` nor its exact quantity formula has been independently established. The findings identify a small definition-only validation candidate; they do not establish a tested repair.

**Documented — user report, 2026-10-18:** actual car refueling works at many visited ProMods Canada and Western Canada stations with the r1 fixes, while the gallon quantity is invalid; returning to the USA restores the initial quantity to zero. This expands the reported runtime evidence for station interaction. It does not measure charged money or prove that an invalid displayed amount matches or differs from the amount added to the tank.

## Screenshot and log evidence

**Observed locally:** the supplied `ats_20261018_001621_00.png`, read at original resolution, shows the Polish panel labels `Cena paliwa: $0,00`, `Galony: -nan(ind)`, and `Suma: $0`, while the panel prompts refueling. A static screenshot does not establish whether the button was previously pressed. No verified tank percentage is extracted from the screenshot. Microsoft documents `nan(ind)` as an indefinite floating-point NaN, optionally prefixed by a sign. That explains the displayed notation, not the particular calculation in ATS. [Microsoft floating-point formatting](https://learn.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions?view=msvc-170)

**Observed locally:** the available `game.log.txt` starts at **00:20:38**, after the screenshot timestamp **00:16:21**. It is later-session context. It identifies pack set `1.61.3.18`, lists 29 active mods, and confirms the connector above ProMods Definitions. All six installed r1 fuel archives match the delivered output archives byte-for-byte. The log contains no `petrol_price`, `fuel_price`, or `nan(ind)` diagnostics. Absence of a diagnostic does not establish a valid price or identify the screenshot's exact station/country.

The later active list includes Ford Fuel X3, Road Trip Zero Fuel Consumption, Generous Emergency Refuel and additional Workshop/background/branding/traffic packages. Their names alone do not explain the Canadian boundary. Their effective country/UI/economy overrides have not all been inspected, so the source winners below apply to the **supplied map stack**, not a proven reconstruction of every active resource.

Root evidence: `local_outputs/work/2026-10-18_01-04-41/canada-ui-root/`, including `evidence.json`, `game.log.snapshot.txt`, `installed-fix-fingerprints.json`, and `generated-country-scope.json`. The screenshot SHA-256 is `c6a7baae037760f658b24f9b42af638c73b80a1f8b152af7ae6dd26d07c3aec7`.

## Exact British Columbia override

**Observed locally:** both archives below supply the same mounted path, `def/country/bc.sui`, defining the same unit, `country.data.bc` (country ID 202). The connector's higher-priority file is selected as a whole; a field omitted there is not recovered from the lower file at the same resource path.

| Source | `fuel_price` | `petrol_price` | `imperial_units` | Country position |
| --- | ---: | ---: | --- | --- |
| `promods-ats-def-v164.scs` — Definitions 1.6.4 | `1.833761` | `1.502116` | `false` | `(-95000, 0, -92000)` |
| **Winner:** `Western_Canada_Promods_Connections_v1.7.3.scs` — 1.7.3 | `1.630` | **absent** | `false` | `(-93910, 0, -116700)` |

The ProMods source comments identify diesel CAD `2.549` and regular petrol CAD `2.088`, converted to the USD definition values above, dated **2026-08-31**. The connector's comment identifies diesel CAD `2.089` → USD `1.630`, dated **2022-05-20**. These are the authors' in-file price provenance, not independently verified current retail prices.

**Observed locally:** this is more specific than saying ProMods Canada has not added the new field: its supplied 1.6.4 definition already has it. The connector removes it from the effective same-path resource. Restoring the entire ProMods country file would also change the connector's diesel price and country position; that is unnecessarily broad for testing the single missing attribute.

## Western Canada and OtherMaps scope

**Observed locally:** all six country files below are won by `Western_Canada_Expansion_v1.7.3.scs` in the supplied stack. Each sets `imperial_units: false` and omits `petrol_price`. `kbritcolum` is a separate country unit/path from ProMods `bc`; the physical location and map country association determine which applies at a particular pump.

| Mounted country path | Province/territory | `fuel_price` | `petrol_price` |
| --- | --- | ---: | --- |
| `def/country/kalberta.sui` | Alberta | `0.8832147` | absent |
| `def/country/kbritcolum.sui` | British Columbia | `1.0732147` | absent |
| `def/country/kmanitoba.sui` | Manitoba | `0.9092147` | absent |
| `def/country/ksaskatche.sui` | Saskatchewan | `0.9732147` | absent |
| `def/country/knorthwest.sui` | Northwest Territories | `1.1432147` | absent |
| `def/country/kyukon.sui` | Yukon | `1.3692147` | absent |

**Observed locally:** the delegated inventory inspected 316 country definition files across six supplied archives; the other five have none. Reforma OtherMaps 40.161 replaces 19 Mexican country root definitions; none is a Canadian province/territory or the ProMods BC path. It therefore does not supply or remove a Canadian petrol price at these paths. This corrects any inference that its country-price contents make it the Canadian culprit.

The inventory's exact package/path winners, selected raw files and field lines are in `local_outputs/work/2026-10-18_01-04-53/canada-country-inventory/inventory.json`. It inventories country definitions; it does not establish that every active Workshop UI/economy override has been examined.

## Official reference and separate fuel types

**Observed locally:** a fresh selective read from the installed `def.scs` was byte-compared with the historical reference cache. Washington, Montana, California, `economy_data.sii`, `car_economy_data.sii`, and the root `country.sii` match exactly. This checks the actual source for the examples below without relying on cache freshness alone.

| Installed resource | `fuel_price` | `petrol_price` | `imperial_units` |
| --- | ---: | ---: | --- |
| `def/country/washington.sui` | `1.92132` | `1.47197` | `true` |
| `def/country/montana.sui` | `1.59851` | `1.18798` | `true` |
| `def/country/california.sui` | `2.16938` | `1.58979` | `true` |

Their comments express USD per litre and give equivalent US-gallon prices. Thus these are two independently populated price attributes; the presence of the legacy `fuel_price` does not establish that a petrol price is available. Installed Ford engines specify `type: petrol`, as recorded in [refueling findings](REFUELING_RESEARCH_FINDINGS.md#confounders-and-next-experiment).

**Documented:** SCS's `accessory_engine_data` documentation says engine `type` accepts `petrol`, added in 1.61. It does not publish country-price fallback or pump UI arithmetic. [SCS engine unit documentation](https://modding.scssoft.com/wiki/Documentation/Engine/Units/accessory_engine_data)

**Documented — independent first-person report:** MirM's **2026-10-17 15:42** post on the SCS forum identifies missing new `petrol_price` definitions in an economy mod's 86 country files while investigating missing Road Trip fuel prices. This corroborates the migration hazard. It is not an SCS engine specification, evidence that this user has that economy mod, or a report of this exact NaN. The search index returned the post text; direct page opens failed during this inspection. [Original forum post](https://forum.scssoft.com/viewtopic.php?p=2166753)

## Competing mechanisms

- **Hypothesis — most supported: omitted petrol price.** It explains the screenshot's zero unit price, the many-station Canadian boundary, the working US control, the installed engine fuel type, and the exact connector override. A price/display defect can coexist with working interaction and tank filling.
- **Hypothesis — less supported: units or exchange conversion.** Both lower ProMods and winning connector BC files set the same `imperial_units: false`; only the lower one supplies `petrol_price`. The inspected country files have no per-country currency/exchange field. Installed `def/economy_data.sii` has finite nonzero ratios, USD `1` and CAD `1.3909`; `car_economy_data.sii` has no country fuel-price/currency override. A user's gallon selection alone does not show a faulty conversion. Effective Workshop/UI overrides remain a boundary, and switching to litres is a useful secondary check.
- **Hypothesis — less supported: generated co-located services.** The generator adds service/node identities, the petrol service flag and locator, reciprocal references and private prefab resources. Its supported service layout has no independent fuel-price field, and archive inspection confirms none of the six delivered r1 fixes contains `def/country/`, `def/economy_data.sii` or `def/car_economy_data.sii`. User-reported working filling and US behavior weaken a generic service-duplication failure. They do not rule out every service/engine interaction; the unchanged station geometry in the proposed test isolates this alternative.
- **Unknown:** exact engine fallback, whether UI quantity derives from cost, actual amount purchased/charged at a zero-price station, and the country attached to each reported affected location. Do not infer these from `-nan(ind)` alone.

## Smallest discriminating next test

**Hypothesis — proposed, not generated or run:** first identify one affected **ProMods BC (`country.data.bc`)** station and preserve a before-test screenshot/save. Keep the map/vehicle/UI settings and r1 station fix constant. In a disposable/copied profile, test one country-definition override based on the **winning connector** `def/country/bc.sui`, adding only:

```sii
petrol_price: 1.502116
```

The value is copied from the supplied ProMods 1.6.4 file, with its existing dated provenance; it is not a new price estimate. The diagnostic override would need priority above the connector and any other actual writer of that path. Preserve `fuel_price: 1.630`, the connector country position, all other fields and every station resource. Do not reorder the source maps or restore the lower country file wholesale.

Compare the same pump before filling: the unit price should become positive and initial quantity finite zero. Then independently record finite quantity as filling proceeds, tank increase and balance decrease. A truck comparison should retain its diesel-price behavior. Disable the diagnostic override and repeat the panel check if practical. A repaired price with persistent NaN would falsify the simple missing-price explanation and focus the next check on the UI/unit calculation. A finite panel and consistent purchase at unchanged station services would strongly support the country-price cause.

For Western Canada's other province definitions, selecting new petrol prices requires an explicit sourced policy. Copying diesel values into petrol or inventing current CAD/USD conversions would silently change the economy and is outside this research. Confirm the affected country first; a ProMods BC-only test does not validate Western Canada's separate `country.data.kbritcolum` or other provinces. No definition patch, regenerated station package, live installation, save edit or game test was performed here.

## Reproducibility and verification

Research artifacts are under `local_outputs/work/2026-10-18_01-04-55/nan-research/`: the six freshly extracted official definitions, `official-cache-freshness.json` with hashes/equality results, `primary-source-notes.json` with source dates and access limits, and `independent-selected-country-review.json` with fresh ZIP member hashes/field values. The installed source was `/mnt/c/Program Files (x86)/Steam/steamapps/common/American Truck Simulator/def.scs`; it remained read-only. The main research agent independently reread both ProMods/connector BC files and all six Western Canada province files directly from the supplied ZIP archives and reviewed the generator's service-copy mutations. Delegated inventory evidence is recorded alongside this investigation; no source archives or historical outputs were changed.
