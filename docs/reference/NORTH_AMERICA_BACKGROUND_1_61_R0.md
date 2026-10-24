# North America Background Map — ATS 1.61 r0 manual handoff

**Subsequent user feedback — 2026-10-24:** the background renders and its appearance/extra world zoom are liked; truck navigation seems fine and car fuel/parking navigation icons are confirmed at the reported check. Job-market crowding and coast/lake placement defects are under investigation. [Exact feedback and evidence scope](NORTH_AMERICA_BACKGROUND_FEEDBACK_2026_10_24.md), [TASK-0049](../tasks/active/TASK-0049-correct-background-alignment-and-job-market-zoom.md). The offline delivery record below remains historical; unreported runtime details stay open.

**Observed locally — 2026-10-23:** the standalone experimental package passes the automated resource, texture, calibration, reproducibility and regression checks described below. **Unknown:** its runtime appearance and behavior. No game was launched, mod installed, profile/save edited or economy reset.

Title: **szczerb's Road Trip North America Background Map**. Author: **szczerb**. Version: **1.61-r0-experimental**. Requires ATS **1.61**, with no Ford DLC requirement. Expansions retain their own DLC/dependency requirements. This is geographic artwork behind the game's roads/icons, without playable map content.

## Authoritative testing package

- [Install this SCS](../../local_outputs/generated/2026-10-23_21-48-34/szczerbs-road-trip-north-america-background-map-ats-1.61-r0-experimental.scs).
- SHA-256: `913ff62169b2dd7729fe16a0074d4d099d9cdd795c2b785a83a7adf32e32bac4`.
- [Preview gallery](../../local_outputs/generated/2026-10-23_21-48-34/previews/index.html), [overall geography](../../local_outputs/generated/2026-10-23_21-48-34/previews/overall.png), [encoded texture reconstruction](../../local_outputs/generated/2026-10-23_21-48-34/previews/encoded-textures.png).
- Alignment overlays: [USA west](../../local_outputs/generated/2026-10-23_21-48-34/previews/usa-west.png), [USA central/east](../../local_outputs/generated/2026-10-23_21-48-34/previews/usa-central-east.png), [Canada](../../local_outputs/generated/2026-10-23_21-48-34/previews/canada.png), [Alaska/Yukon](../../local_outputs/generated/2026-10-23_21-48-34/previews/alaska-yukon.png), [Mexico](../../local_outputs/generated/2026-10-23_21-48-34/previews/mexico.png).

Circles are actual game CityArea reference centers; amber crosses are the geographic points after calibration. Cyan points were held out from fitting. Those overlay marks are diagnostics only and do not appear in the mod. Both root and an independent delegate examined the overall/regional previews; the actual encoded tile pixels exactly match their source quadrants. Minor crowded diagnostic labels in Mexico do not affect the shipped image.

The earlier `21-38-27` and `21-42-00` run packages are **superseded, not for testing**: a later engine-schema check caught an overlong internal manifest token that the generic parser had accepted. They carry explicit superseded markers and remain only as development evidence. The corrected build enforces SCS's 12-character unit-name token limit; its repeated-build copy in `21-49-32` is marked reproducibility-only. Use only the authoritative path above. Historical N1/N2 and map-fix outputs remain untouched.

## Installation and priority

1. Copy the authoritative `.scs` into your ATS mod directory yourself and enable it in Mod Manager. Keep a copied/disposable profile or existing backup for the manual trial; the generator performs no profile operation.
2. Disable North America Background Map 5.3, all N1/N2 copies (including N2 r3), and other geographic background mods. The new package replaces both the background and N2 presentation overlay and requires none of their includes.
3. Give this package **higher priority than every map-data/background/material override**, including Reforma OtherMaps, ProMods Definitions/Assets, Reforma and any Reforma ProMods Background Fix. Disable an obsolete dedicated background fix, or keep its multipurpose source below this package if needed for other resources.
4. Retain the existing source-map/connector/fuel/rest replacement order beneath it. Keep separate tank and courier mods as before. No new fuel/rest interaction geometry or job whitelist change is included.

For the declared installed combination, top → bottom:

| Priority | Packages |
| --- | --- |
| Highest relevant override | **This North America Background Map r0** |
| Existing independent visual/gameplay packages | Keep current relationships; any package replacing the inspected backdrop paths must remain below this background. |
| Alaska | Existing chosen Alaska replacement/fix directly above **Alaska Expansion 1.2.3** |
| WCE–ProMods connector | Its fix directly above **Western Canada ProMods Connections 1.7.3** |
| OtherMaps | Its price replacement/fix directly above **Reforma OtherMaps Patch 40.161** |
| ProMods Canada | Definitions 1.6.4; chosen map fix; Map 1.6.4; Assets 1.6.4; Models 1.6.4 |
| Western Canada | Its fix directly above **Western Canada Expansion 1.7.3** |
| ATS Expansion | Its fix directly above **ATS Expansion 23.0 / 1.61** |
| Reforma | Its fix directly above **Reforma 3.0.1.161**, then **Mega Resources 3.0.1.161** |
| Stock companion/base | Retain the required stock companion if using the newer complete r10 set, above installed base/map DLCs. |

This preserves the previously declared source priority; it does not instruct mixing old r9 with r10 replacements or recreating the station test batches. The newer r10 evidence was read from `codex/gas-station-car-rest-research` at `2d7394d`; no unrelated tooling was merged. The current live profile is not inspected. Another higher `def/map_data.sii` or map-material override can still shadow this mod; no universal dynamic merge is claimed.

## What is verified

**Observed locally — offline checks:**

- The 22-member deflated ZIP has no duplicate paths, CRC errors, reports, diagnostics, local paths, protected game/map imagery or old-background includes. Every custom MAT→TOBJ→DDS dependency resolves. The only external renderer is the game's stock `ui.rfx` effect.
- One 2048² overview and four 4096² tiles use the inspected stock BGRA8 sRGB DX10 layout, one mip, correct payload lengths and opaque alpha. Raw texture pixels total 272 MiB before ZIP compression; runtime allocation/performance remains unmeasured.
- Map-data and manifest parse, and every unit-name component obeys [SCS's documented 12-character token limit](https://modding.scssoft.com/wiki/Documentation/Engine/Units). All eight masks equal stock. Car fuel/parking bits are present in local tiers. A semantic stock comparison shows only seven geographic camera/size/zoom attribute groups changed; all unrelated fields, truck icon inputs, route costs/colors, nine map-area rows and stock icon dimensions match. Only the last zoom tier differs within its zoom array.
- Bounds enclose the supplied-source and installed base/20-map-DLC sector-name rectangles. Each source's actual version/resource conflicts is documented in the [research](NORTH_AMERICA_BACKGROUND_RESEARCH.md); this is static compatibility evidence, not a road census or runtime pass.
- The 52 references were independently rechecked against original effective sectors and Natural Earth IDs. The selected affine calibration uses 34 fit and 18 check points; no sampled flips/nonfinite data. Check RMS **2,412 game units**, median **2,068**, maximum **6,381 at Fairbanks**. The check set informed model selection; it is not a blind accuracy test.
- Two complete build runs and a third build from the freshly extracted corresponding-source ZIP produce identical archive SHA-256. The full test suite passes **292 tests** (281 existing plus 11 background cases). Tests cover held-out isolation, invalid configuration, source drift, missing texture dependencies, unrelated mask changes, quadrant placement, reproducible ZIP bytes, SCS token-length rejection and overwrite refusal.

Static evidence: [initial audit](../../local_outputs/work/2026-10-23_21-48-34/north-america-background/audit.json), [complete reproduction receipt](../../local_outputs/work/2026-10-23_21-49-32/north-america-background/receipt.json), [per-point errors](../../local_outputs/work/2026-10-23_21-48-34/north-america-background/calibration.json), and [independent archive review](../../local_outputs/work/2026-10-23_21-16-53/engine-inspection/package-final-independent-review.json). These are external local evidence, not archive members.

The map is a readable approximation. Local compressed city geometry and map reworks prevent exact correspondence to real-world geography; eastern USA/Canada, the far Arctic and southern Mexico have no independent game-coordinate checks. A country border need not match every shifted gameplay road. Previews show these compromises rather than concealing residuals.

## Manual checklist: still unverified for this new package

There is no need to repeat accepted refueling/rest-interaction tours. During ordinary play or a copied-profile check:

- Confirm the mod activates without the vanished background or N2 and without a Ford requirement; inspect the new icon/title. Check the game log for missing includes, MAT/TOBJ/DDS load errors or unsupported texture warnings.
- Open the full-screen map. Pan through the USA, Canada, Alaska/Yukon and Mexico; check reachability of the installed areas, land/water contrast, readable borders/labels and absence of rotated tiles, seams or black/missing quadrants. Compare a few familiar coastal/border locations with the alignment previews; report conspicuous offsets.
- Zoom from city view through the farthest world level and back. Check panning limits and the overview/tile transition, particularly when crossing the center of the atlas. Note readability and texture/performance issues.
- In your car, inspect nearby fuel/rest icons in the available navigation interface and the full-screen map at normal zooms. Record which interface and zoom if something is missing; N2's earlier success does not validate this replacement. No new fueling/rest transaction is required to evaluate presentation.
- At a convenient existing truck location, compare ordinary truck/navigation/city/route markers. Check that route and discovery colors remain familiar. After a normal save/reload, note whether the background and icon presentation persist.

If an issue occurs, report location, interface/zoom, game version, active background/map-data overrides, screenshot and relevant log messages. Runtime results remain yours to supply; no launch, installation or save modification was performed by the agents.

## Reproduce and redistribute

Use the [documented build command and versioned configuration](../examples/north-america-background/README.md). The handoff directory also includes a [corresponding project source ZIP](../../local_outputs/generated/2026-10-23_21-48-34/szczerbs-road-trip-north-america-background-1.61-r0-source.zip) for implementation commit `53ff7b3` (source ZIP SHA-256 `ca73047bc6ddf40b897070b1d72d08707060c6e641d51cb6ea4ddf6c1299447b`); it is source, not another mod to enable. All source geographic/font data is fetched by hash with permitted terms, and the normal build runs offline.

Original code, authored definition/cartographic composition/icon and configuration: **AGPL-3.0-only**. Natural Earth vectors: public domain, with dataset provenance/pins in source. DejaVu font/tool/library rights remain separate; the mod contains license/attribution notices and no font binary. Redistribution of the authored materials requires preserving notices and providing their preferred modification sources; the source bundle includes the pipeline/configuration/fetch instructions. No third-party background art/definition is included. This local delivery does not publish or push anything.
