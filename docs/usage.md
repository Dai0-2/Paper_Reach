# Usage

Paper-Reach can be used in two modes:

- as a normal CLI for developers
- as a skill-backed workflow for Codex, Claude Code, OpenClaw-style hosts, and similar runtimes

The execution layer is always the same: the `paper-reach` CLI.

## Check Your Installation

```bash
bash scripts/check-install.sh
```

If you want host-specific skill discovery, sync the bundle first:

```bash
bash scripts/sync.sh
```

## Search Papers Online

Create a query file:

```bash
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json --mode online
paper-reach fetch-fulltext --input query.json --output review.json --mode online --download-dir ./downloads
```

This will try online scholarly channels first. If a backend fails, the workflow continues with whichever channels succeed.

For broader candidate recall:

```bash
paper-reach screen --input query.json --output screen.json --mode online --high-recall --retrieval-limit 120
```

With a user-authorized session:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --mode online \
  --download-dir ./downloads \
  --cookie-file ./cookies.json \
  --header-file ./headers.json
```

## Screen A Folder Of Local PDFs

```bash
paper-reach review --input query.json --output result.json --mode offline --local-path ./downloads
```

Behavior:

- `.txt` files are parsed directly
- `.pdf` files are parsed if PyMuPDF is installed
- `.json` metadata files are loaded as local candidate records

## Combine Online And Offline Inputs

```bash
paper-reach run --input query.json --output result.json --mode auto --local-path ./downloads --channel openalex --channel local_files
```

This is useful when you want remote discovery plus local evidence extraction.

## Inspect JSON Output

The output file contains:

- `query_summary`
- `screening_candidates`
- `selected`
- `ambiguous`
- `rejected`
- `gap_analysis`
- `recommended_next_queries`

Notable explainability fields:

- `query_summary.search_plan`
- `screening_candidates[].screening_dimensions`
- `screening_candidates[].abstract_findings`

Optional stricter query fields:

- `must_include`
- `soft_include`
- `must_exclude`

You can inspect the result with:

```bash
python -m json.tool result.json
```

## CLI Reference

```bash
paper-reach doctor
paper-reach example-query
paper-reach screen --input query.json --output screen.json
paper-reach fetch-fulltext --input query.json --output review.json
paper-reach review --input query.json --output result.json
paper-reach summarize --input result.json --output titles.json --format titles
paper-reach version
paper-reach run --input query.json --output result.json
```

## Export A Compact Human View

Keep the full workflow JSON for reproducibility, then export a short list for manual reading.

Titles only:

```bash
paper-reach summarize --input result.json --output titles.json --format titles
```

Brief view with title, URL, decision, reasons, and a few extracted fields:

```bash
paper-reach summarize --input result.json --output brief.json --format brief
```

## Use From A Codex Or Similar Agent

The simplest pattern is:

1. install Paper-Reach normally
2. let the agent read `AGENTS.md`
3. let the host discover `SKILL.md` if it supports installed skills
4. have the agent call the CLI instead of reproducing workflow logic in prompts

Minimal setup:

```bash
pip install -e .[dev]
bash scripts/sync.sh
```

Then the host can discover one of these installed paths:

- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`
- `~/.codex/skills/paper-reach`

Typical agent execution:

```bash
paper-reach screen --input query.json --output screen.json --high-recall --retrieval-limit 120
paper-reach review --input query.json --output review.json --local-path ./papers
```

## Practical Tips

- Keep `require_fulltext_for_selection` enabled when false positives are costly.
- Use offline mode for reproducibility when you already have a vetted paper set.
- Treat `ambiguous` as the queue for manual review or deeper parsing.

## More

- agent integration: [docs/agent-integration.md](/home/nas/dailing/paper_reach/docs/agent-integration.md)
- end-to-end examples: [examples/README.md](/home/nas/dailing/paper_reach/examples/README.md)
- agent recipes: [examples/agent-recipes/README.md](/home/nas/dailing/paper_reach/examples/agent-recipes/README.md)
- publishing and releases: [docs/publishing.md](/home/nas/dailing/paper_reach/docs/publishing.md)
- browser session export: [docs/browser-cookies.md](/home/nas/dailing/paper_reach/docs/browser-cookies.md)
