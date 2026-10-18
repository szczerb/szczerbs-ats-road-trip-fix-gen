# Fuel/rest and courier artwork prompts

Created and inspected: 2026-10-18. Built-in imagegen; no CLI/API fallback. One call per asset. Prompts below are the exact submitted requests. Large source PNGs are preserved in ignored `local_outputs/work/2026-10-18_15-24-10/artwork/`. Tracked exports are format/downscale-only FFmpeg JPEGs (276x162, Lanczos, quality 2, yuvj444p).

**Documented — user choice:** M2 (navy bands, three parked cars) is selected for the next map batch. M2A/M2B are requested Ford-vehicle alternatives; no substitution has been approved. Courier J1B is provisional while the user compares J1B/J2B/J3B; the headline change to `JOB TYPES COMPAT` is explicit. J3B's filename is `proposals-v3/j4.jpg` (generation ID retained).

## Initial six proposals

### M1

```text
Use case: logo-brand. Asset type: original American Truck Simulator mod-manager thumbnail, landscape aspect 276:162. Create ONE finished icon, not a contact sheet. Simple bold flat illustration, readable at only 276 by 162 pixels, no ATS or Ford logos. Green roadside-sign design with cream typography, rounded border. Large fuel pump at left, clear blue European-style parking sign with a large white P at right, two small passenger cars centered below. Top text verbatim "FUEL & REST FIX"; footer text verbatim "ATS EXPANSION". The parking P must be clearly separate from the title. Clean high contrast, few large shapes, balanced wide composition, professional friendly utility-mod branding. No extra words, watermarks or tiny detail. Keep all text and objects inside safe margins.
```

### M2

```text
Use case: logo-brand. Asset type: one original ATS mod manager thumbnail landscape aspect 276:162. Design ONE finished compact icon, no contact sheet. Simple flat illustrated overhead/three-quarter scene: three small colorful passenger cars parked within clear white parking-space outlines on dark asphalt, a prominent blue parking sign with white P, a large simple fuel pump beside the parking spaces. Dark navy and warm cream frame with teal accents. Readable at 276x162, bold few shapes, professional utility-mod logo. Top text verbatim "FUEL & REST FIX". Bottom footer verbatim "ATS EXPANSION". No ATS logo, no company logos, no extra text or watermark. Large readable typography and safe margins.
```

### M3

```text
Use case: logo-brand. Asset type: one original ATS game mod-manager thumbnail, landscape 276:162 aspect. ONE finished icon only. Green roadside sign with cream rounded border and large cream title, matching a simple classic American road sign. A bold fuel NOZZLE silhouette at left, a clearly recognizable blue P parking sign at right. Four small front-view passenger cars in two pairs along the middle-bottom, each standing in clearly drawn parking bays with white outlines. Flat friendly high-contrast illustration, simple large shapes readable at 276x162. Top text exactly "FUEL & REST FIX". Footer exactly "ATS EXPANSION". No ATS or Ford logos, no other words, no watermarks, no extra panels.
```

### J1

```text
Use case: logo-brand. Asset type: ONE original American Truck Simulator mod-manager thumbnail, landscape aspect 276:162. Bold flat friendly illustration readable at tiny 276x162 pixels. Deep green roadside-sign frame with warm cream typography. Main subject: a recognizable red 1967 American fastback muscle coupe seen three-quarter front, no visible logos. Beside the car are one small parcel and an envelope, suggesting practical courier deliveries that fit a car. Few large shapes, simple background, clean professional utility-mod branding. Top text exactly "MORE COURIER JOBS", can use two balanced lines if needed. Bottom footer exactly "MUSTANG". No other text, no ATS or Ford logos, no watermark. Keep text and subjects fully inside frame.
```

### J2

```text
Use case: logo-brand. Asset type: ONE finished original ATS mod-manager icon landscape 276:162 aspect. Dark navy blue background with cream title and warm amber accents. A simple cream silhouette of a classic 1967 fastback muscle car moving along a short road line; large clean envelope and small parcel icons above it, with a simple route pin/checkmark motif. This is an illustration for a mod enabling more practical courier jobs in an owned Mustang, not a racing game. Bold minimal high-contrast shapes, readable at 276x162, balanced composition and thick frame. Exact top text "MORE COURIER JOBS"; exact bottom text "MUSTANG". No logos, tiny labels, numbers or watermarks. One image only, no grid.
```

### J3

```text
Use case: logo-brand. Asset type: ONE finished landscape game mod-manager thumbnail, aspect ratio 276:162. Original friendly illustrated badge: cream/off-white background, forest green border and headline, warm red details. Side profile of a red classic 1967 fastback muscle coupe centered, with a neatly stacked small cardboard parcel, a document envelope, and a small key beside it. Clear delivery theme and a modest green check mark; spacious uncluttered design with thick shapes visible at 276x162. Top text verbatim "PRACTICAL COURIER"; footer text verbatim "MUSTANG JOBS". No Ford or ATS logo, no other text, no tiny fine print, no watermark or extra panels.
```

## Requested Ford and courier variations

All local edit targets were visually inspected before invoking imagegen.

### M2A

Input: `m2-original.png` (edit target). Export: `proposals-v3/m2a.jpg`.

```text
Use case: precise-object-edit. Edit target: supplied navy/cream/teal FUEL & REST FIX mod icon. Preserve the frame, headline "FUEL & REST FIX", footer "ATS EXPANSION", fuel pump, blue P parking sign, sunlit station, three white parking bays and existing elevated three-quarter view from behind. Replace ONLY the three generic modern cars with vehicles recognizable as the Ford Road Trip DLC models: blue 1967 Ford Mustang fastback (left), red 1956 Ford Fairlane Crown Victoria with classic chrome details (middle), green 2023 Ford F-150 pickup truck with clearly visible open cargo bed (right). Match illustrative polished style, perspective and lighting. Three vehicles in exactly three parking bays, naturally fitting without overlap, all distinct silhouettes. The Victoria is a 1950s classic, not a modern police sedan. Preserve all text verbatim, no added labels or logos. One finished landscape 276:162 aspect thumbnail with readable bold text and safe margins.
```

### M2B

Input: `m2-original.png` (edit target). Export: `proposals-v3/m2b.jpg`.

```text
Use case: precise-object-edit. Edit target: supplied navy/cream/teal FUEL & REST FIX mod icon. Create a second composition variant of this same design with the same top headline "FUEL & REST FIX", bottom label "ATS EXPANSION", navy text bands, cream border, teal accents, pump and blue P sign. Show three vehicles parked neatly in three outlined parking bays, from a slightly lower front three-quarter camera angle so the fronts and distinctive body shapes are visible: a red 1967 Ford Mustang fastback, a turquoise-and-cream 1956 Ford Fairlane Crown Victoria with rounded 1950s styling and chrome, and a dark blue 2023 Ford F-150 pickup with tall cab and bed visible. Cars should resemble those three Ford Road Trip DLC vehicles; no modern Crown Victoria police sedan. Keep the friendly polished illustrated style, balanced station setting, sunlight, large simple readable shapes and 276:162 landscape aspect. No extra text, no logos, no additional vehicles.
```

### J1B

Input: `j1-original.png` (edit target). Export: `proposals-v3/j1b.jpg`.

```text
Use case: text-localization. Edit target: supplied green-framed red classic Mustang courier icon. Replace ONLY the top headline "MORE COURIER JOBS" with exact text "JOB TYPES COMPAT". Preserve green/cream frame, bottom word "MUSTANG", red 1967 fastback, parcel and envelope, landscape, lighting, colors, positions and all other artwork unchanged. Fit the new headline in the original top band in bold cream lettering, readable at final 276x162 size, single line if possible. No other text or logos. Preserve landscape 276:162 aspect and safe margins.
```

### J2B

Input: `j2-original.png` (edit target). Export: `proposals-v3/j2b.jpg`.

```text
Use case: text-localization. Edit target: supplied navy/gold Mustang courier icon. Replace ONLY the top headline "MORE COURIER JOBS" with exact text "JOB TYPES COMPAT". Preserve navy/cream/gold palette, golden frame, bottom word "MUSTANG", cream 1967 fastback, envelope, parcel, route, pin/check mark, sun and background, all positions and other artwork unchanged. Fit new headline in original top band in bold cream lettering, readable at final 276x162 size, single line if possible. No other words or logos. Preserve landscape 276:162 aspect and safe margins.
```

### J3B

Input: `j2-original.png` (style reference). Export: `proposals-v3/j4.jpg`.

```text
Use case: logo-brand. Reference image: supplied navy/gold Mustang courier icon is style and subject inspiration, not an edit target. Create ONE distinct third option for an ATS mod-manager icon in a landscape 276:162 aspect. Top headline exactly "JOB TYPES COMPAT", footer exactly "MUSTANG", both large and readable. Navy, warm cream and teal palette with a crisp cream rounded frame. Main subject a beautifully illustrated red 1967 Ford Mustang fastback in side/front three-quarter view, next to a tidy selection of small courier items: document envelope, keys, small parcel. Arrange the courier items like a simple compatibility checklist with three bold teal check marks, conveying more compatible job types. Keep this uncluttered and readable at 276x162. Polished classic American road-sign illustration, few strong shapes. No additional text, logos, watermarks, grids or panels.
```

## Selected M2 map-label exports

Edit target for each request: inspected `m2-original.png`. These replace only the footer; the runtime generator reuses the checked-in JPEG and makes no image-generation call.

### REFORMA

Export: `map-compatibility/reforma.jpg`.

```text
Use case: text-localization. Edit target: the supplied finished navy fuel-and-parking mod icon. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "REFORMA". Where slash appears in requested label, render two centered lines instead of slash. Keep the headline "FUEL & REST FIX", navy/cream/teal palette, border, fuel pump, blue P sign, three parked cars, parking-bay lines, positions and all other artwork unchanged. Preserve landscape aspect 276:162 and safe margins. Footer must be bold and legible when exported at 276x162. No additional text, logos or elements.
```

### PROMODS CANADA

Export: `map-compatibility/promods-canada.jpg`.

```text
Use case: text-localization. Edit target: the supplied finished navy fuel-and-parking mod icon. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "PROMODS CANADA". Where slash appears in requested label, render two centered lines instead of slash. Keep the headline "FUEL & REST FIX", navy/cream/teal palette, border, fuel pump, blue P sign, three parked cars, parking-bay lines, positions and all other artwork unchanged. Preserve landscape aspect 276:162 and safe margins. Footer must be bold and legible when exported at 276x162. No additional text, logos or elements.
```

### WESTERN CANADA

Export: `map-compatibility/western-canada.jpg`.

```text
Use case: text-localization. Edit target: the supplied finished navy fuel-and-parking mod icon. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "WESTERN CANADA". Where slash appears in requested label, render two centered lines instead of slash. Keep the headline "FUEL & REST FIX", navy/cream/teal palette, border, fuel pump, blue P sign, three parked cars, parking-bay lines, positions and all other artwork unchanged. Preserve landscape aspect 276:162 and safe margins. Footer must be bold and legible when exported at 276x162. No additional text, logos or elements.
```

### ALASKA

Export: `map-compatibility/alaska.jpg`.

```text
Use case: text-localization. Edit target: the supplied finished navy fuel-and-parking mod icon. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "ALASKA". Where slash appears in requested label, render two centered lines instead of slash. Keep the headline "FUEL & REST FIX", navy/cream/teal palette, border, fuel pump, blue P sign, three parked cars, parking-bay lines, positions and all other artwork unchanged. Preserve landscape aspect 276:162 and safe margins. Footer must be bold and legible when exported at 276x162. No additional text, logos or elements.
```

### REFORMA + OTHERMAPS PATCH

Export: `map-compatibility/reforma-othermaps-patch.jpg`.

```text
Use case: text-localization. Edit target: the supplied finished navy fuel-and-parking mod icon. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "REFORMA / OTHERMAPS PATCH". Where slash appears in requested label, render two centered lines instead of slash. Keep the headline "FUEL & REST FIX", navy/cream/teal palette, border, fuel pump, blue P sign, three parked cars, parking-bay lines, positions and all other artwork unchanged. Preserve landscape aspect 276:162 and safe margins. Footer must be bold and legible when exported at 276x162. No additional text, logos or elements.
```

### WCE + PROMODS + CONNECTIONS

Export: `map-compatibility/western-canada-promods-connections.jpg`.

```text
Use case: text-localization. Edit target: the supplied finished navy fuel-and-parking mod icon. Change ONLY its bottom footer map label from "ATS EXPANSION" to exactly "WCE + PROMODS / CONNECTIONS". Where slash appears in requested label, render two centered lines instead of slash. Keep the headline "FUEL & REST FIX", navy/cream/teal palette, border, fuel pump, blue P sign, three parked cars, parking-bay lines, positions and all other artwork unchanged. Preserve landscape aspect 276:162 and safe margins. Footer must be bold and legible when exported at 276x162. No additional text, logos or elements.
```

## Discarded preparation

Six M3 footer edits were generated before the user selected M2. They are unused in packages; no M3 selection is implied. Their originals remain at the image tool's default location and are not runtime dependencies. Earlier green C fuel-only artwork is retained unchanged; its historical preparation is in [the asset guide](README.md).

