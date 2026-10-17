# Passenger-car refueling

Inspected: 2026-10-17. SCS's 1.61 release post concerns ATS map preparation for Road Trip; the prefab locator page describes shared ATS/ETS2 asset authoring, not a complete car fueling specification. **Documented** cites SCS; **observed locally** requires local files or a game test; **hypothesis** needs testing; **unknown** lacks sufficient evidence. No installed station or car definitions were inspected for this note.

## Three distinct questions at a station

1. **Physical access — documented:** In its ATS 1.61 release post, SCS says it added gas stations intended to serve cars once Road Trip released. A car still needs a reachable route and pump area in the effective map/prefab. The announcement does not say every existing map-mod station works for cars. [ATS 1.61 update release](https://blog.scssoft.com/2026/09/american-truck-simulator-161-update-release.html?m=0)
2. **Interaction — documented:** SCS prefab locators can define trigger areas and actions when a player enters or manually activates them. The page also discusses gas-station AI behavior. These facts support inspecting the effective station prefab and its interactions, but they do not identify a specific 1.61 car-fueling trigger name or guarantee that a visible pump is interactive. [Prefab locators](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators)
3. **Vehicle eligibility — documented:** SCS's `accessory_engine_data` page says the engine `type` token accepts `diesel`, `electric`, and `petrol`, with `petrol` added in 1.61. The page describes powertrain behavior; it does not alone establish the complete fuel purchase or pump eligibility rule. [accessory_engine_data](https://modding.scssoft.com/wiki/Documentation/Engine/Units/accessory_engine_data)

**Unknown:** Which of those layers fails at a particular map-mod station, and whether its fix is a definition, prefab, map-sector edit, or another mechanism. Passenger-car refueling might be harder than a text-only compatibility patch. Do not promise a common fix across stations or reuse a courier-job fix without evidence.

## Minimal controlled comparison

- **Hypothesis:** Compare one official station where the same Road Trip car can refuel and one modded station where it cannot. Record ATS build, DLCs, car and engine, fuel level, active mod order, station coordinates, ability to enter the forecourt, prompt/trigger behavior, and game log. A truck test at the same station helps distinguish general station failure from a car-specific failure.
- **Hypothesis:** If the car cannot reach the pump, inspect map placement and prefab routes. If it reaches the pump but gets no prompt, compare the effective prefab interaction. If the prompt appears but fuel cannot be bought, compare vehicle and fuel eligibility. These are diagnostic branches, not proven causes.
- **Unknown:** Ease of repairing passenger-car refueling in third-party maps. Keep generator scope conditional until a reproducible before/after patch demonstrates which files are sufficient.

See [Map structure and compatibility](./MAP_STRUCTURE_AND_COMPATIBILITY.md), [SCS archives and definitions](./SCS_ARCHIVES_AND_DEFINITIONS.md), the separate [Economy and courier jobs](./ECONOMY_AND_COURIER_JOBS.md), and [Local input inventory](./LOCAL_INPUT_INVENTORY.md).
