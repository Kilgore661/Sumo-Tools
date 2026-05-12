"""Placeholder page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_tbd_page(page: Page, target_path: Path) -> None:
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            f"<title>{escape(page.title)}</title>",
            "<style>",
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-line: #7f95c0; }",
            "* { box-sizing: border-box; }",
            "body { min-height: 100vh; margin: 0; padding: 20px; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; }",
            ".tool-shell { min-height: calc(100vh - 40px); border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tbd { padding: 18px; font-size: 1.2rem; }",
            "</style>",
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
            '<main class="tbd">TBD</main>',
            "</div>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


