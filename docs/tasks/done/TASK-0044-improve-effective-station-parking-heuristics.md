---
id: TASK-0044
title: Improve parking selection from effective station geometry
status: done
priority: high
repositories: [.]
depends_on: [TASK-0039, TASK-0040, TASK-0041, TASK-0042]
owner: shared
---

# Goal

Implement deterministic, explainable station-parking improvements, validate an actual marked USA case and the effective Dawson replacement model, and deliver limited source-pinned PoCs for later gameplay testing. An unresolved activation rule may be documented with a discriminating test; a missing required real case does not complete the goal.

# Context

**Observed locally / user report (2026-10-19):** Both historical A LINES and B GEOMETRY produce a rest prompt. B has a narrow, unintuitive working position. N2 restores both navigation icons in the Mustang. Effective Real Companies geometry removes the stock Chemron separator cluster. Empty frontage does not prove sufficient pump access; the whole strip may be unsuitable. See the canonical feedback reference.

# Scope

- Existing experimental branch/worktree only; main checkout remains unchanged.
- Effective model-state pins, candidate validation/ranking, diagnostics, two actual cases, source/resource preservation and manual handoff.
- No map-wide integration, game operation, installation, publication, merge or push. TASK-0043 remains deferred.

# Implementation Plan

1. Freeze comparable source/results and run the existing test suite.
2. Research activation independently of geometry changes; inspect an effective marked station from main USA.
3. Resolve visible model parts using pinned model-state data; preserve historical schema-1 controls.
4. Improve candidate access checks, deterministic ranking and diagnostic explanations. Verify actual effective cases, preserve payloads, and generate distinctly labelled revisions where evidence permits.
5. Record results, limitations, ADR/interface decisions and manual alternatives.

Delegation: `research_rest_activation_rule` (gpt-6.1-sol/high), read-only activation/source research; `find_effective_marked_station` (gpt-6-luna/high), read-only concrete marked-case inventory; `effective_model_state` (gpt-6-luna/high), only new `model_state.py` and its authored tests. Root owns integration and reviews all results. Subsequent bounded assignments: the resolver agent also owned `workflow.py`/its tests, then `features.py`/its tests, reviewed integration and independently audited E. The activation agent owned new access/ranking and curbside modules/tests, then independent C payload audits. The inventory agent verified the operational native control and its schema comparison. Root corrected parallel-entry consistency and concave-wall normals after review, independently checked variant tokens, reconciled effective texture providers, and compared current native control to the full installed-stack run.

# Acceptance Criteria

- Source-pinned effective model/variant selection fails closed on drift and ambiguity.
- Real marked station and effective unmarked Dawson evaluated, with comparable old/new diagnostics and documented evidence limits.
- Explainable deterministic ranking, circulation/occupancy checks and meaningful authored fixtures.
- New behavior packages have new revisions and early variant identities; old A/B and independent N2 retained.
- Full required tests, actual archive and effective-composition preservation audits pass; runtime improvement explicitly pending user validation.

# Verification

- Started 2026-10-19 from `d7b043b`; initial branch clean. Baseline source archive and run evidence: `local_outputs/work/2026-10-19_21-22-36/heuristic-baseline` (ignored, local-only).
- Exact frozen pre-change suite: 336 tests (supporting icon assets required by tests were supplied from the same HEAD). The live baseline including the first six resolver tests passed 342.
- Complete actual historical schema-1 A/B reports, SVG and resource SHA-256 snapshots remain identical.
- Schema-2 effective Dawson: zero painted banks; 13 unmarked candidates; preliminary survivor is unchanged B. This initial stage is superseded by the raised-boundary and operational-control results below.
- [Effective-state decision](../../architecture/decisions/ADR-0020-plan-parking-from-effective-model-state.md); [activation/effective research](../../reference/STATION_PARKING_HEURISTICS_1_61.md).
- Raised-boundary proposals implemented; concave winding and angled proxy orthogonality verified. Parallel approaches were corrected after independent review to use longitudinal entry areas. Clearance ranking includes bounded, centimetre-rounded surplus over exclusions.
- Marked operational native control validated at `sec-0010+0008`, UID `0x6032dc12c1350001`: three service matches, two painted bays fully inside native car group 1, no output. Schema comparisons retained in `local_outputs/work/2026-10-19_21-53-22/native-control-validation/`.
- First full-stack C r1 generated at `local_outputs/generated/2026-10-19_21-44-53/`; intermediate, superseded by C r2 ranking refinement. Final C r2 run uses `2026-10-19_21-59-06`; it passes all 50 independent package checks plus 6 clearance/ranking checks.
- E CONTACT r1 independently verified: 24/25 gameplay members exact; four flag bytes in the last member, unchanged geometry/services/actions. Report in `local_outputs/work/2026-10-19_21-58-02/e-contact-independent-audit/`.
- User clarification: potentially inactive but visually valid stations are a deferred feature. This increment retains operational GAS/service gates and does not activate the unlinked marked probe.
- Final suite: 381 tests pass; final actual A/B reports/resources/SVG remain identical to the frozen baseline (`local_outputs/work/2026-10-19_22-00-31/legacy-final-verification/`). Independent C r1 intermediate payload audit passes all 50 checks; final C r2 audit passes 50 package and 6 independent clearance/ranking checks. Root adds 23 actual-archive/N2-composition/main-checkout checks. Final before/after SVG/PNG plans are rendered and visually inspected; the C2/E1 test bundle and [manual handoff](../../reference/STATION_PARKING_HEURISTICS_HANDOFF_1_61.md) are ready.

- Implementation milestones committed locally as `776f9fc` and `0f6e89d`; final handoff is a subsequent documentation commit. Main master remains clean at `445ef581886538465564a24be0b1199164e43272`. No merge, push, installation or gameplay operation. Runtime validation remains separate.

# Links

- [Station research](../../reference/GAS_STATION_CAR_REST_RESEARCH.md)
- [User feedback](../../reference/GAS_STATION_CAR_REST_FEEDBACK_2026_10_19.md)
- [Existing PoC handoff](../../reference/GAS_STATION_CAR_REST_POC_HANDOFF.md)
