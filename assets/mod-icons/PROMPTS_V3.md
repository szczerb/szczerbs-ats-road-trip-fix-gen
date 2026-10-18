# Corrected Ford vehicle artwork prompts

Created: 2026-10-18. Built-in imagegen edit requests, one call per proposal. Edit target: inspected `local_outputs/work/2026-10-18_15-24-10/artwork/m2a-original.png`. User requested M2A's location and parking direction, a correct DLC-era Crown Victoria and a second four-car version adding the DLC-era Bronco. Prompts below are exact. New large originals belong to `local_outputs/work/2026-10-18_16-10-22/artwork/`; tracked small JPEGs use final size/format export only.

**Observed locally — ATS 1.61.3.18, inspected 2026-10-18:** installed Ford definition series are Crown Victoria 2006 (`ford.victoria_06`, `@@series_ford_crown_victoria_2006@@`) and Bronco 2024 (`ford.bronco_24`, `@@series_ford_bronco_2024@@`). [Existing extraction evidence](../../docs/reference/COURIER_RESEARCH_FINDINGS.md).

**Documented — SCS, inspected 2026-10-18:** [Crown Victoria vehicle article](https://blog.scssoft.com/2025/11/ats-road-trip-ford-car-pack-crown.html), published 2025-11-29, explicitly describes the in-game 2006+ version. [Official Road Trip page](https://americantrucksimulator.com/roadtrip.php) lists Crown Victoria '06 and Bronco '24. Older announcement/release copy calls Bronco 2023; this artwork follows the installed series token and current model selector. Prior M2A/M2B prompts intentionally specified the wrong 1956 Victoria; that was the agent's error, not a user request. Preserve those prompts as history rather than silently rewriting them.

## M2C

Export: `proposals-v4/m2c-3-fords.jpg`.

```text
Use case: precise-object-edit. Edit target: the supplied M2A navy/cream/teal FUEL & REST FIX illustration with three cars seen from above and behind. Preserve exactly this location, camera angle, parking direction, pump on right, blue P sign on left, navy text bands, cream border, teal accents, top title "FUEL & REST FIX" and bottom label "ATS EXPANSION". Replace ONLY the middle red-and-cream 1950s car with a solid red 2006 Ford Crown Victoria sedan, matching the actual Road Trip DLC: late Panther-platform four-door full-size sedan, smooth modern 2000s body, long flat trunk, wide horizontal red tail lamps, black rear trim, ordinary civilian vehicle without police equipment. Absolutely NO 1950s styling, tailfins, continental spare wheel, chrome extravagance or two-tone paint on this sedan. Keep the blue 1967 Mustang fastback at left and green 2023 F-150 pickup at right unchanged. All three cars face into their bays toward the upper/background side, rear bumpers visible toward viewer. Keep wheel stops ONLY at the far/front ends of bays; leave the foreground behind all cars completely unobstructed for backing out. One finished landscape 276:162 aspect thumbnail, typography unchanged, no extra words or vehicles, preserve high-quality friendly illustration and safe margins.
```

## M2D

Export: `proposals-v4/m2d-4-fords.jpg`.

```text
Use case: precise-object-edit. Edit target: supplied M2A navy/cream/teal FUEL & REST FIX station illustration. Produce a FOUR-vehicle variant of this same location and same elevated rear three-quarter camera angle: everyone faces into the parking bays toward the upper/background side, rear bumpers toward viewer. Keep the original pump on the right, blue P parking sign left, landscaping, navy text bands, cream border, teal accents, top headline exactly "FUEL & REST FIX", bottom label exactly "ATS EXPANSION". Re-space the central parking area into exactly four distinct white-lined bays, all with free unobstructed reversing space behind them. Left to right: blue 1967 Ford Mustang fastback; solid red 2006 Ford Crown Victoria four-door sedan with long flat trunk, 2000s smooth body and horizontal red tail lamps; orange 2024 Ford Bronco four-door modern boxy off-road SUV with black hardtop and rear-mounted spare tire; green 2023 Ford F-150 pickup with visible open bed. The Crown Victoria must be the 2006+ Panther generation, NEVER a 1950s Fairlane; Bronco must be the current 2024 generation, NEVER a classic Bronco. Preserve these distinct silhouettes and sensible relative sizes without vehicle overlap. Wheel stops only at far/front ends of bays, none behind the rear bumpers or blocking exits. Maintain polished friendly illustrated style, readable large shapes at 276x162, landscape 276:162 aspect, no added words, no fifth vehicle, no watermarks.
```

