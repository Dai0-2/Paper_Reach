# Changelog

All notable changes to this project will be documented in this file.

The format is intentionally lightweight and follows a simple Keep a Changelog style.

## [0.1.0] - 2026-03-10

### Added

- initial Paper-Reach repository structure
- Python CLI with `screen`, `fetch-fulltext`, `review`, `run`, `doctor`, `example-query`, and `version`
- reusable skills for paper search, paper reading, and paper ranking
- online backends for OpenAlex and arXiv
- offline local-files backend
- parser layer with text parsing and optional PyMuPDF PDF support
- two-stage screening workflow with `screening_candidates`
- conservative ranking rubric and JSON-first outputs
- query and result schemas
- examples and agent integration documentation
- high-recall retrieval mode with multi-query expansion
- contribution guide

### Notes

- scholarly retrieval remains lightweight and defensive
- some full-text access paths are intentionally stubbed or conservative
- the repository is positioned as scaffolding, not a heavyweight autonomous framework

