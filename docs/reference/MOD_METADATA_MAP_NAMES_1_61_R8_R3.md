# Exact Expansion map identities: r8 maps and unchanged courier r3

**Documented — user instructions, 2026-10-18:** identify the supplied maps as **Western Canada Expansion** and **Alaska Expansion**, including icon text and metadata. Their names distinguish them from unrelated maps covering the same regions. Western Canada ProMods Connections remains a separate connector. The user also reports that connector fix's icon is missing in Mod Manager.

## Download

Eight-mod r8/r3 ZIP (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_17-04-30/szczerbs-road-trip-test-batch-ats-1.61-map-r8-courier-r3-experimental.zip`), **68,459,292 bytes**.

SHA-256: `880e5e242772ce7b1dabc26326b294b58baea40d73ae9691611127989e253aac`.

Western Canada ProMods Connections fix r8 (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_17-04-30/szczerbs-road-trip-map-fix-western-canada-promods-connections-1.61-r8-experimental.scs`).

Seven map packages are r8; Job Types Compat Mustang r3 is copied byte-for-byte. Map filenames now use `szczerbs-road-trip-map-fix-<full-map-slug>-1.61-r8-experimental.scs`. The shorter shared prefix reduces the connector icon-cache path budget; full source-map names and manifest titles remain clear. [ADR-0014](../architecture/decisions/ADR-0014-shorten-map-package-cache-paths.md).

Disable previous copies when replacing these fixes. Keep each fix directly above its source. The new Expansion names appear in manifests, archive slugs, description titles and all seven priority lists. Existing CLI commands infer those full source labels automatically; combined default is r8, courier remains r3 and legacy fuel remains r2. Generic Alaska/Western Canada labels do not select these specific Expansion maps' artwork automatically.

## Icons and scope

Combined presets are `map-compatibility/alaska-expansion.jpg` and `map-compatibility/western-canada-expansion.jpg`. Both retain M2D's four-Ford station scene and add EXPANSION in the footer. New `alaska-expansion-c.jpg` and `western-canada-expansion-c.jpg` also give future fuel-only builds accurate source names. Original fuel-only art is retained as history. No source archive was edited. [Exact imagegen prompts and targets](../../assets/mod-icons/PROMPTS_EXPANSION_NAMES.md).

The five other map icons, including the connector's distinct labelled icon, remain byte-identical to r7. Courier artwork and its complete archive are unchanged. All eight gameplay dictionaries and inventories are identical to the accepted r7/r3 handoff. Historical generation reports may retain older short labels as provenance; current manifest metadata and description labels are canonical. This release does not add support for unrelated paid/Patreon regional maps.

## Connector missing-icon investigation

**Observed locally — ATS 1.61.3.18 log, 2026-10-18 16:54:43 session:** r7 was discovered with the correct title and a valid manifest-referenced 276x162 JPEG. The game failed to create/copy its icon-cache file before reporting 8x8 dimensions. The cache filename hex-decodes to the full 96-character package stem. An initial directory-only absence inference was superseded by the dated log.

**Hypothesis:** under the normal `/home` VFS alias mapping, the old physical path would be 262 characters (263 including NUL), beyond the classic Win32 budget documented by [Microsoft](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation). The shorter r8 connector name yields a derived 234-character path (235 with NUL). Exact API/opt-in behavior and physical cache state remain unknown. No Windows settings were changed and no cache was deleted. [INC-0001](../incidents/INC-0001-connector-icon-cache/README.md) preserves the evidence and pending check.

After installing r8, confirm the connector picture appears in Mod Manager. If it does not, retain the fresh relevant log before another session. A valid packaged JPEG and shorter filename do not prove successful runtime rendering.

## Verification

All **248 tests pass**, including canonical profile labels with preserved Western Canada dependency resolution, unknown regional artwork rejection, exact connector icon packaging and the shorter filename/cache-budget regression. Four new JPEG exports decode and pass writer validation at 276x162, and their footer text was visually inspected. Image edits used built-in imagegen; FFmpeg only performed format/downscale export.

Root and independent GPT-6 Luna checks confirm seven r8 gameplay inventories/bytes match r7, the two renamed icons match their new presets, five other map icons stay unchanged and the courier archive is copied exactly. Manifest names, version, icon field, marker count, full source/ProMods order and OtherMaps price-only description pass. Every relevant derived cache-path candidate is below 260 including NUL for the logged home. Outer ZIP CRC/SHA, exact eight-mod-plus-README inventory and individual member hashes pass.

Documentation QA passes 105 Markdown files, 803 relative links, 27 heading fragments and 27 task records (26 done, one active). All 12 input identities and 26 artifact exclusions pass.

Evidence: ignored `local_outputs/work/2026-10-18_17-04-30/`, including `full-tests.log`, `delivery-result.json`, `independent-review.json`, `connector-icon-evidence.json`, image provenance and documentation QA. Previous [r7/r3 delivery](MOD_METADATA_RENAME_1_61_R7_R3.md) and all source inputs remain unchanged. Existing [fuel/rest/courier manual tests](MANUAL_TEST_CHECKLIST.md) remain open, together with the connector image check. [TASK-0027](../tasks/done/TASK-0027-clarify-expansion-map-branding.md).
