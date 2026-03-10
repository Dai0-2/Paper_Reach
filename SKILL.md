---
name: paper-reach
version: "0.1.0"
description: "Run evidence-aware literature screening with Paper-Reach. Search candidate papers, screen abstracts conservatively, review full text when available, and emit structured JSON."
argument-hint: "screen topic query.json, review local PDFs, run literature screening for a research question"
allowed-tools: Bash, Read, Write
homepage: https://github.com/Dai0-2/paper_reach
repository: https://github.com/Dai0-2/paper_reach
author: Paper-Reach contributors
license: MIT
user-invocable: true
---

# Paper-Reach Skill

Use this skill when the user wants a rigorous literature-review workflow rather than ad hoc web search.

## Purpose

Paper-Reach is a reusable screening workflow for:

- candidate paper retrieval
- conservative abstract screening
- optional full-text fetching and review
- evidence extraction
- rubric-based ranking
- JSON-first outputs for literature review and gap analysis

## Host-Agnostic Workflow

1. Find the Paper-Reach installation root if you need repository files.
2. Read `AGENTS.md` for repository-wide expectations.
3. Use the relevant sub-skill under `skills/`:
   - `skills/paper-search/SKILL.md`
   - `skills/paper-reader/SKILL.md`
   - `skills/paper-ranker/SKILL.md`
4. Prefer the installed `paper-reach` CLI over reimplementing screening logic in prompts.
5. Consume the generated JSON and reason from explicit evidence and conservative decisions.

## Finding The Repository Root

If the current working directory is not obviously the repo root, search these common locations and use the first directory that contains both `AGENTS.md` and `paper_reach/cli.py`:

```bash
for dir in \
  "." \
  "${CLAUDE_PLUGIN_ROOT:-}" \
  "${GEMINI_EXTENSION_DIR:-}" \
  "$HOME/.claude/skills/paper-reach" \
  "$HOME/.agents/skills/paper-reach" \
  "$HOME/.codex/skills/paper-reach"; do
  [ -n "$dir" ] && [ -f "$dir/AGENTS.md" ] && [ -f "$dir/paper_reach/cli.py" ] && PAPER_REACH_ROOT="$dir" && break
done
```

If you only need execution and the package is already installed, you can skip repository path discovery and call the CLI directly.

## Execution Preference

Prefer these commands:

```bash
paper-reach doctor
paper-reach example-query
paper-reach screen --input query.json --output screen.json --high-recall --retrieval-limit 120
paper-reach review --input query.json --output review.json --local-path ./papers
paper-reach fetch-fulltext --input query.json --output review.json --download-dir ./downloads
paper-reach run --input query.json --output result.json
```

Fallback if the console script is unavailable:

```bash
python -m paper_reach.cli doctor
python -m paper_reach.cli screen --input query.json --output screen.json
```

## Guardrails

- Never treat title-only relevance as enough for final selection.
- Treat abstract-only support as coarse evidence.
- Keep unsupported papers as `ambiguous` or `need_fulltext`.
- Prefer JSON outputs over free-form prose when handing results back to the user or another agent step.
- If remote retrieval fails, fall back to offline mode or local files instead of inventing evidence.
