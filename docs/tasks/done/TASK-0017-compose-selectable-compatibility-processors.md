---
id: TASK-0017
title: Compose selectable compatibility processors
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0014
owner: shared
---

# Goal

Separate source-map analysis and generation by compatibility topic, selected through an explicit enum configuration, while preserving the existing fuel command and composing local rest edits safely.

# Context

**Documented — user direction, 2026-10-18:** fuel, rest and eventually Courier Jobs should be independent processors selected with a list of enum values. Rest has a location-dependent 1,000-unit rule and must not change the shared truck action globally. Existing fuel output also edits sectors and private prefab descriptors, so independent byte dictionaries cannot be combined by blind overwrite.

# Scope

- Add validated configuration for `fuel` and `rest`, with `courier` reserved and explicitly rejected until implemented.
- Retain `generate-map-fuel` and its fuel/price behavior. Provide a general command with explicit processor selection and rest radius.
- Run fuel before rest in canonical order; compose shared resources, preserve original ownership, and block the complete output when any enabled processor reports incomplete coverage.
- Make filenames, manifest names, descriptions and reports accurately identify enabled topics. Preserve historical gas-only branding; do not reuse a gas-labelled icon automatically for rest-containing output.
- Preserve original inputs, prior artifacts and live game/profile data. No runtime validation is implied.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Processor enum/configuration, pipeline, map workflow and CLI regression tests | GPT-6 Sol / high | processors.py, bulk_run.py, cli.py and related tests |
| Local rest planner integration | GPT-6.1 Sol / high | TASK-0016 rest module and tests |
| Package topic metadata, documentation, independent integration and commit | Root | mod_writer.py, metadata tests and authored references |

# Acceptance Criteria

- Fuel-only, rest-only and both selections are deterministic; duplicate, empty, unknown or unimplemented selections fail clearly.
- Disabled processors do not analyze or emit changes. Fuel prices remain part of the fuel processor.
- Composition retains both features on shared resources; incompatible output/collisions or incomplete coverage prevent package publication.
- Historical fuel command/default revision remain stable; generic output is experimental with topic-accurate metadata and a distinct filename.
- Tests cover selection, order independence, blockers, metadata and shared-resource preservation. Real-input evidence and any unsupported scope are recorded honestly.

# Verification

2026-10-18: implementation/static integration complete; manual gameplay acceptance remains separate.

- GPT-6 Sol / high implemented enum/configuration, pipeline, workflow/CLI and related tests. GPT-6.1 Sol / high integrated the rest planner under TASK-0016. Root added topic metadata and tests, reviewed composition, documented the user-approved boundary approximation and ran actual generation. GPT-6 Sol / medium independently verified the resulting archive.
- **179 tests pass**, including disabled processor isolation, explicit/duplicate/unknown/unimplemented selection, canonical order, empty/incomplete coverage blockers, undeclared collisions, actual rest-planner overlay composition and topic-specific metadata. The legacy fuel command retains its default revision 2; generic CLI requires explicit topics and defaults to revision 3.
- The public workflow generated the combined WCE candidate with **510 gameplay resources**, no blockers, selected topics `fuel`/`rest` and the r3 Map Compatibility Fix title. An ignored integration adapter reused read-only cached extraction bytes from the same pinned archives; package identities/order and cache hashes were checked, with no product cache dependency. [Results and reproduction](../../reference/COMPATIBILITY_PROCESSORS.md).
- Independent output verification confirms retained r2 fuel resources/country prices and deliberate rest composition on **118 shared sector paths**, plus five rest-only sector paths. Only selected model/action tokens change in those sectors; original fuel services and nodes remain identical. The shared action definition is untouched.
- Archive CRC, metadata/report/resource hashes and source preservation pass; output remains experimental and gameplay-unverified. Evidence: `local_outputs/work/2026-10-18_02-18-17/verification/`; tests: `local_outputs/work/2026-10-18_02-01-14/tests-final.log`.

Final integration checked 65 Markdown files, 477 relative links, 18 heading fragments and all 17 task metadata/status/dependency graphs with no errors. Twelve input identities are unchanged, 16 artifact paths pass Git exclusions, no supplied/generated assets are tracked, and whitespace checks pass. QA: `local_outputs/work/2026-10-18_02-01-14/documentation-qa.json`. No installation, profile changes, remote configuration or push occurred.

# Links

- [Local rest implementation](TASK-0016-prepare-rest-eligibility-experiment.md)
- [Rest research](../../reference/PASSENGER_CAR_REST_RESEARCH.md)
- [Processor and proximity decision](../../architecture/decisions/ADR-0008-compose-processors-and-local-rest-polygons.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
