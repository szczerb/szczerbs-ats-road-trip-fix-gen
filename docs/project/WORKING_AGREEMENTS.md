# Working Agreements

## Documentation and evidence

Write all workspace-authored documentation in English. Keep root documents navigational, stable evidence in references, current work in tasks, durable decisions in ADRs, and reproducible failure evidence in incidents. Update current state whenever findings or priorities change.

Use these labels for substantive technical findings:

| Label | Meaning and required evidence |
| --- | --- |
| **Documented** | Supported by a linked primary source; record applicable game/tool version and inspection date. |
| **Observed locally** | Seen in a named archive/file or experiment; record source path, version when available, date, and method. |
| **Hypothesis** | A possible explanation, its origin, and the comparison or experiment that could test it. |
| **Unknown** | Evidence is missing or insufficient; state what must be collected next. |

Treat old wiki pages as evidence for the described behavior, not proof of the complete ATS 1.61/Road Trip schema. Distinguish shared ATS/ETS2 engine concepts from ATS-specific behavior. Metadata declarations are not tested compatibility, and static file observations are not in-game validation. User reports must be attributed as reports; do not relabel them as reproduced local observations.

## Portable versioned paths

Never record absolute host filesystem paths in versioned material or commit messages. This applies to documentation links, tracked reports, source comments, configuration examples and fixtures. Use repository-relative project paths and document-relative Markdown links. External filesystem locations must be supplied through runtime arguments or ignored local configuration; construct temporary paths at runtime. URLs and game/archive virtual identifiers retain their required syntax. Inspect staged changes and commit messages before publication; ignored reports may contain local paths and require a separate review before sharing.

## Image evidence

Before citing a user-supplied screenshot or image in documentation or a task/goal prompt, keep an unchanged project-local copy and cite that copy with a relative path. Check an existing copy and reuse it when it already matches; avoid duplicating large images. Leave the supplied original untouched, record its provenance and SHA-256 in the evidence manifest, and do not write to `local_inputs/`.

Store large image evidence in ignored `local_outputs/work/<Warsaw timestamp>/` directories. Use tracked documentation-image locations only when that storage is appropriate and authorized. Relative documentation links resolve from the Markdown file; paths in a goal prompt must explicitly resolve from the project/worktree root. Do not make the external Windows screenshot folder or a transient attachment path the working reference.

Label ignored evidence as local-only and state how to supply it in another checkout. If a future worktree lacks the copy, reuse the preserved evidence read-only or copy it into that worktree's new ignored run and update its relative references; verify identity rather than inventing a path. Existing original copies and historical artifacts stay in place.

## Tasks and decisions

Follow the [task/ADR workflow](HOW_TO_WORK_WITH_TASKS_AND_ADRS.md) and templates. Use `backlog`, `active`, and `done` statuses only; keep location synchronized. Record dependencies, blockers, uncertainty, acceptance criteria, and actual verification. Keep Courier Job and refueling research at equal priority unless the user changes direction.

## Delegation and cost

Delegate independent bounded work using explicit file ownership in shared checkouts. Select an economical model and effort for routine inventory/documentation; use a stronger model where technical uncertainty or integration warrants it. Review delegated claims, source quality, and links. Every Plan Mode plan must contain a task/model/effort breakdown; distinguish work already performed from proposed assignments. Record actual contributors and material checks in the task.

## Artifacts and experiments

Treat `local_inputs/` as read-only. Do not extract to it, rename or edit supplied archives, or automatically remove sidecars or other untrusted adjacent metadata. Preserve sidecars unless the user explicitly requests a change. Keep the existing ignored-directory rules intact. Put all new scratch, extracted samples, reports, temporary archive staging, and expressly requested input-sidecar moves under `local_outputs/work/<YYYY-MM-DD_HH-MM-SS>/`, using Europe/Warsaw local time. Put generated mods under `local_outputs/generated/<YYYY-MM-DD_HH-MM-SS>/` with human-readable names that identify the map and ATS/map version. Keep each run's artifacts in its timestamped directory; do not move or delete older outputs automatically. Use selective metadata/text reads before considering broader extraction. Keep large logs, game/mod assets, downloaded tools, and generated packages out of tracked docs. See [workspace structure](../reference/WORKSPACE_STRUCTURE.md).

Track small original project-authored icon exports and prompts under `assets/mod-icons/`; keep large generated originals ignored. Fuel package naming, author and game-based revision requirements follow the [metadata contract](../reference/MOD_METADATA.md).

Alternative experiment packages must identify their variant at the start of the display name, archive filename and description, before branding that may be truncated. Include a readable method/area distinction and an explicit simultaneous-versus-alternative instruction. Do not identify packages by list order, file timestamps, identical descriptions, or method suffixes hidden at the end of long titles. Metadata-only replacements must preserve all gameplay bytes. See the [metadata contract](../reference/MOD_METADATA.md#experimental-variant-identity).

Future in-game experiments must use a disposable or copied profile and record exact build, DLCs, mod versions, load order, observation method, and logs. Do not prescribe a market reset or modify a live save without establishing its effects and the experiment's authorization. Initialization performs no in-game experiments.

## Commits

The user authorizes routine local commits at coherent, verified milestones. There is one contributor. The maintainer configured the GitHub origin and uploaded the cleaned history privately on 2026-10-18. Requested audits may inspect the existing remote read-only; agent pushes, remote replacement and visibility changes need user direction. Small documentation changes and stable work can go directly on `master`. Isolate substantial/experimental tooling in `codex/` branches; use worktrees when parallel edits need independent checkouts. Merge verified milestones locally and report any experiments retained on branches. Resolve shared immutable inputs at runtime when working from another checkout; never record their absolute host locations in versioned material.

Use a meaningful concise subject and a body for non-trivial changes. Broad, checkpoint, architectural, and first-project commits must explain major areas changed, purpose, relevant user feedback/caveats/direction, and verification. Avoid vague subjects whose meaning requires opening the diff. The canonical instructions are in [AGENTS.md](../../AGENTS.md#commit-messages).
