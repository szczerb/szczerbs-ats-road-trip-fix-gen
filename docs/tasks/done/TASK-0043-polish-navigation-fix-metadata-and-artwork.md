---
id: TASK-0043
title: Polish navigation-fix metadata and artwork
status: done
priority: medium
repositories:
  - .
depends_on:
  - TASK-0042
owner: shared
---

# Goal

Prepare the user-tested N2 navigation visibility fix as a clearly presented experimental package, with final player-facing metadata and dedicated topic artwork, while preserving its reviewed gameplay payload.

# Context

**Documented — user report, 2026-10-19:** both fuel and parking icons are visible in Mustang navigation with N2 at the reported test context. The exact interface, location, zoom and profile were not itemized. N2 is the source-pinned navigation overlay documented in [CAR_PARKING_NAVIGATION_ICONS.md](../../reference/CAR_PARKING_NAVIGATION_ICONS.md), not a parking-generation or map-sector fix.

N1 and N2 already carry experiment-identifying metadata. The remaining work is final player-facing presentation and dedicated artwork, not adding the first metadata to otherwise unidentified experiments. The applicable metadata contract requires a JPEG `mod_icon.jpg` at exactly 276 × 162 pixels and is documented in [MOD_METADATA.md](../../reference/MOD_METADATA.md) and [ADR-0013](../../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md).

# Scope

- Review and finalize the player's display title, description, revision/version, dependency fields and load-order instructions for the N2 overlay, following the metadata contract and clearly distinguishing it from N1 and map-sector fixes.
- Create dedicated 276 × 162 JPEG artwork appropriate to the parking and fuel navigation-visibility topic, then package the reviewed metadata and image with N2.
- Confirm the final package retains the source pins and runtime-accepted navigation-mask gameplay member byte-for-byte; retain the established background-map dependency and precedence.
- Do not change map-sector resources, parking geometry, services, triggers, prices or the navigation heuristic. Do not generate the artwork, edit a metadata package, or issue a new revision while this task remains in backlog. Do not publish or release the package.

# Implementation Plan

1. Re-read the N2 handoff, metadata contract and ADR-0013; decide the final player-facing fields and explicit dependency/load-order text.
2. Produce and inspect the dedicated 276 × 162 JPEG artwork, then prepare a new experimental package without overwriting historical N1/N2 artifacts.
3. Compare gameplay members and source pins against the accepted N2 handoff; record package checks and any remaining user-facing caveat.

# Acceptance Criteria

- The completed package has clear, distinct player-facing title and description, correct version/revision and dependency fields, and explicit load order above North America Background Map and other map-data providers.
- It includes topic-specific 276 × 162 JPEG artwork and meets the metadata contract.
- The only gameplay payload remains the reviewed N2 `def/map_data.sii` change; all other packaged gameplay data, if any, is byte-identical to the accepted N2 package.
- No map-sector, parking-generation, fuel-service or economy behavior changes are introduced, and no public release occurs as part of this task.

# Verification

Completed 2026-10-23. Root integrated the work on the existing `codex/gas-station-car-rest-research` checkout; master is unchanged.

- GPT-6 Luna/medium inventoried the source/accepted N2 archive and implemented only navigation metadata/icon handling and tests. GPT-6 Sol/medium checked primary author/Steam/SCS publication evidence and authored the rights reference. Root reviewed claims and code, generated/inspected artwork, packaged and independently checked the payload.
- Three built-in image_gen proposals A/B/C were generated and exported as 276 × 162 JPEG. The user chose A and requested a modest zoom-out showing a passenger-car interior plus ROAD TRIP. Built-in imagegen edited A into sibling A2; no historical image was overwritten. A2 is the current candidate, with no separate final approval inferred. Prompts and small exports are tracked; large originals/previews are ignored.
- N2 r3 preserves the accepted r2 gameplay payload exactly: 3,236 bytes, SHA-256 `8d42f35dbdf92a0e8e2e8d85081376415ea84fdbec9f5b0d6e8411ad0e6a75c6`. Reversing its four local-tier token edits recovers the original background source. Every source/include pin still matches. Historical N1 regeneration is byte-identical, SHA-256 `97e36da9a440299ebe2f9e07b4aba65bd5f92dfda6e9b94a221865dbfd32c362`.
- The report-free local testing copy is 37,407 bytes, SHA-256 `96dc2e8e350ad960b14b876110f52008a3202e6796f1d891a00784c936450b66`. It has exactly four members: unchanged gameplay definition, manifest, description and A2 icon. Only the internal report is omitted from the generator's copy; the audit is retained externally. Both ZIPs pass CRC checks; retained members match exactly.
- All 508 tests pass, including ten focused navigation tests. Actual exports decode; package/manifest gates, default and override icons, mask/source identity and include hashes pass independent checks. Documentation QA verifies relative links (ignoring local-artifact availability as explicitly documented), task/status/dependency consistency, exclusions and whitespace. No game/profile or supplied input mutation occurred.
- Rights review finds no explicit permission to redistribute the complete background-derived definition in the inspected Workshop description/installed package. This does not prove infringement or ownership of every byte. The project AGPL does not clear third-party bytes. Ready-made public distribution remains unestablished; original generator/change-spec sharing and author permission are documented alternatives. No author contact or release occurred.

Evidence: ignored `local_outputs/work/2026-10-23_16-54-37/` and `local_outputs/work/2026-10-23_17-04-49/`. Final artifact identifier and exact load priority are in the new r3 handoff. Historical N1/N2/A drafts and r10 map packages remain unchanged.

# Links

- [R3 handoff](../../reference/NAVIGATION_ICONS_METADATA_1_61_R3.md)
- [Publication boundary](../../reference/NAVIGATION_ICONS_PUBLICATION.md)
- [Artwork and prompts](../../../assets/mod-icons/navigation-icons/README.md)

- [N2 navigation-icon handoff](../../reference/CAR_PARKING_NAVIGATION_ICONS.md#n2-analogous-fuel-visibility-candidate)
- [Metadata contract](../../reference/MOD_METADATA.md)
- [ADR-0013: topic artwork and player descriptions](../../architecture/decisions/ADR-0013-topic-artwork-and-player-descriptions.md)
- [TASK-0042: test the analogous local-navigation fuel icon mask](../done/TASK-0042-test-local-navigation-fuel-icon-mask.md)
