# Map-wide gas station fix generation

Updated: 2026-10-17. Applies to installed ATS 1.61.3.18 and the eleven current input archives. **Observed locally:** automated structural audits and generated packages. **Documented — user report:** only the original single-point Helena pair has actual car/truck refueling evidence. Broader gameplay remains unverified.

## Run one command

From the repository root:

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/ATS_Expansion_v23.0_1.61.scs --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/Reforma_3_0_1_161.scs --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/promods-ats-map-v164.scs --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/Western_Canada_Expansion_v1.7.3.scs --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/Alaska_Expansion_v1.2.3.scs --experimental
PYTHONPATH=src python3 -m ats_road_trip generate-map-fuel local_inputs/Western_Canada_Promods_Connections_v1.7.3.scs --experimental
```

Each invocation discovers targets and builds its fix with Python and the external HashFS extractor. It needs no per-station recipe or language-model call. Known sibling companions are selected automatically. The game path comes from `--game-dir`, `ATS_GAME_DIR`, or the detected Windows Steam installation. Source-map contents remain read-only.

Optional arguments: `--map-name`, `--revision` (default `1` for this first full-map increment), `--run-id YYYY-MM-DD_HH-MM-SS`, repeated `--dependency` (low-to-high additional resources), and `--icon`. Known map/connector names and map-labelled C icons are automatic. Connectors reuse their parent map's selected C artwork; their titles and filenames distinguish the connection patch. Generated version is initially `1.61-r1-experimental`; the earlier isolated sample remains r0. The command reads the actual game version from `version.scs:/version.sii` and rejects other game families/releases.

Explicit dependency order is authoritative. Missing known companions are inserted without reordering the supplied sequence; the source is highest and must not be repeated as a dependency. Source-only companion order is a declared baseline, not a substitute for the user's combined stack. See [connector reproduction](CONNECTOR_FUEL_FIXES.md#reproduction) for the full screenshot-derived order.

Each run writes an audit beneath `local_outputs/work/<timestamp>/<map-slug>/` and the descriptive `.scs` beneath `local_outputs/generated/<timestamp>/`. Timestamps default to Europe/Warsaw. Failed/partial coverage produces an audit and error rather than a complete-labeled mod. A source already covered produces `already_covered` without an empty archive. Existing outputs and audits are not overwritten.

## Effective data and scope

The installed baseline consists of base, shared assets, base map, definitions, installed state/map DLCs and Road Trip Ford. Installed DLCs are treated as owned for this user's explicitly confirmed all-DLC setup, and this assumption is recorded. This is not a general entitlement detector. Selected source/dependency order is an explicit analysis stack, not a current profile inspection.

| Source map | Automatically selected sibling packages |
| --- | --- |
| ATS Expansion | None |
| Reforma | Mega Resources |
| ProMods Canada map | Assets, models and definitions |
| Western Canada | Complete ProMods companion set when provided; partial/ambiguous sets are rejected |
| Alaska | None |
| Western Canada ProMods Connections | Western Canada, then ProMods models, assets, map and definitions; connector highest |
| Reforma OtherMaps Patch | Mega Resources and Reforma; the inspected patch has zero sector fuel targets and produces no empty fix |

Extra connection/OtherMaps patches are not silently pulled from the live mod directory. The two known connector families are recognized when explicitly selected as the source. Additional dependencies and changed source/resource versions alter the effective data and require review/regeneration. The [input inventory](LOCAL_INPUT_INVENTORY.md) records supplied versions and the [connector findings](CONNECTOR_FUEL_FIXES.md) distinguish the inspected patches' actual roles.

Coverage targets truck fuel items belonging to source sectors or linked to source prefabs across neighboring boundaries. A fuel point already available to a car at exactly the same transform is retained. Existing car pumps at other positions are also retained, but do not count as a co-located counterpart for a different truck pump. Counts describe logical interaction points and prefab instances, not visible dispensers or unique real-world stations.

## Deterministic transformation

**Observed locally — code and supplied files:** all 1,220 `.base` and 1,220 `.aux` files parse sequentially, including 107 exact empty legacy `.base` sectors. The largest inspected Reforma `.aux` exceeds the old read limit and uses bounded 64 MiB disk-backed reads. Unknown nonempty layouts, nested fuel, unresolved identities, unknown GAS flags and ambiguous placement remain blockers.

1. Read typed prefab units while retaining complete original unit text, including numeric and array attributes. Decode placed prefab tokens and resolve their descriptors from the effective stack. Some supplied declarations use uppercase letters; lookup is normalized to the lowercase alphabet stored in map tokens, while copied source attributes remain intact.
2. Resolve source/neighbor parents, linked services and fixed-point nodes. Rotate control-node order using the prefab's Origin. Validate placement and match GAS points uniquely, with tight horizontal and bounded measured vertical tolerance. Match by geometry rather than serialized list index.
3. For each missing counterpart, retain the truck GAS/service/node and add a car GAS locator plus a kind-7 Service/node at the same serialized transform. Keep existing car records. If only one side of the car cache exists, add only the missing side. Private prefab aliases/descriptors apply to edited instances; stock descriptors are not globally overwritten.
4. Update parent reference counts, item/node tables, explicit visibility lists and nonzero layer membership. Original node records are retained and the output node table is UID-sorted. Data/description payloads and opaque original records remain unchanged; a new Service has no separate data payload in the inspected reader.
5. Validate unchanged original truck records/nodes and resulting reciprocal car links. Reject incomplete coverage before packaging. Include sources, hashes, assumptions, point counts and limitations in the audit and embedded report. Run timestamps stay in external audit metadata to preserve reproducible package bytes.

**Hypothesis — garage extension:** a source FuelPump kind 35 gains an ordinary car Service while retaining the FuelPump. The inspected PrefabCreator consumes the first garage GAS as FuelPump and remaining GAS as ordinary Services. This is structurally supported and statically tested; garage ownership, price/discount and gameplay behavior are not verified. One ATS Expansion/stock boundary has a pre-existing unlisted FuelPump UID: unique geometry validates the point, all original references remain, and only the new car reference is appended. The baseline inconsistency is reported, not silently repaired.

**Documented in inspected independent parser source:** PPD v23 uses 32-byte spawn records, v24/v25 36-byte records. Version 25 also changes semaphore records. Legacy conversion is therefore allowed only for zero-semaphore descriptors; all original nonspawn section bytes and indices remain intact. All three legacy GAS descriptors supplied by ATS Expansion satisfy this guard. These are independent parser findings, not an official complete engine specification.

Primary format references: [TruckLib serialization at inspected commit](https://github.com/sk-zk/TruckLib/tree/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/Serialization), [PrefabCreator](https://github.com/sk-zk/TruckLib/blob/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/PrefabCreator.cs), [TruckLib.Models PPD implementation](https://github.com/sk-zk/TruckLib.Models/tree/master/TruckLib.Models/Ppd), and [SCS prefab locator documentation](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators). Inspection date: 2026-10-17; the corresponding source copies/coverage reports are in the timestamped work directory. [ADR-0006](../architecture/decisions/ADR-0006-discover-and-clone-map-fuel-services.md) records the decision and evidence limits.

## First complete output batch

See [r1 results](FUEL_FIX_BATCH_1_61_R1.md) for the five packages, exact fingerprints, 2,281 added points, independent verification and the nearer Helena test target.

The [additional connection package](CONNECTOR_FUEL_FIXES.md#western-canadapromods-connection) adds 50 points on connector-derived sectors. Its counters overlap the earlier packages' superseded sector versions; do not sum the six package counts as unique combined-stack coverage.

## Installation and testing

Disable older r0 fuel samples. Use a copied/disposable profile. **Place each fix immediately above its own source map**, preserving relative map priority; do not automatically stack all fixes above all maps. A higher-priority map or connection patch can replace a whole sector and invalidate a lower fix. Resource/definition companions remain required.

The generator changes interaction data, not physical access roads, meshes, pump layout or the economy. Start by testing the nearer multi-point Helena station with the full ATS Expansion fix, then truck/car purchases, garages and reload controls on each other map. User gameplay results belong in [validation results](VALIDATION_RESULTS.md) and [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). Courier fixes are not generated by this command.
