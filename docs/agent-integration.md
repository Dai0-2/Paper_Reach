# Agent Integration

## Goal

Paper-Reach is designed to be usable in two ways:

1. as a normal Python CLI and library
2. as a skill-backed workflow for coding agents

The repository does not require a specific agent runtime. Instead, it provides:

- a root `SKILL.md` for host discovery
- an agent-friendly `AGENTS.md`
- reusable skills under `skills/`
- a CLI that performs the real workflow steps
- thin host-specific metadata files for discovery and installation

This separation keeps the project portable across agent environments.

## Integration Layers

Paper-Reach uses four layers:

1. execution layer: the `paper-reach` CLI and `paper_reach/` package
2. repository guidance layer: `AGENTS.md`
3. host-agnostic skill layer: `SKILL.md` plus the task-specific files in `skills/`
4. host-specific discovery layer:
   - `agents/openai.yaml`
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `gemini-extension.json`

This mirrors the pattern used by multi-host skills that support Claude-style plugins, Codex/OpenAI-style skill discovery, and Gemini-style extensions without duplicating the core workflow.

## Recommended Integration Pattern

Use Paper-Reach as an external workflow tool rather than reimplementing literature screening in prompts.

Recommended pattern:

1. the agent reads `AGENTS.md`
2. the agent picks the relevant skill from `skills/`
3. the agent prepares a query JSON
4. the agent calls the CLI
5. the agent reads the resulting JSON and continues reasoning from structured outputs

## Codex-Style Integration

For Codex-like agents working inside the repository:

- keep the repository checked out locally
- expose the root `SKILL.md` in a known skill location if the host expects installed skills
- let the agent operate inside the repo root
- rely on `AGENTS.md` and `skills/` for workflow guidance
- use the CLI commands directly

Typical flow:

```bash
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json --high-recall
paper-reach review --input query.json --output review.json --local-path ./papers
```

For skill discovery metadata, Paper-Reach ships [agents/openai.yaml](/home/nas/dailing/paper_reach/agents/openai.yaml).

## OpenClaw Or Similar Skill-Based Agents

For agents that support reusable skill folders:

- point the agent to the repository root or an installed `paper-reach` skill directory
- let the host discover [SKILL.md](/home/nas/dailing/paper_reach/SKILL.md)
- keep the executable workflow in the installed `paper-reach` CLI
- do not duplicate business logic into skill prompts

Suggested mapping:

- `paper-search` -> run `paper-reach screen`
- `paper-reader` -> run `paper-reach review` or `paper-reach fetch-fulltext`
- `paper-ranker` -> interpret final review outputs and produce a ranked shortlist

## Installation Models

### Model A: repo-local usage

Best for development and contribution.

```bash
git clone <repo>
cd paper-reach
pip install -e .[dev]
```

If your host can work directly from the repository, this is usually enough.

### Model B: package installation

Best for using Paper-Reach as a shared tool from other repositories.

```bash
pip install paper-reach
```

This assumes the package is published or installed from a source URL.

### Model C: sync to common skill directories

Best for hosts that scan a dedicated skill folder.

```bash
pip install -e .[dev]
bash scripts/sync.sh
```

This copies the root skill entrypoint, host manifests, integration docs, and task-specific skills into:

- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`
- `~/.codex/skills/paper-reach`

The sync script is intentionally simple. It does not publish the package or create virtual environments. It only mirrors the skill bundle to common host locations.

## Host Metadata Files

- [SKILL.md](/home/nas/dailing/paper_reach/SKILL.md): shared skill entrypoint with host-agnostic instructions
- [agents/openai.yaml](/home/nas/dailing/paper_reach/agents/openai.yaml): discovery metadata for OpenAI-style/Codex hosts
- [.claude-plugin/plugin.json](/home/nas/dailing/paper_reach/.claude-plugin/plugin.json): Claude plugin metadata
- [.claude-plugin/marketplace.json](/home/nas/dailing/paper_reach/.claude-plugin/marketplace.json): Claude marketplace metadata
- [gemini-extension.json](/home/nas/dailing/paper_reach/gemini-extension.json): Gemini extension metadata

## Skills Versus CLI

The skills should remain thin and reusable.

- skills explain when and why to run a workflow step
- CLI commands execute the workflow
- JSON outputs are the interface between agent reasoning and workflow execution

This is deliberate. It keeps the project:

- easier to test
- easier to version
- easier to integrate across agent platforms

## Offline And Restricted Environments

Agents should not assume open internet access.

Paper-Reach supports:

- fully offline screening from local files
- mixed online/offline operation
- graceful degradation when external APIs fail

Restricted full-text access should be represented explicitly in outputs instead of hidden behind vague failure messages.

## Suggested Future Packaging

If you want stronger agent portability later, add:

- a published PyPI package
- host-specific validation hooks where they provide real value
- install snippets for Cursor or future hosts
- packaging automation that keeps host manifests versioned together

See [examples/agent-recipes/README.md](/home/nas/dailing/paper_reach/examples/agent-recipes/README.md) for starter recipes.
