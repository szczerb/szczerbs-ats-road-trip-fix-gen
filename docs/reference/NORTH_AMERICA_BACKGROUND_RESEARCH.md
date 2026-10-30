# Original North America background: ATS 1.61 research

Inspection date **2026-10-23**. Target: installed ATS **1.61.3.18**, map format 907. This concerns the geographic UI backdrop behind roads/markers. It creates no playable roads, terrain, cities or sectors. [Delivery](NORTH_AMERICA_BACKGROUND_1_61_R0.md), [reproduction and source pins](../examples/north-america-background/README.md), [ADR-0025](../architecture/decisions/ADR-0025-generate-original-geographic-backgrounds.md).

## Starting evidence and independence

**Documented — user objective:** North America Background Map 5.3 by CairamR/CAIRAM, Workshop item `3348711188`, disappeared locally after a crash/restart. The crash cause is **Unknown**; this work does not diagnose it. The former Workshop directory is absent in the current filesystem snapshot.

**Observed locally:** `master` started at `445ef58`; the existing `codex/gas-station-car-rest-research` checkout at `2d7394d` contains newer evidence. Its `CAR_PARKING_NAVIGATION_ICONS.md`, `NAVIGATION_ICONS_METADATA_1_61_R3.md`, `NAVIGATION_ICONS_PUBLICATION.md`, `REALISTIC_MAP_REPLACEMENTS_1_61_R10.md` and `navigation_icons.py` were inspected read-only. No unrelated branch commits were merged. That N2 implementation replaces `def/map_data.sii` but still references `def/map_data/{colour_data,full_detail_config,zoom_uplift_config}.sui` from the vanished background. Its publication assessment found no redistribution grant for those third-party definition bytes.

**Documented — earlier user report preserved at that branch:** N2 made both fuel and parking icons clearly visible in Mustang navigation in the reported context. Exact interface/zoom details were not itemized. That is evidence for the earlier overlay, not runtime validation of this new background. The vanished image was neither copied nor traced. This implementation serializes newly authored definitions and renders public-domain vectors.

## Actual UI resource contract

**Observed locally — read-only selective extraction from current `base.scs`, `def.scs` and `base_map.scs`:**

| Resource | Observed contract / implementation consequence |
| --- | --- |
| `material/ui/map/map.mat` | `ui.rfx`, texture source `map.tobj`, clamp U/V, no mip filtering; whole-map overview. |
| `map0..map3.mat` | Same material interface; visual inspection of recovered stock rasters establishes northwest, southwest, northeast, southeast ordering. These are geographic tiles, not four zoom levels. |
| `map*.tobj` | Binary 2D UI texture objects with absolute `material/ui/map/map*.dds` references. New serializer reproduces the observed structural bytes; no geographic art is copied. |
| `map*.dds` | Stock: 2048×2048, DX10 `B8G8R8A8_UNORM_SRGB` (DXGI 91), one mip, 148-byte header followed by BGRA pixels; flags `0x21007`, pitch field zero. New overview is 2048², four tiles 4096² (8192² atlas), same format and flags. No converter or extracted texture is bundled. |
| `def/map_data.sii` | One `map_data : .map.data` unit; arrays have eight UI tiers. New file is standalone and contains no includes. |
| `map/usa.mbd` | Current base header: 69 bytes, format 907; normal scale 20.0, city scale 3.0. Values are inspected using the [unofficial field layout](https://github.com/sk-zk/map-docs/wiki/mbd), independently consistent with SCS's [1:20 rescale announcement](https://blog.scssoft.com/2016/11/ats-world-rescale-open-beta.html). No MBD is emitted. |
| `def/climate.sii` | `lambert_conic`, parallels 33/45, origin (39,-96), factors (-1.7706234e-4,1.76689948e-4). It motivates the projection but does not establish its exact earth model. No climate changes are emitted. |

The extractor's HashFS v2 listing has TOBJ entries rather than independent DDS entries. Direct selective extraction of the TOBJs recovers embedded DDS payloads; the existing project wrapper otherwise copies only the requested TOBJ out of temporary staging. The raw UI textures were inspected solely for interoperability. Scratch: `local_outputs/work/2026-10-23_21-16-53/engine-inspection/` (inventories, five decoded stock previews, extracted header and independent review). The new implementation needs none of those images to reproduce the package.

**Observed locally / derived model:** north is decreasing game Z, east is increasing X. A world-space canvas of 500,000 units at map scale 20 corresponds to `ui_map_size=(10000,10000)` real km. The configured center is (-20000,-40000), yielding X [-270000,230000], Z [-290000,210000]. Stock center/size comments identify editor coordinates versus real km; this conversion is an evidence-based UI mapping model awaiting runtime confirmation. Do not mistake SCS's old [Map Editor reference-image guide](https://modding.scssoft.com/wiki/Documentation/Tools/Map_Editor/ATS_Map_Rescale) for the in-game UI contract.

Local tiers 0–3 retain zoom heights 50/220/900/4000; world tiers 4–7 use 1000/5000/18500/**120000**. Only the last height is expanded from stock. The generated unit names obey [SCS's token/component limit](https://modding.scssoft.com/wiki/Documentation/Engine/Units); the dedicated validator rejects overlong components even though the general text parser can parse them. Stock icon sizes, player sizes, road factors, 3D pitch, route costs/colors, all nine map-area color rows and full-detail values are explicitly preserved. The local/world camera bounds are expanded coherently; camera start remains (-90000,3000). The farthest zoom and panning behavior are **Unknown** until tested in game.

Stock masks are `0x0F685FFF` at 0–3; `0x0F685FAF` at 4–5; `0x0F685487` at 6; `0x0C481402` at 7. These include car fuel bit 24 and parking bit 25 locally. Keeping them restores the visibility inputs absent from the former background without removing unrelated stock truck/map categories. The previous N2 masked variant was `0x03685FFF` locally; the new file deliberately preserves the additional stock categories too. No marker/action/service geometry or eligibility changes are included.

## Actual compatibility and priorities

**Observed locally — supplied manifests and exact path inventories:**

| Source | Actual version | Background-resource overlap |
| --- | --- | --- |
| Base ATS and 20 installed map DLCs | ATS 1.61.3.18 | Stock overview/tiles and map-data definition. |
| ATS Expansion | 23.0 / 1.61 | None on the inspected backdrop paths. |
| Reforma Mega Resources | 3.0.1.161 | None on those paths. |
| Reforma | 3.0.1.161 | Map-data definition, five MATs and TOBJs. |
| Western Canada Expansion | 1.7.3 | None on those paths. |
| ProMods Canada Models | 1.6.4 | None on those paths. |
| ProMods Canada Assets | 1.6.4 | Five TOBJs. |
| ProMods Canada Map | 1.6.4 | None on those paths; replaces some WCE city sectors. |
| ProMods Canada Definitions | 1.6.4 | Map-data definition. |
| Reforma OtherMaps Patch | 40.161 | Map-data definition, five MATs and TOBJs. Older description text says 39.161; the supplied manifest is 40.161. |
| Western Canada ProMods Connections | 1.7.3 | None on the inspected backdrop paths; supplies winning Calgary sector. |
| Alaska Expansion | 1.2.3 | None on those paths; wins northern duplicate sectors. |

Installed map-DLC archives: Arkansas, Arizona, Colorado, Iowa, Idaho, Illinois, Kansas, Louisiana, Missouri, Montana, Nebraska, Nevada, New Mexico, Oklahoma, Oregon, South Dakota, Texas, Utah, Washington and Wyoming. The installation contains 76 SCS archives, 66 named `dlc_*`. Presence is not entitlement or proof of current profile activation. Archive path inventories do not establish live load priority; the handoff uses the user's previously declared source order and requires the background to win above every competing map-data/material provider.

The supplied source sector-name rectangle is X [-160000,36000], Z [-236000,112000]. Installed base/map-DLC rectangle is X [-124000,40000], Z [-76000,76000]. Both fit inside the configured canvas. Signed sector indices follow the game-world signs, with each cell [index×4000,(index+1)×4000]; projection northing inversion does not invert sector-name Z. These are coarse rectangles of named sectors, not a playable-road census or a whole-world absence proof.

A historical installed Reforma ProMods Background Fix supplied the same map-data values as OtherMaps; the former background and N1/N2 also conflict. Disable obsolete background overlays, and place the new package above any retained provider. It replaces these backdrop paths, not unrelated gameplay resources in a multipurpose patch. Keep all source-relative fuel/rest replacements and connector relationships unchanged beneath it. [Exact installation order](NORTH_AMERICA_BACKGROUND_1_61_R0.md#installation-and-priority).

## Calibration and accuracy

**Observed locally — 52 individually rechecked references:** each is a native CityArea node in its winning source sector, paired to a Natural Earth populated-place ID. A city with several regions uses the broadest CityArea as a deterministic representative. It can differ substantially from the real-world downtown reference, particularly in the compressed/reworked city layout. The independent delegate re-extracted all 52 sectors and verified SHA-256, item UID, node UID and XZ, and all Natural Earth coordinates/identities, with zero discrepancies.

The join was manually curated by city identifier, country and region. Ambiguous global names were corrected (Las Vegas Nevada, Mazatlán Sinaloa, Vancouver Washington). ProMods removes the lower WCE Vancouver BC marker in the winning sector, so the accepted reference is actual ProMods Abbotsford BC. Calgary follows the connector's winning sector; Alaska wins Anchorage/Fairbanks/Whitehorse/Dawson references. Do not restore the superseded WCE-only Vancouver reference.

The baseline is spherical LCC with radius 6,371,000 m, geographic meters divided by 20 and northing sign inverted. A least-squares affine fit uses 34 points; 18 check points do not affect fitting. The more flexible thin-plate option with smoothing 0.005 lowers fit RMS but worsens check RMS. Thus r0 uses affine:

| Model | Fit RMS | Check RMS | Check maximum |
| --- | ---: | ---: | ---: |
| Affine after LCC, selected | 1,995 | 2,412 | 6,381 (Fairbanks) |
| Smooth thin-plate residual | 488 | 3,081 | 6,846 |

Units are game-world XZ units. Do not describe them as surveyed physical meters or infer a precise ×20 real-world error in locally distorted cities. The selected model's check median is 2,068; fit maximum 4,119. Its deformation check samples 3,850 geographic points and reports positive area ratios (~1.0545 of the baseline). High-resolution atlas spacing is **61.035 game units per pixel**. Geographic detail/resolution and city layout impose further limits.

The check set was used for model comparison, so it is held out from fitting, not an untouched final accuracy test. The worst residual is visually explicit in the Alaska overlay. All references are in the installed western/central USA, western Canada/Yukon/Alaska and northern/central Mexico. The eastern USA, eastern Canada, far Arctic and southern Mexico are drawn from geography but lack independent game calibration points. This is an experimental compromise, not a claim of coast/road alignment at every location.

## Rights and output boundary

**Documented — primary terms inspected 2026-10-23:** [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) places all its raster/vector data in the public domain and permits modification/dissemination. Actual dataset versions and archive hashes are separately pinned; this work does not label every layer “5.1.2.” [DejaVu font terms](https://dejavu-fonts.github.io/License.html) permit the font use with its notice. No font binary is shipped in the mod; its notice is included with rendered text. Downloaded sources/tools remain ignored. No paid service or image-generation model produced the geography.

Project code, authored definitions/cartographic composition/icon/configuration are AGPL-3.0-only under [LICENSING.md](../../LICENSING.md). Data remains public domain and fonts/tools retain their own terms. A local source bundle accompanies the handoff for the authored materials; redistribution must preserve the notices and provide corresponding preferred modification sources under that license. This statement grants no rights in SCS or other map assets: none are bundled. The installed game supplies the shader/roads/icons. No public upload, push, author contact or visibility change occurred.

**Unknown — runtime boundary:** UI image mapping, texture-size acceptance/performance, world-map versus GPS background rendering, far zoom/panning, filter/interface-specific icon visibility and actual visual alignment beneath roads. Static success and earlier N2 user reports cannot establish these results for the new package.
