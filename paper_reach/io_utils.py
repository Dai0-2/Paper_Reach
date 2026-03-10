"""I/O helpers for JSON and local files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import QueryInput, WorkflowOutput


def load_query(path: str | Path) -> QueryInput:
    """Load query input from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return QueryInput.model_validate(data)


def load_workflow_output(path: str | Path) -> WorkflowOutput:
    """Load workflow output from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return WorkflowOutput.model_validate(data)


def write_json(path: str | Path, payload: Any) -> None:
    """Write a JSON payload with stable formatting."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_json(payload: Any) -> None:
    """Print JSON to stdout."""
    print(json.dumps(payload, ensure_ascii=False, indent=2))
