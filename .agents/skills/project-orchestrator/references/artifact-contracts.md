# Artifact contracts

Read this reference only when creating or substantially updating durable project guidance.

## Minimal project contract

Use a separate contract only when the project has material scope, assumptions, decisions, or acceptance criteria that should survive future sessions. The suggested Codex location is `.project-orchestrator/PROJECT.md`, but follow an existing project convention when one exists.

Keep only useful sections:

- outcome and user value;
- in-scope and out-of-scope work;
- acceptance evidence;
- requirements and assumptions with `CONFIRMED`, `ASSUMED`, `OPEN`, `REJECTED`, or `SUPERSEDED` state;
- permissions and consequential-action boundaries;
- current source-of-truth artifacts;
- decisions whose rationale would otherwise be rediscovered;
- current stage, blockers, and stop conditions.

Do not duplicate chat history or maintain a chronological diary. Update the current truth and retain only change history needed to explain a decision or correction.

## Project instruction file

Use the host-native project instruction file: `AGENTS.md` for Codex, `CLAUDE.md` for Claude Code, or a verified equivalent on another host. It should remain concise and stable. Merge with existing guidance instead of replacing it. Useful content may include:

- the project's durable objective;
- current source-of-truth precedence;
- environment constraints that commonly cause failure;
- conditional routing to project-local skills;
- permission or safety boundaries;
- required acceptance entrypoints;
- the correction rule: current user direction and verified artifacts override superseded plans.

Avoid embedding a full implementation plan, volatile status, long source lists, or generic model advice. Put detailed workflows in a local skill and volatile project state in the contract.

When adding a routing rule, identify both the matching task and the skill. Example shape, not required wording:

```markdown
- For tasks that acquire, validate, or report this project's market data, use
  the local `market-data-report` skill before writing project outputs.
```

Do not route unrelated tasks through the skill.

## Project-local skill

Create one local skill for one coherent recurring capability. Its `description` should lead with what it does and when it applies, plus a meaningful exclusion when adjacent work would otherwise misroute.

Place it in the host-native repository skill directory, such as `.agents/skills/<name>/` for Codex or `.claude/skills/<name>/` for Claude Code. Keep the portable skill content equivalent across hosts; isolate only discovery paths or host metadata.

Keep in `SKILL.md`:

- purpose and activation boundary;
- inputs and expected artifacts;
- domain-specific decision criteria;
- non-obvious invariants, permissions, and stopping rules;
- routes to conditional references or deterministic scripts;
- observable completion evidence.

Avoid:

- universal implementation recipes;
- fixed tools or sources when equivalent alternatives are valid;
- examples presented as mandatory;
- copied project history;
- requirements already enforced by the host or repository.

Use references for substantial domain modes, schemas, source policies, or deliverable-specific validation. Use scripts when deterministic behavior is repeated and materially safer than regeneration.

## Task portrait and validation profile

Classify only dimensions that change a decision:

| Dimension | Examples | What it changes |
|---|---|---|
| Intent | research, build, transform, report, deliver, automate, audit, recover | stages and outputs |
| Evidence | papers, official docs, APIs, local files, databases, live UI | provenance and access strategy |
| Artifact | catalog, code, dataset, model, HTML, email, automation | acceptance target |
| Risk | read-only, local reversible, external write, credentials, privacy, cost | authorization and safeguards |
| Time | one-off, long-running, incremental, recurring | state, idempotency, recovery |
| Validation | citation, cross-source, schema, tests, visual QA, delivery proof | evidence gate |
| Uncertainty | goal, scope, data access, environment, preference | clarification boundary |
| Reversibility | easy rollback, migration, irreversible, third-party impact | execution threshold |

Typical validation profiles are composable:

- Research: traceability, definition checks, source independence, domain fit, coverage gaps.
- Data: schema, units, coverage, duplicates, missingness, temporal alignment, cross-source discrepancies.
- Software: relevant tests, contract checks, failure behavior, compatibility, artifact equivalence when required.
- Report: data-to-render consistency, required content, real rendering, readability, links and archive integrity.
- Delivery: exact recipients or destination, idempotency, sent-state or destination-side evidence, retry boundary.
- Automation: schedule and timezone, trigger eligibility, persistent environment, concurrency, duplicate prevention, recovery.

Select what matches the failure modes. Do not require every profile for every project.
