"""Download SumoDB Rikishi.aspx search pages for duplicate History shikona."""

from __future__ import annotations

import argparse
import socket
from collections import Counter
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from src.infra.get_bios.make_public_shikona import make_history_shikona_by_rikid
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


BASE_URL = "https://sumodb.sumogames.de/Rikishi.aspx"
OUTPUT_DIR = (
    Path("files")
    / "output"
    / "infra"
    / "tracker"
    / "scraper"
    / "rikishi_aspx_scraper"
)
REQUEST_TIMEOUT_SECONDS = 30
REQUEST_PAUSE_SECONDS = 1
MINIMUM_FILE_SIZE_BYTES = 512
USER_AGENT = "Mozilla/5.0 (compatible; rikishi-aspx-scraper/1.0)"


def duplicate_history_shikona(history: History) -> tuple[str, ...]:
    """Return History shikona that belong to more than one represented rikishi."""
    shikona_by_rikid = make_history_shikona_by_rikid(history)
    counts = Counter(str(shikona) for shikona in shikona_by_rikid.values())
    return tuple(sorted(shikona for shikona, count in counts.items() if count > 1))


def search_url(shikona: str) -> str:
    """Return the SumoDB search-result URL for one shikona."""
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
    return f"{BASE_URL}?{query}"


def output_path(shikona: str) -> Path:
    """Return the local cache path for one shikona search page."""
    return OUTPUT_DIR / f"{quote(shikona, safe='')}.html"


def existing_page_is_usable(path: Path) -> bool:
    """Return whether a cached page is large enough to be worth reusing."""
    return path.exists() and path.stat().st_size >= MINIMUM_FILE_SIZE_BYTES


def download_page(shikona: str) -> bytes | None:
    """Download one SumoDB shikona search page."""
    request = Request(search_url(shikona), headers={"User-Agent": USER_AGENT})

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = response.read()
    except (HTTPError, URLError, TimeoutError, socket.timeout, OSError) as exc:
        print(f"[rikishi_aspx_scraper] {shikona}: download failed: {exc}")
        return None

    if len(data) < MINIMUM_FILE_SIZE_BYTES:
        print(
            f"[rikishi_aspx_scraper] {shikona}: response too small "
            f"({len(data)} bytes)"
        )
        return None

    return data


def save_page(path: Path, data: bytes) -> None:
    """Save a downloaded search page."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def scrape(history: History, *, force: bool = False) -> bool:
    """Ensure search pages exist for all duplicate History shikona."""
    shikona_values = duplicate_history_shikona(history)
    print(
        "[rikishi_aspx_scraper] "
        f"{len(shikona_values)} duplicate History shikona to check."
    )

    failed: list[str] = []
    changed = False

    for index, shikona in enumerate(shikona_values, start=1):
        path = output_path(shikona)

        if not force and existing_page_is_usable(path):
            continue

        print(
            "[rikishi_aspx_scraper] "
            f"{index}/{len(shikona_values)} downloading {shikona!r}"
        )
        data = download_page(shikona)
        if data is None:
            failed.append(shikona)
            sleep(REQUEST_PAUSE_SECONDS)
            continue

        save_page(path, data)
        changed = True
        sleep(REQUEST_PAUSE_SECONDS)

    if failed:
        print(
            "[rikishi_aspx_scraper] failed shikona: "
            + ", ".join(repr(shikona) for shikona in failed)
        )
        return False

    if changed:
        print("[rikishi_aspx_scraper] complete; cache changed.")
    else:
        print("[rikishi_aspx_scraper] complete; cache already current.")
    return True


def load_history(history_zip: str | None) -> History:
    """Load History from a zip-backed path or the live store."""
    if history_zip is None:
        return get_history()
    path = Path(history_zip)
    return load_history_with_annotations(str(path.with_suffix("")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Download SumoDB Rikishi.aspx search-result pages for non-unique "
            "History shikona."
        )
    )
    parser.add_argument(
        "--history-zip",
        default=None,
        help="Optional History zip path. Defaults to the live store.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download pages even when a cached file already exists.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = load_history(args.history_zip)
    if not scrape(history, force=args.force):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
