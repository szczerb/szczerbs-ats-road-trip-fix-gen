# R9 passenger-car parking markers: local handoff

Inspected and prepared: 18–19 October 2026. Baseline **ATS 1.61.3.18**, Steam build **25952361**, Road Trip Ford and the installed map DLCs. This is a local experimental handoff, with no publication, game launch, installation or profile edit.

**Subsequent user validation, 2026-10-19:** the maintainer confirms parking icons in Alaska and Canada after checking two towns, and reports denser map coverage. [Dated evidence and limits](VALIDATION_RESULTS.md#2026-10-19-r9-parking-icons-confirmed-in-alaska-and-canada). The tested archives below remain unchanged; their embedded runtime status records generation time.

## Package set and replacement

Seven map/connector `.scs` files are supplied in the local ZIP below. **Replace the seven r8 map fixes one-for-one, disabling older copies.** Keep every fix directly above its own source; preserve the existing source order. The separate **Job Types Compat Mustang r3** and **reasonable tank upgrades r0** remain unchanged and are not in this ZIP.

Final ZIP: `local_outputs/generated/2026-10-19_00-03-23/szczerbs-road-trip-map-test-batch-ats-1.61-r9-experimental.zip` (ignored local artifact).

Size: **68,664,125 bytes**. SHA-256: `e1eef95f5ed30cc43c5896c44af1fd8de368aad7b60ef2895cfd9fcb8432142f`. The ZIP contains exactly seven mods, `README_INSTALL.txt` and `SHA256SUMS.txt`.

All map filenames follow `szczerbs-road-trip-map-fix-<slug>-1.61-r9-experimental.scs`. Exact source versions remain those in [README](../../README.md#game-and-map-versions-checked); the full Expansion names identify only those supplied sources.

| Source | Slug | Car-only rest groups/items | SHA-256 |
| --- | --- | ---: | --- |
| Alaska Expansion | `alaska-expansion` | 31 | `2e0dbce357ffa91664f76c33ef66fd9d040f0513f896107668a19f58113542b7` |
| ATS Expansion | `ats-expansion` | 766 | `c08a21fe0e0c7b0d361dbf16dd6c52c2dfcada440bb5efc240b9872e3aa76248` |
| ProMods Canada | `promods-canada` | 95 | `ce0033ffcc77cbe68c0f8e22e7cc866d7b73a5559df89b15d34e9cc325444d0a` |
| Reforma | `reforma` | 119 | `c7a0f03b941b851829c81ac368b1bac9c25dff8b90f4557b4cd0946b8528e983` |
| Reforma OtherMaps Patch | `reforma-othermaps-patch` | 0 | `af7b1fb53c230c1686aa95eba0f8c4d9644846db665bfe8462df6bd00757bbde` |
| Western Canada Expansion | `western-canada-expansion` | 202 | `0ca6bd7e7b6696d9b617a69427f3ad918bf1a8d874d8a51aafc27b575314e907` |
| Western Canada ProMods Connections | `western-canada-promods-connections` | 41 | `a5ca10c041c50a747d34479151e6083a49a1aec29b480da8186cdeae612ef603` |

The 1,254 additions are per-package counts, not unique map icons. They comprise 357 prefab groups and 897 standalone Trigger items. Current sources require no additional repairs of already mixed car-enabled locations; that case is covered by regression tests.

OtherMaps remains price-only. It has no station/rest sectors; its r9 gameplay resources are unchanged from r8. Reforma also gets the repair at its generated rest locations: dense native Mexican icons did not validate the earlier generated additions.

The confirmed supplied order, highest first, is:

1. Alaska Expansion fix, then Alaska Expansion 1.2.3.
2. Western Canada ProMods Connections fix, then its 1.7.3 source.
3. Reforma OtherMaps fix, then OtherMaps 40.161.
4. ProMods Canada Definitions 1.6.4; ProMods fix directly above its Map 1.6.4; then Assets and Models 1.6.4.
5. Western Canada Expansion fix, then Western Canada Expansion 1.7.3.
6. ATS Expansion fix, then ATS Expansion 23.0.
7. Reforma fix, then Reforma 3.0.1.161; Mega Resources 3.0.1.161 below it.

Keep unrelated mods in their established positions. This preserves the [confirmed source-relative order](CONNECTOR_FUEL_FIXES.md#screenshot-confirmed-order); the verification scope is the supplied map stack and inspected resource paths, not every possible third-party semantic override. The connector's Mod Manager artwork/cache issue remains a separate [open runtime check](../incidents/INC-0001-connector-icon-cache/README.md).

## Cause and repair

**Observed locally — independently repeated executable inspection:** ATS's prefab and standalone parking-marker builders test truck/bus before car. R8's single mixed truck/bus/car action selects the large-vehicle marker category, preventing a separate car marker. R7 has the same gameplay bytes, so this defect predates the r8 branding change. Physical car activation is a separate mechanism and was not disproved by the absent icons. [Exact executable identity, branches and placed comparisons](CAR_PARKING_ICON_INVESTIGATION.md).

R9 appends independent native `parking_car` trigger groups to selected placement-local descriptors and independent car-only standalone Trigger items/nodes. Original truck/bus actions and trigger geometry remain intact. New groups remap internal neighbors; standalone twins retain exact geometry, flags, radius, tags and visibility/layer membership without duplicating unrelated actions. No guessed fuel flag or obsolete Parking overlay is used. [ADR-0017](../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md).

The inclusive **1,000-unit straight-line XZ** rule and immutable original physical-car inventory remain unchanged for new permissions. Separate reporting covers repair of an already car-enabled mixed location without expanding eligibility. Current source runs select the same locations as r8. Known irregular shapes are cloned exactly with the existing conservative proximity policy. Bounded source/halo inspection can miss a car neighbor outside its perimeter, producing the user-accepted extra permissions. This is not stock-map-wide coverage; sparse stock Montana sectors outside a source's scope are not automatically repaired.

**Observed locally — delivery audit correction:** fresh generation initially changed fuel IDs in the two renamed Expansion maps because public display names were used as hash seeds. Those drafts remain preserved but are excluded from this handoff. Commit `f561751` restores the historical Alaska/Western Canada fuel namespace while retaining public Expansion labels. The final audit requires every r8 fuel service/node and private fuel alias/descriptor to survive, rather than checking only common IDs.

## Verification and limits

**Observed locally — 2026-10-19:** all **281 tests pass** with `PYTHONPATH=src python3 -m unittest discover -s tests -q`. Tests cover separate marker groups, exact original records, geometry/topology, mixed-mode proximity, immutable neighbors, native/custom actions, irregular and spherical areas, reciprocal nodes, UID conflicts, visibility ownership, malformed layers and fuel/rest layer composition. The renamed-source regression compares complete fuel resource dictionaries, not just counters.

GPT-6 Sol/high independently reviewed the marker mechanism and production code, then verified all seven final archive hashes. Its output audit checks 342 source descriptors, all 2,156 original PPD trigger records, 2,249 original standalone Trigger records and 401,634 original source nodes, plus exact geometry/actions for the 357 new car groups and 897 standalone twins. All 7,264 per-package r8 service records and linked nodes and all 162 private fuel descriptor/definition pairs retain their identities and bytes. Rest selections match r8 under the same inclusive radius. ZIP CRC, inventory/resource hashes, manifest, descriptions and icons pass. These are inspection counts with possible overlap between packages, not unique world locations.

Root's additional checks pass:

- **Effective stack:** 583 changed sector paths; all 2,202 surviving generated truck fuel targets retain co-located car counterparts, and all 3,518 car services have reciprocal links. There are 306 surviving prefab car-only groups and 846 standalone car-only items with node/layer/visibility checks. Higher-priority sources supersede 51 prefab groups and 51 standalone items, explaining the difference from the per-package total. Four unrelated stock truck points without car twins were not generation targets and remain unchanged, as in the earlier batch.
- **Namespaces and courier contexts:** no conflicting generated paths or additive units across 1,041 definition/descriptor paths and 550 units. All 46 context units retain their classifications. WCE's 380 Company records are byte-identical and all 14 classified Company-parent aliases retain their mappings.
- **Layers:** the independent ZIP-source review checks 392 selected sector-layer paths. Root additionally reads all 66 relevant Reforma HashFS source layer files and checks all 88 standalone twins against them; none of those original items has explicit layer membership. Fixture tests exercise actual nondefault layer writes and visibility cloning, which these particular source placements do not require.
- **Preservation:** country resource paths/bytes match r8, including all 27 effective country paths; the OtherMaps gameplay dictionary and all seven packaged icons are unchanged. All 44 recorded game/source stat identities still match, and all seven original r8 archive hashes are unchanged. No job or tank resource is added.
- **Delivery:** the outer ZIP CRC, exact nine-member inventory and every contained mod's SHA-256 match the independently audited final selection. The five unchanged candidates are copied exactly; corrected Alaska/WCE candidates replace only the rejected drafts in the final selection.

Evidence: `local_outputs/work/2026-10-19_00-03-23/` contains the final selection/ZIP receipt, 281-test log, `verify_composed_graph.json`, `verify_definition_collisions.json`, `verify_wce_companies.json`, `verify_preservation.json` and `verify_reforma_layers.json`. Independent read-only verifier and final/rejected receipts are in `local_outputs/work/2026-10-18_23-37-00/mechanism/`; source comparisons are in `local_outputs/work/2026-10-18_23-37-37/parking-inventory/`. First batch command/audit records remain in `local_outputs/work/2026-10-18_23-48-10/`.

Production commits are `42b6e9b` (native car-only rest twins) and `f561751` (historical fuel namespace). Full command records, embedded reports, independent byte checks, effective-stack and namespace results, source stat identities, hashes and ZIP checks are retained in ignored timestamped work directories. Original r8, preliminary r9 and rejected namespace-drift drafts remain in their original locations.

**Documented — user gameplay report:** icons work at the reported two-town Alaska/Canada scope. Actual rest prompt/fatigue recovery, tag/script behavior and truck/bus/reload steps were not individually enumerated. Static classification, exact-byte preservation and valid graphs provide the basis for this experiment; they are not a gameplay acceptance result.

## Additional checks after the two-town confirmation

The initial Alaska/Canada icon check is user-confirmed; do not request it again as a missing result. For broader coverage or individual controls when convenient, use a copied profile and the exact delivered filenames. In car map mode, inspect Canada, Alaska and map-mod-covered Montana. At one selected formerly missing location, check the icon, then the actual rest prompt with engine off and successful fatigue recovery. Check an original truck rest control and repeat icon/access checks after reload. Record location, mode, package versions and result; keep a fresh log if something fails. These are separate observations. No interruption of the current Mexico job is requested.

Canada/Mexico refueling access remains user-confirmed; numerical prices/billing and courier delivery retain their separate status. The broader runtime task [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) stays open. [TASK-0038](../tasks/done/TASK-0038-investigate-missing-car-parking-icons.md) covers the completed local implementation/handoff, not a new in-game success report.
