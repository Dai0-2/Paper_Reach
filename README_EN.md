<div align="center">

# 👁️ Paper-Reach

Give your AI agent a rigorous literature review workflow.

MIT License · Python 3.8+ · Agent Skill · Literature Workflow

[Quick Start](#quick-start) · [中文](README.md) · [Supported Platforms](#supported-platforms) · [Design Philosophy](#design-philosophy)

</div>

`Paper-Reach` is an open-source skill + CLI for literature search, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is designed for coding agents such as Codex, Claude Code, OpenClaw, Cursor, and similar tools, while also working as a standalone Python CLI.

## Why Paper-Reach?

AI agents can already write code, edit docs, and manage repositories. But once you ask them to do a real literature review, they often fail in predictable ways:

- They overclaim from title-only matches.
- They treat abstract-only evidence as stronger than it is.
- They stall when a PDF cannot be downloaded.
- They return giant JSON outputs that humans do not want to inspect.

The hard part is not search. The hard part is evidence-based screening.

Paper-Reach turns that into a repeatable workflow:

1. retrieve a large candidate pool
2. screen conservatively at abstract level
3. fetch full text when possible
4. review with stronger evidence
5. export both machine-readable and human-readable outputs

## Quick Start

Install locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

Generate a sample query:

```bash
paper-reach example-query > query.json
```

Run the full workflow:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

Export a human-readable shortlist:

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

The bundled run directory looks like this:

```text
runs/demo/
├─ 00_query.json
├─ 10_screen.json
├─ 20_fetched_papers.json
├─ 30_result_full.json
├─ 40_result_brief.json
├─ 50_result_titles.json
├─ manifest.json
└─ downloads/
```

## Supported Platforms

| Platform | Works now | Better with configuration | How to enable |
|---|---|---|---|
| **OpenAlex** | Metadata retrieval and abstract screening | Official content API PDF download | Set `OPENALEX_API_KEY` |
| **arXiv** | Search and metadata retrieval | PDF / local review | No extra setup |
| **Local PDFs / TXT / JSON** | Offline screening and review | Stronger local evidence extraction | No extra setup |
| **Publisher landing pages** | Best-effort OA fallback | Session reuse for gated content | Provide cookies / headers |
| **Codex / OpenAI-style hosts** | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| **Claude-style hosts** | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| **Gemini-style hosts** | Extension metadata included | Bundle install | `bash scripts/sync.sh` |

### Cookie-Based Access for Scholarly Platforms

Some scholarly platforms require login or an institution-backed browser session.

For platforms that need cookies, the most practical setup is:

**browser login -> Cookie-Editor export -> send cookies to the agent -> run Paper-Reach**

Example:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

This is usually simpler and more reliable than trying to automate login or browser verification flows.

For details, see [docs/browser-cookies.md](docs/browser-cookies.md).

## Design Philosophy

Paper-Reach is not a heavyweight autonomous research framework.

It is a practical starter repo for literature workflow scaffolding.

The main design principles are:

- Search is easy, screening is hard.
- Weak evidence should remain weak.
- Abstract and full text are different evidence levels.
- Offline mode matters.
- JSON should remain the primary interchange format.
- Human review still matters.

## OpenAlex-First Full-Text Fetching

If `OPENALEX_API_KEY` or `OPENALEX_CONTENT_API_KEY` is configured, Paper-Reach tries the OpenAlex content API first:

```bash
export OPENALEX_API_KEY=your_key
```

The OpenAlex API key is optional. Without it, Paper-Reach falls back to open-access URLs, landing page extraction, cookie/header session reuse, and abstract-only review.

## Documentation

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)
