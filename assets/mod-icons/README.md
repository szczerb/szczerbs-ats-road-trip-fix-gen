# Original gas station fix icons

Created and inspected: 2026-10-17. **User selection: C**, the green sign with a pump and four passenger cars. Its top text is `GAS STATIONS FIX`; bottom text is `ATS EXPANSION`. A and B remain alternative proposals. All three tracked files are original project artwork exports, not game assets or copied ATS logos.

| Option | File / motif | Bytes | JPEG SHA-256 |
| --- | --- | ---: | --- |
| A | [Pump and one car](ats-expansion-a.jpg) | 29,055 | `3dc705ce50b03bfe7e7f9e992fc4fadb63ac7bed1f554134265e5dcb99f58c1f` |
| B | [Nozzle and two cars](ats-expansion-b.jpg) | 25,487 | `f7387266da5cfd4ffd3145d039f0037af37c816b998a923b64a8d70d0ade37b0` |
| C | [Green sign, pump and four cars (selected)](ats-expansion-c.jpg) | 28,404 | `5fc8e0d416a338cdc8d4aa3b2ebb00cc71ee593a2c90771eebd8a1d40a9d6ea8` |

## Generation and export

GPT-6 Luna / medium prepared three separate built-in **imagegen** requests, one per proposal, with no API/CLI fallback. [Exact prompts](PROMPTS.md) preserve the requests verbatim. The use case is brand/icon design; the recorded prompt asset label does not select an API model. The originals were copied from the tool's generated-images destination into ignored `local_outputs/artwork/icon-proposals/`:

- `proposal-a-pump-one-car.png`, 1637x960.
- `proposal-b-nozzle-two-cars.png`, 1637x961.
- `proposal-c-pump-several-cars.png`, 1637x961.

The root agent inspected each original and exported the three JPEGs using FFmpeg, Lanczos scaling to 276x162, one frame, JPEG quality 2 and `yuvj444p`. This is the final format/size export; no subject, text or palette edits were applied after generation. All exports were decoded with FFmpeg, visually reviewed at native size and checked by the package writer's JPEG header validation. The large generated originals remain ignored; these small, self-contained JPEG exports and prompts are tracked. Repeating a creative generation is not byte-deterministic; reusing the tracked exports makes package generation deterministic.

For another map, prepare a separately reviewed icon with that map's own bottom label. The CLI does not edit embedded text or automatically choose artwork. Always pass the selected map's JPEG via `--icon`. See the [metadata contract](../../docs/reference/MOD_METADATA.md) and [sample command](../../docs/reference/OVERLAPPING_FUEL_SAMPLE.md#reproduce).
