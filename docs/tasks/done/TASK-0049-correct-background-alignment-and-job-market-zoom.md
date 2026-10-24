---
id: TASK-0049
title: Correct background alignment and job-market zoom from r0 gameplay feedback
status: done
priority: high
repositories: [.]
depends_on: [TASK-0048]
owner: shared
---

## Goal

Investigate and correct the reported r0 geographic placement and fixed job-market zoom issues, preserve the accepted visual style/navigation visibility, and deliver a verified experimental revision or a precise external blocker.

## Context

**Documented — user feedback, 2026-10-24:** background generally works and its appearance is liked; extra world-map zoom-out is appreciated; truck navigation looks fine. A short car-mode check confirms both refueling and parking icons visible in car navigation. Job-market maps (quick/freight/external) are too zoomed out and lack user zoom controls. User prefers an independent ~20% zoom-in, prioritizing city selection over extra world-map zoom if inseparable. Mobridge, South Dakota appears in a lake; other cities lie over ocean/lake water and a northern port appears too far inland. Screenshots accompany these reports. No completed refueling/rest transaction is inferred.

The user asked to collect feedback without investigation until explicitly finished; that boundary ended with their final testing message. They now authorize investigating the issues and continuing without a new prompt. No game launch, live installation/profile edits, push or publication.

## Scope

Review all supplied screenshots, compare actual effective game geometry with the original geographic inputs, separate projection/global calibration and local map distortions, improve the backdrop without modifying playable map resources, and investigate a separate job-market zoom setting. Preserve r0 artifacts and original input files. Attribute runtime reports to the user.

## Implementation Plan

1. Preserve 43 supplied screenshot files and hashes under the current ignored run; record positive results and remaining defects.
2. Delegate stock UI/job-market zoom research to GPT-6 Luna/high (scratch ownership `job-market-investigation`); screenshot location/offset review to GPT-6 Luna/medium (`screenshot-review`). Main agent owns integration and alignment; a later bounded delegate owns version-aware resources/tests, and then the r1 reproduction README. City census/official-reference extraction is delegated read-only to GPT-6 Luna/high.
3. Quantify the screenshot issues against original vectors/effective map references and select a justified correction with independent checks.
4. Implement/reproduce one new experimental revision, inspect comparative previews and audits, update evidence/handoff, and commit verified milestones locally.

## Acceptance Criteria

- All user feedback retained with exact reported scope; screenshots accessible/reviewed without requiring reuploads if WSL mapping works.
- Evidence-based job-market zoom adjustment near the requested 20%; world-map maximum retained if independent configuration is possible, otherwise tradeoff documented.
- Geographic corrections measured at reported locations; no concealed local data edits or claims of exact all-world alignment.
- Accepted car fuel/rest masks, unrelated icon/route behavior, palette, and standalone/no-Ford/no-sector scope retained.
- Automated checks, reproducibility and original-r0 reproduction pass, with a clear manual-test handoff or exact major blocker.

## Verification

Implementation, offline checks and corresponding-source bundle reproduction pass. R1 is ready for the user’s next manual trial; explicit residual/source-data limitations remain in the handoff. Clean starting branch `codex/north-america-background`, HEAD `099510f`. Work run: `local_outputs/work/2026-10-24_02-39-28/`, Europe/Warsaw. Original Windows screenshot paths resolve read-only as `local_outputs/work/2026-10-24_02-39-28/user-evidence/`; attachment errors did not mean the underlying files were absent.

### Execution and results

- GPT-6 Luna/high: job-market resource research, version-aware packaging/tests and bounded integration review; later r1 README. GPT-6 Luna/medium: all coast/border screenshot review, source land/water comparisons, independent archive/raster/preview review. GPT-6 Luna/high: complete effective CityArea/city-definition census, conservative joins and primary CGNDB/GNIS retrieval. Each had explicit scratch or file ownership; root reviewed and integrated findings.
- All 43 screenshots recovered through WSL and hash-preserved. Complete census: 3,474 effective sectors, 2,910 CityAreas, 610 tokens, zero parse failures. 269 conservative Natural Earth city matches; 288 total evaluation references after retained/official additions.
- Selected compact correction retains the exact r0 affine outside local disks. 26 controls / 24 exact; Surrey/Nimpkish softened, Split Lake excluded because its official point is within the source lake. Regional RMS 1373→504; 229 excluded references slightly regress 1571→1605. No concealed whole-world accuracy claim. New source detail fixes the factual Mobridge water-containment defect; all 26 selected center pixels are land/shoreline, with whole-road coverage explicitly unproven.
- Shared zoom tier 7 lowered 120000→100000, reflecting user priority. No independent exposed market setting found; all other map-data bytes/fields match r0. Accepted palette, bounds, image sizes, masks and standalone scope preserved.
- 295 tests pass (`OPENBLAS_NUM_THREADS=1 PYTHONPATH=src:. <recorded-venv>/bin/python -m pytest -q`). Missing repository root on PYTHONPATH initially caused collection errors; corrected invocation passes. 174,436 deformation samples have no folds. Resource audit/CRC/encoded quadrant checks pass. Original r0 archive reproduces byte-identically with revised code.
- Authoritative r1: `local_outputs/generated/2026-10-24_03-10-27/`, SHA `a10d9abcf32d9f469a819292c56e012919759775d48492dbf51ca6fd31e88033`. Repeated final builds match. Earlier manually chosen development timestamp labels were ahead of the clock; canonical build uses generator's actual Europe/Warsaw clock. Earlier outputs retained and marked superseded/reproduction-only.
- Independent review confirms 15 selected centers use land fill and 11 use coastline pixels; nearby water can remain. Split Lake center remains water and is a documented source/reference limitation. All five final DDS payloads and previews match the independently reviewed candidate; final rebuild changes only exact OGL attribution typography. No runtime result inferred.

## Links

- [R0 handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R0.md)
- [Original engine/calibration research](../../reference/NORTH_AMERICA_BACKGROUND_RESEARCH.md)
- [Current state](../../project/CURRENT_STATE.md)

- [R1 handoff](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R1.md)
- [Regional-correction ADR](../../architecture/decisions/ADR-0026-bound-regional-background-corrections.md)

**Final source verification:** source commit `f02c313`, source ZIP SHA `fb8a4d1eb7ed627c965413bb1d79cd44e87dfc4d808ae7811f177695a111a084`. Rebuild from its extracted tree produced SCS SHA `a10d9abcf32d9f469a819292c56e012919759775d48492dbf51ca6fd31e88033`. This completes the experimental revision handoff, without claiming all reported runtime issues fixed.
