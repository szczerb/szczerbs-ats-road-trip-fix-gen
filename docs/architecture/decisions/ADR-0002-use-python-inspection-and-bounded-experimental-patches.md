# ADR-0002: Use Python inspection and bounded experimental patches

## Context

Date: 2026-10-17. The user authorized autonomous research, useful archive tooling, and an evidence-supported proof of concept after initialization. Both compatibility investigations produced concrete static mechanisms, with runtime uncertainties. See [courier findings](../../reference/COURIER_RESEARCH_FINDINGS.md), [refueling findings](../../reference/REFUELING_RESEARCH_FINDINGS.md), and [installed baseline](../../reference/RESEARCH_BASELINE.md).

The environment provides Python 3 and a working Linux HashFS extractor. Existing source ZIPs and HashFS packages, conditional mounts, additive SII files, and binary PPDs all need inspection. Choosing an unrelated UI framework or implementing a complete HashFS engine would not advance the immediate experiments.

## Decision

Use Python 3.11+ and its standard library for a CLI/package, with the external versioned sk-zk Extractor for HashFS. Keep original archives and game installation read-only; store extracted/reference data and generated packages in ignored output directories. Use explicit low-to-high package ordering, support directory/base/DLC mounts, and fail on unsupported nested-part archives or ambiguous mounts.

Implement read-only unit/include parsing sufficient for the observed definitions. Preserve unsupported/ambiguous attribute information and fail if an analysis consumes it; do not rewrite arbitrary original SII. Audit context coverage without equating it to playable job availability.

Two explicitly experimental generators are supported:

- Courier aliases: match an unclassified map-used prefab to an officially classified prefab using the same model and PPD paths; require available assets, unchanged canonical references, no map asset override, no exclusion, and unambiguous tags. Emit only a new additive context file, with source/asset fingerprints. Allow restricting generation to a reviewed prefab such as `ahorrara`.
- Fuel descriptors: for structurally consistent PPD v25 only, duplicate existing GAS type-3/flags-0 locators with flags 1, preserving originals and other section data. Refuse unknown GAS flags and implicit v23/v24 upgrades. Do not edit map sectors or claim runtime service rebuilding.

Outputs are deterministic ZIP_STORED `.scs` packages containing a generated manifest, description, changed resources, and a JSON report declaring experimental status and unperformed game validation. The CLI requires `--experimental`; existing output files are not overwritten. A declared ATS 1.61 version is required. These are research interfaces, not a stable public API.

## Consequences

The first increment produces reproducible static experiments and useful diagnostics. It does not automatically fix arbitrary companies, infer safe new marker coordinates, or validate a whole active profile. Exact path equivalence is a conservative candidate rule, not proof of physical placement. Fuel PPD changes may require separate map/editor service rebuilding. A copied-profile validation task follows; preserve truck behavior and shared progression during that future work.

No remote or push is introduced. Verified work is committed on the local research branch and integrated locally into master; disposable experiments remain ignored. See [prototype task](../../tasks/done/TASK-0006-build-inspector-and-experimental-generators.md).
