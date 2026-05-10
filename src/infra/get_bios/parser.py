# src/infra/get_bios/parse.py

import csv
import json
import re
from collections import OrderedDict
from datetime import datetime
from html import unescape
from pathlib import Path

from ..parser.parser2 import OUTPUT_DIR


BIO_DIR = Path(OUTPUT_DIR) / "infra" / "rikishi"

MISSING_FIELDS_CSV = Path(OUTPUT_DIR) / "infra" / "rikishi_bio_missing_fields.csv"
OUTPUT_JSON = Path(OUTPUT_DIR) / "infra" / "rikishi_bios.json"

EXPECTED_FIELDS = [
    "Highest Rank",
    "Real Name",
    "Birth Date",
    "Death Date",
    "Shusshin",
    "Height and Weight",
    "University",
    "Heya",
    "Shikona",
    "Hatsu Dohyo",
    "Intai",
    "Kabu",
]

PERSISTED_FIELDS = [
    "Birth Date",
    "Shusshin",
    "Heya",
    "Shikona",
    "Hatsu Dohyo",
    "Intai",
]

CAREER_RECORD = "Career Record"

RIKISHIDATA_TABLE_START_PAT = re.compile(
    r'<table\s+class="rikishidata"\s+border="0"\s*>',
    re.DOTALL | re.IGNORECASE,
)
RIKISHI_TABLE_START_PAT = re.compile(
    r'<table\s+class="rikishi"\s+border="0"\s*>',
    re.DOTALL | re.IGNORECASE,
)
ROW_PAT = re.compile(r"<tr>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
CAT_VAL_PAT = re.compile(
    r'<td\s+class="cat"[^>]*>\s*(.*?)\s*</td>\s*'
    r'<td\s+class="val"[^>]*>\s*(.*?)\s*</td>',
    re.DOTALL | re.IGNORECASE,
)
SHIKONA_HEADER_PAT = re.compile(
    r'<th\s+colspan="6"\s*>\s*(.*?)\s*</th>',
    re.DOTALL | re.IGNORECASE,
)
BANZUKE_DATE_PAT = re.compile(
    r"<td>\s*<a\s+href='Banzuke\.aspx\?b=(\d{6})",
    re.DOTALL | re.IGNORECASE,
)
TAG_PAT = re.compile(r"<.*?>", re.DOTALL)
SHIKONA_SPLIT_PAT = re.compile(r"\s+[-‐-‒–—―]\s+")


def clean_html_text(text: str) -> str:
    text = TAG_PAT.sub("", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    return " ".join(text.split())


def find_matching_table_end(text: str, table_start: int) -> int:
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


def extract_table(text: str, start_pat: re.Pattern) -> str:
    start_match = start_pat.search(text)
    if start_match is None:
        raise ValueError(f"could not find table matching {start_pat.pattern}")

    end = find_matching_table_end(text, start_match.start())
    return text[start_match.start():end]


def parse_top_fields(text: str) -> tuple[dict[str, str], set[str]]:
    table_html = extract_table(text, RIKISHIDATA_TABLE_START_PAT)

    fields = {}
    unexpected = set()

    for row_match in ROW_PAT.finditer(table_html):
        row_html = row_match.group(1)

        cat_val_match = CAT_VAL_PAT.search(row_html)
        if cat_val_match is None:
            continue

        heading = clean_html_text(cat_val_match.group(1))
        value = clean_html_text(cat_val_match.group(2))

        if not heading:
            continue

        if heading == CAREER_RECORD:
            break

        if heading in EXPECTED_FIELDS:
            fields[heading] = value
        else:
            unexpected.add(heading)

    return fields, unexpected


def yyyy_mm_from_yyyymm(value: str) -> str:
    return f"{value[:4]}/{value[4:6]}"


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip()

    match = re.search(r"(\d{4})\.(\d{2})", value)
    if match:
        return f"{match.group(1)}/{match.group(2)}"

    try:
        dt = datetime.strptime(value, "%B %d, %Y")
        return f"{dt.year:04d}/{dt.month:02d}/{dt.day:02d}"
    except ValueError:
        return value


def parse_shikona_history(text: str) -> tuple[OrderedDict[str, str], list[str]]:
    table_html = extract_table(text, RIKISHI_TABLE_START_PAT)

    result = OrderedDict()
    diagnostics = []

    current_shikona = None
    awaiting_date_for = None

    for row_match in ROW_PAT.finditer(table_html):
        row_html = row_match.group(1)

        header_match = SHIKONA_HEADER_PAT.search(row_html)
        if header_match:
            if awaiting_date_for is not None:
                diagnostics.append(f"no first-use date found for shikona {awaiting_date_for!r}")

            current_shikona = clean_html_text(header_match.group(1))
            awaiting_date_for = current_shikona
            continue

        if awaiting_date_for is not None:
            date_match = BANZUKE_DATE_PAT.search(row_html)
            if date_match:
                result[yyyy_mm_from_yyyymm(date_match.group(1))] = awaiting_date_for
                awaiting_date_for = None

    if awaiting_date_for is not None:
        diagnostics.append(f"no first-use date found for shikona {awaiting_date_for!r}")

    return result, diagnostics


def expected_shikona_list(top_shikona: str | None) -> list[str]:
    if not top_shikona:
        return []
    return [x.strip() for x in SHIKONA_SPLIT_PAT.split(top_shikona) if x.strip()]


def check_shikona(rikid: str, shikona_history: OrderedDict[str, str]) -> list[str]:
    diagnostics = []

    for first_used, shikona in shikona_history.items():

        words = shikona.split()

        normalized_words = [
            w[:-1] if w.endswith("#") else w
            for w in words
        ]

        normalized = " ".join(normalized_words)

        if not re.fullmatch(r"[A-Za-z ]+", normalized):
            diagnostics.append(
                f"{rikid}: odd shikona chars at {first_used}: {shikona!r}"
            )

        if len(words) > 2:
            diagnostics.append(
                f"{rikid}: shikona has more than two words at {first_used}: {shikona!r}"
            )

    return diagnostics


def build_persisted_record(fields: dict[str, str], shikona_history: OrderedDict[str, str]) -> dict:
    return {
        "Birth Date": normalize_date(fields.get("Birth Date")),
        "Shusshin": fields.get("Shusshin") or None,
        "Heya": split_dash_list(fields.get("Heya")),
        "Shikona": shikona_history,
        "Hatsu Dohyo": normalize_date(fields.get("Hatsu Dohyo")),
        "Intai": normalize_date(fields.get("Intai")),
    }


def rikid_from_path(path: Path) -> str:
    return path.stem

def split_dash_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    parts = [x.strip() for x in SHIKONA_SPLIT_PAT.split(value) if x.strip()]
    return parts or None

def main() -> None:
    if not BIO_DIR.exists():
        print(f"Bio directory does not exist: {BIO_DIR}")
        return

    html_files = sorted(BIO_DIR.glob("*.html"))

    missing_rows = []
    all_unexpected = {}
    diagnostics = []
    persisted = OrderedDict()

    for path in html_files:
        rikid = rikid_from_path(path)

        try:
            text = path.read_text(encoding="utf-8")
            fields, unexpected = parse_top_fields(text)
            shikona_history, shikona_parse_diagnostics = parse_shikona_history(text)

            top_shikona = expected_shikona_list(fields.get("Shikona"))
            parsed_shikona = list(shikona_history.values())

            if top_shikona and parsed_shikona and top_shikona != parsed_shikona:

                max_len = max(len(top_shikona), len(parsed_shikona))

                diagnostics.append(
                    f"{rikid}: top Shikona field differs from career table:"
                )

                for i in range(max_len):

                    top_val = top_shikona[i] if i < len(top_shikona) else ""
                    parsed_val = parsed_shikona[i] if i < len(parsed_shikona) else ""

                    marker = "==" if top_val == parsed_val else "!="

                    diagnostics.append(
                        f"    {i:02d}: "
                        f"top={top_val!r:<30} "
                        f"{marker} "
                        f"career={parsed_val!r}"
                    )

            diagnostics.extend(f"{rikid}: {msg}" for msg in shikona_parse_diagnostics)
            diagnostics.extend(check_shikona(rikid, shikona_history))

        except Exception as exc:
            print(f"{rikid}: parse error: {exc}")
            fields = {}
            unexpected = {f"PARSE ERROR: {exc}"}
            shikona_history = OrderedDict()
            diagnostics.append(f"{rikid}: parse error: {exc}")

        if unexpected:
            all_unexpected[rikid] = sorted(unexpected)

        missing_row = {"rikid": rikid}
        for field in EXPECTED_FIELDS:
            missing_row[field] = "" if field in fields else "1"
        missing_rows.append(missing_row)

        persisted[rikid] = build_persisted_record(fields, shikona_history)

        print(f"{rikid}: parsed")

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(MISSING_FIELDS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rikid", *EXPECTED_FIELDS])
        writer.writeheader()
        writer.writerows(missing_rows)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(persisted, f, indent=4, ensure_ascii=False)

    print(f"\nWrote {MISSING_FIELDS_CSV}")
    print(f"Wrote {OUTPUT_JSON}")

    if all_unexpected:
        print("\nUnexpected top-section headings found:")
        for rikid, headings in all_unexpected.items():
            for heading in headings:
                print(f"  {rikid}: {heading}")
    else:
        print("\nNo unexpected top-section headings found.")

    if diagnostics:
        print("\nDiagnostics:")
        for msg in diagnostics:
            print(f"  {msg}")
    else:
        print("\nNo diagnostics.")


if __name__ == "__main__":
    main()
