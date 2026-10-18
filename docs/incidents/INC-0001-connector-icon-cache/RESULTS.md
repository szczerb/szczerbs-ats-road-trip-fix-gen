# Results and limits

**Observed locally — 2026-10-18:** r7's embedded icon is valid and the game reports cache-write failure. The hex filename is the full package stem; the proposed shorter filename reduces the encoded portion by 28 characters. The r8 connector still embeds the same valid JPEG, with a correct manifest target.

**Documented — Microsoft Learn, inspected 2026-10-18:** [Maximum Path Length Limitation](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation) describes the classic 260-character Win32 path limit including NUL, and requirements for longer paths. This supports a possible mechanism; it does not establish the ATS executable's API/opt-in behavior.

**Hypothesis:** the old derived 263-character path including NUL exceeds that legacy budget and causes the cache-copy failure. Shortening to 235 including NUL should avoid this particular issue. Longer home paths, access restrictions or other cache problems are not ruled out.

**Unknown:** whether the new filename restores the picture in the user's game. Keep this incident open until the user confirms. No cache reset, file deletion, system-setting change or live mod installation occurred.

See [r8/r3 static checks](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md) and the [manual checklist](../../reference/MANUAL_TEST_CHECKLIST.md).
