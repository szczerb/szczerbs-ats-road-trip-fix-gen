# Dawson City PoC feedback and variant identity — 2026-10-19

Applicable baseline: ATS 1.61 / Road Trip Ford, original Alaska-based Dawson r0 alternatives from TASK-0039. This follow-up stays on `codex/gas-station-car-rest-research` in its retained worktree. [Task](../tasks/done/TASK-0040-identify-dawson-test-and-label-variants.md) · [Original research](GAS_STATION_CAR_REST_RESEARCH.md) · [Original handoff](GAS_STATION_CAR_REST_POC_HANDOFF.md).

## User report and screenshot scope

**Documented — user report:** both `.scs` files were present in the mod folder but enabled/disabled individually from the title-screen manager. This does not imply simultaneous activation. Both manager descriptions were identical and their long titles/package names were truncated, so the user could not identify the successful test by name. The first trial displayed a full-screen map icon but the user could not find a rest position. The second exposed an interaction on the dark asphalt in front of the building. The player describes the supplied vehicle position as the furthest-left point with that interaction, sees no painted car parking lines, and suggests extending along the building toward the next pump.

**Observed locally — images:** the two UI captures reproduce the metadata defect. The gameplay frame shows the striped player car beside the building-side asphalt strip, left of another parked car. Its HUD asks to switch off the engine; it does not independently show a completed rest or fatigue recovery. The interaction result is attributed to the user's report and supported by the log below. List ordering and its relationship to archive timestamps remain **Unknown** and are not used for attribution.

Ignored evidence is retained under `local_outputs/work/2026-10-19_18-49-11/dawson-user-feedback/`, including untouched screenshot copies, SHA records, a snapshot of the existing game log, and the event-attribution JSON. New image/log evidence remains ignored rather than introducing additional large or private source files into Git.

| Image | SHA-256 |
| --- | --- |
| `Zrzut ekranu 2026-10-19 182044.png` | `b3d7385ebdc376b497d564204bdbe0f9631e9cee4d7905572b75c167e52a06b0` |
| `Zrzut ekranu 2026-10-19 182053.png` | `ef407f5c97f71682ca423f5cdef03d22fc6c94bf4c7d7ff40e59d1b1c6d42f4e` |
| `ats_20261019_182957_00.png` | `b0d172f6f13c59ae288a3cb00f308f43ab9b7bcc522e0c3c40853553e38d7dac` |

## Exact attribution from the game log

**Observed locally — preserved log:** startup is dated `2026-10-19 18:17:27` local time. The captured `game.log.txt` has 536,806 bytes and SHA-256 `cf9e4e3c67ddc4ddef23bf918ae2cf801ef926c19d0a749ca7c2870e75e3afc3`. Both installed r0 archive hashes match the exact original handoff: painted `c29ed511c66cc14709385106a67af5112f80ac9e6efcd0f6215647dce55bb63f`; geometry `2af31469fa7be3ddea7ecee315cac7ad12ea9a7e828059b06e9722e7b6d6f02e`.

| Preserved log line | Session elapsed time | Event |
| --- | --- | --- |
| 3267 | `00:03:44.783` | Gameplay stack mounts `unmarked_geometry` |
| 4239 | `00:07:19.388` | Subsequent gameplay stack mounts `painted_bays` |
| 4750–4764 | `00:09:37.808` through `00:12:22.604` | Repeated `Handled action (Parking - Small vehicles)` events in that painted session |
| 4765 | `00:12:30.136` | Screenshot requested, matching wall-clock 18:29:57 |
| 4766 | `00:12:33.251` | Exact `ats_20261019_182957_00.png` filename written |
| 4772 | `00:12:48.257` | Small-vehicle parking action resets while leaving the world |
| 5229 | `00:13:11.284` | Geometry alternative mounts again after the screenshot |

Earlier manager preview mounts around `00:02`–`00:03` are immediately unmounted and are not gameplay sessions. There is no intervening geometry mount between the painted gameplay stack and this screenshot. Therefore **the supplied successful screenshot belongs to `painted_bays`, now labelled A LINES**. A photo-only assessment had insufficient coordinates and could have suggested the other region; the explicit screenshot event and gameplay mount chronology resolve that ambiguity. The earlier no-position-found report concerns B GEOMETRY at the position tried then. A later follow-up below supersedes it as a general statement about prompt availability: the user now reports finding B's action with navigation icons as guidance.

This establishes the observed/reported car interaction for A at this station and exact r0 package. At the time of the original report, B's prompt availability remained unresolved. Completed rest, fatigue recovery, reload stability, fuel/truck controls and broad map coverage remain individually unreported.

## What the source-model lines establish

**Observed locally — original inspected game model:** the four parallel separator components are in PIM piece 5, material alias `mat_0005_lines1`, part `part1`. Both `default` and `city` variants in the corresponding converted PIT mark that part visible. An inactive part is therefore not the explanation in this inspected model. The generator's current all-piece scan is nevertheless a general variant-filtering limitation before expanding to different families. Original strips sit at about Y 0.14610 m; sampled asphalt is about Y 0.139318 m. These are source-model observations, not proof of visible lines in the user's complete profile.

**Observed locally — actual active visual override:** the game log also mounts `Real companies, gas stations & billboards` 4.02.01 after the selected station PoC. Its installed resources override the exact same `prefab/gas/nm_truckstop1_chemron.pmg` and `.pmd` virtual names. The current PMG has 1,046,984 bytes and SHA-256 `1178ad1c0c8378d60261278e74bf52514d395479790bc711ddd5bc7843b3bf7c`, whereas the model used for initial detection had 1,143,024 bytes and SHA-256 `eaf63893a37537bc2acb5e0d961115ea1534c422b6e12c56c94dd7fee89ce491`. The current override PMD SHA-256 is `8128199e3eccb67b5843c48524aa01d9ae1d95583e9127c2a9f695962b550061`. No same-name PPD was found in that installed mod.

Consequently the original generated descriptor can drive a different visual model than the one used for source-model line detection. The earlier eleven supplied map packages were not the user's entire runtime resource stack; this visual mod was explicitly outside that original inspection. A selective conversion of that exact active model establishes the local difference: it has 23,352 vertices, 14,180 triangles, 42 pieces, three parts and 34 locators, versus the base model's 27,140 / 17,025 / 32 / three / 32. Its `mat_0006_lines1` piece 6 is visible in both variants, but its line geometry lies at X approximately −38.891…20.010, Z −124.883…−36.646; the base car-bank cluster at Z −21.144…−14.740 is absent. The same bounded bank detector finds zero painted banks in the active model. This establishes why source-model line evidence did not correspond to painted car bays visible in this profile; it is not an inactive-part inference or a claim based solely on darkness. The A label describes an inference from the original model rather than confirmed visible paint. Future geometry research must include the effective runtime model/material/variant dependencies before claiming their visible layout matches the player's scene.

**Observed locally — active-model NPC evidence:** the replacement model also adds two `car.parked.physics` locators in the A strip: `ml65` near local X 21.209 / Z −17.958 and `ml66` near X 24.072 / Z −17.739. This supports the user's observation that NPC cars occupy that strip, without proving their randomization frequency or identifying each runtime car. Applying the existing bounded mesh checker to the active model gives ground coverage and no render-obstacle hits for A, but conservatively rejects it for those parked-car locators. B's selected footprint/approach has ground coverage and no rejection in that same bounded check. Thus this visual-model change does not alone explain why the user could not find B's prompt; runtime activation position and occupancy remain separate questions. A working rest interaction is not a guarantee that every part of its polygon is unoccupied.

## Proposed enlargement

**Documented — user request:** consider the dark strip as a natural parking area and extend left along the building while leaving usable pump access. This is a sensible hypothesis for another bounded experiment, not an authorization to infer free physical space from one projection.

**Observed locally — original geometry-only diagnostics:** four adjacent 3 × 6 m candidates along one edge pass the current static checks. They span local X approximately 3.166–15.766 m, a 12.6 m run, at Z approximately −19.270…−13.270 m. These are candidates of method B, not an already-validated enlargement of the successful A polygon. Nearby rejected candidates carry pump-interaction, building/canopy/obstacle-proxy or model-clearance conflicts. They must not be included merely to form a large rectangle.

**Historical geometry hypothesis:** a contiguous usable strip or several adjacent parking footprints could be evaluated on the effective visible model, retaining pump, approach, door/furniture and NPC occupancy clearances. Any wider polygon would need to follow those exclusions rather than extend indiscriminately to the other end of the building. The newer feedback below reports B prompt availability and defers geometry changes; this earlier proposal is not an active placement instruction. No geometry, trigger, NPC, source service or live profile was changed in this metadata follow-up.

## 2026-10-19: B GEOMETRY and navigation-icon follow-up

**Documented — first-hand user report:** the user now confirms that both A LINES and B GEOMETRY expose a small-vehicle parking action at the Dawson test site once navigation icons help locate the position. This supersedes the earlier B trial's “no position found” as a statement of overall prompt availability; it does not erase the fact that the earlier attempted position had no prompt. No completed rest or fatigue recovery was reported.

The user describes B's usable position as precise and unintuitive. Of three nearby positions, one displays the prompt while positions slightly forward or backward do not, despite apparent curb space. The user reports this as a placement/usability issue and does not establish that polygon size alone causes it. **Geometry changes are deferred**; no placement heuristic change is made here. A possible relationship to the vehicle activation reference point or footprint is a **Hypothesis** for future investigation, not a diagnosed cause.

**Documented — first-hand user report:** N1 NAV PARKING now shows parking icons in vehicle navigation. The fuel icon remains absent even though the in-world fuel action avatar is visible; no fuel transaction result is implied.

**Observed locally — supplied images and log:** the three unchanged captures `ats_20261019_202859_00.png`, `ats_20261019_202919_00.png` and `ats_20261019_202947_00.png` and their hashes are listed in the [evidence manifest](../../local_outputs/work/2026-10-19_20-36-39/navigation-followup/evidence.json). All are 5120 × 1440. The first shows the engine-off prompt and the next two do not. The images show the HUD; navigation-icon visibility is reported by the user and is not directly shown in these captures. The preserved 457,425-byte log (SHA-256 `b18f554ccaca04f71126ce1d60c6dbfee3ab477d1c8ba1d06578e70285c3756f`) mounts B GEOMETRY and N1 before the captures and records nearby parking-action handled/reset events. Thus the images are attributable to the B + N1 session. Pixel positions do not establish metric offsets or geometry dimensions.

The overhead images are already copied unchanged inside the retained research worktree; their identities were rechecked against the supplied originals on 2026-10-19. These links are relative to this document and point to ignored, local-only evidence:

| Project copy | Observed prompt / user-reported position |
| --- | --- |
| [202859 overhead screenshot](../../local_outputs/work/2026-10-19_20-36-39/navigation-followup/ats_20261019_202859_00.png) | Engine-off prompt visible; usable B position. |
| [202919 overhead screenshot](../../local_outputs/work/2026-10-19_20-36-39/navigation-followup/ats_20261019_202919_00.png) | No prompt visible; the user describes a slightly forward position. |
| [202947 overhead screenshot](../../local_outputs/work/2026-10-19_20-36-39/navigation-followup/ats_20261019_202947_00.png) | No prompt visible; the user describes a slightly rearward position. |

For a goal prompt, use the same `local_outputs/work/2026-10-19_20-36-39/navigation-followup/<filename>` paths relative to the worktree root. The adjacent `evidence.json` and `game.log.txt` retain hashes and session/action attribution. These images help compare visual placement and observed activation; they are not a metric overhead survey or sufficient data to hardcode world coordinates. Other checkouts must be supplied the local evidence or reuse the preserved copies under the [image-evidence rule](../project/WORKING_AGREEMENTS.md#image-evidence).

Fatigue recovery, reload behavior, truck controls, fuel completion, numerical price/billing, and broader coverage remain unreported. This feedback does not establish that every apparent curb area is valid, and it supplies no reason to change generation heuristics now.

## Corrected experiment identity and delivery

**Documented — user instruction:** every experimental alternative must be distinguishable in its metadata. [AGENTS](../../AGENTS.md), [working agreements](../project/WORKING_AGREEMENTS.md#artifacts-and-experiments), and the [metadata contract](MOD_METADATA.md#experimental-variant-identity) now require an early stable label in the title, filename and first description line, a readable method/area explanation and an explicit activation rule.

The labels are **A LINES** / `a-lines-…` for `painted_bays` and **B GEOMETRY** / `b-geometry-…` for `unmarked_geometry`. Both files may be installed in the folder; activate exactly one, replacing Alaska r9 at its original source-relative position. Keep WCE r9 and the other source fixes enabled as before. Labelled copies are metadata-only and do not enlarge either polygon. Original r0 archives remain untouched. The production metadata helper now creates these identities for new generations as well; dimensions follow geometry config parameters rather than a fixed station assumption. Existing workflow tests compare both alternatives and assert early title/filename/description distinction while keeping the planned-resource payload unchanged.

**Observed locally — metadata-only package audit:** both corrected archives retain the exact original 28-member set and all **25 gameplay members** byte-for-byte. Only `manifest.sii`, `mod_description.txt` and the internal report change. The report identifies the original archive hash and metadata-only reissue; geometry is unchanged. Both archive CRCs pass, the full suite passes **326 tests**, and the focused station workflow module passes six tests.

| Variant | Corrected filename prefix | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| A LINES | `a-lines-` | 573,214 | `08712d133f0ebc4002e7d2a4dce590da9836de70d33e166971b1d5100964ad94` |
| B GEOMETRY | `b-geometry-` | 599,476 | `90cdc5af012422d468ff494f0957d88b864e3ebec35d9ecd803912654b731424` |

Both labelled SCS files are in `local_outputs/generated/2026-10-19_18-54-57/`, with their label prefix added before the original descriptive filename. Metadata-only comparisons, per-gameplay-member hashes and the bundle audit are in the ignored feedback evidence directory. Their two titles differ from the first characters, descriptions distinguish the inference methods, and filenames preserve their labels even when truncated.

The local bundle is `local_outputs/generated/2026-10-19_18-54-57/szczerbs-dawson-city-labelled-variants-alaska-1.61-r0-experimental.zip` (369,393 bytes), SHA-256 `9c6392e3b7f35d8c0fb071785be5ce9efd94a21e0a04d42bc074f7e39f71be04`. It contains both alternatives, an English README, exact metadata-only audit and member hashes. ZIP CRC and every bundled member byte were checked. It replaces neither installed files nor the original test bundle automatically.
