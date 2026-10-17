# ADR-0001: Use a documentation and evidence workflow before generator implementation

## Context

Date: 2026-10-17. The user approved project initialization for an ATS Road Trip compatibility utility before implementation. Courier Job and passenger-car refueling failures have been reported, but their causes and automatic-fix feasibility are unconfirmed. The repository contains supplied local mod archives and existing artifact exclusions.

Related work: [TASK-0001](../../tasks/done/TASK-0001-initialize-project.md), [project brief](../../project/PROJECT_BRIEF.md), and [working agreements](../../project/WORKING_AGREEMENTS.md).

## Decision

Adopt the bootstrap skill's task/ADR/incident structure, with project-specific evidence labels and linked references. Track bounded work through backlog, active, and done directories with matching frontmatter status. Preserve original local inputs and keep large/derived artifacts in ignored local directories.

Prepare versioned reference data, investigate Courier Jobs and passenger-car refueling at equal priority, then review both outcomes before choosing the first generator increment. Delegate bounded work with explicit ownership and economical model/effort selection. Preserve the user's Plan Mode task/model-table and meaningful commit-message requirements in AGENTS.md.

## Consequences

- This milestone produces documentation and research tasks, not a functioning fix tool.
- Technical claims need sources/version context or local evidence; unproven explanations remain hypotheses.
- Task moves require status and link updates, and significant findings require current-state updates.
- Product implementation choices remain open until research supports a concrete increment; later durable decisions get their own ADRs.
- The workflow adds a small documentation-maintenance cost in exchange for reproducible handoffs and visible uncertainty.
