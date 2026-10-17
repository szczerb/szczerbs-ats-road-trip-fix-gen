# Fuel access and petrol-price batch: ATS 1.61, revision r2

Prepared: 2026-10-18. Run timestamp: `2026-10-18_01-27-24` (Europe/Warsaw). Applies to the eleven supplied map/resource archives and installed ATS 1.61.3.18. **Documented — user authorization:** fill the evident missing petrol fields now, with manual confirmation of the Canadian display/billing issue later. The user has finished gameplay for tonight. [ADR-0007](../architecture/decisions/ADR-0007-repair-missing-petrol-prices.md) records the policy.

## Generation scope

`generate-map-fuel SOURCE --experimental` now includes country petrol-price inspection and repairs. Its current default revision is 2; explicit older revisions do not reproduce older algorithms. Historical r0/r1 archives remain unchanged. Known source-family dependencies and explicit low-to-high priority are retained.

| Package | Car fuel interactions added against its source | Missing petrol fields added |
| --- | ---: | ---: |
| ATS Expansion | 894 | 0 |
| Reforma | 954 | 19 estimated |
| ProMods Canada | 102 | 0 |
| Western Canada | 288 | 6 estimated |
| Alaska | 43 | 1 estimated |
| Reforma OtherMaps Patch | 0 | 19 estimated |
| Western Canada ProMods Connections | 50 | 1 restored |

These are independent package counters, not unique combined coverage. The nineteen Mexican country paths occur in both Reforma and OtherMaps; OtherMaps wins in the confirmed source order. The combined set has **27 distinct added country paths**, from **46 additions across seven packages** (45 estimates, one lower-source restoration).

The existing six packages' station resources must remain byte-identical to r1. The new OtherMaps package contains only country overrides plus metadata/report, because its station-target count is zero. A price repair does not implement rest eligibility or change the station positions, roads, geometry, existing truck interactions, fatigue settings, saves or vehicle definitions.

## Price policy

Keep a positive finite existing petrol price. When absent or invalid, first restore the highest valid lower-priority value from the **same path and country unit**, copying only that field. Connector BC thus receives ProMods' `petrol_price: 1.502116` while preserving connector diesel `1.630` and its country position.

Where no such value exists, use `source fuel_price × (1.47197 / 1.92132)`, rounded to eight decimals with `ROUND_HALF_UP`. The ratio comes from the installed **game-only** Washington country, with source hash and inputs recorded. This is a game-economy estimate; it does not represent independently researched current Canadian/Mexican/Alaskan retail prices. A reference drift or invalid/ambiguous definition blocks generation rather than silently publishing incomplete coverage. `--petrol-reference` selects an explicit alternative game country.

All other source bytes/attributes are retained. Do not restore a complete lower-priority country file: that would also change diesel price and position. Source scope applies to each package's own effective country definitions; it is not a complete audit of every Workshop economy/UI override.

## Install and later test

Disable superseded r1/r0/sample versions when using r2. Keep every fix directly above its own source, preserving the screenshots' map order. In particular: connection fix above Western Canada ProMods Connections; OtherMaps fix above Reforma OtherMaps; ProMods fix above its Map package (Definitions may remain above it). Do not collect all fixes at the top.

**Manual validation remains pending.** Check a positive Canadian petrol price, finite initial zero and increasing quantity, actual tank and balance changes, the US control, truck diesel behavior, garages where used and reload. A finite positive definition is not proof that the whole `-nan(ind)` symptom is cured. See the [manual checklist and reminder](MANUAL_TEST_CHECKLIST.md). No rest patch is included; [rest research](PASSENGER_CAR_REST_RESEARCH.md) identifies a separate action filter and next experiment.

## Artifacts and verification

Generation/audits/logs and independent verifier: `local_outputs/work/2026-10-18_01-27-24/`. Generated archives: `local_outputs/generated/2026-10-18_01-27-24/`. All seven source commands exited zero with complete coverage. The independent verifier passed **7/7** packages, all **46** source-byte/policy checks and all **27** combined effective country files. Every previous station gameplay resource is byte-identical to r1; only country resources and metadata/report were added/updated. Original eleven archives and one sidecar remain unchanged.

All `.scs` filenames use `szczerbs-road-trip-gas-stations-fix-<slug>-1.61-r2-experimental.scs`:

| Slug | Bytes | SHA-256 |
| --- | ---: | --- |
| `alaska` | 516,616 | `7a6360db60912cf77096ee3780501318c38892b375f3723be82bd4377796145f` |
| `ats-expansion` | 59,401,425 | `dc799b4fa7e42f0220e8ad1f853088b34d9b336f02b263bee8ccc360f7006ea1` |
| `promods-canada` | 9,011,181 | `80af7ea9256c0b12d80afaca190ef291cbc7d8fcba92f8c026d0c480d67cb804` |
| `reforma` | 66,961,991 | `89672d9a90f2f1ea1f3aa37d3d23156f0def847db58f6b8cc60d9ff769ff28af` |
| `reforma-othermaps-patch` | 117,678 | `5dcea190cfa36e33a8e1c221b7af77cd03e2f2656954b002ecda2d8070d6f5d0` |
| `western-canada` | 5,246,674 | `d9959c7f97d17997eefa7c87cbe23b7dea7bcc8128d73c743ca10c75047b6fad` |
| `western-canada-promods-connections` | 2,670,424 | `c8b1c3123c9813b983d483b67ef599bff3e14424b711f88ef791fa8ccb7d4c75` |

The same folder has `BATCH_MANIFEST.json`, `SHA256SUMS.txt`, `INSTALL_AND_TEST.txt`, and a convenience bundle, `szczerbs-road-trip-gas-stations-fixes-1.61-r2-experimental.zip`: **62,601,876 bytes**, SHA-256 `68f3c5bb156e03be6882587dd0e31f3aad14d0fb5462c2503e13fb646a249974`. Extract the bundle and install its `.scs` files individually; the bundle itself is not a game mod. Bundle CRC and contained package hashes pass. No supplied archive or live game/profile was modified.

The code baseline has **131 passing unit/integration tests**, covering source priority, numeric validity, explicit policy coverage, all other country attributes and CRLF preservation, idempotence, lower-source restoration, game-only reference isolation, missing/ambiguous inputs, extreme-number blockers, deterministic packaging and the prior station graph cases.

See [TASK-0014](../tasks/done/TASK-0014-audit-and-test-petrol-price-overrides.md), the [original Canadian symptom and diagnosis](CANADA_FUEL_DISPLAY_RESEARCH.md), and the historical [r1 map batch](FUEL_FIX_BATCH_1_61_R1.md) / [r1 connector](CONNECTOR_FUEL_FIXES.md).
