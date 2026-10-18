---
id: TASK-0025
title: Restore topic-appropriate mod icons and readable player descriptions
status: done
priority: high
repositories: [.]
depends_on: [TASK-0024]
owner: shared
---

# Goal

Prepare map fuel/rest and Mustang courier icon proposals, restore suitable packaging artwork, and explain effects and source-relative priority clearly inside Mod Manager.

# Context

**Documented — user request, 2026-10-18:** combined map fixes lost their image; include parking imagery alongside fuel imagery, propose separate Mustang job artwork, and write concise descriptions with paragraph breaks. Map descriptions should contain the full known combination with the current fix clearly marked in parentheses. The user is independently testing r4/r0; this work must preserve gameplay payloads.

# Scope

- Three original image proposals per family, plus small 276x162 JPEG exports and original prompt provenance.
- Readable English descriptions selected by package scope, including the price-only OtherMaps case and dynamic courier counts.
- Full known map/source order, optional background/courier add-ons, and exactly one current-mod marker.
- Generator integration and refreshed metadata-only packages; preserve earlier archives and live profiles.
- Publication must compare every gameplay resource byte against its accepted r4/r0 source.

# Implementation Plan

| Assignment | Actual model / effort | Ownership |
| --- | --- | --- |
| Description renderer and focused structural tests | GPT-6 Sol / medium | mod_descriptions.py and test_mod_descriptions.py |
| Built-in imagegen prompts, exports, integration and packaging | Root | Remaining files and ignored run |
| Artwork selector tests and independent metadata/payload comparison | GPT-6 Luna / medium | test_mod_artwork.py and read-only final package evidence |

# Acceptance Criteria

- Both families have visible, labelled proposals, saved originals and exact prompts; selected/default artwork is explicit.
- Combined packages include suitable map-labelled fuel/parking artwork; courier artwork is separate.
- Descriptions contain real paragraphs and correct placement, with no false gameplay promises or OtherMaps station/rest claims.
- Current-fix markers and all map/connector/ProMods source priorities agree with the known combination.
- All refreshed gameplay resources are byte-identical to r4/r0; no live installation or input changes occur.

# Verification

Completed 2026-10-18. The user explicitly approved M2D map artwork and J3C courier artwork after confirming both are visible. J3C replaces the automotive key/fob with mechanical access keys, consistent with the reviewed Substation Access Keys cargo. Final deliverables are seven map r6 archives and separate courier r2 in one eight-mod ZIP.

- All **246 tests pass** with map default r6, courier default r2 and legacy fuel default r2. This includes description/order, artwork selection, explicit/default courier icon packaging, report-only analysis and existing gameplay planners. Final log: `local_outputs/work/2026-10-18_16-35-26/full-tests.log`.
- Root and independent GPT-6 Luna checks confirm seven complete r6 map archives are unchanged and courier r2 differs from r1 only in four metadata paths. Its exact `def/car_job_data.sii` bytes and resource hashes match r0, r1 and r2. Counts remain 58 selected jobs and nine untouched vehicle-transfer definitions.
- The courier preset and embedded icon equal the approved J3C JPEG exactly; 276x162 writer validation and FFmpeg decoding pass. Manifest author/title/category/revision, real paragraphs, one `(THIS MOD)` marker, optional job add-on placement, and full map/connector/ProMods order pass. OtherMaps remains explicitly price-only.
- Outer ZIP CRC, SHA, exact eight-mod-plus-README inventory and all member hashes pass. Final evidence: `local_outputs/work/2026-10-18_16-35-26/delivery-result.json`, `delivery.log`, `independent-review.json` and documentation QA. Supplied inputs and prior output archives remain unchanged; no live installation, profile edits or game operation occurred.
- Built-in imagegen produced proposals and targeted edits; FFmpeg only performed format/downscale export. Exact prompts and small original exports are tracked in the artwork guide. Large originals/provenance remain in timestamped ignored artwork runs. Bounded Sol work covered descriptions/guides; Luna covered artwork tests, source-key/year evidence, documentation and independent package reviews; root integrated art and delivery.
- Display history is preserved in the artwork guide: local Markdown/native gallery failures were followed by a Windows-local HTML gallery; a later J3C failure was addressed by embedding byte-verified PNG data in that known gallery. The user then confirmed J3C visibility and approved it. No approval was inferred from failed previews.
- Final documentation QA passes 750 links, 27 heading fragments and 25 task records with synchronized status/directory/dependencies. All 12 immutable input identities and 26 artifact exclusions pass; `git diff --check` passes.
- Historical r5/r1 and r6/r1 handoffs retain their original archives, hashes and staged checks. They document the transition from initial M2/J1B through selected M2D to final J3C. Manual billing, rest and courier acceptance/delivery remain in TASK-0007 and are not completed by this metadata task.

# Links

- [Approved final r6/r2 delivery](../../reference/MOD_METADATA_FINAL_1_61_R6_R2.md)


- [Selected M2D r6/r1 handoff](../../reference/MOD_METADATA_REFRESH_1_61_R6.md)
- [Metadata refresh](../../reference/MOD_METADATA_REFRESH_1_61_R5.md)
- [Existing delivery](../../reference/OVERNIGHT_TEST_BATCH_1_61_R4.md)
- [Metadata contract](../../reference/MOD_METADATA.md)
- [Icon archive](../../../assets/mod-icons/README.md)
- [Manual tests](../../reference/MANUAL_TEST_CHECKLIST.md)
