# Connector-aware fuel fixes

Inspection date: 2026-10-17. Applies to the eleven supplied archives and ATS 1.61.3.18. [TASK-0012](../tasks/done/TASK-0012-inspect-and-fix-map-connectors.md) records the work; the [input inventory](LOCAL_INPUT_INVENTORY.md#current-connector-additions-eleven-archives-total) preserves exact source metadata. Static observations do not establish gameplay behavior.

Subsequent update, 2026-10-18: the [r2 price increment](FUEL_FIX_BATCH_1_61_R2.md) retains the station resources documented here and adds missing petrol fields. OtherMaps now has a **price-only** fix; the statement below that it needs no station-interaction fix remains true. Commands without an explicit revision now use r2, not the historical r1 artifact. [Manual price/billing tests](MANUAL_TEST_CHECKLIST.md) are still pending.

## What the original overlap check established

**Observed locally:** the five original r1 fixes share changed-sector paths in three pairs: ATS Expansion–Western Canada (6), Alaska–Western Canada (3), and ProMods Canada–Western Canada (15). This was an exact intersection of output file paths. It did not compare road geometry, merge maps, establish defects, or include the two then-unprovided connectors. See the [original batch](FUEL_FIX_BATCH_1_61_R1.md).

The user's proposed installation rule is appropriate for these whole-sector overrides: keep each fix directly above its own source, retaining the source mods' relative priority. The higher source and its fix still win. A higher source that replaces an entire sector also supersedes the lower fix's additions there; a connector-specific fix must derive from that higher sector version rather than resurrect a lower map's version.

Generation additionally needs the effective prefab definitions/descriptors from other packages. Some fuel parents and nodes cross sector boundaries. This is why source-relative installation does not eliminate the need to identify the data stack used during generation. Neighbor edits must be checked explicitly for retained coverage and links.

## Screenshot-confirmed order

**Documented — supplied screenshots inspected through WSL, 2026-10-17:** `Zrzut ekranu 2026-10-17 230330.png` and `230340.png` show the following high-to-low supplied map order:

1. Alaska Expansion 1.2.3.
2. Western Canada ProMods Connections 1.7.3.
3. Reforma OtherMaps Compatibility Patch 40.161.
4. ProMods Canada Definitions 1.6.4.
5. ProMods Canada Map 1.6.4.
6. ProMods Canada Assets 1.6.4.
7. ProMods Canada Models 1.6.4.
8. Western Canada Expansion 1.7.3.
9. ATS Expansion 23.0.
10. Reforma 3.0.1.161.
11. Reforma Mega Resources 3.0.1.161.

Real Companies, Gas Stations & Billboards and a partly visible traffic-density mod appear above this order. Their archives were not supplied. **Unknown:** their actual resource overrides. A texture-only change would not replace interaction records, but a screenshot or branding-oriented title does not prove the archive's scope. No additional source was silently read from the live mod directory.

The first five-map generation used independent per-source stacks; in particular Western Canada's inferred stack put it above ProMods. The screenshots show the opposite map priority. Whole-sector source-relative installation still follows the screenshots, but connector generation now explicitly uses the confirmed low-to-high dependencies. CLI dependency arguments retain their caller-supplied order; family defaults must not reject a different explicit order.

## Reforma OtherMaps: no additional station fix

**Observed locally:** the supplied 40.161 patch contains no sectors, prefab definitions, PPDs, or fuel-service asset references. Its 367 definitions concern cities, countries, map/sign metadata and a road look; 19 country files contain `fuel_price`. Those price settings do not conflict with the station-interaction resources in the five r1 fixes. Description text still says 39.161; the manifest identifies 40.161.

The deterministic command completed with zero source fuel targets and no output. Its generic `already_covered` status means there is nothing for this sector-scoped generator to change in this archive; it is not a claim that every station in every map named by the patch has been verified. No empty Reforma OtherMaps fuel mod is needed for these inspected contents. The existing Reforma map fuel fix stays directly above the Reforma map.

## Western Canada–ProMods connection

**Observed locally:** version 1.7.3 contains 26 sector stems (52 `.base`/`.aux` files). All parse structurally. Fourteen `.base` files contain 56 fuel candidate records (six FuelPump kind 35, fifty fuel Service kind 7). Those fourteen paths intersect Western Canada's r1 fix; six also intersect ProMods' r1 fix and one ATS Expansion's r1 fix. Alaska's source sectors do not intersect the connector's sectors.

The source archive itself requires Western Canada 1.7.3, ProMods 1.6.4, ATS 1.61 and all map DLC. The original other-map fix records overridden at these paths are not additional unique surviving stations; do not add their counters together to estimate combined coverage.

The generated **1.61-r1-experimental** connection fix adds **50** missing co-located car interactions, including **six garage points**, across **31 changed fuel prefab instances**. The other candidate records include existing car-only interactions. It changes **14 `.base` files**, all from the connector itself; it does not replace any extra neighbor sector. Original truck interactions and the connector's nonfuel changes are retained.

Output: `local_outputs/generated/2026-10-17_23-08-21/szczerbs-road-trip-gas-stations-fix-western-canada-promods-connections-1.61-r1-experimental.scs`, **2,661,218 bytes**, SHA-256 `3142a6ace997b5102200fc975fead2f34215d2d5a4fcc510380f4a3169de4cbd`. Author/title/version follow the metadata contract; the icon reuses the selected Western Canada C artwork. Place this fix **directly above Western Canada ProMods Connections**, below Alaska and its own fix, retaining the screenshot order. Keep the five existing map fixes directly above their source maps; the ProMods fix belongs above its map package and below its definitions package. No fuel fix is added above OtherMaps or resource-only packages.

**Observed locally — independent verification:** ZIP CRC, metadata/icon and all resource hashes pass. All 50 added services/nodes have exact truck-node transforms and reciprocal links. All 7,447 original items remain in order; 11,307 original node records and all 67 kind-7 / six kind-35 records are byte-identical. Other records are unchanged except verified prefab alias/slave additions and visibility references. The 14 private definitions and 14 private PPDs have no resource-path collisions with the old five fixes. Full independent script/JSON: `local_outputs/work/2026-10-17_23-08-21/verification/`.

Composition checks for the supplied screenshot order are recorded in `local_outputs/work/2026-10-17_23-08-21/verify_composed_graph.json`: **all 2,202 surviving generated truck targets have exact-transform car counterparts**, and all **3,514 car services** in the winning fix sectors have reciprocal parent/node links. The latter count includes existing car services, not just generated additions. The scope is generated targets and surviving car links in the 527 sector paths changed by the six fixes, not every stock station or unrelated map asset. An expanded diagnostic also identified four unrelated stock truck points in a copied stock neighbor sector (`map/usa/sec+0007+0002.base`); these were never generation targets and are preserved. An independent review compared all four original service/node byte records with the pre-existing stock cache and confirmed that their absence of co-located twins predates generation. They must not be relabeled as lost generated counterparts. The raw expanded diagnostic is retained separately.

All **116 tests pass**. Static coverage does not prove actual purchases, physical access, garage ownership/price behavior, or reloads. These remain [gameplay validation](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). Inputs, sidecars and game/profile files are unchanged. Work/output artifacts remain in timestamped ignored directories. The first minimal-stack run was interrupted at the user's pause request; the final output uses the subsequent screenshot-derived stack.

## Reproduction

The compact source command infers the connector's required Western Canada and ProMods siblings:

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/Western_Canada_Promods_Connections_v1.7.3.scs --experimental
```

For the screenshot stack, supply the additional packages and the exact low-to-high sequence explicitly:

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel \
  local_inputs/Western_Canada_Promods_Connections_v1.7.3.scs --experimental \
  --dependency local_inputs/Reforma_MegaResources_v3_0_1_161.scs \
  --dependency local_inputs/Reforma_3_0_1_161.scs \
  --dependency local_inputs/ATS_Expansion_v23.0_1.61.scs \
  --dependency local_inputs/Western_Canada_Expansion_v1.7.3.scs \
  --dependency local_inputs/promods-ats-models-v164.scs \
  --dependency local_inputs/promods-ats-assets-v164.scs \
  --dependency local_inputs/promods-ats-map-v164.scs \
  --dependency local_inputs/promods-ats-def-v164.scs \
  --dependency local_inputs/Reforma_OtherMaps_Patch_40_161.scs
```

The connector is the highest source in this generation scope. Alaska has higher live priority and zero exact source-sector intersection with it; final composition checks must still consider Alaska's fix. Unsupplied branding/traffic mods remain outside the verified scope. This generator does not infer a full profile from a screenshot or silently reorder the user's maps.
