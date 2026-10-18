# Crown Victoria versus Mustang: stock courier cargo review

Inspected: 2026-10-18. Target: installed ATS 1.61.3.18s (`def.scs`, pack 1.61.3.18). This is a read-only review of extracted stock definitions; it does not establish live offers, successful loading, or delivery.

## Result

**Observed locally:** stock Ford definitions tag `ford.victoria_06` as `sedan`, and `ford.mustang_67` as both `muscle` and `veteran` (see [courier research findings](COURIER_RESEARCH_FINDINGS.md)). Of 149 stock `car_job_data` units, 147 list `sedan`, while 54 list at least one of `muscle` or `veteran`. Thus a Mustang is explicitly admitted to far fewer stock job units. At rating 0 the comparison is 7 Mustang-tagged units versus 29 sedan-tagged units, as recorded in [availability research](COURIER_JOB_AVAILABILITY_RESEARCH.md).

**Observed locally:** the Mustang exclusion gap is not evidence of a trunk-capacity rule. Stock job units select a vehicle class, cargo definition identifiers (when applicable), endpoint context tags, distance interval, and rating. They expose no vehicle cargo-volume field or cargo-to-vehicle fit dimensions. Cargo definitions give names, fragility/value, icons, and toy-seat accessory paths; those fields do not state real package dimensions or a Mustang loading limit.

Parser-based comparison of every unit gives 147 sedan units, 54 Mustang-tagged units, 52 in both sets, **95 sedan-only units**, and **2 Mustang-only units**. The earlier 68-unit figure was caused by a regex-based block scan that missed nested/multiline unit structure; it is withdrawn. Counts below use `ats_road_trip.sii.parse_units`.

## Sedan-only job families

Here “sedan-only” means a unit lists `sedan` and lists neither `muscle` nor `veteran`; other classes may also be allowed by that unit. There are 95 such units. The table groups units by job family; repeated units are rating tiers or standard/express/fragility/value variants, not distinct real-world cargo sizes. The seven standard Car Jockey units are shown separately because they have no cargo field.

| Job family | Units | Definition evidence (semantic names/comments, not localized UI strings) |
| --- | ---: | --- |
| `car_job.mparts_*` — Machine Parts | 13 | Cargo definitions use box accessories. |
| `car_job.tsparts_*` — Truck Small Parts | 8 | Cargo definitions use box accessories. |
| `car_job.jockey_*` — Car Jockey | 7 | No `cargos[]`; vehicle-transfer family, not loose-cargo evidence. |
| `car_job.chem_*` — Chemical Samples | 7 | Sample variants; box/briefcase accessories. |
| `car_job.tdiag_*` — Tractor Diagnostic Module | 7 | Standard, fragile, and valuable variants; box accessory. |
| `car_job.hcert_*` — Livestock Health Certificates | 5 | Paperwork; envelope/briefcase accessory. |
| `car_job.grid_*` — Grid Relay Components | 5 | Parts variants; box accessory. |
| `car_job.soil_*` — Soil Samples | 4 | Sample variants; briefcase accessory. |
| `car_job.ore_*` — Ore & Mineral Samples | 4 | Sample variants; briefcase accessory. |
| `car_job.confid_*` — Confidential Delivery | 4 | Parcel variants; briefcase accessory. |
| `car_job.drill_*` — Drill Core Samples | 3 | Sample variants; briefcase accessory. |
| `car_job.oparts_*` — Outboard Engine Parts | 3 | Parts variants; box accessory. |
| `car_job.propel_*` — Replacement Propeller | 3 | Cargo definition uses a box accessory; title gives no geometry. |
| `car_job.unident_*` — Unidentified Shipment | 3 | Shipment variants; box accessory. |
| `car_job.jtools_*` — Job Tools | 2 | Cargo definition uses a box accessory. |
| `car_job.seedl_*` — Plant Seedlings | 2 | Standard/fragile variants; box accessory. |
| `car_job.subkeys_*` — Substation Keys | 2 | Envelope/box accessory. |
| `car_job.seals_*` — Transfer Seals | 2 | Briefcase accessory. |
| `car_job.undisc_*` — Undisclosed Consignment | 2 | Box accessory. |
| `car_job.aucdocs_46` — Livestock Auction Documents | 1 | Paperwork; envelope/briefcase accessory. |
| `car_job.cusdocs_46` — Customs Documents | 1 | Paperwork; briefcase accessory. |
| `car_job.manif_26` — Manifest | 1 | Paperwork; document accessory. |
| `car_job.waybill_26` — Waybill | 1 | Paperwork; document accessory. |
| `car_job.restock_0` — Fill-In Restock | 1 | Restock cargo; box accessory. |
| `car_job.misdel_0` — Misrouted Supplier Delivery | 1 | Delivery cargo; box accessory. |
| `car_job.crewsup_0` — Crew Supplies & Snacks | 1 | Supplies; box accessory. |
| `car_job.tmaps_0` — Tourist Maps | 1 | Paper/map cargo; document accessory. |
| `car_job.ffinder_0` — Fish Finder Unit | 1 | Equipment cargo; the definition gives no dimensions. |

Totals reconcile to 95 sedan-only units. The names are semantic family descriptions derived from stock unit identifiers and cargo `name` localization tokens; rendered localized UI titles were not verified. No numeric dimensions or load-volume values appear in the inspected `car_cargo.sii` records.

**Observed locally:** the other 52 sedan-tagged units also list `muscle` or `veteran`, so the Mustang class tags already admit them. The two Mustang-only units are `car_job.prem_46` and `car_job.prem_e46`; both have no `cargos[]`, require rating 4.6, and use the `car_dealer` context at both endpoints. Their job names use `@@cjob_premium_allocation@@`. They allow `veteran`, `sport`, and `muscle`; the definitions do not explicitly call them Car Jockey jobs. **Unknown:** whether any listed cargo meshes or vehicle-transfer jobs are physically awkward or impossible to attach to/drive with the Mustang in gameplay.

## Answer to the fit question

**Unknown:** a Crown Victoria fit does not prove a Mustang fit in game. The static evidence supports a narrower conclusion: ATS classifies the two cars differently for job eligibility, but it does not encode trunk capacity or cargo-size compatibility in these job/cargo records. The sedan-only cargo mix includes paperwork, samples, parcels, parts, small equipment, and seven standard-family vehicle-transfer definitions. Those accessory paths suggest presentation as carried items; they do not establish in-car collision geometry, attachment support, or successful completion. In particular, do not infer that the propeller title makes that shipment physically oversized, or that “samples” guarantee it fits.

The defensible static explanation is the explicit `vehicle_types[]` whitelist. Other possible restrictions—job context, rating, distance and available endpoints—also affect eligibility. Whether the game intentionally withholds sedan-only families from a muscle/veteran Mustang, and whether adding a class tag yields usable contracts, requires a controlled Road Trip session. No cargo dimensions, real-world trunk-volume comparison, map fix, or generated mod was used here.

## Source and reproducibility

**Observed locally:** primary inputs are `local_outputs/extracted/game-def/def/car_job_data.sii` and `car_cargo.sii`, selective extracts from installed ATS `def.scs`. SHA-256 values are `car_job_data.sii`: `4a62420d6bd79086fdf4fa1caa3e37a6bb53636a1c82d65b78ab7eb0049b2d28`; `car_cargo.sii`: `230c1aef59446b944e02f138ca2802c3560d3e9c2663070120e6cbcd854f4ffa`. The parsed sedan-only unit IDs and grouped counts are in the ignored reproducibility inventory (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-23-44/sedan-only-courier-units.json`). Vehicle tags and earlier counts are summarized in [COURIER_RESEARCH_FINDINGS.md](COURIER_RESEARCH_FINDINGS.md) and [COURIER_JOB_AVAILABILITY_RESEARCH.md](COURIER_JOB_AVAILABILITY_RESEARCH.md). No source assets were modified and no full-game extraction was performed for this review.
