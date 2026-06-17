import argparse
import unicodedata
import re
import json
from pathlib import Path
from typing import Any
from collections import defaultdict

import requests


FILES_DIR = Path("files")

BASES = {
    "en": [
        "https://www.sumo.or.jp/EnHonbashoBanzuke/indexAjax",
    ],
    "ja": [
        "https://www.sumo.or.jp/ResultBanzuke/indexAjax",
    ],
}

REFERERS = {
    "en": "https://www.sumo.or.jp/EnHonbashoBanzuke/index/",
    "ja": "https://www.sumo.or.jp/ResultBanzuke/table/",
}

SCRIPT_ROW_METADATA_KEYS = {
    "_language",
    "_division_id",
    "_page",
    "_division_name",
    "_source_url",
    "_cache_file",
}


def norm_romaji(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def get_headers(language: str) -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": REFERERS[language],
    }


def parse_json_text(text: str, url: str, content_type: str | None) -> dict[str, Any]:
    text = text.strip()

    if not text:
        raise RuntimeError(f"Empty response from {url}")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Could not parse response as JSON from {url}\n"
            f"Content-Type: {content_type}\n"
            f"First 500 chars:\n{text[:500]}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Expected JSON object/dict from {url}, got {type(data).__name__}"
        )

    return data


def get_json_from_url(
    session: requests.Session,
    url: str,
    language: str,
) -> dict[str, Any]:
    response = session.get(
        url,
        timeout=20,
        headers=get_headers(language),
    )

    response.raise_for_status()

    # JSA may return JSON while incorrectly labelling it as text/html.
    # Decode the bytes explicitly instead of inheriting requests' text heuristic.
    return parse_json_text(
        text=response.content.decode("utf-8"),
        url=url,
        content_type=response.headers.get("content-type"),
    )


def read_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse cached JSON file: {path}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Expected cached JSON object/dict in {path}, got {type(data).__name__}"
        )

    return data


def write_json_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def cache_path_for(language: str, division: int, page: int) -> Path:
    return FILES_DIR / f"banzuke_{language}_division_{division}_page_{page}.json"


def build_url(base: str, division: int, page: int) -> str:
    return f"{base.rstrip('/')}/{division}/{page}/"


def download_page_trying_bases(
    session: requests.Session,
    language: str,
    division: int,
    page: int,
) -> tuple[dict[str, Any], str]:
    errors: list[str] = []

    for base in BASES[language]:
        url = build_url(base, division, page)

        try:
            print(f"Downloading {language} division={division} page={page}: {url}")
            data = get_json_from_url(
                session=session,
                url=url,
                language=language,
            )
            return data, url
        except Exception as exc:
            errors.append(f"{url}\n  {type(exc).__name__}: {exc}")

    raise RuntimeError(
        f"Could not download {language} page from any candidate endpoint.\n\n"
        + "\n\n".join(errors)
    )


def get_banzuke_page(
    session: requests.Session,
    language: str,
    division: int,
    page: int,
    refresh: bool,
) -> tuple[dict[str, Any], str]:
    path = cache_path_for(language, division, page)

    if path.exists() and not refresh:
        data = read_json_file(path)

        source_url = data.get("_downloaded_from")
        if not isinstance(source_url, str):
            source_url = build_url(BASES[language][0], division, page)

        return data, source_url

    data, source_url = download_page_trying_bases(
        session=session,
        language=language,
        division=division,
        page=page,
    )

    data["_downloaded_from"] = source_url
    write_json_file(path, data)

    return data, source_url


def get_page_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("BanzukeTable", [])

    if not isinstance(rows, list):
        raise RuntimeError(
            f"Expected BanzukeTable to be a list, got {type(rows).__name__}"
        )

    return [
        r for r in rows
        if isinstance(r, dict)
        and r.get("rikishi_id")
        and r.get("shikona")
    ]


def fetch_banzuke_ajax(
    language: str,
    refresh: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with requests.Session() as session:
        for division in range(1, 7):
            for page in range(1, 50):
                data, source_url = get_banzuke_page(
                    session=session,
                    language=language,
                    division=division,
                    page=page,
                    refresh=refresh,
                )

                page_rows = get_page_rows(data)

                if not page_rows:
                    break

                for r in page_rows:
                    r["_language"] = language
                    r["_division_id"] = division
                    r["_page"] = page
                    r["_division_name"] = data.get("Kakuzuke")
                    r["_source_url"] = source_url
                    r["_cache_file"] = str(cache_path_for(language, division, page))

                rows.extend(page_rows)

    return rows


def partition_keys_by_value_equality(
    english_rows: list[dict[str, Any]],
    japanese_rows: list[dict[str, Any]],
) -> tuple[list[str], list[str], list[str]]:
    """
    Returns:
      language_independent_keys:
        Values are always identical in the English and Japanese rows.

      localized_keys:
        Values are always different in the English and Japanese rows.
        These are the keys where English contains the romanized/localized value
        and Japanese contains the Japanese string.

      mixed_keys:
        Values are the same for some row pairs and different for others.
    """
    if len(english_rows) != len(japanese_rows):
        raise RuntimeError(
            f"Row count mismatch: English={len(english_rows)}, Japanese={len(japanese_rows)}"
        )

    same_counts: dict[str, int] = defaultdict(int)
    diff_counts: dict[str, int] = defaultdict(int)

    for i, (en_row, ja_row) in enumerate(zip(english_rows, japanese_rows)):
        en_keys = set(en_row.keys()) - SCRIPT_ROW_METADATA_KEYS
        ja_keys = set(ja_row.keys()) - SCRIPT_ROW_METADATA_KEYS

        if en_keys != ja_keys:
            only_en = sorted(en_keys - ja_keys)
            only_ja = sorted(ja_keys - en_keys)
            raise RuntimeError(
                f"Key mismatch at row {i}\n"
                f"Only English: {only_en}\n"
                f"Only Japanese: {only_ja}"
            )

        for key in en_keys:
            if en_row.get(key) == ja_row.get(key):
                same_counts[key] += 1
            else:
                diff_counts[key] += 1

    total_rows = len(english_rows)
    keys = sorted(set(same_counts) | set(diff_counts))

    language_independent_keys: list[str] = []
    localized_keys: list[str] = []
    mixed_keys: list[str] = []

    for key in keys:
        same = same_counts[key]
        diff = diff_counts[key]

        if same == total_rows:
            language_independent_keys.append(key)
        elif diff == total_rows:
            localized_keys.append(key)
        else:
            mixed_keys.append(key)

    return language_independent_keys, localized_keys, mixed_keys


def collect_japanese_strings(
    japanese_rows: list[dict[str, Any]],
    localized_keys: list[str],
) -> list[dict[str, Any]]:
    japanese_strings: list[dict[str, Any]] = []

    for row_index, row in enumerate(japanese_rows):
        for key in localized_keys:
            value = row.get(key)

            if isinstance(value, str):
                japanese_strings.append(
                    {
                        "row": row_index,
                        "rikishi_id": row.get("rikishi_id"),
                        "key": key,
                        "value": value,
                    }
                )

    return japanese_strings


def print_string_list(title: str, values: list[str]) -> None:
    print(title)
    print("=" * len(title))
    if not values:
        print("  none")
    else:
        for value in values:
            print(f"  {value}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch English and Japanese JSA banzuke data from cached files "
            "or from the JSA AJAX endpoints, then partition keys by whether "
            "their English/Japanese values are identical or localized."
        )
    )

    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "Download English and Japanese banzuke pages again, even if cached "
            "files already exist."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    english_rows = fetch_banzuke_ajax(
        language="en",
        refresh=args.refresh,
    )

    japanese_rows = fetch_banzuke_ajax(
        language="ja",
        refresh=args.refresh,
    )

    language_independent_keys, localized_keys, mixed_keys = partition_keys_by_value_equality(
        english_rows=english_rows,
        japanese_rows=japanese_rows,
    )

    japanese_strings = collect_japanese_strings(
        japanese_rows=japanese_rows,
        localized_keys=localized_keys,
    )

    print(f"Compared {len(english_rows)} English/Japanese row pairs by list index.")
    print()

    print_string_list("Language-independent keys", language_independent_keys)
    print_string_list("Localized English/Japanese keys", localized_keys)
    print_string_list("Mixed keys", mixed_keys)

    print(f"Collected {len(japanese_strings)} Japanese strings from localized keys.")
    print("First 5 Japanese strings")
    print("========================")
    for item in japanese_strings[:5]:
        print(item, classify_japanese_string(item['value']))

import unicodedata


def is_kanji_char(ch: str) -> bool:
    code = ord(ch)

    # Main CJK Unified Ideographs + common extensions
    return (
        code == 0x3000 or                # space
        0x4E00 <= code <= 0x9FFF or      # CJK Unified Ideographs
        0x3400 <= code <= 0x4DBF or      # CJK Extension A
        0x20000 <= code <= 0x2A6DF or    # Extension B
        0x2A700 <= code <= 0x2B73F or    # Extension C
        0x2B740 <= code <= 0x2B81F or    # Extension D
        0x2B820 <= code <= 0x2CEAF or    # Extension E/F
        0x2CEB0 <= code <= 0x2EBEF or    # Extension G/H
        0xF900 <= code <= 0xFAFF         # CJK Compatibility Ideographs
    )


def is_katakana_char(ch: str) -> bool:
    code = ord(ch)

    return (
        0x30A0 <= code <= 0x30FF or      # Katakana
        0x31F0 <= code <= 0x31FF or      # Katakana Phonetic Extensions
        code == 0x3000 or                # space
        ch in {"ー", "・", "＝"}           # common in foreign words/names
    )


def classify_japanese_string(s: str) -> str:
    """
    Return 'kanji', 'kana', or 'neither'.

    Empty strings are classified as 'neither'.
    """
    if not s:
        return "neither"

    if all(is_kanji_char(ch) for ch in s):
        return "kanji"

    if all(is_katakana_char(ch) for ch in s):
        return "kana"

    return "neither"

if __name__ == "__main__":
    main()
