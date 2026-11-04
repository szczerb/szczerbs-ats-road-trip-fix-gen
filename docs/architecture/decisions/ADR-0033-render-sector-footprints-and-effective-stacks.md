# ADR-0033: Render sector footprints and effective stacks separately

## Context

The maintainer needs to inspect how map expansions and connector versions fit together. An archive can supply empty replacements or individual sector members whose roads and other resources come from different providers. The existing North America atlas is registered to ATS world X/Z coordinates and can supply geographic context for read-only images.

## Decision

Shade the exact union of supplied 4,000-unit sector tiles per map namespace. Include empty and layer-only tiles and preserve gaps. Render native road items and supported placed prefab links separately from that coverage layer. Use the existing generator’s full raster and world bounds. Retain coordinates outside the atlas and support explicit crops for close inspection.

Standalone and comparison views preserve each selected archive’s own geometry, with declared dependencies available to resolve references. The effective view takes an explicit low-to-high stack and selects winners per virtual resource. The image distinguishes visible providers and stock/DLC context, and the summary names the winning and shadowed providers.

Report the decoded road count, supported links, verified endpoint approximations, and unresolved records. Keep validated resource paths and package identities in the summary and resolve machine-specific input locations at runtime. The renderer can tolerate malformed HashFS v1 deep-discovery candidates by counting and discarding them before any selected extraction. Generation retains strict archive inventory.

## Consequences

A full footprint can include distant detached tiles that make a single overview less useful at road scale. A shared crop preserves registration and can show the seam while the full view remains available. Archive and prefab decoding limits remain visible in the image and summary. The tool offers static evidence about the declared resources and their coverage.

[Renderer usage and geometry evidence](../../reference/MAP_MOD_RENDERER.md)
