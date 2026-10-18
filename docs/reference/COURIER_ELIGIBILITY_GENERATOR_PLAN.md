# Plan: explicit Mustang courier eligibility experiment

**Status: implemented 2026-10-18.** This document preserves the reviewed design rationale and initial proposal. For actual commands, generated-package evidence, and current limits, see the [implemented generator guide](PRACTICAL_COURIER_GENERATOR.md). The example TOML remains the reviewed input. No game/profile installation or runtime validation has occurred.

## Goal and source boundary

Use a human-reviewed, version-pinned configuration to add the Mustang's `muscle` class to selected stock `car_job_data` units for owned-car Dispatch exploration. The user excludes vehicle transfers and selects certificates/customs paperwork, keys, samples, small parts, maps/seals, and compact equipment/supplies as practical candidates. These are ordinary real-world judgments, not measured Mustang cargo capacity.

The pinned ATS 1.61.3.18 definitions contain 149 job units. Parser counts are 147 sedan-tagged, 54 tagged `muscle` or `veteran`, 52 shared, 95 sedan-only, and 2 Mustang-only. The 95 sedan-only units include 88 cargo-bearing units and seven ordinary Car Jockey units with no `cargos[]`. Two additional Mustang-only units are premium-allocation vehicle-transfer jobs. The config pins the normalized numeric game version, exact source fingerprints, and the digest of the sorted 149 job IDs; refresh requires review when the version, source hash, ID set, or counts change.

The example divides all 88 sedan-only cargo jobs (46 distinct cargo IDs) into enabled groups (58 jobs, 32 IDs) and disabled groups (30 jobs, 14 IDs). Enabled: paperwork/maps (10), keys/seals (4), samples (18), small parts (8), compact equipment (15), and small supplies/seedlings (3). Disabled: ambiguous machinery/outboard parts/propellers (19) and unclear sealed, unidentified, restock, or mixed shipments (11). Fragile and valuable variants follow their family defaults. Samples, relays, diagnostic modules, hand tools, snacks, and young seedlings are treated as plausible carloads for this experiment, while their quantities and dimensions remain unknown. Unclear generic machinery, outboard parts, propellers, and shipment contents remain optional, easy-to-review groups.

The parser-based validation of this proposed TOML and its source-pinned cargo-ID partition is recorded in the ignored coverage scratch report (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-33-59/proposed-config-static-coverage.json`).

## Proposed selection and patch behavior

1. Read TOML with Python 3.11 `tomllib`; validate schema version, normalized numeric ATS version (`1.61.3.18`, matching the installed-version reader), both source hashes, sorted job-ID digest, target class token, unique group IDs, disjoint cargo-ID membership, and an explicit default for every group. Reject unknown keys/IDs and count mismatches.
2. Parse the effective stock `def/car_job_data.sii` and `def/car_cargo.sii` with the existing SII reader. Require the exact expected 149 unique stock job IDs and sorted-name digest and a unique effective definition for each. Require configured family prefixes and cargo IDs to match the pinned source classification; do not infer from localized names or fuzzy matching.
3. Preserve all nine explicit transfer job IDs unchanged. Any other empty-`cargos[]` sedan-only job is a blocker. A cargo-bearing job is eligible only if it is a configured sedan-only family, every referenced cargo ID is known, and all its cargo IDs belong to enabled group(s). Disabled or mixed enabled/disabled cargo jobs remain unchanged; unknown cargo IDs, overlapping groups, duplicate attributes, and unsupported SII shapes fail closed.
4. For selected jobs only, add `muscle` to `vehicle_types[]` if neither `muscle` nor `veteran` is already present. Preserve every byte outside those explicitly changed array declarations, including comments, formatting, all other attributes, and all 149 unit IDs. If a strictly targeted byte-preserving edit cannot be produced, block. Do not add `veteran`, change Ford tags, alter ratings/cargos/contexts/distance, add aliases, or touch map sectors.
5. Emit a full same-path replacement for `def/car_job_data.sii`, retaining every source unit because SCS's older additive-file documentation does not list `car_job_data`. This can affect every system reading the shared job definitions, including Quick Jobs and Dispatch; there is no Dispatch-only filter here. Report the effective canonical provider and any declared replacements; block generation if its bytes differ from the reviewed source hash. Report additional job files separately, preserve them, and block conflicting duplicate unit IDs across resources. The replacement must load above game data and any intended source definitions; collisions with other replacement mods need an explicit report.

Use a source-span-preserving patch strategy. The current parser provides semantic attributes but no source offsets, so first extend it safely or add a tokenizer that preserves comments, whitespace, array ordering and non-target text. Never serialize all parsed units into a newly formatted approximation. Validate the result by reparsing and comparing all unit IDs, all non-target attributes, and the exact selected `vehicle_types[]` changes.

## Command, output, and report

Add `analyze-courier-eligibility --config <toml> [--game-dir <path>] [--dependency <path>]` and `generate-courier-eligibility --config <toml> [--game-dir <path>] [--dependency <path>] [--revision <n>] [--experimental]`, following the existing `ResourceStack` and `write_mod` patterns. Analysis reports proposed/blocked units and group totals without calling the writer. Generation defaults revision to 0, requires `--experimental`, and refuses to overwrite outputs. Write reports/mods only below ignored timestamped `local_outputs/work/<Warsaw timestamp>/` and `local_outputs/generated/<Warsaw timestamp>/` paths. The report records the config hash, source hashes/build, package order and overrides, exact changed unit IDs/fields, enabled and disabled group counts, exclusions, blockers, and `in_game_verified: false`.

Before extending `write_mod`, confirm that `other` is accepted as a manifest category by the target ATS 1.61 release; do not assume this based only on a general category list. If confirmed, add an optional validated category argument preserving existing callers' `map` default. Use an explicit courier experiment title, existing project author, experimental `1.61-rN` version, and no gas-station icon. The description says shared job eligibility can affect Quick Jobs and Dispatch. Do not call it a map fix.

## Acceptance and unresolved behavior

The generator is ready only when the exact source-pinned inventory is reproducible; the six enabled groups select 58 cargo units and the two disabled groups retain 30; all nine transfers and every empty/unknown cargo case stay unchanged or block; only selected jobs gain `muscle`; duplicate/unknown/config drift checks fail closed; analysis emits no resources; and the package report proves all non-target bytes are unchanged. Manual game validation is separate: on a copied profile, compare Dispatch with a matched unmodified control, then check Quick Jobs, offer appearance, acceptance, physical cargo attachment, route, delivery, and logs independently. Definition eligibility does not prove a Dispatch-only outcome, offer generation, fit, or completion.

## Work plan and model choices

| Work item | Status | Model/effort |
| --- | --- | --- |
| Draft this plan and the reviewed initial cargo configuration | Completed here | GPT-6 Luna, medium (actual) |
| TOML schema, hash/count checks, and inventory-only analysis | Future recommendation | GPT-6 Luna, low |
| Source-preserving SII patcher, writer category option, and CLI | Future recommendation | GPT-6 Sol, medium |
| Review merge/override behavior and generated diff before any handoff | Future recommendation | GPT-6.1 Sol, medium |
| Confirm market and physical behavior | Manual game session | User; not model-verifiable |
