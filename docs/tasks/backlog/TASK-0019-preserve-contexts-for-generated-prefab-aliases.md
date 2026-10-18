---
id: TASK-0019
title: Preserve courier contexts when generating private prefab aliases
status: backlog
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

| Assignment | Proposed model / effort | Result |
| --- | --- | --- |
| Review context semantics and alias-preservation design | GPT-6.1 Sol / high | Evidence-backed policy and ambiguous-case boundary |
| Implement bounded preservation and regression tests | GPT-6 Sol / high | Deterministic processor integration |
| Independently compare generated classifications and unchanged records | GPT-6 Luna / medium | Ignored audit and authored summary |

# Acceptance Criteria

- Supported aliases retain the exact effective original classification; excluded/unclassified originals do not acquire guessed eligibility.
- Conflicting contexts and unsupported joins are explicit; package/source precedence is preserved.
- Tests cover both processors, composed edits, exclusions, existing targets and conflicts.
- A real WCE comparison accounts for all 14 observed Company-parent aliases and retains original Company records and fuel/rest behavior structurally.
- Runtime courier regression or preservation remains unverified until controlled truck/car offer and delivery checks; no static result closes TASK-0007.

# Verification

Not started. Required evidence: original-to-alias context audit, generated resource provenance, regression tests and subsequent manual controls. The initial discovery audit is recorded in the marker research document; it is not repair verification.

# Links

- [Reporting milestone](../done/TASK-0018-report-courier-company-locations.md)
- [Processor composition](../done/TASK-0017-compose-selectable-compatibility-processors.md)
- [Marker and alias evidence](../../reference/COURIER_MARKER_RESEARCH.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
