# Metadata refresh: map r5 and courier r1

Historical handoff: the selected four-Ford M2D artwork is now available in [map r6 with unchanged courier r1](MOD_METADATA_REFRESH_1_61_R6.md). This r5 archive and its recorded hashes remain unchanged.

**Observed locally — ATS 1.61.3.18 project, inspected 2026-10-18:** the eight refreshed packages preserve every gameplay resource path and byte from the [r4/r0 delivery](OVERNIGHT_TEST_BATCH_1_61_R4.md). Only icons, paragraph descriptions, manifest revisions and embedded provenance changed. No game-data inspection or fix regeneration was needed for this release.

## Download and replacement

Eight-mod ZIP (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_15-24-10/szczerbs-road-trip-test-batch-ats-1.61-map-r5-courier-r1-experimental.zip`), 68,461,510 bytes.

SHA-256: `866188de68a9e83aaba6045f6f7344c12d66c759a09ffb8b221c6973950caa84`.

It contains seven source-specific map/connector fixes `1.61-r5-experimental`, Practical Courier Jobs `1.61-r1-experimental`, and `README.txt`. Disable the earlier copy of each fix when replacing it; keep the matching source map enabled. There is no need to interrupt an ongoing r4/r0 gameplay test. This release was not installed automatically.

## Presentation changes

**Documented — user choice, 2026-10-18:** map artwork M2 is the navy/cream/teal scene with three parked cars, a pump and P sign. Each of the seven packages has its own map/connector footer. Two Ford-car variants, M2A and M2B, remain alternatives for later selection.

Courier artwork uses the explicitly requested headline `JOB TYPES COMPAT`. J1B (green frame/red Mustang), J2B (navy/gold) and J3B (red Mustang with compatibility checklist) are saved proposals. The package provisionally uses J1B; this is not a user selection. [Saved exports, prompts and display notes](../../assets/mod-icons/README.md).

Descriptions explain fuel/rest effects, the local rest rule, experimental petrol prices and pending game checks in separate paragraphs. Each map description lists the complete confirmed combination, including both connectors and all four ProMods packages. Exactly one `(THIS MOD)` identifies the relevant fix immediately above its source. Optional background, Practical Courier Jobs and Food/Medical/Rideshare entries are included. OtherMaps explicitly says it changes missing petrol prices and has no station/rest edits, despite using shared family artwork.

The courier description explains 58 additional reviewed stock job types, shared vehicle-class effects and Quick Jobs, nine unchanged vehicle transfers, add-on eligibility limits and load priority. The tool renders counts from the actual plan rather than always claiming 58.

## Generation and verification

**Observed locally — 2026-10-18:** all **246 tests pass**. Focused coverage includes description structure and priority, map-labelled artwork selection, no wrongly labelled fallback, default/explicit courier artwork and the analysis-only boundary.

The one-run script `local_outputs/work/2026-10-18_15-24-10/refresh_delivery.py` loads the frozen r4/r0 candidate list and checks each source ZIP for CRC, duplicate paths and agreement with its embedded resource inventory. It passes those same gameplay bytes to the existing package writer with new metadata. It then compares the complete resource dictionaries and inventories, icon bytes/hashes, manifest fields, paragraph boundaries and current-mod markers. It checks source archives remain byte-identical. The outer ZIP CRC and exact nine-entry inventory also pass. An independent GPT-6 Luna review confirms these results. Nineteen new JPEGs pass writer validation and FFmpeg decoding. Documentation QA checks 89 Markdown files, 699 links, 26 heading fragments, 25 task records, unchanged identities for all 12 inputs and 26 artifact exclusions without errors.

Machine evidence: `local_outputs/work/2026-10-18_15-24-10/delivery-result.json`, `refresh-delivery.log`, `full-tests.log`, `description-previews/` and the independent review in the same ignored run. The package reports retain original generation provenance and add a `metadata_refresh` record with the previous archive hash/version and explicit scope. Large artwork originals and generation records are under that run's `artwork/` directory.

**Unknown — gameplay:** finite fuel quantity, petrol price/payment, car rest and new courier pickup/cargo fit/completed delivery remain pending under [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). Continue the [manual checklist](MANUAL_TEST_CHECKLIST.md); metadata equality does not establish a runtime result.

## Current tooling

`generate-map-fix` now defaults to r5 and auto-selects reviewed map-labelled combined art. `generate-courier-eligibility` defaults to r1, selects separate courier art and accepts `--icon`. `generate-map-fuel` keeps its r2 default. General map courier generation remains unsupported. [Metadata contract](MOD_METADATA.md), [processor guide](COMPATIBILITY_PROCESSORS.md), [courier usage](PRACTICAL_COURIER_GENERATOR.md), [ADR-0013](../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md).
