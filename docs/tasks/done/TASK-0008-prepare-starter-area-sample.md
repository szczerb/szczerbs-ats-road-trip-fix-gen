---
id: TASK-0008
title: Prepare an ATS Expansion sample near a candidate starting garage
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0006
owner: agent
---

# Goal

Identify an accessible candidate starting area from actual game/mod data and generate a reproducible, narrowly scoped experimental compatibility sample with clear test directions.

# Context

The user will create a disposable profile and wants a practical location close to its initial garage. **Unknown:** the authoritative ATS 1.61 fresh-profile selector list. City definitions alone do not establish eligibility. The user's one-slot initial garage observation motivates inspecting placed garage flags rather than assuming all garage cities qualify.

# Scope

- Read installed definitions and ATS Expansion sectors without modifying inputs.
- Establish candidate garage eligibility and nearby placed fuel/company evidence; separate static evidence from UI confirmation.
- Prepare a minimal sample only where the evidence supports a concrete transformation, with reproducible commands and fingerprints.
- Keep all generated mods/assets ignored; do not install mods, open the game/editor, or change profiles.

# Implementation Plan

1. Delegate bounded starter-garage inspection to GPT-6 Luna / medium, with read-only ownership and ignored research outputs only.
2. Cross-reference placed station and company data with candidate garage locations; inspect shared service fields as well as descriptors.
3. Delegate an independent experimental fuel design review to GPT-6.1 Sol / high. Root integrates code, tests, and English documentation.
4. Generate and statically verify the sample and record limitations and user test steps. Runtime validation remains TASK-0007.

# Acceptance Criteria

- A candidate city/area is justified from placed map data; no unsupported full starter-city list is claimed.
- Sample changes, effective source packages, scope/conflicts, and expected truck/car behavior are explicit.
- Generation is reproducible and refuses mismatched source data; original inputs remain unchanged.
- Relevant structural tests and documentation/link checks pass; runtime limitations remain explicit.

# Verification

Completed static milestone, 2026-10-17, installed ATS 1.61.3.18 / ATS Expansion 23.0:

- Read 270 expansion `.base` sectors and selected installed definitions/PPDs; selectively extracted 58 Montana `.base` members and one stock model. Original archives were opened read-only. No game/editor/profile operation or mod installation occurred.
- GPT-6 Luna / medium performed bounded garage/source inspection, writing ignored reports only. Root review caught that its initial 20-city inventory filtered expansion city tokens and that stock-Montana proximity estimates did not account for winning expansion sectors. Both limitations were corrected in reports/references; effective garage identities/positions were cross-checked. Helena and Kalispell retain stock garage class `81`; the other four compared Montana cities use custom models. No authoritative full HQ selector list is claimed.
- GPT-6.1 Sol / high independently reviewed the service-plus-descriptor experiment and actual implementation/package. It confirmed the source-derived offsets, exact hashes/minimal byte changes, unchanged lengths/references, and focused tests; no commit-blocking issue remained. Petrol-bit interpretation and runtime access remain hypotheses.
- Implemented `generate-local-fuel`, authored pinned recipes, and generated Helena-area and Great Falls packages. The Helena-area sector changes eight bytes; Great Falls changes seven. Each private PPD changes only byte 336. Exactly three gameplay resources per output; no global stock PPD override or new locator/node/service count.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: all 43 tests passed, including four focused structural/CLI/fingerprint/collision cases and invalid UID boundaries. Real ZIP integrity, original sector/PPD fingerprints, changed-byte allowlists, output definitions/alias tokens, package contents, and byte-identical second generation passed for both samples.
- Documentation reading paths, relative links, task IDs/frontmatter/status/dependencies, and ADR cross-links checked. `git diff --check` passed; all five supplied inputs and generated/extracted artifacts remain ignored and outside the Git change set. Final documentation check: 38 Markdown documents, 229 relative links, eight task IDs/statuses/metadata/dependency references, all passing.
- Runtime blocker for TASK-0007: confirm new-profile HQ choices against the exact stack, physical access/garage substitution, actual fuel purchase and unchanged nearby truck controls. Starting-city status is not inferred from slot counts or `key_city`. All eight inspected Great Falls company editor definitions already have courier contexts, so no redundant tag patch was generated.

# Links

- [Prototype](../done/TASK-0006-build-inspector-and-experimental-generators.md)
- [Gameplay validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Refueling findings](../../reference/REFUELING_RESEARCH_FINDINGS.md)
- [Starting-garage evidence and samples](../../reference/STARTER_AREA_SAMPLE.md)
- [Pinned sector experiment decision](../../architecture/decisions/ADR-0003-allow-pinned-single-pump-sector-experiments.md)
