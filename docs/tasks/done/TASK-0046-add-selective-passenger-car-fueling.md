---
id: TASK-0046
title: Add explainable selective passenger-car fueling and a comparison PoC
status: done
priority: high
repositories: [.]
depends_on: [TASK-0045]
owner: shared
---

# Goal

Implement an opt-in, evidence-based alternative to broad car fueling, preserving native facilities and existing compatibility repairs, and deliver audited broad/selective comparison packages with a compact, diverse test tour. User gameplay remains later validation; static delivery and preservation checks are required for completion.

# Context

**Documented — user objective, 2026-10-21:** some added car fuel points appear to belong to truck/fleet infrastructure. Research suitability per pump group, distinguish inference from actual fuel restrictions, retain uncertainty, and preserve legacy broad behavior. Fuel and parking are independent; ADR-0022 requires alternative generated parking strategies. This increment focuses on fuel and may deliver a fuel-only PoC, not a complete realistic preset.

# Scope

- Reuse the existing research branch/worktree and immutable input/cache evidence.
- Investigate public stations, mixed public truck stops, company/depot and private fleet infrastructure, and ambiguous/composite cases.
- Implement opt-in classification/configuration with explainable intentional exclusions and uncertain-case behavior; preserve broad generation, prices, source services, aliases and contexts.
- Deliver actual alternatives, an independently checked effective-stack setup, annotated plans and a concise results README.
- No parking geometry improvements, game/profile changes, automatic installation, merge, push or publication.

# Implementation Plan

1. Inventory representative real source/map evidence using bounded cached reads; inspect official documentation for claimed semantics.
2. Define classification and evidence/uncertainty policy; implement selection before PPD/service additions.
3. Integrate public CLI/configuration, reporting and unambiguous variant metadata; verify legacy behavior.
4. Select real test groups and generate broad/selective alternatives from an audited source baseline that excludes inherited broad additions.
5. Independently inspect actual archives and effective dependencies; prepare plans, site identifiers, expectations and result table.
6. Reconcile every goal requirement against current evidence, update references/current state and commit verified milestones.

# Acceptance Criteria

- Working opt-in fuel policy alongside unchanged broad behavior, with configuration validation and pump-level mixed-layout decisions.
- Evidence distinguishes suitability from diesel-only claims, and company relationships from proximity.
- Unknown cases remain explicit; intentional skips do not mask structural coverage failures.
- Original native car/truck services, nodes, context lineage and selected price repairs are preserved.
- Effective selective setup genuinely lacks excluded generated car services/locators, including inherited dependencies.
- Ready-to-test comparison packages cover public, private/truck, mixed and uncertain cases with exact setup and annotated location plans.
- Appropriate tests and independent output audits pass; in-game outcomes remain unverified until user testing.

# Verification

2026-10-21: root read the complete supplied objective and revalidated the clean research branch at `260c58e` and clean main checkout at `445ef58`. Goal evidence is copied unchanged into the new ignored Warsaw-timestamped run. Existing historical artifacts remain untouched.

Initial assignments (completed scope and follow-up assignments below): existing `batch_station_inventory` (GPT-6 Luna / high) owns only new ignored inventory evidence, reviewing actual station/company/pump semantics and compact real sites. `fuel_policy_core` (GPT-6.1 Sol / high) owns the new fuel-selection package, bulk fuel/PPD subset planning and their tests. Root owns interface/workflow integration, test packaging, evidence review, documentation and final verification. Independent actual-output scripts were subsequently assigned once concrete artifacts existed. No duplicate full-world extraction is planned.

## Completed implementation and delivery — 2026-10-21

Opt-in immutable fuel selection now reaches the existing general CLI/processors and a guarded finite-site workflow; broad defaults remain unchanged. Four descriptor/model-state catalog rules plus a semantic garage fallback express per-GAS suitability with confidence/evidence and uncertain-case behavior. Native car/truck services, independent prices and courier context lineage survive. General visual bytes are not pinned; the finite comparison independently verifies its actual visual providers. The algorithm is a conservative reviewed-layout classifier, not universal public/private or diesel-only detection.

G1 BROAD r1 and G2 SELECT r1 are delivered as alternatives over the same six-site/five-resource baseline, with nine versus one added car fuel groups, four retained native groups, exact load order, seven annotated plans, per-pump reasons/results table, source pins and reproducible public CLI commands. The source-resource guards deliberately displace lower generated fuel/rest edits in three resources; temporary non-tour loss is quantified in the handoff. This is fuel-only, not the completed realistic parking preset. N2 stays independent; metadata/artwork remains deferred. Lufkin is optional; the other four US sites cluster in New Mexico and the private/fleet example is at the Mexican border.

Actual delegation: `batch_station_inventory` (GPT-6 Luna/high) supplied bounded layout inventory and owned batch workflow/tests. `fuel_policy_core` (GPT-6.1 Sol/high) owned classifier/PPD/planner changes and later wrote separate read-only actual-archive/effective-stack audit scripts. `private_fuel_evidence` (GPT-6.1 Sol/high) supplied Castores Company/model/sign evidence and reviewed inference/pin limits; its final code/goal review found the cross-resource exclusion gap, now fixed with a regression and actual-source gate check. Root integrated interfaces, reviewed code/evidence/audit logic, authored tests/configs/handoff/plans and verified outputs. File ownership was explicit; the auditing agent edited only ignored verification scripts. Separate review tightened the batch boundary gate while the artifacts stayed unchanged.

Verification: **460 tests pass**. Full ATS Expansion broad output retains all 202 historical pre-rest sector hashes and 106 private fuel resources (894 additions). Independent actual pair audit validates exact permitted byte changes, source/native/rest/Company retention, nine versus one appended locators/services/nodes, no orphans, metadata, CRC and equal 27-country prices. Effective-stack review validates selected winning resources, source/context alias lineage, original input identities, original Castores visual providers/pins and unchanged whole N2/payload. It caught the cached G05 garage reference mismatch; evidence/table/plan were corrected to ProMods GAS2, while the production output had already used those correct bytes. Old snapshots and historical packages remain untouched. Bundle file hashes/CRC and relative links are checked at closure.

Implementation milestone / artifact generation: `2b19c32`; subsequent boundary gate fix: `c0428f8`. The delivered source groups satisfy that gate without any gameplay payload change. No main-checkout edits, merge, push, publication, installation, game launch or profile change. Runtime acceptance remains later user work and is not inferred from static checks.

# Links

- [Policy, package fingerprints, exact test setup and verification](../../reference/SELECTIVE_CAR_FUELING.md)
- [Reviewed reproduction configuration](../../examples/selective-fuel-tour/README.md)

- [Processor configuration](../../reference/COMPATIBILITY_PROCESSORS.md)
- [Refueling research](../../reference/REFUELING_RESEARCH_FINDINGS.md)
- [Forecourt user feedback](../../reference/STATION_PARKING_FORECOURT_TOUR_FEEDBACK_2026_10_21.md)
- [Parking alternatives](../../architecture/decisions/ADR-0022-select-mutually-exclusive-car-parking-strategies.md)
