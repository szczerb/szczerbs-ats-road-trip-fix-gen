# Portable station-parking evidence

## Input contract

**Observed locally — ATS 1.61.3.18, reviewed 2026-10-24; portability checked 2026-10-30:** `station_bays` uses four reviewed effective station model families. Their binaries come from **Real Companies 4.02.01**, Workshop item `2316796205/latest`, with material dependencies resolved against the installed ATS `base.scs` and `base_share.scs`. Stock models alone do not reproduce these fingerprints. A newer game/mod/tool version requires a separate review; the generator does not relax the pins.

Every single-map `generate-map-fix` / `analyze-map` invocation selecting `--parking-strategy station_bays`, and every realistic `generate-map-stack` / `analyze-map-stack` invocation, requires **`--station-evidence-dir DIR`**. `DIR` is a private flat directory containing exactly the required named `.pim` and `.pit` files (additional receipt files are harmless). No historical ignored output directory is searched. Missing files or a wrong mesh/state hash fail before a public workflow mounts the original packages or creates its run directory. Broad/truck-area parking and fuel-only workflows need no station evidence.

The project-authored [review metadata](../../src/ats_road_trip/station_parking/reviewed_catalog.json) is versioned and included in Python distributions. It records all four families, including the previously local-only GP material classifications; exact PMD/PMG/PIM/PIT and material-resource pins; permitted methods; converter identity; and both exact accepted Dawson areas. This file contains metadata and project-authored policy, with no game mesh, material, binary, or converted asset. The Dawson override retains its original Alaska archive/sector and original base descriptor guards; historical effective-overlay sector/descriptor hashes never replace those original guards.

## Reproduce from owned original resources

Use the separate external [ConverterPIX](https://github.com/mwl4/ConverterPIX) executable built from revision `3cd4e73a86d0c6bd28e117664c50a36cabeccf38` (LGPL-3.0). The reviewed Linux binary SHA-256 is `fba5a52f763d07d3dc110dea4980fe2c7e656a8c0afa05b6b7a4ab4373dc950d`. No converter executable or source is bundled with this repository. No Blender session is needed.

Set `ATS_GAME_DIR` to your installed ATS 1.61.3.18 directory, `REAL_COMPANIES_DIR` to your installed original Real Companies 4.02.01 `latest` directory, and `CONVERTER_PIX` to the separate executable. Run this Bash recipe from the repository root; all newly created conversion files stay in a fresh ignored run. The converter reads original installed resources and exports only the four selected models and their required dependencies. Its base arguments deliberately list Real Companies first, as in the reviewed conversion; they are **converter lookup order**, independent of the generator's low-to-high game/map package order.

```bash
set -euo pipefail
: "${ATS_GAME_DIR:?Set the installed ATS directory}"
: "${REAL_COMPANIES_DIR:?Set the installed original Real Companies 4.02.01 latest directory}"
: "${CONVERTER_PIX:?Set the separate reviewed converter executable}"
export CONVERTER_PIX
python3 - <<'CHECK'
import hashlib, os
from pathlib import Path
actual = hashlib.sha256(Path(os.environ['CONVERTER_PIX']).read_bytes()).hexdigest()
expected = 'fba5a52f763d07d3dc110dea4980fe2c7e656a8c0afa05b6b7a4ab4373dc950d'
if actual != expected:
    raise SystemExit('ConverterPIX executable SHA-256 drift; stop and review the tool')
CHECK

RUN_ID=$(TZ=Europe/Warsaw date +%Y-%m-%d_%H-%M-%S)
WORK="local_outputs/work/$RUN_ID/station-evidence-preparation"
mkdir -p "local_outputs/work/$RUN_ID"
mkdir "$WORK"
for family in nm_gas_station1_chemron nm_truckstop1_chemron \
              nm_gas_station2-corner_chemron nm_gas_station2-corner_gp
do
  "$CONVERTER_PIX" \
    -b "$REAL_COMPANIES_DIR" \
    -b "$ATS_GAME_DIR/base.scs" \
    -b "$ATS_GAME_DIR/base_share.scs" \
    -e "$WORK/converted/$family" \
    -m "/prefab/gas/$family" > "$WORK/$family-conversion.log" 2>&1 || exit 1
done

PYTHONPATH=src python3 -m ats_road_trip.station_parking.evidence \
  --converted-dir "$WORK/converted" \
  --output "$WORK/station-evidence"
STATION_EVIDENCE_DIR="$WORK/station-evidence"
```

The preparation helper recursively finds only the eight named PIM/PIT inputs in explicitly supplied conversion directories, verifies every candidate, preserves their original bytes, and writes a new flat evidence directory plus `preparation.json`. It never overwrites an existing destination, rewrites review metadata, runs a converter, or installs a mod. Missing files and any mismatched duplicate conversion abort before creating the destination. You can import several existing conversion runs instead by repeating `--converted-dir`; this is also the supported migration from retained private conversions. No particular old run path is required.

The receipt records original file locations, raw byte hashes, the normalized UTF-8 text hashes used by the existing catalog contract, metadata hash, and the reviewed converter identity. It records an expected converter identity rather than attesting which program produced preexisting files; output fingerprints are the acceptance gate. PMD/PMG and material bytes are checked separately against the mounted effective original game/map/resource stack during planning. Preparation itself does not certify source resources or runtime behavior. Keep both conversions and evidence private unless you independently hold redistribution rights.

## Use the prepared directory

Examples below assume the setup above and an installed project CLI (or invoke `PYTHONPATH=src python3 -m ats_road_trip.cli`). Supply the full explicit original stack in the established low-to-high order; the illustrative single package below does not replace required map/resource companions.

```bash
ats-road-trip analyze-map-stack \
  --preset realistic --game-dir "$ATS_GAME_DIR" \
  --station-evidence-dir "$STATION_EVIDENCE_DIR" \
  --package local_inputs/your-original-map.scs

ats-road-trip analyze-map local_inputs/your-original-map.scs \
  --map-name 'Your Map' --game-dir "$ATS_GAME_DIR" \
  --processor rest --parking-strategy station_bays \
  --station-evidence-dir "$STATION_EVIDENCE_DIR"
```

`generate-map-stack` and `generate-map-fix` accept the same evidence option and require the existing `--experimental` acknowledgement. Evidence location is carried in `ProcessorConfig`, workflow audits, stack summaries, and station planning reports. Reproduction requires the same original resources and reviewed files, not the original machine's directory names. The files remain generation inputs and are never included as gameplay resources in generated mods.

For API callers, pass `station_evidence_dir` to `ProcessorConfig`, `run_map_stack`, `generate_map_fix`, `analyze_map`, or `plan_map_station_parking`. An explicitly supplied authored `catalog` remains available to isolated planner fixtures; it does not cause public workflows to discover private files implicitly.

## Reviewed model/state fingerprints

**Observed locally — ATS 1.61.3.18 / Real Companies 4.02.01, inspected 2026-10-19 and retained at the 2026-10-24 review:** the following pins are preserved, with material-resource hashes and classifications in the versioned metadata. PIM/PIT comparisons use UTF-8 text after optional BOM removal and newline normalization, matching the preexisting loader. Original PMD/PMG and material pins remain raw byte hashes.

| Family | Resource | SHA-256 |
| --- | --- | --- |
| `nm_gas_station1_chemron` | PMD | `f34965d3613eaac120256cf04fcbefb48aeff3924e0b098c513fb5c4d8f95301` |
| `nm_gas_station1_chemron` | PMG | `c9874060404d200024e158c86399e30ed191ddf8364bab478a88da0f5d6f6526` |
| `nm_gas_station1_chemron` | PIM | `68011614086e4e78505d3ab3849f416b29e7b26cf2eaf93cb84e426226429644` |
| `nm_gas_station1_chemron` | PIT | `98d12127c619f7796b839f544145e580157a678bd217145e6e94e260e6c2401d` |
| `nm_truckstop1_chemron` | PMD | `8128199e3eccb67b5843c48524aa01d9ae1d95583e9127c2a9f695962b550061` |
| `nm_truckstop1_chemron` | PMG | `1178ad1c0c8378d60261278e74bf52514d395479790bc711ddd5bc7843b3bf7c` |
| `nm_truckstop1_chemron` | PIM | `4d9d4e11353d5aebaafc9eef3e650f56bd3ccdd51b33b399fdfdb4a1bc25fbaa` |
| `nm_truckstop1_chemron` | PIT | `9636530d37cac78b3109909ccd7af50ba034f59adde0f1276cf9e7edfea5e220` |
| `nm_gas_station2-corner_chemron` | PMD | `a472b46db2911373b806b6aad7d037d68f80b67e3f567ceea74a731a753d4b28` |
| `nm_gas_station2-corner_chemron` | PMG | `04cfa38be260b82dc5b26ff146ffccdfd1e4b20a3b3ff7e87a72e0d15eaa4008` |
| `nm_gas_station2-corner_chemron` | PIM | `0e4b6f9c40a0ba3bbb7f1c4c4e7dab584aa721f669f9aa0497e7687fa34b03e8` |
| `nm_gas_station2-corner_chemron` | PIT | `6fd85033d31a16e207b49809a3448d253fb74a7ce748efe197792b8229762db8` |
| `nm_gas_station2-corner_gp` | PMD | `2a8d37fa45d33a87284ec29b36c7303ad0b55c1c5c4b9f9515bf739b6eaff294` |
| `nm_gas_station2-corner_gp` | PMG | `39d1d65208af5d676887a4ae7f06ec8eb35bb74d47793190a8630aa4a266a648` |
| `nm_gas_station2-corner_gp` | PIM | `3088fd090938ad4971540da99d7636de46aca64fe36dcc7779ab0e3e5a0abc02` |
| `nm_gas_station2-corner_gp` | PIT | `4db3aaee046f13b908649362171849ec0cce54da541b145a60e5c36a8e4e8ff8` |

**Observed locally — portability verification, 2026-10-30:** importing the retained reviewed conversions into a new explicit directory verified all eight PIM/PIT identities. The loaded family catalog, including every source/material/state guard and both exact Dawson areas, matched the former loader in every semantic field; only evidence file locations changed. Authored-fixture tests cover missing inputs, mesh/state drift, ambiguous conversions, independent paths, CLI forwarding, and early failure. This check imported existing conversions; it did not perform a fresh conversion from the currently installed game/mod resources or establish in-game parking results.
