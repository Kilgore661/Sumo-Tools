"""Configuration for the mojibake audit."""

from __future__ import annotations

TEXT_SUFFIXES = frozenset(
    {
        ".cfg",
        ".css",
        ".csv",
        ".html",
        ".js",
        ".json",
        ".md",
        ".py",
        ".svg",
        ".toml",
        ".tsv",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "node_modules",
    }
)

SKIP_PATH_PARTS = (
    ("files", "output"),
    ("files", "cache"),
)

THIS_TOOL_PATH = "src/misc/mojibake_audit.py"

MOJIBAKE_MARKERS = (
    "\ufffd",
    "Ã",
    "Â",
    "Å",
    "â€™",
    "â€œ",
    "â€\u009d",
    "â€“",
    "â€”",
    "â€¦",
)

HTTP_RESPONSE_NAMES = frozenset({"r", "resp", "response"})
