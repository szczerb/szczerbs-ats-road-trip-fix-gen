# Architecture Decisions

This directory stores architecture and workflow decisions using ADR files named `ADR-XXXX-<slug>.md`.

Create a new ADR when a decision changes architecture, repository structure, data flow, interfaces, or workflow conventions.

Do not rewrite old ADRs to hide history. If a decision changes, create a newer ADR and link the two.

## Accepted decisions

- [ADR-0001: Use a documentation and evidence workflow before generator implementation](ADR-0001-documentation-and-evidence-workflow.md).

- [ADR-0002: Use Python inspection and bounded experimental patches](ADR-0002-use-python-inspection-and-bounded-experimental-patches.md).

- [ADR-0003: Allow pinned single-pump sector experiments](ADR-0003-allow-pinned-single-pump-sector-experiments.md).

- [ADR-0004: Add pinned overlapping fuel services](ADR-0004-add-pinned-overlapping-fuel-services.md).

- [ADR-0005: Standardize fuel package metadata](ADR-0005-standardize-fuel-package-metadata.md).

- [ADR-0006: Discover and clone map fuel services](ADR-0006-discover-and-clone-map-fuel-services.md).

- [ADR-0007: Repair missing petrol prices with explicit provenance](ADR-0007-repair-missing-petrol-prices.md).

- [ADR-0008: Compose selected processors and apply rest eligibility locally](ADR-0008-compose-processors-and-local-rest-polygons.md).

- [ADR-0009: Report courier inputs before generating fixes](ADR-0009-report-courier-inputs-before-generating-fixes.md).

- [ADR-0010: Preserve contexts for generated prefab aliases](ADR-0010-preserve-contexts-for-generated-prefab-aliases.md).

- [ADR-0011: Generate practical courier eligibility as a separate mod](ADR-0011-generate-standalone-practical-courier-eligibility.md).

- [ADR-0012: Preserve irregular source rest geometry](ADR-0012-preserve-irregular-source-rest-geometry.md): action-only edits with explicit conservative proximity, no geometry repair.

Runtime fix validation and general map-sector authoring remain open.
