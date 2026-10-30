# Background branch: public-source review and rebase, 2026-10-30

**Subsequent authorized publication, 2026-10-30:** a fresh independent second review and all 692 tests pass. The reviewed source branch is pushed and [PR #2](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/pull/2) is OPEN/mergeable against master with automatic merge disabled. [TASK-0061](../tasks/done/TASK-0061-review-and-open-background-source-pr.md) records that later authorization and source-only publication. The preparation history below remains the evidence for that decision; private release artifacts remain excluded and r4 runtime confirmation is pending.

**Observed locally — source preparation verified, 2026-10-30:** the user authorizes branch-only history sanitation, a rebase onto current master, and public-source readiness work. No push, PR, release, visibility change, live installation or game/profile action is part of this task. This record concerns source, not approval to upload existing SCS/source ZIPs or private comparison evidence.

## Findings and remediation

- **History privacy — resolved:** six historical document blobs carried absolute host paths or a host-path placeholder. Branch-only rewriting replaces them with project-local evidence references and a repository-root instruction. Four documents differ at the original branch tip; no background implementation or calibration byte changes. All 19 development milestones and original author name/email/date are preserved. Full original history is recoverable from a verified ignored bundle.
- **Public documentation — resolved:** 71 background links advertised ignored local archives, source bundles, reports or screenshots as clickable targets. The eight references now state their local-only status and retain non-clickable repository-relative evidence identifiers and hashes. No private evidence is copied into Git or uploaded. Existing upstream local-artifact references are outside this branch's cleanup scope.
- **Integration — resolved:** upstream `c459b2addfb057e681a27245702a6f97c1827998` contains the separately developed station-parking/fueling/truck-rest work. Rebase conflicts retain both research tracks and preserve upstream station-catalog package data alongside optional background dependencies.
- **Identifier collisions — resolved:** master retains its published IDs. Background ADR-0028/0029 become ADR-0031/0032; background TASK-0051/0052/0054 become TASK-0057/0058/0059. Filenames, labels, dependencies and links follow those mappings. Historical source receipts retain their original commit identifiers as artifact provenance; the table below identifies the corresponding sanitized/rebased milestones.
- **Discovery/reproduction — resolved:** the root README and documentation index point to r4, and its guide documents fetching public geographic/font inputs, generating the exact r3 intermediate, then applying the existing surgical r4 repair. The recorded Python/render/font environment and hash guard remain explicit. Contributors use pytest with optional background dependencies; unittest alone does not collect the background tests.

## Source rights and output boundary

**Observed locally:** the outgoing source contains authored code/configuration, factual correspondence/provenance records, documentation and font/GSHHG notices. No screenshots, game/map resource payloads, downloaded tools or generated mods are added. No credential/private-key match was found by the bounded outgoing-history scan. A negative pattern scan is not a universal secret detector.

**Documented — retained notices:** project-authored material remains AGPL-3.0-only. GSHHG remains LGPL-3.0-or-later, Natural Earth/USGS sources retain their stated public-domain scope, and DejaVu retains its own notice. Full GPL/LGPL/font notice texts remain unchanged. Small source-derived factual GIS references retain their captured uncertainty, including the Seattle service's uncaptured explicit license statement; this review makes no blanket rights grant over external GIS responses or protected native artwork. The code was source-informed, not claimed clean-room.

**Unknown / pending:** r4's in-game restoration at all four world-map zoom levels is still awaiting the user. R3's known loading regression and remaining coast/lake alignment issues remain recorded. These limits do not block sharing accurately described experimental source, but they do prevent claiming a fully tested mod release. Existing ignored source ZIPs predate sanitation and are not cleared by the source-tree review; review/rebuild release artifacts separately before any later publication.

## Verification

- All 692 tests in the combined branch pass. Main, CLI-module and background help smoke checks pass.
- Wheel build/inspection includes all eight background modules, upstream `station_parking/reviewed_catalog.json`, and LICENSE/LICENSING/THIRD_PARTY_NOTICES. Build tools were provisioned only beneath the ignored verification run.
- Background source modules, map-sector changes, tests, JSON calibration inputs and the r4 recipe remain byte-identical to original tip `ed0c16e`; all license texts remain unchanged.
- Post-rebase reproduction of the original r4 correction matches SHA-256 `00e3932434dee49003fbf6f02da925f239939fd2997cbab78a54d5e305f013b4`. Existing 25 background delivery artifacts are protected by before/after fingerprints.
- Independent outgoing-history/content and pending-document scans find no host-path, secret-pattern or protected/binary-payload blocker. Task/ADR IDs are unique, all 1575 checked non-artifact local documentation targets resolve, and all 25 pre-existing background artifact hashes match. Other local branch/ref identities are unchanged, apart from the authorized branch and origin/master tracking update.

Local-only verification identifiers: `local_outputs/work/2026-10-30_18-27-01/public-prep/`, including `before-public-prep.bundle`, `original-background-artifacts.json`, `sanitized-commit-map.json`, `final-development-commit-map.json`, `validation/`, `docs-cleanup/` and final audit reports. These are excluded from public source. Actual delegated work uses GPT-6 Luna/medium for complete tests/package checks, the bounded eight-reference cleanup and independent publication verification; main performs/reviews history integration and final evidence.

## Development commit mapping

These are source-history fingerprints, not public download or commit links. Original archived artifact hashes are unchanged. Public upstream commits and other local branch histories were not rewritten.

| Original milestone | Sanitized/rebased milestone | Subject |
| --- | --- | --- |
| `53ff7b3` | `de66221` | Generate an original standalone ATS North America background |
| `099510f` | `22b51fc` | Record verified background source bundle and manual-test handoff |
| `f02c313` | `2c7ab51` | Correct regional background shorelines and shared job-market zoom |
| `2831a84` | `196dfa7` | Record exact r1 source-bundle reproduction and testing handoff |
| `12c2a14` | `69ea173` | Diagnose background calibration failure against runtime road geometry |
| `3e284fd` | `3b84ad2` | Read native road visibility flags correctly and support bounded calibration fields |
| `18e5f13` | `ad86346` | Calibrate r2 background with road geometry and physical ground constraints |
| `f3bfec5` | `57d75fb` | Record verified r2 delivery and exact corresponding-source rebuild |
| `003abd0` | `2e1aac5` | Record working r2 market zoom and prepare a stricter shoreline repair goal |
| `6c5ce73` | `a9074b4` | Add staged feature calibration and detailed shoreline rendering |
| `a0dfbe3` | `9a1b0d6` | Guard narrow shoreline features before raster classification |
| `5f6546c` | `5ceff4f` | Transport regional features without shrinking their source geometry |
| `85c2b6c` | `5c3f5f6` | Check accumulated background deformation outside landmark regions |
| `941056a` | `17f7213` | Record complete deformation checks and rejected shoreline drafts |
| `2536ce7` | `515f0c0` | Resolve ferry activation links and bound dense regional audits |
| `bd613b7` | `2b05d9e` | Calibrate r3 shores with bounded regional ground corrections |
| `5e1de7a` | `3ca1f06` | Document verified r3 shoreline repair and authoritative testing package |
| `868ec03` | `36e6a47` | Diagnose r3 detailed-background loss as oversized loading requests |
| `ed0c16e` | `1451931` | Restore working detailed texture sizes without changing r3 cartography |

## Readiness decision

**Ready for a later push of this reviewed branch and a PR as experimental source.** No concrete source-publication blocker remains in the bounded review. Retain the documented source/GIS provenance limits and pending r4 runtime status in the PR description. This judgment does not clear existing private SCS/source ZIPs, screenshots or other release artifacts for publication. At the end of that preparation stage the branch was not pushed and no PR or release had been created. The subsequent authorized source push/PR is recorded above; no mod release was created.

[Task](../tasks/done/TASK-0060-rebase-background-and-prepare-public-source-pr.md), [r4 reproduction](../examples/north-america-background/r4/README.md), [r4 runtime boundary](NORTH_AMERICA_BACKGROUND_1_61_R4.md), [portable evidence policy](../architecture/decisions/ADR-0030-use-portable-reviewed-evidence-and-versioned-paths.md).
