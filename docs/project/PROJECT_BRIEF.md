# Project Brief

## Goal and audience

Build a utility that automatically produces small compatibility mods for American Truck Simulator map expansions and reworks, enabling Road Trip Courier Jobs and passenger-car refueling where support is missing. The initial user is an ATS player with existing map mods and little prior SCS modding experience; documentation should explain relevant concepts before relying on specialist terms.

The two features have equal research priority. Automation and small patch size are goals whose feasibility must be established from evidence.

**Documented — expanded user direction, 2026-10-18:** include passenger-car rest eligibility as its own selectable processor alongside fuel and future Courier Jobs. Only add car support to a truck/bus rest area if no existing car rest lies within 1,000 game-world units in a straight line. Preserve truck/bus behavior and shared action definitions; compose selected changes into one source-specific mod. See [processor scope](../reference/COMPATIBILITY_PROCESSORS.md).

**Documented — authorized scope extension, 2026-10-18:** implement a standalone courier vehicle-eligibility generator, starting with reviewed practical Crown Victoria cargo jobs excluded for the Mustang. See the [generator guide](../reference/PRACTICAL_COURIER_GENERATOR.md). This is separate from source-map compatibility fixes and does not authorize silently bundling eligibility changes into them. Physical cargo suitability, class-wide effects and runtime behavior remain unverified; broader economy rebalancing remains outside the goal.

## Reported problem and evidence boundary

**User report (2026-10-17, ATS 1.61 / Road Trip context):** some modded cities offer Courier Jobs while others appear not to, and passenger cars cannot refuel at some stations in modded areas. Specific city/station examples have deliberately been deferred.

**Hypothesis:** Gemini suggested missing car-specific job markers and reuse of standard company identifiers explain the difference. This has not been confirmed by game data or experiments. See [economy and Courier Jobs](../reference/ECONOMY_AND_COURIER_JOBS.md).

**Observed locally — later research, 2026-10-18:** fuel compatibility uses placed service/prefab and sector edits; rest uses vehicle-filtered polygon actions. Standalone courier eligibility uses job-class definitions. General map courier repair and any common cause remain **Unknown**. See [car refueling](../reference/PASSENGER_CAR_REFUELING.md).

## Initialization deliverable (completed)

- Agent entrypoint, project context, task tracking, templates, and decision/incident conventions.
- Sourced references for shared SCS formats and ATS Road Trip behavior, with explicit evidence labels and version limits.
- A light inventory of supplied archives and a bounded, linked research backlog.

Initialization excluded utility code and experiments. The subsequently approved overnight milestone authorized archive tooling, research of both mechanisms, and an evidence-supported prototype. [ADR-0002](../architecture/decisions/ADR-0002-use-python-inspection-and-bounded-experimental-patches.md) records the resulting implementation choices; generated packages remain unverified in game.

## Eventual success criteria

Once a mechanism is proven, a future increment should generate the smallest supported compatibility artifact from identified game/mod inputs, explain its dependencies and required load order, and produce reproducible validation evidence. Courier validation must cover market availability and completing a delivery; refueling validation must cover reaching a station and replenishing fuel. Both must check relevant truck behavior and shared-profile progression for regressions.

These are future validation goals, not claims that an implementation is currently possible. The [design task](../tasks/done/TASK-0005-design-first-generator-increment.md) selected a concrete first increment after both investigations; runtime acceptance remains a separate gate.

## Target and non-goals

Target ATS 1.61 and Road Trip first, recording exact build/DLC/mod versions during research. ETS2 is a shared-format reference, not a promised product target. Existing companies and stations are the intended locations; new maps, a general mod editor, economy rebalancing, and changes to the player's career are outside the goal.
