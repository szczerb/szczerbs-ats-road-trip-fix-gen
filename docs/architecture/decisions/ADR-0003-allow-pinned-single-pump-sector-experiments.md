# ADR-0003: Allow pinned single-pump sector experiments

Partial supersession: [ADR-0004](ADR-0004-add-pinned-overlapping-fuel-services.md) permits a separate pinned additive service/node experiment at the same position. Existing conversion semantics below remain unchanged.

## Context

Date: 2026-10-17. The user requested a practical ATS Expansion sample near a candidate starting garage. Follow-up inspection found a separate serialized service field correlated with car-oriented PPD flags, and a Great Falls single-locator prefab near a placed garage. See [location and evidence](../../reference/STARTER_AREA_SAMPLE.md) and [TASK-0008](../../tasks/done/TASK-0008-prepare-starter-area-sample.md).

The first fuel generator duplicates a locator while leaving existing serialized services unchanged. The new observation supports a controlled alternative that preserves counts and transforms. It does not establish the runtime interpretation of every service bit or fresh-profile garage eligibility.

## Decision

Add an explicitly experimental `generate-local-fuel` command accepting a reviewed JSON recipe. For the inspected ATS 1.61.3.18 / map format 907 baseline, require exact source sector/PPD hashes, one stock `02003` configuration with a default variant, two prefab nodes, one GAS locator, and one correctly linked service. Convert that one existing interaction using a private prefab alias/descriptor and a bounded sector token/service-bit change. Reject mismatches and collisions; preserve all other bytes, references, transforms, lengths, and counts.

This narrowly supersedes ADR-0002's prohibition on sector edits **for this separate recipe-driven command only**. Existing `generate-fuel` semantics remain unchanged. Do not silently promote this bounded field patcher to a general map serializer, automatic location discovery, or verified repair. The three-resource package and recipe report remain ignored local artifacts apart from the authored recipe itself, which contains identifiers/hashes/coordinates rather than copied game resources.

## Consequences

The sample can test a localized service-plus-descriptor mechanism without upgrading old PPDs or adding nodes/services. It converts one pump rather than promising dual truck/car access. Its entire `.base` resource replaces the source sector in mod resolution and can conflict with other map/companion-data changes despite the tiny byte diff. A higher-priority mod can invalidate the intended runtime stack; generation hashes do not enforce installation order.

Starting-city selector behavior, garage substitution/access, map caching, actual fuel purchase, and preserved nearby truck use remain [gameplay validation](../../tasks/active/TASK-0007-validate-courier-and-fuel-experiments-in-game.md). Authored recipes cover Great Falls and the Helena area. Helena retains a stock garage class and is the stronger HQ candidate; neither is a confirmed selector entry. Courier behavior receives separate observation; no duplicate context-tag change is justified for already classified Great Falls company definitions.

See [ADR-0002](ADR-0002-use-python-inspection-and-bounded-experimental-patches.md) for the unchanged archive, parsing, context-generator, deterministic-output, and profile-preservation decisions.
