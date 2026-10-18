# Reasonable gas tank upgrades

Inspected: 2026-10-18. Product: ATS **1.61.3.18**, installed `dlc_rt_ford.scs`. This is a separate vehicle-capacity mod, independent of map access and job-class eligibility. [TASK-0028](../tasks/done/TASK-0028-build-reasonable-gas-tank-upgrades.md) records implementation and delegation; [ADR-0015](../architecture/decisions/ADR-0015-source-pinned-reasonable-tank-upgrades.md) records the policy.

## Selected capacities

**Observed locally:** selective reads from the installed Ford archive give the following stock chassis values. **Documented:** the named real-world tank options exist in the sources below. Choosing them for the simulated vehicles is an explicit mod policy, not evidence that the unmodified game models those upgrades.

| DLC vehicle | Stock game litres | Selected litres | Decision |
| --- | ---: | ---: | --- |
| Mustang Fastback 1967 | 61 | **76** | Nominal 20 US gal, adapted 1969 tank; +24.6% over the game value |
| Crown Victoria 2006 | 72 | 72 | Unchanged: no adequately supported moderate larger gasoline tank found |
| F-150 2023, four-door, 5.5-ft box, 5.0 V8 | 98 | **136** | Nominal 36 US gal, Ford extended-range option; +38.8% over the game value |
| Bronco 2024, four-door | 79 | 79 | Unchanged: no adequately verified moderate larger replacement found |

One US gallon is 3.785411784 litres. The selected nominal sizes convert to 75.708 and 136.275 litres; the game policy rounds to whole litres. Percentage changes above use the actual game values, not the nominal 16/26-gallon descriptions. All gallon references here are **US**, not Imperial.

## Automotive evidence

**Documented — Mustang:** manufacturer [Dorman 576-175](https://www.dormanproducts.com/p-47090-576-175.aspx) specifies a 20-gallon tank for the **1969** Mustang/Cougar. The tank supplier's own [1969 tank listing](https://secure.cougarpartscatalog.com/store/p/12933-Fuel-Tank-Economy-Repro-1969-Mercury-Cougar-/-1969-Ford-Mustang.html) explicitly describes fitment to 1967–68 cars with filler-neck adjustment and preferably the corresponding sender. This supports the user's later-year-tank idea; it does not support saying the swap needs no adaptation. These are first-party product/fitment statements, not an OEM-approved retrofit. Inspected 2026-10-18.

**Documented — alternative, not selected:** a [1967–68 22-gallon conversion kit](https://www.cjponyparts.com/fuel-tank-conversion-kit-22-gallon-mustang-1967-1968/p/FTK16/) is also marketed, using a 1970-style tank and conversion filler pipe. The initial policy deliberately chooses the smaller 20-gallon option. Neither option establishes how common a conversion is in real-world ownership; prevalence remains **Unknown**. The local stock 61-L capacity and 16-gallon description agree approximately with the original capacity.

**Documented — F-150:** Ford's [2023 F-150 order guide](https://dealerimages.dealereprocess.com/image/upload/v1679674915/1/ford/PDFs/2023_F-150_Order_Guide.pdf), Ford Division document distributed by a dealer host, lists **Extended Range 36 Gallon Fuel Tank**, option **655**, with configuration restrictions (PDF pages 6/12/17, zero-based pages 5/11/16). The guide includes the 145-inch-wheelbase SuperCrew/5.5-ft-box configuration. The 3.5L PowerBoost hybrid is excluded; do not generalize this policy to that drivetrain or every F-150 body style. **Observed locally:** the installed DLC supplies one F-150 engine, `ford_tivct_32v_v8.sii`, with `volume: 5.0` and `type: petrol`, and chassis `4doors_55_awd.sii`. The OEM extended-range option is a better basis than inventing an intermediate 30-gallon size. Inspected 2026-10-18.

**Documented — Crown Victoria:** Ford's [2006 owner's guide](https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/06croog1e.pdf), printed page 253, lists 19.0 gallons / 71.9 L. This matches the local game's rounded 72 L. **Unknown:** a credible moderate larger gasoline tank compatible with this civilian model. Searches did not establish one. CNG police/taxi cylinders, custom fuel cells and a different vintage of Crown Victoria do not establish such an upgrade.

**Observed locally — Bronco:** `ford.bronco_24/chassis/4doors_awd.sii` contains 79 L and a nominal `20 @@gal@@` info line. These are distinct fields; their imperfect agreement is retained, not silently normalized. Older SCS material and Ford market specifications differ in year/capacity labelling. **Unknown:** a sufficiently verified, model-appropriate moderate larger tank. The initial policy keeps the game source unchanged rather than inferring an upgrade from another Ford or an unsupported vendor claim. No conclusion that a custom conversion is impossible is intended.

## Engine mechanism and exact scope

**Documented — shared engine:** SCS describes [`accessory_chassis_data.tank_size`](https://modding.scssoft.com/wiki/Documentation/Engine/Units/accessory_chassis_data) as fuel capacity in litres. This older shared ATS/ETS2 reference is not by itself proof of every Road Trip runtime behavior. **Observed locally:** the Ford DLC uses that same unit and field under `def/vehicle/car/`. No `fuel_tank_size` accessory override was found in the extracted Ford car definitions. The package edits the existing chassis; it adds no visible model, shop accessory, fuel-consumption change or upgrade purchase price.

Two complete virtual files are overridden, with only the live `tank_size` numeric value and matching capacity `info[]` value changed:

- `def/vehicle/car/ford.mustang_67/chassis/rwd.sii`
- `def/vehicle/car/ford.f150_23/chassis/4doors_55_awd.sii`

The four-model [TOML policy](../examples/reasonable-gas-tank-upgrades.toml) pins the exact game version, canonical paths/units and complete stock-file SHA-256 values. All four are validated, including the two intentionally unchanged models; those two files are **not** packaged. The policy records rationale and source URLs. Runtime generation uses deterministic values from this reviewed policy; it does not ask an LLM to select capacities.

The planner preserves all other original bytes, including relative includes, comments, encoding/newlines and Mustang sibling suspension-animation units. It reparses changes and compares all unit attributes. Unsupported layouts, missing includes, source drift, wrong units or invalid policy block publication atomically. The 1.6x maximum is an implementation guard for this moderate-upgrade policy, not a universal physical-fitment rule. A future source/game update needs review and a new fingerprint, not blind hash replacement.

## Commands and load order

From the repository root, with Python 3.11+ and the existing [HashFS extractor](TOOLING.md):

```bash
PYTHONPATH=src python3 -m ats_road_trip analyze-tank-upgrades \
  --config docs/examples/reasonable-gas-tank-upgrades.toml

PYTHONPATH=src python3 -m ats_road_trip generate-tank-upgrades \
  --config docs/examples/reasonable-gas-tank-upgrades.toml --experimental
```

Both commands accept `--game-dir`, ordered archive `--dependency` values and `--run-id`. Generation also accepts `--revision` (default **0**) and an optional 276x162 JPEG `--icon`. Analysis writes a report only and never invokes the mod writer. Archives/extraction/audits remain in ignored Warsaw-timestamped work/output directories. Existing outputs are not overwritten.

Display name: **szczerb's Road Trip reasonable gas tank upgrades**. Author: **szczerb**. Version: **1.61-r0-experimental**. The shorter filename is `szczerbs-road-trip-reasonable-gas-tank-upgrades-1.61-r0-experimental.scs`; category `other`, required DLC `dlc_rt_ford`. The original project icon is [reasonable-gas-tank-upgrades.jpg](../../assets/mod-icons/reasonable-gas-tank-upgrades.jpg), generated with the built-in image tool and exported to 276x162 JPEG. It is provisional artwork, not a user-approved replacement for any existing map/courier icon.

**Disable Ford Fuel X3 / other capacity mods first.** Place this mod above other vehicle mods that override either of these chassis paths. Whole files win by priority; lower-priority edits to the same chassis are not merged. Job Types Compat Mustang changes a different resource, so its relative order and the source-relative map-fix order do not need to change. Do not silently feed the old 3x mod as a dependency: its different source bytes should block this stock-pinned policy.

## Runtime boundary and next test

**Unknown:** whether the existing owned car's capacity refreshes immediately on load, how fuel saved above the new smaller limit is handled, exact UI range/fuel-gauge behavior and any shared Quick Jobs effect. Generation does not touch saved fuel or make fuel-level migration promises.

With the old 3x mod disabled, check the existing Mustang and F-150 show the intended capacity, can refuel above their stock limits, stop at the new limits, and retain sensible fuel after save/reload. Also verify price, charged amount and consumption remain sensible. Crown Victoria and Bronco should retain stock capacity. If a displayed capacity does not refresh on the owned car, report it before attempting profile edits or purchasing another vehicle. Follow [the manual checklist](MANUAL_TEST_CHECKLIST.md); pending Canada fuel-price and car-rest checks remain separate.

## Verified r0 handoff

**Observed locally — 2026-10-18:** generated candidate `local_outputs/generated/2026-10-18_18-06-57/szczerbs-road-trip-reasonable-gas-tank-upgrades-1.61-r0-experimental.scs`, **46,674 bytes**, SHA-256 `95bf7495c1274917ac1eccd5b13b367ce66376b363a884629a649ce99b51dc5e`. ZIP CRC, manifest, required DLC, JPEG dimensions and report/resource checksums pass. Independent GPT-6 Luna/medium reconstruction from read-only stock bytes confirms exactly the two approved field edits in each of the two chassis; all sibling animation bytes remain identical. No map/job resources or unchanged-model chassis are packaged.

The complete authored suite passes **266 tests**, including 18 new planner/workflow tests for source drift, sibling preservation, effective resource priority, blocked plans, analysis/generation separation, metadata and CLI acknowledgement. An initial real-data analysis correctly blocked because the first implementation expected a single unit per file; all four Ford chassis actually contain additional animation units. That limitation was fixed and tested before generation. A later report-only run at `2026-10-18_18-19-12` reports complete coverage with zero generated packages. The original failed audit is retained rather than overwritten.

Ignored evidence is grouped under `local_outputs/work/2026-10-18_18-06-57/`: stock inspection, three automotive reports, independent audit, unit-test log and generated audit. No game launch, installation, profile write or existing map/courier repack occurred. Gameplay remains pending in TASK-0007.
