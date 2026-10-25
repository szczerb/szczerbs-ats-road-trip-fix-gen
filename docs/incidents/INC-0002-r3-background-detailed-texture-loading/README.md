# INC-0002: R3 background disappears at detailed world-map zooms

**Status:** open runtime regression; diagnosis complete, corrective build and runtime confirmation pending.

**Documented — user, 2026-10-25:** ATS world map has four visible zoom levels. The r3 background appears only at maximum zoom out and disappears at the three more detailed levels. This supersedes blanket runtime-unknown wording for that behavior; it does not validate shoreline improvements or other interfaces.

**Observed locally — 2026-10-25, ATS 1.61.3.18s:** the latest game log explicitly names the delivered r3 archive in a DirectStorage batch failure, code `0x89240008`. Microsoft identifies this as `E_DSTORAGE_REQUEST_TOO_LARGE`: a compressed or uncompressed request exceeds the configured staging buffer. R3 increased each detailed DDS from 64 MiB to 256 MiB of pixels, while the separate overview remains 16 MiB. The log and resource split strongly implicate this change. The log omits the failing member/chunk and actual staging size, so the exact DDS request is not proven individually.

- [Problem and resource changes](PROBLEM_STATEMENT.md)
- [Debugging plan and controlled correction](DEBUGGING_PLAN.md)
- [Inspection steps and provenance](STEP_BY_STEP.md)
- [Findings, alternatives and limits](RESULTS.md)
- [Analysis task](../../tasks/done/TASK-0054-diagnose-r3-detailed-map-background-loss.md)
- [R3 delivery and original offline checks](../../reference/NORTH_AMERICA_BACKGROUND_1_61_R3.md)
