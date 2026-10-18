# Problem statement

**Documented — user report, 2026-10-18:** the fix for Western Canada ProMods Connections has no picture in Mod Manager. Expected: the approved M2D family icon with the connector label.

**Observed locally — log created 2026-10-18 16:54:43, inspected 2026-10-18:** `game.log.txt` records the r7 fix mounted from User mods at lines 1321–1322. Lines 1325–1326 report a `create_truncate` failure for `/home/cache/mod_icons/<hex>.jpg` and inability to copy the package's `mod_icon.jpg`. Line 1328 then reports required dimensions 276x162, actual 8x8. This is Mod Manager discovery evidence, not proof of active gameplay load order.

The generated r7 archive's manifest points to the existing `mod_icon.jpg`; CRC, JPEG dimensions and FFmpeg decoding pass. Historical r4 lacked an icon entirely, but the dated failing session explicitly identifies r7. The earlier iconless version alone does not explain this log.

Large evidence remains ignored: `local_outputs/work/2026-10-18_17-04-30/connector-icon-evidence.json`, original game log path and source archive hashes. No game/cache files were modified.
