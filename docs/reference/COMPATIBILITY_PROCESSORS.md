# Selectable compatibility processors

Updated: 2026-10-18. Target: ATS 1.61 / Road Trip Ford. [ADR-0008](../architecture/decisions/ADR-0008-compose-processors-and-local-rest-polygons.md) records the user-selected processor model and rest-distance rule. Runtime behavior remains subject to the [manual checklist](MANUAL_TEST_CHECKLIST.md).

## Selection and commands

The general command requires explicit processor selection. Repeat `--processor` to combine topics:

```bash
# Only rest eligibility; no fuel-point or price analysis.
PYTHONPATH=src python3 -m ats_road_trip generate-map-fix \
  local_inputs/Western_Canada_Expansion_v1.7.3.scs \
  --processor rest --rest-radius 1000 --experimental

# Fuel access/prices and rest eligibility in one composed package.
PYTHONPATH=src python3 -m ats_road_trip generate-map-fix \
  local_inputs/Western_Canada_Expansion_v1.7.3.scs \
  --processor fuel --processor rest --rest-radius 1000 --experimental
```

These are generation commands, not evidence that every supplied map passes coverage checks. They require the installed game/reference data and appropriate map dependencies. Use repeated `--dependency` in lowest-to-highest order where needed; the [source priority guide](CONNECTOR_FUEL_FIXES.md) remains authoritative. The generator does not infer the active profile's mods.

| Enum value | Included work | Status |
| --- | --- | --- |
| `fuel` | Missing car fuel interactions plus country petrol-price repair | Existing r2 algorithm; [price policy](../architecture/decisions/ADR-0007-repair-missing-petrol-prices.md) |
| `rest` | Local car rest eligibility subject to the proximity rule | Experimental; supported layouts and coverage must pass before packaging |
| `courier` | Source-relative company locations, marker evidence and context/job inputs | [Analysis/reporting only](COURIER_REPORTING.md); generation still raises an explicit unimplemented error |

Python callers use `Processor`, `ProcessorConfig` and `ProcessorMode` from `ats_road_trip.processors`. Disabled processors do not run. Duplicate/empty selections, unknown names, generation of unimplemented topics, or negative/nonfinite radii fail validation. Fuel runs before rest regardless of selection order. Courier reporting is available in explicit analysis mode through `analyze-map --processor courier`; that mode writes an audit and never calls the mod writer.

```python
from ats_road_trip.processors import Processor, ProcessorConfig

config = ProcessorConfig(
    enabled=(Processor.FUEL, Processor.REST),
    rest_radius=1000,
)
```

The existing `generate-map-fuel` command retains fuel-only behavior and default revision 2. The general command defaults to revision 6 and uses names matching the selected topics: Gas Stations Fix, Rest Stops Fix, or Map Compatibility Fix. Author remains `szczerb`; all versions remain experimental. Combined fuel/rest output uses the selected M2D four-Ford map-specific icon for each of the seven supplied sources, selected from `assets/mod-icons/map-compatibility/<map-slug>.jpg`; an explicit valid `--icon` overrides it. Fuel-only output retains the historical icon selector. Rest-only output has no default icon. All packages get a topic-specific player description with source-relative priority and pending gameplay checks. The separate Practical Courier Jobs generator defaults to revision 2 with the approved J3C icon. [Metadata contract](MOD_METADATA.md) and [final handoff](MOD_METADATA_FINAL_1_61_R6_R2.md).

Use **one generated fix per source map**. Select both topics in one run to retain both features. Independently generated rest-only and fuel-only packages can replace the same whole sector; placing one above the other does not merge their content. A combined package replaces that source's earlier fuel-only fix. Rest-only generation against the original source does not include previous fuel corrections and is not an add-on to the r2 fuel package.

## Rest distance and local actions

**Documented — user direction:** use straight-line distance in the game world, not a route/nav distance. The default radius is **1,000 map-world units in XZ**. Compare the minimum distance between the complete parking polygons; overlapping/contained areas have distance zero. A car rest exactly at the radius counts as nearby, so no addition is made. This is not a claim about displayed navigation kilometres, road accessibility or elevation.

Use the original effective car-rest inventory from source-owned sectors and a bounded halo of neighboring sectors, resolving data through the supplied game/DLC/dependency/source order. A nearby car rest from another package suppresses the addition when it falls within the inspected scope. Generated car permissions do not become new neighbors during the same run, so candidate order does not change the result. Different map namespaces are independent. **Documented — latest user instruction:** boundary false positives are acceptable: missing an existing car area beyond the inspected region may produce an extra car permission at a truck/bus rest. This is reported, not treated as a requirement to scan the whole game.

The halo is a filename neighborhood around nonempty source sectors; empty reservation sectors do not expand it. Its width is `max(1, ceil(radius / 4000))` sectors, using the nominal 4,000-unit grid. This is a practical search bound, not a proof that no prefab extends beyond it. The report lists source/halo paths, counts and omissions. Far sectors and unrelated map namespaces are not read merely to prove absence.

**Observed locally — installed ATS 1.61.3.18 definitions:** prefab polygons reference named shared actions. The source file `def/world/trigger_action.sii` explicitly permits additive `trigger_action.<unique>.sii` files, with a shared unit namespace. Existing `hud_parking` has `truck` and `bus`; `parking_car` has `car`; both use `hud_activate` with numeric parameter 3. [Dated source evidence](PASSENGER_CAR_REST_RESEARCH.md).

For a selected truck/bus polygon, create a private action containing its original vehicle list plus `car`, then change only that polygon's action reference through a private prefab descriptor/definition. Keep the original shared action and untouched placements unchanged. Preserve polygon geometry, topology and all other descriptor bytes; this avoids overlapping duplicated rest polygons. Standalone map triggers need their serialized action parameters checked separately.

**Observed locally — static format audit, 2026-10-18:** 1,800 cached sector files contain 6,478 standalone rest triggers (including lower-layer copies, not unique effective locations). All observed activation flags fit the documented mask `0x0007ff3f`; ordinary areas use flags such as `0x0c`/`0x0d`, not zero. The audit includes 6,477 polygons and one two-node sphere. [Primary Trigger implementation](https://github.com/sk-zk/TruckLib/blob/master/TruckLib/ScsMap/Trigger.cs) distinguishes vehicle/trailer activation, partial/oriented/collision settings, DLC guards, initially disabled, view-distance and secret bits. The generator preserves those flags and guards, excludes disabled/non-vehicle areas, and refuses unsupported source activation semantics. It records the project's all-DLC ownership assumption; it does not remove a guard to make an area available.

Two-node spheres use the first node as center and the node separation as radius. Their horizontal distance subtracts activation radii from shape separation. Supported legacy one-node spheres use their serialized range. Prefab rest polygons retain their original trigger topology. Numeric HUD identifiers are compared by value, so a car-rest alias using `3.0` or `3e0` is not missed merely because stock definitions spell it `3`.

**Observed locally — broader source inventory, 2026-10-18:** some original standalone triggers have crossing edges or duplicate vertices. Their geometry stays byte-identical. Such existing car areas are used only when a pair of original vertices proves proximity; otherwise they can be missed and cause extra car permissions. For a validated irregular standalone truck action without a vertex-proven neighbor, only its action token is retargeted, with conservative proximity recorded; geometry is never repaired. [ADR-0012](../architecture/decisions/ADR-0012-preserve-irregular-source-rest-geometry.md) distinguishes this implementation decision from the user’s explicit boundary approximation. The audit lists `legacy_irregular_polygons` with its reason and proximity method. Descriptor v23/v24 trigger arrays are supported only after header/section validation and exact 48-byte record checks, as for v25. Uniform `0x4` partial-activation groups retain their raw flags when retargeted; mixed or unknown flags still block. [Source-layout evidence and limits](REST_LEGACY_LAYOUT_TRIAGE.md). Definition-only sources have no rest targets and report `not_applicable`, permitting an independent price-only package.

**Hypothesis:** the additional vehicle parameter makes that rest area usable by cars while retaining truck/bus behavior. Static byte/parameter checks do not prove the action's runtime handling, map-icon discovery or successful fatigue recovery.

## Composition, blockers and validation

Fuel's staged sector/private-prefab resources are input to rest generation. Rest must retain fuel changes on any shared paths and explicitly declare composed resources; unacknowledged collisions block publication. Source ownership is determined from the original package stack, not from a synthetic overlay's identity.

All enabled processors finish analysis before a mod is written. Unsupported source geometry/action layouts, missing transforms/resources needed for source edits, ambiguous definitions or conflicting edits prevent a package from being published as complete. Neighbor-only omissions and the bounded search perimeter are recorded as limitations rather than whole-world coverage blockers. The timestamped work audit records the reason. A successful fixture test is not proof of a whole-world car-rest inventory. Completion applies to the declared supported source-edit scope; known uninspected/omitted neighbor data can cause the accepted extra additions.

Manual acceptance remains separate: car rest prompt with engine off, actual fatigue recovery, truck/bus preservation where applicable, icons/discovery and save/reload. When fuel is included, also test positive petrol price, finite quantities, tank increase and correct payment. No automatic installation, game launch or save/economy/fatigue changes occur.

## Verified Western Canada candidate

Historical r3 result; the overnight r4 implementation preserves alias context inputs as described in [ADR-0010](../architecture/decisions/ADR-0010-preserve-contexts-for-generated-prefab-aliases.md). The r5 metadata refresh retained those gameplay bytes; the r6 map handoff must do the same. Runtime preservation remains unverified.

**Later static finding, 2026-10-18:** [14 Company-parent aliases lose their original context mappings](COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk). The fuel/rest checks below do not establish courier preservation. Runtime effect remains unknown; [TASK-0019](../tasks/done/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md) tracks the required preservation review. The historical candidate remains untouched; the overnight r4 packages include preservation.

**Observed locally — 2026-10-18:** the combined `fuel` + `rest` workflow generated `local_outputs/generated/2026-10-18_02-18-17/szczerbs-road-trip-map-compatibility-fix-western-canada-1.61-r3-experimental.scs`. Size **7,168,670 bytes**; SHA-256 `49ade9be22ea02d0ba73335352a4495c2a71430aff183249b366dd84d61a64ec`. Manifest title: `szczerb's Road Trip Map Compatibility Fix for Western Canada`; author `szczerb`; selected topics `fuel`, `rest`; no automatic gas-only icon.

| Result | Count |
| --- | ---: |
| Source sector files | 952, including 598 nonempty files |
| Additional halo sector files | 52; zero reported omissions |
| Existing car rest areas in the bounded index | 99 |
| Source truck/bus rest areas considered | 206 |
| Areas left unchanged because a car rest is nearby | 4 |
| Areas gaining car eligibility | 202 across 198 placements |
| Car fuel interactions retained from r2 | 288 |
| Petrol-price additions retained from r2 | 6 |

These are logical areas/interactions, not necessarily distinct physical parking lots or stations. Scope is source-relative and approximate at the boundary; other active maps may override some resources at runtime. This is one Western Canada candidate, not a regenerated seven-map rest batch.

The ordinary command is the combined example above. The integration run reused read-only extraction caches from the first full-world probe through an ignored local adapter, while invoking the public workflow and retaining original package identities/order. Source identities and reused cache hashes passed before/after checks. Audits are in `local_outputs/work/2026-10-18_02-18-17/`; the helper and original probe remain under `local_outputs/work/2026-10-18_02-01-14/`. No product dependency on those caches was introduced.

Independent package verification passed ZIP CRC, metadata and all resource hashes. Every earlier r2 gameplay resource is identical except sectors deliberately composed with rest changes. Across rest-touched sectors, 745 original fuel service records and 29,952 map nodes are byte-identical. All 179 private rest descriptors preserve spawns/geometry/topology and change only selected eight-byte action tokens; standalone edits likewise change only selected action tokens. The private action retains `truck`/`bus` and adds `car`; the shared action file is not overridden. Verification script/report: `local_outputs/work/2026-10-18_02-18-17/verification/`.

The full authored suite passes **179 tests**. Independent bounded fixtures use unchanged WCE and connector sectors, verify r2 fuel composition, and separately inject a clearly labelled synthetic car neighbor at 65.221 units to test suppression. A prior full-world probe correctly refused output because the first parser did not yet recognize ordinary standalone activation flags; source-guided flag/sphere support and the user-approved bounded search replace that attempt. No complete-neighborhood or gameplay success is inferred from the passing candidate.

For later testing, replace **only the Western Canada r2 fix** with this combined r3 package, at the same source-relative priority. Keep other maps' r2 fixes in place. Do not enable the old WCE fuel fix and this combined replacement together. The [manual checklist](MANUAL_TEST_CHECKLIST.md) remains pending; no game/profile/install action occurred.
