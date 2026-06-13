"""Parse cached SumoDB Rikishi.aspx search pages into a flat CSV."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from src.infra.get_bios.make_public_shikona import make_history_shikona_by_rikid
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History


INPUT_DIR = (
    Path("files")
    / "output"
    / "infra"
    / "tracker"
    / "scraper"
    / "rikishi_aspx_scraper"
)
OUTPUT_DIR = (
    Path("files")
    / "output"
    / "infra"
    / "tracker"
    / "scraper"
    / "rikishi_aspx_parser"
)
OUTPUT_CSV = OUTPUT_DIR / "rikishi_by_shikona.csv"

EXPECTED_HEADERS = (
    "Shikona",
    "Heya",
    "Shusshin",
    "Birth Date",
    "Highest Rank",
    "Hatsu Dohyo",
    "Intai",
    "Last Shikona",
)

TABLE_PAT = re.compile(
    r"<thead\b[^>]*>\s*(.*?)\s*</thead>\s*<tbody\b[^>]*>\s*(.*?)\s*</tbody>",
    re.DOTALL | re.IGNORECASE,
)
ROW_PAT = re.compile(r"<tr\b[^>]*>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
CELL_PAT = re.compile(r"<t[dh]\b[^>]*>\s*(.*?)\s*</t[dh]>", re.DOTALL | re.IGNORECASE)
LINK_PAT = re.compile(r"<a\b[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", re.DOTALL | re.IGNORECASE)
TAG_PAT = re.compile(r"<.*?>", re.DOTALL)
BASHO_DATE_PAT = re.compile(r"(\d{4})\.(\d{2})")


@dataclass(frozen=True)
class RikishiSearchRow:
    source_shikona: str
    rikid: str
    shikona: str
    heya: str
    shusshin: str
    birth_date: str
    highest_rank: str
    hatsu_dohyo: str
    intai: str
    last_shikona: str


def clean_html_text(text: str) -> str:
    """Return normalized text from an HTML fragment."""
    text = TAG_PAT.sub("", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    return " ".join(text.split())


def normalize_basho_date(value: str) -> str:
    """Normalize SumoDB YYYY.MM basho dates to YYYY/MM."""
    match = BASHO_DATE_PAT.fullmatch(value.strip())
    if match is None:
        return value
    return f"{match.group(1)}/{match.group(2)}"


def normalize_optional_text(value: str) -> str:
    """Normalize blank, dash, and non-breaking-space cells to empty string."""
    value = value.strip()
    if value == "-":
        return ""
    return normalize_basho_date(value)


def row_cells(row_html: str) -> list[str]:
    return [match.group(1) for match in CELL_PAT.finditer(row_html)]


def row_headers(row_html: str) -> tuple[str, ...]:
    return tuple(clean_html_text(cell) for cell in row_cells(row_html))


def shikona_cell_rikid(shikona_cell_html: str) -> str:
    """Extract the rikishi id from the Shikona cell link."""
    for link_match in LINK_PAT.finditer(shikona_cell_html):
        href = unescape(link_match.group(1))
        query = parse_qs(urlparse(href).query)
        rikids = query.get("r")
        if rikids:
            return str(int(rikids[0]))

    raise ValueError("could not find Rikishi.aspx?r=<rikid> link")


def parse_result_table(source_shikona: str, header_html: str, body_html: str) -> list[RikishiSearchRow] | None:
    """Parse the expected SumoDB shikona search-result table."""
    header_rows = list(ROW_PAT.finditer(header_html))
    if len(header_rows) != 1:
        return None

    if row_headers(header_rows[0].group(1)) != EXPECTED_HEADERS:
        return None

    rows: list[RikishiSearchRow] = []

    for row_match in ROW_PAT.finditer(body_html):
        cells = row_cells(row_match.group(1))
        if len(cells) != len(EXPECTED_HEADERS):
            continue

        values = [normalize_optional_text(clean_html_text(cell)) for cell in cells]
        rows.append(
            RikishiSearchRow(
                source_shikona=source_shikona,
                rikid=shikona_cell_rikid(cells[0]),
                shikona=values[0],
                heya=values[1],
                shusshin=values[2],
                birth_date=values[3],
                highest_rank=values[4],
                hatsu_dohyo=values[5],
                intai=values[6],
                last_shikona=values[7],
            )
        )

    return rows


def source_shikona_from_path(path: Path) -> str:
    """Return the search shikona represented by a cached HTML filename."""
    return unquote(path.stem)


def parse_page(path: Path) -> list[RikishiSearchRow]:
    """Parse one cached search-result page."""
    text = path.read_text(encoding="utf-8", errors="replace")
    source_shikona = source_shikona_from_path(path)

    for table_match in TABLE_PAT.finditer(text):
        rows = parse_result_table(source_shikona, table_match.group(1), table_match.group(2))
        if rows is not None:
            return rows

    raise ValueError(f"could not find expected result table in {path}")


def represented_rikids(history: History) -> set[str]:
    """Return rikishi ids represented in at least one History banzuke."""
    return {
        str(int(rikid))
        for rikid in make_history_shikona_by_rikid(history)
    }


def load_history(history_zip: Path | None) -> History:
    """Load History from a zip-backed path or the live store."""
    if history_zip is None:
        return get_history()
    return load_history_with_annotations(str(history_zip.with_suffix("")))


def parse_all(input_dir: Path, *, allowed_rikids: set[str]) -> list[RikishiSearchRow]:
    """Parse every cached search-result page in input_dir."""
    rows: list[RikishiSearchRow] = []
    failures: list[str] = []

    for path in sorted(input_dir.glob("*.html")):
        try:
            rows.extend(
                row
                for row in parse_page(path)
                if row.rikid in allowed_rikids
            )
        except Exception as exc:
            failures.append(f"{path}: {exc}")

    if failures:
        for failure in failures:
            print(f"[rikishi_aspx_parser] {failure}")
        raise SystemExit(1)

    return rows


def write_csv(rows: list[RikishiSearchRow], output_csv: Path) -> None:
    """Write parsed search rows to CSV."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_shikona",
                "rikid",
                "shikona",
                "heya",
                "shusshin",
                "birth_date",
                "highest_rank",
                "hatsu_dohyo",
                "intai",
                "last_shikona",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse cached Rikishi.aspx search-result pages to CSV."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=INPUT_DIR,
        help="Directory containing cached Rikishi.aspx search-result HTML.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=OUTPUT_CSV,
        help="CSV path to write. Defaults to rikishi_by_shikona.csv.",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        default=None,
        help="Optional History zip path. Defaults to the live store.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = load_history(args.history_zip)
    allowed_rikids = represented_rikids(history)
    rows = parse_all(args.input_dir, allowed_rikids=allowed_rikids)
    write_csv(rows, args.output_csv)
    print(
        f"[rikishi_aspx_parser] wrote {len(rows)} represented rows "
        f"to {args.output_csv}"
    )


if __name__ == "__main__":
    main()
