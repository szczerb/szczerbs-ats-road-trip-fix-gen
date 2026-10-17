# SCS archives and definitions

Inspected: 2026-10-17. Applies to the shared ATS/ETS2 data and mod packaging conventions documented by SCS; it is not a complete ATS 1.61 or Road Trip schema. **Documented** means an SCS source says it; **observed locally** means verified in local game or mod files; **hypothesis** needs a test; **unknown** has no sufficient evidence yet. The local-format observation below comes from the inventory's targeted inspection; no full extraction or independent game-data inspection was performed for this note.

## How the pieces fit

- **Documented:** SCS's Game Archive Packer creates and extracts `.scs` packs. ATS/ETS2 1.50 introduced HashFS v2; SCS says older formats remain supported for mods, but can load less efficiently. The current packer creates v2 and extracts v1/v2. [Game Archive Packer](https://modding.scssoft.com/wiki/Documentation/Tools/Game_Archive_Packer)
- **Documented:** A mod package can be a directory or a ZIP archive with `.scs` or `.zip` extension. `manifest.sii` supplies display metadata and can declare compatible game versions and DLC dependencies. From ATS/ETS2 1.48, a package may use `base` plus `dlc_` named parts; `base` mounts generally while DLC parts mount only when the named DLC is owned. A file merely being present in a package therefore does not prove it is mounted for a particular player. [Mod manager](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager)
- **Documented:** Definitions are plain-text `.sii` unit files, even though SII also has a binary representation. An `.sii` starts with `SiiNunit`, contains named unit objects and attributes, and may use `@include` to bring in `.sui` fragments. An `.sui` is an included fragment without the `SiiNunit` wrapper. Unit names, references, arrays, and token constraints matter when comparing definitions. [Units](https://modding.scssoft.com/wiki/Documentation/Engine/Units)
- **Observed locally (2026-10-17):** the supplied ZIP mods contain both stored and DEFLATE entries; `.scs` does not mean uncompressed ZIP. The Reforma packages instead have HashFS v2 headers. See [exact signatures and counts](./LOCAL_INPUT_INVENTORY.md).

## Official tools and unit syntax

**Documented:** the packer accepts `scs_packer extract archive.scs -root <directory>` and `scs_packer create archive.scs -root <directory>`. Creation compresses supported files by default; `-nocompress` disables compression. The same SCS page links the older extraction-only tool and version-specific downloads. These are documented command forms, not commands run or tools installed during initialization. Match the selected binary to the recorded game/archive versions before relying on it. [Game Archive Packer](https://modding.scssoft.com/wiki/Documentation/Tools/Game_Archive_Packer)

**Documented:** unit names consist of dot-separated tokens with a maximum of 12 characters per token; tokens use lowercase letters, digits, and underscores. Arrays may use `attribute[]: value` or indexed entries. SCS requires `@include` at the beginning of its own line without leading whitespace. Include resolution and named unit references must be preserved when comparing definitions; a fragment alone may lack its enclosing context. [Units](https://modding.scssoft.com/wiki/Documentation/Engine/Units)

## What a compatibility generator must establish

1. **Project recommendation:** Record the target ATS version and owned DLC before selecting mounted package parts. **Documented:** manifests can restrict game versions and package mounts can depend on owned DLC. Those declarations alone do not demonstrate working Road Trip jobs or car refueling. [Mod manager](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager)
2. **Hypothesis:** A small compatibility mod may supply definitions at paths used by the installed map mod and game. Record every source archive, virtual path, and mounted condition before generating an output. Verify the effective result in game; do not infer it from a single archive listing.
3. **Unknown:** The exact precedence among a particular ATS 1.61 game build, DLCs, map packages, and compatibility packages has not been verified here. Do not assume that adding a file with a familiar name merges individual unit attributes. Compare the effective files at the intended load order.

The archive inventory and inspection limits belong in [Local input inventory](./LOCAL_INPUT_INVENTORY.md). Follow [Map structure and compatibility](./MAP_STRUCTURE_AND_COMPATIBILITY.md) for map data, [Economy and courier jobs](./ECONOMY_AND_COURIER_JOBS.md) for job definitions, and [Passenger-car refueling](./PASSENGER_CAR_REFUELING.md) for station behavior.
