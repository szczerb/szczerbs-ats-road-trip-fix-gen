---
id: TASK-0045
title: Build one curated multi-location station-parking test mod
status: active
priority: high
repositories: [.]
depends_on: [TASK-0044]
owner: shared
---

# Goal

Deliver one source-pinned SCS overlay with private PPDs for a finite curated set of real operational stations, plus a sequential test itinerary, diagnostics, manifest and audited ZIP. Target 6–10 sites / three geometric families; required minimum four newly served sites / two families, including unserved painted bays and an unmarked proposal. Native controls do not count toward that minimum.

# Context

**Documented — user goal, 2026-10-19:** continue the existing isolated research worktree from `2e5d91a`, preserve C2/E and independent user-confirmed N2, retain effective standard r9 fuel/rest/context payload, and expand analysis to external map objects. No game operation, installation, profile changes, merge, push or publication. Runtime activation shape/tolerance and C2 usability remain unverified. Inactive-station activation and TASK-0043 presentation remain deferred.

# Scope

Effective station inventory, shared model/state versus PPD/placement separation, bounded local-world checks, explicit batch manifest, private aliases, disjoint guarded same-sector composition and one overlay above retained source-specific fixes. Preserve single-station APIs and legacy results. No rest-radius/density integration or broad automatic map generation.

# Implementation Plan

1. Freeze source/tests and inspect effective resources and current r9 packages.
2. Inventory real operational stations and select diverse generated sites with separate native controls.
3. Add bounded external-context checks and explicit pure batch composition with strict manifest validation.
4. Integrate public analyze/generate batch workflow, retain actual effective baseline bytes and validate input identities.
5. Verify authored fixtures, actual selected sites and final archive/stack; render plans and deliver one SCS + ZIP with itinerary and checksums.

Delegation: `batch_station_inventory` (gpt-6-luna/high), owns only ignored inventory scripts/reports; `batch_composition` (gpt-6.1-sol/high), owns new `station_parking/batch.py` and `tests/test_station_parking_batch.py`; `station_world_context` (gpt-6-luna/high), owns new `station_parking/local_context.py` and its authored tests. Root owns workflow/CLI/planner integration, task/ADR/documentation, actual configs, final audits and commits. All work is reviewed before integration.

# Acceptance Criteria

- Finite explicit set meets the stated minimum, with target coverage attempted and limitations reported.
- One actual SCS contains every selected private alias and all same-sector edits, preserving r9/source records, services, rest and contexts.
- Per-placement world checks inspect recognized source representations and disclose unsupported objects without claiming collision completeness.
- Deterministic order-independent composition; drift/ambiguity/conflicts block atomically; single-station legacy output unchanged.
- Every delivered site is audited from the final archive; full tests and effective N2/baseline composition checks pass.
- One ZIP includes the mod, reproducible manifest/configs, plans, reports, a grounded sequential itinerary/result table and SHA-256 checksums.

# Verification

- Initial branch/worktree clean at `2e5d91a`; baseline source snapshot and test output under ignored local-only `local_outputs/work/2026-10-19_22-36-47/batch-baseline/`.
- Frozen baseline: **381 tests pass**. Initial workflow/CLI and optional context integration are implemented; pure composition/context modules are being verified.
- [Batch composition decision](../../architecture/decisions/ADR-0021-compose-explicit-station-parking-batches.md).
- Verified first implementation milestone: **412 tests pass**. Complete actual historical A/B reports, resources and SVG hashes remain exact (`local_outputs/work/2026-10-19_22-46-00/legacy-batch-verification/`).
- Independent review added manifest/config parse-before-pin protection and direct directory dependency hashing. External context now evaluates both painted approach ends before selection, including their minimum margins, without changing the legacy no-context rule.
- Actual-site curation, final full-stack generation and handoff remain pending. Do not mark complete from a narrower partial sample.

# Links

- [Current heuristic handoff](../../reference/STATION_PARKING_HEURISTICS_HANDOFF_1_61.md)
- [Effective model-state decision](../../architecture/decisions/ADR-0020-plan-parking-from-effective-model-state.md)
