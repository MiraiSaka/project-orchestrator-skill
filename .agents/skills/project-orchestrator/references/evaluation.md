# Behavior evaluation

Read this reference only when testing or changing the global Skill.

## Evaluation objective

The Skill should improve durable planning, correction, and acceptance without reducing a capable model's ability to discover and implement a strong solution.

Evaluate observable decisions and artifacts. Do not require fixed headings, wording, tool choices, implementation order, or agent count.

## Core invariants

For substantial project requests, check that the model:

- identifies the outcome and completion evidence;
- asks only material blocking questions and groups them efficiently;
- records reversible defaults as assumptions;
- creates or updates only useful durable artifacts;
- preserves existing project guidance and user work;
- keeps implementation methods open unless risk justifies specificity;
- selects validation from actual artifacts and failure modes;
- separates audience-facing deliverables from internal validation evidence unless the intended audience needs them combined;
- separates sourced facts, gaps, and analysis when material;
- obtains authorization before consequential external actions;
- stops or escalates when retries provide no new evidence;
- supersedes corrected assumptions and revalidates affected work.

For simple or already-governed requests, check that it does not create unnecessary project machinery.

## Test groups

Maintain positive, negative, ambiguous, correction, stale-instruction, permission, delivery, and cross-host cases. Keep DEAP operator research and futures data/report delivery as anchor cases, but include unrelated domains so finance examples do not leak into the global core.

Use the repository's `evals/behavior-cases.json` as the initial case catalog.

## Comparison method

For important cases, compare:

- no Skill baseline;
- current Skill;
- an intentionally rigid workflow as a pressure control.

Blind-score outcome understanding, useful questions, plan quality, problem discovery, solution flexibility, validation quality, unnecessary work, and user turns. The current Skill should improve planning and acceptance without lowering solution quality.

Run key cases more than once because model behavior is nondeterministic. Record model, host, date, prompt, generated artifacts, result, and failure category.

## Fix discipline

1. Reproduce a behavioral failure and state the violated invariant.
2. Distinguish a Skill issue from environment failure or normal model variance.
3. Make the smallest targeted change.
4. Re-run the failing case, nearby negative cases, and autonomy comparison.
5. Remove duplicated or overgeneral rules during refactoring.

If a failure is domain-specific, fix the generated project-local skill or adapter. Do not accumulate global rules for every example.

## Candidate release gates

- zero consequential permission violations;
- zero continued reliance on a corrected critical assumption;
- zero missing declared critical acceptance gates;
- strong-project routing succeeds in at least 90% of repeated anchor runs;
- obvious simple-task false activation stays at or below 10%;
- solution quality does not regress against the no-Skill baseline;
- fresh-host installation and discovery are verified separately from local source validation.

Treat thresholds as candidates until a baseline corpus is large enough. Never tune only to the anchor prompts.
