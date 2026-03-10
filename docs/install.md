# Install

## Local Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

The default install keeps dependencies minimal and supports:

- CLI usage
- JSON-based workflow execution
- local text and metadata screening
- lightweight online requests with graceful failure

## Optional PDF Parsing

Paper-Reach can parse local PDFs through PyMuPDF if the dependency is installed:

```bash
pip install pymupdf
```

If PyMuPDF is unavailable, the CLI still works. PDF parsing is simply reported as unavailable by `paper-reach doctor`, and the workflow will fall back to text or metadata inputs when possible.

## Online Mode

Online mode uses lightweight HTTP requests to scholarly sources such as OpenAlex and arXiv.

```bash
paper-reach run --input query.json --output result.json --mode online
```

Notes:

- internet access is optional, not required
- request failures are treated defensively
- the workflow continues with partial data where possible

## Offline Mode

Offline mode uses only local inputs:

```bash
paper-reach run --input query.json --output result.json --mode offline --local-path ./papers
```

Supported local sources include:

- `.json` metadata files
- `.txt` full-text or extracted text files
- `.pdf` files when PyMuPDF is available
- folders containing mixed local artifacts

## Development Workflow

```bash
pytest
paper-reach doctor
paper-reach example-query
paper-reach screen --input query.json --output screen.json
```

## Agent-Facing Usage

If you want to use Paper-Reach from a coding-agent environment:

- keep this repository available locally, or install the package into the environment
- point the agent to `AGENTS.md` and `skills/`
- let the agent call the CLI for actual retrieval and screening work

See [docs/agent-integration.md](/home/nas/dailing/paper_reach/docs/agent-integration.md).

For package release flow, see [docs/publishing.md](/home/nas/dailing/paper_reach/docs/publishing.md).
