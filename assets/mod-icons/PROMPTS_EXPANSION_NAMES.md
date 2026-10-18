# Expansion map-name footer edits

**History note:** repository commit IDs in this document are pre-cleanup identifiers; use the [old-to-new mapping](../../docs/reference/HISTORY_CLEANUP.md#commit-identifiers). Upstream object IDs and artifact checksums are unchanged.

Created and inspected: 2026-10-18. The user explicitly requests Western Canada Expansion and Alaska Expansion in artwork/metadata, distinguishing these supplied sources from unrelated maps of the same regions. Built-in imagegen, four footer-only edit calls. Prior target paths below were read from commit `93255ed`; exact input JPEG copies are preserved under ignored `local_outputs/work/2026-10-18_17-04-30/artwork/references/`. Large originals and generation records are in that artwork run. Final FFmpeg export changes only size/format (276x162, Lanczos, JPEG quality 2, yuvj444p). Original selected M2D composition and historical green fuel-only composition are retained.

## alaska-expansion

Edit target at generation time: `assets/mod-icons/map-compatibility/alaska.jpg`. Export: `map-compatibility/alaska-expansion.jpg`.

```text
Use case: text-localization. Edit target: supplied user-selected M2D navy/cream/teal fuel/parking mod icon. Change ONLY the bottom map-name label to exactly "ALASKA EXPANSION". A slash in this requested label means two centered lines, not a printed slash. Preserve the headline "FUEL & REST FIX", four Ford vehicles, blue P sign, pump, parking direction and bays, colors, cream frame and all other artwork. The full word EXPANSION is essential to identify the specific source map. Fit bold legible lettering into the existing footer band with safe margins; do not cover art or alter headline. Keep landscape 276:162 aspect. No added words or watermarks. One finished thumbnail.
```

## western-canada-expansion

Edit target at generation time: `assets/mod-icons/map-compatibility/western-canada.jpg`. Export: `map-compatibility/western-canada-expansion.jpg`.

```text
Use case: text-localization. Edit target: supplied user-selected M2D navy/cream/teal fuel/parking mod icon. Change ONLY the bottom map-name label to exactly "WESTERN CANADA / EXPANSION". A slash in this requested label means two centered lines, not a printed slash. Preserve the headline "FUEL & REST FIX", four Ford vehicles, blue P sign, pump, parking direction and bays, colors, cream frame and all other artwork. The full word EXPANSION is essential to identify the specific source map. Fit bold legible lettering into the existing footer band with safe margins; do not cover art or alter headline. Keep landscape 276:162 aspect. No added words or watermarks. One finished thumbnail.
```

## alaska-expansion-c

Edit target at generation time: `assets/mod-icons/alaska-c.jpg`. Export: `alaska-expansion-c.jpg`.

```text
Use case: text-localization. Edit target: supplied historical selected green gas-station mod icon. Change ONLY the bottom map-name label to exactly "ALASKA EXPANSION". A slash in this requested label means two centered lines, not a printed slash. Preserve the headline "GAS STATIONS FIX", the central pump, four cars, green/cream colors, border and all other artwork. The full word EXPANSION is essential to identify the specific source map. Fit bold legible lettering into the existing footer band with safe margins; do not cover art or alter headline. Keep landscape 276:162 aspect. No added words or watermarks. One finished thumbnail.
```

## western-canada-expansion-c

Edit target at generation time: `assets/mod-icons/western-canada-c.jpg`. Export: `western-canada-expansion-c.jpg`.

```text
Use case: text-localization. Edit target: supplied historical selected green gas-station mod icon. Change ONLY the bottom map-name label to exactly "WESTERN CANADA / EXPANSION". A slash in this requested label means two centered lines, not a printed slash. Preserve the headline "GAS STATIONS FIX", the central pump, four cars, green/cream colors, border and all other artwork. The full word EXPANSION is essential to identify the specific source map. Fit bold legible lettering into the existing footer band with safe margins; do not cover art or alter headline. Keep landscape 276:162 aspect. No added words or watermarks. One finished thumbnail.
```
