# Debugging plan

1. Verify manifest-relative icon target, JPEG dimensions/decoding, ZIP CRC and exact generated version.
2. Prefer dated log evidence over a current directory listing when they differ. Identify failure before the invalid-dimensions message.
3. Decode the cache basename and derive its path budget under the logged home/VFS mapping.
4. Shorten the common filename prefix while retaining full map identity, game version, revision and experimental suffix. Check every known generated map filename and connector icon packaging.
5. Hand off r8 for the user to confirm icon visibility. If it still fails, collect fresh relevant cache errors and inspect the resulting path/write conditions; do not delete cache or change Windows settings automatically.

**Unknown:** the exact Win32 API used by ATS, long-path opt-in and the physical cache state. These are not inferred solely from the 8x8 fallback report. No game launch/profile operation is part of this investigation.
