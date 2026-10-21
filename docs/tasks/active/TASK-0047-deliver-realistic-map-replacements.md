---
id: TASK-0047
title: Deliver complete realistic fuel and dedicated-parking map replacements
status: active
priority: high
repositories: [.]
depends_on: [TASK-0045, TASK-0046]
owner: shared
---

# Goal

Deliver a complete, statically audited realistic replacement set for all seven supported r9 map fixes, with selective facility-level fuel and exclusive dedicated station parking. Supply usable packages for normal career play, not another finite test batch. A separately explained stock-game companion may be needed for approved DLC-owned sites.

# Context

**Documented — user objective, 2026-10-21:** G1 interactions work at six sites. Include G01/G02/G06 whole public stations; exclude additions at G03 logistics, G04 farm/equipment fuel and G05 truck garage. User accepts a short optional uncertainty list for ordinary play; no separate-profile tour, pump matrix or new game evidence is required before delivery. This explicit instruction supersedes the default disposable-profile experimentation agreement for the user handoff. No agent launches the game or edits profiles.

# Scope

Map-wide facility classification, configurable broad/realistic presets and independent fuel/parking strategies; source-owned composition preserving native facilities, prices, identifiers and contexts; supported dedicated-bay geometry and explicit no-candidate/unsupported skips. All seven replacement sources, optional base companion if needed, exact installation, source coverage, 8–12 optional readable uncertain-site locators, reproducible configuration and independent actual-output audits. N2 presentation remains deferred. No main edits, merge, push, publication or installation.

# Implementation Plan

1. Revalidate original sources/current game and reuse cached map/model/action evidence.
2. Implement facility fuel rules and preset/exclusive parking configuration while retaining broad behavior.
3. Discover source-owned station placements and safely reuse reviewed effective geometry families; resolve existing activation/orientation/ownership issues before broad reuse.
4. Compose original-source fuel/parking/price/context resources into complete replacement packages, independent of r9 assets.
5. Inspect actual archives and the full declared source stack, package coverage and optional normal-play uncertainty handoff, update durable references and commit verified milestones.

# Acceptance Criteria

- Full seven-source replacement SCS set and ZIP, usable with all r9 and experimental overlays disabled.
- Revised user decisions implemented through reusable facility semantics, explicit uncertainty and unsupported-site reporting.
- Dedicated bays only; no generated truck-area car permission or fallback. Original/native interactions remain unchanged.
- Prices, contexts, source priority, cross-resource graph composition and stable identities preserved where unchanged.
- Meaningful tests plus independent full actual-artifact/effective-stack checks, source coverage and bounded uncertainty list.
- No fabricated runtime acceptance or requirement for a new tour. Goal scope audited item-by-item before completion.

# Verification

Initial state: clean research branch at `4c91271`, clean master at `445ef581886538465564a24be0b1199164e43272`. Complete goal copied unchanged under the ignored timestamped realistic-map-replacements run.

Assignments: `fuel_policy_core` (GPT-6.1 Sol/high) owns fuel selection/planner facility semantics and tests; `realistic_parking` (GPT-6.1 Sol/high) owns map-wide dedicated parking/catalog and station geometry tests; `batch_station_inventory` (GPT-6 Luna/high) owns bounded ignored inventory/uncertainty/attribution research. Root owns staged source composition, presets/workflow/CLI, final artifacts, documentation and integration. Actual output audit will be independently assigned after artifacts exist. Explicit file ownership avoids concurrent edits.

# Links

- [Accepted fuel feedback](../../reference/SELECTIVE_CAR_FUELING_FEEDBACK_2026_10_21.md)
- [Parking feedback](../../reference/STATION_PARKING_FORECOURT_TOUR_FEEDBACK_2026_10_21.md)
- [Exclusive parking strategies](../../architecture/decisions/ADR-0022-select-mutually-exclusive-car-parking-strategies.md)
- [Fuel selection](../../architecture/decisions/ADR-0023-select-car-fuel-additions-by-reviewed-pump-role.md)

Implementation verification checkpoint (2026-10-21): 507 unittest regressions pass, including real cross-sector source-owner composition, one final fuel→parking context chain, independent parking-only selection, unsafe global blocker rejection, high-provider price-priority rejection, CLI analysis/generation boundaries, resource overlay ownership, facility source/state/corridor counterexamples, no truck fallback, and recorded disk-cache reuse. Full original-stack generation and independent finished-archive inspection remain in progress. An initial slow run was interrupted without outputs after repeated per-member HashFS reads were identified; exact descriptor/model/material inputs are now batch-prefetched, retaining the same selection policy. Historical scratch is preserved.
