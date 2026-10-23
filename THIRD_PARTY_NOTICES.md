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

## ConverterPIX station-model research

[ConverterPIX](https://github.com/mwl4/ConverterPIX) was invoked as a separate process to convert individually selected installed ATS models into PIM/PIT/PIP research artifacts. Inspected source commit: `3cd4e73a86d0c6bd28e117664c50a36cabeccf38`; bundled Linux executable SHA-256: `fba5a52f763d07d3dc110dea4980fe2c7e656a8c0afa05b6b7a4ab4373dc950d`. Its [upstream license](https://github.com/mwl4/ConverterPIX/blob/3cd4e73a86d0c6bd28e117664c50a36cabeccf38/LICENSE) is LGPL-3.0. No converter code or executable is included in the Python distribution. The new project reader parses the observed text format and does not implement PMG conversion. Converted game meshes remain ignored local artifacts with separate rights.

The station-map reader extends existing PPD research using the 48-byte MapPoint record layout, the [TruckLib.Models MapPoint source](https://github.com/sk-zk/TruckLib.Models/blob/master/TruckLib.Models/Ppd/MapPoint.cs), [SCS Blender Tools flag constants](https://github.com/SCSSoftware/BlenderTools/blob/master/addon/io_scs_tools/consts.py), and [official locator documentation](https://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools/Locators/Prefab_Locators). These sources were consulted for format facts and authoring semantics; existing upstream provenance and license limits above still apply. New geometry algorithms and text parsing were authored for this experiment, not copied from converter or Blender routines. The earlier implementation-independence assessment predates these new modules and is not an audit of them. See [TASK-0039 research](docs/reference/GAS_STATION_CAR_REST_RESEARCH.md).

## Navigation overlay source dependency

The source-pinned N2 navigation generator transforms North America Background Map 5.3 by CairamR (installed author CAIRAM), Steam Workshop item 3348711188. Local generated N2 archives contain one complete modified background definition; the three SUI includes and background artwork remain supplied by the original mod. This project's AGPL does not relicense that definition. No redistribution grant was found in the inspected author listing/installed package; [scope, sources and publication boundary](docs/reference/NAVIGATION_ICONS_PUBLICATION.md) record the evidence and limits. The source definition itself is not tracked.

## Original geographic background inputs (2026-10-23)

The optional background generator uses Natural Earth vectors, expressly public domain under [Natural Earth's terms](https://www.naturalearthdata.com/about/terms-of-use/). Dataset-specific versions, download URLs and SHA-256 pins are in [sources.json](docs/examples/north-america-background/sources.json); downloaded archives are ignored. The renderer does not use or trace any third-party background image.

DejaVu Sans Book 2.37 from Debian fonts-dejavu-core 2.37-8 is a separately licensed font input. The exact archive/member pins are in [font.json](docs/examples/north-america-background/font.json); the [Bitstream Vera notice](assets/background-map/FONT-LICENSE.txt) accompanies rendered artwork. DejaVu changes are public domain. No font binary is committed or bundled in the mod.

Optional Python build libraries (not bundled in the mod): Pillow (HPND), NumPy and SciPy (BSD-3-Clause), PyShp (MIT), and pyproj (MIT; its PROJ dependency has its own permissive notices). Pinned versions are in the background requirements file; installed distributions retain their license files. The build uses these as libraries, without copying their sources into project code. The SCS shader and stock UI remain supplied by the game; functional format/field observations do not convey rights in its artwork.
