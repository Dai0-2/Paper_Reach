# China Disaster Exposure Example

This example shows how to use Paper-Reach for a topic that benefits from a larger recall pool before full-text review.

## Run

From the repository root:

```bash
paper-reach screen \
  --input examples/china_disaster_exposure/query.json \
  --output examples/china_disaster_exposure/screen.json \
  --high-recall \
  --retrieval-limit 60
```

Then run review:

```bash
paper-reach fetch-fulltext \
  --input examples/china_disaster_exposure/query.json \
  --output examples/china_disaster_exposure/review.json \
  --high-recall \
  --retrieval-limit 60 \
  --download-dir examples/china_disaster_exposure/downloads
```

## What This Demonstrates

- broader multi-query retrieval
- coarse screening into `screening_candidates`
- review-stage handling of partial full-text access
- JSON outputs that an agent can consume directly

## Notes

- this example is intentionally broad to demonstrate retrieval and screening behavior
- it is not intended as a final curated bibliography
- for real review work, refine the query and inspect the JSON output carefully

