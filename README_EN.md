<div align="center">

# 👁️ Paper-Reach

Give your AI agent a more rigorous literature search and screening workflow

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](pyproject.toml)
[![GitHub Stars](https://img.shields.io/github/stars/Dai0-2/Paper_Reach?style=social)](https://github.com/Dai0-2/Paper_Reach)

[Quick Start](#quick-start) · [中文](README.md) · [Supported Platforms](#supported-platforms) · [Design Philosophy](#design-philosophy)

</div>

---

## Why Paper-Reach?

`Paper-Reach` is an open-source Skill + CLI for literature retrieval, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is designed for AI coding agents such as Codex, Claude Code, OpenClaw, and Cursor, while also working as a standalone Python CLI.

The point is not “search more sources.” The point is “screen papers better with evidence.”

AI agents can already write code, edit docs, and manage repositories. But once you ask them to do a real literature review, they usually break down:

- “Find papers that truly match my criteria.” -> They overclaim from titles.
- “Tell me which papers actually use this dataset or supervision signal.” -> Abstract evidence is often too weak.
- “Download the paper and confirm the method.” -> PDF access fails, and the workflow stalls.
- “Give me a shortlist I can actually inspect.” -> The output becomes a giant JSON blob.

The hard part is not search. The hard part is **evidence-based screening**.

Paper-Reach turns that into a reusable workflow:

1. retrieve a large candidate pool
2. screen conservatively at abstract level
3. fetch full text when possible
4. review with stronger evidence
5. export results for both agents and humans

### Before You Use It

| Item | What it means |
|---|---|
| **Conservative by default** | Title-only relevance is never treated as strong evidence |
| **Agent-friendly** | Works both as a CLI and as a reusable skill bundle |
| **Graceful fallback** | If full text cannot be downloaded, the workflow still remains useful |
| **Human-readable output** | You get `brief` and `titles` exports, not just giant JSON |
| **Extensible** | Search backends, parsers, ranking profiles, and fetch logic are pluggable |

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

Export a shortlist for manual review:

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

The `bundle-dir` layout looks like this:

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

> Already installed? Updating is usually just:
>
> ```bash
> git pull
> pip install -e .[dev]
> ```

---

## Supported Platforms

| Platform | Works now | Better with configuration | How to enable |
|---|---|---|---|
| **OpenAlex** | Metadata retrieval, abstract screening | Official content API PDF download | Set `OPENALEX_API_KEY` |
| **arXiv** | Search and metadata retrieval | PDF / local review | No extra setup |
| **Local PDFs / TXT / JSON** | Offline screening and review | Stronger local evidence extraction | No extra setup |
| **Codex / OpenAI** | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| **Claude** | Skill discovery + CLI use | Bundle install | `bash scripts/sync.sh` |
| **Gemini** | Extension metadata included | Bundle install | `bash scripts/sync.sh` |

### How to Handle Cookie-Based Scholarly Platforms

Some scholarly platforms require login state or an institution-backed browser session.

For these platforms, the most practical approach is:

**browser login -> Cookie-Editor export -> pass cookies to the agent / Paper-Reach**

Recommended flow:

- sign in to the publisher platform in Chrome
- export cookies using the Chrome extension `Cookie-Editor`
- pass the cookie file to Paper-Reach with `--cookie-file`

Example:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

This is usually simpler and more reliable than trying to automate login or browser verification.

Cookie handling principles:

- cookies stay local
- cookies are never required for the core workflow
- if cookies are missing or invalid, Paper-Reach falls back gracefully

See [docs/browser-cookies.md](docs/browser-cookies.md) for details.

---

## Design Philosophy

Paper-Reach is not a heavyweight autonomous research framework.

It is a practical starter repo for literature workflow scaffolding.

Its core principles are:

- **Search is easy, screening is hard**
  - the value is in better screening, not just more sources
- **Weak evidence stays weak**
  - title-only relevance must not be overclaimed
- **Abstract and full text are different evidence levels**
  - abstract support is useful, but full-text support is stronger
- **Offline mode matters**
  - the workflow must still work with local PDFs, metadata files, and DOI lists
- **JSON first**
  - outputs should be reusable by agents and scripts
- **Human review still matters**
  - the project should produce shortlists that people can actually inspect

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

## Core Capabilities

- High-recall literature retrieval with query expansion
- Conservative abstract screening with explainable reasons
- Full-text review when PDFs are available
- OpenAlex-first download with automatic fallback
- Profile-based ranking with hard gates and weighted dimensions
- Compact human-facing outputs: `titles` and `brief`
- Structured full JSON output for agents and downstream analysis

## A Concrete Example

Here is a realistic query:

```json
{
  "topic": "China static population exposure assessment for disasters and infectious disease",
  "keywords": [
    "China",
    "static population",
    "gridded population",
    "census population",
    "population exposure",
    "population at risk",
    "disaster exposure",
    "hazard exposure",
    "infectious disease exposure",
    "WorldPop",
    "LandScan",
    "GPW"
  ],
  "inclusion_criteria": [
    "study area is in China",
    "uses static population data or gridded population as exposure input",
    "focuses on disaster exposure or infectious-disease exposure",
    "estimates exposed population or population at risk"
  ],
  "exclusion_criteria": [
    "study area outside China only",
    "not an exposure study",
    "generic epidemiology without exposure modeling",
    "dynamic mobility only without static population baseline"
  ],
  "year_range": [2005, 2026],
  "max_results": 200,
  "need_gap_analysis": true,
  "mode": "auto",
  "require_fulltext_for_selection": false,
  "profile": "static_population_exposure_baseline"
}
```

## OpenAlex-First Download

If `OPENALEX_API_KEY` or `OPENALEX_CONTENT_API_KEY` is configured, Paper-Reach will try the OpenAlex content API first:

```bash
export OPENALEX_API_KEY=your_key
```

Download priority:

1. OpenAlex content API
2. open-access PDF URL
3. landing page extraction
4. cookie / header session reuse
5. abstract-only fallback

The OpenAlex API key is an enhancement, not a hard requirement.

## Multi-Host Skill Support

Paper-Reach follows the same structure used by mature cross-host skill projects:

- one shared execution engine
  - `paper-reach` CLI + `paper_reach/`
- one host-agnostic skill entrypoint
  - `SKILL.md`
- several host-specific lightweight manifests
  - `agents/openai.yaml`
  - `.claude-plugin/plugin.json`
  - `gemini-extension.json`

This keeps the core logic in one place while making the skill discoverable across different agent ecosystems.

## Repository Structure

```text
paper-reach/
├─ README.md
├─ README_EN.md
├─ AGENTS.md
├─ SKILL.md
├─ docs/
├─ examples/
├─ skills/
├─ agents/
├─ .claude-plugin/
├─ paper_reach/
├─ scripts/
└─ tests/
```

## Documentation

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)
