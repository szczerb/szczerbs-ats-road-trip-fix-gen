---
id: TASK-0014
title: Audit effective petrol prices and test a sourced BC override
status: backlog
priority: high
repositories:
  - .
depends_on:
  - TASK-0013
owner: shared
---

# Goal

Add deterministic country-price diagnostics and prepare the smallest sourced British Columbia override to test the missing-price hypothesis, preserving source map/connector definitions and diesel behavior.

# Context

**Observed locally, 2026-10-18:** ProMods BC has a positive `petrol_price`, but the higher connection file omits it. Western Canada's six province definitions also omit it. **Documented — user report:** access/refueling works across many Canadian stations, while displayed gallons are invalid; the screenshot shows zero price. The engine default and exact quantity arithmetic are unverified. [TASK-0013](../done/TASK-0013-investigate-canadian-fuel-nan-display.md) establishes the evidence and limits.

# Scope

- Audit effective country-unit fuel fields and their provenance against an explicit source order; distinguish missing, zero, nonfinite and positive values without silently selecting a fallback.
- Prepare a definition-only BC candidate from the winning connector file, adding only the existing ProMods `petrol_price: 1.502116` with its provenance. Do not change the connector's `fuel_price: 1.630`, position, station records or other attributes.
- Keep the diagnostic separable from r1 station-access packages; the same-pump test requires a confirmed BC location and recorded effective mods.
- For other provinces and potentially affected Alaska/Reforma definitions, establish an explicit sourced price policy before generating replacements; missing fields alone do not authorize invented prices or imply observed runtime failures there.
- Do not modify a live profile, install mods automatically, replace whole lower-priority country definitions, or claim runtime repair from static checks.

# Implementation Plan

1. GPT-6 Sol / medium implements the bounded audit and source-preserving diagnostic packaging with meaningful tests.
2. GPT-6.1 Sol / high reviews effective-source resolution, numeric validation and any proposed broader price policy.
3. Root integrates, documents source hashes/order and prepares the candidate for TASK-0007's user-run same-station comparison.

# Acceptance Criteria

- Audit results identify exact effective country paths, units, source versions and finite/missing petrol-price status.
- A BC candidate is reproducible and changes only the sourced petrol-price attribute; unsupported/ambiguous cases are reported.
- Static checks confirm preserved diesel price and all other source fields, deterministic packaging and immutable inputs.
- Runtime acceptance requires a positive price, initial finite zero, finite changing quantity, measured tank/balance changes and a truck control at the same station; record a blocker if the location/setup is unavailable.
- No broader price policy is applied implicitly; define explicit provenance and version behavior before expanding beyond BC.

# Verification

Not started. This is follow-up scope, not a generated or tested repair. Proposed runtime comparisons are described in [the research reference](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md#smallest-discriminating-next-test).

# Links

- [Completed investigation](../done/TASK-0013-investigate-canadian-fuel-nan-display.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Canadian fuel display research](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md)
- [Metadata conventions](../../reference/MOD_METADATA.md)
