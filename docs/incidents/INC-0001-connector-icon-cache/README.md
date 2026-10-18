# INC-0001: Connector icon cache write failure

Opened: 2026-10-18. Status: **runtime confirmation pending**. ATS 1.61.3.18; Western Canada ProMods Connections compatibility fix r7. Implementation: [TASK-0027](../../tasks/done/TASK-0027-clarify-expansion-map-branding.md).

Runtime follow-up: [TASK-0007](../../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md).

The user reports a missing Mod Manager image. The package contains a valid 276x162 JPEG, while the game log reports failure copying it into the icon cache, followed by 8x8 dimensions. A long generated cache path is the leading hypothesis. The r8 handoff shortens package filenames and retains the connector image; no in-game success is claimed yet.

- [Problem statement](PROBLEM_STATEMENT.md)
- [Debugging plan](DEBUGGING_PLAN.md)
- [Investigation sequence](STEP_BY_STEP.md)
- [Results and limits](RESULTS.md)
- [Current r8/r3 handoff](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md)
