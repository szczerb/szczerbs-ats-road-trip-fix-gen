# N2 navigation icon fix: r3 presentation handoff

Prepared and inspected 2026-10-23 against ATS 1.61.3.18 and North America Background Map 5.3 (Workshop 3348711188). This is a local metadata/artwork increment; no game launch, installation, profile edit or public release occurred.

## Local testing package

Artifact: `local_outputs/generated/2026-10-23_17-04-49/testing/n2-szczerbs-road-trip-nav-icons-nabm-5.3-1.61-r3-experimental.scs` (ignored). Size **37,407 bytes**, SHA-256 **96dc2e8e350ad960b14b876110f52008a3202e6796f1d891a00784c936450b66**.

| Field | Value |
| --- | --- |
| Display name | N2 NAV ICONS | szczerb's Road Trip Navigation Icons Fix for North America Background Map 5.3 |
| Author | szczerb |
| Version | 1.61-r3-experimental |
| Category / game gate | map / 1.61.* |
| Retained DLC gate | dlc_rt_ford |
| Artwork | A2, revised from the user's preferred A; 276 × 162 JPEG |
| Gameplay resource | def/map_data.sii only, 3,236 bytes |

R3 supersedes N1 and older N2 copies; enable only one navigation overlay. Put it above **all** map-data providers, including North America Background Map and Reforma OtherMaps Patch. Keep the original background enabled and leave the other source-specific fixes/order unchanged. It works alongside the complete r10 map replacements but does not replace any of them. Whole-file overrides do not automatically merge other mods' map-display settings. This is not a standalone background or a universal background-map patch.

The testing copy contains four files: the gameplay definition, manifest, description and icon. It omits the internal `road_trip_fix_report.json`, whose complete audit remains outside the delivery archive. The original generated-with-report copy and earlier r3/A draft remain preserved in their own timestamped directories; none is overwritten. No public redistribution is performed or represented as cleared: read [publication boundary](NAVIGATION_ICONS_PUBLICATION.md).

## Scope and reproduction

**Observed locally:** the gameplay member is byte-identical to accepted N2 r2 (SHA-256 `8d42f35dbdf92a0e8e2e8d85081376415ea84fdbec9f5b0d6e8411ad0e6a75c6`). Relative to the pinned background definition, only bits 24/25 at local tiers 0–3 are enabled. World tiers 4–7, remaining source bytes and the three referenced SUI files are unchanged. This may reveal existing markers map-wide at those local tiers; it adds no station, parking area, service, economy field or map sector. [Mechanism and user evidence](CAR_PARKING_NAVIGATION_ICONS.md).

**User-reported:** both icons were visible in Mustang navigation on 2026-10-19 at the reported context; surface/zoom and broad coverage were not itemized. R3 changes presentation only. Generation-time `in_game_verified` remains false and the prior user report is attributed separately. No new runtime result is inferred.

Generate the internal auditable copy using the installed background's `universal` virtual root:

```bash
PYTHONPATH=src python3 -m ats_road_trip.navigation_icons \
  --source-package "<NABM_5_3_UNIVERSAL_ROOT>" \
  --game-version 1.61.3.18 --acknowledge-experimental --variant parking-fuel
```

The generator defaults to A2 and accepts `--icon` for a validated 276 × 162 JPEG override. It verifies the definition and all three include hashes before editing, rejects drift, uses a new Warsaw timestamp and refuses overwrite. Standard generator output includes its report; the separate testing delivery removes only that report and retains every remaining member byte-for-byte.

## Verification

All **508 tests pass**, including ten navigation tests for source pins, mask preservation, variant metadata, icon defaults/overrides, rejected malformed/missing icons and N1/N2 whole-file precedence. Independent actual-package checks confirm CRC, four delivery members, exact accepted r2 gameplay equality, recovery of the original source by reversing four literal edits, all include hashes and unchanged manifest gates. All four JPEG proposals decode successfully; the exported canvas is 276 × 162. Regenerated historical N1 r1 is byte-identical, SHA-256 `97e36da9a440299ebe2f9e07b4aba65bd5f92dfda6e9b94a221865dbfd32c362`.

Evidence remains ignored under `local_outputs/work/2026-10-23_16-54-37/` and `local_outputs/work/2026-10-23_17-04-49/`. The source definitions/includes and old generated archives remain unchanged. The work stays on `codex/gas-station-car-rest-research`; no merge, push or publication is part of this task. [Artwork and prompts](../../assets/mod-icons/navigation-icons/README.md), [TASK-0043](../tasks/done/TASK-0043-polish-navigation-fix-metadata-and-artwork.md).
