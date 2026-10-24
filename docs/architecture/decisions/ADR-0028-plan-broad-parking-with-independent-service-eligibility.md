# ADR-0028: Plan broad parking regions with independent service eligibility

- Status: accepted
- Date: 2026-10-24
- Task: [TASK-0052](../../tasks/active/TASK-0052-generate-broad-station-parking-areas.md)
- Extends: [ADR-0022](ADR-0022-select-mutually-exclusive-car-parking-strategies.md), [ADR-0024](ADR-0024-compose-complete-realistic-map-replacements.md)
- Supersedes: ADR-0024's preference for individual generated bays in realistic mode; its fuel/source-composition policy remains.

## Context

**Documented — user feedback, 2026-10-24:** the localized two-area Dawson r11 correction provides exactly the requested experience. Generalize coherent parking regions to other stations, first handling facilities without original functional car rest. Existing car-rest facilities should receive enhancements only through an explicit default-off flag. Fueling remains a separate service: existing parking must not suppress missing eligible car fueling, and existing fueling must not suppress missing parking. The user will report issues opportunistically during career play.

## Decision

Classify original effective facility support as `present`, `absent`, or `unknown` before the reviewed-model gate. Inspect actual PPD and standalone actions, resolving custom/mixed vehicle eligibility and numeric rest HUD parameters. Paint, NPCs, fuel locators and icons alone are not functional rest evidence. Exclude generated fixes from the original census.

Associate additional rest through actual placement/slave links or contained geometry within the placed light station-lot proxy. Inspect a bounded 3x3 base/aux neighborhood, with elevation and nearby-facility ambiguity checks. Do not use the independent 1,000-unit truck-area rule here. Unresolved relevant definitions, activation semantics or geometry produce `unknown`; unrelated distant objects do not automatically invalidate a station. An absence result is limited to this disclosed inspection scope.

Any original car rest serving the facility exempts its entire station by default. `ProcessorConfig.improve_existing_car_parking` and `--improve-existing-car-parking` default to false. True requires the rest processor with the `station_bays` strategy, propagates into real planning and permits safe disjoint additions while preserving native areas. Invalid/nonboolean/irrelevant combinations fail validation. Original support is always reported even when the flag is true. Enhancement currently requires unambiguous support in the placement’s own PPD. Related unresolved evidence or externally associated/standalone native rest causes an explicit skip because the planner does not yet clip improvements against those shapes.

The flag and native classification apply only to parking. Fuel planning, selection, prices and context composition remain independent. A skipped, unknown or native-supported parking location cannot cancel eligible fuel changes. Likewise, retained native fuel support does not exempt missing parking. Keep the accepted realistic facility exclusions unchanged; independence creates no new fuel or parking eligibility policy.

Realistic parking uses whole evidenced paint banks and deterministic contiguous curb/landscape strips. Validate permanent model geometry, ground and heights, pump work space, navigation/circulation, entrances and bounded external objects. Split disconnected regions and reject unsuitable intervals; do not fall back to an arbitrary small bay or truck-rest access. Treat variable NPC parked locators as parking evidence rather than permanent obstacles. Accessible marked bays remain eligible; access hatching remains excluded.

Each selected logical area receives its own native car-only group, fresh group ID and independent links. New broad-area groups explicitly set PPD partial-contact bit `0x4`; native parameters remain unchanged. Existing per-station experiments preserve their former default behavior. Cache family geometry only across identical descriptor, model, variant/parts and parameters; keep placement/world context checks separate.

Retain Dawson's exact accepted two rectangles as a source-pinned reviewed override in the family catalog. Rebuild against the original/fuel-preserving descriptor rather than mounting old gameplay fixes. Preserve original archive/sector/descriptor/model pins and reject drift. Do not generalize the literal Dawson footprint or force exactly two regions elsewhere.

## Consequences

The next complete set is source-stack-specific and consists of eight full replacements, with native improvements OFF. Existing native facilities, truck/bus triggers, fuel IDs/private lineage, country price provenance and winning-provider composition remain protected. Background/navigation packages are outside this goal under the user’s subsequent explicit scope clarification. The parking/fueling outputs introduce no presentation resources.

Coverage must distinguish original support states, generated station counts and logical area counts, separately from fuel interactions and policy exclusions. Unsupported families and ambiguous layouts remain explicit skips. Full replacement packaging is not universal geometry support. Static checks establish emitted bytes and structural preservation, not runtime vehicle shape, fatigue, billing or save behavior. Dawson retains its actual user-accepted scope; other new regions await ordinary-play feedback.
