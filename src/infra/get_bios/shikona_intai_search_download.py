# src/infra/get_bios/shikona_intai_search_download.py

"""
Download SumoDB shikona-search pages for missing-Intai investigation.

This is a dirty-boundary helper for the shikona normalisation work.  It does not
normalise labels and it does not update parsed bio data.  It only downloads and
caches the SumoDB search pages needed to investigate collision groups where the
normalisation probe could not find retirement dates.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import urlopen


OUTPUT_ROOT = Path("files") / "output" / "infra" / "get_bios"
DEFAULT_FINDINGS_CSV = (
    OUTPUT_ROOT
    / "shikona_normalisation_probe"
    / "unresolved_findings.csv"
)
DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "shikona_intai_search_download"

SEARCH_BASE_URL = "https://sumodb.sumogames.de/Rikishi.aspx"
DOWNLOAD_TIMEOUT_SECONDS = 10
REQUEST_PAUSE_SECONDS = 1
MINIMUM_FILE_SIZE_BYTES = 512

TARGET_FINDING_KINDS = {
    "missing_intai_in_collision_group",
    "missing_intai_year_for_suffix",
    "multiple_active_holders",
}


def search_url(shikona: str) -> str:
    query = urlencode(
        {
            "shikona": shikona,
            "heya": "-1",
            "shusshin": "-1",
            "b": "-1",
            "high": "-1",
            "hd": "-1",
            "entry": "-1",
            "intai": "-1",
            "sort": "1",
        }
    )
    return f"{SEARCH_BASE_URL}?{query}"


def cache_filename(shikona: str) -> str:
    return f"{quote(shikona, safe='')}.html"


def read_target_shikona(path: Path) -> list[str]:
    with path.open("r", newline="", encoding="utf-8") as f:
        rows = csv.DictReader(f)
        result = {
            row["latest_shikona"]
            for row in rows
            if row["kind"] in TARGET_FINDING_KINDS and row["latest_shikona"]
        }

    return sorted(result)


def download_text(url: str) -> str | None:
    try:
        with urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
            data = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"glitch: {url}: {exc}")
        return None

    if len(data) < MINIMUM_FILE_SIZE_BYTES:
        print(f"glitch: {url}: too small: {len(data)} bytes")
        return None

    return data.decode("utf-8", errors="replace")


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["shikona", "filename", "status", "url"],
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download SumoDB shikona-search pages for missing-Intai investigation.",
    )
    parser.add_argument(
        "--findings-csv",
        default=str(DEFAULT_FINDINGS_CSV),
        help=f"Normalisation unresolved findings CSV (default: {DEFAULT_FINDINGS_CSV})",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    findings_csv = Path(args.findings_csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = read_target_shikona(findings_csv)
    manifest_rows = []

    print(f"{len(targets)} shikona search pages required.")

    for shikona in targets:
        filename = cache_filename(shikona)
        output_file = output_dir / filename
        url = search_url(shikona)

        if output_file.exists():
            print(f"{shikona}: already downloaded")
            status = "cached"
        else:
            text = download_text(url)
            if text is None:
                status = "glitch"
            else:
                output_file.write_text(text, encoding="utf-8")
                print(f"{shikona}: saved {output_file}")
                status = "downloaded"

            sleep(REQUEST_PAUSE_SECONDS)

        manifest_rows.append(
            {
                "shikona": shikona,
                "filename": filename,
                "status": status,
                "url": url,
            }
        )

    manifest_path = output_dir / "manifest.csv"
    write_manifest(manifest_path, manifest_rows)
    print(f"\nWrote {manifest_path}")


if __name__ == "__main__":
    main()
