# Courier location reporting

Updated: 2026-10-18. Target: ATS 1.61 with Road Trip Ford. This increment reports static inputs only; it generates no courier fix or market changes. [ADR-0009](../architecture/decisions/ADR-0009-report-courier-inputs-before-generating-fixes.md) records that boundary. [Marker research](COURIER_MARKER_RESEARCH.md) records the actual physical-point comparison and its limitations.

## Run one source-map report

```bash
PYTHONPATH=src python3 -m ats_road_trip analyze-map \
  local_inputs/ATS_Expansion_v23.0_1.61.scs --processor courier
```

The source-map workflow resolves the installed ATS baseline, map DLCs, Road Trip Ford and known source-family companions. Supply `--game-dir` when detection is unsuitable. Repeat `--dependency` in lowest-to-highest order when the source needs other packages; the source remains highest in this source-relative workflow. This is not automatic reconstruction of the live profile. Inputs and game files remain read-only.

There is no `--experimental` requirement for analysis, because no `.scs` is written. The command prints the new audit path under `local_outputs/work/<Europe-Warsaw-timestamp>/<map-slug>-analysis/audit.json`. It refuses to overwrite an existing audit. Unlike generation, partial inspection can still return a useful report, with `reported_partial` status and explicit blockers. I/O/setup errors still fail with a failure audit where possible.

`ProcessorMode.ANALYZE` permits the `courier` topic; default `GENERATE` continues to reject it. The old `courier-audit` command remains a context/definition-only report; it does not provide this placed-location analysis. Historical `generate-context` experiments retain their original explicit experimental boundary and are not called by this processor.

## What the report means

| Report evidence | Interpretation |
| --- | --- |
| Company item, city/company tokens, parent prefab UID | A serialized placed company and its declared identity; not a generated offer |
| Activation node, world coordinates and source sector | A resolved serialized Company main-node location; runtime selection and car activation remain unverified |
| Additional spawn nodes and raw flags | Separate loading/spawn data; no invented car bit or car endpoint suitability |
| Actual placed prefab, descriptor and generic type-13 Company Point count | Physical resource evidence; empty custom-depot descriptors can coexist with resolved map company nodes |
| Effective company editor definitions | Semantic city/prefab linkage, resolved from parsed units rather than an assumed `<city>.sii` filename |
| Actual and editor prefab contexts | Static tags and matching source/target job-definition IDs; mismatches remain visible |
| Explicit SCS exclusion comment | Intentional exclusion evidence, distinct from unclassified data; never an automatic patch instruction |
| Source package/path/SHA-256 and inspection coverage | Reproducible provenance and stated scope, subject to the supplied package order |

Only source-owned `.base`/`.aux` sectors are targets. A one-sector halo is fetched when their company references need nearby prefab/node data. This is bounded source-relative inspection, not a whole-world search. Unsupported compound-contained companies are explicitly counted and reported as coverage blockers. Conflicting/missing nodes, definitions, resources and associations remain unresolved; identical shared node copies may resolve.

`coverage.complete` describes the supported inspection, **not** courier support. Individual `static_linkage` values and `unknowns` remain significant even when inspection completes. Every location keeps `courier_market_eligibility: unknown`; the module does not simulate rating, eligible vehicle, distance/routing, destination availability, market time, discovery, pickup or delivery completion. Context matches are candidate job-definition references, not actual offers. Prefab definition inputs are fingerprinted, but the current reader attributes parsed units to the including root file rather than the exact included source line. Company editor `.sii` roots are parsed once; `.sui` fragments are read through includes instead of treated as independent roots.

## Evidence for shared job selection

**Observed locally:** 82 company records across 22 freshly source-matched stock/ATS Expansion sectors have one main company node and separate additional spawn arrays. Four selected stock depot descriptors have one generic Company Point/type-13 locator each; three custom-depot descriptors have none while their placed companies still have resolved nodes. [Exact evidence](COURIER_MARKER_RESEARCH.md).

**Hypothesis supported by that structure:** a common company check-in supplies job selection in the appropriate mode. No inspected data establishes a missing second car-specific selection marker. **Unknown:** actual truck/car activation and avatar rendering in each game state. Do not turn this static observation into an automatic marker-duplication rule.

## Actual source reports

**Observed locally — ATS 1.61.3.18, 2026-10-18:** the public `analyze-map` command was exercised on ATS Expansion and on the existing WCE r3 patch as a bounded source. Both reports inspect original effective inputs, emit zero mods and retain `courier_market_eligibility: unknown` for every company.

| Evidence | ATS Expansion source | WCE r3 patch source |
| --- | ---: | ---: |
| Source sector files parsed | 540 / 540 | 123 / 123 |
| Company placements | 1,246 | 380 |
| Resolved main nodes | 1,246 | 380 |
| Resolved separate spawn nodes | 6,376 | 2,440 |
| Actual prefab classified / explicitly excluded / unclassified | 1,171 / 63 / 12 | 341 / 20 / 19 |
| Resolved semantic editor links | 1,226 | 380 |
| Per-location partial linkage | 97 | 39 |
| Sector/definition inspection blockers | 0 | 0 |

**Observed locally:** ATS Expansion's remaining editor records comprise 18 unresolved company tokens (four also have unresolved city tokens) and two duplicate semantic candidate sets. The duplicate sets are `vor_oil_gst` / `woodward` and `mcsb` / `sidney`, with byte-identical files at different effective paths; the reporter keeps both sources instead of inventing engine duplicate-unit precedence. A separate `pt_trk_dlr` / `joplin` pair shares a prefab UID but has distinct Company records/main nodes. This is a diagnostic, not evidence that one Company is for trucks and the other for cars. Across ATS Expansion, 699 locations use descriptors with one generic Company Point and 547 use descriptors with none; all their main nodes still resolve.

**Observed locally:** the WCE patch-source report detects all 14 private aliases from the [independent static alias audit](COURIER_MARKER_RESEARCH.md#existing-generated-prefab-aliases-a-static-cross-feature-risk): their actual context is unclassified while their original editor context is `truck_dealer`. Its other five unclassified placements use `d_food_str`. WCE r3 scope covers only the 123 sector files carried by the patch, with original WCE and ProMods supplied below it; this does not reconstruct the active profile or report all original WCE sectors. Existing packages remain unchanged. [Preservation follow-up](../tasks/backlog/TASK-0019-preserve-contexts-for-generated-prefab-aliases.md).

Final audits are under `local_outputs/work/2026-10-18_02-50-30/ats-expansion-analysis/audit.json` and `local_outputs/work/2026-10-18_02-50-30/western-canada-r3-audit-analysis/audit.json`. Exact hashes and independent verification are recorded in the milestone task. Earlier `02-46-30` audits preceded the final `.sui` include guard and remain historical artifacts, not the final handoff.

## Verification boundary

Source-map integration results and final test counts are recorded in [TASK-0018](../tasks/done/TASK-0018-report-courier-company-locations.md). Manual validation stays in [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md): observe the opened market at a common company location in truck and car modes, then test a courier offer, reachable pickup and completed delivery independently. No further manual testing is expected during this night's work.
