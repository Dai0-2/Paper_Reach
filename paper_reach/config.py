"""Configuration helpers for Paper-Reach."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration for the workflow."""

    default_channels: List[str] = field(
        default_factory=lambda: ["openalex", "arxiv", "local_files"]
    )
    request_timeout_seconds: int = 15
    user_agent: str = "paper-reach/0.1.0"
    parser_priority: List[str] = field(
        default_factory=lambda: ["pymupdf", "simple_text"]
    )

    def as_dict(self) -> Dict[str, object]:
        """Return a serializable view of the config."""
        return {
            "default_channels": self.default_channels,
            "request_timeout_seconds": self.request_timeout_seconds,
            "user_agent": self.user_agent,
            "parser_priority": self.parser_priority,
        }


DEFAULT_CONFIG = AppConfig()

