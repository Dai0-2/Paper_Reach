# OpenClaw Recipe

This recipe shows a minimal skill-oriented integration pattern for an OpenClaw-style agent runtime.

## Recommended Setup

- keep Paper-Reach installed as a normal Python package or editable repo
- expose this repository's root `SKILL.md` and `skills/` directory to the agent
- keep screening and review logic in the CLI

If the runtime expects an installed skill directory, run:

```bash
bash scripts/sync.sh
```

## Suggested Skill Mapping

- `paper-search` -> `paper-reach screen`
- `paper-reader` -> `paper-reach fetch-fulltext` or `paper-reach review`
- `paper-ranker` -> inspect the final JSON and produce the shortlist

## Example Query

Use [query.json](/home/nas/dailing/paper_reach/examples/agent-recipes/openclaw/query.json).

## Commands

```bash
paper-reach screen \
  --input examples/agent-recipes/openclaw/query.json \
  --output examples/agent-recipes/openclaw/screen.json \
  --high-recall \
  --retrieval-limit 80
```

```bash
paper-reach fetch-fulltext \
  --input examples/agent-recipes/openclaw/query.json \
  --output examples/agent-recipes/openclaw/review.json \
  --high-recall \
  --retrieval-limit 80 \
  --download-dir examples/agent-recipes/openclaw/downloads
```

## Why This Pattern

The runtime can swap prompts or skills, but the workflow stays consistent because the CLI output is the shared contract.
