# paper-search

## Name

paper-search

## Description

Retrieve candidate papers and perform conservative coarse screening using title and abstract evidence. This skill is for building a candidate set, not for making strong final claims.

## Use When

- the user wants candidate papers for a topic
- the workflow needs abstract-level screening
- the agent needs to search online sources or local metadata
- the repository needs a first-pass shortlist before full-text review

## Inputs

- topic
- keywords
- inclusion criteria
- exclusion criteria
- year range
- max results
- mode: `online`, `offline`, or `auto`
- local paths or local metadata files when available

## Outputs

- normalized paper metadata
- coarse screening reasons
- `screening_candidates` and `need_fulltext` flags for uncertain items
- abstract-level evidence snippets where available
- structured JSON-ready paper records

## Workflow

1. Load the query input.
2. Choose channels based on mode.
3. Search remote sources if online access is allowed and available.
4. Fall back to local metadata, JSON files, DOI/title lists, or folders if online retrieval is unavailable.
5. Normalize results into a common paper schema.
6. Screen conservatively:
   - title can suggest relevance
   - abstract can support plausible relevance
   - title alone must not justify selection
7. Mark items as `need_fulltext` when the abstract is missing, vague, or insufficient for inclusion criteria.
8. Output plausible matches into a `screening_candidates` set for later full-text review.

## Guardrails

- Do not overclaim based on title only.
- Do not label a paper as definitively selected during this step.
- If abstract evidence conflicts with inclusion criteria, reject or downgrade the paper.
- If internet access is unavailable, say so and continue with local inputs when possible.
- Record evidence quality explicitly.

## Online And Offline Behavior

- `online`: use scholarly APIs defensively and continue on failure
- `offline`: use local metadata or user-supplied paper lists only
- `auto`: attempt online retrieval first, then merge or fall back to offline inputs

## Example

Input:

```json
{
  "topic": "Driving attention prediction with BDD-100K",
  "keywords": ["BDD-100K", "driving attention", "gaze prediction", "attention map"]
}
```

Output behavior:

- candidate papers returned with metadata
- reasons referencing title and abstract cues
- uncertain papers flagged `need_fulltext: true`
