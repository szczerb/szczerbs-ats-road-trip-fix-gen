# Practical Courier Jobs eligibility generator

**Observed locally, ATS 1.61.3.18, inspected 2026-10-18.** This standalone experiment adds the `muscle` class to selected stock Road Trip `car_job_data` units. It is a class-wide eligibility edit: any car with the `muscle` tag can be affected. The shared definitions can feed Dispatch Market, Quick Jobs, and other job readers. The reviewed stock Mustang tags are `muscle`/`veteran`; this workflow does not revalidate effective vehicle-definition tags after external vehicle mods. Such a mod needs a separate tag check. The tool does not target the Mustang model ID specifically, change the Mustang's tags, or modify map sectors.

The reviewed input is [mustang-practical-courier.toml](../examples/mustang-practical-courier.toml). It pins the normalized game version, effective `def/car_job_data.sii` and `def/car_cargo.sii` SHA-256 hashes, and a sorted job-ID digest. The ATS 1.61.3.18 source contains 149 canonical job units. Of 95 sedan-only units, 88 carry cargo; the example enables 58 and leaves 30 disabled. All nine vehicle-transfer units remain unchanged. The enabled groups cover paperwork/maps, keys/seals, samples, small parts, compact equipment, and small supplies. Ambiguous parts and unclear shipments default off. Changing a group's `enabled` value changes the selected jobs without changing its pinned source assertions; inspect the report before using a different policy.

## Run the commands

From this checkout, with Python 3.11 or newer:

```bash
PYTHONPATH=src python3 -m ats_road_trip analyze-courier-eligibility \
  --config docs/examples/mustang-practical-courier.toml \
  --game-dir "/path/to/American Truck Simulator"

PYTHONPATH=src python3 -m ats_road_trip generate-courier-eligibility \
  --config docs/examples/mustang-practical-courier.toml \
  --game-dir "/path/to/American Truck Simulator" \
  --revision 0 --experimental
```

`--game-dir` is optional when the installed ATS directory is detected. Repeat `--dependency /path/to/archive.scs` for explicit additional definition packages in low-to-high priority order. The workflow reads installed `def.scs`, `dlc_rt_ford.scs`, then declared dependencies; it records the effective canonical providers and same-path overrides. It does not infer the user's active profile order. `--run-id YYYY-MM-DD_HH-MM-SS` selects a Warsaw-time run folder; omit it for an automatic timestamp. For an external HashFS extractor, place global `--extractor /path/to/tool` before the subcommand.

Analysis writes a JSON audit below ignored `local_outputs/work/<run-id>/practical-courier-jobs-analysis/` and creates no mod. Generation requires `--experimental`, defaults to revision 0, writes its audit below `local_outputs/work/<run-id>/practical-courier-jobs/`, and creates one `.scs` below `local_outputs/generated/<run-id>/`. Existing audit or package paths are never overwritten. A package is emitted only when coverage is complete and free of blockers. The package has category `other` and the experimental version `1.61-rN-experimental`.

## Source and edit checks

The generator requires the exact reviewed source hashes and job-ID inventory. It rejects malformed policy keys or types, unknown cargo IDs, unlisted empty-cargo jobs, overlapping or unclassified families, duplicate job IDs in additional effective `car_job_data*.sii` files, unsupported source forms, and source drift. A source change requires a new review and updated fingerprints; do not merely replace the hashes to bypass the inventory checks.

For every selected unit, the patcher inserts one live `vehicle_types[]: muscle` declaration. It preserves the complete canonical file and every original byte outside those insertions, including comments, line endings, strings, other attributes, and all transfer bodies. It reparses the output, checks all 149 IDs and attributes, and reverses the insertions to prove exact original-byte recovery. The generated package replaces the full `def/car_job_data.sii` path. Put it above game data and any intended definition source. A different mod that replaces that path can supersede or be superseded by this package; inspect the active stack and regenerate against the intended effective provider instead of assuming field-level merging.

The 2026-10-18 generated package (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_03-56-10/szczerbs-road-trip-practical-courier-jobs-muscle-1.61-r0-experimental.scs`) has SHA-256 `e2f3b803e27435aad3d9db74fcc227a91aff0863a406fc995c91638d510d883b`. Its audit (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-56-10/practical-courier-jobs/audit.json`) reports 58 additions, 30 disabled cargo units, nine transfers, complete coverage, and no blockers. An independent package review (local artifact, excluded from Git: `local_outputs/work/2026-10-18_03-47-10/batch-review/courier-verification-final.json`) checked the archive CRC, its single canonical resource, all 58 exact insertions, and nine byte-identical transfer bodies. These are static checks.

**Unknown, pending manual game tests:** Definition eligibility does not establish Dispatch offer appearance, a Dispatch-only effect, job acceptance, physical cargo attachment, driving, or delivery completion. The tool does not install the package into a live mod directory or alter a profile. Use a copied test profile and the [manual checklist](MANUAL_TEST_CHECKLIST.md); compare Dispatch with a matched unmodified control and check Quick Jobs and logs separately. See [TASK-0007](../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md) for the outstanding game validation.

## Installed courier add-ons and priority

**Observed locally — 2026-10-18, installed Steam Workshop files, ATS 1.61 test setup:** Food Courier Jobs (3811536074, manifest 0.9.4), Medical Courier Jobs (3812885729, 0.2.4), and Rideshare Jobs (3813173177, 0.9.1) each select their `universal` package through `versions.sii`. Primary evidence is the installed `def/car_job_data.food_courier.sii`, `def/car_job_data.medical_courier.sii` and `def/car_job_data.rs_test.sii` resources in those package directories.

These job resources have distinct paths and unit IDs: 28 Food, 31 Medical and 87 Rideshare definitions, with no duplicates between them or the source-pinned r0 file's 149 stock IDs. They do not replace the canonical `def/car_job_data.sii`. No direct job-resource priority conflict was found with our r0; the three add-ons can remain together above the map packages in the shown order. Keeping North America Background Map first and placing Practical Courier Jobs immediately below it, above Food/Medical/Rideshare, is a clear arrangement. This statement concerns the inspected job resources, not every accessory or unrelated mod.

The installed definitions permit at least one reviewed Mustang tag (`muscle`/`veteran`) in 18/28 Food, 23/31 Medical and 87/87 Rideshare jobs. Our r0 changes only stock definitions and does not unlock the remaining add-on jobs. These counts are definitions, not live offers or completed deliveries. Two bounded read-only passes (GPT-6 Luna / medium and root parser comparison) agree on IDs and eligibility counts; no assets were extracted or changed. Runtime compatibility remains **Unknown**. Keep these add-ons unchanged between with/without-r0 comparisons to distinguish their jobs from the 58 stock eligibility additions.
