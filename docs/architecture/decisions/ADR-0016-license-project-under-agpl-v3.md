# ADR-0016: License project-authored materials under AGPLv3

## Context

**Documented — user direction, 2026-10-18:** the maintainer prefers software freedom to remain available to downstream users, rather than permitting closed forks, and requests applying AGPL after discussing GPL/MPL and network-service obligations. The [deeper implementation audit](../../reference/IMPLEMENTATION_INDEPENDENCE_ASSESSMENT.md) found no obvious substantial translated upstream routine in its bounded comparison. It is technical evidence, not a clean-room claim or legal certificate. Historical consulted sources have a verified GPLv2 grant, with later-version permission unverified; this decision cannot relicense a protected GPLv2-only adaptation if one is later identified.

## Decision

Apply **AGPL-3.0-only**, exactly GNU Affero GPL version 3, to original project code, tests, documentation, configuration examples and project-authored artwork, subject to explicit third-party notices and the rights actually held. Do not add an unrequested future-version grant. Put the unmodified FSF license in root `LICENSE`, the copyright/version notice and scope in [LICENSING.md](../../../LICENSING.md), and matching license metadata in `pyproject.toml`. Ship these notices with built Python distributions.

Retain [third-party notices](../../../THIRD_PARTY_NOTICES.md). Exclude game/DLC/map resources and separately obtained tools from this grant; generated `.scs` files do not acquire AGPL automatically through tool use. Third-party trademark and depicted-material rights are not granted. Intentionally submitted contributions use AGPL-3.0-only unless separately agreed, without automatic assignment or additional relicensing rights.

## Consequences

Covered distributed derivatives retain copyleft obligations; modified versions supporting remote network interaction must offer corresponding source as section 13 specifies. Commercial use remains allowed, and private local edits do not require public posting. The maintainer can offer their own code under additional terms, but cannot retract granted rights or unilaterally relicense someone else's protected contribution. See [the official rationale](https://www.gnu.org/licenses/why-affero-gpl.html) and [official license text](https://www.gnu.org/licenses/agpl-3.0.txt).

This supersedes the earlier MIT policy recommendation, not the audit evidence or upstream terms. It does not publish the repository, configure a remote, rewrite history, sanitize local paths, rebuild gameplay mods or settle third-party asset rights. [TASK-0031](../../tasks/done/TASK-0031-apply-agpl-and-explain-local-paths.md) records verification and the local-path explanation.
