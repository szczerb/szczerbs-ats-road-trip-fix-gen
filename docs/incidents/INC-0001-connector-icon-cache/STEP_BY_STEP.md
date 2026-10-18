# Investigation sequence

1. Root/Luna inspected the generated r7 connector fix: icon target present, 276x162 JPEG, SHA/CRC/decoding valid.
2. An initial directory listing contained source map files but no generated fixes. This was inconclusive; the subsequent dated log explicitly showed r7 discovery. The directory snapshot is not proof of what Mod Manager loaded earlier.
3. The log shows icon-cache creation/copy failure preceding the 8x8 message. Replacing a valid JPEG alone would not address that evidence.
4. The cache basename hex-decodes to the complete 96-character r7 archive stem. `/home` is treated as the game's VFS home alias; appending another literal physical `home` directory was a rejected path-calculation interpretation.
5. Under the normal alias mapping to the logged home, the derived old path is 262 characters (263 including NUL). Removing `compatibility-` from the combined filename reduces the derived connector path to 234 characters (235 with NUL). Current snapshot cache directories were absent, so this physical mapping is a derivation rather than an observed existing cache file.
6. Root added regression coverage for the shorter known connector filename, declared embedded icon and cache-path budget. Full map identities remain in filenames and manifests.
7. Seven r8 packages were prepared without gameplay regeneration. The courier r3 archive is copied unchanged. Final independent archive checks are recorded in the handoff.

Future user reproduction/confirmation: use the copied test setup and r8 fix directly above its connector, disable the older fix, open Mod Manager and inspect its image. If missing, preserve the new log before another session. No automated installation or reproduction was performed.
