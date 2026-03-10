# Architecture

## Repository Philosophy

Paper-Reach is scaffolding, not a full autonomous system.

The repository is optimized for:

- clear interfaces
- conservative evidence handling
- JSON-first interoperability
- low setup cost
- extension by agents or developers

It is intentionally not optimized for orchestration complexity, hidden chains of tools, or a large built-in agent runtime.

## Workflow Pipeline

The default pipeline is:

1. load a `QueryInput`
2. query one or more search channels
3. merge and normalize metadata
4. perform coarse screening from title and abstract
5. move plausible items into `screening_candidates`
6. fetch or attach full text where available
7. parse local full text when available
8. extract evidence snippets
9. score each paper with the rubric
10. emit structured JSON output

This pipeline preserves the distinction between title-only signals, abstract-level support, and full-text-supported decisions.

## Backend Abstraction

Search channels implement a small interface that returns normalized `PaperMetadata` items. The interface is intentionally simple:

- input: `QueryInput`
- output: list of normalized metadata records
- failure mode: graceful, empty list plus warnings where appropriate

This makes it straightforward to add new backends such as Semantic Scholar, Crossref, or internal datasets.

## Parser Abstraction

Parsers implement a small contract for reading local content into plain text:

- text parser for `.txt`
- optional PDF parser for `.pdf`
- extensible base class for richer document readers later

The parser layer is independent from ranking logic. A stronger parser should improve evidence quality without requiring redesign of the workflow.

## Ranking Abstraction

Ranking lives in a dedicated rubric module with explicit scoring dimensions:

- topic relevance
- method match
- dataset match
- supervision or annotation match
- evidence confidence

Decision labels are:

- `selected`
- `ambiguous`
- `rejected`

The ranker is conservative by design. It penalizes weak evidence and criteria violations rather than turning uncertain cases into false positives.

## Why This Is Not A Heavy Framework

Paper-Reach is meant to be embedded into agent workflows, not to replace them. The project supplies:

- skills
- schemas
- CLI
- interfaces
- starter implementations

That keeps the repository publishable, inspectable, and easy to extend without locking users into a specific orchestration model.
