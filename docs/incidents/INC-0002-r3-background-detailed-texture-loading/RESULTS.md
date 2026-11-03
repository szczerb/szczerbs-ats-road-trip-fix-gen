# Results

## Confirmed facts

**Documented — user, 2026-10-25:** r3 background is invisible at the three more detailed world-map levels and visible at maximum zoom out.

**Observed locally — same installed r3 bytes, ATS 1.61.3.18s:** the preserved log reports an archive-specific DirectStorage batch failure, `0x89240008`. All eleven presentation definition/material/TOBJ resources compared with r2 are byte-identical. Detailed DDS dimensions doubled and expanded pixels quadrupled; overview dimensions stayed unchanged. All DDS files retain the prior format, one mip, flags and pitch policy. Current `r_texture_detail` is `0`; no missing-mip explanation is supported by a changed mip policy.

**Documented — Microsoft DirectStorage maintainer, 2023-01-17; inspected 2026-10-25:** [DirectStorage issue 21](https://github.com/microsoft/DirectStorage/issues/21) identifies this exact code as `E_DSTORAGE_REQUEST_TOO_LARGE`: either compressed or uncompressed request data exceeds the staging-buffer size. [Microsoft developer guidance](https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md) describes staging-buffer/request restrictions and size selection. These document the API mechanism, not the staging-buffer value chosen internally by ATS 1.61.

## Causal assessment

**Strongly supported inference:** increasing each detailed uncompressed tile from 64 MiB to 256 MiB crossed the working loading-request size boundary in this engine/archive path. The small overview remains loadable, matching the user's reported zoom split. The concrete DirectStorage code makes this more specific than a generic GPU-memory or projection hypothesis.

**Unknown:** the precise failed member and request, engine staging-buffer size, whether DDS headers are included in that request, and whether a different archive layout alone would avoid it. The empty chunk field prevents attributing the first failure to an individual tile. No fixed universal 4096 texture limit or exact 128/256 MiB ATS threshold is established. A controlled resized build and user retest remain needed to close the causal loop.

**Documented — Microsoft Direct3D 11 resource limits; inspected 2026-10-25:** [feature-level-11 2D textures may reach 16384 per axis](https://learn.microsoft.com/en-us/windows/desktop/direct3d11/overviews-direct3d-11-resources-limits). An 8192 tile therefore does not by itself prove a hardware dimension violation. Engine loading constraints and GPU texture dimension capability are different checks. The logged adapter has ample reported VRAM, but that does not enlarge DirectStorage staging requests automatically.

## Alternatives assessed

- **Zoom, camera and icon configuration:** no changed bytes in `def/map_data.sii`; accepted `zoom_uplift[7]=60000` and all tiers preserved. No new zoom retuning is supported.
- **Material paths, missing references, wrong quadrant mapping, filtering:** MAT/TOBJ resources identical. Static checks verify the references and encoded pixels. These cannot demonstrate successful runtime request processing.
- **Geographic projection/shore repair:** changes coastline placement, not whether all four detailed resource files load. No evidence supports undoing that model to fix a loader failure.
- **Corrupt or different installed copy:** installed r3 hash matches delivery; the previous independent ZIP/CRC audit passed. A valid ZIP can still contain a member that the runtime cannot load in one request.
- **Mipmaps:** one-mip DDS and `mip_filter : none` policy predate r3. Unchanged policy cannot alone explain this revision-specific regression; alternate mip/engine behavior is not instrumented.
- **Transit-image dimensions:** the log separately reports 11008×2880 transit images with a 5120×1440 detected display. This is a real separate UI warning, but no causal link to the r3 background or detailed DDS is established.
- **Other map/company/vehicle errors:** present but not a substitute explanation for the archive-specific loader failure.

## Why the offline release checks missed it

**Observed locally — implementation review:** `validate_inputs` accepts power-of-two `texture_size` values through 16384. `build_resources` uses half of that for each detailed tile. `validate_package` checks dimensions against the supplied config, DDS structure, opaque pixels, exact resources and ZIP integrity; it never exercises the ATS DirectStorage queue or enforces an engine-tested expanded resource budget. Its success established valid authored bytes, not acceptance of a 256 MiB texture request. The prior 326-test count did not cover this external loading mechanism. The r3 handoff noted the increased pixel payload/performance uncertainty, but that was insufficient as a release gate for retaining functioning detailed backgrounds.

**Recommendation:** first return detailed resources to the working 4096-square/64 MiB pixel budget while preserving r3's geometry and all accepted map-data bytes. Retain the original source atlas if useful, with a separately validated delivery raster. A distinctly versioned corrective package and user runtime confirmation are the next step. This analysis changes documentation only; the runtime regression remains open.
