# Local publication-history cleanup

**Documented — user authorization, 2026-10-18 (Europe/Warsaw):** the sole contributor reports an external project backup and explicitly authorizes a local history rewrite, personal-path neutralization and GitHub commit attribution. Publication, remote configuration, push, game launch and changes to ignored inputs/existing outputs are excluded. This supersedes the earlier recommendation to leave the intentional placeholder identity unchanged; that earlier address was not a leaked private mailbox.

## Scope and method

**Observed locally — 2026-10-18:** the initial checkout was clean on `codex/overnight-test-mods`. There were six branches, two Codex capture refs pointing directly to trees, one worktree, no tags, stashes or remotes, and 35 reachable commits. All refs were inventoried before modification. No unknown ref or worktree was deleted. Inspection of the backed-up Git administrative files also found `ORIG_HEAD`; it was preserved and mapped from pre-cleanup commit `698ba9a959099cd314969cc5824563b6068add4b` to `8a5e978e05890231733ca34c3a5cced3f3951b2d`. No other inspected recovery/operation pseudo-ref files existed. The current branch remains the same; `master` retains its earlier research position rather than being advanced to the latest implementation.

The rewrite used [git-filter-repo v2.47.0](https://github.com/newren/git-filter-repo/tree/v2.47.0) in an isolated Git copy, with commit-message hash rewriting disabled and empty/degenerate commit pruning disabled. Its downloaded script SHA-256 is `67447413e273fc76809289111748870b6f6072f08b17efe94863a92d810b7d94`. The first staging attempt failed because a callback lacked the metadata argument; the corrected second staging copy passed all checks before any original ref changed. No hand-written rebase sequence was used.

Git fast-export skips tree-valued refs. Both Codex trees were therefore recursively rebuilt using the same reviewed content transformation, preserving filenames, modes and unchanged blobs. After verification, cleaned objects were imported and all eight refs were updated in one Git ref transaction with checks against their original values. Repository-local configuration now selects `szczerb <39603356+szczerb@users.noreply.github.com>`; global configuration is unchanged. This prepares email-based GitHub attribution; no GitHub account or server-side contribution view was accessed.

| Branch | Pre-cleanup tip | Rewritten tip, before the new cleanup-record commit |
| --- | --- | --- |
| `codex/courier-reporting` | `d96e10bd788c8f4f747d466bf1188e2d74c270e3` | `69eb3de5d8361a68b03054e43d5d2ec8d01c72d6` |
| `codex/map-wide-fuel-fixes` | `defa832a104e7e15dd9468a1f0ed78f940419ec1` | `1d4551056703edbfb1792fc4b4b886b241ce1e8f` |
| `codex/overnight-test-mods` | `179e24dbf67a71cc8ff93c55516dcebccb692ebf` | `825e1240916d90c4be77cbdefd41edde9132ce1a` |
| `codex/road-trip-compatibility-research` | `f5162ea4c0f22a9a44797c1358b9906768f48a1c` | `b79fbe7989c49e042c37f0cdd37d412ffedfbb9c` |
| `codex/starter-area-sample` | `9f8c1b71db56d27289245c8f471c106999f3c3e7` | `21fae31279402911482e0992ba7482661078e722` |
| `master` | `f5162ea4c0f22a9a44797c1358b9906768f48a1c` | `b79fbe7989c49e042c37f0cdd37d412ffedfbb9c` |

| Preserved local Codex ref | Old tree | Cleaned tree |
| --- | --- | --- |
| `refs/codex/turn-diffs/captures/1792329798376/33e9b8bd-0561-447e-a1db-2e789fd79740/base` | `75320cf674d9a4b0255c97fe73c2e6b90dea634d` | `56c9ead4e9a385cc22cd55d63abe96957b805f0a` |
| `refs/codex/turn-diffs/captures/1792348239321/8345f187-f088-4b88-9742-c4110d757b2c/base` | `7753a6172a91978a46f10dcda1e07e94c895a7b6` | `cbb0d1120cc5126fb8bf6fc931387a3ac6ec45e3` |

Codex capture refs are local application bookkeeping, not proposed publication branches. They were sanitized as an additional safeguard rather than deleted. No `refs/original`, backup branch, remote-tracking ref or replacement ref was created in the working repository. Old reflogs/unreachable history are removed only after the verified backup exists; recovery uses that excluded backup.

## Content changes and preserved evidence

- Absolute personal-project links into ignored outputs became plain project-relative artifact identifiers, explicitly labeled local and excluded from Git. A public clone does not contain those artifacts.
- Screenshot locations became `<LOCAL_SCREENSHOT_PATH>`, `<LOCAL_SCREENSHOT_DIR>` or `<LOCAL_ATS_SCREENSHOT_DIR>`; filenames, hashes and observation limits remain.
- The Windows cache-path fixture uses `guest`, preserving the original five-character account component and complete path length. No production code changed. Generic engine paths such as `/home/cache/mod_icons/` remain useful evidence.
- Historical prose calls the old email a legacy placeholder rather than printing it or incorrectly recasting it as the new address. The earlier correction of the privacy finding remains explicit. Author and committer emails were changed only when they exactly matched the sole contributor's former address.
- All dates (including timezone offsets), names, commit messages, parent relationships, file modes and path inventories are preserved. Only approved blob content, identity email fields and the necessarily resulting object IDs differ.
- `LICENSE`, `LICENSING.md`, `THIRD_PARTY_NOTICES.md`, package licensing metadata, production modules and ignore rules retain their exact baseline bytes. AGPL-3.0-only and separate upstream rights remain. C# consultation, parser comparisons, uncertainty and the correction from upstream commit to tree identity remain documented.

## Commit identifiers

The tracked [complete 35-row old-to-new mapping](HISTORY_CLEANUP_COMMIT_MAP.tsv) is the durable reference. It maps **this repository's commits only**. Both columns are full commit IDs; the old column is explicitly a pre-cleanup identifier and does not retain the old commit object. Historical reports keep their original baseline/introduction identifiers with a history note directing readers here. Resolve an old abbreviated ID against the old column, then use the new full ID with `git show`.

Upstream commit/tree/blob IDs and input/output SHA-256 values are not rewritten. The original history remains available in the private backup for forensic comparison. The mapping intentionally excludes the new commit recording this cleanup; its identity follows the new configuration and its hash is not embedded in itself. No repeated hash-update cycle is needed.

## Backup and local evidence

All following paths are local, ignored artifacts excluded from the repository, relative to its root:

`local_outputs/work/2026-10-18_20-31-16/`

- `git-before.tar.gz`: full original `.git`, including refs, reflogs, index, config and object storage. It was extracted into `backup-verification/.git`; full fsck and exact original-ref comparison passed.
- `before.bundle`: separately verified bundle of all original refs, including both tree refs; `BACKUP_SHA256SUMS` records checksums for it, the archive and baseline JSON. The complete `.git` archive remains the authoritative backup for reflogs/unreachable objects/configuration.
- `baseline.json`, `bundle-verify.txt`, `backup-fsck.txt`: original state and backup verification. No external user backup was touched.
- `commit-map.txt`, `tree-map.json`, `pseudo-ref-map.json`, `refs-after-rewrite.txt`, `rewrite-verification.json`: mechanical maps and staged verification. The tracked TSV duplicates the commit mapping for future readers.
- `artifacts-before.json`, `artifacts-verification.json`: baseline fingerprints and final comparison for every pre-existing file beneath `local_inputs/` and `local_outputs/`, excluding only this new run directory.
- `neutralize.py`, `rewrite.py`, `verify-rewrite.py`, `integrate.py`, staging copies and test/audit logs: local reproducibility and recovery evidence. These contain the original personal strings by design and must remain excluded.

Neither backup files nor staging repositories are referenced by a live backup ref. Ordinary pushes transfer reachable selected refs, not ignored files or reflogs; nevertheless publish only explicitly selected reviewed branch/tag refs. Do not upload this working directory or mirror its ignored backup directories. No publication command was run.

## Verification and remaining publication choices

**Observed locally — 2026-10-18:** root checked the staged transformation across all 35 commits, 614 reachable blobs and both tree refs. Exact commit-message/header comparison confirms date/name/topology preservation. An independent GPT-6 Luna/medium agent repeated the all-ref path/email, metadata, topology and protected-file comparison read-only: zero mismatches. All 705 historical production-file instances were unchanged. Seven historical test-file instances differ only by the equal-length synthetic account substitution. Forty-eight distinct changed blob pairs exactly match the reviewed neutralizer.

All 266 authored tests passed before rewriting. All 266 tests also passed after rewriting (2.144 seconds). Rehashing all 73,683 pre-existing ignored files confirmed identical contents, sizes, modification times and path inventory. Live reflogs were expired and unreachable objects pruned after backup validation; all 35 original commit objects are absent from the live store. The all-stored-object path/email scan and full Git fsck pass. Documentation checks and post-commit integrity results are recorded in [TASK-0032](../tasks/done/TASK-0032-clean-publication-history-and-git-identity.md) and the ignored run logs. The scan covers tracked filenames, reachable blobs, commit headers/messages and all existing refs; it does not claim an exhaustive personal-data or image-content privacy audit beyond those concrete path/email checks.

Before future publication, choose the intended default/public branches explicitly: the latest implementation, AGPL files and cleanup record are on `codex/overnight-test-mods`, while `master` still denotes the early research snapshot. Review the remaining [artwork/provenance and generated-resource rights](PUBLIC_REPOSITORY_REVIEW.md) at the appropriate release scope; sanitization supplies no new rights clearance. Server-side attribution can be confirmed only after separately authorized publication. Existing gameplay unknowns remain in TASK-0007; this cleanup does not require running the game.
