---
id: TASK-0019
title: Preserve courier contexts when generating private prefab aliases
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0017
  - TASK-0018
owner: shared
---

# Goal

Prevent fuel/rest prefab cloning from silently losing existing static courier classifications, while preserving source exclusions and effective package precedence.

# Context

**Observed locally — ATS 1.61.3.18, 2026-10-18:** the existing Western Canada r3 fuel/rest package changes 14 Company-parent prefabs from officially `truck_dealer`-classified identifiers to private aliases without matching context targets. Company records remain byte-identical. [Exact evidence](../../reference/COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk).

**Hypothesis:** runtime courier behavior could change if the engine classifies the actual placed model identifier. **Unknown:** the runtime identity join and actual effect on offers, pickup or delivery. This is a confirmed static input change, not 14 confirmed broken job locations. The reporting-only milestone deliberately leaves existing packages untouched.

# Scope

- Audit private prefab aliases from both fuel and rest processors against effective original context mappings, including explicit exclusions and unclassified originals.
- Design deterministic preservation of exact original classifications for supported aliases. Do not infer new tags from company/model naming, override intentional exclusions or union conflicting effective definitions silently.
- Check additive context resource naming, unit identity, source order and interactions between selected processors.
- Make unsupported/ambiguous preservation visible before publishing a future package. Keep reports traceable from original identifier to alias.
- Regenerate affected candidates only as a separate implementation milestone; retain old artifacts and document replacement instructions and manual controls.

# Implementation Plan

| Assignment | Actual model / effort | Result |
| --- | --- | --- |
| Context policy, implementation and bounded rest-layout triage | GPT-6 Sol / medium | Proven sector transition lineage, exact tag preservation and fail-closed conflicts |
| Integration review, batch generation and source-order graph | Root | Public workflow, combined resources and metadata |
| Independently compare generated classifications and unchanged records | GPT-6 Luna / medium | Ignored audit and authored summary |

# Acceptance Criteria

- Supported aliases retain the exact effective original classification; excluded/unclassified originals do not acquire guessed eligibility.
- Conflicting contexts and unsupported joins are explicit; package/source precedence is preserved.
- Tests cover both processors, composed edits, exclusions, existing targets and conflicts.
- A real WCE comparison accounts for all 14 observed Company-parent aliases and retains original Company records and fuel/rest behavior structurally.
- Runtime courier regression or preservation remains unverified until controlled truck/car offer and delivery checks; no static result closes TASK-0007.

# Verification

Implemented `prefab_contexts.py` and composed processor transitions. Unique additive resources retain exact supported original tags; original exclusions/unclassified models are left unclassified. Conflicting live tags/exclusion comments, duplicate units, conflicting aliases and missing lineage block publication. Chained fuel-to-rest aliases retain the original model's classification. [ADR-0010](../../architecture/decisions/ADR-0010-preserve-contexts-for-generated-prefab-aliases.md).

The real WCE r4 planner reports 190 aliases, 14 classified and 176 unclassified/excluded. Independent source/output checks and final batch acceptance are recorded in TASK-0024. Final authored suite: **233 passing tests**, `local_outputs/work/2026-10-18_04-08-02/tests-final.log`. Independent WCE source/output comparison retains **380 Company records** across 123 edited sectors byte-for-byte and accounts for all **14** Company-parent aliases; `local_outputs/work/2026-10-18_04-00-48/verify_wce_companies.json`. The independent WCE package review verifies actual original context units against all generated classifications. Runtime courier behavior remains unknown; TASK-0007 stays active.

# Links

- [Overnight delivery task](../done/TASK-0024-deliver-overnight-test-mod-batch.md).

- [Reporting milestone](../done/TASK-0018-report-courier-company-locations.md)
- [Processor composition](../done/TASK-0017-compose-selectable-compatibility-processors.md)
- [Marker and alias evidence](../../reference/COURIER_MARKER_RESEARCH.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
