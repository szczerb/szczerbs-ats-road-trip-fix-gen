---
id: TASK-0025
title: Restore topic-appropriate mod icons and readable player descriptions
status: active
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

Implementation and package verification completed; final courier artwork selection remains pending; M2D is now explicitly selected for maps. The user confirms corrected variants display both in chat and the Windows-local HTML gallery. Work and original artwork: `local_outputs/work/2026-10-18_15-24-10/`. Built-in image outputs existed but failed to render in the app; proposals were exported to project-local JPEGs and shown using standard Markdown image paths. The user subsequently confirmed seeing the six map-footer tool previews while Markdown variants still failed. The five requested variants were re-presented as actual tool image content. The user then reported the native gallery still failed; Windows-local copies and an HTML gallery succeeded, explicitly confirmed. J3B is now the favorite, not a final selection. M2 remains the selected existing map preset, J1B provisional for courier. Requested M2C/M2D proposals correct the Victoria to 2006 and add the Bronco 2024; they retain M2A's location/direction and unobstructed reversing space. No default/package replacement is inferred from this proposal request.

- All 246 tests pass, including seven description tests, five delegated artwork selector tests and the new courier default/explicit artwork packaging test. Full log: `full-tests.log` in the run.
- Root and independent Luna checks pass for eight source/output gameplay dictionaries and embedded hashes, source archive SHA, CRCs, all icon dimensions/bytes, descriptions, exactly one current marker, map/source order and the nine-entry delivery ZIP. Evidence: `delivery-result.json` and `independent-review.json`. Only four metadata paths differ from r4/r0.
- Generated seven r5 map packages plus r1 courier and the combined ZIP. Existing outputs and local inputs remain unchanged; no live installation or game operation.
- Image generation/editing used built-in imagegen; FFmpeg only resized/exported. M2A/M2B and J1B/J2B/J3B exact prompts and small exports are tracked.
- Documentation QA passes: 89 Markdown files, 699 relative links, 26 heading fragments, 25 task records and dependency/status consistency. All 12 input identities are unchanged and 26 artifact exclusions pass. Nineteen new JPEGs pass writer validation and FFmpeg decoding; `git diff --check` passes.

- Additional read-only Luna review confirms Substation Access Keys job/cargo IDs, exclusion of all nine vehicle transfers, and the installed 2006/2024 vehicle series. Two new imagegen proposals pass JPEG writer validation and FFmpeg decoding; originals and export provenance are under `local_outputs/work/2026-10-18_16-10-22/artwork/`. No utility code changed or gameplay tests were required.

- M2D acceptance: six new footer-only imagegen edits plus exact ATS Expansion selected JPEG now supply all seven combined presets. Map r6 generation defaults and descriptions advance together; 56 focused metadata/CLI/workflow tests pass. Seven JPEGs decode/validate and gameplay inventories remain byte-identical to r5. Courier r1 is copied byte-for-byte; no J3B swap is inferred. Independent Luna checks confirm the seven map packages, exact ATS Expansion selected icon, unchanged courier archive and outer ZIP inventory/CRC/SHA. Documentation QA passes 726 links, 25 task records, 12 unchanged input identities and 26 artifact exclusions. New run: `local_outputs/work/2026-10-18_16-16-22/`.

- J3C is an additional courier-art proposal: it replaces J3B's automotive-looking key/fob with four metal access keys and preserves its checklist, Mustang, headline and frame. The exact prompt is [PROMPT_J3C_KEYS.md](../../../assets/mod-icons/PROMPT_J3C_KEYS.md); the 276x162 export is [j3c-access-keys.jpg](../../../assets/mod-icons/proposals-v5/j3c-access-keys.jpg). Root generated and inspected the image and export; the large original is in `local_outputs/work/2026-10-18_16-25-09/artwork/`. GPT-6 Luna / medium recorded the proposal in this task and the artwork guide. The user has not selected a final courier icon: J1B and r1 remain unchanged. No code or gameplay changed, and no utility tests needed rerunning.

# Links

- J3C display retry: the user reports both chat and the new HTML link failed. Existing PNG/HTML and relative targets were checked; the original PNG is now embedded byte-identically in the earlier working gallery and standalone `j3c.html`. Retry uses the known gallery URL without a fragment. Client visibility remains unconfirmed; no artwork or package bytes changed.

- [Selected M2D r6/r1 handoff](../../reference/MOD_METADATA_REFRESH_1_61_R6.md)
- [Metadata refresh](../../reference/MOD_METADATA_REFRESH_1_61_R5.md)
- [Existing delivery](../../reference/OVERNIGHT_TEST_BATCH_1_61_R4.md)
- [Metadata contract](../../reference/MOD_METADATA.md)
- [Icon archive](../../../assets/mod-icons/README.md)
- [Manual tests](../../reference/MANUAL_TEST_CHECKLIST.md)
