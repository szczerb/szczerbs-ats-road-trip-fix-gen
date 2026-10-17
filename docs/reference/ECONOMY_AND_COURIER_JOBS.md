# Economy and Road Trip courier jobs

Inspected: 2026-10-17. SCS's company/cargo unit pages describe established ATS/ETS2 freight definitions; SCS's September 2026 Road Trip posts describe player-facing ATS Road Trip behavior. Neither is a complete courier data schema for ATS 1.61. **Documented** cites SCS; **observed locally** requires installed content or a game test; **hypothesis** needs testing; **unknown** lacks sufficient evidence. No local game data was inspected for this note.

## Established freight relationship

- **Documented:** A `company_permanent` definition supplies common company data. Its `out_cargo`, `in_cargo`, and `city_names` lists are generated from `cargo_def` files in the company's `out/` and `in/` folders and `company_def` files in its `editor/` folder; SCS says not to set those arrays manually. A `cargo_def` associates a cargo unit with a company as output or input. A `company_def` associates a city and prefab with the company. This gives a useful baseline for comparing two maps' conventional freight, but does not prove how courier jobs are registered. [company_permanent](https://modding.scssoft.com/wiki/Documentation/Engine/Units/company_permanent), [cargo_def](https://modding.scssoft.com/wiki/Documentation/Engine/Units/cargo_def), [company_def](https://modding.scssoft.com/wiki/Documentation/Engine/Units/company_def)

## Road Trip behavior confirmed by SCS

- **Documented:** Road Trip adds courier Quick Jobs with a supplied vehicle and company-paid expenses, and a Dispatch Market for an owned vehicle with higher payout and player-paid fuel/repairs. Examples include packages, documents, and vehicle transfers; the vehicle type can affect available work. [Road Trip: Quick Jobs & Freight Market](https://blog.scssoft.com/2026/09/road-trip-quick-jobs-freight-market.html?m=1)
- **Documented:** Customer reviews assess timing, vehicle appearance, and cargo handling. Courier Rating affects job types, maximum route distance, and earnings. Money goes into the existing ATS profile, while courier rating and reviews provide Road Trip progression rather than a separate XP system. [Road Trip: Quick Jobs & Freight Market](https://blog.scssoft.com/2026/09/road-trip-quick-jobs-freight-market.html?m=1)
- **Documented:** SCS announced the Road Trip: Ford DLC release on 2026-09-29 with Car Mode, Quick Jobs, and Dispatch Market. The earlier preview called the owned-car equivalent of Freight Market the Dispatch Market; use the release name in player-facing notes. [Road Trip: Ford DLC Release](https://blog.scssoft.com/2026/09/road-trip-ford-dlc-release.html?m=1)

## Investigation boundary

- **Unknown:** SCS's cited sources do not identify the complete ATS 1.61 courier registration schema, pickup/drop-off marker format, or exact conditions for showing a job in a map-mod city. Do not equate conventional `in/` and `out/` cargo files with courier support.
- **Hypothesis:** A particular absence of jobs might reflect rating, vehicle eligibility, or other market conditions even if location data is valid. The documented eligibility rules justify controlling those variables during a comparison; they do not diagnose the user's cases.
- **Hypothesis:** Courier availability may depend on both economic definitions and placed or eligible pickup/drop-off locations. Compare an official working area and a failing mod area at the same game version, owned DLCs, profile rating, vehicle, and active mod order. Record static source-file observations separately from a marker rule validated by a controlled in-game result.
- **Hypothesis:** Gemini's proposed missing-marker/company-prefix explanation might account for absent courier jobs. There is no verified 1.61 source or local comparison in this note establishing that cause. Keep it as a test candidate, not a generator rule.

See [Map structure and compatibility](./MAP_STRUCTURE_AND_COMPATIBILITY.md) for placed prefabs and binary sectors, [SCS archives and definitions](./SCS_ARCHIVES_AND_DEFINITIONS.md) for packaging and syntax, [Passenger-car refueling](./PASSENGER_CAR_REFUELING.md) for the separate fueling track, and [Local input inventory](./LOCAL_INPUT_INVENTORY.md) for installed inputs.
