# Selective passenger-car fueling — ATS 1.61 research and PoC

Date: 2026-10-21. [TASK-0046](../tasks/done/TASK-0046-add-selective-passenger-car-fueling.md), [ADR-0023](../architecture/decisions/ADR-0023-select-car-fuel-additions-by-reviewed-pump-role.md).

**Subsequent user feedback — 2026-10-21:** G1 works at all six visited sites. Include G01/G02/G06 as whole stations; exclude our additions at G03/G04/G05. This supersedes the old G2 sample suitability choices; that archive and its config remain historical and unchanged. [Report, table snapshot and full-map readiness](SELECTIVE_CAR_FUELING_FEEDBACK_2026_10_21.md).

## Evidence and policy

**Documented — official authoring scope:** SCS prefab locators define map connections, AI behavior and player interactions; GAS spawn points are distinct from generic trigger polygons. The public authoring documentation does not establish a complete ATS 1.61 petrol/ownership schema. [SCS prefab locators](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators), inspected 2026-10-21. The [prior flag/service research](REFUELING_RESEARCH_FINDINGS.md) supplies versioned local observations and limits.

**Observed locally — ATS 1.61.3.18:** GAS flags 1 / map service bit `0x4000` correlate with car interactions; flags 0 with truck interactions. This is target-vehicle evidence, not a declaration that a pump sells only diesel or prohibits public customers. Preserve source-native car support regardless of the suitability policy.

**Observed locally / policy inference:** reviewed layout evidence produces these decisions:

| Evidence | Delivered decision | Limit |
|---|---|---|
| Legacy retail GAS exactly matches a native Road Trip car locator in the same visual model | Include that source group, high confidence | Reference layout changes other locators; loose nearest matches are insufficient. |
| Native mixed public layout already separates car and truck groups | Keep its native car groups, omit extra car support at reviewed truck groups, medium confidence | This preserves the inspected distinction; it does not prove fuel chemistry. |
| Same-parent freight Company plus pumps inside a fenced logistics lot and visible distribution-company signage | Omit added car support at the reviewed yard groups, medium confidence | Public-access rules and diesel-only status remain Unknown. |
| Original garage FuelPump item | Omit added car support under the truck-garage policy, medium confidence | This is a garage-facility decision, not proof that every garage bans cars. |
| Generic trigger-only fuel point beside a company with a different parent | Uncertain; skip new support by default | Proximity alone does not establish ownership. |

The public Gallon Oil prefab paths include `nm_gas_station1_depot` and `nm_truckstop1_depot`; a Company relationship and “depot” filename are therefore counterexamples to blanket private-fuel filtering. Official `gas_station` context tags help interpret semantics, but one mixed truck-stop prefab is excluded from that context because of player-spawn orientation, not private fuel. The code does not turn those tags into an ownership rule.

The Castores distribution family supplies both the freight-yard and inferred fleet-fueling case; these are one physical layout, not two independent private-family validations. Mexicali has exactly two original truck GAS groups, no native car groups, same-parent Company `cas_tc1`, and pumps inside the lot behind the warehouse. Default-visible geometry includes fencing, pump assets and logistics signage. [Private-yard evidence](../../local_outputs/work/2026-10-21_01-30-52/private-fuel-evidence/private-yard-evidence.json) and [annotated local plan](../../local_outputs/work/2026-10-21_01-30-52/private-fuel-evidence/private-yard-plan.svg). The inspected original texture has distribution/logistics wording; a Pemex brand by itself supplies no fuel-type proof.

[Mixed/public/composite inventory evidence](../../local_outputs/work/2026-10-21_01-17-55/fuel-site-inventory/FINDINGS.md) contains exact service UIDs, transforms, Company references and source hashes. Early sample labels for Socorro/Las Cruces were reversed; decoded Company city tokens, not those provisional labels, resolve the locations. The final tour uses verified source identifiers.

These ignored evidence files are local-only in the research worktree; another checkout needs verified copies at the linked paths. Original game/mod files remain unmodified and excluded from Git. No new user screenshot is required; no screenshot is cited from an external attachment path.

## Public interface

The existing commands accept either `--fuel-policy broad|realistic` or `--fuel-selection-json PATH`, never both:

```bash
PYTHONPATH=src python3 -m ats_road_trip generate-map-fix SOURCE.scs \
  --processor fuel --fuel-selection-json docs/examples/selective-fuel-tour/selective-policy.json \
  --experimental
```

The existing `generate-map-fuel` and `analyze-map` commands accept the same selection. Default and explicit broad behavior are identical. A bare `--fuel-policy realistic` has no reviewed catalog: unreviewed groups remain uncertain and are skipped by default. Use a reviewed configuration to admit known suitable groups. Passing nondefault fuel configuration without selecting the fuel processor is rejected.

`FuelSelectionConfig` is immutable. Strict JSON schema 1 contains mode, uncertain-case behavior and reviewed layout rules; [delivered policy](../examples/selective-fuel-tour/selective-policy.json). Each rule pins descriptor path/hash, visual model path, variant token, active parts and definition additional-parts, with per-GAS role/confidence/reason/evidence. Duplicate JSON fields, overlapping rules, unknown fields, invalid types and source/state drift are rejected. These checks pin descriptor bytes, visual model path and declared parts/state fields; they do not pin PMD/PMG/texture bytes in the general classifier. A same-path visual override can invalidate the reviewed signs/geometry without triggering descriptor drift. The finite tour separately checks the actual winning Castores visual resources against the evidence hashes. Later visual overrides require renewed review. None of these checks is a complete collision or runtime accessibility proof.

A layout catalog is reusable across placements but does not classify unseen models automatically. The four delivered rules distinguish six test placements spanning five visual model families. Explicit UIDs occur in the [test manifest](../examples/selective-fuel-tour/manifest.json), not the suitability classifier.

## Delivered comparison and effective-stack setup

The bounded `analyze-fuel-selection-batch` / `generate-fuel-selection-batch` commands use the six-site manifest, original low-to-high map/resource inputs and explicit selection. They validate the installed exact game version, sector owner/hash and target UID, plus source/price/context identities. The audit embeds the complete fuel policy and canonical SHA-256.

The comparison variants are G1 BROAD and G2 SELECT, alternatives to activate separately. G2 restores required source-sector bytes around exclusions so a retained lower r9 does not restore those generated car points. This temporarily omits other generated car fuel/parking additions in those replaced sectors. Original map services, nodes, geometry and native facilities remain. Outside those sector overrides, retained source fixes continue to apply. Fuel prices are processed independently for explicitly selected original price packages and must match between alternatives.

This is a fuel-only comparison. It does not complete parking strategy exclusivity for the whole active map stack, modify parking geometry, or implement the full realistic preset. Keep N2 independent and disable the older F/A/B/C/C2/E station experiments during the comparison. General selective source packages must replace their same-source broad fixes according to their own handoff; do not assume the bounded guards exist in every generation workflow.

**Observed locally — delivered, 2026-10-21:** [complete test ZIP](../../local_outputs/generated/2026-10-21_01-47-10/g1-g2-fuel-selection-tour-ats-1.61-r1-experimental.zip), [testing README and results table](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/README.md), [exact load order](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/LOAD_ORDER.md) and [per-pump reasons/transforms](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/pump-decisions.json). The bundle includes the two actual SCS files, seven annotated PNG/SVG plans, source-pinned configs, exact command arrays, generation reports and independent audit receipts. These ignored local artifacts need verified copies in another checkout.

| Alternative | Bytes | SHA-256 | New car fuel groups / retained native groups |
| --- | ---: | --- | --- |
| [G1 BROAD r1](../../local_outputs/generated/2026-10-21_01-47-10/g1-broad-r1-fuel-tour-ats-1.61-experimental.scs) | 1,209,551 | `95623693dca7796457f78bdcdd1d8fdd94bc4caf53f93b726b3729b51d8edc6c` | 9 / 4 |
| [G2 SELECT r1](../../local_outputs/generated/2026-10-21_01-47-10/g2-select-r1-fuel-tour-ats-1.61-experimental.scs) | 1,202,974 | `91b89746a9bd92a913a309c513becfc055065ccec71a41057593573a17affe63` | 1 / 4 |

Enable **exactly one G variant above all declared maps, seven retained r9 fixes and Real companies**; keep independent N2 above its retained background. Disable N1 and old F/A/B/C/C2/E experiments. Source-relative order below the overlay stays unchanged. No source map or historical package is removed or rewritten. Both alternatives replace five `.base` resources; only three of those have matching lower r9 overrides. Those three carried 18 added car fuel services, seven standalone rest triggers and prefab aliases carrying further rest edits, including non-tour additions. Both variants temporarily displace that generated content before adding their own selected fuel groups; original source facilities remain. No matching r9 auxiliary/layer payload exists for these five stems. This bounded resource restoration is not a whole-world parking exclusion proof.

The batch now rejects policy-skipped groups whose service or resolved nodes extend into an unguarded neighboring resource; the adjacent-sector regression emits no archive. All six real source groups pass that boundary condition using the reconstructed immutable generation halo. The delivered SCS files were generated at implementation milestone `2b19c32`; this later safety check adds selective report provenance and changes no gameplay bytes at these sites. [Boundary receipt](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/audits/actual-source-boundary-check.json).

The visit list is Roswell retail G01 plus garage G05, Artesia native control G06, Las Cruces mixed public stop G02, Mexicali Castores yard G03 and optional distant Lufkin composite G04. G01 F1 already tests uncertainty if G04 is skipped. The garage pump is **G05 F2**, from the effective ProMods garage descriptor; an older cached base-game reference had GAS0. Independent archive review caught that evidence mismatch; production already used the correct source. [Correction receipt](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/audits/garage-evidence-correction.json). Old evidence remains unchanged and is not the delivered plan baseline. Gameplay is later user validation.

## Verification

**Observed locally:** full ATS Expansion broad generation still produces 894 added car points, 41 garage points and 515 changed stations. All 202 generated pre-rest sector hashes and 106 private fuel resources match the historical r9 fuel-planner output; this does not claim equality to the full combined r9 archive. [Legacy receipt](../../local_outputs/work/2026-10-21_01-18-31/selective-fuel/legacy-real-source-equality.json). The final suite passes **460 tests**, covering default/explicit broad equality, mixed selection, native preservation, uncertainty, configuration/drift, malformed skipped graphs, subset aliases, pricing/context composition, source guards, cross-resource exclusion rejection and analysis without a mod writer.

**Observed locally — independent actual-output audit:** [byte/graph audit](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/audits/independent-actual-pair-audit.json) independently counts nine versus one new services/nodes, preserves four native car groups, original service/node/rest/Company bytes and PPD opaque sections, and validates links, no orphan additions, metadata prefixes, resource inventory and ZIP CRC. G2's four fully excluded source resources are exact originals; Roswell composes only G01 F0 while retaining its skipped groups without additions. Both alternatives supply identical 27-country price payloads.

**Observed locally — declared effective-stack audit:** [resource/visual/context audit](../../local_outputs/generated/2026-10-21_01-47-10/fuel-selection-tour/audits/independent-effective-stack-audit.json) checks original sources plus retained r9, background and N2. Selected `.base` resources resolve to the G overlay, lower aliases cannot reintroduce excluded services, original alias attributes and existing empty/excluded context state survive (no positive tag sets exist at these selected originals), country resources equal retained r9 repairs, and pre-generation original input identities remain unchanged. The winning Castores PMD/PPD and sign DDS extracted from its original TOBJ match reviewed evidence. PMG has original-provider proof and a current hash, without a prior evidence byte pin. N2's whole archive/payload match their historical hashes. [Delivery CRC/hash receipt](../../local_outputs/work/2026-10-21_01-18-31/selective-fuel/delivery-verification.json).

Root reviewed the audit logic and concrete artifacts, corrected the garage reference and checked all final plans. No game or profile was changed. Purchases, billing, access restrictions, physical reachability and gameplay acceptance remain Unknown until user testing; static success does not convert inferred suitability into fuel chemistry or ownership proof.
