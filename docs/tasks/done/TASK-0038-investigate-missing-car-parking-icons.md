---
id: TASK-0038
title: Repair missing passenger-car parking markers
status: done
priority: high
repositories: [.]
depends_on: []
owner: shared
---

# Goal

Identify the cause of missing car-mode parking icons, implement an evidence-supported repair, test and independently review it, and deliver local r9 map replacements. Runtime confirmation may follow later on a copied profile; the authorized deliverable excludes launching/installing the game or changing the user's profile.

# Context

**Documented — user clarification, 2026-10-18:** Canada/Alaska show no car parking icons and Montana is sparse, while Mexico has dense coverage. Physical rest was not tested; the earlier late-night rest-success report may have been mistaken. Washington icons were initially misread by root as southern BC and corrected by the user. Preserve the earlier report with that qualification. Fuel access, jobs and tanks retain separate evidence.

R8 is installed correctly and has r7 gameplay bytes, so a pre-existing defect is possible. The user authorizes autonomous research, supported implementation, tests, independent review, local experimental r9 packages, documentation and local commits. No push, publication, installation, game launch, profile edit or interruption of the current Mexico job.

# Scope

- Repair source-specific rest marker representation while retaining the inclusive 1,000-unit XZ permission rule, original geometry, truck/bus rest, fuel data and courier classifications.
- Keep bounded source/halo inspection and accepted boundary over-additions explicit; do not claim stock-Montana-wide coverage or equate markers with successful fatigue recovery.
- Keep all supplied inputs, installed files, r8 and preliminary/rejected r9 outputs intact. Final candidates live under ignored `local_outputs/generated/2026-10-19_00-03-23/`.
- Work was isolated on `codex/car-parking-icons`; production commits are `42b6e9b` and `f561751`, with the final documentation milestone merged locally. No push.

# Implementation Plan

1. Verify installed r8 hashes, r7 equality and active source order; review both screenshots with corrected geography.
2. Compare placed native Washington/Reforma car rests and selected WCE/Alaska source/r8 geometry, actions and map representation.
3. Independently trace both prefab/standalone marker builders and semantic action matching in the exact installed executable; reject unproven overlay/fuel-bit theories.
4. Add separate native car-only groups/items, preserving originals and composing fuel/rest graph, visibility, layers and contexts; exercise proximity and safety cases.
5. Generate seven r9 packages, independently audit full output bytes and r8 invariants, then inspect the effective supplied stack. Correct and replace drafts that fail preservation.
6. Bundle only audited finals, document replacement/later tests, check documentation and commit/merge locally. Leave runtime observations in TASK-0007.

Actual delegation and ownership:

| Work | Model / effort | File ownership and verification |
| --- | --- | --- |
| Source inventory and paired comparisons | GPT-6 Luna / medium | Read-only sources; owned inventory scratch. Root checked exact records/tokens/coordinates and corrected prefab/action alias conflation. |
| Regression cases | GPT-6 Luna / high | Owned `tests/test_rest_stops.py`; targeted 69 tests pass and root ran the full suite. |
| Independent mechanism/code/archive review | GPT-6 Sol / high | Read-only production; owned separate disassembly/audit scratch. Root matched seven audited hashes to the final bundle selection. |
| Manual-test/result documentation follow-up | GPT-6 Luna / medium | Owned manual checklist, validation results and TASK-0007; root reviewed evidence wording and finalized audit status. |
| Production, integration, effective-stack checks, final artifacts/docs | Main model / current | Owned production and all remaining documentation; independent review and final gates below. |

The initial documentation checkpoint also used bounded GPT-6 Luna/high read-only research; it was not a substitute for the later independent mechanism/output review.

# Acceptance Criteria

- Concrete placed source/r8 comparisons and a supported marker mechanism, with version/identity and uncertainty recorded.
- Implemented car-only marker representation under the original distance/geometry policy, with truck/bus/fuel/context preservation and no invented fuel flag.
- Meaningful regression tests and independent code plus final archive review, including effective resource order.
- Seven ready r9 replacements with exact fingerprints, clear installation/later-test instructions, and all older results retained.
- English docs/current state/task/ADR updates, appropriate QA and local commits/merge; no publication/push or game/profile operation.
- Do not claim in-game success from counters, static graphs or marker classification; hand off the short deferred runtime check explicitly.

# Verification

**Subsequent user validation and authorization, 2026-10-19:** the maintainer confirms r9 parking icons in Alaska and Canada after checking two towns, with denser map coverage. This supersedes the handoff's lack of runtime icon evidence at that scope; individual fatigue/truck/reload steps were not enumerated. The user explicitly requests commit and push of the work, authorizing the subsequent source update beyond the original local-only boundary. A GPT-6 Luna/medium read-only review checks evidence wording; root owns edits, documentation QA, commit and push. [Dated evidence](../../reference/VALIDATION_RESULTS.md#2026-10-19-r9-parking-icons-confirmed-in-alaska-and-canada).

**Observed locally — validation-record follow-up:** documentation QA passes 133 Markdown files, 1,051 relative links, 76 heading fragments and 37 task records, plus whitespace/exclusion checks. The r9 delivery ZIP hash is unchanged. This update changes only documentation; the previous 281-test code baseline is retained without an unnecessary rerun. Evidence: ignored `local_outputs/work/2026-10-19_00-44-45/`.

**Observed locally — 2026-10-19:** the [r9 handoff](../../reference/MOD_REST_MARKERS_1_61_R9.md) records final fingerprints, commands, independent byte checks, scope and manual test. All six implementation/delivery requirements are satisfied at the explicitly authorized static boundary:

1. Placed native Washington/Reforma and source/r8 WCE/Alaska comparisons establish action/geometry differences. The [investigation](../../reference/CAR_PARKING_ICON_INVESTIGATION.md) preserves corrected screenshots, installed equality and bounded higher-mod path inspection.
2. Root and Sol/high independently find truck-first parking-marker classification in the exact executable (`c60e8ee02cc97b3cc6ef8c6298bb5c3c23c4ffd330b8185b646fb1b608a3c7b4`). Dynamic command/parameter matching rules out private alias spelling as the cause. Both prefab and standalone paths require distinct car-only geometry; no overlay or guessed fuel flag is added. [ADR-0017](../../architecture/decisions/ADR-0017-separate-car-rest-marker-geometry.md).
3. Native `parking_car` twins preserve source geometry, original truck/bus actions/records, tags and graph relationships; the immutable physical-car index and inclusive 1,000-unit rule remain. Mixed-mode marker repair is separately tested/reported. An extra final audit detected branding-induced fuel UID drift in two first drafts; `f561751` preserves historical namespace seeds and the two maps were regenerated.
4. `PYTHONPATH=src python3 -m unittest discover -s tests -q` passes **281 tests**. Independent seven-archive review checks original records, 357 new prefab groups, 897 standalone twins, r8 fuel service/node/private-resource identities, selection continuity, metadata, CRC and hashes. Root checks 583 effective sector paths, 2,202 truck fuel targets with car counterparts, 3,518 reciprocal car service links and 1,152 surviving car-only rest groups/items. Namespace/context/company and ZIP/HashFS layer checks pass. [Full scope and limits](../../reference/MOD_REST_MARKERS_1_61_R9.md#verification-and-limits).
5. Final ZIP contains exactly seven r9 mods plus README/checksums: **68,664,125 bytes**, SHA-256 `e1eef95f5ed30cc43c5896c44af1fd8de368aad7b60ef2895cfd9fcb8432142f`. Every contained mod matches the independent final review. R8/earlier drafts remain intact; only the two corrected Expansion finals enter the bundle. Jobs r3/tank r0 are separate and unchanged.
6. Current docs/ADR and later manual checklist distinguish static completion from runtime unknowns. Documentation QA validates local links/fragments, task metadata/status, artifact exclusions and whitespace. Local commits/merge preserve this milestone without push. No game operation, installation or profile edit occurred.

Authoritative final evidence: `local_outputs/work/2026-10-19_00-03-23/` (full test log, command records, delivery manifest/receipt, independent-review hash matching, effective graph, namespace/company/preservation/layer checks, documentation/completion audit). Independent source/code/output evidence: `local_outputs/work/2026-10-18_23-37-00/mechanism/final-seven-audit.json` and `rejected-drafts-audit.json`; paired inventory: `local_outputs/work/2026-10-18_23-37-37/parking-inventory/`. Original seven-map generation/audits remain under `local_outputs/work/2026-10-18_23-48-10/`.

**Historical handoff runtime status, superseded for icons by the later report above:** actual r9 icon rendering, rest prompt/fatigue recovery, truck/bus/tag/script controls and reload had not been reported at handoff. Individual rest/fatigue/truck/reload steps remain unreported. This task completes the requested local implementation and ready experiment, not gameplay acceptance. [TASK-0007](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) remains active.

## Initial investigation checkpoint, 2026-10-18

The following preserves the initial evidence state before the supported mechanism and implementation above. Its then-unknown marker questions and “no production changes” statement apply only to the `23-24-54` documentation checkpoint and are superseded by the later evidence.

**Observed locally — 2026-10-18:** all seven installed map r8 archives match the delivered archives by SHA-256. Every `map/`, `prefab/` and `def/` resource is byte-identical to its r7 predecessor. The 22:49:31 game-log session lists all seven r8 fixes active in the expected source-relative sequence. This excludes an r7-to-r8 gameplay payload change; it does not exclude an earlier defect or uninspected effective-resource interaction.

**Observed locally:** embedded rest reports contain 31 Alaska, 202 Western Canada, 95 ProMods, 41 connector, 766 ATS Expansion and 119 Reforma additions. These count action edits per package, not visible icons or unique effective-world sites. OtherMaps is price-only. Private rest actions contain `hud_activate`, numeric parameter 3 and `truck`, `bus`, `car` strings.

**Observed locally:** root inspected `ats_20261018_232603_00.png` through WSL. **User-corrected geography:** the visible bed icons are in Washington, USA; none appear north of the Canadian border at the shown zoom. Root's initial southern-BC description was incorrect and has been corrected in the evidence. Alaska is outside this screenshot; it does not show all Montana.

**Observed locally:** second screenshot `ats_20261018_232848_00.png` shows dense Mexican icons. **Hypothesis — user:** the problem affects all fixes except Reforma. The source-plus-halo Reforma report contains 1,342 existing car rests and 961 truck polygons suppressed by existing neighbors, versus Alaska's zero existing car rests and all 31 truck polygons selected. This supports investigating native-versus-generated marker behavior; it does not identify the visible icons' provenance.

**Observed locally:** eleven logged higher-priority Workshop directory inventories and the opaque No DeadEnds archive have no exact r8 sector/private-resource collisions. This is a bounded path check, not a complete semantic runtime audit.

**Observed locally:** the saved log has five vehicle-mode rejection messages between session offsets 00:06:39 and 00:07:42. Both original and private actions share the label “Parking - Large vehicles”; these messages contain no trigger UID/location/token. They cannot be attributed to the screenshot, Canada, Alaska or a generated action.

**Observed locally — root review of delegate findings:** rest edits retarget action tokens; they do not create Parking services or Map Overlays. **Documented:** SCS distinguishes sleeping-area triggers from map-icon overlays. **Unknown:** whether generated private actions are recognized for car-map icon discovery, whether a separate marker is needed, and the exact ATS 1.61 vehicle-mode filter. Absence of explicit marker edits alone does not prove the cause. See the [evidence reference](../../reference/CAR_PARKING_ICON_INVESTIGATION.md).

2026-10-18: active investigation; no supported marker repair or in-game validation yet. Next work is a source/stock comparison of marker and action representations, not a requested interruption of the user's current job. No production/package changes or utility-test rerun for this documentation milestone.

Documentation QA: 11 changed/new documents, 270 relative links/heading fragments, seven installed/r7 equality results and seven scratch-evidence exclusions pass; `git diff --check` passes. Root preserved the original positive report with an explicit later qualification and updated current-facing acceptance language. Evidence: `documentation-qa.json` in the ignored run directory.

# Links

- [R9 handoff](../../reference/MOD_REST_MARKERS_1_61_R9.md)
- [Icon investigation](../../reference/CAR_PARKING_ICON_INVESTIGATION.md)
- [Gameplay results](../../reference/VALIDATION_RESULTS.md)
- [Manual validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
- [Historical r8 handoff](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md)
