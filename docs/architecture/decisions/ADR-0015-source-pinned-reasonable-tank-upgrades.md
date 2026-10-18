# ADR-0015: Source-pinned reasonable tank upgrades

## Context

Date: 2026-10-18. The user requests a separate realistic tank upgrade mod to replace an excessive 3x-capacity mod and authorizes parallel automotive research for all four Road Trip Fords. The installed game is ATS 1.61.3.18. Credible options are an adapted 1969 20-US-gallon Mustang tank and the applicable non-hybrid F-150 36-US-gallon OEM extended-range tank. No adequately supported moderate upgrades were established for Crown Victoria or Bronco.

## Decision

Generate a separate experimental mod from an explicit four-model, source-pinned TOML policy. Select 76 L for Mustang and 136 L for F-150, rounded from the documented nominal capacities; leave Crown Victoria at 72 L and Bronco at 79 L. No multiplier or unsupported all-model increase is applied. Record fitment/year limitations and source provenance.

Override the existing two chassis resources. Change only live capacity and its displayed info line, preserving all other bytes and sibling units. Validate complete source hashes, exact version, unit identities, includes and before/after semantics; fail atomically. The moderate-policy ceiling is 1.6x; physical fitment is established by research, not by this numerical ceiling. Offer distinct analysis and explicitly experimental generation commands using timestamped artifacts. The archive carries readable scope, priority, author and game/revision metadata plus its own icon.

## Consequences

The mod represents the selected capacity on the existing chassis automatically rather than implementing a paid, separately selectable garage accessory. This keeps the initial implementation bounded; accessory UI/purchase modeling is deferred. Whole-resource priority conflicts with tank/chassis mods remain possible, so the old 3x mod must be disabled. At generation, saved fuel above the new limit and runtime capacity refresh required manual testing. The user subsequently confirmed the tank mod works and accepted internal completion on 2026-10-18; individual migration measurements remain unspecified. [Acceptance evidence](../../reference/VALIDATION_RESULTS.md#2026-10-18-tank-upgrades-accepted-internally). No game/profile writes, installations, tank visuals, consumption adjustments or existing map/courier package repacking are part of this increment.

See [research and commands](../../reference/REASONABLE_GAS_TANK_UPGRADES.md), [policy](../../examples/reasonable-gas-tank-upgrades.toml) and [TASK-0028](../../tasks/done/TASK-0028-build-reasonable-gas-tank-upgrades.md).
