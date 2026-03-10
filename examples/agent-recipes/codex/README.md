# Codex Recipe

This recipe shows the intended way to use Paper-Reach from a Codex-style coding agent.

## Assumptions

- the agent is operating inside the repository checkout
- the agent can read `AGENTS.md`
- the package is installed in the environment

If your Codex host scans installed skills, also run:

```bash
bash scripts/sync.sh
```

Paper-Reach ships Codex/OpenAI-style discovery metadata in [agents/openai.yaml](/home/nas/dailing/paper_reach/agents/openai.yaml).

## Minimal Flow

1. read [AGENTS.md](/home/nas/dailing/paper_reach/AGENTS.md)
2. choose the relevant skill from `skills/`
3. prepare a query file
4. run `paper-reach screen`
5. optionally run `paper-reach fetch-fulltext`
6. run `paper-reach review` or `paper-reach run`
7. consume JSON output

## Example Query

Use [query.json](/home/nas/dailing/paper_reach/examples/agent-recipes/codex/query.json).

## Commands

```bash
paper-reach screen \
  --input examples/agent-recipes/codex/query.json \
  --output examples/agent-recipes/codex/screen.json \
  --high-recall \
  --retrieval-limit 60
```

```bash
paper-reach run \
  --input examples/agent-recipes/codex/query.json \
  --output examples/agent-recipes/codex/result.json \
  --high-recall \
  --retrieval-limit 60
```

## Why This Pattern

The Codex-side prompt stays small. The real workflow lives in the CLI and schemas, which makes behavior more stable and testable.
