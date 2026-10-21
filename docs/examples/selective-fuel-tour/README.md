# Reproduce the selective fuel comparison

ATS **1.61.3.18**, inspected 2026-10-21. This is a bounded fuel-only comparison, not a complete realistic parking preset. [Policy and actual test handoff](../../reference/SELECTIVE_CAR_FUELING.md) records the evidence and output audits.

- `manifest.json` pins six placements, five original sector resources and seven independent price-source packages.
- `selective-policy.json` contains four reusable layout rules. Placement UIDs belong only in the manifest; suitability rules use descriptor/model state and per-GAS evidence.
- The public batch command requires original map/resource inputs in the exact low-to-high order listed in the test README. Installed game/DLC packages are mounted automatically; omit generated r9/F packages from generation inputs.
- Keep the shared `local_inputs/` read-only. A worktree may reference the main checkout's original archives by absolute path; no copies are required.

Use the same installed source stack as the delivered handoff. The explicit input sequence is MegaResources, Reforma, ATS Expansion, Western Canada Expansion, ProMods models/assets/map/def, OtherMaps, Western Canada ProMods Connections, Alaska Expansion and the inspected Real companies directory. Pass each with a separate `--package PATH`; source basenames and sector hashes are checked. A different installation needs renewed evidence, not edited pins to bypass drift.

From the research checkout, with the required `--package` arguments added:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m ats_road_trip --extractor EXTRACTOR generate-fuel-selection-batch --manifest docs/examples/selective-fuel-tour/manifest.json --experimental --revision 1 --fuel-policy broad
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m ats_road_trip --extractor EXTRACTOR generate-fuel-selection-batch --manifest docs/examples/selective-fuel-tour/manifest.json --experimental --revision 1 --fuel-selection-json docs/examples/selective-fuel-tour/selective-policy.json
```

`--game-dir PATH` can select the audited ATS installation explicitly. Default run IDs use Europe/Warsaw timestamps; choose a fresh `--run-id YYYY-MM-DD_HH-MM-SS` to reproduce a named run. Both alternatives can share one run ID because their work/output names differ. Existing destinations are refused. The handoff includes exact executed argument arrays, input order, source fingerprints and complete embedded selection configurations with canonical hashes.

Use `analyze-fuel-selection-batch` instead of `generate-fuel-selection-batch`, omitting `--experimental` and `--revision`, to plan/report without a mod writer. Generation checks original source ownership, UIDs and hashes; validates even policy-skipped fuel graphs; repairs petrol prices independently; preserves context lineage; rechecks input identities before output; rejects policy-skipped services/nodes extending into unguarded neighboring resources, and emits source-sector guards needed to block lower r9 additions at exclusions. Guards have a documented temporary cost to other generated features in the replaced resources. Static audit is separate from later gameplay.

General `generate-map-fix --processor fuel --fuel-selection-json ...` also accepts this policy, but performs source-relative map coverage and does not implement the bounded tour's guard/subtraction behavior. Its selective output must replace its same-source broad package. Unseen layouts are uncertain and skipped under this configuration; `unknown: include` is an explicit alternative, not proof of suitability. No general visual-byte pins or complete collision/access classifier are implemented.
