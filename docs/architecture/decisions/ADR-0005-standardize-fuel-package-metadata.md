# ADR-0005: Standardize fuel package metadata

## Context

Date: 2026-10-17. The user confirms both-mode refueling with sample 2 and requests recognizable metadata before mass generation. The old manifest has research/sample branding and the mod manager displays a default ATS logo. Different map targets need an explicit short name.

## Decision

Use `szczerb's Road Trip Gas Stations Fix for <short map name>` for all fuel generation commands, author `szczerb`, and `<ATS major.minor>-r<nonnegative revision>-experimental`. Start with `1.61-r0-experimental`. Revisions are explicitly supplied, never inferred from file counts or automatically advanced on regeneration. Stable publication is deferred; the experimental gate remains mandatory. The tool's own Python package version remains independent.

Require `--map-name`; support `--revision` (default 0) and `--icon`. Package supplied icons as root `mod_icon.jpg`, referenced by the manifest. Keep icon/name/version in the embedded metadata report separately from gameplay-resource hashes. If no icon is supplied, omit the icon field rather than shipping an ATS logo. Branded handoff samples include an original icon; the user selected design C (green sign, four cars) from three proposals. Courier candidates retain their own purpose-specific title and never receive fuel branding implicitly.

Small project-authored icon exports and their prompts are tracked. Large generated originals and generated mods stay ignored. Metadata-only rebuilding must retain gameplay payload bytes and preserve historical tested outputs. This supersedes ADR-0004's sample-specific display-name choice; sample identity remains in the description/report and canonical guide.

## Consequences

The long display name may be clipped in narrow mod-manager panels; the full manifest title remains as requested. Map name and version label do not establish map-wide coverage or compatibility. Source pins, experimental flags, explicit scope and validation evidence remain necessary. Package hashes change when metadata or artwork changes; compare gameplay-resource hashes separately.

See [metadata contract and source](../../reference/MOD_METADATA.md) and [TASK-0010](../../tasks/done/TASK-0010-brand-gas-station-fix-packages.md).
