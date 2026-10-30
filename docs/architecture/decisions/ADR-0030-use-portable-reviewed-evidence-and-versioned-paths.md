# ADR-0030: Use portable reviewed evidence and relative versioned paths

- Status: Accepted
- Date: 2026-10-30
- Related task: [TASK-0056](../../tasks/active/TASK-0056-clean-research-history-and-prepare-public-pr.md)

## Context

Realistic station parking originally loaded reviewed converted models and one family configuration from ignored dated research directories. Exact source guards were useful, but a source checkout could not prepare its own evidence through a documented portable input contract. Historical handoffs also recorded a concrete local worktree root. The user authorizes a branch-only history cleanup and requires relative paths in versioned material.

## Decision

- Track authored four-family catalog metadata and existing source fingerprints; never track converted game meshes or third-party resource payloads.
- Supply reviewed model evidence explicitly through `--station-evidence-dir`, propagated through processor configuration and stack/single-map planning. Preparation verifies all reviewed text hashes before importing local converted files. Missing or changed evidence fails clearly before real generation; broad legacy processing requires no such evidence.
- Use repository-relative project references and document-relative Markdown links. External filesystem locations are runtime arguments or ignored configuration; temporary paths are constructed at runtime. The rule covers every versioned file and commit message. URLs and engine/archive virtual identifiers retain their required syntax.
- Keep the North Platte placement supplement source-specific and validate its exact original resources only when that source partition is selected. Shared sector coordinates are not sufficient to identify its applicability.
- Rewrite only authorized branch-only historical document paths. Preserve parent topology and commit metadata, retain a verified ignored recovery backup and publish only reviewed branch refs.

## Consequences

A fresh checkout can prepare reviewed evidence from its own exact original resources without receiving third-party assets or recreating private historical directory layouts. The converter and reviewed source versions remain explicit prerequisites; changed resources require review rather than repinning automatically. Existing generated packages retain their historical receipts. Publishing source does not authorize distribution of the generated source-derived resources.
