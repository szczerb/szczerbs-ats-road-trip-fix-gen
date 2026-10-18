# Third-party tools and research sources

The Python package has no third-party runtime Python dependencies. HashFS inspection invokes an independently downloaded executable; that binary and its downloaded ZIP are ignored local artifacts, not part of this repository.

## sk-zk Extractor

- Project: [sk-zk/Extractor](https://github.com/sk-zk/Extractor).
- Tested release: [2026-07-29](https://github.com/sk-zk/Extractor/releases/tag/2026-07-29), Linux x64.
- License source: [upstream LICENSE](https://github.com/sk-zk/Extractor/blob/master/LICENSE), containing the GNU General Public License version 2 text. Consult upstream for complete terms and source.
- The wrapper launches the tool as a separate process. No Extractor source code or executable is copied into tracked project files.
- Observed download/executable hashes and the tested commands are in [the research baseline](docs/reference/RESEARCH_BASELINE.md) and [tooling guide](docs/reference/TOOLING.md).

## Binary-format research references

PPD and map-service research consulted the authors' implementations in [TruckLib.Models](https://github.com/sk-zk/TruckLib.Models), [TruckLib](https://github.com/sk-zk/TruckLib), and [TruckLib.Core](https://github.com/sk-zk/TruckLib.Core), plus [SCS Blender Tools](https://github.com/SCSSoftware/BlenderTools). The project implements bounded Python PPD inspection/transformation, map-field/graph transformations and a sequential map-907 structural reader after consulting those sources. No C# source files are versioned. This describes the implementation workflow; it is not a legal determination that all implementations are independent of upstream copyright. Earlier module/reference wording called `c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0` a commit; the saved GitHub API response actually identifies a **Git tree snapshot**. The publication review records that correction and the remaining commit/grant verification limit. Exact source links and applicability limits are recorded in [refueling findings](docs/reference/REFUELING_RESEARCH_FINDINGS.md) and the [starter-area guide](docs/reference/STARTER_AREA_SAMPLE.md).

## Publication and license review

Reviewed 2026-10-18. [Versioned-content review](docs/reference/PUBLIC_REPOSITORY_REVIEW.md), [license recommendation](docs/reference/OPEN_SOURCE_LICENSE_RECOMMENDATION.md), and [SCS mod publication terms](docs/reference/SCS_MOD_PUBLICATION_TERMS.md) distinguish generator code, local GPL research/tool copies, and generated game/map-resource overrides. Project-authored materials now use **AGPL-3.0-only** under [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md). These notices preserve the separate terms of referenced tools and materials; applying the project license does not relicense them. A different implementation language or an ignored upstream copy alone does not establish freedom from upstream obligations.

The saved reference trees identify TruckLib `c42dbe4f2d6bfb7b87c9ff1199c3cf5b7d1e27b0`, TruckLib.Models `6f09e0eb5c687202ffde0595e434675c455830e8` and TruckLib.Core `85e810f66a94e13b00a89ce3b149e0bcaa2dbfd4`. All list the same LICENSE blob `d159169d1050894d3ea3b98e1c965c4058208fe1`. These are Git tree/blob identities, not verified commit IDs or proof of an “or later” grant. Root compared Git blob hashes of the local C# research copies against those trees: 78 TruckLib, five Models and three Core local file instances match exactly; some are duplicate local copies. Ignored evidence: `local_outputs/work/2026-10-18_19-11-25/tree-provenance.json`. Historical source labels/links remain historical; use the corrected object types for future provenance work.

## Deeper implementation review

Follow-up 2026-10-18: the [complete map/parser audit](docs/reference/DEEP_MAP_PARSER_PROVENANCE_REVIEW.md) and [helper/all-module audit](docs/reference/DEEP_HELPER_PROVENANCE_REVIEW.md) compare original/current project code with exact historical C# sources. No obvious substantial translated routine was identified; format facts and a short token formula remain shared, and the process was source-guided rather than clean-room. The [integrated assessment](docs/reference/IMPLEMENTATION_INDEPENDENCE_ASSESSMENT.md) records the technical conclusion and legal limits. Nineteen additional historical blobs were downloaded and verified against the saved trees, including READMEs, license/project files and Token/Trigger sources. They establish the inspected GPLv2 baseline; an operative later-version grant was not found. The containing commit IDs remain unknown, without changing the exact file-byte evidence. The earlier MIT recommendation has been superseded by the maintainer's **AGPL-3.0-only** choice in [ADR-0016](docs/architecture/decisions/ADR-0016-license-project-under-agpl-v3.md), preserving the documented provenance limits. No protected upstream adaptation is relicensed by that choice.
