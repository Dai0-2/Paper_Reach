# paper-reader

## Name

paper-reader

## Description

Read abstracts and, when available, full text to extract evidence relevant to literature screening. This skill is for second-stage review, not just summarization.

## Use When

- the user needs evidence from full text
- the workflow needs method, dataset, or supervision details
- a paper is ambiguous after abstract screening
- local PDFs or text files are available for deeper review

## Inputs

- normalized paper metadata
- local file paths when present
- abstract text
- screening criteria

## Outputs

- structured evidence entries
- abstract summary
- extracted method, dataset, task, supervision, and limitation notes
- explicit notice when full text is unavailable

## Workflow

1. Start from existing metadata and abstract.
2. If full text is available locally, parse it.
3. Extract evidence for:
   - task
   - method
   - dataset
   - supervision or annotation
   - limitations
4. Attach evidence with section, excerpt, note, and confidence.
5. If only abstract is available, say so explicitly and keep confidence conservative.

## Guardrails

- Do not pretend full text was read if it was not available.
- Distinguish abstract evidence from full-text evidence.
- Prefer short, attributable excerpts over vague claims.
- If parser output is poor or missing, mark the paper as needing manual review.

## Online And Offline Behavior

- `online`: may retrieve metadata remotely, but evidence extraction should still depend on actual accessible text
- `offline`: use local PDFs, text extracts, or metadata files
- when full text is unavailable in either mode, report the gap explicitly

## Example

Expected extracted fields:

```json
{
  "method": "Transformer with gaze-supervised attention head",
  "dataset": "BDD-100K-derived driving videos",
  "supervision": "human gaze maps",
  "limitations": "No night-scene evaluation reported"
}
```
