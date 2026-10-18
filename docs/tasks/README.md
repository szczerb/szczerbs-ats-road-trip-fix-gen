# Task Board

Use the [workflow](../project/HOW_TO_WORK_WITH_TASKS_AND_ADRS.md) and [task template](../templates/TASK_TEMPLATE.md). Status and directory must agree; IDs are stable, dependencies use IDs, and blockers belong inside tasks.

## Active

- [TASK-0007: Validate experiments in game](active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) — user reports successful car and truck refueling with overlapping sample 2; reload, other locations and courier validation remain open.

## Backlog

No unstarted tasks.



## Done

- [TASK-0026: Unify Job Types Compat Mustang naming](done/TASK-0026-unify-job-types-compat-mustang-branding.md) — consistent filenames/metadata/priority labels, r7/r3 batch and unchanged gameplay/icons; 246 tests and independent archive review.

- [TASK-0025: Refresh icons and player descriptions](done/TASK-0025-refresh-mod-icons-and-player-descriptions.md) — approved M2D/J3C artwork, readable priority descriptions, final r6/r2 batch, 246 tests and independent payload checks.

- [TASK-0024: Deliver overnight test mods](done/TASK-0024-deliver-overnight-test-mod-batch.md) — eight reviewed mods, 233 tests, effective-stack/namespace checks and one ZIP with installation/test instructions. Manual acceptance remains TASK-0007.

- [TASK-0019: Preserve contexts for generated prefab aliases](done/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md) — integrated exact-tag preservation; all 14 WCE Company-parent aliases and 380 unchanged Company records verified.
- [TASK-0023: Build configurable courier eligibility tooling](done/TASK-0023-build-configurable-courier-eligibility-generator.md) — standalone source-pinned generation and reporting, reviewed 58-job preset, nine transfers unchanged, independently verified r0.

| Task | Outcome |
| --- | --- |
| [TASK-0001: Initialize project](done/TASK-0001-initialize-project.md) | Documentation, references, inventory, and workflow |
| [TASK-0002: Establish reference data/extraction](done/TASK-0002-establish-reference-data-and-extraction.md) | Installed baseline, provenance, and verified HashFS access |
| [TASK-0003: Investigate courier compatibility](done/TASK-0003-investigate-courier-compatibility.md) | Context mechanism, counterevidence, concrete alias candidate |
| [TASK-0004: Investigate car refueling](done/TASK-0004-investigate-car-refueling-compatibility.md) | GAS flag evidence, placed station/service, bounded descriptor experiment |
| [TASK-0005: Design first generator increment](done/TASK-0005-design-first-generator-increment.md) | Python inspection/experimental patch design and validation boundaries |

- [TASK-0006: Build inspector and experimental generators](done/TASK-0006-build-inspector-and-experimental-generators.md) — 39 tests and real-input static checks passed; experimental packages and handoff produced.

- [TASK-0008: Prepare starter-area samples](done/TASK-0008-prepare-starter-area-sample.md) — effective garage comparison, pinned single-pump generator, Helena-area/Great Falls packages, and 43 passing tests.

- [TASK-0009: Build overlapping fuel pair](done/TASK-0009-build-overlapping-fuel-pair.md) — source-pinned same-position truck/car candidate, original truck records preserved, 48 tests passed; runtime checks remain TASK-0007.

- [TASK-0010: Brand gas station fix packages](done/TASK-0010-brand-gas-station-fix-packages.md) — requested metadata, selected icon C, identical sample-2 gameplay payload and 51 passing tests.

- [TASK-0011: Generate map-wide fuel fixes](done/TASK-0011-generate-map-wide-fuel-fixes.md) — five complete r1 packages, 2,281 new car points, original truck records retained, 111 passing tests and independent full-output checks.

- [TASK-0012: Inspect and fix map connectors](done/TASK-0012-inspect-and-fix-map-connectors.md) — connector-derived 50-point Western Canada–ProMods fix, no station fix needed for OtherMaps, explicit source order and 116 passing tests.

- [TASK-0013: Investigate Canadian fuel quantities](done/TASK-0013-investigate-canadian-fuel-nan-display.md) — confirmed BC override drops ProMods' petrol price; WCE province fields also missing; strong cause hypothesis and bounded diagnostic, no price patch generated.

- [TASK-0014: Repair missing petrol prices](done/TASK-0014-audit-and-test-petrol-price-overrides.md) — seven r2 packages, 27 effective country paths, r1 station payloads retained, 131 tests and independent checks; manual symptom/billing validation pending.

- [TASK-0015: Investigate car rest areas](done/TASK-0015-investigate-passenger-car-rest-areas.md) — separate vehicle-filtered polygon actions and two concrete truck-stop placements; no rest package or gameplay repair claimed.

- [TASK-0016: Implement proximity-filtered rest eligibility](done/TASK-0016-prepare-rest-eligibility-experiment.md) — bounded source-plus-halo rule, private truck/bus/car action, 202 WCE additions with explicit boundary limits and manual testing pending.

- [TASK-0017: Compose selectable compatibility processors](done/TASK-0017-compose-selectable-compatibility-processors.md) — enum/CLI selection, atomic composed output, accurate topic metadata, 179 tests and independently verified WCE fuel/rest package.

- [TASK-0018: Report courier company locations](done/TASK-0018-report-courier-company-locations.md) — read-only selectable analysis, shared-marker evidence, 194 tests and real ATS Expansion/WCE patch reports; existing alias-context risk tracked separately.

- [TASK-0020: Research courier quantities and discovery](done/TASK-0020-research-courier-market-job-quantity.md) — sourced online findings, unproven global-budget hypothesis, concrete stock Mustang restrictions and controlled future discovery tests.

- [TASK-0021: Mustang cargo exclusions and eligibility-mod feasibility](done/TASK-0021-research-mustang-cargo-and-eligibility-mod.md) — two sequential Luna passes, 95 sedan-only definitions reviewed, class-level standalone-mod proposal and explicit physical/runtime unknowns.

- [TASK-0022: Plan practical courier eligibility tooling](done/TASK-0022-plan-practical-courier-eligibility-tooling.md) — explicit human cargo groups, source-pinned TOML, 58 proposed additions, transfer preservation and implementation-ready checks.

Courier Jobs and car refueling retain equal research priority. Completed research and static tests do not complete the pending gameplay-validation task.
