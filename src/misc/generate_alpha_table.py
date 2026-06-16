#!/usr/bin/env python3
"""
Generate an HTML table showing alpha-composited steps from a base color to white.

Usage:
    python generate_alpha_table.py 0b1d3e 13

This creates:
    alpha_table_0b1d3e_13_steps.html
"""

import argparse
import re
from pathlib import Path
import os
root = os.path.splitext(os.path.split(__file__)[1])[0]
path = f'files/output/misc/{root}'
os.makedirs( path, exist_ok=True )

def parse_hex_color(value: str) -> tuple[str, tuple[int, int, int]]:
    """Accept a 6-digit hex color with or without a leading #."""
    value = value.strip().lower().removeprefix("#")

    if not re.fullmatch(r"[0-9a-f]{6}", value):
        raise argparse.ArgumentTypeError(
            "base_colour must be a 6-digit hex string, e.g. 0b1d3e or #0b1d3e"
        )

    rgb = tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    return value, rgb  # value has no leading #


def composite_with_white(base_rgb: tuple[int, int, int], i: int, steps: int) -> tuple[int, int, int]:
    """
    Return the visible RGB color for step i, where:
        alpha = i / (steps - 1)
        visible = round((1 - alpha) * base + alpha * 255)

    Step 0 is the base color.
    The final step is white.
    """
    alpha = i / (steps - 1)
    return tuple(round((1 - alpha) * channel + alpha * 255) for channel in base_rgb)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def readable_text_color(rgb: tuple[int, int, int]) -> str:
    """Choose dark or white text based on perceived luminance."""
    r, g, b = rgb
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#111111" if luminance > 170 else "#ffffff"


def build_html(base_hex_no_hash: str, base_rgb: tuple[int, int, int], steps: int) -> str:
    base_hex = f"#{base_hex_no_hash}"

    row_html_parts = []

    for i in range(steps):
        alpha = i / (steps - 1)
        alpha_byte = round(255 * alpha)
        overlay_hex = f"#ffffff{alpha_byte:02x}"

        visible_rgb = composite_with_white(base_rgb, i, steps)
        visible_hex = rgb_to_hex(visible_rgb)
        text_color = readable_text_color(visible_rgb)

        row_html_parts.append(f"""        <tr>
          <td style="background:{visible_hex}; color:{text_color};">
            {visible_hex}
            <span>i={i}, overlay {overlay_hex}, alpha={alpha:.4f}</span>
          </td>
        </tr>""")

    row_html = "\n".join(row_html_parts)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{steps}-step computed colors from {base_hex}</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #f5f7fb;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 24px;
      box-sizing: border-box;
    }}

    .panel {{
      background: {base_hex};
      padding: 24px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    }}

    .title {{
      color: white;
      font-weight: 700;
      margin: 0 0 12px 0;
      text-align: center;
    }}

    table {{
      border-collapse: collapse;
      border-spacing: 0;
      width: 340px;
    }}

    td {{
      height: 40px;
      border: 0;
      padding: 4px 8px;
      text-align: center;
      vertical-align: middle;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    td span {{
      display: block;
      font-size: 12px;
      font-weight: 600;
      opacity: 0.9;
      letter-spacing: 0.01em;
      margin-top: 2px;
    }}
  </style>
</head>
<body>
  <div class="panel">
    <div class="title">Computed visible colors from {base_hex}, {steps} steps</div>
    <table aria-label="{steps}-step table of visible colors computed from the alpha compositing formula">
{row_html}
    </table>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an HTML file showing alpha-composited steps from a base color to white."
    )
    parser.add_argument(
        "base_colour",
        type=parse_hex_color,
        help="6-digit hex color, with or without leading #, e.g. 0b1d3e",
    )
    parser.add_argument(
        "steps",
        type=int,
        help="Number of table rows/steps. Must be at least 2.",
    )

    args = parser.parse_args()
    base_hex_no_hash, base_rgb = args.base_colour

    if args.steps < 2:
        parser.error("steps must be at least 2")

    filename = f"{path}/alpha_table_{base_hex_no_hash}_{args.steps}_steps.html"
    output_path = Path(filename)

    output_path.write_text(
        build_html(base_hex_no_hash, base_rgb, args.steps),
        encoding="utf-8",
    )

    print(f"Created {output_path}")


if __name__ == "__main__":
    main()
