# Debugging plan

## Completed analysis

1. Preserve the latest game log and its hash/mtime without touching profiles or running ATS.
2. Compare actual r2/r3 ZIP resources, DDS headers and expanded sizes; verify installed r3 against the delivered SHA.
3. Decode the logged failure against primary Microsoft DirectStorage documentation and maintainer explanations.
4. Separate confirmed loader failure from the inferred individual failing DDS, and assess unchanged zoom/material/settings and unrelated warnings.

## Controlled correction proposed, not performed

The lowest-risk comparison build would retain r3 geography/calibration, world mapping and accepted map-definition bytes while returning detailed tiles to the working r2 size of 4096 square. Keep the overview at 2048 square. Package under a distinct revision and preserve r2/r3 originals. If producing tiles from the selected atlas, verify exact quadrant/downsampling correspondence rather than silently rolling back the geographic model.

Verify DDS dimensions, expanded member sizes, all references, unchanged map definition/materials/TOBJs and deterministic packaging. Add a resource-size compatibility guard so the generator cannot silently emit another oversized detailed member under the same tested delivery policy. A power-of-two/header check alone is insufficient; separate renderer canvas resolution from deliverable texture resolution if needed.

Runtime acceptance must check all four world-map levels after a full game restart and the new log for this DirectStorage failure. The user performs in-game testing. A passing resized build would isolate the changed request size much more directly than another projection change.

A stored/uncompressed ZIP or correctly chunked engine archive is a secondary packaging experiment if necessary, not a verified remedy. GPU block compression could reduce runtime pixels at retained dimensions, but changes the codec/quality contract and needs separate validation. Do not prescribe launch-option/memory changes as a mod fix; the engine staging-buffer value is unknown. No such changes were made.
