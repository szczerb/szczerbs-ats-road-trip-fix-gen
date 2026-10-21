# G1 fuel tour feedback and station-level policy — 2026-10-21

**Implemented follow-up — 2026-10-21:** [realistic r10](REALISTIC_MAP_REPLACEMENTS_1_61_R10.md) implements the accepted five additions / four native groups / three omitted facilities in actual archives and delivers the complete map replacements. The readiness section below is the historical intake state. No repeat G2 tour, profile, route or pump matrix is required; later feedback is opportunistic during career play.
**Documented — first-hand user report, ATS 1.61 comparison:** the user visited all six sites with **G1 BROAD r1**, reports that everything works, and filled the handoff table. **Observed locally — table inspection:** the G1 result cells contain `works`; G2 cells are blank. The user explicitly declines individual-pump suitability distinctions for this sample. Record six-site interaction success; do not infer separately controlled per-pump trials, completed purchases, numerical prices/billing, truck controls or reload results. G2 gameplay is unreported.

## Accepted site decisions

| Site | Future added passenger-car fuel eligibility | User's reason |
| --- | --- | --- |
| G01 Roswell retail | Include the whole station | Appropriate public car-fueling location. |
| G02 Las Cruces mixed public stop | Include the whole station | Public station is suitable; no separate pump exclusions requested. |
| G03 Mexicali Castores | Exclude our car additions | Logistics hub full of trucks; a normal public petrol station is nearby. |
| G04 Lufkin | Exclude our car additions | User identifies the setting as a cattle ranch, with fuel appearing intended for farming equipment. |
| G05 Roswell player garage | Exclude our car additions | User expects the truck garage's supply to be diesel for trucks. |
| G06 Artesia | Include the whole station | Appropriate public station; retain native car groups and enable the remaining group. |

These are **user-selected gameplay suitability rules**, not documented fuel inventory or legal public-access restrictions. In particular, G04's `kdgrain` context and generic trigger alone did not establish ranch/equipment use; the user's in-game observation adds that setting evidence. Company names, proximity and truck-correlated source flags alone remain insufficient blanket exclusion rules.

For the reviewed six-site baseline, applying these choices would add five car fuel groups, omit four and retain four native car groups. This is an expected policy outcome, not a newly generated or tested package. The user's approved public sites G01/G02/G06 supersede the old G2 decisions that omitted G01 F1, G02 F0/F1 and G06 F2. The granular implementation can select every group of an approved station; it does not require the player to judge every pump. Approval applies to these inspected examples and their justified reusable facility rules, not automatically to every unseen model or placement.

## Evidence

[Unchanged snapshot of the user-edited results table](../../local_outputs/work/2026-10-21_20-08-07/g1-fuel-feedback/README-user-feedback.md) and [provenance](../../local_outputs/work/2026-10-21_20-08-07/g1-fuel-feedback/provenance.json). These are ignored project-local evidence; another checkout needs verified copies at these relative paths. The current chat clarification supplies the final inclusion/exclusion decision above. Original user notes, handoff files, archives and source/config snapshots remain unchanged.

## Readiness for full-map realistic output

**Observed locally — current interfaces:** general source-map fuel generation already accepts `FuelSelectionConfig`; the four-rule delivered catalog is a bounded reviewed sample, not a complete all-map classification inventory. The old G2 and its uncertainty defaults do not implement the user's revised decisions. Future work must update facility rules, review/classify effective source-map sites, preserve context/price/native repairs, and report unsupported or uncertain cases with coverage.

**Documented — ADR-0022 / observed locally — processor interfaces:** exclusive parking strategies remain unimplemented as a general selector/composed workflow. `rest` enables truck-area car twins; separate station commands generate source-pinned bays. F BATCH over r9 deliberately retains both generated strategies and cannot be relabeled as the final realistic preset. Dedicated-bay output must be generated from an audited source baseline with selected fuel/price/context repairs, omitting generated truck-area car access and preserving original native facilities. No acceptable bay means a reported skip, with no truck-space fallback.

Prior parking feedback still requires engineering work: natural curb placement, P04 activation, P09 orientation and attribution of broad Mexican activation areas to source versus generated rest items. Existing census/model evidence should drive that work before another driving request. A full-map candidate may have explicit supported/skipped coverage; it must not claim all stations are solved from the small test batch.

There is **no requirement for another full G2 tour or new pump-level research from the user before implementation proceeds**. After implementation and static effective-stack audits, a short regression should compare a public inclusion, an exclusion and representative dedicated parking. More driving should be requested only for a concrete unresolved runtime question. Complete all-map fuel plus exclusive dedicated parking remains an implementation/generation milestone, not a ready-to-run preset at this intake.

## Links

- [Current fuel implementation, historical G1/G2 artifacts and audits](SELECTIVE_CAR_FUELING.md)
- [Parking strategy requirement](../architecture/decisions/ADR-0022-select-mutually-exclusive-car-parking-strategies.md)
- [Existing parking report and outstanding geometry questions](STATION_PARKING_FORECOURT_TOUR_FEEDBACK_2026_10_21.md)
