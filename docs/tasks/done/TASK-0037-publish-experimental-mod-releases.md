---
id: TASK-0037
title: Publish the first experimental job and tank releases
status: done
priority: high
repositories: [.]
depends_on: [TASK-0036]
owner: shared
---

# Goal

Publish the prepared Job Types Compat Mustang r3 and reasonable gas tank upgrades r0 as separate downloadable GitHub prereleases.

# Context

**Documented — maintainer instruction and first-hand gameplay report, 2026-10-18:** the maintainer manually installed the updated packages, launched the game and reported that they work. This does not establish itemized billing, individual completed deliveries or every compatibility scenario. The maintainer approved pushing documentation commit `2845566`, targeting both release tags at that commit, uploading the two prepared assets, and pushing final publication documentation.

Public release notes describe features, requirements, installation and testing. They omit unrelated job add-ons, internal packaging details and deleted releases. Tank capacities include approximate US liquid gallons rounded to one decimal place.

# Scope

Two prereleases, one existing `.scs` asset each, unchanged archive bytes and mod revisions. Normal master pushes and fixed release tags are authorized. No generator/runtime changes, original artifact edits, settings changes, history rewrite or game launch.

# Implementation Plan

1. Recheck checkout, remote state, release/tag names and asset identities.
2. Push approved commit `2845566`; create drafts targeting its full SHA.
3. Verify uploaded assets and approved notes, then publish both as prereleases without Latest.
4. Independently verify public metadata, tag targets and download links.
5. Record publication and the user report, then commit/push documentation without moving release tags.

# Acceptance Criteria

- Both approved tags point to `2845566dc7d3b8ad1c3ba53b7ec137f5d42fce2d`.
- Both releases are published prereleases, with their approved titles/notes and exactly one correct `.scs` asset each.
- Remote asset SHA-256 values equal the prepared local copies; US-gallon conversions are correct.
- Gameplay confirmation is attributed to the maintainer without adding unreported test outcomes.
- Final documentation is pushed and checkout is clean; tags remain fixed.

# Verification

**Observed — authenticated GitHub CLI and independent public downloads, 2026-10-18:** both releases were created as drafts, their asset digests verified, and then published as prereleases without Latest. Both tags are direct commit refs at the exact approved SHA. Each release has one expected `.scs` asset. Public titles/bodies match the approved text, including US-gallon conversions and SHA-256; unrelated add-ons and internal packaging details are absent from the release notes.

| Release | Asset bytes | SHA-256 |
| --- | ---: | --- |
| [Job Types Compat Mustang r3](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases/tag/job-types-compat-mustang-1.61-r3-experimental) | 122472 | `473467135df149f457c1832ae20040c333bc8eacd69e89da159ab127796b71af` |
| [Reasonable gas tank upgrades r0](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases/tag/reasonable-gas-tank-upgrades-1.61-r0-experimental) | 39344 | `14b6dfc1f393076337bb29c29967b53b468660052c5ae32b8009ebd0471daab1` |

Root owned all GitHub mutations and integration. GPT-6 Luna/low independently checked the notes, then made fresh API requests and downloaded both public assets: sizes and SHA-256 match the plan, expected tag targets match, and `/releases/latest` returns the expected 404 for prereleases. No findings remained. The gameplay report is recorded with its limits in [validation results](../../reference/VALIDATION_RESULTS.md#2026-10-18-updated-job-and-tank-packages-work-in-game).

Detailed approved notes, CLI snapshots, publication script and `independent-review.json` remain ignored under `local_outputs/work/2026-10-18_23-11-13/`. Source generators, tests, licenses/notices and prepared archive bytes are unchanged; runtime tests were not rerun for publication/documentation work. README points directly to both verified releases. Final documentation is committed/pushed separately; release tags remain on the prepared-package commit.

# Links

- [Prepared packages and fingerprints](TASK-0036-prepare-report-free-publication-packages.md)
- [Current state](../../project/CURRENT_STATE.md)
- [Gameplay evidence](../../reference/VALIDATION_RESULTS.md)
- [GitHub Releases](https://github.com/szczerb/szczerbs-ats-road-trip-fix-gen/releases)
