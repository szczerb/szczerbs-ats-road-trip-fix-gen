# Project Brief

## Goal and audience

Build a utility that automatically produces small compatibility mods for American Truck Simulator map expansions and reworks, enabling Road Trip Courier Jobs and passenger-car refueling where support is missing. The initial user is an ATS player with existing map mods and little prior SCS modding experience; documentation should explain relevant concepts before relying on specialist terms.

The two features have equal research priority. Automation and small patch size are goals whose feasibility must be established from evidence.

## Reported problem and evidence boundary

**User report (2026-10-17, ATS 1.61 / Road Trip context):** some modded cities offer Courier Jobs while others appear not to, and passenger cars cannot refuel at some stations in modded areas. Specific city/station examples have deliberately been deferred.

**Hypothesis:** Gemini suggested missing car-specific job markers and reuse of standard company identifiers explain the difference. This has not been confirmed by game data or experiments. See [economy and Courier Jobs](../reference/ECONOMY_AND_COURIER_JOBS.md).

**Unknown:** whether the courier and refueling failures share a mechanism, whether either permits definition-only overrides, and whether fixes can be generated without editing prefabs or map sectors. See [car refueling](../reference/PASSENGER_CAR_REFUELING.md).

## Initialization deliverable

- Agent entrypoint, project context, task tracking, templates, and decision/incident conventions.
- Sourced references for shared SCS formats and ATS Road Trip behavior, with explicit evidence labels and version limits.
- A light inventory of supplied archives and a bounded, linked research backlog.

This milestone excludes utility code, extractor installation, patch generation, city-specific diagnosis, and in-game experiments. No language, CLI, public API, schema, or packaging strategy is selected.

## Eventual success criteria

Once a mechanism is proven, a future increment should generate the smallest supported compatibility artifact from identified game/mod inputs, explain its dependencies and required load order, and produce reproducible validation evidence. Courier validation must cover market availability and completing a delivery; refueling validation must cover reaching a station and replenishing fuel. Both must check relevant truck behavior and shared-profile progression for regressions.

These are future validation goals, not claims that an implementation is currently possible. The [design task](../tasks/backlog/TASK-0005-design-first-generator-increment.md) will select a concrete first increment after both investigations.

## Target and non-goals

Target ATS 1.61 and Road Trip first, recording exact build/DLC/mod versions during research. ETS2 is a shared-format reference, not a promised product target. Existing companies and stations are the intended locations; new maps, a general mod editor, economy rebalancing, and changes to the player's career are outside the goal.
