---
name: project-orchestrator
description: Turn substantial multi-stage goals into correctable local project contracts and scoped local skills with evidence-based acceptance. Use when work spans research through delivery or future sessions. Do not use for simple questions, one-off edits, or informal brainstorming without project files.
---

# Project Orchestrator

Convert a substantial goal into the smallest durable project structure that helps a capable model finish and verify the work. Keep implementation choices open. Be strict only about user intent, evidence, permissions, correction, and acceptance.

## Decide Whether to Projectize

Use this workflow when the request combines several phases such as research, building, data work, validation, delivery, automation, or continuation across sessions.

Do not create project files when ordinary direct work is enough. If the user asks only to discuss or plan, stop at that boundary unless they also ask for local project artifacts.

If current project instructions and skills already cover the work, update them only when a demonstrated gap matters. Do not create parallel sources of truth.

## Establish the Contract

Before substantial writes or external actions:

1. Inspect the current workspace, effective instruction files, relevant local skills, and existing source-of-truth artifacts.
2. Resolve the intended target directory from the user's scope and current work. A parent Git root alone does not justify writing project artifacts above an explicitly scoped subdirectory.
3. Identify the desired outcome, completion evidence, scope, constraints, permissions, and material unknowns.
4. Classify the task only as far as classification changes planning or validation. Useful dimensions are intent, evidence source, artifact, risk, time behavior, uncertainty, reversibility, and validation method.
5. Ask together only for missing choices that materially change the outcome, acceptance, authorization, cost, or irreversible risk. Discover local facts instead of asking for them.
6. When the user is unsure, recommend a conservative, reversible default and record it as an assumption rather than a confirmed requirement.

Use `CONFIRMED`, `ASSUMED`, `OPEN`, `REJECTED`, and `SUPERSEDED` where requirement state matters. Keep the contract readable; YAML is optional.

## Choose the Minimum Durable Artifacts

Read [references/artifact-contracts.md](references/artifact-contracts.md) before creating or substantially updating project guidance.

Create only artifacts that reduce future rediscovery:

- Keep stable, repository-wide rules in `AGENTS.md` or the host's verified equivalent.
- Create one project-local skill when a recurring or domain-specific workflow needs more detail than project instructions should carry.
- Use a separate project contract when goals, assumptions, decisions, or acceptance criteria are too changeable or detailed for `AGENTS.md`.
- Add scripts only for repeated deterministic checks or transformations.
- Put conditional detail in references instead of expanding the skill entrypoint.

Preserve existing user content and authority. Prefer a focused merge over replacement. Never copy the entire plan into every artifact.

When a project-local skill is created, make its description discriminating and add a short conditional routing rule to the project's instruction file. Do not require the skill for unrelated work.

## Execute With Open Methods and Gated Outcomes

For the current stage:

1. Define the observable result and the evidence that would pass it.
2. Choose an implementation approach using the current environment and evidence. Treat examples as options, not mandatory recipes.
3. Produce one useful, reviewable increment when the work is large.
4. Validate the real artifact or external state in proportion to failure cost.
5. Continue, adapt, re-plan, or stop based on evidence.

Separate sourced facts, unresolved gaps, and analysis when the distinction matters. Cross-check critical claims with appropriate independent evidence; do not reduce source quality to popularity or citation count alone.

Do not prescribe a fixed tool, framework, agent count, implementation order, or retry count without a concrete reason. Stop when attempts yield no new evidence, a required permission or input is unavailable, acceptance criteria conflict, or further work would exceed the authorized risk or cost.

External sends, publishing, deletion, spending, credential use, and other consequential mutations require authorization at the point they become necessary. A successful local command is not proof of external delivery.

## Correct Misunderstandings Immediately

When the user corrects the goal or a material assumption:

1. Pause the affected path.
2. Mark the old requirement or assumption `SUPERSEDED`; do not leave contradictory active guidance.
3. Recompute the impact on scope, artifacts, implementation, tests, and delivery.
4. Update only affected project instructions, contract sections, local skills, and outputs.
5. Re-read changed guidance and re-run affected acceptance checks. Preserve still-valid evidence.
6. State which prior outputs are invalid, still valid, or not yet rechecked.

Files are persistent state, not immutable truth. Never continue merely because the first interpretation was already written down.

## Handle Host-Specific Integration Carefully

Read [references/host-adapters.md](references/host-adapters.md) when installing local skills, editing project instruction files, adding invocation assurance, or preparing another agent host.

For Codex, re-read a changed `AGENTS.md` during the current task, but describe this accurately as a contextual refresh. Verify critical instruction changes in a new run because the native instruction chain is built at run or session start.

Activation receipts and hooks are optional assurance layers. They may prove that files were read and unchanged; they do not prove semantic understanding. Do not install hooks unless their benefit and trust cost are justified.

## Validate and Report Completion

Separate audience-facing deliverables from internal validation evidence. Keep the main deliverable focused on what its intended audience needs to use and trust it, including relevant sources, definitions, decision-relevant methodology, limitations, and a concise quality status. Put implementation logs, tool traces, test matrices, and detailed acceptance checklists in the project contract or a separate validation/audit artifact unless the user or audience explicitly needs them combined.

Choose validation from the task's risks and artifacts. Relevant checks may include provenance, cross-source agreement, schemas, tests, coverage, visual rendering, archive integrity, idempotency, or external delivery evidence.

Before declaring completion, report:

- what outcome was produced;
- which acceptance checks passed and their evidence;
- remaining assumptions, gaps, or blocked items;
- material files or external state changed;
- the safest next action, if work remains.

Use `scripts/validate_project.py --host <codex|claude>` for structural checks after creating host-native project guidance. A project-local skill is optional by default; pass `--require-skill` only when the project design explicitly requires one. Use `scripts/instruction_state.py` only when stale-instruction detection materially improves a long or high-risk task.

## Evolve This Skill From Evidence

When testing or modifying this global skill, read [references/evaluation.md](references/evaluation.md). Judge observable behavior and artifacts, not required wording. Prefer the smallest fix for a demonstrated failure, and confirm that added rules do not reduce a strong model's problem-solving quality.
