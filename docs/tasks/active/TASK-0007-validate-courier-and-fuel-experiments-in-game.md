---
id: TASK-0007
title: Validate generated courier and refueling experiments in game
status: active
priority: high
repositories:
  - .
depends_on:
  - TASK-0006
owner: shared
---

# Goal

Determine whether the generated candidates produce usable courier work and passenger-car refueling in their actual map locations, preserving truck behavior and shared-profile progression.

# Context

Static analysis and package generation do not prove runtime behavior. Courier aliases require valid placed depots, routes, eligibility, and market state. Fuel PPDs have separate linked map services, so a descriptor change may require an editor rebuild. No such in-game/editor operation was performed during the overnight research.

# Scope

- Use a disposable/copied profile with exact game/DLC/mod versions, priority, vehicle/class, rating, and baseline observations.
- Record the Helena-area user test and compare the closer city station next, including physical locator/service matching and preserved truck interactions.
- Confirm Great Falls HQ selection/access and compare the [single-pump sample](../../reference/STARTER_AREA_SAMPLE.md), including the converted pump and unchanged nearby truck controls.
- Test the narrow Ahorrara courier candidate separately from the wider alias experiment and the fuel descriptor experiment.
- Compare unmodified, candidate-only, and (only if necessary) separately editor-rebuilt fuel data.
- Record counterexamples, actual fuel changes and completed deliveries, logs, and truck regressions.
- Do not install into or reset the user's live profile as an incidental setup step.

# Implementation Plan

1. Follow [validation handoff](../../reference/VALIDATION_HANDOFF.md), confirm a safe test profile and expected source hashes, and collect actual working/affected examples.
2. Establish a reproducible control stack, isolating extra courier and fuel mods first.
3. Compare courier offers, pickup orientation/access, route completion, and delivery/rating results with matched market progression.
4. For the Helena sample, record the combined descriptor/service outcome, corrected baseline screenshot context, reported patched truck-map absence, and remaining physical truck/reload checks. Establish car and truck support at the same physical pump before broadening to the nearer multi-point city station; do not assume splitting dispensers is necessary. For the separate Reforma PPD-only candidate, compare actual fuel purchase and truck behavior; investigate editor rebuilding only if its own result requires it.
5. Update hypotheses with results and create the next implementation task only from demonstrated behavior.

# Acceptance Criteria

- Each tested candidate has explicit before/after evidence or a reproducible blocker with next evidence needed.
- Courier success requires an offer and completed usable delivery, not just a context entry.
- Refueling success requires a measurable fuel increase and preserved truck access, not just an added PPD record.
- Tests identify effective stack, source/output fingerprints, side effects, and whether map rebuilding is required.
- Live profile and original inputs remain preserved; negative results are recorded.

# Verification

2026-10-17: partial runtime evidence received. The user created a disposable ATS Expansion test profile and reports that enabling the Helena-area sample made the eastern point available to cars and allowed successful refueling. Three inspected map screenshots support the icon change; a cockpit screenshot shows the nearer city forecourt, still reported truck-only. See [validation results](../../reference/VALIDATION_RESULTS.md) for exact attribution, screenshot filenames/provenance, candidate mapping, and limitations.

GPT-6 Luna / medium independently rechecked the existing read-only station inventory, descriptor and generator guards. Root inspected all four supplied PNGs through WSL, verified the v25 city descriptor's four GAS records and four linked services, and reviewed the distinction between model/recipe scope and inherent station risk. No source/archive, code, generated package, game, editor, or profile changes were made. The earlier city-token table's duplicate `.base` extension was corrected while updating the guide.

Documentation checks passed: 39 Markdown documents, 247 relative links, eight task metadata/status/dependency records, 20 corrected sector paths against the source ZIP, four original screenshot fingerprints, and `git diff --check`. These are the appropriate checks for this documentation-only update; gameplay was performed by the user, not the agent. Existing 43 code tests remain the prior static baseline and were not rerun for prose edits.

Follow-up, 2026-10-17: user recalls the original truck-map screenshot probably predates installing the sample, during the initial truck quick job. With the sample now active, the tested point is reported absent in Truck map mode and present only in Car mode. No actual truck-refueling failure is reported. The sample therefore lacks confirmed both-mode visibility, while physical truck fueling remains unknown. GPT-6 Luna / medium reviewed this distinction against the existing code/report; root updated the dated results and ignored evidence metadata. No code, package, game, or profile changes were made.

Still pending: exact runtime build/installed-sample fingerprints, numerical fuel/payment observations, truck and reload regressions, multi-point city-station design/validation, Great Falls/Reforma tests, and courier offers/completed deliveries. A combined PPD/service success does not isolate each component's necessity. This task remains active; one successful user-reported fuel test does not satisfy all acceptance criteria.

# Links

- [Prototype](../done/TASK-0006-build-inspector-and-experimental-generators.md)
- [Validation handoff](../../reference/VALIDATION_HANDOFF.md)
- [Courier findings](../../reference/COURIER_RESEARCH_FINDINGS.md)
- [Refueling findings](../../reference/REFUELING_RESEARCH_FINDINGS.md)

- [User test results and selection review](../../reference/VALIDATION_RESULTS.md)
