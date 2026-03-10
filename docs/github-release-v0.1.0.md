# GitHub Release Body: v0.1.0

## Paper-Reach v0.1.0

Paper-Reach is a lightweight open-source starter project for evidence-based literature screening with coding agents.

This first release establishes the repository as:

- a Python CLI for literature review workflows
- a reusable skill collection for agent environments
- a JSON-first scaffolding project for search, screening, evidence extraction, and conservative ranking

## Highlights

- two-stage workflow: `screen`, `fetch-fulltext`, `review`, `run`
- OpenAlex and arXiv starter backends
- offline local-files mode
- optional PDF parsing via PyMuPDF
- conservative ranking rubric with `selected`, `ambiguous`, and `rejected`
- high-recall retrieval mode for larger candidate pools
- reusable `skills/` for paper search, reading, and ranking
- agent integration docs and starter recipes for Codex and OpenClaw

## Quick Start

```bash
pip install -e .[dev]
paper-reach doctor
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json --high-recall
```

## Included Docs

- installation guide
- architecture notes
- usage guide
- agent integration guide
- publishing guide
- examples and recipes

## Notes

- this release is intentionally a starter, not a heavyweight autonomous framework
- remote retrieval is lightweight and defensive by design
- restricted full-text access remains conservative and partially stubbed

## Full Changelog

See [CHANGELOG.md](/home/nas/dailing/paper_reach/CHANGELOG.md).

