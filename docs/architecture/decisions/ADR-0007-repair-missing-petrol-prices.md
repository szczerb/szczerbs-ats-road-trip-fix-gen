# ADR-0007: Repair missing petrol prices with explicit provenance

## Context

Date: 2026-10-18. The user reports working car refueling in Canada but a zero unit price and invalid gallon quantity. The connector drops ProMods' valid BC `petrol_price`; six Western Canada province definitions omit it too. Alaska and nineteen Mexican country definitions also omit this field. Existing r1 packages only repair station interactions. The user explicitly authorizes the missing-field correction now and accepts later manual validation, having closed the game/rig for the night.

## Decision

Extend `generate-map-fuel` to audit and repair petrol prices in effective country definitions owned by its selected source archive. Retain valid positive finite petrol values. Prefer the highest lower-priority definition of the same mounted path and country unit with a positive finite petrol value. Thus the connector's BC file receives ProMods' `1.502116`, preserving its own diesel price `1.630`, position and other fields.

Where no such value exists, estimate petrol as the target's unchanged diesel price multiplied by the stock-game Washington ratio: `1.47197 / 1.92132`, rounded to eight decimals with `ROUND_HALF_UP`. Resolve this reference in the game-only stack, never through map overrides, and retain source hashes and all inputs. This is a transparent game-economy fallback, not a current retail-price claim. `--petrol-reference` permits an explicit alternative game country. The default reviewed inputs are pinned; drift or invalid/ambiguous data blocks complete generation.

Only add or replace `petrol_price` in the winning original country file. Keep all other source bytes/attributes, including comments and line endings where applicable. Preserve diesel behavior and every existing station resource. Combine price and station coverage; either kind of blocker prevents output. OtherMaps can now produce a price-only package even though it owns no fuel sectors. Do not sum duplicate country resources across independent package outputs as unique effective coverage.

Use revision **2** for this increment and make it the map-wide command default. Historical pinned commands keep their previous defaults; old outputs remain immutable. Source-specific metadata/icons and source-relative installation still apply. This extends ADR-0006 and the metadata conventions without relabeling historical artifacts.

## Consequences

Numeric/static checks can establish complete source-owned definitions and retained diesel attributes, but cannot establish the game's exact omitted-field fallback, NaN formula, billed amount, or UI/reload behavior. Keep those items explicitly pending in the [manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md) and TASK-0007. The user's acceptance of implementation without tonight's gameplay supersedes the former TASK-0014 runtime-completion requirement.

The fallback preserves relative local diesel pricing, but its petrol values are estimates. Broader realism or a new reference is a separate explicit policy change. Missing country definitions outside the selected source scope and other active mods' overrides remain separate stack inputs. Rest-area eligibility is a different feature and is not silently added to fuel packages.

See [price research](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md) and [TASK-0014](../../tasks/done/TASK-0014-audit-and-test-petrol-price-overrides.md).
