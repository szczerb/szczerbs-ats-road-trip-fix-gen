---
id: TASK-0014
title: Repair missing petrol prices and defer manual symptom validation
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0013
owner: shared
---

# Goal

Integrate deterministic missing-petrol-price repair into source-map generation, preserving effective definitions/diesel behavior, and deliver revised experimental packages with explicit later manual validation.

# Context

**Observed locally, 2026-10-18:** ProMods BC has a positive `petrol_price`, but the higher connection file omits it. Western Canada's six province definitions also omit it. **Documented — user report:** access/refueling works across many Canadian stations, while displayed gallons are invalid; the screenshot shows zero price. The engine default and exact quantity arithmetic are unverified. [TASK-0013](../done/TASK-0013-investigate-canadian-fuel-nan-display.md) establishes the evidence and limits.

**Documented — user authorization, 2026-10-18:** implement the evident missing field now as a necessary fix, retaining later manual verification of the whole symptom. The game/rig are closed for tonight. This supersedes the original BC-only diagnostic scope and any requirement to wait for gameplay before completing implementation; runtime acceptance stays in TASK-0007.

# Scope

- Audit effective country-unit fuel fields and their provenance against an explicit source order; distinguish missing, zero, nonfinite and positive values without silently selecting a fallback.
- Restore the highest valid lower-layer petrol price from the same country path/unit where available (BC: ProMods `1.502116`), keeping all winning connector fields including diesel `1.630`.
- Where no such value exists, apply the documented game-economy fallback: target diesel price multiplied by the stock Washington petrol/diesel ratio from installed ATS, rounded to eight decimals. Record all inputs/hashes and label the result estimated, not current retail pricing. Existing positive finite petrol prices are retained.
- Integrate with the source-map command and generate r2 packages; OtherMaps now needs its own price-definition package even though it has no station-sector edits. Do not confuse independent package counters with unique effective countries.
- Do not modify a live profile, install mods automatically, replace whole lower-priority country definitions, or claim runtime repair from static checks.

# Implementation Plan

1. GPT-6 Sol / medium implements the bounded audit and source-preserving diagnostic packaging with meaningful tests.
2. GPT-6.1 Sol / high reviews effective-source resolution, numeric validation and any proposed broader price policy.
3. Root integrates, documents source hashes/order and prepares the candidate for TASK-0007's user-run same-station comparison.

# Acceptance Criteria

- Audit results identify exact effective country paths, units, source versions and finite/missing petrol-price status.
- Missing-price fixes are reproducible and change only the petrol-price attribute; unsupported/ambiguous cases are reported.
- Static checks confirm preserved diesel price and all other source fields, deterministic packaging and immutable inputs.
- Implementation acceptance is static. Later manual validation requires a positive price, initial finite zero, finite changing quantity, measured tank/balance changes and a truck control; record this as pending under TASK-0007 and remind the user at handoff.
- No broader price policy is applied implicitly; define explicit provenance and version behavior before expanding beyond BC.

# Verification

2026-10-18: implementation and static generation complete under the user's explicit acceptance of deferred gameplay. [ADR-0007](../../architecture/decisions/ADR-0007-repair-missing-petrol-prices.md) records the selected policy; [r2 batch](../../reference/FUEL_FIX_BATCH_1_61_R2.md) records outputs and [manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md) keeps symptom/billing tests pending.

| Actual assignment | Model / effort | Reviewed result |
| --- | --- | --- |
| Country audit/editor, explicit policy, workflow/CLI integration and tests | GPT-6 Sol / high | Source-preserving edits, game-only reference, lower-layer restoration, complete coverage guards and 131 passing tests |
| Independent real-output review | GPT-6 Luna / medium | All seven archives, exact source hashes/bytes, r1 station identity, ratio calculation and combined country priority |
| Policy decision, batch generation, distribution bundle, documentation/reminder and integration | Root | Seven source commands with confirmed connector dependencies; verified distribution and persisted manual checks |

Checks performed:

- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: **131 passed**. Meaningful cases include country/source priority, exact non-petrol bytes and CRLF, arrays/comments, malformed/duplicate units, missing/incomplete policy, valid-price retention, zero/nonfinite/huge/tiny values, idempotence, lower-layer unit identity, game-only ratio isolation and blocked packaging.
- Seven source commands exited zero with complete station/price coverage and no blockers. All six historical station packages retain their original point counts; OtherMaps now generates a country-only package. Artifacts/audits are in `local_outputs/work/2026-10-18_01-27-24/`; output files in `local_outputs/generated/2026-10-18_01-27-24/`.
- **46** country additions across independent packages resolve to **27 distinct effective paths** in the confirmed source order. **45** additions use the documented game-ratio estimate; connector BC restores the lower ProMods value **1.502116** while retaining connector diesel **1.630**. Nineteen Mexican paths are supplied in both Reforma and higher-priority OtherMaps; counters must not be summed as unique coverage.
- Independent verification passed **7/7** ZIP CRCs, metadata/icon/resource hashes, positive finite prices, exact original source SHA and non-petrol raw byte/attribute preservation. Every r1 station gameplay resource in the six revised packages is byte-identical. All 27 combined effective country files preserve every non-petrol field. Exact reference inputs match the independent official Washington source hash. Full script/JSON: `local_outputs/work/2026-10-18_01-27-24/verification/`.
- The distribution ZIP contains exactly seven `.scs` packages and authored install/test instructions, manifest and checksums. Its CRC and each inner `.scs` SHA match the verified originals. The bundle is **62,601,876 bytes**, SHA-256 `68f3c5bb156e03be6882587dd0e31f3aad14d0fb5462c2503e13fb646a249974`.
- Eleven input archives and the one pre-existing sidecar retain their size/mtime identities. No source/archive, game installation, live mod directory, save, historical output or fatigue setting was changed. No manual game test occurred.
- A one-time thread reminder is scheduled for **2026-10-18 18:00 Europe/Warsaw**; AGENTS and the manual checklist require later handoff reminders until results arrive. No daily testing expectation or further tonight's gameplay was introduced.

Final integration checked 62 Markdown files, 446 relative links, 18 heading fragments and all 16 task metadata/status/dependency graphs: no errors. All 12 input identities are unchanged; 25 input/output/report paths pass Git exclusion checks, no supplied archives or generated assets are tracked, and `git diff --check` passes. QA evidence: `local_outputs/work/2026-10-18_01-27-24/documentation-qa.json`. Implementation is complete, while runtime symptom, purchases, truck/garage and reload validation stay in TASK-0007. No rest package is included; its source mechanism is separate.

# Links

- [Completed investigation](../done/TASK-0013-investigate-canadian-fuel-nan-display.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Canadian fuel display research](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md)
- [Metadata conventions](../../reference/MOD_METADATA.md)
