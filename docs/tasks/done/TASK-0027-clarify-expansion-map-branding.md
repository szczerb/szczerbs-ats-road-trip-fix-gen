---
id: TASK-0027
title: Clarify Expansion map branding and investigate connector icon failure
status: done
priority: high
repositories: [.]
depends_on: [TASK-0026]
owner: shared
---

# Goal

Identify the supplied Alaska Expansion and Western Canada Expansion unambiguously in filenames, metadata and icons, and address the reported missing connector fix icon.

# Context

**Documented — user requests, 2026-10-18:** use the Expansion suffix to distinguish these source maps from unrelated regional products, especially for future distribution. The user additionally reports no icon on the Western Canada ProMods Connections fix.

**Observed locally — ATS 1.61.3.18 log, inspected 2026-10-18:** r7's connector JPEG is valid, but the game reports an icon-cache copy failure and then 8x8 dimensions. The logged cache basename hex-decodes to its 96-character package stem; its physical path is 262 characters. A legacy Win32 path-limit cause is a strong hypothesis, not yet confirmed by a renamed in-game test.

# Scope

- Canonical Alaska Expansion and Western Canada Expansion names in profiles, manifests, descriptions, source order, filenames and combined/fuel-only artwork.
- Keep Western Canada ProMods Connections distinct; inspect generated package and logged cache failure without touching profiles or cache.
- Map r8 metadata release with shorter `szczerbs-road-trip-map-fix-<full-map-slug>-...` filenames, keeping full identities. Courier r3 remains unchanged.
- Preserve all gameplay bytes and historical outputs. No live installation, settings change or cache deletion.

# Implementation Plan

| Assignment | Actual model / effort | Ownership |
| --- | --- | --- |
| Current guides and metadata references | GPT-6 Sol / medium | Seven explicitly assigned guides |
| Image edits, naming integration, package handoff | Root | Artwork/source/tests/task/new references |
| Connector log research and independent archive checks | GPT-6 Luna / medium | Read-only ignored evidence |

# Acceptance Criteria

- Full Expansion names appear on both icon families, default outputs, manifest titles and the current map order.
- Western Canada dependency resolution and connector identity/own icon remain correct.
- Shorter output filenames address the observed cache-path budget without truncating map identities.
- All gameplay resources and unaffected icons/courier archive remain unchanged; complete package/static checks pass.
- Report observed cache failure separately from the hypothesized path-limit cause and pending runtime confirmation.
- Task/docs/exclusions/immutable inputs stay consistent; commit the verified milestone locally.

# Verification

Completed implementation/static verification 2026-10-18. Evidence: `local_outputs/work/2026-10-18_17-04-30/`.

- All 248 tests pass, including canonical source profile/dependency behavior, accurate icon selection, rejection of generic regional label reuse, and connector packaging with its declared JPEG/short filename/cache budget.
- Four footer-only imagegen edits were inspected; all new JPEGs pass writer validation and FFmpeg decoding at 276x162. Exact prompts, original input copies and generated originals are retained; runtime generation uses tracked exports.
- Root and independent Luna checks confirm seven r8 gameplay dictionaries and inventories match r7; only the two Expansion-labelled icons change, while five other map icons (including the connector) remain identical. Courier r3 is an exact archive copy. Correct manifests/names/slugs/current markers/source priority, all source archive hashes, ZIP CRC and bundled member SHA pass.
- The current batch is eight mods plus README. The shorter prefix keeps all known generated cache candidates below the legacy budget for the logged home (derived mapping, not a runtime guarantee). Inputs and prior outputs are unchanged. No live mod installation, profile/cache operation or Windows setting change occurred.
- Connector investigation corrected the initial directory-only inference using the dated r7 mount/cache-failure log. The VFS alias calculation is 263 including NUL for r7 and 235 for r8; appending a literal extra home directory was rejected. Valid JPEG plus cache-copy failure is observed; the path-limit explanation remains a hypothesis.
- Runtime image confirmation is explicitly retained in INC-0001 and TASK-0007/manual checklist, alongside existing gameplay tests. This completed task does not claim the icon is now visible in game.
- Documentation QA passes 803 links, 27 heading fragments and 27 synchronized task records; all 12 input identities and 26 artifact exclusions pass.
- Sol updated bounded guides; Luna researched the actual package/log and independently reviewed the final archive set; root integrated artwork, naming, regression checks and handoff.

# Links

- [Current r8/r3 handoff](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md)
- [Connector cache incident](../../incidents/INC-0001-connector-icon-cache/README.md)
- [Previous handoff](../../reference/MOD_METADATA_RENAME_1_61_R7_R3.md)
- [Metadata contract](../../reference/MOD_METADATA.md)
- [Manual tests](../../reference/MANUAL_TEST_CHECKLIST.md)
