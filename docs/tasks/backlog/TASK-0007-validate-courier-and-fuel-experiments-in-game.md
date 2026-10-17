---
id: TASK-0007
title: Validate generated courier and refueling experiments in game
status: backlog
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
- Confirm Great Falls HQ selection/access and compare the [single-pump sample](../../reference/STARTER_AREA_SAMPLE.md), including the converted pump and unchanged nearby truck controls.
- Test the narrow Ahorrara courier candidate separately from the wider alias experiment and the fuel descriptor experiment.
- Compare unmodified, candidate-only, and (only if necessary) separately editor-rebuilt fuel data.
- Record counterexamples, actual fuel changes and completed deliveries, logs, and truck regressions.
- Do not install into or reset the user's live profile as an incidental setup step.

# Implementation Plan

1. Follow [validation handoff](../../reference/VALIDATION_HANDOFF.md), confirm a safe test profile and expected source hashes, and collect actual working/affected examples.
2. Establish a reproducible control stack, isolating extra courier and fuel mods first.
3. Compare courier offers, pickup orientation/access, route completion, and delivery/rating results with matched market progression.
4. Compare station approach, prompts, actual fuel purchase, and trucks before/after the PPD-only candidate. If ineffective, investigate service-item/spawn rebuilding as a separate controlled map experiment.
5. Update hypotheses with results and create the next implementation task only from demonstrated behavior.

# Acceptance Criteria

- Each tested candidate has explicit before/after evidence or a reproducible blocker with next evidence needed.
- Courier success requires an offer and completed usable delivery, not just a context entry.
- Refueling success requires a measurable fuel increase and preserved truck access, not just an added PPD record.
- Tests identify effective stack, source/output fingerprints, side effects, and whether map rebuilding is required.
- Live profile and original inputs remain preserved; negative results are recorded.

# Verification

Pending game/editor work and concrete location observations. Existing static tests are evidence about the generator, not completion of this task.

# Links

- [Prototype](../done/TASK-0006-build-inspector-and-experimental-generators.md)
- [Validation handoff](../../reference/VALIDATION_HANDOFF.md)
- [Courier findings](../../reference/COURIER_RESEARCH_FINDINGS.md)
- [Refueling findings](../../reference/REFUELING_RESEARCH_FINDINGS.md)
