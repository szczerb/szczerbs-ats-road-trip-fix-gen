# Current State

Updated: 2026-10-17. Initialization completed and verified under [TASK-0001](../tasks/done/TASK-0001-initialize-project.md).

## Current milestone

The workspace was generated with the bootstrap skill in merge mode and specialized for this project. Agent/workflow instructions, five technical reference topics, an input inventory, a workflow ADR, and four research backlog tasks are complete. Documentation links, task metadata/dependencies, inventory metadata, and artifact exclusions passed verification. No task is active; no utility, generated fix, or in-game validation exists.

## Evidence collected

- **Observed locally, 2026-10-17:** five supplied `.scs` archives are present. ATS Expansion, Alaska Expansion, and Western Canada Expansion are ZIP-readable; both Reforma packages have HashFS v2 headers. The ZIP archives contain stored and DEFLATE entries.
- **Observed locally, 2026-10-17:** ATS Expansion uses a `base/` asset prefix; Alaska and Western Canada use root-level `def/` and `map/`. Small company definitions connect city identifiers to prefabs, and ATS Expansion includes traditional company cargo input/output definitions.
- **Unknown:** the internal Reforma content; a suitable HashFS extractor was not available on PATH during inspection. No full extraction, integrity scan, or in-game compatibility check was performed.

Exact archive metadata, source paths, method, and limitations belong to the [inventory](../reference/LOCAL_INPUT_INVENTORY.md). These observations establish input structure only; they do not diagnose either gameplay issue.

## Open questions

- **Hypothesis:** missing courier markers or company naming explains absent jobs. This is unproven; [courier research](../tasks/backlog/TASK-0003-investigate-courier-compatibility.md) must distinguish physical locations from registration and market eligibility.
- **Unknown:** station physical access, trigger behavior, and fuel/vehicle eligibility in affected areas; [refueling research](../tasks/backlog/TASK-0004-investigate-car-refueling-compatibility.md) has equal priority.
- Exact installed game build, Road Trip/DLC package data, enabled mod stack/load order, and working/affected examples have not been established. Collect them when the corresponding research starts, not during initialization.

## Next work

Start [reference data and extraction preparation](../tasks/backlog/TASK-0002-establish-reference-data-and-extraction.md). Its findings support the two equal-priority compatibility investigations. Review both outcomes before [designing the first generator increment](../tasks/backlog/TASK-0005-design-first-generator-increment.md).

Implementation language, interfaces, schemas, extraction integration, override strategy, and output packaging remain undecided. See [system overview](../architecture/SYSTEM_OVERVIEW.md).
