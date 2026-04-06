<h1 align="center">Paper-Reach</h1>

<p align="center">
  <strong>Give your AI agent a rigorous literature review workflow.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
</p>

<p align="center">
  <a href="#quick-start">快速开始</a> · <a href="#english-overview">English</a> · <a href="#supported-platforms">支持平台</a> · <a href="#design-philosophy">设计理念</a>
</p>

---

## English Overview

Paper-Reach is an open-source skill + CLI scaffold for literature search, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is designed for Codex, Claude Code, OpenClaw, Cursor, and similar coding agents, but it also works as a normal Python command-line tool.

Most paper-search workflows fail in the same way:

- a title match is treated like real relevance
- abstract-only evidence is overclaimed
- blocked PDF downloads stop the workflow
- final outputs are too verbose for humans and too messy for agents

Paper-Reach fixes this by separating the review process into explicit stages:

- retrieve candidate papers
- screen papers conservatively from title and abstract
- fetch full text when available
- review downloaded papers with stronger evidence
- export both full JSON and compact human-readable lists

The core idea is simple: **search is easy; evidence-based screening is hard.**

## What's New

- OpenAlex Content API is used first when an API key is configured
- `run --bundle-dir` writes a full run bundle with every stage output
- `summarize` exports compact `titles` and `brief` views for human review
- profile-based ranking supports task-specific hard gates and weighted scoring
- multi-host skill packaging is included for Codex, Claude-style, and Gemini-style hosts

## Core Capabilities

- ✅ high-recall scholarly retrieval with multi-query expansion
- ✅ conservative abstract screening with explainable reasons
- ✅ full-text fetching with graceful fallback when PDFs are unavailable
- ✅ OpenAlex-first PDF fetching when API access is configured
- ✅ offline review from local PDFs, TXT files, metadata JSON, DOI lists, and title lists
- ✅ structured evidence and ranking outputs for downstream agents
- ✅ compact exports for people: `titles` and `brief`
- ✅ reusable Skill packaging for multiple agent hosts

## Supported Platforms

| Source / capability | Works by default | Config unlocks | How to configure |
|---|---:|---:|---|
| OpenAlex metadata search | ✅ | broader and better PDF access | optional `OPENALEX_API_KEY` |
| OpenAlex Content API | — | official PDF download when content is available | `export OPENALEX_API_KEY=...` |
| arXiv search | ✅ | — | no setup |
| Local PDFs / TXT / JSON metadata | ✅ | — | pass `--local-path` or use offline mode |
| Open-access PDF URLs | ✅ | — | no setup |
| Publisher landing pages | ✅ | better results with session headers | optional cookie/header files |
| Login-required sites | — | session reuse | export cookies from your browser |
| PDF parsing | basic fallback | stronger parsing | optional `pymupdf` |
| Agent hosts | ✅ | skill discovery | `bash scripts/sync.sh` |

Need cookies for a login-required site?

Use the same simple flow every time:

```text
Browser login -> Cookie-Editor export -> give the cookie file to your agent -> run Paper-Reach
```

Recommended browser extension:

- Chrome Cookie-Editor: https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm

Example:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/my-topic \
  --cookie-file ./cookies.json \
  --header-file ./headers.json
```

Cookies stay local. Do not commit them to GitHub.

## Quick Start

Install locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

Run a demo query:

```bash
paper-reach example-query > query.json

paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

Export a compact reading list:

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

The run bundle looks like this:

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

## Example: Static Population Exposure Review

Suppose you want to study why dynamic population data is better than static population data for exposure assessment. You first need a baseline pool of papers that use static or gridded population data.

Example query:

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

Run:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/china_static_population \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

If an OpenAlex key is configured, Paper-Reach will try OpenAlex's official content API first:

```bash
export OPENALEX_API_KEY=your_key
```

If the content API is unavailable, quota-limited, or the paper has no OpenAlex-hosted PDF, Paper-Reach automatically falls back to the default open-access and landing-page fetchers.

## How Agents Use It

Paper-Reach is not just a prompt collection. It is a small execution engine plus host-specific skill metadata.

Install the skill bundle:

```bash
pip install -e .[dev]
bash scripts/sync.sh
bash scripts/check-install.sh
```

Common install targets:

- `~/.codex/skills/paper-reach`
- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`

Agent-facing files:

- `SKILL.md`
- `AGENTS.md`
- `skills/paper-search/SKILL.md`
- `skills/paper-reader/SKILL.md`
- `skills/paper-ranker/SKILL.md`

Host metadata:

- `agents/openai.yaml`
- `.claude-plugin/plugin.json`
- `gemini-extension.json`

## Design Philosophy

Paper-Reach is scaffolding, not a heavyweight research automation framework.

It should help an agent do the boring parts reliably:

- generate a high-recall candidate pool
- keep title-only relevance weak
- use abstract evidence for coarse screening
- prefer full-text evidence when available
- mark weak evidence as ambiguous
- export both complete and compact outputs

It should not pretend to solve access control, publisher restrictions, or all of literature review quality in one giant autonomous system.

The best default behavior is conservative:

- no full text means no strong claim
- weak abstract evidence means ambiguous, not selected
- blocked downloads should not stop the run
- human-readable shortlists should be generated from the full trace

## Repository Structure

```text
paper-reach/
├─ README.md
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

Key directories:

- `paper_reach/` — CLI, workflow, models, ranking, fetchers, parsers
- `skills/` — paper-search, paper-reader, paper-ranker
- `examples/` — example queries, auth examples, agent recipes
- `docs/` — install, usage, architecture, roadmap, publishing
- `scripts/` — skill sync and install checks

## Documentation

- [Install](docs/install.md)
- [Usage](docs/usage.md)
- [Architecture](docs/architecture.md)
- [Agent integration](docs/agent-integration.md)
- [Browser cookies](docs/browser-cookies.md)
- [Publishing](docs/publishing.md)
- [Roadmap](docs/roadmap.md)

## Contributing

Contributions are most useful when they improve:

- screening quality
- evidence extraction
- backend extensibility
- offline usability
- agent integration

Keep the core modular, conservative, and easy to inspect.
