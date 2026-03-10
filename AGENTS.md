# AGENTS.md

## Purpose

Paper-Reach gives coding agents a reusable workflow for literature search, screening, evidence extraction, and conservative ranking. The repository is designed for literature review support, not for general web browsing and not for a heavyweight autonomous agent stack.

## Preferred Workflow

Agents working in this repository should follow this sequence:

1. Load or construct a structured query input.
2. Search candidate papers using the relevant search skill and backend.
3. Coarsely screen papers using title and abstract evidence only.
4. Move plausible papers into `screening_candidates` for second-stage review.
5. Mark uncertain cases as `ambiguous` or `need_fulltext`.
6. When full text is available, extract evidence for method, dataset, supervision, limitations, and task framing.
7. Rank papers with the rubric and produce structured JSON output.
8. Generate conservative gap-analysis notes and next-query suggestions.

## Evidence Rules

- Strong claims require evidence.
- Title-only relevance is never enough for final selection.
- Abstract-only evidence supports coarse screening, not overconfident conclusions.
- If the workflow lacks full text and the query requires stronger support, the agent should keep papers as `ambiguous`.
- Missing evidence should be surfaced explicitly in the result JSON.

## Expected Structured Outputs

Agents should prefer JSON-first outputs that preserve:

- `query_summary`
- `screening_candidates`
- `selected`
- `ambiguous`
- `rejected`
- `gap_analysis`
- `recommended_next_queries`

Each paper record should include metadata, decision, reasons, score, and evidence entries with section, excerpt or quote, note, and confidence.

## Skill Usage

Use the relevant skill for the current step:

- `paper-search` for candidate retrieval and abstract-level coarse screening
- `paper-reader` for extracting evidence from abstract or full text during review
- `paper-ranker` for conservative final ranking and decisioning

## Offline Fallback

If internet access is unavailable or remote APIs fail, fall back to local files, local metadata, user-supplied paper lists, DOI lists, BibTeX-derived records, or text extracts. Record the reduced evidence confidence rather than pretending remote retrieval succeeded.
