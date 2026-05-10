# src/infra/get_bios/parse.py

import csv
import re
from html import unescape
from pathlib import Path

from ..parser.parser2 import OUTPUT_DIR


BIO_DIR = Path(OUTPUT_DIR) / "infra" / "rikishi"
OUTPUT_CSV = Path(OUTPUT_DIR) / "infra" / "rikishi_bio_missing_fields.csv"

EXPECTED_FIELDS = [
    "Highest Rank",
    "Real Name",
    "Birth Date",
    "Shusshin",
    "Height and Weight",
    "University",
    "Heya",
    "Shikona",
    "Hatsu Dohyo",
    "Intai",
    "Kabu",
    "Death Date"
]

CAREER_RECORD = "Career Record"

H2_PAT = re.compile(r"<h2>\s*(.*?)\s*</h2>", re.DOTALL | re.IGNORECASE)
RIKISHIDATA_TABLE_START_PAT = re.compile(
    r'<table\s+class="rikishidata"\s+border="0"\s*>',
    re.DOTALL | re.IGNORECASE,
)
ROW_PAT = re.compile(r"<tr>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
CAT_VAL_PAT = re.compile(
    r'<td\s+class="cat"[^>]*>\s*(.*?)\s*</td>\s*'
    r'<td\s+class="val"[^>]*>\s*(.*?)\s*</td>',
    re.DOTALL | re.IGNORECASE,
)
TAG_PAT = re.compile(r"<.*?>", re.DOTALL)


def clean_html_text(text: str) -> str:
    """
    Convert a small HTML fragment to comparable plain text.
    """
    text = TAG_PAT.sub("", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    return " ".join(text.split())


def find_matching_table_end(text: str, table_start: int) -> int:
    """
    Return the index just after the matching </table> for the table that starts
    at table_start.

    This handles nested tables.
    """
    table_open_pat = re.compile(r"<table\b[^>]*>", re.IGNORECASE)
    table_close_pat = re.compile(r"</table>", re.IGNORECASE)

    pos = table_start
    depth = 0

    while True:
        open_match = table_open_pat.search(text, pos)
        close_match = table_close_pat.search(text, pos)

        if close_match is None:
            raise ValueError("could not find matching </table>")

        if open_match is not None and open_match.start() < close_match.start():
            depth += 1
            pos = open_match.end()
        else:
            depth -= 1
            pos = close_match.end()

            if depth == 0:
                return pos


def extract_first_rikishidata_table(text: str) -> str:
    """
    Extract the outer rikishidata table following the rikishi title.
    """
    start_match = RIKISHIDATA_TABLE_START_PAT.search(text)
    if start_match is None:
        raise ValueError("could not find rikishidata table")

    end = find_matching_table_end(text, start_match.start())
    return text[start_match.start():end]


def parse_bio_fields(text: str) -> tuple[set[str], set[str]]:
    """
    Parse known pre-Career Record fields.

    Returns:
        present_fields, unexpected_fields
    """
    table_html = extract_first_rikishidata_table(text)

    present = set()
    unexpected = set()

    for row_match in ROW_PAT.finditer(table_html):
        row_html = row_match.group(1)

        cat_val_match = CAT_VAL_PAT.search(row_html)
        if cat_val_match is None:
            continue

        heading = clean_html_text(cat_val_match.group(1))

        if not heading:
            continue

        if heading == CAREER_RECORD:
            break

        if heading in EXPECTED_FIELDS:
            present.add(heading)
        else:
            unexpected.add(heading)

    return present, unexpected


def rikid_from_path(path: Path) -> str:
    """
    Return the rikid as a 05d-style string, preserving the filename stem.
    """
    return path.stem


def main() -> None:
    if not BIO_DIR.exists():
        print(f"Bio directory does not exist: {BIO_DIR}")
        return

    html_files = sorted(BIO_DIR.glob("*.html"))

    rows = []
    all_unexpected = {}

    for path in html_files:
        rikid = rikid_from_path(path)

        try:
            text = path.read_text(encoding="utf-8")
            present, unexpected = parse_bio_fields(text)
        except Exception as exc:
            print(f"{rikid}: parse error: {exc}")
            present = set()
            unexpected = {f"PARSE ERROR: {exc}"}

        if unexpected:
            all_unexpected[rikid] = sorted(unexpected)

        row = {"rikid": rikid}
        for field in EXPECTED_FIELDS:
            row[field] = "" if field in present else "1"

        rows.append(row)
        #print(f"{rikid}: parsed")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rikid", *EXPECTED_FIELDS])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {OUTPUT_CSV}")

    if all_unexpected:
        print("\nUnexpected headings found:")
        for rikid, headings in all_unexpected.items():
            for heading in headings:
                print(f"  {rikid}: {heading}")
    else:
        print("\nNo unexpected headings found.")


if __name__ == "__main__":
    main()
