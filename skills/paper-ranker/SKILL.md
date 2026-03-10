# paper-ranker

## Name

paper-ranker

## Description

Apply a conservative screening rubric to separate selected, ambiguous, and rejected papers with reasons and evidence references.

## Use When

- the user wants final selection or ranking
- a candidate set already exists
- abstract and optional full-text evidence need to be turned into decisions
- the workflow must produce reproducible, structured outputs

## Inputs

- normalized paper records
- evidence entries
- inclusion criteria
- exclusion criteria
- rubric dimensions and thresholds
- `require_fulltext_for_selection`

## Outputs

- relevance score
- decision: `selected`, `ambiguous`, or `rejected`
- reasons
- evidence references
- grouped result sets

## Workflow

1. Start from the `screening_candidates` set.
2. Review criteria and available evidence.
3. Score each paper on:
   - topic relevance
   - method match
   - dataset match
   - supervision or annotation match
   - evidence confidence
4. Check exclusion criteria and missing required evidence.
5. Apply conservative decision rules.
6. Return grouped outputs and recommended follow-up actions.

## Guardrails

- Apply the rubric conservatively.
- Separate `selected`, `ambiguous`, and `rejected`.
- Do not convert uncertainty into selection.
- If full text is required for selection and unavailable, keep the paper ambiguous.
- Provide reasons and evidence references for every decision.

## Online And Offline Behavior

- works in either mode because ranking depends on normalized evidence, not on network access
- weak evidence in offline-only metadata should reduce confidence rather than inflate score

## Example

Decision pattern:

- `selected`: strong topic and supervision match with sufficient evidence
- `ambiguous`: promising paper but missing method, dataset, or full-text confirmation
- `rejected`: exclusion triggered or relevance too weak
