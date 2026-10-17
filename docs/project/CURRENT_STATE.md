# Current State

Updated: 2026-10-17. The first complete map-wide fuel generation milestone is complete and statically verified. [TASK-0011](../tasks/done/TASK-0011-generate-map-wide-fuel-fixes.md) records implementation, delegation and checks; [batch r1](../reference/FUEL_FIX_BATCH_1_61_R1.md) records the five output fingerprints and load priority.

## Available result

- `generate-map-fuel SOURCE --experimental` resolves installed ATS reference data and known sibling companions, discovers missing car fuel interactions and creates a descriptive map-specific fix. No hand-authored station recipe or LLM is needed to run it. [Usage and mechanism](../reference/MAP_WIDE_FUEL_GENERATOR.md).
- Five **1.61-r1-experimental** packages are generated: ATS Expansion **894**, Reforma **954**, ProMods Canada **102**, Western Canada **288**, Alaska **43** new car points. Total **2,281**, including **133** garage points. Every original truck service/FuelPump and node is retained byte-for-byte; every new point passed independent transform/link verification. These are logical interaction counts, not unique physical stations.
- All **111 tests pass**. All 2,440 source sector files parse; all five output integrity/resource/source checks pass. Each archive also survives byte-identical repackaging. Unsupported coverage would prevent output; these five reports have zero blockers.
- The older ZIP/HashFS inspector, selective extractor, courier-context audit, bounded courier alias generator, descriptor-only fuel experiment and pinned single-point samples remain available. Their historical scopes do not restrict the separate new map-wide command.

## Runtime boundary

**Documented — user report, 2026-10-17:** the original overlapping Helena-area sample 2 works for both a car and truck at the same physical pump. The previous sample 1 allowed car refueling but lost the truck map icon. [Dated evidence](../reference/VALIDATION_RESULTS.md) preserves both results and their attribution; the agent has not reproduced gameplay.

**Unknown:** runtime behavior of the complete r1 packages, multi-point/cross-slope stations, garage ownership and price behavior, reload/control regressions and physical access at every location. These outputs remain experimental. The ATS Expansion package now covers the nearer four-point station inside Helena as well as the previously tested eastern point. See [next-test instructions](../reference/FUEL_FIX_BATCH_1_61_R1.md#load-priority-and-next-user-test).

Whole-sector overrides must follow source priority: each fix directly above its own map, not all fixes above all maps. Three map pairs have shared changed sectors. Extra connection/compatibility patches are separate effective-data inputs. No profile, live mod directory, game installation or economy reset was modified.

## Baseline and artifacts

Observed reference is ATS **1.61.3.18**, Steam build **25952361**, installed map DLCs plus Road Trip Ford. The user confirms owning all DLCs; the generator records this installed/owned assumption. [Nine supplied archives](../reference/LOCAL_INPUT_INVENTORY.md) now include the four ProMods 1.6.4 packages. Sources are immutable; no future metadata cleanup is automatic.

Current work/cache/audit files live under ignored `local_outputs/work/<Europe-Warsaw-timestamp>/`; new outputs under `local_outputs/generated/<timestamp>/`. The final five-file collection is `local_outputs/generated/2026-10-17_22-46-14/`. Historical samples/tools remain at their recorded locations. Small original map-labelled icons and prompts are tracked; copied game/mod data are not.

## Courier research and next work

Courier jobs use prefab context tags. Existing audits classified 964 of 1,030 sampled ZIP company definitions, with 25 SCS exclusions and 41 unclassified. Prefix-wide patches remain unsupported. Reforma `ahorrara` has an exact stock model/descriptor counterpart and an additive retail-context candidate; usable offers/deliveries are still unverified. [Courier findings](../reference/COURIER_RESEARCH_FINDINGS.md).

Next: active [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). Test actual car/truck purchases with r1 and source-relative priority, first at the nearer Helena station, then other maps/garages/reloads. Courier completion remains an offer plus a usable completed delivery, not a definition tag. The current user request focused implementation on fuel; no map-wide courier fix is claimed.
