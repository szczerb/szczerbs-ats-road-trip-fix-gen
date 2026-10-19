# ADR-0021: Compose explicit station-parking batches over the effective stack

## Context

Date: 2026-10-19. [TASK-0045](../../tasks/done/TASK-0045-build-curated-station-parking-test-batch.md) extends the earlier single-station experiment to one mod with a curated list of real test sites. Whole-sector overrides do not merge, and returning to a fuel-only baseline would discard the user's standard r9 rest fixes. A shared visual model does not establish shared PPD actions or identical local surroundings.

## Decision

Add explicit `analyze-station-parking-batch` / `generate-station-parking-batch` workflows with a strict finite manifest: stable P01-style site IDs, separate schema-2 config and paired PIM/PIT paths, and a uniquely resolved original source archive basename per site. Retain the existing single-station API and its historical schema-1 behaviour. Source/fix archives are mounted in the declared effective low-to-high order, including standard r9 fixes where applicable; no fix is silently promoted to the top or replaced by an older payload.

Every site is planned against the same immutable effective stack. Each creates a new private PPD/definition and changes only that placement's eight-byte model token. Compose disjoint checked byte ranges into one output per sector. Reject duplicate placements, overlapping/conflicting resources, partial or no-change sites and incompatible pins before writing a mod. The overlay ships only changed sectors and genuinely new resources; existing baseline PPDs, actions, prices, services and contexts remain dependencies below it. Never merge completed single-station packages by dictionary replacement.

Inspect a bounded 3 × 3 base/aux sector neighborhood for each site. Transform recognized external-prefab PPD UI polygons into world space and treat supported inaccessible colours as explicitly conservative obstacle proxies. Other map items and unsupported representations remain reported unknowns. Anchor-distance and sector bounds do not establish complete collision or absence of external objects. Check physical proposal and approach before ranking; keep native activation parameters unchanged.

Schema-2 painted planning retains each accepted whole separator bank and also evaluates its existing individual free-gap bay polygons. A bay inherits corroboration from the accepted bank of at least three separators; two isolated stripes do not become sufficient evidence. Each records its two source boundary references and parent evidence. Existing occupancy/access/model checks and native parameters remain unchanged, the total stays bounded to 128 candidates, and schema-1/default proposal outputs remain exact. This allows an unoccupied bay to survive without treating a partially occupied row as wholly usable.

## Consequences

The batch is tied to exact effective source versions and needs an explicit installation order above the retained source-specific fixes. A finite curated set is not map-wide generation and does not integrate the 1,000-unit rest/density policy. All listed sites must survive final archive composition and independent audits. Original native car parking suppresses duplication and may be a separate control, not a newly served site. C2/E remain historical comparisons; user-confirmed N2 stays independent and its presentation task remains deferred. Runtime access, prompt tolerance, fatigue and reload require later user tests.
