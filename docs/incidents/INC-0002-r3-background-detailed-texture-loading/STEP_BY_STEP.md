# Inspection steps and evidence

**Observed locally — 2026-10-25:** working branch `codex/north-america-background`, starting source/delivery commit `5e1de7a`. Inputs and all prior generated packages are unchanged.

Scratch root: `local_outputs/work/2026-10-25_17-54-11/` (Europe/Warsaw).

- `log-audit/game.log.txt`: read-only snapshot of the current user log, 320488 bytes; SHA-256 `d661e16840f7d14032bdf0ebdc93daba5a54ec91e6283b03af8e64fca3120d9b`; source mtime `2026-10-25 17:51:58.706831600 +0100`.
- `log-audit/summary.txt`: bounded delegate findings.
- `resource-audit/r2-r3-resource-comparison.md` and adjacent machine-readable audit: independent archive comparison.
- `main/verify_loading_delta.py` and `main/verified-loading-delta.json`: main's independent installed-file SHA, eleven unchanged resource checks, DDS headers/expanded sizes and exact log excerpts.

R2 input: `local_outputs/generated/2026-10-24_18-30-20/szczerbs-road-trip-north-america-background-map-ats-1.61-r2-experimental.scs`, SHA-256 `58cbfe4047113308bb82a0e5ed4d15e298515f22916bab8eb8b1fc403c521604`.

R3 input: `local_outputs/generated/2026-10-25_07-07-39/szczerbs-road-trip-north-america-background-map-ats-1.61-r3-experimental.scs`, SHA-256 `8d29a9531e4ffab939f11891042e3a5fc2260310d7919eae83797f0329be9329`.

At snapshot lines 2780–2781, timestamp `00:05:02.480`, the engine logs:

```text
<ERROR> [dstorage] Batch error! This is the error code of the first failure. Invalidating all remaining requests! (0x89240008)
<ERROR> [dstorage] File: .../szczerbs-road-trip-north-america-background-map-ats-1.61-r3-experimental.scs, Chunk:
```

The chunk field is empty. The error record names the archive, not `map0.dds` or another member. No separate DDS decoding or graphics-memory-exhaustion error was found. The log also includes repeated `The transit image is too big (11008x2880), check the viewport!` warnings/errors; these refer to a separate transit render target and do not identify map DDS files.

Actual delegation: GPT-6 Luna/high owned only `resource-audit/`; GPT-6 Luna/medium owned only `log-audit/`. Main independently checked their decisive archive/log observations, verified Microsoft sources, integrated the diagnosis and authored these documents. No main/delegate launched the game, changed graphics/launch settings, edited the live mod, save or profile, rebuilt the geographic model, or published anything.
