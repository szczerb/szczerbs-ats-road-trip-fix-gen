# F BATCH r1 — user tour feedback received 2026-10-21

**Documented — first-hand user report, received 2026-10-21:** the completed F BATCH table, its Notes, all screenshot filename comments, all 20 images, and the accompanying chat form one report. The screenshot set accompanies the tour completed by this report. This records user gameplay and agent inspection of evidence; the agent did not reproduce gameplay or modify the tool, mods, game or profile.

## Setup and evidence boundary

The user used a newly downloaded test profile from a mod site, with approximately $100M and all base-map garages unlocked. Garages outside the base map were unavailable for quick travel, so the user drove from nearby US cities to foreign test sites. P05 Dawson was skipped because of the travel burden. Its similarity to P06–P08 is the user's expectation, not a P05 result. P08 was visited and reported equivalent to P06/P07; no P08 screenshot was taken. Some of these Canadian stations have an adjacent mechanic, with no reported effect on the parking judgment.

The handoff baseline is ATS 1.61.3.18 and F BATCH r1 over retained source-relative r9 fixes, with independent N2. The exact runtime build, installed archive fingerprints and active order were not independently captured for this report; setup confirmation is requested from memory. The profile's downloaded provenance does not by itself invalidate the reported parking observations.

The filled table is preserved unchanged in an ignored snapshot. Existing project-local images are reused unchanged rather than duplicated. Filename comments are primary feedback, even where they describe something beyond the table. Relative links below resolve from this document. All large evidence is local-only in the retained research worktree; another checkout needs the same relative evidence paths or verified copies from that worktree.

- [User-edited README](../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/README.md) — SHA-256 `000c5417636655ead7a449275940bf600f54b72333d4bdcaae43b122704488cd`.
- [Unchanged intake snapshot](../../local_outputs/work/2026-10-21_00-48-35/forecourt-tour-user-report/README-user-report.md) and [20-image provenance/hash manifest](../../local_outputs/work/2026-10-21_00-48-35/forecourt-tour-user-report/evidence.json).
- [Original handoff, exact site identities and source dimensions](STATION_PARKING_FORECOURT_TOUR_1_61.md). The original delivered ZIP/SCS remain immutable. The subsequently edited directory is user evidence, not a claim that its changed README still matches the old bundle checksums.

## Combined per-site result

All outcomes below are **Documented — user report**. Visible details are **Observed locally — screenshot inspection, 2026-10-21**, not calibrated world measurements.

| Site | Visited / evidence | Combined result |
|---|---|---|
| P01 Roswell | Yes; image 01 | Found, natural pose and prompt all Yes. Two bays to the left were NPC-occupied, including the bay marked original in the handoff. Image shows the Mustang in an ordinary bay beside an accessible bay, with an engine-off prompt. |
| P02 Parral A | Yes; images 02–06 | Found, natural and prompt Yes; regular bays on both sides work and are easy to use. One icon/combined region also permits stopping in the circulation space between perpendicular banks. User proposes splitting coverage into the two banks. Image 03 proposes an additional unmarked curbside position behind/alongside the building; it is a suggestion, not a proven generated or working spot. |
| P03 Parral B | Yes; images 07–09 | Found, natural and prompt Yes in usable regular bays. Similar oversized combined-area concern. A separate building/support intrudes into the corner bank; user objects to parking that blocks both banks. Image 09 shows an engine-off prompt in the hatched propane/equipment exclusion area. User also reports the accessible bay works and leaves its desirability undecided. |
| P04 Mazatlán | Yes; images 10–15 | Found and natural Yes, prompt Yes but not all spaces. Large combined area permits both sensible edge positions and an undesirable middle position. On the opposite side, hatching and accessible bay did not activate; user tentatively accepts those exclusions. The neighboring ordinary bay failed or perhaps flashed a prompt only briefly, so activation of that target is uncertain. |
| P05 Dawson | No; no images | Skipped. Do not extrapolate the other placements into runtime acceptance here. |
| P06 Powerview | Yes; table only | Found/prompt Yes, natural Not exactly. A single small active spot occupies a much larger plausible unmarked strip; several bays or a wider combined area might fit. Activation requires stopping short of the curb. |
| P07 Gimli | Yes; image 16 | Found/prompt Yes, natural Not exactly. Requires a gap from the curb; space farther right could accommodate additional cars, as suggested by the parked NPC. Screenshot shows the active Mustang visibly farther from the curb than a nearby NPC, with its rear near the circulation strip. |
| P08 Bissett | Yes; table only | Found/prompt Yes, natural Not exactly. User reports the same issues as P06/P07 and deliberately did not take another screenshot. |
| P09 Las Cruces | Yes; images 17–20 | Found/prompt Yes, natural No. User proposes rotating the layout 90 degrees and estimates room for about three cars. Image 20 shows a resting-place/not-tired message in the current awkward pose alongside the storefront; image 18 shows a more natural perpendicular pose without a prompt. Images 17/19 document original areas with substantial NPC occupancy. |

Eight sites were visited and some parking interaction was found at each; this is not eight verified generated-bay successes. P04's intended ordinary bay remains unreliable, and attribution of other marked-lot interactions needs analysis. Engine-off, rest-key and not-tired messages are interaction evidence. Completed rest, measured fatigue recovery, truck/fuel controls and save/reload persistence were not separately reported.

## Interpretation and next research

**Observed locally — final handoff reports/configs:** F BATCH adds exactly one four-vertex car polygon per selected site. P01–P04 each add a single 3.35 × 4.99 m rectangle. It does not generate the broad right-angle combined regions described in Mexico. Preserving selected source PPD triggers also does not prove that a separate prefab/standalone item at the same visual station has no parking. The census contains service-only companion prefabs near P02/P03/P04. **Observed locally — bounded attribution check:** their `prefab/gas/us_gas_station_trigger_only_rt.ppd` has no trigger/action groups or native parking in the [hash-verified descriptor census](../../local_outputs/work/2026-10-19_23-21-30/action-census/descriptor-action-groups.json), SHA-256 `0bacf050ae1d9bc4e5040de7f5332165ca912be7fffcba306f56425ff74c65d8`. Those particular companions therefore do not explain the broad active rest areas in the declared stack. Nearby P04 warehouse UI polygons are obstacle proxies, not evidence of parking actions.

**Hypothesis:** some excessive Mexican activation comes from another existing prefab/standalone parking item or a different effective runtime setup rather than the new rectangle. Do not label those areas heuristic failures, or alter original triggers, until source ownership and effective coverage are established. Inspect other existing native/r9 parking items and exact transforms, and establish the effective runtime setup, before asking the user for another long driving tour. Exact runtime action ownership cannot be proved from the screenshots alone.

The next geometry work has distinct evidence-backed targets:

- Make unmarked activation correspond to a natural curbside pose, including the actual vehicle activation reference and usable tolerance. Do not assume the entire rectangular vehicle footprint controls activation, or simply enlarge into circulation space.
- Reconsider parallel/perpendicular ranking for P09 using real access and occupancy constraints. The user's three-car estimate is a candidate capacity, not a measured clearance result.
- Account for separate nearby buildings/supports and actual NPC-occupied bays; P03 demonstrates why model-local evidence alone is insufficient.
- Consider additional usable capacity where geometry permits it, keeping drive-through space, hatching, pumps and pedestrian access clear. The P02 extra curbside suggestion needs the same clearance evaluation.
- Resolve P04's intended bay against its height, transform and activation envelope before treating similar-looking painted stations as uniformly successful.

Accessible-bay policy remains **Unknown / user preference pending**. The report expresses uncertainty rather than authorizing a global policy. Broad existing-area repair, if needed, is a separate scope choice from adding new parking; no original parking has been changed during this intake.

## Screenshot index

Each link preserves the user's exact filename/comment. Root reviewed every full frame and a central detail view; derived JPEG previews are inspection-only and do not replace originals.

| ID | Original screenshot / filename comment |
|---|---|
| 01 | [P01-works.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P01-works.png>) |
| 02 | [P02-also works great and easy to park.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P02-also works great and easy to park.png>) |
| 03 | [P02-suggestion for another spot in this station layout.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P02-suggestion for another spot in this station layout.png>) |
| 04 | [P02-works and another very good and easy to park.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P02-works and another very good and easy to park.png>) |
| 05 | [P02-works but probably should not as it is kinda in the middle actually a place that you drive through into the two sets of parking spots nearby.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P02-works but probably should not as it is kinda in the middle actually a place that you drive through into the two sets of parking spots nearby.png>) |
| 06 | [P02-works great and easy to park.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P02-works great and easy to park.png>) |
| 07 | [P03 works great.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P03 works great.png>) |
| 08 | [P03-works but look at how the one in the corner is blocked off by a bulding support and also a building wall is slightly on the edge of the other one.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P03-works but look at how the one in the corner is blocked off by a bulding support and also a building wall is slightly on the edge of the other one.png>) |
| 09 | [P03-works but should not as it is clearly marked with multiple lines not to park there and also the disabled spot works fine which I am not sure what to think about.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P03-works but should not as it is clearly marked with multiple lines not to park there and also the disabled spot works fine which I am not sure what to think about.png>) |
| 10 | [P04-and probably also good that the handicapped space is not functional but I am still unsure those.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P04-and probably also good that the handicapped space is not functional but I am still unsure those.png>) |
| 11 | [P04-could not get this one to work.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P04-could not get this one to work.png>) |
| 12 | [P04-good that it does not work.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P04-good that it does not work.png>) |
| 13 | [P04-works but should not as it is too much in the middle of the lot.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P04-works but should not as it is too much in the middle of the lot.png>) |
| 14 | [P04-works good spot in the corner of the too large combo area.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P04-works good spot in the corner of the too large combo area.png>) |
| 15 | [P04-works good spot on the right of the too large combo area.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P04-works good spot on the right of the too large combo area.png>) |
| 16 | [P07-works but only in a specific spot away from the curb.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P07-works but only in a specific spot away from the curb.png>) |
| 17 | [P09-and the corner originals for reference all taken by NPCs.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P09-and the corner originals for reference all taken by NPCs.png>) |
| 18 | [P09-same place better orientation not working.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P09-same place better orientation not working.png>) |
| 19 | [P09-shot of originals for reference most taken by NPCs.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P09-shot of originals for reference most taken by NPCs.png>) |
| 20 | [P09-works but weird position.png](<../../local_outputs/work/2026-10-19_23-16-09/forecourt-tour-handoff/bundle/game screenshots/P09-works but weird position.png>) |

## Verification and continuation

Root reviewed the complete edited table, all filenames, and all 20 images; captured the README and original image fingerprints; and left originals and historical ZIP/SCS untouched. The existing `batch_station_inventory` delegate (GPT-6 Luna, high effort) performed a bounded read-only attribution review of the source inventory/reports and companion-prefab evidence. Root retains responsibility for integrating those findings; unresolved ownership stays a hypothesis. This is a documentation-only intake, so generator tests were not rerun. Link targets, immutable evidence hashes, archive identities and whitespace are checked before commit.

[TASK-0007 runtime validation](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) remains active. TASK-0045's delivery milestone remains complete; these results inform a later heuristic increment. No new mod, installation, profile change, master merge, push or publication is part of this report intake.
