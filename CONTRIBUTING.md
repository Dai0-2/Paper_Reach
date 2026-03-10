# Contributing

Thanks for contributing to Paper-Reach.

## Scope

Paper-Reach is a literature workflow starter for coding agents. Contributions should make the project:

- easier to install
- easier to integrate with agents
- more rigorous in evidence-based screening
- more robust in offline and partially connected environments

Please avoid turning the repository into a heavyweight autonomous framework. Keep extensions modular and easy to inspect.

## Good Contribution Areas

- new scholarly search backends
- better metadata normalization
- stronger full-text parsing
- better screening heuristics
- richer JSON schemas and examples
- reproducible fixtures for tests
- agent integration docs for Codex, Claude Code, OpenClaw, Cursor, and similar tools

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Design Expectations

- keep dependencies minimal
- preserve type hints and public docstrings
- prefer explicit interfaces over hidden behavior
- keep output JSON stable and well-structured
- treat abstract-only evidence conservatively
- do not claim full-text support unless actual text was available

## Pull Request Guidance

- explain the user-facing problem being solved
- mention any schema or CLI changes
- include tests for core logic changes
- document stubs and failure modes clearly when adding network-backed behavior

## Documentation

If you add a new workflow stage, backend, parser, or integration path, update:

- `README.md`
- relevant files under `docs/`
- examples if the feature is user-facing

