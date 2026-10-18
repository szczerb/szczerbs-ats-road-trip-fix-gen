# ADR-0014: Shorten generated map package filenames

## Context

**Observed locally — ATS 1.61.3.18, 2026-10-18:** the r7 Western Canada ProMods Connections fix has a valid JPEG, but its icon-cache write fails. The game's cache basename hex-encodes the complete package stem, doubling its length. The normal mapping from the logged home gives a 263-character path including NUL. A legacy Win32 path limit is a strong hypothesis; runtime confirmation is pending. [Incident evidence](../../incidents/INC-0001-connector-icon-cache/README.md).

The user also requires full Alaska Expansion and Western Canada Expansion identities for distribution clarity. Truncating map names would weaken that requirement. [TASK-0027](../../tasks/done/TASK-0027-clarify-expansion-map-branding.md).

## Decision

Accepted 2026-10-18. Combined map outputs use `szczerbs-road-trip-map-fix-<full-map-slug>-1.61-rN-experimental.scs`, replacing the redundant `map-compatibility-fix` filename prefix. Keep full source-map names, author branding, game version, revision and experimental suffix. Manifest titles remain `szczerb's Road Trip Map Compatibility Fix for <full map name>`.

Known source profiles identify Alaska Expansion and Western Canada Expansion by those full labels; their icon presets and priority text agree. Generic regional labels do not auto-select those maps' artwork. The separate connector identity remains Western Canada ProMods Connections.

## Consequences

The r8 connector's derived cache path drops to 235 characters including NUL. Regression checks cover the known connector filename/cache budget, embedded icon and canonical source labels; gameplay planners and source dependency behavior stay unchanged. Fuel-only/rest-only filename families and courier names retain their existing patterns.

This is a reversible filename mitigation, not a universal long-path guarantee for every username, home location or custom map label. No filesystem settings or cache files are modified. Previous package archives retain their historical names. [R8/r3 handoff](../../reference/MOD_METADATA_MAP_NAMES_1_61_R8_R3.md) records the exact payload comparison and pending image-display check.
