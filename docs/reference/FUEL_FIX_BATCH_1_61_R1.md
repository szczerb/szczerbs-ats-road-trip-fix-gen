# Fuel fix batch: ATS 1.61, revision r1

Prepared: 2026-10-17. Collection timestamp: `2026-10-17_22-46-14` (Europe/Warsaw). **Observed locally:** five experimental packages were produced using one source-map CLI invocation per map, without per-station recipes or language-model patch generation. All coverage reports are complete with zero blockers. **Unknown:** gameplay across all these points; the earlier single Helena pair is the only user-reported dual-vehicle refueling test.

The verified collection is in ignored `local_outputs/generated/2026-10-17_22-46-14/`, with `BATCH_MANIFEST.json` and `SHA256SUMS.txt`. Individual generation audits retain their own timestamped work directories; the collection copies preserve their original package bytes. Collection verification/rechecks are in `local_outputs/work/2026-10-17_22-46-14/release-verification/`.

| Map | Supplied source version | New car fuel points | Includes garage points | Changed fuel prefabs | Changed sector files | Bytes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ATS Expansion | 23.0 | 894 | 41 | 515 | 202 | 59,391,874 |
| Reforma | 3.0.1.161 + Mega Resources 3.0.1.161 | 954 | 46 | 622 | 185 | 66,888,118 |
| ProMods Canada | 1.6.4 (all four packages) | 102 | 11 | 69 | 28 | 9,000,655 |
| Western Canada | 1.7.3 + supplied ProMods companions | 288 | 30 | 162 | 118 | 5,213,090 |
| Alaska | 1.2.3 | 43 | 5 | 24 | 18 | 503,354 |

Totals: **2,281** added car interaction points, including **133** garage points. Prefab counts are not unique physical station counts. Existing car points and every original truck record/node were retained. The packages retain author `szczerb`, family name `szczerb's Road Trip Gas Stations Fix for <map name>`, matching map-labelled C artwork and version `1.61-r1-experimental`.

## Output fingerprints

All filenames start `szczerbs-road-trip-gas-stations-fix-` and end `-1.61-r1-experimental.scs`.

| Map slug | SHA-256 |
| --- | --- |
| `ats-expansion` | `0fab6ce3fc6f1a6d0aeb503ca0a868d212aca7ccd453c20831e7ada732b0e0e2` |
| `reforma` | `34a75f7f5afdc27ce49efdf5d1ffd43e4c38572dc2f56b8ed6bebda5af3c880f` |
| `promods-canada` | `c39f1ea3ce6548f3a80965c91349313e01fbcccb5e632d9568df09e99d65da65` |
| `western-canada` | `81c249d9c3a5912fdfa74f3158737d2ab32d39e1e2ceb34e4e2f138c7b3706b4` |
| `alaska` | `16fe7631cd4b6b96984ad727f7a98fb41d0552457bc4425bd1af550aacd8a8b6` |

## Verification performed

- All 1,220 source `.base` and 1,220 `.aux` files parsed with complete structural boundaries. Exactly empty legacy sectors were classified as having no fuel targets; no nonempty unknown layouts were accepted.
- **111 unit/integration tests passed**, including multi-point/origin/grade matching, existing partial car data, legacy PPD conversion guards, opaque source-attribute preservation, source drift refusal, failed audits, deterministic repeated planning, visibility/layer updates, orphan FuelPump bounds and both-mode byte preservation.
- Independent verification checked all five ZIP CRCs; exact name/author/version/icon; generated resource and sector source/output SHA-256; all original Service/FuelPump and node bytes; sorted node tables; every new service's flags, exact co-located node transform and reciprocal parent references. **All 2,281 new services passed**, with zero findings. The rerunnable script and JSON are in ignored `local_outputs/work/2026-10-17_22-11-10/verification/`.
- Repackaging each archive through the writer using its exact report/resources/metadata was byte-identical for all five; every collection copy also matches the original generation. This checks deterministic serialization, alongside the planner determinism tests. No game/profile installation or gameplay run was performed by the agent.
- Original archives were read only. Source assets, extractor binaries, caches, full reports and generated `.scs` files remain ignored; tracked changes contain independently authored code/tests/docs and small artwork exports only.

The implementation caught and resolved two real Reforma terrain cases before releasing a package: the 72-metre control span rises about 2.94 metres, requiring projected rather than normalized horizontal rotation; a three-control prefab has cross-slope requiring a fitted elevation plane. An ATS Expansion/stock boundary contains a pre-existing unlisted truck FuelPump UID; unique geometric matching accepts this narrow case, preserves every old reference and record, and adds only the car counterpart. These are coded/general checks, not hand-written per-location patches.

## Load priority and next user test

**Put each fix immediately above its own source map and disable all old r0 samples.** Keep the maps' existing relative priority. Do not move all fixes together above every map. Exact changed-sector intersections were found for ATS Expansion–Western Canada (**6**), Alaska–Western Canada (**3**) and ProMods Canada–Western Canada (**15**); the other seven pairs have zero intersections. Higher-priority connection or compatibility patches still determine the effective sector and may require a separate generation stack.

For the first full-map test, use the **nearer station inside Helena**, prefab `1e00i`, UID `0x42dd66b86ad1d49f`, in `map/usa/sec-0016-0013.base`. The ATS Expansion fix now includes all **four** truck GAS points there, adding four car twins under private alias `rtgcc777400`. This is the station excluded by the first single-point prototype. The eastern previously tested point is included too.

Check actual car/truck refueling and reloads, not only icons. Garages are an experimental extension; car access, ownership/price/discount behavior and other mode-specific effects still need observation. No geometry, roads, dispensers, courier data, profile or economy-reset operation was changed by this generator.

See [single-command reproduction and mechanism](MAP_WIDE_FUEL_GENERATOR.md), [input versions](LOCAL_INPUT_INVENTORY.md), [dated gameplay evidence](VALIDATION_RESULTS.md) and active [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md).
