# Usage

## Search Papers Online

Create a query file:

```bash
paper-reach example-query > query.json
paper-reach screen --input query.json --output screen.json --mode online
paper-reach fetch-fulltext --input query.json --output review.json --mode online --download-dir ./downloads
```

This will try online scholarly channels first. If a backend fails, the workflow continues with whichever channels succeed.

For broader candidate recall:

```bash
paper-reach screen --input query.json --output screen.json --mode online --high-recall --retrieval-limit 120
```

## Screen A Folder Of Local PDFs

```bash
paper-reach review --input query.json --output result.json --mode offline --local-path ./downloads
```

Behavior:

- `.txt` files are parsed directly
- `.pdf` files are parsed if PyMuPDF is installed
- `.json` metadata files are loaded as local candidate records

## Combine Online And Offline Inputs

```bash
paper-reach run --input query.json --output result.json --mode auto --local-path ./downloads --channel openalex --channel local_files
```

This is useful when you want remote discovery plus local evidence extraction.

## Inspect JSON Output

The output file contains:

- `query_summary`
- `screening_candidates`
- `selected`
- `ambiguous`
- `rejected`
- `gap_analysis`
- `recommended_next_queries`

You can inspect the result with:

```bash
python -m json.tool result.json
```

## CLI Reference

```bash
paper-reach doctor
paper-reach example-query
paper-reach screen --input query.json --output screen.json
paper-reach fetch-fulltext --input query.json --output review.json
paper-reach review --input query.json --output result.json
paper-reach version
paper-reach run --input query.json --output result.json
```

## Practical Tips

- Keep `require_fulltext_for_selection` enabled when false positives are costly.
- Use offline mode for reproducibility when you already have a vetted paper set.
- Treat `ambiguous` as the queue for manual review or deeper parsing.

## More

- agent integration: [docs/agent-integration.md](/home/nas/dailing/paper_reach/docs/agent-integration.md)
- end-to-end examples: [examples/README.md](/home/nas/dailing/paper_reach/examples/README.md)
- publishing and releases: [docs/publishing.md](/home/nas/dailing/paper_reach/docs/publishing.md)
