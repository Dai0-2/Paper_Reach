# Paper-Reach

Give your AI agent a rigorous literature review workflow.

`Paper-Reach` is an open-source skill + CLI for literature search, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is built for coding agents such as Codex, Claude Code, OpenClaw, Cursor, and similar tools, but it also works as a standalone Python CLI.

[Quick Start](#quick-start) · [English](#english) · [Supported Platforms](#supported-platforms) · [Design Philosophy](#design-philosophy)

---

## Why Paper-Reach?

AI agents can already write code, edit docs, and manage repositories. But once you ask them to do a real literature review, they usually break down:

- "Find papers on this topic and keep only the ones that actually match my criteria." -> They overclaim from titles.
- "Tell me which papers really use this dataset or supervision signal." -> Abstract evidence is often too weak.
- "Download the paper and confirm the method." -> PDF access fails, and the workflow stalls.
- "Give me a shortlist I can actually read." -> The output is a giant JSON blob.

The hard part is not search. The hard part is **evidence-based screening**.

Paper-Reach turns that into a repeatable workflow:

1. retrieve a large candidate pool
2. screen conservatively at abstract level
3. fetch full text when possible
4. review with stronger evidence
5. export both machine-readable and human-readable outputs

### Before You Use It

| Item | What it means |
|---|---|
| **Conservative by default** | Title-only relevance is never treated as strong evidence |
| **Agent-friendly** | Works as a CLI and as a reusable skill bundle |
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

> Already installed? Update is just a normal `git pull` plus reinstall if needed:
>
> ```bash
> git pull
> pip install -e .[dev]
> ```

---

## English

The repository default is English.

This README, the CLI, the JSON schema, and the main documentation are designed to be readable for international users. The project can still be used in Chinese-language workflows, but the public-facing repository should stay English-first.

Typical message to an agent:

```text
Install and use Paper-Reach from this repository. Run a high-recall literature screening workflow, keep the output conservative, and export both a full JSON result and a brief shortlist.
```

---

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

For platforms that need cookies, the most practical setup is:

**browser login -> Cookie-Editor export -> send cookies to the agent -> run Paper-Reach**

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

Cookie handling principles:

- cookies stay local
- cookies are never required for the core workflow
- if cookies are missing or invalid, Paper-Reach falls back gracefully

For details, see [docs/browser-cookies.md](docs/browser-cookies.md).

---

## Design Philosophy

Paper-Reach is not a heavyweight autonomous research framework.

It is a practical starter repo for literature workflow scaffolding.

The main design principles are:

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
- a skill bundle for multiple agent hosts
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
- OpenAlex-first content download with graceful fallback
- Profile-based ranking with hard gates and weighted dimensions
- Compact output modes for humans: `titles` and `brief`
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

## Multi-Host Skill Support

Paper-Reach follows the same pattern used by mature cross-host skill repos:

- one shared execution engine
  - `paper-reach` CLI + `paper_reach/`
- one host-agnostic skill entrypoint
  - `SKILL.md`
- thin host-specific manifests
  - `agents/openai.yaml`
  - `.claude-plugin/plugin.json`
  - `gemini-extension.json`

This keeps the workflow logic in one place while making the skill discoverable across different agent ecosystems.

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

## Documentation

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## What I Would Still Improve

After looking at the overall shape of `Agent-Reach`, the most useful next improvements for `Paper-Reach` are:

- make installation even more one-shot
  - for example, a raw install doc that an agent can follow directly
- make the homepage more outcome-oriented
  - show what users get, not just what modules exist
- keep “configuration with cookies” visible and practical
  - this matters a lot for real publisher workflows
- continue improving shortlist quality
  - better final ranking matters more than adding more backends

## Contributing

Contributions are most useful when they improve:

- screening quality
- evidence extraction
- backend extensibility
- offline usability
- agent integration

The project should stay modular, conservative, and easy to extend.
