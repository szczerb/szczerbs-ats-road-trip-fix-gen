---
id: TASK-0018
title: Report courier company locations and investigate shared job markers
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0003
  - TASK-0017
owner: shared
---

# Goal

Add source-relative courier analysis/reporting to the selectable processors, without generating courier patches, and establish what the inspected game data says about truck/car company job-selection markers.

# Context

**Documented — user request, 2026-10-18:** begin the courier module with verification/reporting only. Determine whether the physical job-selection avatars at companies are shared between trucks and passenger-car couriers or represented by separate markers. Earlier context-only audits do not inspect placed Company objects; fuel/rest vehicle filters must not be inferred for this feature.

# Scope

- Expose existing Company map-item fields without changing serialization: city/company identity, parent prefab, activation node, spawn-node references and raw flags.
- Join source-owned placements to effective company definitions, prefab definitions/descriptors, context tags and static job-definition matches; retain unknowns and intentional exclusions.
- Inspect only source sectors and the local references needed for their company objects; do not scan the whole world or active profile.
- Add explicit analysis mode and `analyze-map --processor courier`. Preserve existing fuel/rest generation; courier selection for generation remains rejected.
- Keep source hashes/order, inspection versions, evidence limits and reproducible commands. No `.scs` output, installation, save/market changes or game launch.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Courier marker mechanism and bounded real stock/mod comparison | GPT-6.1 Sol / high | COURIER_MARKER_RESEARCH.md and ignored evidence |
| Company-location report and authored regression tests | GPT-6 Sol / high | courier_locations.py and its tests |
| Bounded cached-definition inventory | GPT-6 Luna / medium | Ignored evidence only |
| Analysis/generation boundary, CLI, Company parser fields, actual report run, docs and commit | Root | Integration and remaining authored files |

# Acceptance Criteria

- Source-owned company locations report their resolved/unknown physical and definition links with provenance; missing context is not labelled a confirmed absent job market.
- Generic Company Point, Company map node and loading/trailer spawn points are distinguished. Do not invent a car-marker flag or claim universal runtime reuse from a generic pre-Road-Trip authoring source.
- Read-only courier mode emits a report and no mod; unsupported/missing data is disclosed. Generation still refuses courier and preserves existing fuel/rest behavior.
- Tests cover meaningful joins, ambiguity, exclusions, source priority, marker/node evidence, malformed/unsupported data and the no-package boundary.
- At least one supplied source-map report is exercised with actual data. Manual offer availability, check-in behavior and completed delivery remain pending under TASK-0007.

# Verification

**Observed locally — 2026-10-18:** all **194 tests pass** (`PYTHONPATH=src python3 -m unittest discover -s tests -v`), including semantic DLC filenames, included fragments without duplicate candidates, distinct candidate ambiguity, source priority, actual/editor model disagreement, shared Company parents, raw flags, malformed sectors, exclusions, nested/unsupported coverage and analysis never calling the mod writer. Log: `local_outputs/work/2026-10-18_02-28-11/tests-final.log`.

The final public CLI reports use frozen code and ATS **1.61.3.18**:

| Source | Supported inspection | Report SHA-256 |
| --- | --- | --- |
| ATS Expansion v23.0 / 1.61 | 540/540 sectors, 1,246 companies, all 1,246 main and 6,376 spawn nodes resolved; 1,171 classified, 63 explicitly excluded, 12 unclassified | `127dff6f9f81fa6055d63d02a19f87bdc1c653508937aa5cecbb43bbb8d974e1` |
| Existing WCE r3 patch, with original WCE/ProMods dependencies | 123/123 patch sectors, 380 companies, all main and 2,440 spawn nodes resolved; 341 classified, 20 excluded, 19 unclassified | `d166d4f7ec2a4146d1f55dd64feffb4b63f45bb4df79b9b09354feda396f6ddc` |

Audits: `local_outputs/work/2026-10-18_02-50-30/ats-expansion-analysis/audit.json` and `local_outputs/work/2026-10-18_02-50-30/western-canada-r3-audit-analysis/audit.json`. Both return `reported`, with zero global inspection blockers, zero planned resources and zero generated mods. Their 97/39 partial per-location records remain visible; all runtime eligibility is unknown. [Interpretation and exact editor caveats](../../reference/COURIER_REPORTING.md#actual-source-reports). Earlier runs remain unchanged historical evidence.

The independent marker investigation freshly compares 82 Company records in 22 stock/mod sectors and seven stock PPDs. It supports a common check-in hypothesis, not verified Road Trip mode behavior. An independent read-only comparison also proves that 14 existing WCE r3 Company-parent aliases lack their originals' context mappings, while Company bytes are unchanged. The new reporter detects all 14 actual/editor mismatches; runtime regression is unknown. [TASK-0019](../backlog/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md) tracks preservation separately; no package is regenerated here.

GPT-6 Luna / medium independently verified final report counts, provenance, all 27 ATS/32 WCE package identities, immutable inputs, no-mod output and evidence wording. Verification SHA-256: `4c250d87c0b3a66921d3f806b7661f75de993bb8114f6648506db5176257fa78`. Its ignored verification is `local_outputs/work/2026-10-18_02-28-11/childinventory/report-verification.json`. Documentation QA passed: 70 Markdown files, 529 relative links, 26 heading fragments, 19 task IDs/status/metadata/dependencies (17 done, one active, one backlog), all 12 archive/sidecar identities, 16 artifact-exclusion checks and whitespace; results are saved to `local_outputs/work/2026-10-18_02-28-11/documentation-qa.json`.

Manual market opening, car/truck activation, courier pickup/delivery, fuel billing and rest behavior remain pending under TASK-0007. No live game, profile, market state or installed mod directory was changed.

# Links

- [Earlier context research](../../reference/COURIER_RESEARCH_FINDINGS.md)
- [New marker investigation](../../reference/COURIER_MARKER_RESEARCH.md)
- [Processor guide](../../reference/COMPATIBILITY_PROCESSORS.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
