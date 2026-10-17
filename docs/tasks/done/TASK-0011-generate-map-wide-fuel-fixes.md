---
id: TASK-0011
title: Generate deterministic map-wide passenger-car fuel fixes
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0009
  - TASK-0010
owner: agent
---

# Goal

Provide a single-command deterministic generator which adds missing co-located car refueling to truck fuel points in the supplied ATS Expansion, Reforma, ProMods Canada, Western Canada and Alaska maps, preserving trucks and reporting coverage accurately.

# Context

The user reports successful same-position car/truck refueling with the Helena sample, and now authorizes whole-map generation. The former pinned single-point writer is insufficient for discovery, multi-point stations and arbitrary sectors. Source archives are immutable. The user is supplying missing ProMods inputs; other map/resource packages are already present.

# Scope

- Inspect map sectors and referenced prefab definitions/descriptors from an explicit effective stack; support multiple fuel points and already-existing car counterparts.
- Generalize byte-preserving sector edits with validated item boundaries, nodes, parents, counts and auxiliary metadata. Detect unsupported layouts rather than presenting skipped sites as complete coverage.
- Add one source-map command, descriptive filenames, chosen icon family, provenance, coverage and source/load-order assumptions. Generate five experimental packages if coverage/data permit; record concrete blockers otherwise.
- No LLM-generated gameplay patches: all assets/edits derive from deterministic code. No game/profile installation or automatic market/save modification.

# Implementation Plan

1. GPT-6 Luna / medium inventories original inputs/dependencies; GPT-6 Sol / high reviews prefab/service matching and old PPD versions; GPT-6.1 Sol / high implements the bounded general sector reader with explicit file ownership.
2. Root integrates a map-wide planner, source/dependency/reference preparation, command interface and regression tests; review delegate code and uncertain cases.
3. Run real complete inventories, validate all changed records/reference counts and preserved originals, report already-supported/changed/blocked points and cross-map sector conflicts.
4. Generate deterministic packages using descriptive names and map-specific icons. Record checks, remaining gameplay scope and commit coherent milestones.

# Acceptance Criteria

- One command selects source archive(s), resolves versioned reference data/dependencies and generates the corresponding small override package without hand-authored per-station recipes.
- All eligible truck fuel points have car counterparts; existing car/truck points remain, and ambiguous/unsupported coverage prevents an unqualified complete result.
- Outputs exist for each available requested map, with accurate map names, game/revision version and matching icon labels.
- Meaningful synthetic tests cover multiple points, partial existing car support, unchanged original bytes, source/package drift, malformed sectors and deterministic packaging.
- Real input/coverage/resource checks and documentation/task/link checks pass; inputs, game, profiles and historical samples are unchanged.

# Verification

2026-10-17: complete for the nine supplied archives and installed ATS 1.61.3.18 baseline. Five source-map CLI invocations produced complete experimental r1 packages; coverage blockers are zero. See [batch results](../../reference/FUEL_FIX_BATCH_1_61_R1.md) for exact output fingerprints, counts and source-relative priority.

Actual delegation with shared-checkout file ownership:

| Assignment | Model / effort | Result |
| --- | --- | --- |
| Input/dependency inventory, HashFS v1/deep and disk-backed staging, artifact policy, independent output review | GPT-6 Luna / medium | Nine inputs, safe bounded caches, all five outputs independently verified |
| Geometric matching, origin/grade/partial cache handling, one-source workflow | GPT-6 Sol / high | Matching and run workflow; two real Reforma tilt regressions resolved |
| Sequential sector/layer reader, all-map layout coverage, bulk regression tests and orphan review | GPT-6.1 Sol / high | All 2,440 files parse; source-pinned structural evidence and tests |
| Planner, CLI integration, legacy PPD upgrade, metadata/artwork, graph validation, documentation and final verification | Root | Reviewed delegate code and actual results; generated/published verified collection |

Verification performed:

- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: **111 passed**. Coverage includes complete multi-point edits, partial existing car data, origin/shuffled matching, longitudinal/cross-slope, ambiguous/unknown layouts, typed source units and uppercase model-token lookup, legacy semaphores, visibility/layers, narrow orphan FuelPump handling, deterministic repeated planning, source drift and failure audits, and unchanged original bytes.
- All **1,220 .base + 1,220 .aux** inputs parsed sequentially; 107 exact empty legacy .base files classified without accepting nonempty old layouts. One 32,238-item Reforma aux exceeded the old per-member limit and passed the explicit 64 MiB bounded read. HashFS v1 ProMods assets/models use deep discovery and selected extraction, not an empty-list fallback.
- Real generated points: ATS Expansion **894** (41 garage), Reforma **954** (46), ProMods **102** (11), Western Canada **288** (30), Alaska **43** (5), total **2,281** (133 garage). Changed sector counts 202/185/28/118/18. Complete audits accompany each source invocation. The first ATS run's boundary FuelPump mismatch and two Reforma tilt blockers were investigated and coded with regression tests before publishing; no failed partial output was handed off.
- Independent review verified every original source/output sector SHA, every original Service/FuelPump/node byte record, all generated resource/icon hashes, ZIP CRCs, names/author/version, UID ordering and all **2,281** exact source-transform/new-parent/node correspondences. All five outputs have zero review findings. Root independently repackaged each report/resources/metadata through the writer and obtained byte-identical archives; final collection copies retain those hashes.
- Runtime output collection: `local_outputs/generated/2026-10-17_22-46-14/`; rechecks and collection manifest verification: `local_outputs/work/2026-10-17_22-46-14/release-verification/`. Detailed independent script/JSON: `local_outputs/work/2026-10-17_22-11-10/verification/`. No supplied .scs, game installation, live mod folder or profile was changed. At user request only, pre-existing standalone Zone.Identifier sidecars were moved into run work storage. All copied assets, source caches, generated archives, full reports and tools remain ignored.
- Pairwise source-sector intersections are ATS Expansion–Western Canada **6**, Alaska–Western Canada **3**, ProMods–Western Canada **15**; other pairs zero. Each fix must stay immediately above its own source, preserving map priority; extra connection/compatibility patches remain explicit inputs.
- Reading path, relative links, eleven task metadata/status/dependency records, cycles, Git artifact exclusions and diff whitespace checked. Five known map-labelled C artwork exports decode and meet JPEG 276x162.

Completion covers deterministic generation and static full-source coverage, not full-map gameplay. The previous single Helena pair remains the only user-tested dual-vehicle fixture. Garages (including ownership/prices), the nearer four-point Helena station, other maps and reloads are explicit TASK-0007 comparisons; courier behavior is unchanged.

# Links

- [Previous overlapping sample](../done/TASK-0009-build-overlapping-fuel-pair.md)
- [Metadata convention](../../reference/MOD_METADATA.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
