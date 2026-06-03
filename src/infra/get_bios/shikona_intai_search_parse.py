# src/infra/get_bios/shikona_intai_search_parse.py

"""
Parse cached SumoDB shikona-search pages for missing-Intai investigation.

This is an exploratory parser for the shikona normalisation work.  It reads the
cached pages downloaded by ``shikona_intai_search_download.py`` and emits
candidate rows.  It does not update ``rikishi_bios.json`` and it does not decide
which candidate should repair a missing Intai value.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, urlparse


OUTPUT_ROOT = Path("files") / "output" / "infra" / "get_bios"
DEFAULT_INPUT_DIR = OUTPUT_ROOT / "shikona_intai_search_download"
DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "shikona_intai_search_parse"

ROW_PAT = re.compile(r"<tr\b[^>]*>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
CELL_PAT = re.compile(r"<t[dh]\b[^>]*>\s*(.*?)\s*</t[dh]>", re.DOTALL | re.IGNORECASE)
LINK_PAT = re.compile(r"<a\b[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", re.DOTALL | re.IGNORECASE)
TAG_PAT = re.compile(r"<.*?>", re.DOTALL)
DATE_PAT = re.compile(r"(\d{4})\.(\d{2})")

EXPECTED_HEADERS = [
    "Shikona",
    "Heya",
    "Shusshin",
    "Highest Rank",
    "Hatsu Dohyo",
    "Intai",
]


@dataclass(frozen=True)
class CandidateRow:
    search_shikona: str
    rikid: str
    shikona: str
    heya: str
    shusshin: str
    highest_rank: str
    hatsu_dohyo: str
    intai: str


@dataclass(frozen=True)
class ParseFinding:
    search_shikona: str
    filename: str
    kind: str
    detail: str


def clean_html_text(text: str) -> str:
    text = TAG_PAT.sub("", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    return " ".join(text.split())


def normalize_basho_date(value: str) -> str:
    match = DATE_PAT.search(value)
    if match is None:
        return value
    return f"{match.group(1)}/{match.group(2)}"


def rikid_from_cell(cell_html: str) -> str:
    for link_match in LINK_PAT.finditer(cell_html):
        href = unescape(link_match.group(1))
        query = parse_qs(urlparse(href).query)
        value = query.get("r")
        if value:
            return f"{int(value[0]):05d}"
    return ""


def cells_from_row(row_html: str) -> list[str]:
    return [match.group(1) for match in CELL_PAT.finditer(row_html)]


def header_from_cells(cells: list[str]) -> list[str]:
    return [clean_html_text(cell) for cell in cells]


def looks_like_target_header(headers: list[str]) -> bool:
    return all(header in headers for header in EXPECTED_HEADERS)


def row_to_candidate(
    *,
    search_shikona: str,
    headers: list[str],
    cells: list[str],
) -> CandidateRow | None:
    if len(cells) != len(headers):
        return None

    values = {
        header: clean_html_text(cell)
        for header, cell in zip(headers, cells)
    }

    shikona_index = headers.index("Shikona")
    rikid = rikid_from_cell(cells[shikona_index])
    if not rikid:
        return None

    return CandidateRow(
        search_shikona=search_shikona,
        rikid=rikid,
        shikona=values["Shikona"],
        heya=values["Heya"],
        shusshin=values["Shusshin"],
        highest_rank=values["Highest Rank"],
        hatsu_dohyo=normalize_basho_date(values["Hatsu Dohyo"]),
        intai=normalize_basho_date(values["Intai"]),
    )


def parse_page(search_shikona: str, filename: str, text: str) -> tuple[list[CandidateRow], list[ParseFinding]]:
    headers: list[str] | None = None
    candidates: list[CandidateRow] = []
    findings: list[ParseFinding] = []

    for row_match in ROW_PAT.finditer(text):
        row_html = row_match.group(1)
        cells = cells_from_row(row_html)
        if not cells:
            continue

        if headers is None:
            possible_headers = header_from_cells(cells)
            if looks_like_target_header(possible_headers):
                headers = possible_headers
            continue

        candidate = row_to_candidate(
            search_shikona=search_shikona,
            headers=headers,
            cells=cells,
        )
        if candidate is not None:
            candidates.append(candidate)

    if headers is None:
        findings.append(
            ParseFinding(
                search_shikona=search_shikona,
                filename=filename,
                kind="header_not_found",
                detail="Could not find a SumoDB rikishi search-result header row with expected columns.",
            )
        )
    elif not candidates:
        findings.append(
            ParseFinding(
                search_shikona=search_shikona,
                filename=filename,
                kind="no_candidate_rows",
                detail="Found expected header row, but no candidate rows with Rikishi.aspx?r= links.",
            )
        )

    return candidates, findings


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_candidates(path: Path, rows: list[CandidateRow]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "search_shikona",
                "rikid",
                "shikona",
                "heya",
                "shusshin",
                "highest_rank",
                "hatsu_dohyo",
                "intai",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_findings(path: Path, rows: list[ParseFinding]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["search_shikona", "filename", "kind", "detail"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse cached SumoDB shikona-search pages for Intai candidates.",
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
        help=f"Downloader output directory (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Parser output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = input_dir / "manifest.csv"
    manifest = read_manifest(manifest_path)

    candidates: list[CandidateRow] = []
    findings: list[ParseFinding] = []

    for row in manifest:
        if row["status"] == "glitch":
            findings.append(
                ParseFinding(
                    search_shikona=row["shikona"],
                    filename=row["filename"],
                    kind="download_glitch",
                    detail="Downloader did not cache this page.",
                )
            )
            continue

        path = input_dir / row["filename"]
        text = path.read_text(encoding="utf-8")
        page_candidates, page_findings = parse_page(row["shikona"], row["filename"], text)
        candidates.extend(page_candidates)
        findings.extend(page_findings)

    candidate_path = output_dir / "intai_candidates.csv"
    findings_path = output_dir / "parse_findings.csv"

    write_candidates(candidate_path, candidates)
    write_findings(findings_path, findings)

    print(f"Parsed {len(manifest)} cached search pages.")
    print(f"Wrote {candidate_path}")
    print(f"Wrote {findings_path}")
    print(f"Candidate rows: {len(candidates)}")
    print(f"Parse findings: {len(findings)}")


if __name__ == "__main__":
    main()
