<div align="center">

# 👁️ Paper-Reach

Give your AI agent a rigorous literature review workflow

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8%2B](https://img.shields.io/badge/python-3.8%2B-blue.svg)](pyproject.toml)
[![GitHub Stars](https://img.shields.io/github/stars/Dai0-2/paper_reach?style=social)](https://github.com/Dai0-2/paper_reach)

[Quick Start](#quick-start) · [Chinese](README.md) · [Supported Platforms](#supported-platforms) · [Design Philosophy](#design-philosophy)

</div>

---

## Why Paper-Reach?

`Paper-Reach` is an open-source skill + CLI for literature retrieval, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is designed for AI coding agents such as Codex, Claude Code, OpenClaw, and Cursor, while also working as a standalone Python CLI.

The point is not “search more sources.” The point is “screen papers better with evidence.”

Many agents can already find paper titles and abstracts. But when asked to do a real literature review, they tend to break down:

- they overclaim from titles
- abstract evidence is often too weak
- PDF access fails and stalls the workflow
- the final output is too large for humans to inspect

Paper-Reach turns this into a reusable workflow:

1. retrieve a large candidate pool
2. screen conservatively at abstract level
3. fetch full text when possible
4. review using abstract or full-text evidence
5. export both full JSON and compact human-readable outputs

## Quick Start

Install:

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

Run abstract-level screening:

```bash
paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

Run the full workflow and save every stage:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

Export a shortlist:

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

## Supported Platforms

| Platform | Works now | Better with configuration | How to enable |
|---|---|---|---|
| **OpenAlex** | Metadata retrieval, abstract screening | Official content API PDF download | Set `OPENALEX_API_KEY` |
| **arXiv** | Search and metadata retrieval | PDF / local review | No extra setup |
| **Local PDFs / TXT / JSON** | Offline screening and review | Stronger local evidence extraction | No extra setup |
| **Publisher landing pages** | Best-effort OA fallback | Session reuse for gated content | Provide cookies / headers |
| **Codex / OpenAI-style hosts** | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| **Claude-style hosts** | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| **Gemini-style hosts** | Extension metadata included | Bundle install | `bash scripts/sync.sh` |

### Cookie-Based Access for Scholarly Platforms

Some scholarly platforms require login or an institution-backed browser session.

For these platforms, the most practical setup is:

**browser login -> Cookie-Editor export -> send cookies to the agent -> run Paper-Reach**

Recommended flow:

- log into the publisher site in Chrome
- use the Chrome extension `Cookie-Editor` to export cookies
- pass the cookie file to Paper-Reach with `--cookie-file`

Example:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

This is usually simpler and more reliable than trying to automate login or verification flows.

## Design Philosophy

Paper-Reach is not a heavyweight autonomous research framework.

It is a practical starter repo for literature workflow scaffolding.

Core principles:

- search is easy, screening is hard
- weak evidence stays weak
- abstract and full text are different evidence levels
- offline mode matters
- JSON first
- human review still matters

### What Paper-Reach Is

- a reusable literature workflow for AI agents
- a Python CLI
- a multi-host skill bundle
- a starter scaffold for literature review and gap analysis

### What Paper-Reach Is Not

- a giant autonomous multi-agent system
- a promise that every paper can always be downloaded
- a black-box ranking engine with hidden logic

## Documentation

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)
