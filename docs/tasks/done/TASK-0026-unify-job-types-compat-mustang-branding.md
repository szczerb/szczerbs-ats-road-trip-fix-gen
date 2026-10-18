---
id: TASK-0026
title: Unify Job Types Compat Mustang filename and metadata
status: done
priority: high
repositories: [.]
depends_on: [TASK-0025]
owner: shared
---

# Goal

Use Job Types Compat Mustang consistently in the courier mod filename, manifest, descriptions and current generator output.

# Context

**Documented — user instruction, 2026-10-18:** the courier filename still says practical, while approved artwork says JOB TYPES COMPAT / MUSTANG. Unify the player-facing name. Preserve author szczerb and established Road Trip branding, game-based revisions and experimental suffix.

# Scope

- Display name `szczerb's Road Trip Job Types Compat Mustang` and filename `szczerbs-road-trip-job-types-compat-mustang-1.61-r3-experimental.scs`.
- Update generator presets/work folder names and courier/map descriptions, including load-order references.
- Advance courier to r3 and map metadata to r7 so updated labels are distinguishable from previous handoffs.
- Keep exact approved J3C/M2D artwork, job eligibility, map gameplay resources and source-pinned policy unchanged. CLI command names and policy filename stay stable.
- Preserve historical outputs; no live installation or game/profile operation.

# Implementation Plan

| Assignment | Actual model / effort | Ownership |
| --- | --- | --- |
| Current guides and metadata contract | GPT-6 Sol / medium | Seven explicitly assigned documentation files |
| Naming integration, packaging and task evidence | Root | Source/tests/assets/new handoff and task |
| Independent archive/branding comparison | GPT-6 Luna / medium | Read-only ignored verification evidence |

# Acceptance Criteria

- Manifest name, archive filename, description title/load order and current docs agree with approved wording.
- Analysis remains report-only; source configuration and gameplay outputs are unchanged.
- Courier and seven map resources match previous accepted payloads exactly; icons remain byte-identical.
- Task/link/status consistency, appropriate tests, immutable inputs, ZIP inventory and CRC/hash checks pass.

# Verification

Completed 2026-10-18. Work and packaging evidence: `local_outputs/work/2026-10-18_16-44-40/`.

- All 246 tests pass, including exact courier filename/full manifest title, renamed icon/work paths, new default revisions, current description labels, and report-only analysis behavior.
- Root and independent GPT-6 Luna checks confirm all eight gameplay dictionaries, inventories and SHA values match the accepted r6/r2 sources. All eight icons are byte-identical. Original source archive SHA values are unchanged.
- Courier r3 uses the exact requested name in its manifest, filename, title and priority. Seven map r7 descriptions use the same courier label, with exactly one current marker and unchanged source/ProMods priority. No mod description retains the former title. Historical report provenance and policy names remain preserved deliberately.
- ZIP CRC, bundle SHA/size, eight-mod-plus-README inventory and every bundled member hash pass. The current preset is the approved J3C byte sequence under its renamed asset path. No live installation, input/archive editing, profile modification or gameplay test occurred.
- Documentation QA passes 768 links, 27 heading fragments and 26 task records with synchronized status/dependencies; all 12 input identities and 26 artifact exclusions pass.
- Sol updated bounded current guides; Luna independently reviewed packages; root integrated naming, tests, refreshed archives and evidence. New handoff: [r7/r3 naming delivery](../../reference/MOD_METADATA_RENAME_1_61_R7_R3.md).

# Links

- [Previous approved metadata delivery](../../reference/MOD_METADATA_FINAL_1_61_R6_R2.md)
- [Metadata contract](../../reference/MOD_METADATA.md)
- [Courier generator](../../reference/PRACTICAL_COURIER_GENERATOR.md)
