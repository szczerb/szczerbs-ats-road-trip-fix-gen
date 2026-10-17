# Sample 2: overlapping truck and car fuel interactions

Prepared: 2026-10-17. Reference ATS **1.61.3.18**, ATS Expansion **23.0**, Road Trip Ford. **Observed locally:** generated and structurally verified. **Unknown:** actual coexistence/filtering/refueling in game; this is an experiment, not a verified dual-vehicle fix.

## Use this sample

File: `local_outputs/generated/ats-expansion-helena-overlapping-fuel-sample-2.scs`.
Mod-manager display name: **Road Trip Helena - truck + car at one pump (sample 2)**.

1. Use the existing disposable profile. Disable sample 1 and other generated fuel samples. Enable sample 2 **above ATS Expansion**. It is generated from original expansion data and does not need sample 1 installed.
2. Return to the **same eastern Helena-area single dispenser already tested**, not the nearer city station or Great Falls. The physical position/geometry is unchanged.
3. In truck mode, check map visibility, marker/prompt and actual fuel increase/payment at that dispenser. With the same sample still active, switch to car mode and check the same things at the same place. A map icon alone is insufficient to establish refueling support.
4. Record each mode separately, including no prompt, overlapping/flickering markers, wrong interaction, or failure after reload. Both interactions are deliberately co-located; do not move one as part of this initial comparison.

The expected outcome is truck and car interactions at the same physical dispenser, selected appropriately by the game mode. It is still a **hypothesis** that the engine accepts the two records at identical transforms. No game/editor/profile operation or automatic installation was performed by the agent.

## Exact fixture and output

The [schema-2 recipe](../../examples/helena-overlapping-fuel-1.61.3.18.json) pins the original sector/PPD, service node, node-table boundary/counts and four companion hashes. Target identity and previous observations are in the [starter guide](STARTER_AREA_SAMPLE.md) and [validation results](VALIDATION_RESULTS.md).

| Property | Value |
| --- | --- |
| Target sector | `map/usa/sec-0015-0012.base` |
| Original prefab UID | `0x45aa5478ea6f0001` |
| Original truck service UID | `0x660cd95039002d88` |
| Original truck node UID | `0x660cd9510b802d87` |
| Added car service UID | `0xf43eb64570b95935` |
| Added car node UID | `0xf64c7320c86a342e` |
| Private prefab alias | `prefab.rtp1f50062a` |
| Both service-node positions | `(-57751.1015625, 78.09765625, -47850.9765625)` |
| Both PPD-local positions | `(2.25, 0.09955330193042755, -5.944096088409424)` |
| Descriptor GAS records | Original flags `0`, added flags `1`; identical 28 position/rotation bytes |
| Service flags | Original `0x80000000`, added `0x80004000` |
| Sector size | 94,944 → 95,085 bytes (+141) |
| Sector item / node counts | 319 → 320 / 396 → 397 |
| Prefab service references | 1 → 2 |
| PPD size / spawn count | 908 → 944 bytes / 1 → 2 |
| Generated gameplay resources | Private prefab definition, private PPD, one `.base` override |

**Observed locally:** original truck GAS record, 77-byte service record and 56-byte node record are retained byte-for-byte. The added GAS locator copies the same prefab-local position and quaternion bytes; the added map node copies the same world position and quaternion bytes. There is no positional epsilon, new physical dispenser, mesh duplication, or road/parking change. Quaternion components in the inspected serialization are ordered WXYZ.

The sector adds eight bytes to the parent's service-reference list, one 77-byte car service, and one 56-byte car node. Original variable-length items and the complete original node table remain unchanged apart from the parent prefab alias/reference-count edits and file counters. A reconstruction check removes additions/reverts those bounded edits and recovers the original source bytes. The final original item is a 165-byte Company, not another service; the implementation does not assume a final item type.

## Why companions remain unchanged

**Documented in pinned independent parser source:** [TruckLib Map.cs](https://github.com/sk-zk/TruckLib/blob/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/Map.cs) reads `.base` as a 16-byte header, counted variable-size items, counted nodes, and counted visibility references. `.data` payload entries are keyed by item UID rather than by item offsets/indices. [ServiceSerializer](https://github.com/sk-zk/TruckLib/blob/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/Serialization/ServiceSerializer.cs) has no separate data payload. [PrefabSerializer](https://github.com/sk-zk/TruckLib/blob/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/Serialization/PrefabSerializer.cs) uses control-node count, which is unchanged here, for its payload shape. [Node.cs](https://github.com/sk-zk/TruckLib/blob/c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0/TruckLib/ScsMap/Node.cs) defines the fixed 56-byte node layout. These describe an independent parser implementation, not a complete official ATS engine specification.

**Observed locally:** the source has 396 UID-sorted node records at offset 72,764 after the node count at 72,760, followed by a zero visibility-child count. The 24-byte `.layer` has no entries. `.data`, `.aux`, `.desc` and `.layer` are fingerprinted, retained from ATS Expansion and not packaged. Source `.desc` version 3 exceeds the parser's described default 2; it is kept opaque and untouched. No new `.data` payload or layer registration is assumed for the added service.

New UIDs are deterministic hash-derived ordinary uint64 values with a high prefix for the reviewed local append ordering. Collisions are checked against the original sector and all four pinned companions; this is not a scan of every UID in every possible game/mod stack. Engine overlap behavior, marker rendering and activation range still require the user test.

## Reproduce

The local successful invocation uses existing original snapshots, whose provenance is recorded in the [baseline](RESEARCH_BASELINE.md) and previous [sample guide](STARTER_AREA_SAMPLE.md):

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-overlap-fuel \
  --baseline local_outputs/extracted/game-def \
  --baseline local_outputs/research/refueling/official-ppds \
  --baseline local_outputs/extracted/starter-fuel-assets \
  --map local_inputs/ATS_Expansion_v23.0_1.61.scs \
  --recipe examples/helena-overlapping-fuel-1.61.3.18.json \
  --output local_outputs/generated/ats-expansion-helena-overlapping-fuel-sample-2-recheck.scs \
  --game-version 1.61.3.18 --experimental
```

Alternatively use the original installed `base.scs` and `def.scs` as repeated baseline packages and specify the external `--extractor` before the subcommand. The gameplay payload should match; provenance paths in the embedded report differ between archive and snapshot invocations. Existing outputs are never overwritten.

Original source sector SHA-256: `e807655d879eb07d069b4f3dd362007eaba7e4bdc935810aea43445c787a700c`.
Generated sector SHA-256: `77c156624472d2379254509a105e2e182f1885e92b25b90597becebe3726acbe`.
Generated PPD SHA-256: `7390eb7ede94f3e1eea8d8bf62fe4d49d97cfe09ee02a859557b0583c4f0bfff`.
Package: 105,307 bytes; SHA-256 `fe783c39547cb59980278db4e9c2314bf0c0983477480c47291f937b4c7b1347`.

**Compatibility boundary:** this remains a full `.base` override tied to the pinned source expansion sector and companions. Use one fuel experiment at a time; sample 1 above this package would replace its sector and invalidate the comparison. The generator rejects source/companion drift and unsupported layout rather than rebasing unknown maps. All generated/copied assets stay ignored; only authored source, recipe and documentation are tracked.

See [TASK-0009](../tasks/done/TASK-0009-build-overlapping-fuel-pair.md) for implementation/static verification and [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) for runtime acceptance.
