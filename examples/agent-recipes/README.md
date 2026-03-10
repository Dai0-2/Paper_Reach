# Agent Recipes

This directory contains minimal integration recipes for using Paper-Reach from coding-agent environments.

The recipes are intentionally lightweight:

- the agent reads repository guidance
- the agent prepares a query JSON
- the agent runs the CLI
- the agent consumes the JSON output

Current recipes:

- `codex/`
- `openclaw/`

Paper-Reach also ships host metadata in the repository root:

- `SKILL.md`
- `agents/openai.yaml`
- `.claude-plugin/plugin.json`
- `gemini-extension.json`

If your host expects skills in a dedicated directory, run:

```bash
bash scripts/sync.sh
```

This mirrors the skill bundle to common Claude/Codex/OpenAI-style locations.
