<h1 align="center">Paper-Reach</h1>

<p align="center">
  <strong>Give your AI agent a rigorous literature review workflow.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
</p>

<p align="center">
  <a href="#quick-start">快速开始</a> · <a href="README.md">English</a> · <a href="#supported-platforms">支持平台</a> · <a href="#design-philosophy">设计理念</a>
</p>

---

## Why Paper-Reach?

Paper search is easy. Literature screening is hard.

Most tools can return titles and abstracts. Fewer tools can help an agent answer these questions reliably:

- Is this paper only title-relevant?
- Is it abstract-supported but still uncertain?
- Is the claim actually supported by full-text evidence?
- Can the result be reused as a clean baseline set for the next research step?

Paper-Reach is built for that second half of the workflow.

If you want your agent to do literature review instead of just returning search results, this repo gives you a reusable scaffold:

- retrieve candidate papers
- screen with evidence
- fetch full text when possible
- keep conservative rankings
- export both full JSON and compact review lists

## What's New

- OpenAlex content API is used first when an API key is configured
- `run --bundle-dir` now writes a complete run folder with all stage outputs
- `summarize` exports both `titles` and `brief` review views
- profile-based ranking supports task-specific hard gates and weighted scoring
- multi-host skill packaging is included for Codex, Claude-style, and Gemini-style hosts

## Supported Platforms

| Source / Capability | Works Out of the Box | Better With Configuration | How to Configure |
|---|---|---|---|
| OpenAlex metadata search | Yes | More full-text downloads | Set `OPENALEX_API_KEY` |
| OpenAlex full-text download | No | Yes | Set `OPENALEX_API_KEY` or `OPENALEX_CONTENT_API_KEY` |
| arXiv search | Yes | — | No extra config |
| Local PDF / TXT / JSON metadata | Yes | — | Provide `--local-path` |
| Authenticated publisher pages | Limited | Yes | Provide `--cookie-file` and/or `--header-file` |
| Codex / Claude / OpenClaw style skill loading | Yes | — | Run `scripts/sync.sh` |

### Cookie-based Platforms

For platforms that require login or session cookies, export your browser cookies and pass them to the agent.

Recommended flow:

`browser login -> Cookie-Editor export -> send cookies to the agent`

Chrome extension:
- [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

Why this matters:
- more reliable than ad hoc manual copy steps
- easier to repeat than QR-style login workarounds
- fits one unified workflow for authenticated sources

Example usage:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

Cookies stay local to your machine. They are not uploaded by this repo.

---

## Quick Start

Give your agent a runnable literature workflow first. Then optimize query profiles and ranking rules.

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

### 2. Run a high-recall screen

```bash
paper-reach example-query > query.json

paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

### 3. Run the full workflow

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

### 4. Export a readable short list

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

---

## Example Task

Suppose you want to collect papers in China that use static or gridded population as exposure input, so you can later compare them against dynamic-population methods.

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

## What the Workflow Produces

When you use `run --bundle-dir`, Paper-Reach writes a complete review bundle:

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

What each file is for:

- `30_result_full.json`
  - full machine-readable output
  - best for agents, debugging, and downstream processing
- `40_result_brief.json`
  - shorter human-readable review list
  - includes title, URL, year, decision, reasons, venue, PDF path, and review fields
- `50_result_titles.json`
  - minimal shortlist with title + URL

This keeps the repo useful for both:
- agents that need structured data
- humans who want a fast shortlist

---

## Multi-Host Skill Support

Paper-Reach follows a cross-host packaging pattern:

- one shared execution engine
  - `paper-reach` CLI + `paper_reach/` package
- one host-agnostic skill entrypoint
  - `SKILL.md`
- thin host-specific manifests
  - `agents/openai.yaml`
  - `.claude-plugin/plugin.json`
  - `gemini-extension.json`

This keeps the logic in one place while making the skill discoverable across different agent ecosystems.

To sync the skill bundle into common host directories:

```bash
bash scripts/sync.sh
bash scripts/check-install.sh
```

---

## Design Philosophy

**Paper-Reach is scaffolding, not a heavyweight framework.**

That means:

- the core workflow should stay modular
- evidence quality should stay visible
- title-only relevance should never be treated as strong support
- abstract screening should remain conservative
- full-text review should strengthen claims, not fabricate certainty
- outputs should be reusable by both agents and humans

This repo is meant to help agents screen literature better, not pretend every paper is fully understood just because it was retrieved.

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

Key directories:

- `paper_reach/`
  - CLI, workflow, ranking, fetchers, parsers, schemas
- `skills/`
  - paper-search, paper-reader, paper-ranker
- `examples/`
  - query samples, auth examples, agent recipes
- `docs/`
  - install, usage, architecture, roadmap, publishing

## Documentation

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## Contributing

Good contributions usually improve one of these areas:

- better retrieval backends
- stronger abstract or full-text evidence extraction
- clearer ranking profiles
- better offline support
- better agent-host integration

The project should stay conservative, modular, and easy to extend.
