# Overnight test delivery: map r4 and practical courier r0

**Observed locally — generated and statically verified 2026-10-18, ATS 1.61.3.18.** [Download the delivery ZIP](../../local_outputs/generated/2026-10-18_04-25-54/szczerbs-road-trip-test-batch-ats-1.61-map-r4-courier-r0-experimental.zip). It contains **eight** `.scs` files, `README_TESTING.md`, SHA-256 checksums and a delivery manifest. Extract the individual mods before installing manually. ZIP SHA-256: `11688bd8f64b2183615c803106c2f1fd13c4df513f1566e98ca6920cf5602902`; size 68,147,151 bytes.

## Package contents

The seven map/connector packages are `1.61-r4-experimental`, combining selected fuel/rest processors, the reviewed missing-petrol-price policy, and exact original context preservation for private prefab aliases. Logical counts are per source package; overlapping map sectors mean their sum is not unique combined-world coverage.

| Source-specific fix | Added car fuel points | Added car rest areas | Petrol fields | Classified aliases preserved |
| --- | ---: | ---: | ---: | ---: |
| [ATS Expansion](../../local_outputs/generated/2026-10-18_04-08-02/szczerbs-road-trip-map-compatibility-fix-ats-expansion-1.61-r4-experimental.scs) | 894 | 766 | 0 | 19 |
| [Reforma](../../local_outputs/generated/2026-10-18_04-00-48/szczerbs-road-trip-map-compatibility-fix-reforma-1.61-r4-experimental.scs) | 954 | 119 | 19 | 7 |
| [ProMods Canada](../../local_outputs/generated/2026-10-18_03-52-00/szczerbs-road-trip-map-compatibility-fix-promods-canada-1.61-r4-experimental.scs) | 102 | 95 | 0 | 2 |
| [Western Canada](../../local_outputs/generated/2026-10-18_03-52-00/szczerbs-road-trip-map-compatibility-fix-western-canada-1.61-r4-experimental.scs) | 288 | 202 | 6 | 14 |
| [Alaska](../../local_outputs/generated/2026-10-18_03-52-00/szczerbs-road-trip-map-compatibility-fix-alaska-1.61-r4-experimental.scs) | 43 | 31 | 1 | 2 |
| [Reforma OtherMaps Patch](../../local_outputs/generated/2026-10-18_03-52-00/szczerbs-road-trip-map-compatibility-fix-reforma-othermaps-patch-1.61-r4-experimental.scs) | 0 | 0 | 19 | 0 |
| [Western Canada ProMods Connections](../../local_outputs/generated/2026-10-18_03-52-00/szczerbs-road-trip-map-compatibility-fix-western-canada-promods-connections-1.61-r4-experimental.scs) | 50 | 41 | 1 | 2 |
| Package totals | 2331 | 1254 | 46 | 46 |

OtherMaps has no source-sector fuel/rest targets; its package contains only country petrol fields. Existing diesel and other country attributes remain unchanged. Price values use lower same-unit data where available or the explicit stock-game ratio; these are not real-world price claims.

The separate [Practical Courier Jobs r0](../../local_outputs/generated/2026-10-18_03-56-10/szczerbs-road-trip-practical-courier-jobs-muscle-1.61-r0-experimental.scs) adds `muscle` to **58** reviewed cargo job definitions. Thirty ambiguous candidates remain off. All nine vehicle transfers and all non-target original bytes are unchanged. It preserves ratings, rewards, contexts, distance fields and vehicle tags. It affects a class/shared definitions, potentially including other muscle-tagged cars and Quick Jobs, rather than exclusively the owned Mustang/Dispatch. [Configuration, commands and limits](PRACTICAL_COURIER_GENERATOR.md).

## Installation priority

Disable superseded samples, source fuel-only r1/r2 fixes and WCE r3 for maps replaced by r4. Use one combined fix per source. Each fix belongs directly above its own map/connector, because whole sector resources replace rather than merge.

For the supplied screenshot order, **top to bottom**:

1. Practical Courier Jobs r0, separately; review any other `def/car_job_data.sii` replacement before stacking.
2. Alaska r4 fix → Alaska Expansion.
3. Western Canada ProMods Connections r4 fix → its connector.
4. Reforma OtherMaps Patch r4 fix → OtherMaps Patch.
5. ProMods definitions.
6. ProMods Canada r4 fix → ProMods map.
7. ProMods assets/models, keeping their existing relative order.
8. Western Canada r4 fix → Western Canada Expansion.
9. ATS Expansion r4 fix → ATS Expansion.
10. Reforma r4 fix → Reforma.
11. Reforma Mega Resources.

Two displayed branding/traffic mods remain unsupplied and uninspected. The declared generation stack and source-relative installation are separate checks. No game, profile, live mod directory or economy reset was touched. [Original source priority evidence](CONNECTOR_FUEL_FIXES.md).

## Static verification

- Full authored suite: **233 tests pass**, [final log](../../local_outputs/work/2026-10-18_04-08-02/tests-final.log).
- Independent read-only output checks: ZIP CRC, inventory/resource hashes, source-owned sector pins, original Service/FuelPump records and nodes, unchanged r2 fuel payloads, rest descriptor/standalone action-only edits, actual private truck/bus/car parameters, original context resources versus generated tags, and finite positive petrol with unchanged non-petrol fields. [Per-package evidence](../../local_outputs/work/2026-10-18_03-47-10/batch-review/).
- [WCE Company comparison](../../local_outputs/work/2026-10-18_04-00-48/verify_wce_companies.json) retains all 380 original Company records in edited sectors byte-for-byte and accounts for all 14 classified Company-parent aliases.
- Standalone proof removes exactly 58 inserted declarations to recover the canonical source file byte-for-byte; all nine transfer bodies are checked separately.
- [Winning-sector graph](../../local_outputs/work/2026-10-18_04-00-48/verify_composed_graph.json) passes across 583 relevant effective paths: 2202 surviving generated truck targets retain co-located car interactions, and 3518 car services have reciprocal nodes. It does not infer gameplay or unseen mods. Unrelated original truck points in copied neighbors are listed separately.
- [Namespace check](../../local_outputs/work/2026-10-18_04-00-48/verify_definition_collisions.json) passes for 556 generated definition units; no conflicting non-sector definition/descriptor paths or duplicate additive unit IDs. Country precedence is reviewed separately.
- Input archive/sidecar identities and shared source versions are checked before delivery. No supplied archives, extracted data or generated mods are tracked in Git. [Delivery provenance](../../local_outputs/work/2026-10-18_04-00-48/delivery-result.json).

## Scope and pending game tests

Rest uses the selected **1,000 game-world-unit XZ** proximity rule and original car inventory in source sectors plus a bounded halo. Missed neighbors can add accepted extra permissions. Existing irregular standalone shapes remain geometrically unchanged; a disclosed conservative vertex proof can also cause extra permissions, while validated action tokens alone are retargeted. [Legacy layout evidence](REST_LEGACY_LAYOUT_TRIAGE.md) and [ADR-0012](../architecture/decisions/ADR-0012-preserve-irregular-source-rest-geometry.md) record that implementation decision and its limits. Source and neighbor coverage/omissions remain in embedded reports.

**Unknown, manually unverified:** r4 petrol display/quantities/billing, truck/garage/reload controls, rest prompts/fatigue recovery/icons, and newly eligible Mustang offers/pickup/cargo attachment/completed delivery. Follow the [manual checklist](MANUAL_TEST_CHECKLIST.md). The existing reminder remains scheduled for 2026-10-18 18:00 Europe/Warsaw; no further tests were expected during the night.

General map courier generation remains unsupported and reporting-only. This delivery does not invent missing markers, promise a city-wide offer count, or modify a speculative global job budget. Static preserved classifications do not establish runtime courier success.
