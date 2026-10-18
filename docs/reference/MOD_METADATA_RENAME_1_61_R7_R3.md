# Job Types Compat Mustang naming: map r7 and courier r3

**Documented — user instruction, 2026-10-18:** align the courier mod's filename and metadata with the approved icon's JOB TYPES COMPAT / MUSTANG wording. The current display name is **szczerb's Road Trip Job Types Compat Mustang**. Author remains **szczerb**.

## Download

Job Types Compat Mustang r3 (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_16-44-40/szczerbs-road-trip-job-types-compat-mustang-1.61-r3-experimental.scs`).

Full eight-mod r7/r3 ZIP (local artifact, excluded from Git: `local_outputs/generated/2026-10-18_16-44-40/szczerbs-road-trip-test-batch-ats-1.61-map-r7-courier-r3-experimental.zip`), **68,458,855 bytes**.

Bundle SHA-256: `82152e10a06348ad0412ce4497b9138bfa0cc82b40c2ed3e9aed72c517bdb2d6`.

The courier archive is `szczerbs-road-trip-job-types-compat-mustang-1.61-r3-experimental.scs`. Its manifest name, description heading and priority instructions use Job Types Compat Mustang. The filename no longer uses `practical` or `muscle`. All seven map fixes advance to r7 solely to update their description's courier priority label and version/provenance. Their own map titles and resource coverage stay the same. Earlier [r6/r2](MOD_METADATA_FINAL_1_61_R6_R2.md) and older deliveries remain unchanged.

Replace older copies rather than enabling both names. Use the same priority: below the optional background map, above Food/Medical/Rideshare and map mods. Each map fix remains directly above its source. No automatic installation, live profile change or economy reset occurred.

## Tooling and preserved scope

Current generation defaults are courier r3, combined maps r7 and legacy fuel r2. The separate icon preset is now `assets/mod-icons/job-types-compat-mustang.jpg`; it contains the exact approved J3C bytes. Courier work folders use `job-types-compat-mustang` (or `job-types-compat-mustang-analysis`). Existing command names and the pinned `docs/examples/mustang-practical-courier.toml` policy filename remain stable. Those are technical interfaces, not the Mod Manager title.

**Observed locally — ATS 1.61.3.18 project, inspected 2026-10-18:** all gameplay resource paths, bytes and inventories are identical to r6/r2, and all eight embedded icons are identical. Courier still adds the same 58 reviewed stock job eligibilities while retaining nine unchanged vehicle-transfer jobs. The Mustang title remains shorthand for the intended user vehicle: shared muscle-class and Quick Jobs effects still apply. The rename does not add model-specific targeting or change ratings, rewards, source hashes or eligibility rules.

## Verification

All **246 tests pass**, including the exact new archive filename, full manifest title, new defaults, renamed preset/work paths, description priorities and report-only analysis boundary. Source/output ZIP CRCs and generated-resource size/SHA checks pass. Courier title/category/author/version, map markers and updated priority labels agree. The bundle contains eight mods plus README; all members match their standalone archives and its recorded SHA/CRC passes. Independent GPT-6 Luna review confirms package naming, descriptions, priorities, resource/icon equality, source identities and the bundle checks. Old source archives remain byte-identical. Old names in historical report provenance intentionally preserve the original generation evidence.

Documentation QA passes 96 Markdown files, 768 relative links, 27 heading fragments and all 26 task records (25 done, one active), plus all 12 unchanged input identities and 26 artifact exclusions.

Ignored work: `local_outputs/work/2026-10-18_16-44-40/`, containing full test log, source-linked `delivery-result.json`, `delivery.log`, `rename_delivery.py`, description previews and independent/documentation reviews. [TASK-0026](../tasks/done/TASK-0026-unify-job-types-compat-mustang-branding.md).

**Unknown — runtime:** Canadian prices/billing, car rest and courier acceptance/cargo fit/completed deliveries still require the existing [manual checklist](MANUAL_TEST_CHECKLIST.md). Metadata consistency and unchanged bytes do not establish those results.
