Resolve the remaining North America background shoreline/lake alignment defects and deliver a substantially better ATS 1.61-r3-experimental testing package.

Continue autonomously until you deliver a verified new testing version meeting the acceptance criteria below, or a genuine external blocker prevents further meaningful progress. Do not stop after another diagnosis, a failed model, finding that more landmarks are needed, or obtaining a modest aggregate score improvement while the same conspicuous defects remain. Finding reliable references and implementing a better model are part of this goal.

WORKSPACE AND STARTING POINT

Work in the existing repository root.
Read AGENTS.md, inspect the current branch/worktree and preserve unrelated changes. Continue the existing background work, normally on codex/north-america-background. Read:
- docs/project/CURRENT_STATE.md
- docs/reference/NORTH_AMERICA_BACKGROUND_FEEDBACK_2026_10_25.md
- docs/reference/NORTH_AMERICA_BACKGROUND_1_61_R2.md
- docs/reference/NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md
- docs/architecture/decisions/ADR-0027-check-backgrounds-against-road-and-shore-geometry.md
- docs/architecture/decisions/ADR-0028-calibrate-background-with-roads-and-ground-constraints.md
- docs/tasks/done/TASK-0051-recalibrate-background-to-roads-and-shores.md
- docs/examples/north-america-background/r2/ and src/ats_road_trip/background/

Baseline: local_outputs/generated/2026-10-24_18-30-20/szczerbs-road-trip-north-america-background-map-ats-1.61-r2-experimental.scs
SHA-256: 58cbfe4047113308bb82a0e5ed4d15e298515f22916bab8eb8b1fc403c521604
Source implementation commit: 18e5f13c07d976fff4a7d6f2a91275a249a5b825; delivery documentation commit: f3bfec5.
Preserve r0/r1/r2 archives and source bundles unchanged as historical fallbacks.

USER FEEDBACK AND ACCEPTED BEHAVIOR

On 2026-10-25 the user confirms that r2 job-market zoom is fixed and usable. Preserve zoom_uplift[7]=60000, all other zoom tiers, icon/navigation masks and the entire packaged def/map_data.sii byte-for-byte against r2. Do not reopen zoom tuning or request another initial market/icon confirmation. The user's suggested zoom quantization explanation is unverified; the reason the earlier smaller change was not perceptible remains unknown and is outside this repair's priority.

Shoreline alignment is still unsatisfactory. The user thinks some places improved slightly, but the same places still have problems, and supplied 25 main-world-map screenshots of everything that looked odd at first glance. Treat that report as stronger practical acceptance evidence than r2's aggregate offline improvements. Do not infer every individual defect, exact projection cause, or an itemized mode/interface pass from this general report.

NEW EVIDENCE

All 25 PNGs exist despite the desktop attachment-reader errors. Read the verified inventory:
local_outputs/work/2026-10-25_00-22-06/screenshot-inventory/inventory.json
Preserved originals:
local_outputs/work/2026-10-25_00-22-06/screenshot-inventory/user-evidence/
Overview contact sheet:
local_outputs/work/2026-10-25_00-22-06/screenshot-inventory/contact-sheet-25.png
Original source directory, read-only:
local_outputs/work/2026-10-25_00-22-06/screenshot-inventory/user-evidence/

Exact filenames are ats_20261025_<TIME>_00.png, with TIME:
000340, 000349, 000357, 000407, 000417, 000429, 000435, 000441, 000447,
000500, 000506, 000513, 000520, 000524, 000538, 000548, 000553, 000606,
000640, 000655, 000735, 000748, 000756, 000808, 000817.

The inventory is evidence preservation and a preliminary thumbnail review, not a completed geographic defect catalogue. Inspect every full-size screenshot. Identify each location, affected roads/cities/shore features and the actual suspicious relationship. Record uncertainty rather than guessing. Link overlapping views to shared defects so repeated images do not artificially weight one region.

Reuse sound existing evidence from:
- local_outputs/work/2026-10-24_17-09-42/ (r2 fitting, corrected native extraction, route/ground/bridge audits and final regressions)
- local_outputs/work/2026-10-24_16-17-05/ (r1 screenshots, atlas registration and global-transform experiments)
- local_outputs/work/2026-10-24_02-39-28/ (effective-source census and geographic data)
- local_outputs/generated/2026-10-24_18-30-20/ (r2 comparisons and verification)
Validate source hashes and effective resource priority before reuse. Check current game-log/package evidence read-only if needed; do not assume r1 registration matrices automatically apply to r2 screenshots.

DELEGATION AND COST

Delegate bounded parallel work to economical subagents with explicit file ownership:
- GPT-6 Luna low/medium: source inventories, screenshot indexing, resource-priority checks and mechanical extraction/reporting.
- GPT-6 Luna high: native road/prefab/bridge/bank correspondence analysis, geographic feature identification and independent numerical/visual audits.
- Main model: correspondence acceptance, model design, integration and final verification. Use a stronger delegate only for a specific unresolved technical ambiguity that warrants it.

Give each agent a small deliverable, source/provenance requirements and scratch directory. Review their claims independently. Reuse cached sound work, avoid repeated whole-world scans and endless parameter sweeps, and retire unproductive hypotheses. Record actual model/effort assignments and checks in the task. If entering Plan Mode, include the required task/model/effort table. Delegation does not replace main-agent inspection of the final before/after views.

REPAIR APPROACH

1. Build a defect catalogue for all 25 views. Separate geometric displacement, inadequate source-shore detail, raster/texture sampling, expanded game-city footprints and legitimate water crossings. Coarse pixels alone do not prove a projection defect, and smoother rendering alone does not repair displaced geography. Define region-level acceptance checks before tuning.

2. Find identified geographic/native correspondences that constrain both X and Z: route intersections, bridge landings and approaches, river mouths, peninsula/bay features, lake banks/islands and other reliable landmarks. Verify semantic identity, effective map provider, coordinate frames, units and uncertainty. A generic model origin/bounding box is not automatically a shoreline; a bridge-inventory point is not automatically its mesh center. Read native resources without changing them.

3. Evaluate the limitations of r2 explicitly. Its normal-distance route fitting allows tangential slide. Its checks mostly interpolate near same-route fitting observations. All 962 ground facts were used for fitting. Its signed-distance mask classifies rendered labels/strokes as non-water. Endpoint-only metrics miss road curves, ramps, prefab junctions and full urban footprints. Sparse/thresholded aggregate scores can hide the exact defects the user sees. Address these weaknesses rather than repeating their acceptance test.

4. Use clean vector land/water geometry or an unstyled classification mask for shore constraints; distinguish bridges/piers/elevated structures and uncertain ground-use facts. Inspect actual native road curves and relevant prefab/urban footprints where available, not only a few endpoints or CityArea centers. Label chord/approximation limits honestly. Preserve legitimate water under bridges and correct land approaches; dry bridge channels are defects too.

5. Compare supported calibration approaches. You may replace r1/r2's geographic calibration or field design when evidence supports it; retaining the old affine/865 coefficients is not a requirement. Investigate coherent regional/multiscale or feature-constrained mapping where global projection changes are insufficient. Avoid arbitrary coast painting, generic land buffers, tracing protected native artwork, or moving playable roads to fit the background. Geometry/detail changes must follow identifiable features, preserve sensible topology and remain reproducible. Audit folds, excessive stretch, continuity, coast/lake consistency and uncertainty. Investigate atlas/overview sampling or texture density separately if necessary, with practical memory/resource checks and preserved world-to-texture mapping.

6. Use independent validation: withhold whole geographic groups/corridors where feasible, plus separately identified two-dimensional landmarks and road/shore relationships. Freeze the check set before final tuning; disclose reused check data and selection bias. Report regional and worst-case behavior, including small-but-conspicuous offsets. Neither training RMS, city-center pixels, the old >500-unit threshold nor fewer water pixels is sufficient acceptance evidence.

REQUIRED COVERAGE AND ACCEPTANCE

Account for every new screenshot, and regress earlier reported regions: southern/northern Baja; Los Angeles/San Diego and the Pacific coast northward; Vancouver Island/lower mainland and northern ports; Brownsville/Corpus Christi/Galveston/Lafayette/New Orleans; Chicago/Lake Michigan; Canadian lake belt; Mobridge/Lake Oahe; previously corrected Alaska/Canada.

For each distinct reported defect, provide the original view, a registered/world-aligned r2-versus-candidate comparison with identical native geometry, and a status: resolved, materially improved, unchanged, regressed, intentional crossing, or uncertain. Give evidence and severity. Validate comparisons at the user's close world-map scale as well as regional scale. Do not silently omit difficult views or present unverified matches as facts.

The release gate is a clear visual and quantitative improvement across a substantial majority of the independently identified problem areas, including conspicuous coast/road conflicts, with no unexplained new severe regression. Predeclare what constitutes material improvement using feature scale and source uncertainty, then assess the candidate against it. Keep unresolved defects explicit and continue improving if the result merely shifts the same errors or improves only a headline average. Fully eliminating every unavoidable game-versus-real-world discrepancy is not required, but another small statistical improvement without convincing screenshot-level repair is insufficient.

IMPLEMENTATION, VERIFICATION AND DELIVERY

Produce 1.61-r3-experimental with the existing title/author, accepted appearance and standalone/no-Ford scope. Keep r2 map_data.sii byte-identical and separate fuel/rest/courier/tank mods untouched. Use appropriately licensed geographic data/tools; native facts may inform interoperability calibration, but do not distribute protected game/map assets, traced native artwork or diagnostic overlays as mod artwork/source assets.

Deliver:
- One clearly identified authoritative SCS, SHA-256 and corresponding source ZIP.
- Overall/regional previews and inspectable comparisons covering every supplied view.
- Per-defect results, independent landmark/region checks, full road/shore diagnostics where available, worst cases, and explicit regressions/uncertainty.
- Resource graph, encoded texture/quadrant, bounds/mapping, deformation/topology, unchanged map-data/navigation-mask and relevant regression checks.
- Deterministic repeat build and exact rebuild from the extracted corresponding source ZIP.
- Committed configuration/provenance, meaningful local commits, task/current-state/ADR updates, reproduction commands, load order and concise manual handoff.

Follow AGENTS.md artifact conventions: current Europe/Warsaw timestamped ignored work/generated directories, immutable local_inputs and old outputs, small English authored documentation only in Git. No game launch, live installation, profile/save changes, economy reset, push/publication or paid services. Licensed public downloads, read-only local inspection, local tooling changes and verified local commits are authorized within this goal.

Keep brief meaningful progress updates and carry work through compaction. Do not ask routine permission or end with a research-only report when independent work can continue. A failed model or missing first-choice correspondence is not an external blocker. If genuinely blocked, preserve work and state the exact missing input, alternatives exhausted, why no meaningful independent work remains and the minimum external action needed. Final runtime acceptance remains mine; do not claim an in-game pass.
