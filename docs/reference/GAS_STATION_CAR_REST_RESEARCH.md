# Gas-station car rest research

**Status:** Initial evidence inventory; investigation is active under [TASK-0039](../tasks/active/TASK-0039-research-gas-station-car-rest.md).

## User direction and boundary

The requested experiment covers both painted passenger-car parking bays and unmarked station geometry, including the reported Dawson City case. The intended tool is a separate, deterministic optional processor that targets only individually selected stations. It must not apply the existing 1,000-unit proximity or density rules, join the existing rest processor's policy, alter shared actions, or clone truck geometry as a fallback. No game launch, profile edit, mod installation or live-save change is part of this research.

## Evidence status

**Unknown — source representation (2026-10-19):** the exact map/game source placement, prefab geometry, action flags and relationship between the Dawson City gas station and rest-capable lot geometry have not yet been established. The screenshots below identify the visual location context supplied by the user; they are not a substitute for definition-level provenance.

**Unknown — painted bays (2026-10-19):** it is not yet established how painted car bays are represented in the applicable ATS/map data, or whether they have independent geometry or rest actions that can be safely associated with an individually selected station.

**Documented — existing project boundary:** current rest generation uses independent native car-only markers and a 1,000-unit proximity criterion. This new experiment is intentionally independent and does not inherit that selection policy. See [ADR-0017](../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md) and [processor coverage and limits](COMPATIBILITY_PROCESSORS.md).

## Dawson City user screenshots

These user-provided in-game screenshots show the station/cafe approach, nearby seating, and the Dawson City map view. They establish what location the report refers to, not that the lot supports passenger-car rest in game.

![Dawson City gas station and cafe viewed from the vehicle](images/gas-station-car-rest/dawson-city/ats_20261019_004222_00.png)

*Dawson City station/cafe from the vehicle, screenshot timestamp 2026-10-19 00:42:22.*

![Cafe-side seating and nearby station lot](images/gas-station-car-rest/dawson-city/ats_20261019_004242_00.png)

*Cafe-side seating and the adjacent lot, screenshot timestamp 2026-10-19 00:42:42.*

![Dawson City map view with service markers](images/gas-station-car-rest/dawson-city/ats_20261019_004305_00.png)

*World-map view centered on Dawson City, screenshot timestamp 2026-10-19 00:43:05.*

## Required investigation and processor shape

1. Pin the applicable ATS and map versions and identify the exact station placement in source data.
2. Trace station prefab membership, neighboring geometry and any rest-capable polygons/actions, retaining original geometry and truck/bus/shared behavior.
3. Inspect painted car bays as a separate representation question and determine whether native car-only markers can align with actual car-sized spaces.
4. Specify explicit station identifiers as the only selection input. Unknown flags, malformed/nonfinite geometry, ambiguous station membership or unsafe action layouts must block generation rather than invoke a proximity heuristic or truck-geometry clone.
5. If evidence supports a candidate, validate deterministic output, source preservation and isolated selection through meaningful automated checks. Give the user a manual handoff for car approach/rest interaction and independent truck/bus/shared controls.

An eventual plan view should show the source station footprint, each proposed car marker footprint and orientation, painted-bay boundaries where present, walking/vehicle access, and every retained source rest marker. It must distinguish measured coordinates from illustrative sketches. The Dawson case should be rendered from exact source coordinates only after the placement is found.

## Screenshot integrity

The three files were copied from `local_inputs/gas-station-car-rest/dawson-city/` on 2026-10-19. SHA-256 checksums, identical between source and documentation copies:

| File | SHA-256 |
| --- | --- |
| `ats_20261019_004222_00.png` | `d2902bb005f71b61efb844ac1ff164ca839dd5b3b72984bcc6e275e345a4994d` |
| `ats_20261019_004242_00.png` | `78810d765ee992ebc3fd21b2c019899e4d461e6fdd36df2f0769cfb9f3a00965` |
| `ats_20261019_004305_00.png` | `09203d765d2f89a9cd098caaf3bda9175398a80abdb605babbfcd5126a1a62c2` |

## References

- [Existing passenger-car rest research](PASSENGER_CAR_REST_RESEARCH.md)
- [Independent car-marker geometry decision](../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md)
- [Compatibility processor coverage and limits](COMPATIBILITY_PROCESSORS.md)
- [TASK-0039](../tasks/active/TASK-0039-research-gas-station-car-rest.md)
