# Release Notes: v0.1.0

## Highlights

Paper-Reach `v0.1.0` is the first public starter release of the project.

This release establishes the repository as:

- a Python CLI for literature screening workflows
- a reusable skill collection for coding agents
- a JSON-first scaffolding project for evidence-based paper triage

## Included In This Release

- two-stage workflow:
  - `screen`
  - `fetch-fulltext`
  - `review`
  - `run`
- online retrieval backends for OpenAlex and arXiv
- offline local-files backend
- text parser and optional PyMuPDF PDF parser
- conservative ranking rubric
- query and result JSON schemas
- reusable skills for paper search, reading, and ranking
- examples and agent integration documentation
- high-recall retrieval mode for broader candidate search

## Agent Integration

This release is designed to work well with coding-agent environments by combining:

- `AGENTS.md`
- `skills/`
- the `paper-reach` CLI

The intended integration model is:

1. the agent reads repository guidance
2. the agent chooses a workflow step
3. the agent runs the CLI
4. the agent reasons from the structured JSON output

## Known Limitations

- remote retrieval is intentionally lightweight and defensive
- full-text fetching currently prioritizes open-access links
- restricted institutional access flows remain conservative and only partially stubbed
- retrieval quality is improved by `--high-recall`, but topic-specific query refinement is still important

## Suggested Quick Start

```bash
pip install -e .[dev]
paper-reach doctor
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json --high-recall
```

## Upgrade Notes

This is the initial public release, so there is no upgrade path from a prior version yet.

