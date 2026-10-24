# North America background r0: user gameplay feedback, 2026-10-24

Applies to the r0 background delivered in [TASK-0048](../tasks/done/TASK-0048-build-original-north-america-background.md). The user supplied feedback during ordinary play, requested collection without investigation until finished, then authorized investigation and continued work in [TASK-0049](../tasks/done/TASK-0049-correct-background-alignment-and-job-market-zoom.md). No agent launched ATS, installed a mod or edited a profile.

## Reported positives and scope

**Documented — user reports:** the background generally works, looks good, and its visual style is liked. Extra world-map zoom-out is appreciated. Truck navigation looks fine so far. A later short switch into car mode confirms **both refueling and parking icons display correctly in car navigation**. This supersedes the r0 handoff's blanket unknown status for that reported presentation check; it is not proof of every location/interface/zoom, or a completed fuel/rest transaction, fatigue recovery, billing, or save/reload behavior.

## Job selection

**Documented — user report:** Quick Jobs, normal job market and External World of Trucks job-market maps are too zoomed out, making cities difficult to select because markers crowd together. Those screens do not offer zoom controls in the reported context. The user requests approximately **20% closer presentation**, preferably independent of world-map far zoom. If coupled, usable job-city selection takes priority and the user accepts losing some extra world-map zoom-out.

Screenshot: `ats_20261024_004056_00.png`. **Observed locally:** the supplied view is the External Contracts market; the map shows dense overlapping city dots/rings. It illustrates that screen specifically, while the three-screen scope comes from the user's report.

## Geographic alignment

**Documented — user reports:** Mobridge, South Dakota appears in a large lake; other cities appear over the ocean or lake water, and a northern port looks too far inland. Later screenshot batches cover coasts/lakes and the USA's borders with Canada and Mexico. The user did not enumerate every location and did not claim a uniform offset vector.

**Observed locally — screenshot inspection:** the six Mobridge cab/map pairs show the in-game waterside road and the backdrop's water outline crossing the city/road network. Natural Earth's named feature is Lake Oahe. The coast/lake batch includes California, the ProMods/WCE lower mainland and Vancouver Island, Alaska/panhandle towns, Manitoba's lake region, and Chicago. The border batch spans the USA–Mexico southwest and the USA–Canada west/central boundary. Pixelated outlines and local map-versus-geography differences limit precise screenshot-only offset measurement; source geometry and coordinate checks are needed before attributing all symptoms to a projection error.

## Evidence preservation and accessibility

The desktop attachment reader reported missing Windows paths, but **all 43 referenced PNGs exist** through `local_outputs/work/2026-10-24_02-39-28/user-evidence/`. They were copied read-only into ignored `local_outputs/work/2026-10-24_02-39-28/user-evidence/`; the originals were not renamed/edited. [Snapshot inventory and SHA-256 values](../../local_outputs/work/2026-10-24_02-39-28/user-evidence/inventory.json) records one market screenshot, 12 Mobridge views (six cab/map pairs), 23 coast/lake views and seven border views. The exact file lists are in that inventory; no screenshots or game assets are committed to Git.

Luna/medium visually reviewed all 30 coast/lake/border images; root reviewed the market and Mobridge images plus selected regional detail. Diagnostic crops/contact sheets and source-review notes remain in the same timestamped run. They are evidence aids, not substitute screenshots or artwork for the mod.

## Follow-up boundary

Preserve the accepted style and navigation masks. Investigate market zoom separately from geographic image scaling; do not change `ui_map_size` merely to zoom job selection. Compare coastline detail, land/water geometry, global/region calibration and local city compression, without claiming that a lower numerical point RMS alone repairs coast/road placement. The new revision will require the user's subsequent runtime validation; the accepted r0 car-icon check should not be requested again as if unreported.

**Follow-up implementation — 2026-10-24:** [r1 package and measured limits](NORTH_AMERICA_BACKGROUND_1_61_R1.md) provide finer geography, bounded corrections and the shared zoom experiment. Split Lake and representative-center uncertainty remain explicit; no new runtime pass is claimed.
