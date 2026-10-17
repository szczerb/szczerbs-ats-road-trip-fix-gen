---
id: TASK-0013
title: Investigate invalid Canadian passenger-car refueling quantities
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0011
  - TASK-0012
owner: agent
---

# Goal

Identify an evidence-backed cause or bounded hypothesis for invalid Canadian fuel quantities after the car-access fixes, and define the smallest discriminating validation without inventing engine behavior or silently changing prices.

# Context

**Documented — user report, 2026-10-18:** actual car refueling works at many visited ProMods Canada and Western Canada stations, but the gallon quantity is invalid; returning to the USA restores an initial zero. **Observed locally:** supplied screenshot `ats_20261018_001621_00.png` shows `Cena paliwa: $0,00`, `Galony: -nan(ind)`, and `Suma: $0`. This is a UI observation, not independent measurement of the completed purchase or balance change.

# Scope

- Inspect Canadian/US fuel-price, currency and unit definitions from supplied archives and installed reference data, respecting effective package priority.
- Review primary technical sources and distinguish documented attributes from engine-calculation hypotheses.
- Read the supplied screenshot and a bounded snapshot of the available game log. A later log must not be attributed to the earlier screenshot session.
- Preserve source archives, generated r1 packages, game/profile data and prices. No automatic live mod installation, save modification or speculative price policy.

# Implementation Plan

1. GPT-6 Luna / medium inventories Canadian country definitions and effective winners; own only timestamped ignored evidence.
2. GPT-6.1 Sol / high researches the mechanism and primary sources; own the canonical research reference and ignored evidence.
3. Root inspects screenshot/log evidence, reviews findings, updates validation/current state/task tracking and commits the verified research milestone.

# Acceptance Criteria

- Record the user's expanded runtime result and the invalid display with correct scope and exact text.
- Identify exact source fields/files/values and relevant effective overrides, or document the missing evidence.
- Separate a plausible NaN calculation from any independently established engine implementation.
- Define a minimal validation and price-policy boundary; do not call an untested candidate a confirmed repair.
- Relative links/task metadata and artifact exclusions pass; sources/game/profiles remain unchanged.

# Verification

2026-10-18: completed as a research milestone; no price candidate or confirmed runtime repair is claimed. [Canonical findings](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md) record exact source versions, field values, source priority, primary references, competing mechanisms and the proposed BC test.

| Actual assignment | Model / effort | Reviewed result |
| --- | --- | --- |
| Country-definition inventory and effective winners | GPT-6 Luna / medium | Eleven inputs, 316 selected definitions, source hashes/raw evidence, six WCE provinces and BC override |
| Mechanism/primary-source research and canonical reference | GPT-6.1 Sol / high | Eight independently checked ZIP country files, six fresh official/cache comparisons, ranked causes and one-field test |
| Screenshot/log inspection, installed-output checks, evidence integration and documentation | Root | Original PNG and later-session boundary, all six installed archive fingerprints, no country/economy resources in r1 fixes |

Verification performed:

- Read original-resolution screenshot through WSL. Visible values are price `$0,00`, quantity `-nan(ind)` and total `$0`; the frame prompts the user to hold refuel. No tank level or completed transaction amount is inferred. SHA-256: `c6a7baae037760f658b24f9b42af638c73b80a1f8b152af7ae6dd26d07c3aec7`.
- Snapshot the available log read-only. It was created at **00:20:38**, after screenshot **00:16:21**, and records ATS 1.61.3.18 with 29 active mods. It confirms connector priority and active r1 filenames; all six installed files match the delivered archives byte-for-byte. No targeted price/NaN diagnostics appear. This is later-session context, not the exact screenshot setup.
- Inspected all eleven supplied archives for relevant country files; five contain none. Preserved 316 selected definitions and a source-order winner table under `local_outputs/work/2026-10-18_01-04-53/canada-country-inventory/`. ProMods' `def/country/bc.sui` has `petrol_price: 1.502116`; the higher connection file omits it. Six WCE province definitions also omit the field; `bc` and `kbritcolum` are separate units. Alaska/Reforma omissions are broader static leads, not reported gameplay failures there.
- Independently reread both BC files and six WCE province files from source ZIPs; fresh extraction from installed `def.scs` confirmed the six selected official definitions/cache copies are byte-identical. Reference/source notes and hashes are under `local_outputs/work/2026-10-18_01-04-55/nan-research/`.
- Checked the six generated r1 archives: none contains country/economy definitions. The country price omission is a source-data compatibility gap left outside their station-access transformation. Microsoft documentation identifies the NaN notation; a first-person SCS-forum report independently corroborates the new-field migration risk. The engine's default/fallback and exact `0/0` formula remain hypotheses.
- Defined a BC-only diagnostic preserving the winning connector file and adding the existing ProMods petrol price. No invented province prices, definition patch, generated station archive, installation, save edit or in-game action occurred. [TASK-0014](../done/TASK-0014-audit-and-test-petrol-price-overrides.md) holds implementation and validation scope; TASK-0007 retains runtime checks.
- Integration checks passed: **56 Markdown files**, **393 relative links**, **19 local heading fragments**, **14 task metadata/status/dependency records** with no cycles, and **15 ignored artifact paths**. All eleven source archive and one sidecar size/mtime identities match the pre-research snapshot. `git diff --check` passes and no supplied/generated assets are tracked. No utility code changed, so the 116-test code baseline was not rerun for this research/documentation-only milestone.

Root evidence snapshot: `local_outputs/work/2026-10-18_01-04-41/canada-ui-root/`. Remaining evidence requires a confirmed affected BC pump, same-station one-field comparison, finite displayed quantity, measured tank/payment changes and a truck control. Other active Workshop country/UI/economy overrides remain uninspected; source winner claims are limited to the supplied map stack.

# Links

- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Validation results](../../reference/VALIDATION_RESULTS.md)
- [Connector generation](../done/TASK-0012-inspect-and-fix-map-connectors.md)
- [Canadian fuel display research](../../reference/CANADA_FUEL_DISPLAY_RESEARCH.md)
- [Proposed audit and diagnostic](../done/TASK-0014-audit-and-test-petrol-price-overrides.md)
