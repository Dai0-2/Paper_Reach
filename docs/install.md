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

## Install As A Multi-Host Skill Bundle

Paper-Reach does not need a specific agent host to work. The recommended model is:

1. install the Python package
2. optionally sync the skill bundle into host-specific skill directories

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
bash scripts/sync.sh
```

The sync step mirrors the host-facing files into:

- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`
- `~/.codex/skills/paper-reach`

This makes the same workflow discoverable by Claude-style, Codex/OpenAI-style, and similar skill hosts without duplicating the core logic.

You can verify the setup with:

```bash
bash scripts/check-install.sh
```

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

## User-Authorized Sessions

Some publisher pages need an authenticated browser session, institutional proxy, or user-authorized headers. Paper-Reach supports reusing user-provided local auth state without attempting to bypass site protections.

Supported inputs:

- `--cookie-file`: JSON cookies or a Mozilla/Netscape cookiejar export
- `--header-file`: JSON object of request headers

Example:

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json \
  --header-file ./headers.json
```

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
- expose the root `SKILL.md` if the host expects a skill entrypoint
- point the agent to `AGENTS.md` and `skills/`
- let the agent call the CLI for actual retrieval and screening work

Host metadata shipped with the repository:

- `SKILL.md`
- `agents/openai.yaml`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `gemini-extension.json`

See [docs/agent-integration.md](/home/nas/dailing/paper_reach/docs/agent-integration.md).

For package release flow, see [docs/publishing.md](/home/nas/dailing/paper_reach/docs/publishing.md).

For exporting browser session state, see [docs/browser-cookies.md](/home/nas/dailing/paper_reach/docs/browser-cookies.md).
