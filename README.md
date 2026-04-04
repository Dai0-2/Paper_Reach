<h1 align="center">Paper-Reach</h1>

<p align="center">
  <strong>Give your AI agent a rigorous literature review workflow.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <img src="https://img.shields.io/badge/Skill-Codex%20%7C%20Claude%20%7C%20OpenClaw-black.svg?style=for-the-badge" alt="Agent Skill">
</p>

<p align="center">
  <a href="#quick-start">快速开始</a> · <a href="#english">English</a> · <a href="#supported-platforms">支持平台</a> · <a href="#design-philosophy">设计理念</a>
</p>

---

## English

`Paper-Reach` is an open-source skill + CLI scaffold for literature search, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is built for coding agents such as Codex, Claude Code, OpenClaw, Cursor, and similar tools, but it also works as a standalone Python CLI.

The goal is simple:

> Searching papers is easy. Screening papers with evidence is hard.

Paper-Reach helps an AI agent do the literature-review workflow in a reproducible way:

- retrieve candidate papers from online or offline sources
- screen papers conservatively using title, abstract, and metadata
- fetch full text when available
- review downloaded papers with stronger evidence
- rank results with task-specific rubrics
- export both full JSON and human-readable shortlists

---

## Why Paper-Reach?

Most paper-search workflows fail in predictable ways:

- A title looks relevant, but the abstract does not support the claim.
- An abstract looks relevant, but the full text does not contain the required method, dataset, or study area.
- Some papers cannot be downloaded, but the agent still acts as if it read them.
- Final outputs are giant JSON files that humans cannot quickly inspect.

Paper-Reach separates these stages explicitly:

1. `screen`
   - high-recall search and abstract-level screening
2. `fetch-fulltext`
   - PDF/full-text acquisition with graceful fallback
3. `review`
   - full-text-first review when possible, abstract-level review otherwise
4. `summarize`
   - compact `titles` or `brief` output for human review

---

## What's New

- OpenAlex content API is used first when `OPENALEX_API_KEY` or `OPENALEX_CONTENT_API_KEY` is configured.
- `run --bundle-dir` writes a complete run folder with each stage output.
- `summarize` exports compact `titles` and `brief` views.
- profile-based ranking supports task-specific hard gates and weighted scoring.
- multi-host skill packaging is included for Codex, Claude-style, Gemini-style, and OpenClaw-style agent hosts.

---

## Supported Platforms

### Agent Hosts

| Host | Status | How it works |
|------|--------|--------------|
| Codex / OpenAI-style agents | Supported | Uses `SKILL.md`, `AGENTS.md`, and `agents/openai.yaml` |
| Claude Code / Claude-style skills | Supported | Uses `.claude-plugin/plugin.json` and skill bundle files |
| OpenClaw-style agents | Supported | Uses the synced skill directory and CLI execution |
| Cursor / Windsurf / similar coding agents | Supported | Works as a normal CLI plus readable skill instructions |

### Literature Sources

| Source | Search | Full text | Notes |
|--------|--------|-----------|-------|
| OpenAlex | Supported | Best with API key | Uses metadata first, then OpenAlex content API when configured |
| arXiv | Supported | Limited | Useful for preprints and technical papers |
| Local files | Supported | Supported | PDFs, TXT files, metadata JSON, DOI/title lists |
| Publisher landing pages | Fallback | Best effort | May fail on login walls, Cloudflare, or institutional restrictions |
| User-provided cookies/headers | Optional | Supported | For user-authorized sessions only |

> Need full text from login-protected sites? Use the same pattern as web-agent tools:
>
> Browser login → export cookies with [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) → give the cookie file to your agent → run Paper-Reach with `--cookie-file`.
>
> This is usually more reliable than QR-code login flows and keeps credentials local. Cookies are sensitive credentials; use a dedicated account when possible and never commit cookie files to GitHub.

---

## Quick Start

### Install the CLI

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

### Install as an agent skill bundle

```bash
pip install -e .[dev]
bash scripts/sync.sh
bash scripts/check-install.sh
```

Common skill targets:

- `~/.codex/skills/paper-reach`
- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`

### Run a complete literature workflow

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

This produces:

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

### Export a human-readable shortlist

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

Or export only titles and URLs:

```bash
paper-reach summarize \
  --input result.json \
  --output titles.json \
  --format titles \
  --top-k 20
```

---

## Example: Static Population Exposure Baseline

Suppose you want to find papers that use static or gridded population data in China for disaster or infectious-disease exposure assessment. You want these papers as baselines for comparing dynamic population methods.

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

Expected workflow:

- retrieve up to 200 candidate papers
- keep plausible matches after abstract screening
- download available full text using OpenAlex and open-access fallbacks
- rank reviewed papers with the task profile
- write both full results and compact top-ranked summaries

---

## Optional: OpenAlex Content API

Paper-Reach works without an OpenAlex API key, but full-text retrieval is better with one.

Configure either variable:

```bash
export OPENALEX_API_KEY=your_key
```

or:

```bash
export OPENALEX_CONTENT_API_KEY=your_key
```

Download priority:

1. OpenAlex content API
2. open-access PDF URL
3. publisher landing page extraction
4. user-authorized cookies / headers
5. abstract-only review if full text is unavailable

If the OpenAlex quota is exhausted or a paper has no OpenAlex content PDF, Paper-Reach automatically falls back to the default fetch logic.

---

## Cookie-Based Access

Some publisher pages or institutional routes require a logged-in browser session. Paper-Reach does not bypass login or human verification. It can reuse user-authorized cookies or headers that you explicitly provide.

Recommended flow:

1. Log in with your browser.
2. Open the target publisher page once.
3. Export cookies with Cookie-Editor.
4. Save them locally, for example `cookies.json`.
5. Run Paper-Reach:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/with_cookies \
  --download-dir ./runs/with_cookies/downloads \
  --cookie-file ./cookies.json \
  --workers 8
```

You can also provide request headers:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/with_auth \
  --cookie-file ./cookies.json \
  --header-file ./headers.json
```

Do not commit cookies or headers to GitHub.

---

## Design Philosophy

Paper-Reach is scaffolding, not a heavyweight autonomous research system.

The workflow is intentionally conservative:

- title-only evidence is weak
- abstract evidence is useful but provisional
- full-text evidence is strongest
- failed download should not break screening
- weak evidence should become `ambiguous`, not overconfident `selected`

The project keeps two output layers:

- full JSON for agents, reproducibility, and downstream processing
- compact JSON for human reading and manual screening

This makes it useful both as:

- a standalone literature screening CLI
- a reusable skill backend for AI coding agents

---

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

Key areas:

- `paper_reach/`: CLI, workflow, models, ranking, fetchers, parsers
- `skills/`: paper-search, paper-reader, paper-ranker
- `examples/`: example queries, auth examples, agent recipes
- `docs/`: install, usage, architecture, roadmap, publishing
- `scripts/`: skill sync and install checks

---

## Documentation

- [Install](docs/install.md)
- [Usage](docs/usage.md)
- [Architecture](docs/architecture.md)
- [Agent integration](docs/agent-integration.md)
- [Browser cookies](docs/browser-cookies.md)
- [Publishing](docs/publishing.md)
- [Roadmap](docs/roadmap.md)

---

## Contributing

Contributions are most useful when they improve:

- screening quality
- evidence extraction
- backend extensibility
- offline usability
- agent integration

The project should stay modular, conservative, and easy to extend.
