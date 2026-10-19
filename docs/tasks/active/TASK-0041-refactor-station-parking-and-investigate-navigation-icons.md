---
id: TASK-0041
title: Refactor station parking and investigate navigation icons
status: active
priority: high
repositories:
  - .
depends_on: [TASK-0039, TASK-0040]
owner: shared
---

# Goal

Complete a behavior-preserving, bounded reorganization of the experimental station-parking processor, then investigate why car parking icons may appear on the full-screen map but not in vehicle navigation. Implement a minimal, evidence-supported marker-representation fix and test package if the mechanism is established; otherwise document the precise blocker and smallest next comparison. Do not change candidate geometry or parking-location policy.

# Context

**Observed locally — 2026-10-19:** [TASK-0039](../done/TASK-0039-research-gas-station-car-rest.md) produced explicit `painted_bays` and `unmarked_geometry` Dawson alternatives; [TASK-0040](../done/TASK-0040-identify-dawson-test-and-label-variants.md) correlated the successful rest interaction with A / `painted_bays`. The user's report confirms finding that interaction, but does not enumerate fatigue, reload, or vehicle-navigation icon results. For B / `unmarked_geometry`, the user reports an icon on the full-screen map, no usable rest position found, and no icon in vehicle navigation; the proposed overlap with building/furniture is a **Hypothesis** and is outside this task's scope to resolve by geometry edits.

**Unknown:** whether A's icon appears in vehicle navigation, whether native unmodified parking is a positive navigation control, or whether behavior changes with navigation type, zoom, vehicle, effective map assets, or UI/model mods. Existing reports of missing navigation icons at other parking and fuel points do not establish a shared cause. The active Real companies, gas stations & billboards 4.02.01 mod replaces the inspected station model, and the supplied eleven-map sample is not the user's complete runtime stack. The research must distinguish full-screen map, phone navigation, in-vehicle navigation, and any other relevant interface, and use effective resources and actual priority where available.

The task continues on `codex/gas-station-car-rest-research` in its retained worktree at base `ed89e64`; inspect the live tree before editing. Do not recreate the experiment from master, reset, move the worktree, merge, push, or publish.

# Scope

- Refactor only station-parking code into `src/ats_road_trip/station_parking/`, with boundaries matching actual responsibilities: workflow/resource handling, candidate methods, shared validation, result selection, diagnostics/visualization, and trigger writing. Keep the implementation small; do not create empty layers or a plugin framework.
- Preserve CLI commands/argument meaning, configuration formats, deterministic candidate selection, IDs, geometry, source protections, write behavior, setuptools discovery, and test discovery. Pay special attention to `__file__`-relative paths and output placement.
- Complete this refactor and its verified commit before changing marker behavior.
- Investigate navigation icon inputs and classification using code, current resources, logs, effective mod stack, and native controls where evidence exists. Compare the minimum diagnostic set: a native parking point known to show in the target navigation, A / painted bays, and B / unmarked geometry. If no positive phone or vehicle-navigation control is confirmed, record that absence.
- If evidence establishes a repair, change marker representation only as needed and prepare a small, clearly labelled experiment for later user testing. Preserve A/B meaning, area and activation conditions, full-screen-map display, original truck/bus interactions, source fuel/UID/context data, and exact sector replacement scope. If not, document the specific blocker and next test instead of presenting speculation as a fix.
- Add or update the dedicated navigation-icon report [CAR_PARKING_NAVIGATION_ICONS.md](../../reference/CAR_PARKING_NAVIGATION_ICONS.md). Preserve prior full-screen-map findings as separate historical evidence; the navigation issue does not undo the user's two-town confirmation of r9 icons on that map.
- Do not adjust parking heuristics, move/enlarge areas, select new stations, reposition B's trigger, integrate with the existing rest processor, or change distance/density rules. Do not treat an icon as proof of working rest or fatigue recovery.
- Do not launch ATS, install mods, modify profiles, or change source inputs. Keep new work artifacts in ignored timestamped `local_outputs/` directories. Leave older artifacts intact.

# Implementation Plan

1. Inspect the retained worktree and read the station-parking source, existing tests, `TASK-0039`, `TASK-0040`, [ADR-0018](../../architecture/decisions/ADR-0018-isolate-source-pinned-station-parking-poc.md), and the relevant reports. Establish behavioral baselines for pinned inputs.
2. Move and clarify only station-parking module responsibilities. Verify imports, CLI behavior and package discovery; run the full repository checks and compare generated resources for identical pinned inputs. Commit the refactor as its own milestone before icon changes.
3. Inspect how marker data feeds each navigation surface, audit the effective station/model/map resources and priority, and assemble the smallest supported native/A/B comparison. Record proven facts, hypotheses, unknowns, versions, and source dates.
4. Implement and package the smallest justified representation fix if possible, with meaningful regression checks and an exact priority/test handoff; otherwise record the blocker and minimal next test. Audit output/source preservation and retain static versus runtime claims separately.
5. Update the task, current state, task board, ADR index, and navigation report with actual outcomes and verification. Keep experimental changes on this branch; do not merge or push.

Delegation plan / recorded assignments: root owns code refactor, integration, final verification and navigation reference report; GPT-6 Luna / high effort owns bounded station-parking code restructuring with explicit source-module ownership. GPT-6 Luna / high effort owns read-only navigation mechanism/resource research and evidence, with report findings returned to root. GPT-6 Luna / medium effort owns this task/ADR/board/current-state documentation setup. Root reviews each result and retains integration ownership. No delegated assignment authorizes a merge, push, release, game launch, installation, or profile change.

# Acceptance Criteria

- [x] Station-parking modules have clear responsibilities and a small, understandable dependency flow from effective station data through candidate/check outcomes and selection to trigger writing.
- [x] The refactor preserves CLI/config semantics, deterministic choices/IDs/geometry, writing safeguards and output paths; imports, CLI, setuptools package discovery, and test discovery work.
- [x] Full required checks pass, and pinned-input outputs demonstrate no unintended change to geometry, identifiers, or gameplay resources. The refactor is committed separately before marker changes.
- [ ] Navigation research separates full-screen map, phone, and vehicle navigation; uses effective resources and actual mod order; records a native positive control or explicitly says one is unavailable; and does not confuse icons with interaction/rest success.
- [ ] A marker-representation repair is implemented only if supported by evidence, preserving the parking area, activation and original truck/bus behavior. Otherwise, a precise blocker and minimal next test are documented.
- [ ] Any candidate package has distinguishing labels at the start of its Mod Manager title, filename, and first description line; states method, test purpose, compatibility of alternatives, and exact sector/source replacement priority. Audits preserve fuel, UIDs, actions, and prefab contexts.
- [ ] The later manual test uses the same location and vehicle, checks full-screen map and vehicle navigation at relevant zoom levels, and confirms the existing rest interaction separately. No gameplay success is claimed without the user's report.
- [ ] No game/profile/install action, source-input mutation, merge, push, or publication occurs.

# Verification

**Observed locally — setup, 2026-10-19:** assigned worktree is `.`, branch `codex/gas-station-car-rest-research`, clean at `ed89e64` before this documentation setup. Stage 1 is verified: the focused 45 station tests and full 326-test suite pass; 57 moved function/class bodies match with imports excluded. CLI main/analyze/generate help text matches exactly; setuptools discovers `station_parking` and `station_parking.methods`; `workflow.REPO_ROOT` resolves to this worktree. Root independently compared three authored immutable fixture cases and both actual Dawson pinned inputs: complete canonical report/resource/SVG snapshots are byte-identical, fixture SCS archives are byte-identical, and the three actual planned resources per method match original delivered SCS bytes. The initial comparison harness needed JSON tuple/list normalization; direct complete snapshot file bytes were identical, so no source behavior change was required. Frozen source, comparison runners/results and CLI snapshots are under ignored `local_outputs/work/2026-10-19_19-33-14/reorganization-baseline/`. The structure-only commit is the next integration action; navigation research, any justified patch/package and final task closure remain pending. No game, profile, installation, merge, or push action is part of this assignment.

# Links

- [TASK-0039: Research gas-station car rest areas](../done/TASK-0039-research-gas-station-car-rest.md)
- [TASK-0040: Identify Dawson test and label variants](../done/TASK-0040-identify-dawson-test-and-label-variants.md)
- [ADR-0018: Isolate source-pinned station-parking experiments](../../architecture/decisions/ADR-0018-isolate-source-pinned-station-parking-poc.md)
- [ADR-0019: Separate station-parking workflow, proposal, validation, and output responsibilities](../../architecture/decisions/ADR-0019-station-parking-module-boundaries.md)
- [Gas-station car-rest research](../../reference/GAS_STATION_CAR_REST_RESEARCH.md)
- [Gas-station car-rest PoC handoff](../../reference/GAS_STATION_CAR_REST_POC_HANDOFF.md)
- [Car parking icon investigation](../../reference/CAR_PARKING_ICON_INVESTIGATION.md)
- [Car parking navigation icons](../../reference/CAR_PARKING_NAVIGATION_ICONS.md)
- [Mod metadata contract](../../reference/MOD_METADATA.md)
- [Compatibility processors](../../reference/COMPATIBILITY_PROCESSORS.md)
