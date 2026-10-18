# Selected M2D map-label prompts

Created and inspected: 2026-10-18. User explicitly selected M2D with four Ford vehicles and confirmed both corrected previews display in chat; the local HTML gallery also works. The selection replaces the initial M2 preset for combined map fixes. Courier J3B remains a favorite with a key-fob reservation, not approved; J1B-based r1 remains unchanged.

Built-in imagegen, six footer-only edit requests below. Input: inspected `local_outputs/work/2026-10-18_16-10-22/artwork/m2d-4-fords-original.png`. ATS Expansion reuses the exact selected export. Other map labels are individual reviewed edits. Large originals and machine provenance: ignored `local_outputs/work/2026-10-18_16-16-22/artwork/`. Final FFmpeg export performs format/downscale only (276x162, Lanczos, JPEG quality 2, yuvj444p). Runtime generation reuses tracked JPEG bytes without LLM calls.

Original four-car prompt and model-year sources: [corrected Ford prompts](PROMPTS_V3.md).

## REFORMA

Export: `map-compatibility/reforma.jpg`.

```text
Use case: text-localization. Edit target: the supplied user-selected M2D finished navy fuel/parking mod illustration. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "REFORMA". Where slash appears in requested label, render two centered lines instead of slash. Preserve all other artwork: headline "FUEL & REST FIX", navy/cream/teal palette, frame, pump, blue P sign, station location, elevated rear camera and four parking bays with blue 1967 Mustang, red 2006 Crown Victoria sedan, orange 2024 Bronco with rear spare tire, green 2023 F-150 pickup. Keep all four cars facing the far/front ends of the bays, wheel stops there only and clear reversing space behind cars. Do not change, remove, rotate or add vehicles or objects. Preserve landscape 276:162 aspect and safe margins. Footer bold and legible at 276x162. No added words or other changes.
```

## PROMODS CANADA

Export: `map-compatibility/promods-canada.jpg`.

```text
Use case: text-localization. Edit target: the supplied user-selected M2D finished navy fuel/parking mod illustration. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "PROMODS CANADA". Where slash appears in requested label, render two centered lines instead of slash. Preserve all other artwork: headline "FUEL & REST FIX", navy/cream/teal palette, frame, pump, blue P sign, station location, elevated rear camera and four parking bays with blue 1967 Mustang, red 2006 Crown Victoria sedan, orange 2024 Bronco with rear spare tire, green 2023 F-150 pickup. Keep all four cars facing the far/front ends of the bays, wheel stops there only and clear reversing space behind cars. Do not change, remove, rotate or add vehicles or objects. Preserve landscape 276:162 aspect and safe margins. Footer bold and legible at 276x162. No added words or other changes.
```

## WESTERN CANADA

Export: `map-compatibility/western-canada.jpg`.

```text
Use case: text-localization. Edit target: the supplied user-selected M2D finished navy fuel/parking mod illustration. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "WESTERN CANADA". Where slash appears in requested label, render two centered lines instead of slash. Preserve all other artwork: headline "FUEL & REST FIX", navy/cream/teal palette, frame, pump, blue P sign, station location, elevated rear camera and four parking bays with blue 1967 Mustang, red 2006 Crown Victoria sedan, orange 2024 Bronco with rear spare tire, green 2023 F-150 pickup. Keep all four cars facing the far/front ends of the bays, wheel stops there only and clear reversing space behind cars. Do not change, remove, rotate or add vehicles or objects. Preserve landscape 276:162 aspect and safe margins. Footer bold and legible at 276x162. No added words or other changes.
```

## ALASKA

Export: `map-compatibility/alaska.jpg`.

```text
Use case: text-localization. Edit target: the supplied user-selected M2D finished navy fuel/parking mod illustration. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "ALASKA". Where slash appears in requested label, render two centered lines instead of slash. Preserve all other artwork: headline "FUEL & REST FIX", navy/cream/teal palette, frame, pump, blue P sign, station location, elevated rear camera and four parking bays with blue 1967 Mustang, red 2006 Crown Victoria sedan, orange 2024 Bronco with rear spare tire, green 2023 F-150 pickup. Keep all four cars facing the far/front ends of the bays, wheel stops there only and clear reversing space behind cars. Do not change, remove, rotate or add vehicles or objects. Preserve landscape 276:162 aspect and safe margins. Footer bold and legible at 276x162. No added words or other changes.
```

## REFORMA + OTHERMAPS PATCH

Export: `map-compatibility/reforma-othermaps-patch.jpg`.

```text
Use case: text-localization. Edit target: the supplied user-selected M2D finished navy fuel/parking mod illustration. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "REFORMA / OTHERMAPS PATCH". Where slash appears in requested label, render two centered lines instead of slash. Preserve all other artwork: headline "FUEL & REST FIX", navy/cream/teal palette, frame, pump, blue P sign, station location, elevated rear camera and four parking bays with blue 1967 Mustang, red 2006 Crown Victoria sedan, orange 2024 Bronco with rear spare tire, green 2023 F-150 pickup. Keep all four cars facing the far/front ends of the bays, wheel stops there only and clear reversing space behind cars. Do not change, remove, rotate or add vehicles or objects. Preserve landscape 276:162 aspect and safe margins. Footer bold and legible at 276x162. No added words or other changes.
```

## WCE + PROMODS + CONNECTIONS

Export: `map-compatibility/western-canada-promods-connections.jpg`.

```text
Use case: text-localization. Edit target: the supplied user-selected M2D finished navy fuel/parking mod illustration. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "WCE + PROMODS / CONNECTIONS". Where slash appears in requested label, render two centered lines instead of slash. Preserve all other artwork: headline "FUEL & REST FIX", navy/cream/teal palette, frame, pump, blue P sign, station location, elevated rear camera and four parking bays with blue 1967 Mustang, red 2006 Crown Victoria sedan, orange 2024 Bronco with rear spare tire, green 2023 F-150 pickup. Keep all four cars facing the far/front ends of the bays, wheel stops there only and clear reversing space behind cars. Do not change, remove, rotate or add vehicles or objects. Preserve landscape 276:162 aspect and safe margins. Footer bold and legible at 276x162. No added words or other changes.
```

