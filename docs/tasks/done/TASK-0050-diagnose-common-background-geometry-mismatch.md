---
id: TASK-0050
title: Diagnose the common background geometry and fixed-market scale mismatch
status: done
priority: high
repositories: [.]
depends_on: [TASK-0049]
owner: shared
---

## Goal

Find and quantify a common sizing, coordinate mapping or projection problem explaining the user's persistent r0/r1 coastal/lake misalignment. Correct a demonstrated common defect if possible; avoid another unsupported local calibration revision.

## Context

**Documented — user r1 testing, 2026-10-24:** all original practical defects remain, perhaps slightly shifted. Market zoom remains too far out, identical in truck/car modes. West coast screenshots show Baja roads/cities east of the peninsula and Los Angeles/San Diego west of land. Gulf Coast roads cross backdrop water near Brownsville, Corpus Christi, Galveston, Lafayette and New Orleans. Chicago partly overlaps Lake Michigan; Canadian roads shaped to avoid lakes lie in their water. User hypothesis: background slightly too small or projection mismatch. Feedback collection ended explicitly before this investigation.

R1's offline reference-center tests did not establish runtime road/background correspondence. Preserve r0/r1 historical evidence without treating those tests as proof that the practical issues were repaired. No game launch, live installation, profile writes or push.

## Scope

Recover 18 unique new screenshots and current game log read-only; verify actual r1 loading/content/priority. Independently measure game-to-screen and image-to-screen mappings, inspect effective MBD scale and UI mapping semantics, and audit reference-point validity. Separate common defects from local native city/map distortion and market UI behavior. Main owns tracked integration; delegates own bounded scratch only.

## Implementation Plan

1. Preserve screenshots/log under `local_outputs/work/2026-10-24_16-17-05/` with hashes. Record runtime feedback.
2. GPT-6 Luna/high (`runtime_mapping`): live log/package read-only verification, effective map-scale/UI/zoom research; scratch `runtime-mapping/`.
3. GPT-6 Luna/high (`control_reference_audit`): independent native city/road reference validity audit; scratch `control-audit/`.
4. Root: quantitative screenshot registration, common-cause model comparison and integration. Generate only a justified correction, with reproducible evidence and explicit runtime boundary.

## Acceptance Criteria

- R1 gameplay failure reports preserved; no claim that original issues are fixed.
- Actual loaded package and any priority/scale mismatch verified, or missing evidence identified precisely.
- A common transform/projection explanation tested against geographically separated examples and road geometry, beyond the same city centers used for fitting.
- A demonstrated correction implemented/verified if possible, otherwise a precise evidence-based conclusion and next discriminating check; no speculative replacement labeled fixed.
- Relevant tests, unchanged unrelated navigation behavior and meaningful local milestone commit.

## Verification

Research milestone complete; no verified replacement transform or practical geometry repair is claimed. Starting branch `codex/north-america-background`, clean HEAD `2831a84`. Eighteen unique screenshots are accessible through WSL; `160711` is supplied in two batches and retained once. Current game log explicitly mounts r1 after all other active mods. Further content/scale checks are delegated.

## Links

- [R1 handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R1.md)
- [R0/r1 earlier feedback](../../reference/NORTH_AMERICA_BACKGROUND_FEEDBACK_2026_10_24.md)

### Results

- Exact live r1 hash/priority confirmed; effective inspected map headers retain normal/city scales 20/3. No supporting 19/20 mismatch or relevant load error.
- SIFT atlas/screenshot registration plus independently extracted native road endpoints shows subpixel median endpoint-to-visible-road-mask distances in five well-supported SoCal/Gulf/Chicago/Canadian views. Native extraction: 90,401 regional road records plus expanded 109,194 records (overlapping regions, not unique whole-world coverage); each selected road has two linked endpoint nodes. Weak feature matches and zero-native-support row excluded.
- Geographic +3% enlargement around current canvas center improves SoCal endpoint/water diagnostic 15.23%→0.53%, but worsens southern Baja 8.36%→19.39% and northern Baja 4.23%→14.30%. Free-translation uniform, separate-axis and affine candidates still trade off withheld regions; full affine hits shear bounds. One-sided water coverage is not sufficient calibration truth.
- Reforma's climate LCC alternative worsens controlled reference checks (r0 2412→3210; dense comparison 1549→2681). Constant scale-factor differences are absorbable by the existing affine, so they do not establish a remaining global factor defect.
- Common workflow defect established: representative settlement/CityArea center equality and center pixels are insufficient acceptance tests for road/coast alignment. Dominant causal contribution of region/city distortion remains an evidence-supported hypothesis, not proof of every screenshot's exact cause. A replacement transform needs matching shore/road landmarks. Practical geometry and market usability remain unresolved.
- Direct old/new market map-content matching gives scale 1.1998, 244 inliers, RMS 0.84px. Different market interfaces/crops prevent causal isolation of the zoom setting; user-reported crowding remains valid.
- Root owns tracked diagnosis/integration. GPT-6 Luna/high `runtime_mapping` independently verified live resources, projection alternatives and the registration methodology/claim limits. GPT-6 Luna/high `control_reference_audit` audited city-control semantics and extracted bounded native road endpoints with provenance. All delegated file ownership was scratch-only. Root reviewed overlays and rejected unsupported rows/claims.
- Meaningful checks were the independent registrations, actual effective-sector parsing, controlled size/projection comparisons, source/hash checks and documentation link/diff checks. Production code and package bytes are unchanged; no irrelevant new unit tests or gameplay operation.

### Outcome

[Diagnosis](../../reference/NORTH_AMERICA_BACKGROUND_GEOMETRY_DIAGNOSIS_2026_10_24.md) provides a concrete common calibration/validation flaw, measured rejection of the simple tested alternatives, and the next discriminating repair inputs. [ADR-0027](../../architecture/decisions/ADR-0027-check-backgrounds-against-road-and-shore-geometry.md) prevents representative-point metrics from being treated as a repaired road/background fit. This closes the bounded investigation under its conclusion/next-evidence acceptance route, not the unresolved gameplay defects.
