# Selected M2D artwork: map r6 and unchanged courier r1

**Documented — user selection, 2026-10-18:** use M2D, the navy fuel/parking icon with Mustang 1967, Crown Victoria 2006, Bronco 2024 and F-150 2023, for map fixes. The user confirms both corrected previews display in chat and the Windows-local HTML gallery is useful. J3B remains the courier favorite with a key-fob reservation; no final courier replacement is approved.

**Observed locally — ATS 1.61.3.18 project, inspected 2026-10-18:** all seven map presets now use M2D with the matching map/connector footer. The current generator default is map revision **6**. Legacy fuel remains r2 and courier remains r1. [Original corrected model prompts](../../assets/mod-icons/PROMPTS_V3.md), [selected map-label edit prompts](../../assets/mod-icons/PROMPTS_M2D_SELECTED.md).

## Delivery

Eight-mod ZIP (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_16-16-22/szczerbs-road-trip-test-batch-ats-1.61-map-r6-courier-r1-experimental.zip`), **68,459,553 bytes**.

SHA-256: `c3937371157683b60eb7c8541d8bb4ddcbd89a48af73ec4abfa3eb91d0c76203`.

The ZIP contains seven **r6** map/connector `.scs` files, the exact unchanged **r1** Practical Courier Jobs archive from the [r5/r1 delivery](MOD_METADATA_REFRESH_1_61_R5.md), and `README.txt`. Map fixes change only their icon, version-labelled description, manifest revision and report provenance. The courier archive retains provisional J1B artwork. J3B preference has not silently changed the courier preset or archive.

Disable the earlier copy of each map fix when replacing it. Keep each fix directly above its own source, using the full order in the descriptions/README. An existing r4/r5 gameplay test does not need to be interrupted. No live installation or profile modification occurred.

## Verification and limits

**Observed locally — 2026-10-18:** source and output ZIP CRCs, duplicate-path checks, full gameplay resource dictionaries and embedded hash inventories pass for all seven map packages. Every generated resource path and byte is identical to r5; r5 was independently checked against the original r4 gameplay batch. The entire courier archive is byte-identical to the previously delivered r1. OtherMaps remains price-only. The outer ZIP contains exactly eight mods plus README and passes CRC and SHA verification.

All seven preset JPEGs pass writer validation and FFmpeg decoding at **276x162**. They were visually inspected after export; ATS Expansion reuses the selected M2D JPEG exactly. The other six footer-only imagegen edits preserve four-car composition, parking direction, free reversing space, pump/P sign and title. Runtime packaging uses static tracked bytes. Imagegen was used for art preparation; FFmpeg only performed final format/downscale exports.

The **56 focused metadata, artwork, writer, bulk-workflow and CLI tests pass** for this update. The last complete suite remains **246 tests**, recorded in the r5 milestone. No utility gameplay algorithms changed. Work, large artwork originals, exact generation records, source candidates, delivery fingerprints and comparison results are retained under ignored `local_outputs/work/2026-10-18_16-16-22/`. An independent GPT-6 Luna review confirms package equality, exact selected ATS artwork, unchanged courier bytes, manifest/description metadata and bundle inventory/CRC/SHA. Documentation QA passes for 92 Markdown files, 726 links, 26 heading fragments, 25 task records, all 12 unchanged input identities and 26 artifact exclusions. Evidence is recorded in the same run.

**Unknown — gameplay:** fuel quantity/price/payment, car rest/fatigue recovery and Mustang job pickup/cargo fit/completed delivery remain under the existing [manual checklist](MANUAL_TEST_CHECKLIST.md) and [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). Artwork selection and byte preservation do not settle these tests.

Related: [metadata contract](MOD_METADATA.md), [current state](../project/CURRENT_STATE.md), [artwork guide](../../assets/mod-icons/README.md), [TASK-0025](../tasks/active/TASK-0025-refresh-mod-icons-and-player-descriptions.md).
