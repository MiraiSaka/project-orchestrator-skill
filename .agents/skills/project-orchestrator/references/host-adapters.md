# Host adapters and invocation assurance

Read this reference when installing local skills, editing host instruction files, adding invocation assurance, or moving the workflow to another agent host.

## Portable core

Keep the core workflow portable:

- user intent and acceptance contract;
- minimal durable project guidance;
- scoped local workflow instructions;
- evidence, permission, correction, and stopping rules;
- behavior-based evaluation.

Treat instruction filenames, discovery paths, lifecycle hooks, and UI metadata as host adapters. Do not claim one host's behavior applies to another.

## Codex adapter

Current official OpenAI documentation establishes these boundaries:

- Codex discovers repository skills under `.agents/skills` from the working directory up to the repository root.
- Skill `description` supports implicit selection; explicit `$skill-name` invocation is also available.
- Codex builds the `AGENTS.md` instruction chain once per run or TUI session. Re-reading a changed file adds current-task context but is not native hot reload.
- Codex detects skill changes automatically, but a restart may be needed if an update does not appear.
- Non-managed Hook definitions are trusted by their current hash and require review after changes.
- Command and MCP tool Hook handlers run; prompt and agent handlers are currently parsed but skipped.

Authoritative references:

- <https://learn.chatgpt.com/docs/build-skills>
- <https://learn.chatgpt.com/docs/hooks>
- <https://learn.chatgpt.com/docs/agent-configuration/agents-md>

For a repository-local installation, place the global or project skill at:

```text
<repo>/.agents/skills/<skill-name>/SKILL.md
```

Start a fresh task from the intended repository or test subdirectory when testing implicit discovery.

Validate generated Codex project guidance with:

```text
validate_project.py <project-root> --host codex
```

## Claude Code adapter

Use the same portable `SKILL.md`, references, and scripts. Change only the host integration:

- personal skill: `~/.claude/skills/project-orchestrator/SKILL.md`;
- repository skill: `<repo>/.claude/skills/project-orchestrator/SKILL.md`;
- stable project guidance: `CLAUDE.md`;
- explicit invocation: `/project-orchestrator`; semantic matching may also select the skill from its description.

Validate generated Claude project guidance with:

```text
validate_project.py <project-root> --host claude
```

When an instruction-state receipt is justified, pass `--host claude` to `instruction_state.py snapshot`. The project-local `--skill` receipt input is optional; include it only when that task relies on one.

Select the exact Opus model available in the host and record the displayed model name in evaluations. Do not put model-specific implementation recipes into the portable core merely to optimize one benchmark run.

Reference: <https://code.claude.com/docs/en/skills>

## Context refresh after guidance changes

After changing `AGENTS.md`, a project contract, or an active local skill during a task:

1. state which files changed;
2. re-read the effective files from disk;
3. invalidate any recorded instruction snapshot;
4. mark conflicting assumptions `SUPERSEDED`;
5. continue using the refreshed content;
6. use a new run to verify critical native instruction-chain changes.

## Optional instruction-state receipt

Use `scripts/instruction_state.py` only for long, expensive, or consequential work where stale guidance is a realistic failure mode.

Create a snapshot after the agent has read the active project instruction file and any local skill used by the task:

```text
instruction_state.py snapshot <project-root> --host <codex|claude> [--skill <skill-path>] --task-id <id>
```

Check it before a consequential stage:

```text
instruction_state.py check <project-root>
```

The receipt records hashes and can detect changed or missing files. It does not prove that the model understood them.

## Optional Hooks

Do not install Hooks by default. Add them only after false-positive and trust-cost testing.

Possible Codex use:

- `UserPromptSubmit` adds context suggesting evaluation by the global orchestrator;
- `PreToolUse` blocks a consequential write when an explicitly managed task has a missing or stale receipt;
- `Stop` requests another pass only when a declared critical acceptance gate remains unmet.

Keep Hook classification conservative. Pure explanations, read-only discovery, unrelated tasks, and unmanaged projects should not be blocked. A Hook may improve compliance but cannot prove Skill activation or semantic understanding.

## Other agent hosts

Before adapting to Fable or another host, verify the actual available model name and current support for:

- Agent Skills discovery location and frontmatter;
- project instruction files and precedence;
- live instruction refresh;
- lifecycle hooks and supported handler types;
- script permissions and environment;
- packaging and distribution.

Reuse the portable core and behavior cases. Put host-specific differences in a separate adapter instead of weakening or bloating the core Skill.
