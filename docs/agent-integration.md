# Agent Integration

## Goal

Paper-Reach is designed to be usable in two ways:

1. as a normal Python CLI and library
2. as a skill-backed workflow for coding agents

The repository does not require a specific agent runtime. Instead, it provides:

- an agent-friendly `AGENTS.md`
- reusable skills under `skills/`
- a CLI that performs the real workflow steps

This separation keeps the project portable across agent environments.

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
- let the agent operate inside the repo root
- rely on `AGENTS.md` and `skills/` for workflow guidance
- use the CLI commands directly

Typical flow:

```bash
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json --high-recall
paper-reach review --input query.json --output review.json --local-path ./papers
```

## OpenClaw Or Similar Skill-Based Agents

For agents that support reusable skill folders:

- point the agent to this repository's `skills/` directory
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

### Model B: package installation

Best for using Paper-Reach as a shared tool from other repositories.

```bash
pip install paper-reach
```

This assumes the package is published or installed from a source URL.

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
- install snippets for Codex/OpenClaw/Claude Code/Cursor
- a small `examples/agent-recipes/` directory
- optional one-command setup scripts for local skill linking

See [examples/agent-recipes/README.md](/home/nas/dailing/paper_reach/examples/agent-recipes/README.md) for starter recipes.
