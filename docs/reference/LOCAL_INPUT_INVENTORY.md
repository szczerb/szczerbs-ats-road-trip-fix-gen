# Local Input Inventory

Observation date: 2026-10-17. Evidence label: **Observed locally** for the metadata, tables, and selected paths below; uninspected contents are **Unknown**.

This inventory records metadata visible from the local protected input files on the observation date. It does not establish game compatibility, explain a defect, or prove that a named definition is absent. Archive filenames and the presence or absence of specific names are not evidence of a root cause. Inputs under `local_inputs/` are ignored by Git; the inventory records observations without copying archive assets into the repository.

## Archive overview

Human sizes below use binary units (MiB/GiB); byte counts are exact filesystem sizes observed locally.

| Exact filename | Bytes | Human size | Header / observed archive type | Manifest and compatibility text |
|---|---:|---:|---|---|
| `ATS_Expansion_v23.0_1.61.scs` | 1,598,589,452 | 1,524.53 MiB (1.49 GiB) | Starts `PK\x03\x04`; readable as ZIP | `manifest.sii`: package version `23.0`, display name `ATS Expansion v23.0`, author `Sineptorro, Driver47`, category `map`; declares `compatible_versions[]: "1.61.*"`. The filename includes `1.61`. |
| `Alaska_Expansion_v1.2.3.scs` | 676,950 | 0.65 MiB | Starts `PK\x03\x04`; readable as ZIP | `manifest.sii`: package version `1.2.3`, display name `Alaska Expansion v1.2.3`, author `JacobKazias`, category `map`; the `compatible_versions[]: "1.61.*"` line is commented out, followed by a comment saying compatible with ATS 1.61.x. Filename gives map-package version `1.2.3`, not an ATS version. |
| `Reforma_3_0_1_161.scs` | 371,796,014 | 354.57 MiB | Starts `SCS#\x02\x00\x00\x00`; SCS# v2 HashFS signature, not ZIP | Manifest and contents were not inspected. Filename text is recorded as-is; it is not treated as verified compatibility metadata. |
| `Reforma_MegaResources_v3_0_1_161.scs` | 660,653,538 | 630.05 MiB | Starts `SCS#\x02\x00\x00\x00`; SCS# v2 HashFS signature, not ZIP | Manifest and contents were not inspected. Filename text is recorded as-is; it is not treated as verified compatibility metadata. |
| `Western_Canada_Expansion_v1.7.3.scs` | 45,689,120 | 43.57 MiB | Starts `PK\x03\x04`; readable as ZIP | `manifest.sii`: package version `1.7.3`, display name `Western Canada Expansion v1.7.3`, author `JacobKazias`, category `map`; the `compatible_versions[]: "1.61.*"` line is commented out, followed by a comment saying compatible with ATS 1.61.x. Filename gives map-package version `1.7.3`, not an ATS version. |

For the three ZIP-readable archives, central-directory compression method counts (ZIP method number) were:

| Archive | Stored (0) | Deflate (8) | Central-directory entries |
|---|---:|---:|---:|
| ATS Expansion | 3,488 | 18,508 | 21,996 |
| Alaska Expansion | 87 | 992 | 1,079 |
| Western Canada Expansion | 362 | 4,502 | 4,864 |

The ZIP inspection did not run an archive-wide CRC test. It read only selected small manifest and definition members for the summaries below.

### Declared DLC dependencies

**Observed locally:** the three ZIP manifests declare the same map DLC token set (ordering differs): `dlc_arizona`, `dlc_nevada`, `dlc_nm`, `dlc_co`, `dlc_wa`, `dlc_id`, `dlc_ut`, `dlc_wy`, `dlc_or`, `dlc_mt`, `dlc_tx`, `dlc_ok`, `dlc_ks`, `dlc_ne`, `dlc_ar`, `dlc_mo`, `dlc_ia`, `dlc_il`, and `dlc_la`. ATS Expansion additionally declares `dlc_volvo_construction` and `dlc_heavy_cargo`. These are the exact manifest strings, not a verified list of installed/owned packages. Reforma dependency metadata remains unknown.

## Selected visible structure

These are representative observations from small text definitions and paths, not exhaustive semantic analyses.

- **ATS Expansion:** The archive uses `base/def/company/...` and `base/map/usa/sec±XXXX±YYYY.{aux,base,data,desc,layer}` paths. A representative company editor definition is `base/def/company/03cust/editor/havre.sii`, whose small text declares `company_def : .havre`, city `havre`, prefab `d_cust_3`. A representative incoming cargo definition is `base/def/company/03cust/in/auger_wag.dlc_farm_machinery.sii`, declaring `cargo_def : .auger_wag` and cargo unit `cargo.auger_wag`. The central directory lists 1,350 sector files (270 sector coordinate stems with five listed extensions each).
- **Alaska Expansion:** The archive has root-level `def/company/...` and `map/usa/sec±XXXX±YYYY.{aux,base,data,desc,layer}` paths. A representative company definition, `def/company/18w_trl_svc/editor/kcoldfoot.sii`, declares city `kcoldfoot` and prefab `d_trl_svc`. The map directory also contains map UI assets, so its broad `map` path count is not a sector count. The central directory lists 820 sector files (164 coordinate stems with five listed extensions each).
- **Western Canada Expansion:** The archive has root-level `def/company/...` and `map/usa/sec±XXXX±YYYY.{aux,base,data,desc,layer}` paths. A representative company definition, `def/company/18w_trl_svc/editor/kmoosomin.sii`, declares city `kmoosomin` and prefab `d_trl_svc`. A representative incoming cargo definition, `def/company/du_farm/in/bottles.sii`, declares `cargo_def : .bottles` and cargo unit `cargo.bottles`. The central directory lists 2,380 sector files (476 coordinate stems with five listed extensions each).
- **Reforma and Reforma Mega Resources:** The first 16 bytes identify SCS# v2 HashFS. No manifest, company/cargo definition, or map-sector layout was read. A suitable HashFS extractor was unavailable on `PATH` during this inspection. Their internal contents remain unknown in this inventory.

The `base/` prefix in ATS Expansion and root-level `def/` and `map/` in Alaska and Western Canada describe the observed ZIP member paths only. No compatibility or load-order conclusion follows from those layouts alone.

## Reproducible read-only inspection

The following standard-library Python example prints file size and the first eight header bytes, then summarizes ZIP metadata without extracting members, computing full-file hashes, or scanning member CRCs. Run it from the repository root. It intentionally treats non-ZIP SCS archives as uninspected. For text samples, first inspect `ZipInfo.file_size`, then explicitly select a tiny member with `ZipFile.read(name)`; that decompresses only that member and is not a full archive validation.

```python
from pathlib import Path
from collections import Counter
import zipfile

for path in sorted(Path("local_inputs").glob("*.scs")):
    with path.open("rb") as stream:
        header = stream.read(8)
    print(path.name, path.stat().st_size, header)
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            print("entries", len(entries))
            print("compression methods", dict(Counter(i.compress_type for i in entries)))
            print("first paths", [i.filename for i in entries[:5]])
    except zipfile.BadZipFile:
        print("not readable as ZIP; no extraction attempted")
```

## Related references

- [SCS archives and definitions](SCS_ARCHIVES_AND_DEFINITIONS.md)
- [Map structure and compatibility](MAP_STRUCTURE_AND_COMPATIBILITY.md)
- [Project current state](../project/CURRENT_STATE.md)
