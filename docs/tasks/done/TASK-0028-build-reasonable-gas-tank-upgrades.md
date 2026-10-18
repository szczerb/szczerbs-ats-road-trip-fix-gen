---
id: TASK-0028
title: Research and generate reasonable Ford gas tank upgrades
status: done
priority: high
repositories: [.]
depends_on: [TASK-0002, TASK-0023]
owner: shared
---

# Goal

Deliver a separate experimental capacity mod based on credible, model-specific tank options for the four Road Trip Ford vehicles.

# Context

**Documented — user request, 2026-10-18:** replace the user's excessive 3x-capacity modification with reasonable upgrades. Research the later-year Mustang tank conversion and comparable options for Crown Victoria, F-150 and Bronco. The user will disable the older mod; this workflow does not install packages or edit profiles. Ongoing USA courier testing has no problems reported so far, but does not close TASK-0007.

# Scope

- Primary automotive references, exact installed chassis definitions and an explicit reviewed capacity policy.
- Source-pinned analysis/generation commands, minimal field edits, separate metadata and a reproducible experimental package.
- Leave a vehicle unchanged if no credible moderate upgrade is established. A researched absence is not proof that no custom conversion exists.
- Runtime capacity, retained fuel, billing and save/reload remain manual tests.

# Implementation Plan

| Assignment | Model / effort | Owned files |
| --- | --- | --- |
| Mustang tank research | GPT-6 Luna / medium | Ignored `mustang-tanks-research.md` |
| Crown Victoria tank research | GPT-6 Luna / medium | Ignored `victoria-tanks-research.md` |
| F-150 and Bronco tank research | GPT-6 Luna / medium | Ignored `f150-bronco-tanks-research.md` |
| Guarded planner and synthetic tests | GPT-6 Sol / medium | `tank_upgrades.py`, `test_tank_upgrades.py` |
| Source inspection, policy, integration and final review | Root model | Other implementation and documentation |

1. Check source claims and exact ATS vehicle configurations before selecting targets.
2. Implement byte-preserving, source-pinned capacity and displayed-info changes; report unchanged vehicles.
3. Verify generated resources, metadata, compatibility boundaries and documentation; commit locally.

# Acceptance Criteria

- All four vehicles are researched, with explicit decisions and source/version/date labels.
- An immutable source-pinned policy produces one separate, clearly named experimental mod with the requested author and title.
- Only approved chassis capacity and capacity-display fields change; remaining bytes are preserved.
- Drift, unsupported definitions and unsafe policy values block generation. Analysis never writes a mod.
- Tests and independent archive review pass; no game assets or supplied archives enter Git.
- Installation conflict with the old 3x mod and pending gameplay checks are clearly described.

# Verification

Completed 2026-10-18 against installed ATS 1.61.3.18 / Ford DLC.

- Three GPT-6 Luna/medium automotive reports were reviewed against primary product/OEM evidence; Mustang 20 US gal and applicable F-150 option 655 were selected. Crown Victoria/Bronco remain stock. An auxiliary source-verification note switched to a 2008 Crown Victoria manual; root excluded that page claim and verified the actual 2006 guide, printed page 253.
- GPT-6 Sol/medium implemented the planner and 10 synthetic tests. A real-source analysis exposed sibling animation units; support and preservation checks were added before generation. The initial blocked audit is retained.
- GPT-6 Luna/medium implemented eight workflow tests. `PYTHONPATH=src python3 -m unittest discover -s tests` passes all **266 tests** (18 new).
- Real CLI generation produced one r0 package with two chassis overrides. A subsequent `analyze-tank-upgrades` run reports complete coverage and zero generated packages.
- Independent GPT-6 Luna/medium archive reconstruction verifies only approved capacity/info edits, all animation bytes, metadata, 276x162 icon, DLC requirement, ZIP CRC and report hashes. Package SHA-256: `95bf7495c1274917ac1eccd5b13b367ce66376b363a884629a649ce99b51dc5e`.
- Documentation QA checks reading links/fragments, task metadata/status/dependencies, unchanged 12 input identities, ignored artifacts and whitespace. No supplied/game assets are staged. Work and reports: `local_outputs/work/2026-10-18_18-06-57/`.
- Updated current state and manual checklist with the user's interim USA courier report and the tank transition test. No installation, game launch, profile edits, existing map/courier package changes or runtime validation occurred. TASK-0007 remains active.

Follow-up, 2026-10-18: the user confirms that the tank mod works and explicitly accepts it as internally done; community testing may follow. [Dated acceptance](../../reference/VALIDATION_RESULTS.md#2026-10-18-tank-upgrades-accepted-internally). This closes the internal runtime milestone in addition to the already completed implementation. Per-model measurements and individual migration/reload results were not supplied. The r0 archive and its generation-time report remain unchanged.

GPT-6 Luna / low independently reviewed the acceptance scope and documentation consistency. Documentation-only follow-up checks cover links, task metadata/status, artifact exclusions and whitespace; the passing 266-test implementation baseline was not rerun because no code or package changed. Evidence/check report: `local_outputs/work/2026-10-18_18-47-55/`.

# Links

- [Task board](../README.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Source baseline](../../reference/RESEARCH_BASELINE.md)
- [Standalone courier generator precedent](../../reference/PRACTICAL_COURIER_GENERATOR.md)
