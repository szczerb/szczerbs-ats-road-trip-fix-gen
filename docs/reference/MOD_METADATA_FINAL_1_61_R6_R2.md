# Approved metadata delivery: map r6 and courier r2

Historical delivery: [Job Types Compat Mustang r3 and map r7](MOD_METADATA_RENAME_1_61_R7_R3.md) use the requested unified name while preserving these exact gameplay resources and approved icons. This earlier archive and its fingerprints remain unchanged.

**Documented — user approvals, 2026-10-18:** M2D is the selected four-Ford fuel/parking artwork for all seven map fixes. J3C is the selected Mustang courier artwork, with a mechanical access-key bunch, parcel, envelope and three compatibility check marks. The user confirms J3C is visible and explicitly approves it. The original job-cargo evidence and exact edit prompt are linked from the [artwork guide](../../assets/mod-icons/README.md).

## Download

Final eight-mod ZIP (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_16-35-26/szczerbs-road-trip-test-batch-ats-1.61-map-r6-courier-r2-experimental.zip`), **68,457,764 bytes**.

SHA-256: `b4a8c33f33721f78cd695321d5085b885ee9313c8721f328ec071014cab7ff44`.

Standalone Practical Courier Jobs r2 (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_16-35-26/szczerbs-road-trip-practical-courier-jobs-muscle-1.61-r2-experimental.scs`).

The ZIP includes seven complete **map r6** archives copied byte-for-byte from the [r6/r1 batch](MOD_METADATA_REFRESH_1_61_R6.md), new **courier r2**, and `README.txt`. Only the courier icon, manifest/description version and embedded refresh provenance changed. Its single gameplay resource `def/car_job_data.sii` is byte-identical to courier r1 and r0. This remains the same 58 reviewed eligibility additions with all nine vehicle-transfer jobs unchanged.

Use the same load order printed in the descriptions and README. Disable earlier copies of each fix when replacing them. If map r6 is already installed, only courier r1 needs replacing with r2. This metadata release does not require interrupting a gameplay test; no installation, profile change or economy reset was performed.

## Verification

**Observed locally — ATS 1.61.3.18 project, 2026-10-18:** all **246 tests pass** with the final default courier revision **2**, map revision **6**, and legacy fuel revision **2**. The approved small J3C export was copied exactly to `assets/mod-icons/practical-courier-jobs.jpg`; JPEG writer validation and FFmpeg decoding pass at **276x162**.

Source and output checks confirm all eight complete ZIP inventories and CRCs, generated-resource paths/sizes/SHA hashes and original source identities. The seven map archives remain completely byte-identical. Courier resource bytes and the resource inventory remain identical; only four reserved metadata files differ from r1. The embedded courier icon equals the approved J3C export exactly, and author/title/category, revision, real paragraphs, one `(THIS MOD)` marker and 58/9 counts agree. The outer ZIP contains exactly eight `.scs` files and README; member hashes, CRC and bundle SHA pass. Independent GPT-6 Luna review confirms these results, including direct courier payload comparison against r0/r1/r2.

Machine evidence is retained in ignored `local_outputs/work/2026-10-18_16-35-26/`: `full-tests.log`, `delivery-result.json`, `delivery.log`, `finalize_metadata_delivery.py`, independent review and documentation QA. Documentation QA passes for 94 Markdown files, 750 relative links, 27 heading fragments and all 25 task records (24 done, one active). All 12 input identities and 26 artifact exclusions pass. The previous r6/r1, r5/r1 and r4/r0 archives and source inputs remain unchanged. Embedded courier reports retain prior refresh provenance as history.

## Remaining game checks

**Unknown — runtime:** Canadian petrol quantity/price/payment, car rest prompts/fatigue recovery and Mustang job pickup/cargo fit/completed delivery still need the existing [manual checks](MANUAL_TEST_CHECKLIST.md). Metadata approval and static equality do not establish those outcomes. [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) remains active; [TASK-0025](../tasks/done/TASK-0025-refresh-mod-icons-and-player-descriptions.md) completes the metadata milestone.

See [metadata contract](MOD_METADATA.md), [courier command](PRACTICAL_COURIER_GENERATOR.md), [processor command](COMPATIBILITY_PROCESSORS.md), [current state](../project/CURRENT_STATE.md), and [ADR-0013](../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md).
