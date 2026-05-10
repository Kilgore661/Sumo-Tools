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
CELL_PAT = re.compile(r"<td\b[^>]*>\s*(.*?)\s*</td>", re.DOTALL | re.IGNORECASE)
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
HEIGHT_WEIGHT_PAT = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s+cm\s+(\d+(?:\.\d+)?)\s+kg\s*$",
    re.IGNORECASE,
)
TAG_PAT = re.compile(r"<.*?>", re.DOTALL)
DASH_SPLIT_PAT = re.compile(r"\s+[-‐-‒–—―]\s+")


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


def split_dash_list(value: str | None) -> list[str] | None:
    if not value:
        return None

    parts = [x.strip() for x in DASH_SPLIT_PAT.split(value) if x.strip()]
    return parts or None


def parse_height_weight(value: str | None) -> tuple[str, str] | None:
    if not value:
        return None

    match = HEIGHT_WEIGHT_PAT.fullmatch(value)
    if not match:
        return None

    return match.group(1), match.group(2)


def parse_career_table(
    text: str,
) -> tuple[
    OrderedDict[str, str],
    OrderedDict[str, str],
    OrderedDict[str, str],
    list[str],
]:
    table_html = extract_table(text, RIKISHI_TABLE_START_PAT)

    shikona_history = OrderedDict()
    height_history = OrderedDict()
    weight_history = OrderedDict()
    diagnostics = []

    awaiting_date_for = None

    for row_match in ROW_PAT.finditer(table_html):
        row_html = row_match.group(1)

        header_match = SHIKONA_HEADER_PAT.search(row_html)
        if header_match:
            if awaiting_date_for is not None:
                diagnostics.append(f"no first-use date found for shikona {awaiting_date_for!r}")

            awaiting_date_for = clean_html_text(header_match.group(1))
            continue

        date_match = BANZUKE_DATE_PAT.search(row_html)

        if awaiting_date_for is not None and date_match:
            shikona_history[yyyy_mm_from_yyyymm(date_match.group(1))] = awaiting_date_for
            awaiting_date_for = None

        if date_match:
            basho_date = yyyy_mm_from_yyyymm(date_match.group(1))

            for cell_match in CELL_PAT.finditer(row_html):
                cell_text = clean_html_text(cell_match.group(1))
                parsed = parse_height_weight(cell_text)

                if parsed is not None:
                    height, weight = parsed
                    height_history[basho_date] = height
                    weight_history[basho_date] = weight
                    break

    if awaiting_date_for is not None:
        diagnostics.append(f"no first-use date found for shikona {awaiting_date_for!r}")

    return shikona_history, height_history, weight_history, diagnostics


def expected_shikona_list(top_shikona: str | None) -> list[str]:
    if not top_shikona:
        return []
    return [x.strip() for x in DASH_SPLIT_PAT.split(top_shikona) if x.strip()]


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


def check_shikona_against_top_field(
    rikid: str,
    top_shikona: list[str],
    parsed_shikona: list[str],
) -> list[str]:
    diagnostics = []

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

    return diagnostics


def check_height_weight_against_top_field(
    rikid: str,
    top_height_weight: str | None,
    height_history: OrderedDict[str, str],
    weight_history: OrderedDict[str, str],
) -> list[str]:
    diagnostics = []

    top = parse_height_weight(top_height_weight)

    if top is None:
        if top_height_weight:
            diagnostics.append(
                f"{rikid}: could not parse top Height and Weight field: {top_height_weight!r}"
            )
        return diagnostics

    #if not height_history or not weight_history:
    #    diagnostics.append(
    #        f"{rikid}: top Height and Weight exists but no dated career-table values found: "
    #        f"top={top!r}"
    #    )
    #    return diagnostics

    #last_date = next(reversed(height_history))
    #career = (height_history[last_date], weight_history[last_date])

    #if top != career:
    #    diagnostics.append(
    #        f"{rikid}: top Height and Weight differs from career table: "
    #        f"top={top!r}, career={career!r} at {last_date}"
    #    )

    return diagnostics


def build_persisted_record(
    fields: dict[str, str],
    shikona_history: OrderedDict[str, str],
    height_history: OrderedDict[str, str],
    weight_history: OrderedDict[str, str],
) -> dict:

    top_height_weight = parse_height_weight(fields.get("Height and Weight"))

    if top_height_weight is None:
        height = None
        weight = None
    else:
        height, weight = top_height_weight

    return {
        "Birth Date": normalize_date(fields.get("Birth Date")),
        "Shusshin": fields.get("Shusshin") or None,
        "Heya": split_dash_list(fields.get("Heya")),
        "Shikona": shikona_history or None,
        "Hatsu Dohyo": normalize_date(fields.get("Hatsu Dohyo")),
        "Intai": normalize_date(fields.get("Intai")),
        "Height": height,
        "Weight": weight,
        "Height_by_Date": height_history or None,
        "Weight_by_Date": weight_history or None,
    }


def rikid_from_path(path: Path) -> str:
    return path.stem


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
            shikona_history, height_history, weight_history, career_diagnostics = parse_career_table(text)

            top_shikona = expected_shikona_list(fields.get("Shikona"))
            parsed_shikona = list(shikona_history.values())

            diagnostics.extend(
                check_shikona_against_top_field(rikid, top_shikona, parsed_shikona)
            )
            diagnostics.extend(f"{rikid}: {msg}" for msg in career_diagnostics)
            diagnostics.extend(check_shikona(rikid, shikona_history))
            diagnostics.extend(
                check_height_weight_against_top_field(
                    rikid,
                    fields.get("Height and Weight"),
                    height_history,
                    weight_history,
                )
            )

        except Exception as exc:
            print(f"{rikid}: parse error: {exc}")
            fields = {}
            unexpected = {f"PARSE ERROR: {exc}"}
            shikona_history = OrderedDict()
            height_history = OrderedDict()
            weight_history = OrderedDict()
            diagnostics.append(f"{rikid}: parse error: {exc}")

        if unexpected:
            all_unexpected[rikid] = sorted(unexpected)

        missing_row = {"rikid": rikid}
        for field in EXPECTED_FIELDS:
            missing_row[field] = "" if field in fields else "1"
        missing_rows.append(missing_row)

        persisted[rikid] = build_persisted_record(
            fields,
            shikona_history,
            height_history,
            weight_history,
        )

        #print(f"{rikid}: parsed")

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
