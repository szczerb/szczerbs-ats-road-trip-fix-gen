# Problem statement

**Documented — user report, 2026-10-25:** expected background at all four visible world-map zoom levels; observed background only at the furthest level. The closer three levels are blank. The user requests analysis of changes in the last revision; this investigation makes no new mod, installation or in-game fix claim.

**Observed locally:** the installed r3 archive SHA-256 matches the delivered archive: `8d29a9531e4ffab939f11891042e3a5fc2260310d7919eae83797f0329be9329`. Current log identifies ATS `1.61.3.18s`, DX11, RX 7900 XTX with 24516 MB reported GPU memory and an active r3 mod. Exact effective provider priority is not fully reconstructed in this bounded investigation. The supplied r2/r3 packages are compared directly.

| Resource | R2 | R3 | Consequence |
| --- | --- | --- | --- |
| Rendered source atlas | 8192 square | 16384 square | Doubled linear sampling density |
| `map.dds` overview | 2048 square, 16 MiB pixels | Same dimensions/size | Small overview still available |
| Each `map0..3.dds` quadrant | 4096 square, 64 MiB pixels | 8192 square, 256 MiB pixels | Fourfold expanded request size |
| Four detailed quadrants combined | 256 MiB pixels | 1 GiB pixels | Larger loading/upload burden |
| DDS layout | DX10 BGRA8 sRGB, one mip | Identical format/layout policy | No new codec or mip policy |
| `def/map_data.sii` | 4391 bytes | Byte-identical | Zoom, bounds, masks and camera values unchanged |
| Five MAT and five TOBJ files | Existing definitions | Byte-identical | Paths, shader, addressing and mip filter unchanged |

Exact DDS file lengths include the 148-byte header: overview 16777364 bytes, r2 detailed tile 67109012 bytes, r3 detailed tile 268435604 bytes. Both archives use ZIP DEFLATE for these members. A small compressed archive does not make the expanded texture small.

`map0..3` are northwest/southwest/northeast/southeast geographic quadrants, not four individually named zoom levels. The separate overview/detail resource path explains why one visible level can work while all closer levels fail; the exact runtime selection switch is inferred from the symptom and existing resource contract, not instrumented in this run.

**Observed locally — source changes:** r3 also changes source geography and calibration. These change texture pixels, not the unchanged material/TOBJ/map-definition resource contract. Additional archive members are GSHHG licensing texts. None provides a comparable explanation for a consistent overview/detail disappearance.
