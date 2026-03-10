# Paper-Reach

Give your AI agent a rigorous literature review workflow.

Current starter release: `v0.1.0`

Paper-Reach is a lightweight open-source starter project for research literature screening. It helps coding agents and developers move beyond paper search into evidence-based triage, abstract screening, full-text reading, and conservative ranking. The project is intentionally built as scaffolding: a reusable skill collection, Python CLI, and JSON-first workflow that can be extended without committing to a heavyweight agent framework.

## Why Paper-Reach

Searching papers is easy. Screening them well is hard.

Most agent tooling can collect titles and abstracts, but literature review quality depends on whether the workflow can:

- distinguish title-only relevance from abstract-supported relevance
- mark uncertain papers as needing full text instead of overclaiming
- extract evidence for methods, datasets, and supervision details
- rank papers with a transparent rubric
- stay useful when the internet is unavailable

Paper-Reach focuses on that gap.

## Features

- Skill-based workflow for paper search, paper reading, and ranking
- Python CLI with a small surface area: `screen`, `fetch-fulltext`, `review`, `run`, `doctor`, `example-query`, `version`
- High-recall retrieval mode with multi-query expansion for larger candidate pools
- Online mode via pluggable scholarly backends
- Offline mode via local files, metadata, DOI/title lists, or text extracts
- Defensive parser layer for text and optional PDF extraction
- JSON-first outputs for downstream analysis and reproducibility
- Conservative screening logic that separates `selected`, `ambiguous`, and `rejected`
- Gap-analysis hints and recommended follow-up queries
- Lightweight test coverage for core logic

## What Makes This Different

Paper-Reach is not trying to be a giant autonomous research platform.

It is a practical starter repository for coding agents such as Codex, Claude Code, Cursor, and similar tools. The core value is not “search more sources”; it is “screen papers better with evidence.” The workflow explicitly tracks whether a paper is:

1. only superficially relevant from the title
2. plausibly relevant from the abstract
3. strongly supported by full-text evidence

That distinction is central to the repository design.

## Online And Offline Modes

- `online`: query remote scholarly sources such as OpenAlex and arXiv
- `offline`: use only local inputs such as PDFs, BibTeX-derived metadata, JSON records, DOI lists, or text files
- `auto`: try online sources first, then continue with local inputs and graceful fallbacks

The project assumes internet access may be absent or unreliable. When online retrieval fails, the workflow falls back to local sources where possible and records that evidence confidence is limited.

## Example Use Cases

- Build a candidate set for a new literature review topic
- Triage a folder of downloaded PDFs against inclusion and exclusion criteria
- Rank papers for annotation or closer manual review
- Produce structured outputs for research gap analysis
- Give an AI coding agent a reusable screening workflow instead of ad hoc prompts

## Repository Structure

```text
paper-reach/
├─ README.md
├─ LICENSE
├─ pyproject.toml
├─ AGENTS.md
├─ docs/
├─ skills/
├─ paper_reach/
└─ tests/
```

Key areas:

- `skills/`: reusable agent-facing skills
- `paper_reach/`: Python package, CLI, workflow, backends, parsers, ranking logic
- `docs/`: installation, usage, architecture, roadmap
- `examples/`: end-to-end example queries and workflow recipes
- `tests/`: lightweight regression coverage

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json
paper-reach run --input query.json --output result.json
```

Higher-recall initial retrieval:

```bash
paper-reach screen --input query.json --output screen.json --high-recall --retrieval-limit 120
```

## Agent Integration

Paper-Reach is meant to be usable both as a Python tool and as a reusable agent workflow layer.

- agents read [AGENTS.md](/home/nas/dailing/paper_reach/AGENTS.md)
- agents use the relevant skill under `skills/`
- agents call the CLI instead of reimplementing screening logic in prompts
- agents consume the resulting JSON outputs

See [docs/agent-integration.md](/home/nas/dailing/paper_reach/docs/agent-integration.md) for the recommended integration model.

Offline run with local inputs:

```bash
paper-reach run --input query.json --output result.json --local-path ./papers
```

## Output Philosophy

Paper-Reach writes structured JSON centered on:

- query summary
- screening candidates
- selected papers
- ambiguous papers
- rejected papers
- evidence excerpts
- gap analysis notes
- recommended next queries

The system never treats title-only relevance as strong evidence. The default workflow is two-stage: initial abstract screening first, then full-text review where possible. Abstract-only support is useful for coarse screening, but strong selection decisions should remain conservative, especially when full text is unavailable.

## Roadmap

- add more scholarly backends such as Semantic Scholar and Crossref
- improve DOI resolution and metadata normalization
- support richer full-text section extraction
- integrate stronger PDF parsing pipelines such as GROBID
- benchmark literature-screening tasks with shared evaluation data

See [docs/roadmap.md](/home/nas/dailing/paper_reach/docs/roadmap.md) for details.

## Release And Packaging

- publishing guide: [docs/publishing.md](/home/nas/dailing/paper_reach/docs/publishing.md)
- agent recipes: [examples/agent-recipes/README.md](/home/nas/dailing/paper_reach/examples/agent-recipes/README.md)
- changelog: [CHANGELOG.md](/home/nas/dailing/paper_reach/CHANGELOG.md)

## Contributing

Contributions should preserve the project philosophy:

- keep the core simple and modular
- prefer explicit interfaces over hidden automation
- make evidence quality visible in outputs
- avoid inflating the project into a heavyweight orchestration framework

Issues and pull requests that improve screening rigor, offline usability, JSON interoperability, or backend extensibility are especially welcome.

See [CONTRIBUTING.md](/home/nas/dailing/paper_reach/CONTRIBUTING.md) for development guidance.
