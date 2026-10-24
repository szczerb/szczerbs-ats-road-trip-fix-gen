# Realistic map replacements — ATS 1.61 r10

**Dawson follow-up — 2026-10-24:** the user rejected the single tiny r10 Dawson bay. [A localized Alaska-only r11 replacement](DAWSON_TWO_REVIEWED_PARKING_AREAS_1_61_R11.md) now supplies two user-reviewed broad areas; replace only Alaska r10 and retain the other seven packages. Static checks pass; runtime/user acceptance is pending before wider heuristic changes. Historical r10 artifacts and counts below remain unchanged.

**Observed locally — delivered and statically verified, 2026-10-21:** complete original-stack generation on `codex/gas-station-car-rest-research` produces seven source-relative r9 replacements and a required Base Game and DLC companion. Main remains unchanged. [TASK-0047](../tasks/done/TASK-0047-deliver-realistic-map-replacements.md), [ADR-0024](../architecture/decisions/ADR-0024-compose-complete-realistic-map-replacements.md).

## Local delivery

- [Complete ZIP](../../local_outputs/generated/2026-10-21_22-23-21/realistic-road-trip-complete-map-fixes-1.61-r10-experimental.zip).
- [README, all eight SCS links and exact load order](../../local_outputs/generated/2026-10-21_22-23-21/README.md).
- [Coverage and grouped skip reasons](../../local_outputs/generated/2026-10-21_22-23-21/COVERAGE.md), [machine counts](../../local_outputs/generated/2026-10-21_22-23-21/coverage.json).
- [Eight optional ordinary-career locations with red-ring overviews](../../local_outputs/generated/2026-10-21_22-23-21/UNCERTAINTIES.md).
- [Reproduction configuration and original identities](../../local_outputs/generated/2026-10-21_22-23-21/reproduction.json), [SCS hashes](../../local_outputs/generated/2026-10-21_22-23-21/SHA256SUMS.txt), [ZIP checksum](../../local_outputs/generated/2026-10-21_22-23-21/realistic-road-trip-complete-map-fixes-1.61-r10-experimental.zip.sha256), [final bundle verification](../../local_outputs/work/2026-10-21_20-57-43/realistic-map-replacements/bundle-verification.json).

These ignored local artifacts are available in the retained research worktree, not in Git source history. Other checkouts need verified copies. No publication or installation is performed.

Disable all seven r9 fixes, earlier source-map fuel/rest fixes, and A/B/C/C2/E/F/G site experiments. Enable the complete eight-package set according to its source-relative README order. The stock companion is required, not an optional test. Keep independent N2 above every listed source/replacement (N1 off). Retain North America Background Map 5.3 below the maps, and keep original source/resources and tank/courier packages unchanged. OtherMaps remains price-only. Do not put every replacement together at the top.

## Behavior and evidence

**Documented — accepted user decisions:** public G01 Roswell, G02 Las Cruces truck stop and G06 Artesia receive whole-station additions; G03 Castores logistics, G04 Lufkin ranch/equipment fuel and G05 Roswell truck garage receive none of our additions. Actual archives match five new interactions and four retained native car groups across these controls. The previous G1 visit confirms reported interactions, not fuel chemistry, legal access, numerical billing or save compatibility. [Fuel feedback](SELECTIVE_CAR_FUELING_FEEDBACK_2026_10_21.md).

**Observed locally — presets:** `ProcessorConfig.from_preset('realistic')` selects facility classification, provisional inclusion for unknown fuel facilities, and `station_bays`. `broad` retains broad fueling and the existing local truck-area strategy. Fuel and parking remain independently configurable; rest-only realistic configuration does not run fuel/prices. Existing single-source commands keep their previous defaults. Exactly one generated parking strategy is selected; dedicated-bay failure has no truck-space fallback. Original/native car, truck and bus facilities remain.

Reviewed public descriptor/model/state families include all relevant truck fuel groups. Actual garage FuelPump records support garage exclusion. A pinned Castores distribution model requires its same-parent Company edge. G04's provisional agricultural omission requires an actual Company-to-pinned-field-prefab relationship, exact variant/empty parts and a bounded entrance corridor (depth 0.5–15 m, lateral at most 3 m, height at most 2 m). The measured G04 values are 10.8073 / 1.5174 / 0.1133 m. This is not containment, ownership or diesel-inventory proof. Generic fuel triggers, company names, depot filenames, truck flags and proximity alone are not blacklisted. Unknown families stay provisionally included: 3,044 of 3,073 added fuel points retain explicit uncertainty.

**Observed locally — parking:** original source-owned GAS placements are discovered map-wide; four reviewed converted mesh/model/material/state families gate proposals. Wheelchair-marked bays are eligible; hatching, access/circulation, pump work areas and known obstacles/parked locators are excluded. Output is 120 perpendicular 3 × 6 m bays at a measured curb gap of 0.15 m plus five individual marked 3.354 × 4.988 m bays. Visible stripes still depend on effective visual overrides. Unsupported geometry has no fallback. P04 is skipped while reported unreliable activation remains unresolved. P09 is skipped because its original effective neighborhood has conflicting node geometry; the safe perpendicular preference is reused elsewhere. Broad Mexican activation ownership remains unknown; native polygons stay unchanged. Complete dynamic NPC, independent map-prop collision and vehicle activation behavior remain outside the static model. [Parking feedback](STATION_PARKING_FORECOURT_TOUR_FEEDBACK_2026_10_21.md).

## Actual coverage

| Source | Added car fuel points | Withheld by policy | New bays | Recognized native coverage in reviewed families | Skipped bay placements |
|---|---:|---:|---:|---:|---:|
| Base Game and DLC | 1,007 | 73 | 7 | 11 | 1,149 |
| Reforma | 900 | 54 | 3 | 0 | 1,334 |
| ATS Expansion | 830 | 40 | 1 | 0 | 604 |
| Western Canada Expansion | 189 | 22 | 87 | 0 | 32 |
| ProMods Canada | 65 | 8 | 0 | 0 | 52 |
| Reforma OtherMaps Patch | 0 | 0 | 0 | 0 | 0 |
| Western Canada ProMods Connections | 44 | 6 | 8 | 0 | 25 |
| Alaska Expansion | 38 | 5 | 19 | 0 | 5 |
| **Total** | **3,073** | **208** | **125** | **11** | **3,201** |

The parking census enumerates 3,337 original GAS placements. Native coverage above concerns reviewed families only, not a whole-world native-parking census. Two structurally unmatched stock fuel placements remain unchanged. Twenty-eight effective petrol-price resources are repaired: 19 in OtherMaps, six in Western Canada Expansion, one in Western Canada ProMods Connections and one in Alaska Expansion, and one in the stock companion. Twenty-seven are byte-identical to effective r9 repairs. The new stock `def/country/halloween.sui` (Brackenreach) lacked petrol price; its added value 0.76612433 uses the pinned Washington ratio 1.47197/1.92132 applied to source fuel price 1.0. Original non-petrol bytes remain unchanged. Policy omissions withhold our additions, leaving original interactions intact. Complete replacement packaging does not mean every station receives a new bay.

## Source composition and identity

Generation mounts 25 original game/DLC packages plus 12 original map/resource/visual packages; no r9 or A/B/C/C2/E/F/G overlay supplies gameplay bytes. Staged reads retain original provider ownership. Fuel edits feed parking and final sector bytes ship in the winning source's replacement, including cross-sector composition. Price repairs follow winning country providers. One final additive context file preserves source→fuel→parking classification lineage. Unsafe station transactions roll back; structural global corruption, ambiguous ownership and conflicting identifiers block rather than being hidden as classification uncertainty.

This set is specific to the declared effective stack and installed DLC mounts. Source basenames/versions: Reforma Mega Resources and Reforma 3.0.1.161; ATS Expansion 23.0 / ATS 1.61; Western Canada Expansion 1.7.3; ProMods Canada Models/Assets/Map/Definitions 1.6.4; Reforma OtherMaps Compatibility Patch `Reforma_OtherMaps_Patch_40_161.scs`; Western Canada ProMods Connections 1.7.3; Alaska Expansion 1.2.3. Real Companies visual overrides are declared. Older OtherMaps description text says 39.161; the supplied archive is 40.161. Source/version/DLC/order changes require regeneration; this is not a universal mix-and-match release.

Unchanged source selections preserve historical aliases and service/node identities, including Expansion namespaces. Eighty Reforma `gas_icon.ppd` placements correctly resolve a higher ATS Expansion descriptor in the full original stack, replacing the historical MegaResources descriptor; private alias changes there reflect changed source bytes rather than identical-source renaming. The finished receipt records both hashes and identity comparisons. One historical r9 parent borrowed from stock by ATS Expansion is a garage now excluded, not a surviving public facility. Static identity preservation does not guarantee existing-save compatibility.

N2 is byte-identical and remains independent. It must load above all listed sources/replacements: OtherMaps also supplies `def/map_data.sii` and otherwise shadows N2. The final archive audit verifies N2 as the effective map-data winner; a subsequent [N2 r3 presentation handoff](NAVIGATION_ICONS_METADATA_1_61_R3.md) preserves that same gameplay member while updating metadata/artwork. The historical ZIP above retains its original N2 archive. Background, tank and courier packages are unchanged. [Navigation evidence](CAR_PARKING_NAVIGATION_ICONS.md), [source order](CONNECTOR_FUEL_FIXES.md).

## Reproduction and verification

Use `analyze-map-stack` or `generate-map-stack` with explicit repeated `--package` arguments LOW→HIGH for original map/resource packages; installed game packages are resolved separately. `--preset realistic` is the new stack-command default; `--preset broad` is explicit legacy behavior. Generation requires `--experimental`, defaults to revision 10 and refuses an existing timestamped run. `--game-dir`, global `--extractor` and `--run-id` are available. Analysis never calls the mod writer. The handoff includes `reproduce.py` and exact configuration. Retained reviewed converted PIM/PIT evidence is a generation input, not a runtime dependency. Original supplied inputs remain read-only.

**Observed locally — 508 regression tests pass:** revised six-site/reusable classification, uncertainty and unsafe counterexamples; independent presets and exclusive parking; no candidate without fallback; legacy broad byte equivalence; source ownership and boundary composition; fuel→parking contexts; native preservation; archive cache reuse and CLI boundaries.

**Observed locally — independent actual finished-archive checks pass:** eight SCS CRCs, metadata, hashes/inventories and complete declared load order; 791 composed sectors and 3,073 exact service/node additions; generated private resources and source contexts; effective prices and surviving historical identities. The parking audit verifies 125 four-record car-only PPD additions, unchanged original trigger sections (including 202 fuel private PPDs), and 7,708 original standalone triggers across 656 changed sectors. No generated standalone truck-area car access is present. [Fuel/stack receipt](../../local_outputs/generated/2026-10-21_22-23-21/receipts/fuel-stack-audit.json), [parking receipt](../../local_outputs/generated/2026-10-21_22-23-21/receipts/parking-archive-audit.json), [metadata-only byte identity](../../local_outputs/generated/2026-10-21_22-23-21/receipts/metadata-finalization.json), [tests](../../local_outputs/generated/2026-10-21_22-23-21/receipts/508-tests.log). The generated-UID scan parsed all 3,480 winning original `.base`/`.aux` resources with no omissions or collisions. It also verifies 2,066 surviving effective r9 service/node identities and 1,132 unchanged-source private-alias placements. This is an actual identifier scan, not an inferred proof from metadata resolution.

**Unknown — runtime boundary:** full r10 behavior in an existing career, fatigue recovery, numerical billing, collision-free access and all markers. No new test-profile tour, route, pump matrix, screenshots or game sessions are required before delivery. The user installs and reports issues opportunistically during normal play. Agents did not install, launch the game, reset state or modify profiles; main remains unchanged, and no merge, push or publication occurred.
