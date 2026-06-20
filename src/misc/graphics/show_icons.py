#!/usr/bin/env python3
"""
Generate an HTML preview table for SVG icons at a requested point size.

Usage:
    py show_icons.py --point-size 16 *.svg
    python show_icons.py --point-size 12 --output preview.html icons/*.svg

The generated HTML embeds each SVG as a data URI in an <img>, so the browser
renders the SVG directly rather than using a bitmap conversion.
"""

from __future__ import annotations

import argparse
import base64
import glob
import html
import os
import sys
from pathlib import Path
from typing import Iterable, List


def expand_inputs(patterns: Iterable[str]) -> List[Path]:
    """Expand glob patterns, preserving literal file paths too."""
    files: List[Path] = []
    seen: set[Path] = set()

    for pattern in patterns:
        matches = glob.glob(pattern)
        if not matches:
            matches = [pattern]

        for match in matches:
            path = Path(match)
            if path.is_file() and path.suffix.lower() == ".svg":
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    files.append(path)

    return sorted(files, key=lambda p: str(p).lower())


def svg_to_data_uri(path: Path) -> str:
    """Return a data URI for an SVG file."""
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def build_html(files: List[Path], point_size: float, title: str) -> str:
    rows = []
    for path in files:
        name = html.escape(path.name)
        rel_path = html.escape(os.fspath(path))
        data_uri = svg_to_data_uri(path)
        rows.append(
            f"""        <tr>
            <td class=\"name\"><code>{name}</code><div class=\"path\">{rel_path}</div></td>
            <td class=\"preview\"><img src=\"{data_uri}\" alt=\"{name}\"></td>
        </tr>"""
        )

    row_html = "\n".join(rows) or (
        "        <tr><td colspan=\"2\" class=\"empty\">No SVG files found.</td></tr>"
    )

    safe_title = html.escape(title)
    display_size = f"{point_size:g}pt"

    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{safe_title}</title>
    <style>
        :root {{
            --icon-size: {display_size};
            --border: #d7d7d7;
            --muted: #666;
            --bg-cell: #fafafa;
        }}
        body {{
            margin: 24px;
            font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #222;
        }}
        h1 {{
            margin: 0 0 4px;
            font-size: 20px;
        }}
        .meta {{
            margin: 0 0 18px;
            color: var(--muted);
        }}
        table {{
            border-collapse: collapse;
            width: auto;
            min-width: 420px;
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 10px 12px;
            vertical-align: middle;
        }}
        th {{
            text-align: left;
            background: #f3f3f3;
            font-weight: 650;
        }}
        td.name {{
            min-width: 260px;
        }}
        .path {{
            margin-top: 3px;
            color: var(--muted);
            font-size: 12px;
        }}
        td.preview {{
            width: calc(var(--icon-size) + 32px);
            height: calc(var(--icon-size) + 32px);
            text-align: center;
            background:
                linear-gradient(45deg, #eee 25%, transparent 25%),
                linear-gradient(-45deg, #eee 25%, transparent 25%),
                linear-gradient(45deg, transparent 75%, #eee 75%),
                linear-gradient(-45deg, transparent 75%, #eee 75%);
            background-color: var(--bg-cell);
            background-position: 0 0, 0 8px, 8px -8px, -8px 0;
            background-size: 16px 16px;
        }}
        img {{
            width: var(--icon-size);
            height: var(--icon-size);
            object-fit: contain;
            image-rendering: auto;
        }}
        .empty {{
            color: var(--muted);
            text-align: center;
        }}
        @media print {{
            body {{ margin: 12pt; }}
            .path {{ display: none; }}
        }}
    </style>
</head>
<body>
    <h1>{safe_title}</h1>
    <p class=\"meta\">Rendered as SVG at <strong>{display_size} × {display_size}</strong>. Files: {len(files)}</p>
    <table>
        <thead>
        <tr>
            <th>Icon</th>
            <th>Preview</th>
        </tr>
        </thead>
        <tbody>
{row_html}
        </tbody>
    </table>
</body>
</html>
"""


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an HTML table previewing SVG icons at a specific point size."
    )
    parser.add_argument(
        "svgs",
        nargs="+",
        help="SVG files or glob patterns, for example *.svg or icons/*.svg",
    )
    parser.add_argument(
        "--point-size",
        "-p",
        type=float,
        required=True,
        help="Preview size in points, for example 16",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output HTML file. Defaults to icon-preview-<point-size>pt.html in the current directory.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="HTML page title. Defaults to 'SVG icon preview'.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if args.point_size <= 0:
        print("error: --point-size must be greater than zero", file=sys.stderr)
        return 2

    files = expand_inputs(args.svgs)

    if args.output:
        output = Path(args.output)
    else:
        size_label = f"{args.point_size:g}".replace(".", "-")
        output = Path.cwd() / f"icon-preview-{size_label}pt.html"

    title = args.title or "SVG icon preview"
    html_text = build_html(files, args.point_size, title)
    output.write_text(html_text, encoding="utf-8")

    print(f"Wrote {output}")
    print(f"Included {len(files)} SVG file{'s' if len(files) != 1 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
