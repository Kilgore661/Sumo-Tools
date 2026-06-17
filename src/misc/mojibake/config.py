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

SKIP_MARKER_SCAN_PATHS = frozenset(
    {
        "src/misc/mojibake/config.py",
    }
)

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
