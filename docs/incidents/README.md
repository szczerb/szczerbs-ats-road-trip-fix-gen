# Incidents

This directory stores reproducible failures and longer investigations.

Create a new incident folder only when the project has an actual failure or investigation that needs preserved evidence over time.

Use the [incident template](../templates/INCIDENT_TEMPLATE.md) and link the evidence from an active task. Ordinary planned compatibility research stays in its task until a reproduced failure needs a separate trail. Record version/load-order context and keep large logs or assets in ignored output directories.

Initialization opened no incidents. Subsequent investigations:

- [INC-0001: Connector icon cache write failure](INC-0001-connector-icon-cache/README.md) — valid packaged JPEG, logged copy failure, shorter r8 filename mitigation; in-game confirmation pending.
- [INC-0002: R3 detailed world-map background loss](INC-0002-r3-background-detailed-texture-loading/README.md) — user-reported three-level blank background, archive-specific DirectStorage request-too-large error, detailed tile pixels increased 64→256 MiB; analysis complete, corrective build/runtime confirmation pending.
