# Dawson City station-parking PoC handoff

Date: 2026-10-19. ATS **1.61.3.18**, Alaska Expansion **1.2.3** as the winning source in the supplied combined map stack; Western Canada Expansion **1.7.3** supplies the earlier standalone comparison. This is a local experimental handoff on `codex/gas-station-car-rest-research`, based on master `445ef58`; implementation milestone `4aaeea8`. The branch and its managed worktree are retained. No merge, push, publication, live installation, game launch or profile edit was performed.

[Research, screenshots and limits](GAS_STATION_CAR_REST_RESEARCH.md) · [Decision](../architecture/decisions/ADR-0018-isolate-source-pinned-station-parking-poc.md) · [Task](../tasks/done/TASK-0039-research-gas-station-car-rest.md)

## What to compare later

Both alternatives target **one station**: Dawson City's eastern Chemron-model truck stop, sector `map/usa/sec-0029-0045.base`, original prefab UID `0x5ca1fea582800001` (`us_gas_08`). The supplied screenshots are embedded in the research report.

| Alternative | New car rest area | Position in prefab-local XZ, metres |
| --- | --- | --- |
| `painted_bays` | One bank covering three paint-derived car bays; four actual mesh separators, about 2.858 m pitch | X approximately **17.077–25.340**, Z **−20.894–−14.990**, after a generic 0.25 m inward trigger margin |
| `unmarked_geometry` | One **3 × 6 m** proposal near the building, plus a checked **3 × 4 m** approach strip | X **12.766–15.766**, Z **−19.270–−13.270** |

The methods are alternatives, not a combined policy. The unmarked method does not consume paint to construct its proposal; this particular real model nevertheless also contains painted bays nearby. Successful analysis of a genuinely unmarked different prefab family remains future research. The named model's ground under the selected areas is sampled at approximately Y **0.139318 m**; world elevation at Dawson is approximately **44.214844 m**. The plan views show local geometry; exact world vertices are in each audit.

## Installation for a controlled test

Use a copied/disposable test profile when convenient. There is no need to start the game now to complete this research handoff.

1. Keep **Alaska Expansion 1.2.3**, **Western Canada Expansion 1.7.3**, and the other source maps enabled in their confirmed relative order.
2. Disable the existing **Alaska Expansion r9 combined fix**, and any earlier Alaska fuel/rest fix, including the fuel-only r2 used as the generator's input.
3. Enable **exactly one Alaska-based Dawson PoC**, directly above **Alaska Expansion**, in the position previously occupied by its Alaska fix. The PoC already contains the pinned Alaska fuel-only payload. Do not stack the two PoCs or enable Alaska r2/r9 alongside one.
4. **Keep WCE r9 and the other source-specific fixes enabled** in their existing source-relative positions. Alaska still wins the Dawson sector. Do not move WCE or a WCE-only PoC above Alaska.
5. Switch alternatives at the same Alaska fix position. Return to the canonical Alaska r9 after testing if desired.

**Why Alaska:** source ownership was checked by virtual sector path, exact placement UID and fuel-service identities. Alaska overrides this Dawson sector in the supplied stack. The WCE-only diagnostic packages are valid standalone experiments but are not the combined-stack handoff.

**Scope of replacing r9:** this experiment omits the Alaska fix's generated car-rest additions on truck backlots across its payload, including Dawson's distant large backlot. Original source/native rest areas and truck/bus actions remain; WCE r9 and other map fixes retain their own scope. Neither PoC promises compatibility with arbitrary additional whole-sector overrides. Two unsupplied branding/traffic mods mentioned in earlier reports remain outside the inspected source stack.

The fuel baseline is Alaska r2, SHA-256 `7a6360db60912cf77096ee3780501318c38892b375f3723be82bd4377796145f`. The source archive is SHA-256 `d879c245c1bc8b88c9a884d88952ccaad88b58ce759f665832fd0b664a6200fb`. Its original sector is SHA-256 `ddc5fcee53d1ac3e0b15ba48bb4c47da0492f6abefaea47c4209fa3fa019e532`; the effective fuel-baseline sector is `208711d8347456aa687f1c1ac4044bcdcf4e46d1d001730a2ff901c074037a01`. The effective private descriptor is `prefab/rtfix/rtg822b7379.ppd`, SHA-256 `7a61eccd9d614cd7892c68949b0d4ffcc27fd8dc70a0dd4df741273d67bb1855`.

Generation preserves the fuel-only payload, changes only the selected sector's prefab model token and adds a private station descriptor/definition, plus any independently required context resources. Original Alaska fuel-service UIDs `0x65bbc1a5fa0070f5` and `0x65bbc1a7b50070f7`, and their r2 car counterparts `0xe030cede21ed06e5` and `0xaf69c4e64fa9556f`, match the canonical final Alaska r9 from **2026-10-19 00:03:23**. Its archive SHA-256 is `2e0dbce357ffa91664f76c33ef66fd9d040f0513f896107668a19f58113542b7`. Do not substitute the excluded earlier namespace-drift draft.

## Short manual checklist

For each alternative, record the ATS version, enabled PoC filename, source map and load order; keep the remaining setup constant.

- Approach the near-building footprint shown in its plan; for the painted variant choose a free marked bay. Check actual furniture, signs, curb geometry and NPC occupancy.
- Check the car parking/rest map icon and availability of the rest interaction after stopping and switching off the engine. Confirm fatigue recovery rather than relying on the icon alone.
- Check arrival and departure, that the footprint does not require driving through obstacles or blocking pump lanes, and that the near-building placement feels reasonable.
- Confirm passenger-car refueling still works at the same station; detailed quantity/price/billing results remain separate observations.
- Save/reload and revisit to check persistence and NPC occupancy. Check original truck/bus rest and fuel interactions independently when practical.

No gameplay result is claimed by the archive or static checks. The existing r9 two-town icon confirmation remains accepted and does not validate either new PoC.

## Reproduction from owned source files

Run from the retained research worktree. The JSON policies contain relative virtual resource paths, exact UIDs and hashes, not copies of game assets. Original archives are shared read-only from the main checkout; its ignored `local_inputs` is not copied into the worktree.

1. Use the pinned external ConverterPIX revision `3cd4e73a86d0c6bd28e117664c50a36cabeccf38`, Linux binary SHA-256 `fba5a52f763d07d3dc110dea4980fe2c7e656a8c0afa05b6b7a4ab4373dc950d`. [Upstream](https://github.com/mwl4/ConverterPIX), LGPL-3.0. No Blender session is needed.
2. Selectively convert `/prefab/gas/nm_truckstop1_chemron` from the installed `base.scs`, using `-b GAME/base.scs -m /prefab/gas/nm_truckstop1_chemron -e WORK/model`. Keep `WORK` under a fresh Europe/Warsaw timestamp in `local_outputs/work/`.
3. Verify converted PIM SHA-256 `7a9ea5a438a75ecab933f71ec78574ef9ecac3db3f22124d6808e6b15997af74`. The ignored source/binary/conversion artifacts can be recreated from the pinned upstream tool and owned source files.
4. Supply the existing Alaska fuel-only r2 archive with the SHA-256 stated above. If recreating a different baseline, review and re-pin it; the example intentionally refuses a merely similar archive.
5. Run either CLI command with the chosen [painted](../examples/station-parking-dawson-city-alaska-painted-bays.json) or [geometry](../examples/station-parking-dawson-city-alaska-unmarked-geometry.json) config. The generated audit records the exact mounted inputs and external work paths.

Example Bash setup; replace the three external-directory placeholders:

```bash
SOURCE_ROOT=/path/to/main-checkout
ATS_GAME_DIR=/path/to/American-Truck-Simulator
MESH=/path/to/ignored-run/model/prefab/gas/nm_truckstop1_chemron.pim
INPUT="$SOURCE_ROOT/local_inputs"
EXTRACTOR="$SOURCE_ROOT/local_outputs/tools/extractor-2026-07-29/extractor"
FUEL_BASE="$SOURCE_ROOT/local_outputs/generated/2026-10-18_01-27-24/szczerbs-road-trip-gas-stations-fix-alaska-1.61-r2-experimental.scs"
CONFIG=docs/examples/station-parking-dawson-city-alaska-painted-bays.json

station_args=(
  --config "$CONFIG" --mesh "$MESH" --game-dir "$ATS_GAME_DIR"
  --map-package "$INPUT/Alaska_Expansion_v1.2.3.scs"
  --package "$INPUT/Reforma_MegaResources_v3_0_1_161.scs"
  --package "$INPUT/Reforma_3_0_1_161.scs"
  --package "$INPUT/ATS_Expansion_v23.0_1.61.scs"
  --package "$INPUT/Western_Canada_Expansion_v1.7.3.scs"
  --package "$INPUT/promods-ats-models-v164.scs"
  --package "$INPUT/promods-ats-assets-v164.scs"
  --package "$INPUT/promods-ats-map-v164.scs"
  --package "$INPUT/promods-ats-def-v164.scs"
  --package "$INPUT/Reforma_OtherMaps_Patch_40_161.scs"
  --package "$INPUT/Western_Canada_Promods_Connections_v1.7.3.scs"
  --package "$INPUT/Alaska_Expansion_v1.2.3.scs"
  --base-fix "$FUEL_BASE"
)

# Diagnostic audit and plan.svg only; never invokes the mod writer.
PYTHONPATH=src python3 -m ats_road_trip --extractor "$EXTRACTOR" \
  analyze-station-parking "${station_args[@]}"

# Same explicit selection, with experimental package output.
PYTHONPATH=src python3 -m ats_road_trip --extractor "$EXTRACTOR" \
  generate-station-parking "${station_args[@]}" --experimental
```

Select `station-parking-dawson-city-alaska-unmarked-geometry.json` for the other alternative. Each run writes to a new timestamp and refuses to overwrite an existing run. Additional per-placement examples test a different transform of the same model; unsupported variants/composite station arrangements remain blocked rather than receiving guessed geometry.

## Verification records

Implementation: **326 tests pass** with `PYTHONPATH=src python3 -m unittest discover -s tests -q`; source/metadata whitespace checks pass. Both final plan SVGs were rerendered with the completed renderer and visually inspected; they include the full lot, a footprint inset, source paint, candidate numbers and rejection explanations. The tests use original authored fixtures, not distributed game/map assets, and cover deterministic detection, invalid geometry, exact source preservation, context lineage, read-only analysis and blocked generation.

Final Alaska alternatives were generated through the public CLI with the installed official game packages and all eleven supplied map packages in confirmed low-to-high order. Each preserves 22 of 23 fuel-baseline payload resources byte-for-byte; the only changed baseline payload is the Dawson sector. Two alias resources are added. All original sector records and PPD trigger records survive the targeted change. The baseline's two private aliases and the new station alias are unclassified in the effective supplied stack; no context overlay is needed.

Independent comparison of Alaska r2 and canonical final Alaska r9 found identical sets of 18 sector paths, all 114 service-record bytes unchanged (109 kind-7 and five kind-35), and identical `def/country/kalaska.sui` bytes, SHA-256 `ef28c5becf94bf41595d60809da0eab92013c9417a3a640a3b26415a3a80ce83`. This establishes preservation of those fuel-related resources; it does not establish runtime billing or refueling behavior.

| Method | Generated run | Bytes | Archive SHA-256 | New alias |
| --- | --- | ---: | --- | --- |
| `painted_bays` | `2026-10-19_02-02-32` | 572,656 | `c29ed511c66cc14709385106a67af5112f80ac9e6efcd0f6215647dce55bb63f` | `rsp6997042a` |
| `unmarked_geometry` | `2026-10-19_02-04-49` | 598,969 | `2af31469fa7be3ddea7ecee315cac7ad12ea9a7e828059b06e9722e7b6d6f02e` | `rspde780870` |

Each archive is beneath `local_outputs/generated/<run>/` in the retained worktree, named `szczerbs-road-trip-station-parking-alaska-expansion-dawson-city-chemron-<method>-1.61-r0-experimental.scs`. Each public-CLI audit is `local_outputs/work/<run>/dawson-city-chemron/audit.json`. Full-size final plans and PNG previews are under `local_outputs/work/2026-10-19_02-07-21/final-handoff/`, with `<method>.svg` and `<method>.png` filenames. The PNGs are convenience previews; SVGs and JSON retain exact diagnostic data. The PoCs intentionally use the default mod-manager icon rather than reusing fuel-only artwork.

Independent scratch audit source and JSON evidence are retained under `local_outputs/work/2026-10-19_01-56-03/verification/`: `alaska-painted-audit.json`, `alaska-unmarked-audit.json`, `alaska-fuel-records-r2-vs-r9.json`, and `dawson-source-ownership-priority.json`. These local outputs contain source-derived information and are not tracked or published. Archive CRC, native car trigger fields, original bytes, source fingerprints, service IDs, alias targets and context coverage are checked separately from generator success. No static audit establishes runtime success.

## Local test bundle

`local_outputs/generated/2026-10-19_02-11-48/szczerbs-dawson-city-station-parking-poc-alaska-1.61-r0-experimental.zip` contains both alternatives, SVG/PNG plans, pinned configs, generator/independent audits, `SHA256SUMS.txt` and a short English README. It is an ignored local artifact, not a release. Archive CRC, entry set and every stored member byte were checked. Size: 582,379 bytes. SHA-256: `e7aa05c049dda9d133a4339f589395594247e60dbdcfb2ddefa508236dbe2d21`.
