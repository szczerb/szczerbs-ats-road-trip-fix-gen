---
id: TASK-0041
title: Refactor station parking and investigate navigation icons
status: done
priority: high
repositories:
  - .
depends_on: [TASK-0039, TASK-0040]
owner: shared
---

# Goal

Complete a behavior-preserving, bounded reorganization of the experimental station-parking processor, then investigate why car parking icons may appear on the full-screen map but not in vehicle navigation. Prepare a minimal, evidence-supported visibility experiment where justified; distinguish a candidate from a confirmed fix and document the remaining mechanism uncertainties and smallest next comparison. Do not change candidate geometry or parking-location policy.

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
- [x] Navigation research separates full-screen map, phone, and vehicle navigation; uses effective resources and actual mod order; records a native positive control or explicitly says one is unavailable; and does not confuse icons with interaction/rest success.
- [x] A source-supported visibility candidate is implemented while preserving parking area, activation and original truck/bus inputs; the remaining phone/dashboard binding uncertainty and minimal manual comparison are explicit. No confirmed runtime repair is claimed.
- [x] Any candidate package has distinguishing labels at the start of its Mod Manager title, filename, and first description line; states method, test purpose, compatibility of alternatives, and exact sector/source replacement priority. Audits preserve fuel, UIDs, actions, and prefab contexts.
- [x] The documented later manual test uses the same location and vehicle, checks full-screen map and vehicle navigation at relevant zoom levels, and records the existing rest interaction separately. No gameplay success is claimed without the user's report.
- [x] No game/profile/install action, source-input mutation, merge, push, or publication occurs.

# Verification

**Observed locally — setup, 2026-10-19:** assigned worktree is `.`, branch `codex/gas-station-car-rest-research`, clean at `ed89e64` before this documentation setup. Stage 1 is verified: the focused 45 station tests and full 326-test suite pass; 57 moved function/class bodies match with imports excluded. CLI main/analyze/generate help text matches exactly; setuptools discovers `station_parking` and `station_parking.methods`; `workflow.REPO_ROOT` resolves to this worktree. Root independently compared three authored immutable fixture cases and both actual Dawson pinned inputs: complete canonical report/resource/SVG snapshots are byte-identical, fixture SCS archives are byte-identical, and the three actual planned resources per method match original delivered SCS bytes. The initial comparison harness needed JSON tuple/list normalization; direct complete snapshot file bytes were identical, so no source behavior change was required. Frozen source, comparison runners/results and CLI snapshots are under ignored `local_outputs/work/2026-10-19_19-33-14/reorganization-baseline/`. Commit `7eea2cf` records this structure-only milestone before any navigation code or artifact change. No game, profile, installation, merge, or push action is part of this assignment.


**Observed locally — navigation stage, 2026-10-19:** the effective runtime inventory found North America Background Map 5.3 (Workshop 3348711188) as the final map-data provider in A's logged mount block, overriding the stock masks used in the initial assessment. Root additionally checked B's persistent mount: B mounts at 00:03:44.783 and the same background at 00:03:44.865. The source omits category 25 at every tier. Its three includes do not restore masks. The known native car-only marker category and four named local 3D/minimap tiers support an isolated bit-25 experiment; exact phone/dashboard tier consumers and the reported B world-map icon despite omitted world masks remain unresolved. Native positive phone control, A phone visibility and zoom dependence remain unreported. See the canonical [navigation investigation and handoff](../../reference/CAR_PARKING_NAVIGATION_ICONS.md).

Root implemented the separate `python -m ats_road_trip.navigation_icons` recipe: it pins all four source-member hashes and the caller-declared ATS 1.61.3.18 baseline, edits only four literal mask tokens, and generates N1 NAV PARKING **r1** alongside one unchanged A/B control. It emits only `def/map_data.sii` plus metadata, retains source includes as dependencies, and rejects missing/updated input, no acknowledgment and output reuse. No existing CLI command or station-planning code changed in this stage. The global category setting may reveal all car-parking markers at local tiers, not only Dawson. It does not repair geometry or claim confirmed phone visibility.

**Verification:** six new authored-fixture tests pass, and the full suite passes **332 tests** with `PYTHONPATH=src python3 -m unittest discover -s tests -q`. Tests exercise exact byte/comment/CRLF preservation, unchanged world tiers and fuel bit, malformed/no-op masks, source/include/version drift and mid-read change refusal, a real archive write, immutable inputs, early N1/r1 identity, exclusive output creation and module CLI help. `git diff --check` passes. The source-only refactor's saved complete before/after fixture and actual-Dawson snapshots and CLI help files were rechecked byte-for-byte.

GPT-6 Luna/high independently audited the actual N1 SCS: four unique members, valid CRC, exact allowlist, all source pins, exact four-token-only diff, unchanged world masks and no A/B gameplay-path collision. Root repeated the exact payload check and built both effective background + station-control + N1 resource stacks: all **25 gameplay resources per A/B control** and all three source include resources remain byte-identical. Source controls retain their exact earlier archive hashes. Root also parsed the effective SII with includes: one `map_data : .map.data` unit, no attribute errors, identical non-mask attributes and exactly the expected eight mask values. The independent review raised a question about unclassified aliases; existing source-context evidence in the station research already establishes that these aliases are unclassified in the inspected original stack. N1 leaves every such resource unchanged and establishes no new runtime Courier result.

The 8,243-byte candidate is `local_outputs/generated/2026-10-19_19-47-49/n1-nav-parking-north-america-background-5.3-ats-1.61-r1-experimental.scs`, SHA-256 `97e36da9a440299ebe2f9e07b4aba65bd5f92dfda6e9b94a221865dbfd32c362`. Generation audit, executable payload-audit script/results and full-test log are under `local_outputs/work/2026-10-19_19-47-49/navigation-icons/`. N1 runs above all map-data providers, including the required background map, alongside exactly one A/B; that A/B still replaces Alaska r9 only, WCE r9 remains, and Alaska r2 is not separately enabled. N0 is N1 disabled, not a second file. The handoff covers full-screen map and whichever phone/dashboard interface the vehicle provides, matched zoom and separate prompt observation, without requiring a new B search or a native-site search.

**Delegation actually used:** GPT-6 Luna/high restructured station source/tests; GPT-6 Luna/medium set up task/ADR docs and inventoried active providers; GPT-6 Luna/high researched navigation inputs; GPT-6 Luna/medium authored the navigation handoff/current-state consolidation; GPT-6 Luna/high authored the six navigation regression tests; another GPT-6 Luna/high independently audited the generated artifact. Root reviewed the changes and evidence, wrote/integrated the navigation recipe, reran the full tests, repeated source/output and virtual-stack comparisons and owns final integration. No game launch, profile edit, live installation, source-input mutation, merge, push or publication occurred. Main checkout remains clean on master `445ef58`; experimental worktree/branch are retained.

**Completion boundary:** restructuring and the bounded research/candidate handoff are complete. Rendering in phone/dashboard navigation remains a user-run runtime check under [TASK-0007](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). No geometry, heuristic, distance/density policy or location expansion is part of this result.

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
