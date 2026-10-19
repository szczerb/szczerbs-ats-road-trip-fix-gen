---
id: TASK-0042
title: Test the analogous local-navigation fuel icon mask
status: done
priority: high
repositories: [.]
depends_on: [TASK-0041]
owner: shared
---

# Goal

Record the user's N1 parking-navigation success and both station-parking prompt results, investigate the directly analogous fuel-category visibility mask, and prepare a minimal N2 test candidate if supported. Keep parking geometry and all interaction resources unchanged.

# Context

**Documented — user report, 2026-10-19:** N1 restores parking icons in vehicle navigation. The fuel icon remains absent, while an in-world fuel-action avatar is visible. Both A and B provide a rest interaction; B was difficult to find without its navigation icon. Three supplied overhead screenshots show one engine-off prompt and nearby positions without it, suggesting unintuitive activation placement. This does not establish completed rest/fatigue recovery or a collision-free area.

**Observed locally — preserved log:** the three new screenshot events occur in B / `unmarked_geometry` plus N1, with handled/reset small-vehicle parking events consistent with the prompt sequence. Evidence is under `local_outputs/work/2026-10-19_20-36-39/navigation-followup/`. Earlier A attribution and the native Sioux Falls control remain separate evidence.

The user authorizes fuel-icon work if closely analogous to the parking fix; otherwise defer it. North America Background Map 5.3 omits the high category bits from its local-tier masks. N1 adds only bit 25; the candidate to investigate adds fuel bit 24 while retaining bit 25. Do not rely on previous prose assertions as independent engine evidence for the fuel category.

# Scope

- Preserve exact user/screenshot/log evidence and mark earlier no-position-found B observations as superseded at this tested scope.
- Investigate the fuel visibility category, actual source mask and relationship to the now-confirmed N1 mechanism.
- If justified, extend the same source-pinned generator with an explicit parking-plus-fuel variant, retain N1 as a control, and prepare an N2 r2 archive with early distinguishing metadata and exact load order.
- Preserve all world-map tier inputs, includes, unrelated mask bits, trigger/service/sector/prefab resources, fuel mechanics and A/B geometry. No parking-method, vehicle activation, size, position or density-policy edits.
- No game launch, installation, profile change, merge, push or publication. Retain the existing experimental branch/worktree and old artifacts.

# Implementation Plan

1. Copy the supplied images and a read-only log snapshot into a new ignored Warsaw-timestamped run; inspect and correlate the three screenshot events.
2. Independently research the analogous car-fuel category and source omission; state any uncertainty rather than treating a plausible candidate as a confirmed fix.
3. Implement an explicit N2 variant if justified, defaulting to unchanged N1 behavior. Retain source/include/version pins and generation safeguards.
4. Verify meaningful regressions and actual N1/N2 archive differences, source/geometry preservation, metadata, virtual resource composition and module CLI.
5. Update canonical references, current state and tasks; record a matched N1-control/N2-trial manual handoff, then commit the verified milestone locally.

# Acceptance Criteria

- [x] New user observations are recorded with exact interface/variant attribution and prompt-versus-fatigue limits.
- [x] Fuel-mask research establishes an analogous bounded candidate or a precise reason to defer.
- [x] Any N2 changes only the reviewed local-category bits, retaining N1 parking visibility and all other source/interaction/geometry resources.
- [x] N1 remains a reproducible control; N2 has an early unique identity, new revision and explicit replace-N1/retain-background instructions.
- [x] Focused and full checks, actual archive/source/stack audit and documentation checks pass.
- [x] No runtime success is claimed for untested N2, and all operational boundaries are preserved.

# Verification

Initial tree: clean at `1c596b9` on `codex/gas-station-car-rest-research`. Root inspected all three 5120 × 1440 screenshots and preserved unchanged copies/hashes plus the 457,425-byte game log. Root correlated B/background/N1 persistent mounts and all three screenshot/action events. No geometry or profile write occurred.

Delegation: GPT-6 Luna/high owns read-only fuel-category research; GPT-6 Luna/high owns only the navigation module and its tests for an explicit N2 variant; GPT-6 Luna/medium owns only canonical validation and station-feedback documentation. Root reviews findings and changes, owns the remaining documentation, generation, independent payload comparisons and final integration. These assignments authorize no live installation, game launch, profile change, merge or push.


**Observed locally — primary fuel-renderer evidence:** root and GPT-6 Luna/high independently inspected the pinned executable, without launching/modifying it. `/material/ui/map/gas_small_ico.mat` at VA `0x142373d80` is loaded at `0x14100ef29`; the map object's accessor is called with index 24 at `0x14100ef42`, then the material is passed to the renderer. This supersedes the initial inability to find retained category-24 evidence: it directly associates gas-small rendering with index 24. The exact unnamed accessor contract remains inferred, so the fuel visibility effect is a hypothesis until tested. Bounded excerpts and executable/installed-control fingerprints are in `local_outputs/work/2026-10-19_20-36-39/navigation-followup/fuel-engine-evidence.json` and adjacent excerpt files. The installed N1 and original A/B package hashes match the delivered artifacts.

**Implementation:** explicit `--variant parking-fuel` emits N2 NAV PARKING + FUEL r2 using the same four source/include pins and caller-declared 1.61.3.18 gate. Relative to N1, only bit 24 changes on local tiers 0–3 (`0x02685FFF` to `0x03685FFF`). The default remains N1. Root consolidated the token editor, corrected N2's control/report unknowns, and replaced a metadata-only assertion with an actual two-archive priority test. No station-planning or service/geometry module changed. N1 is disabled when N2 is enabled; the background and the selected A/B or standard map fixes remain in place.

**Verification:** all **336 tests** pass, including ten navigation tests and four additions for N2. Coverage includes an exact N1/N2 fuel-bit-only delta with world-tier/other-byte preservation, source-pinned planner behavior and invalid-variant refusal before writes, real N2 archive/metadata generation, actual whole-file precedence with both orderings and preserved include resolution. The retained six checks cover malformed/no-op data, source/include/version drift, mid-read changes, source immutability, acknowledgment, overwrite refusal and CLI. Full output is `local_outputs/work/2026-10-19_20-40-29/navigation-icons/full-tests.txt`.

Root regenerated N1 under ignored verification staging and compared complete SCS bytes: identical to the delivered N1 SHA-256 `97e36da9a440299ebe2f9e07b4aba65bd5f92dfda6e9b94a221865dbfd32c362`. Actual N2 CRC and the four-member allowlist pass. Its single gameplay member differs from N1 by only the four bit-24 tokens and restores exactly to the pinned source after reversing both category bits. Includes and every non-mask SII attribute are unchanged. Both virtual background + A/B + N2 stacks preserve all 25 gameplay members per control byte-for-byte. Payload evidence is `local_outputs/work/2026-10-19_20-40-29/navigation-icons/payload-audit.json`.

N2 is `local_outputs/generated/2026-10-19_20-40-29/n2-nav-parking-fuel-north-america-background-5.3-ats-1.61-r2-experimental.scs` (8,295 bytes), SHA-256 `db60ff4d21e4ddbd58f7b517f41465385e4dd35dde7808bedf17d6239bc205bd`. N1 and old outputs remain untouched. The handoff identifies N2 at the beginning of title/filename/description, says replace N1 only, retain background, and compare the same car/location/zoom with parking/prompt preservation. Fuel runtime remained unverified at candidate handoff; the subsequent user result below confirms visibility at its tested scope. Broader checks remain in TASK-0007.

Root reviewed the delegated implementation, tests and documentation, independently found the bounded renderer lead and repeated its inspection, generated/audited the actual package and owns final integration. Screenshots show the HUD and one engine-off prompt; the user's vehicle-navigation success and both-prompt report are attributed separately. No agent launched the game, installed a package, changed a profile/input/geometry, merged, pushed or published. Documentation links/hashes/status and whitespace are checked before commit; code tests need no repetition after documentation-only closure.

**Documented — subsequent first-hand user confirmation, 2026-10-19:** with N2, both fuel and parking icons are now clearly visible in Mustang navigation. This confirms the initial fuel-visibility outcome while retaining parking at the reported site/interface scope. [Dated validation](../../reference/VALIDATION_RESULTS.md#2026-10-19-n2-fuel-and-parking-icons-confirmed-in-mustang-navigation). No new screenshots, exact zoom settings, all-map/vehicle coverage, completed refueling/rest, fatigue, truck or reload results were supplied. The original N2 archive and generation-time `in_game_verified: false` report remain unchanged; this later record carries user acceptance. Repeating the initial N2 icon check is not requested.

Root integrated the user result with the canonical validation/navigation references and current state; GPT-6 Luna/medium owned the bounded reference update. This documentation-only follow-up checks links, task/evidence consistency, package hash and whitespace rather than rerunning unchanged utility tests.

# Links

- [Navigation icon evidence and handoff](../../reference/CAR_PARKING_NAVIGATION_ICONS.md)
- [Gameplay validation](../../reference/VALIDATION_RESULTS.md)
- [Station feedback](../../reference/GAS_STATION_CAR_REST_FEEDBACK_2026_10_19.md)
- [TASK-0041](../done/TASK-0041-refactor-station-parking-and-investigate-navigation-icons.md)
- [Runtime validation](../active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md)
