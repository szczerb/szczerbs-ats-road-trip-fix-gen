# Third-party tools and research sources

The Python package has no third-party runtime Python dependencies. HashFS inspection invokes an independently downloaded executable; that binary and its downloaded ZIP are ignored local artifacts, not part of this repository.

## sk-zk Extractor

- Project: [sk-zk/Extractor](https://github.com/sk-zk/Extractor).
- Tested release: [2026-07-29](https://github.com/sk-zk/Extractor/releases/tag/2026-07-29), Linux x64.
- License source: [upstream LICENSE](https://github.com/sk-zk/Extractor/blob/master/LICENSE), containing the GNU General Public License version 2 text. Consult upstream for complete terms and source.
- The wrapper launches the tool as a separate process. No Extractor source code or executable is copied into tracked project files.
- Observed download/executable hashes and the tested commands are in [the research baseline](docs/reference/RESEARCH_BASELINE.md) and [tooling guide](docs/reference/TOOLING.md).

## Binary-format research references

PPD and map-service research consulted the authors' implementations in [TruckLib.Models](https://github.com/sk-zk/TruckLib.Models), [TruckLib](https://github.com/sk-zk/TruckLib), and [TruckLib.Core](https://github.com/sk-zk/TruckLib.Core), plus [SCS Blender Tools](https://github.com/SCSSoftware/BlenderTools). The project contains bounded, independently written PPD inspection/transformation and map-field/graph transformations and a sequential map-907 structural reader, not a vendored copy of those libraries. The map-wide reader uses the inspected TruckLib commit recorded in its module and [generator reference](docs/reference/MAP_WIDE_FUEL_GENERATOR.md). Exact source links and applicability limits are recorded in [refueling findings](docs/reference/REFUELING_RESEARCH_FINDINGS.md) and the [starter-area guide](docs/reference/STARTER_AREA_SAMPLE.md).
