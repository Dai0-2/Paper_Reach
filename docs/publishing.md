# Publishing

## Goal

This document describes a practical release flow for Paper-Reach as an open-source package and GitHub project.

The project is designed to ship as:

- a Python package with a CLI
- a repository that includes reusable `skills/`
- an agent-friendly workflow reference through `AGENTS.md`

## Release Checklist

Before cutting a release:

- run `pytest`
- verify `paper-reach doctor`
- verify `paper-reach example-query`
- verify at least one example from `examples/`
- update `CHANGELOG.md`
- confirm `README.md` reflects current CLI commands and docs
- confirm package version in [pyproject.toml](/home/nas/dailing/paper_reach/pyproject.toml) and [paper_reach/__init__.py](/home/nas/dailing/paper_reach/paper_reach/__init__.py)

## Versioning

Use semantic versioning as a practical guide:

- patch: bug fixes, docs fixes, small non-breaking improvements
- minor: new backends, new workflow options, new fields added compatibly
- major: breaking CLI, schema, or integration changes

## Local Verification

Typical pre-release commands:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
paper-reach doctor
paper-reach example-query
paper-reach screen --input examples/china_disaster_exposure/query.json --output /tmp/paper-reach-screen.json --high-recall --retrieval-limit 40
```

## Build The Package

Install build tooling if needed:

```bash
pip install build twine
```

Then build:

```bash
python -m build
```

This produces source and wheel artifacts under `dist/`.

## Validate Artifacts

```bash
python -m twine check dist/*
```

## Publish To PyPI

Once the package name and credentials are ready:

```bash
python -m twine upload dist/*
```

If using TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

## GitHub Release Flow

Suggested sequence:

1. update version
2. update `CHANGELOG.md`
3. commit release changes
4. tag the release
5. push branch and tag
6. create a GitHub release with summary notes

Example:

```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

## Release Notes Template

Suggested note sections:

- highlights
- CLI changes
- schema changes
- backend or parser changes
- integration notes for agents
- known limitations

## Packaging Notes For Agent Users

For agent-oriented users, the release should clearly state:

- whether `skills/` changed
- whether `AGENTS.md` changed in a behaviorally important way
- whether output JSON added fields
- whether any CLI commands or flags changed

## Recommended First Public Release

For a first public release, keep the scope modest:

- CLI is stable enough to demo
- core workflow is tested
- docs explain integration patterns
- stubs are clearly identified as stubs

That is better than overclaiming feature completeness.

