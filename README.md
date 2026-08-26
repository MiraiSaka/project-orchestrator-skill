# Project Orchestrator Skill

A portable Agent Skill for turning substantial, multi-stage goals into correctable local project guidance, scoped workflow skills, and evidence-based acceptance.

It is designed for capable models: implementation methods stay open, while user intent, permissions, correction, validation, and delivery evidence remain strict.

> 中文简介：把完整、多阶段目标转化为可纠正的项目规范、本地 Skill、项目契约和证据化验收。严格控制结果与风险，但不固定强模型的实施方法。

Status: `0.1.0`. Validated through iterative cross-host testing with Codex and Claude/Opus.

## When it should activate

Use it for work that spans several stages or future sessions, such as research through implementation, data acquisition through reporting, or building through delivery and automation.

Do not use it for simple questions, one-off edits, ordinary format conversion, or discussion-only requests that do not authorize project files.

Codex and Claude may select it from the description. Explicit invocation is also available:

- Codex: `$project-orchestrator`
- Claude Code: `/project-orchestrator`

## What it adds

- A concise host-native project instruction file when durable guidance is useful.
- One scoped project-local Skill when a recurring domain workflow needs it.
- A project contract when goals, assumptions, permissions, or acceptance criteria must survive future sessions.
- Deterministic scripts only where repeated checks materially improve reliability.
- Immediate correction when the user changes or corrects the goal.
- Separation between audience-facing deliverables and internal validation evidence.

The Skill does not prescribe a fixed framework, tool set, implementation order, retry count, or agent count without a concrete reason.

## Repository layout

```text
.agents/skills/project-orchestrator/
|-- SKILL.md
|-- agents/openai.yaml
|-- references/
|   |-- artifact-contracts.md
|   |-- evaluation.md
|   `-- host-adapters.md
|-- scripts/
|   |-- instruction_state.py
|   `-- validate_project.py
evals/
|-- behavior-cases.json
`-- claude-opus-test.md
tests/
`-- ...
```

The directory `.agents/skills/project-orchestrator` is the single portable Skill source. Do not maintain separate Codex and Claude instruction copies in the repository.

## Download

- Repository: <https://github.com/MiraiSaka/project-orchestrator-skill>
- Recommended Skill-only ZIP: <https://github.com/MiraiSaka/project-orchestrator-skill/releases/download/v0.1.0/project-orchestrator-skill-v0.1.0.zip>
- GitHub source ZIP: <https://github.com/MiraiSaka/project-orchestrator-skill/archive/refs/tags/v0.1.0.zip>

The recommended ZIP contains one ready-to-copy `project-orchestrator` directory. Extract it, then place that directory in the appropriate Codex or Claude Skills location below.

## Install in Codex

After downloading or cloning this repository:

- Repository scope: keep the Skill at `<repo>/.agents/skills/project-orchestrator/`.
- User scope: copy that directory to `~/.agents/skills/project-orchestrator/`.
- GitHub installation: ask `$skill-installer`:

  ```text
  Install project-orchestrator from https://github.com/MiraiSaka/project-orchestrator-skill/tree/main/.agents/skills/project-orchestrator
  ```

Start a fresh task in the intended repository when testing discovery. Invoke it explicitly with `$project-orchestrator`, or describe a substantial multi-stage project and test implicit selection.

OpenAI's current Skill documentation: <https://learn.chatgpt.com/docs/build-skills>

## Install in Claude Code and test Opus

Copy the same `.agents/skills/project-orchestrator` directory to either:

- user scope: `~/.claude/skills/project-orchestrator/`;
- project scope: `<repo>/.claude/skills/project-orchestrator/`.

Start a fresh Claude Code conversation, select the available Opus model from `/model`, record the exact displayed model name, and use `/project-orchestrator` or a matching natural-language request.

Run the cases in [evals/claude-opus-test.md](evals/claude-opus-test.md). Do not tune the Skill after one stochastic run; reproduce a real invariant failure before changing the portable core.

Claude Code Skill reference: <https://code.claude.com/docs/en/skills>

## Validate

The scripts use the Python standard library. From the repository root:

```bash
python -m unittest discover -s tests -v
```

Validate a generated project:

```bash
python .agents/skills/project-orchestrator/scripts/validate_project.py <project-root> --host codex
python .agents/skills/project-orchestrator/scripts/validate_project.py <project-root> --host claude
```

Undefined reference-style labels are warnings because CommonMark can treat them as literal text. Explicit links or reference definitions whose local targets are missing remain errors.

A project-local Skill is optional. Add `--require-skill` only when the project design explicitly requires one; any discovered local Skills are validated either way. Use `--require-contract` similarly when a project contract is required.

Create an optional instruction-state receipt with the matching host. `--skill` is optional, and `--instruction-file` can override the host-native default:

```bash
python .agents/skills/project-orchestrator/scripts/instruction_state.py snapshot <project-root> --host codex
python .agents/skills/project-orchestrator/scripts/instruction_state.py snapshot <project-root> --host claude
```

These checks validate structure, links, metadata, and placeholders. They do not prove that a model understood the Skill or produced a strong solution; use the behavior cases for that.

## Security and publishing boundary

This repository contains workflow instructions and deterministic validators only. Do not publish generated project data, credentials, private reports, browsing state, local test workspaces, or instruction receipts.

External sends, publishing, deletion, spending, credential use, and other consequential mutations still require authorization at the point of action.

## License

MIT. See [LICENSE](LICENSE).
