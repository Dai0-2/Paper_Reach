<div align="center">

# 🔎 Paper-Reach

Give your AI agent a rigorous literature review workflow

An open-source skill + CLI for literature search, abstract screening, full-text review, evidence extraction, and conservative ranking.

MIT License · Python 3.8+ · Agent Skill · OpenAlex Ready

[Quick Start](#quick-start) · [中文](README.md) · [Supported Platforms](#supported-platforms) · [Design Philosophy](#design-philosophy)

</div>

---

## Why Paper-Reach?

AI agents can already write code, edit docs, and manage repositories. But once you ask them to do a real literature review, they usually break down:

- "Find papers on this topic and keep only the ones that actually match my criteria." -> They overclaim from titles.
- "Tell me which papers really use this dataset or supervision signal." -> Abstract evidence is often too weak.
- "Download the paper and confirm the method." -> PDF access fails, and the workflow stalls.
- "Give me a shortlist I can actually read." -> The output is a giant JSON blob.

The hard part is not search. The hard part is evidence-based screening.

Paper-Reach turns that into a repeatable workflow:

1. retrieve a large candidate pool
2. screen conservatively at abstract level
3. fetch full text when possible
4. review with stronger evidence
5. export both machine-readable and human-readable outputs

### Before You Use It

| Item | What it means |
|---|---|
| Conservative by default | Title-only relevance is never treated as strong evidence |
| Agent-friendly | Works as both a CLI and a reusable skill bundle |
| Graceful fallback | If full text cannot be downloaded, the workflow still remains useful |
| Human-readable output | You get `brief` and `titles` exports, not just giant JSON |
| Extensible | Search backends, parsers, ranking profiles, and fetch logic are pluggable |

---

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

Run a high-recall screening pass:

```bash
paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

Run the full workflow and save all intermediate outputs:

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

---

## Supported Platforms

| Platform | Works now | Better with configuration | How to enable |
|---|---|---|---|
| OpenAlex | Metadata retrieval, abstract screening | Official content API PDF download | Set `OPENALEX_API_KEY` |
| arXiv | Search and metadata retrieval | PDF / local review | No extra setup |
| Local PDFs / TXT / JSON | Offline screening and review | Stronger local evidence extraction | No extra setup |
| Publisher landing pages | Best-effort OA fallback | Session reuse for gated content | Provide cookies / headers |
| Codex / OpenAI-style hosts | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| Claude-style hosts | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| Gemini-style hosts | Extension metadata included | Bundle install | `bash scripts/sync.sh` |

### Cookie-Based Access for Scholarly Platforms

Some scholarly platforms require login or an institution-backed browser session.

For platforms that need cookies, the most practical setup is:

browser login -> Cookie-Editor export -> give cookies to the agent -> run Paper-Reach

Recommended approach:

- log into the publisher site in Chrome
- use the Chrome extension `Cookie-Editor` to export cookies
- pass the cookie file to Paper-Reach

Example:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

This is usually simpler and more reliable than trying to automate login or browser verification flows.

---

## Design Philosophy

Paper-Reach is not a heavyweight autonomous research framework.

It is a practical starter repo for literature workflow scaffolding.

The main design principles are:

- Search is easy, screening is hard
- Weak evidence stays weak
- Abstract and full text are different evidence levels
- Offline mode matters
- JSON first
- Human review still matters

### What Paper-Reach Is

- a reusable literature workflow for AI agents
- a Python CLI
- a multi-host skill bundle
- a starter scaffold for literature review and research-gap analysis

### What Paper-Reach Is Not

- a giant autonomous multi-agent system
- a promise that every paper can always be downloaded
- a black-box ranking engine with hidden logic

---

## OpenAlex-First Full-Text Fetching

If `OPENALEX_API_KEY` or `OPENALEX_CONTENT_API_KEY` is configured, Paper-Reach tries the OpenAlex content API first:

```bash
export OPENALEX_API_KEY=your_key
```

Download priority:

1. OpenAlex content API
2. open-access PDF URL
3. landing page extraction
4. cookie / header session reuse
5. abstract-only fallback

This means the OpenAlex API key is optional, not required.

## Documentation

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)
