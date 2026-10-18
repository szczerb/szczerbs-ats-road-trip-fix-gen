# Original mod artwork

## Current fuel/rest and courier proposals

Created and inspected: 2026-10-18. **User selection for the next map batch: M2**, the navy/cream/teal frame with three parked cars, pump and parking sign. M2A/M2B are further requested Ford alternatives; they have not replaced the chosen M2. Courier **J1B is provisional**, with the choice among J1B/J2B/J3B still open. The user explicitly requested the courier headline `JOB TYPES COMPAT`.

**Documented — later user feedback, 2026-10-18:** the Windows-local HTML gallery displays successfully. J3B is the courier favorite, with reservations about its car-like key fob; it is not final approval. The existing provisional preset/package stays J1B. Corrected M2C/M2D retain M2A's rear-view parking layout, use Crown Victoria 2006, and add Bronco 2024 in the four-car option. No new mod package or default icon replacement is made in this proposal round.

| Label | Small export | Motif / status |
| --- | --- | --- |
| M1 | [JPEG](proposals-v2/m1.jpg) | Green frame, two cars and parking sign |
| M2 | [JPEG](proposals-v2/m2.jpg) | Navy frame, three parking bays and pump; selected |
| M3 | [JPEG](proposals-v2/m3.jpg) | Green frame, four parked cars |
| M2A | [JPEG](proposals-v3/m2a.jpg) | Historical rear-view proposal; wrong 1956 Victoria |
| M2B | [JPEG](proposals-v3/m2b.jpg) | Historical front-view proposal; wrong Victoria and obstructive wheel-stop layout |
| M2C | [JPEG](proposals-v4/m2c-3-fords.jpg) | M2A location/direction; Mustang 1967, Crown Victoria 2006, F-150 2023 |
| M2D | [JPEG](proposals-v4/m2d-4-fords.jpg) | Four-car version with Bronco 2024 and clear reversing space |
| J1 / J1B | [Original](proposals-v2/j1.jpg) / [new headline](proposals-v3/j1b.jpg) | Green frame, red Mustang, landscape; J1B provisional |
| J2 / J2B | [Original](proposals-v2/j2.jpg) / [new headline](proposals-v3/j2b.jpg) | Navy/gold, cream Mustang, route and parcel |
| J3 | [JPEG](proposals-v2/j3.jpg) | Cream/green original alternative |
| J3B | [JPEG](proposals-v3/j4.jpg) | New navy/teal checklist, red Mustang; current favorite, not final selection |

The seven [combined-map presets](map-compatibility/) reuse M2 with each map/connector's own footer. The separate [courier preset](practical-courier-jobs.jpg) currently copies J1B. These are original project artwork, not copied game assets. The art is illustrative, not an authoritative specification of vehicle geometry or cargo capacity. OtherMaps uses shared family art while its description states its price-only scope.

[Initial prompts](PROMPTS_V2.md) and [corrected Ford prompts with year evidence](PROMPTS_V3.md) record built-in imagegen requests. Root prepared the art; Sol handled bounded description work and Luna reviewed selection and packages. All imagery/text edits used imagegen; FFmpeg performed only final size/format export (276x162, Lanczos, JPEG quality 2, yuvj444p). Every packaged export was decoded, visually reviewed at native size and validated by the writer. Large source PNGs and machine provenance remain ignored under `local_outputs/work/2026-10-18_15-24-10/artwork/` and `local_outputs/work/2026-10-18_16-10-22/artwork/`.

**Observed locally — user report, 2026-10-18:** Markdown references to local Linux image paths displayed broken-image placeholders. The user did see the six map-footer previews returned as tool image content. Variants were therefore re-presented as actual tool image content; final client visibility/choice was pending at handoff. The user then reported another failed gallery display. Copies in the Windows visualization directory plus a local HTML gallery finally worked, explicitly confirmed by the user. Use that gallery for further comparisons. Do not infer approval from an invisible image or a preselected question option.

[Metadata-only r5/r1 handoff](../../docs/reference/MOD_METADATA_REFRESH_1_61_R5.md) and [artwork/description decision](../../docs/architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md).

## Historical fuel-only artwork

Created and inspected: 2026-10-17. **User selection: C**, the green sign with a pump and four passenger cars. Its top text is `GAS STATIONS FIX`; bottom text is `ATS EXPANSION`. A and B remain alternative proposals. All three tracked files are original project artwork exports, not game assets or copied ATS logos.

| Option | File / motif | Bytes | JPEG SHA-256 |
| --- | --- | ---: | --- |
| A | [Pump and one car](ats-expansion-a.jpg) | 29,055 | `3dc705ce50b03bfe7e7f9e992fc4fadb63ac7bed1f554134265e5dcb99f58c1f` |
| B | [Nozzle and two cars](ats-expansion-b.jpg) | 25,487 | `f7387266da5cfd4ffd3145d039f0037af37c816b998a923b64a8d70d0ade37b0` |
| C | [Green sign, pump and four cars (selected)](ats-expansion-c.jpg) | 28,404 | `5fc8e0d416a338cdc8d4aa3b2ebb00cc71ee593a2c90771eebd8a1d40a9d6ea8` |

## Generation and export

GPT-6 Luna / medium prepared three separate built-in **imagegen** requests, one per proposal, with no API/CLI fallback. [Exact prompts](PROMPTS.md) preserve the requests verbatim. The use case is brand/icon design; the recorded prompt asset label does not select an API model. The originals were copied from the tool's generated-images destination into ignored `local_outputs/artwork/icon-proposals/`:

- `proposal-a-pump-one-car.png`, 1637x960.
- `proposal-b-nozzle-two-cars.png`, 1637x961.
- `proposal-c-pump-several-cars.png`, 1637x961.

The root agent inspected each original and exported the three JPEGs using FFmpeg, Lanczos scaling to 276x162, one frame, JPEG quality 2 and `yuvj444p`. This is the final format/size export; no subject, text or palette edits were applied after generation. All exports were decoded with FFmpeg, visually reviewed at native size and checked by the package writer's JPEG header validation. The large generated originals remain ignored; these small, self-contained JPEG exports and prompts are tracked. Repeating a creative generation is not byte-deterministic; reusing the tracked exports makes package generation deterministic.

For another map, prepare a separately reviewed icon with that map's own bottom label. The CLI does not edit embedded text or automatically choose artwork. Always pass the selected map's JPEG via `--icon`. See the [metadata contract](../../docs/reference/MOD_METADATA.md) and [sample command](../../docs/reference/OVERLAPPING_FUEL_SAMPLE.md#reproduce).

## Map-labelled C exports for full-map generation

2026-10-17: `reforma-c.jpg`, `promods-canada-c.jpg`, `western-canada-c.jpg` and `alaska-c.jpg` reuse the selected C illustration. Their footer labels were replaced deterministically during asset preparation with FFmpeg drawbox/drawtext (DejaVu Sans Bold, cream text on dark green), followed by JPEG quality 2 / yuvj444p export. No new image-generation request is needed for runtime builds. All are 276x162 and were visually inspected. The generator selects these tracked map-specific JPEGs by short-name slug, so package creation itself makes no LLM call or image edit. The large original C image and exact original generation prompt remain recorded above.

## Key motif evidence

**Observed locally — ATS 1.61.3.18, inspected 2026-10-18:** the enabled practical policy includes `car_job.subkeys_26` and `car_job.subkeys_v46`, commented Substation Access Keys, using `car_cargo.subst_keys` and `car_cargo.v_subst_keys`. The key motif has a real cargo basis, but the stock definitions do not describe car ignition keys; J3B's automotive-looking fob can therefore mislead. All nine vehicle-transfer definitions remain unchanged. The adjacent `keys_seals` policy group also includes intermodal seal cargo; these are not vehicle transfers. [Cargo review](../../docs/reference/MUSTANG_COURIER_CARGO_REVIEW.md), [enabled policy](../../docs/examples/mustang-practical-courier.toml). Bounded evidence review by GPT-6 Luna / medium confirmed exact IDs and installed vehicle series tokens.
