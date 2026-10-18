---
id: TASK-0020
title: Research courier job quantities and discovered-city effects
status: done
priority: high
repositories:
  - .
depends_on:
  - TASK-0018
owner: shared
---

# Goal

Research online evidence about ATS Road Trip courier offer quantities and explain which mechanisms could account for fewer offers per city as discovery progresses. Produce ranked hypotheses and a controlled comparison plan, or explicitly document missing evidence.

# Context

**Documented — user report, 2026-10-18:** as the user discovers more cities, finding cities with many courier jobs seems harder and more cities appear to have none. This is a reported impression; no fixed-city before/after counts or total-market measurements establish causation yet.

**Observed locally — earlier ATS 1.61.3.18 research:** courier definitions expose context, class, rating and distance inputs. The new company-location report does not simulate market generation, discovery state or live offers. A shared job-selection marker does not explain offer counts by itself.

**Hypothesis:** a bounded overall offer budget could dilute departures across cities. **Alternative hypotheses:** discovery reveals previously hidden sparse cities; local eligible origin/destination density and route limits vary; market time, filters, vehicle, rating or mod changes confound the comparison. No city-count or discovery rule is assumed proven.

# Scope

- Delegate bounded online research to a cheaper model where available, preferring primary SCS sources, original developer statements and published source definitions.
- Distinguish ATS 1.61 Road Trip evidence from historical truck-market guidance and player anecdotes.
- Identify documented controls, unknown global/per-city limits, discovery/UI behavior, expiration/refresh and endpoint/distance constraints.
- Record source URLs, dates/version applicability, inspection date, negative search results and low-risk future controls.
- Preserve game/profile state, inputs and existing generated packages. No economy resets, profile edits, generator changes or new mods.

# Implementation Plan

| Assignment | Model / effort | Ownership |
| --- | --- | --- |
| Online evidence and ranked hypotheses | Existing processor_pipeline subagent; configured model/effort unavailable | COURIER_JOB_AVAILABILITY_RESEARCH.md and ignored scratch |
| Source review, task/current-state integration and local commit | Root | Remaining authored documentation |

# Acceptance Criteria

- The user's observation is retained as a report, not converted into an established discovery rule.
- Technical claims link primary sources and distinguish documented behavior, local prior evidence, hypotheses and unknowns.
- Global-cap dilution is either supported by direct evidence or explicitly remains unproven, with plausible alternatives.
- Future tests distinguish fixed-city counts, total offers, UI visibility and changed eligibility while controlling profile/car/rating/time/mod stack.
- Documentation links, task metadata/status/dependencies and artifact exclusions pass verification. No utility or game tests are required for this research-only milestone.

# Verification

2026-10-18: online research completed by the existing `/root/processor_pipeline` subagent, with ownership limited to the new reference and ignored scratch. A new GPT-6 Luna / medium request was rejected with `agent thread limit reached`; the reused agent's configured model/effort is not exposed, so no cheaper-model guarantee is claimed. Root reviewed primary SCS courier/mode-switch posts and the original SCS-forum player report, and verified the Rideshare author's published location/refresh statements. The Food Courier Workshop URL was unavailable during root rechecking; that page's description is delegate-inspected evidence, not an independently reopened source.

The [research note](../../reference/COURIER_JOB_AVAILABILITY_RESEARCH.md) distinguishes SCS statements, add-on author observations, anecdotes and unknown engine behavior. No inspected source verifies a global/per-city budget, discovery-allocation rule or refresh/expiry schedule; global-pool dilution remains a hypothesis. The stock local data corroborates rating/class/context/distance constraints, not the proprietary allocation algorithm.

Root additionally counted the pinned stock job definitions and the delegate independently recomputed the results: all 149 units have explicit rating and vehicle types. Mustang tag intersections by rating threshold 0/2.6/3.6/4.6 are 7/22/30/54; pickup/offroad/sedan are each 29/71/103/147. These are definition-entry counts, not offers. The source hash matches the prior freshly verified reference. Reproduction and JSON: `local_outputs/work/2026-10-18_03-11-00/compare-stock-courier-classes.py` and `stock-courier-class-comparison.json`. A bounded cached economy keyword scan and source hashes are in `cached-economy-keyword-scan.json`; absence of an obvious count field does not prove the engine has no cap.

Future tests record fixed-city departures and total visible offers separately, control car/rating/market/filters and compare equal elapsed-time copied-profile discovery/control runs over natural updates. Such tests remain pending under TASK-0007; no city examples or gameplay were requested tonight. No utility source, game/profile, input archive or generated package changed. Documentation-only QA passed for Markdown links/fragments, 20 task IDs/status/metadata/dependencies, all 12 immutable archive/sidecar identities, 16 exclusion checks and whitespace. Results are recorded in `local_outputs/work/2026-10-18_03-11-00/documentation-qa.json`; no utility tests were rerun for this research milestone.

# Links

- [Courier location reporting](../../reference/COURIER_REPORTING.md)
- [Economy reference](../../reference/ECONOMY_AND_COURIER_JOBS.md)
- [Prior courier findings](../../reference/COURIER_RESEARCH_FINDINGS.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
