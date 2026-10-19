# F BATCH r1 — Curated Forecourt Tour, ATS 1.61

Research date: 2026-10-19. [TASK-0045](../tasks/done/TASK-0045-build-curated-station-parking-test-batch.md), [ADR-0021](../architecture/decisions/ADR-0021-compose-explicit-station-parking-batches.md). **Delivered:** one combined SCS with **nine newly served locations / three geometric families**, plus one unchanged native control. All final archive and bundle checks pass; gameplay validation remains for the user.

## Effective inventory

**Observed locally — ATS 1.61.3.18, 2026-10-19:** structurally parsed **1,739** effective `map/usa` base sectors without parse errors. The declared **44-package** stack contains installed base/game/DLC resources, eleven supplied map/resource archives, seven source-relative r9 fixes and Real Companies 4.02.01. This is a declared research stack, not an assertion that every other mod in a live profile is supported.

The scoped census found **2,954** placements, **104 visual model paths**, **402 model + variant + additional-parts states**, and **342 winning PPDs**. **2,882** placements have complete inspected same-parent GAS/service graphs; **72** remain unverified or potentially composite. A model or descriptor path containing `/gas/` and actual GAS spawns defines this census scope. Custom station models with other paths and cross-sector/composite services may be missed. Missing services in one prefab do not prove that a whole visual station is inactive; no inactive station is activated here.

A separate descriptor pass verified all 342 hashes and decoded exact action tokens, producing **366 descriptor/action/native-car/service groups**, with no unresolved descriptor or parse errors. Existing `parking_car` groups include r9 additions as well as stock/source groups; they are not all original map-authored parking. Model paths, descriptors and action sets remain separate identities. Painted/unmarked labels apply only to inspected effective model states, not inferred names across all 104 paths.

Local evidence: [effective census](../../local_outputs/work/2026-10-19_22-55-37/effective-station-inventory/inventory.json), [state grouping](../../local_outputs/work/2026-10-19_23-10-30/station-census-summary/grouped-inventory.json), [exact actions](../../local_outputs/work/2026-10-19_23-21-30/action-census/descriptor-action-groups.json), [city anchors](../../local_outputs/work/2026-10-19_23-10-30/station-census-summary/city-anchor-resolution.json). These ignored assets/scripts are retained in the research worktree; small authored summaries/configs are tracked.

## Selection and generalization

The curated manifest selects nine operational placements from three different effective layouts: four `nm_gas_station1_chemron` painted examples, four `nm_truckstop1_chemron` unmarked examples including Dawson continuity, and one `nm_gas_station2-corner_chemron` unmarked corner example. Repeated placements test transforms/local context; neither Dawson repetition nor brand changes are counted as an extra geometry family.

**Observed locally:** an NPC locator obstructs part of the painted two-bay bank. Schema 2 now evaluates each already measured free-gap bay alongside its whole accepted bank. It retains the >=3-separator parent evidence, exact two boundary references, all occupancy/access/model exclusions and native flags 0/range 3. It does not infer a parking place from two isolated lines or hardcoded station coordinates. The proposal count is bounded to 128 and fails closed on excess. Legacy default/schema-1 output remains exact.

Footprints and approaches are evaluated separately from shared model geometry. A 3×3 base/aux halo and 100-unit prefab-anchor radius supply recognized external PPD UI polygon proxies (supported colours 2/4). Both approach ends are checked before selection; external margins participate in ranking. Duplicate node metadata is reported, with placement-local owner-linked nodes preferred and only unique owner-linked remote poses accepted.

**Unknown:** render surfaces, UI polygons and material aliases do not provide full physics or driving paths. Other props, generic map-item bounds, omitted furniture, runtime NPC occupancy, pedestrian routes, terrain and large prefabs whose anchors lie outside the radius remain unresolved. Per-site reports disclose these limits and actual rejection/ranking evidence. No full building-front strip is forced and no 1,000-unit/density policy is added.

Rejected research cases remain explicit: the GP corner's raised mesh has nonmanifold welded edges; one ATS Chemron corner has unmatched additional parts; Gallonoil's decal-like surface has no verified continuous driving ground. These gates were not relaxed to fill a quota.

## Download and setup

- [One test ZIP: F BATCH r1 Forecourt Tour](../../local_outputs/generated/2026-10-19_23-19-21/f-batch-r1-forecourt-tour-test-bundle-ats-1.61.zip). It contains one SCS, instructions/result table, 18 before/after SVGs and PNG/details, all-site overview, portable manifest/configs and paired converted inputs, inventory/action evidence, audits and checksums.
- [SCS alone](../../local_outputs/generated/2026-10-19_23-19-21/f-batch-r1-forecourt-tour-ats-1.61-experimental.scs). Display name and first description line start **F BATCH r1**; the filename puts `r1` early.
- [Instructions, visiting order and result table](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/README.md), [all nine plan details](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/plans/all-nine-after.png), [project manifest](../examples/station-parking-forecourt-tour/manifest.json), [per-site world/heading data](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/sites.json).

Keep all standard r9 map fixes enabled at their source-relative positions, **including Alaska r9**. Enable F BATCH above the declared maps/fixes, with Real Companies held constant; disable old A/B/C/C2/E station experiments. Retain independent N2 above the active background/map-data providers and keep the background enabled. Other job/tank mods stay at their existing positions. All nine sites are tested together; do not switch geometry packages per station or replace Alaska r9 with fuel-only r2.

The suggested visit sequence is **P05 → P08 → P06 → P07 → P01 → P09 → P02 → P03 → P04**. This groups regions, not a proven continuous road route. Find the marked location, approach from pale blue, follow the white suggested nose arrow and record natural pose/prompt/visible conflicts. Completed rest/fatigue, original fuel/truck controls and reload are optional separate observations. The action polygon is not a predicted vehicle-centre envelope; no engine heading requirement is asserted.

| Site | Nearest verified city anchor | Family / method | Sector | Placement UID | Private PPD alias |
|---|---|---|---|---|---|
| P01 | Roswell / New Mexico | painted Chemron1 / `painted_bays` | `map/usa/sec-0010+0007.base` | `0x70b9ed1f7920001` | `rsp4c418153` |
| P02 | Parral / Chihuahua — A | painted Chemron1 / `painted_bays` | `map/usa/sec-0013+0016.base` | `0x2a0836f837400001` | `rsp056bcc89` |
| P03 | Parral / Chihuahua — B | painted Chemron1 / `painted_bays` | `map/usa/sec-0013+0016.base` | `0x2a21695c01800001` | `rsp144aa753` |
| P04 | Mazatlán / Sinaloa | painted Chemron1 / `painted_bays` | `map/usa/sec-0014+0021.base` | `0x89e8c438a900001` | `rspa0e8f9ab` |
| P05 | Dawson City / Yukon | unmarked truckstop Chemron1 / `unmarked_geometry` | `map/usa/sec-0029-0045.base` | `0x5ca1fea582800001` | `rspe40447b8` |
| P06 | Powerview / Manitoba | unmarked truckstop Chemron1 / `unmarked_geometry` | `map/usa/sec-0001-0017.base` | `0x5bd0cba014000001` | `rsp4314fea0` |
| P07 | Gimli / Manitoba | unmarked truckstop Chemron1 / `unmarked_geometry` | `map/usa/sec-0001-0017.base` | `0x5bd0d13bae800000` | `rsp20a51d75` |
| P08 | Bissett / Manitoba | unmarked truckstop Chemron1 / `unmarked_geometry` | `map/usa/sec+0000-0018.base` | `0x5bd0c12d09800001` | `rspf15245c1` |
| P09 | Las Cruces / New Mexico | unmarked corner Chemron2 / `unmarked_geometry` | `map/usa/sec-0013+0008.base` | `0x67e8111ee360001` | `rsp245349fe` |

All selected states use variant `default` with no additional parts. City labels resolve nearby Company tokens through exact city_data units; they do not assert station-city membership. Sector, UID and target coordinates are authoritative identifiers for this handoff.

| Site | Parking centroid X, Y, Z | Physical/activation dimensions | Source map | Local-plan suggested nose |
|---|---|---|---|---|
| P01 | `-39560.83, 56.07, 29350.91` | 3.35 × 4.99 m | ATS Expansion | up, toward the boundary |
| P02 | `-49713.60, 42.61, 66416.21` | 3.35 × 4.99 m | Reforma | up, toward the boundary |
| P03 | `-49998.67, 48.69, 66600.28` | 3.35 × 4.99 m | Reforma | up, toward the boundary |
| P04 | `-54167.84, 1.38, 87869.50` | 3.35 × 4.99 m | Reforma | up, toward the boundary |
| P05 | `-114902.22, 44.21, -177641.41` | 3.00 × 6.00 m | Alaska Expansion | up, toward the boundary |
| P06 | `-468.66, 44.20, -65383.19` | 3.00 × 6.00 m | Western Canada Expansion | up, toward the boundary |
| P07 | `-3494.02, 43.84, -66147.46` | 3.00 × 6.00 m | Western Canada Expansion | up, toward the boundary |
| P08 | `643.01, 44.16, -68309.16` | 3.00 × 6.00 m | Western Canada Expansion | up, toward the boundary |
| P09 | `-51719.34, 60.10, 34214.89` | 3.00 × 6.00 m | Reforma | left, along the boundary |

The plans use local model orientation, not north-up world orientation. P05 preserves the backlot and adds the front proposal. P01–P04 choose the free measured bay beside an NPC-obstructed bank; P09 uses a parallel layout. Recognized external proxies are present in actual P04/P07/P08 neighborhoods; every site retains explicit unassessed-object counts.

The SCS is **11,987,264 bytes**, SHA-256 `60628f27dba5d42df4628a040d32dc915b4a0f7ab615e8147c8b167866e4af19`. The ZIP is **10,063,770 bytes**, SHA-256 `03785abe290b49932f0cacbb3afd8d04130b1b7f61bacf900452330c3219ec27`. All **111** ZIP members pass CRC; **110** recorded member hashes match, including the unchanged SCS. Portable paired-model pins and README links validate. [Bundle audit](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle-audit.json).

## Native control and previous experiments

One unchanged native painted control is UID `0x6032dc12c1350001`, sector `map/usa/sec-0010+0008.base`. Its complete painted bank is inside original native car coverage; the new single bays are subsets. It is excluded from the generation manifest and does not count among the nine changed stations. [Continuity receipt](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/native-control-continuity.json).

C2 and E remain untested historical geometry/activation comparisons with immutable archives/configs. This batch keeps native flags 0/range 3 and does not enable E's partial flag. N2's parking/fuel navigation visibility is user-confirmed at the previously reported scope; it remains independent, with TASK-0043 metadata/artwork deferred. The [earlier handoff](STATION_PARKING_HEURISTICS_HANDOFF_1_61.md) records original C2/E instructions; F BATCH instead retains all standard r9 fixes.

The retained overhead and ground-level screenshots remain project-local, unchanged and hash-rechecked against their evidence manifests. See [feedback/image links](GAS_STATION_CAR_REST_FEEDBACK_2026_10_19.md#2026-10-19-ground-level-forecourt-clearance-view). They support visual interpretation, not calibrated coordinates.

## Verification and delivery

**Observed locally — final public CLI and independent archive audit:** all nine sites survive the actual SCS in seven sectors. P02/P03 and P06/P07 retain both edits in their shared sectors; reverse-order composition is identical. Every byte outside the nine selected eight-byte model-token ranges remains exact. All **66 existing services**, **4,494 nodes** and **3,283 item identities/extents** are preserved. Each private PPD adds one four-vertex native car polygon while preserving source sections and original triggers. All nine actual source aliases are unclassified; no additive context is emitted or positive courier classification claimed. Classified-context preservation is separately covered by authored fixtures.

The full generator used the declared 44-package stack and rechecked input identities. The independent audit reopened 14 declared providers for selected dependencies/context/native control; it does not claim a second whole-world scan. N2 remains byte-identical and gameplay-resource-disjoint. The unchanged native control retains three source rest groups and both derived bays already covered. Root adds **59** archive/metadata/identity/main-checkout checks.

[Public generation audit](../../local_outputs/work/2026-10-19_23-19-21/forecourt-tour/audit.json), [independent nine-site audit](../../local_outputs/work/2026-10-19_23-12-19/independent-final-batch-audit/audit-result.json), [root archive audit](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/root-archive-audit.json), [visual review](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/visual-review.json). **418 authored tests pass**, including same-sector multi-source composition, private alias/context/source preservation, drift/conflicts/atomic generation, external transforms/alternate approaches, native coverage and NPC-obstructed bank/free-neighbor selection. Complete actual legacy A/B reports, resource hashes and SVGs remain exact: [final equality receipt](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/legacy-final-equality.json).

All work remains on `codex/gas-station-car-rest-research` in `.`. Code milestones: `9bc6c47`, `c52b675`, `056ae96`. No game, installation, profile, economy reset, merge, push or publication was performed. Physical usability, activation tolerance, completed rest, fatigue and reload await the user's later tests.
