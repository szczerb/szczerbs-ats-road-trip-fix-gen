# ADR-0020: Plan station parking from pinned effective model state

## Context

Date: 2026-10-19. [TASK-0044](../../tasks/active/TASK-0044-improve-effective-station-parking-heuristics.md) follows both user-confirmed Dawson prompts and the discovery that Real Companies replaces the visible model and removes the stock paint bank. Historical schema-1 A/B inputs remain useful controls but cannot establish the current visual layout. See [dated feedback](../../reference/GAS_STATION_CAR_REST_FEEDBACK_2026_10_19.md).

## Decision

Keep the existing independent station processor and [package boundaries](ADR-0019-station-parking-module-boundaries.md). Introduce explicit configuration schema 2: require effective PMD, PMG, converted PIM and paired PIT fingerprints, plus reviewed effective material/texture resources. Resolve the placement variant and explicitly named additional parts against the paired PIT before inspecting geometry; unknown or ambiguous states block. Record actual source providers and resource hashes. Read directory packages without modifying them, snapshot resource names/stats, and recheck selected model/material bytes before writing.

Preserve schema-1 planning and controls. Schema-2 packages require a new positive revision and leading C FORECOURT / D MARKED experiment identifiers. Do not silently repin historical examples or overwrite their packages.

Keep proposals, access validation, ranking, diagnostics and serialization distinct. Evaluate footprint and approach against conservative operational, map-road, occupancy and sampled-model checks. For painted banks evaluate both ends rather than assuming an entrance. Record rejected alternatives, explicit rank components and a stable ID tie break. Within an evidence class, prefer clearance surplus over mandatory exclusions (capped at 2 m, rounded to centimetres), then pump clearance capped at 20 m and bay capacity. These are proxy-based preferences, not simulated vehicle paths. Physical proposal and technical activation polygon receive separate report fields; native range/flags remain unchanged unless a separately labelled diagnostic explicitly tests a parameter.

**Documented / Unknown:** SCS authoring documentation defines polygon range as vertical and partial activation as border contact. The precise player geometry tested by ATS 1.61 remains unresolved; do not infer an engine-predicted usable-pose envelope. Source-derived placement work may continue independently. [Activation investigation](../../reference/STATION_PARKING_HEURISTICS_1_61.md).

## Consequences

The effective visual model cannot silently fall back to stock paint evidence. Inputs and replays are larger and deliberately explicit. Bounded render sampling and name-assisted curb/door geometry cues still do not prove collision-complete access, real pedestrian routes, runtime NPC occupancy or intuitive activation. Native car controls must suppress duplicate triggers. Whole-sector overrides require explicit composition and source-priority handoffs; N2 remains independent. Runtime improvements require later user tests; no game, profile, merge, push or publication action is implied.
