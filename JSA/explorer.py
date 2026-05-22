import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_FILES_DIR = Path("files")
DEFAULT_LANGUAGES = ("en", "ja")

# These rows appear to be banzuke table layout placeholders rather than rikishi.
# Pattern:
#   ew is present as an east/west number
#   banzuke_id is 0
#   every other field is the empty string
PLACEHOLDER_EW_VALUES = {1, 2, "1", "2"}


def read_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse JSON file: {path}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Expected top-level JSON object/dict in {path}, got {type(data).__name__}"
        )

    return data


def iter_banzuke_files(files_dir: Path, language: str) -> list[Path]:
    pattern = f"banzuke_{language}_division_*_page_*.json"
    return sorted(files_dir.glob(pattern))


def get_banzuke_rows(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """
    Return BanzukeTable rows if this cache file contains banzuke data.

    Some cached files are legitimate "past the end" responses from probing page N
    when only N-1 pages exist. Those may not contain BanzukeTable at all, so this
    explorer treats them as no-data files and skips them.
    """
    table = data.get("BanzukeTable")

    if table is None:
        return None

    if not isinstance(table, list):
        return None

    rows: list[dict[str, Any]] = []
    for row in table:
        if isinstance(row, dict):
            rows.append(row)

    return rows


def is_layout_placeholder_row(row: dict[str, Any]) -> bool:
    """
    Return True if a row matches the observed blank banzuke layout placeholder.

    Expected pattern:
      - ew is 1 or 2
      - banzuke_id is 0
      - every other field is ""

    This deliberately requires all non-ew/non-banzuke_id values to be empty strings,
    so genuinely partial rikishi records are not silently discarded.
    """
    if row.get("ew") not in PLACEHOLDER_EW_VALUES:
        return False

    if row.get("banzuke_id") != 0:
        return False

    for key, value in row.items():
        if key in {"ew", "banzuke_id"}:
            continue
        if value != "":
            return False

    return True


def explore_language(files_dir: Path, language: str) -> dict[str, Any]:
    files = iter_banzuke_files(files_dir, language)

    empty_counts: Counter[str] = Counter()
    null_counts: Counter[str] = Counter()
    present_counts: Counter[str] = Counter()

    raw_row_count = 0
    analysed_row_count = 0
    placeholder_row_count = 0
    files_with_rows = 0
    files_skipped_no_banzuke_table = 0

    for path in files:
        data = read_json_file(path)
        rows = get_banzuke_rows(data)

        if rows is None:
            files_skipped_no_banzuke_table += 1
            continue

        files_with_rows += 1

        for row in rows:
            raw_row_count += 1

            if is_layout_placeholder_row(row):
                placeholder_row_count += 1
                continue

            analysed_row_count += 1

            for key, value in row.items():
                present_counts[key] += 1

                if value == "":
                    empty_counts[key] += 1
                elif value is None:
                    null_counts[key] += 1

    keys_with_absence_values = sorted(
        key for key in set(empty_counts) | set(null_counts)
        if empty_counts[key] or null_counts[key]
    )

    return {
        "language": language,
        "files": files,
        "files_with_rows": files_with_rows,
        "files_skipped_no_banzuke_table": files_skipped_no_banzuke_table,
        "raw_row_count": raw_row_count,
        "placeholder_row_count": placeholder_row_count,
        "analysed_row_count": analysed_row_count,
        "present_counts": present_counts,
        "empty_counts": empty_counts,
        "null_counts": null_counts,
        "keys_with_absence_values": keys_with_absence_values,
    }


def print_language_report(result: dict[str, Any]) -> None:
    language = result["language"]
    files = result["files"]
    files_with_rows = result["files_with_rows"]
    files_skipped_no_banzuke_table = result["files_skipped_no_banzuke_table"]
    raw_row_count = result["raw_row_count"]
    placeholder_row_count = result["placeholder_row_count"]
    analysed_row_count = result["analysed_row_count"]
    present_counts = result["present_counts"]
    empty_counts = result["empty_counts"]
    null_counts = result["null_counts"]
    keys = result["keys_with_absence_values"]

    title = f"Language: {language}"
    print(title)
    print("=" * len(title))
    print(f"Files matched: {len(files)}")
    print(f"Files with BanzukeTable rows: {files_with_rows}")
    print(f"Files skipped with no banzuke data: {files_skipped_no_banzuke_table}")
    print(f"Raw BanzukeTable rows scanned: {raw_row_count}")
    print(f"Layout placeholder rows filtered out: {placeholder_row_count}")
    print(f"Rows analysed after filtering: {analysed_row_count}")
    print()

    if not keys:
        print('No analysed BanzukeTable fields contained "" or null values.')
        print()
        return

    print(f"{'key':<24} {'present':>10} {'empty_string':>14} {'null':>8}")
    print(f"{'-' * 24} {'-' * 10} {'-' * 14} {'-' * 8}")

    for key in keys:
        print(
            f"{key:<24} "
            f"{present_counts[key]:>10} "
            f"{empty_counts[key]:>14} "
            f"{null_counts[key]:>8}"
        )

    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Explore cached JSA banzuke JSON files and report BanzukeTable "
            "fields that contain empty strings or JSON null values, after "
            "filtering apparent layout-placeholder rows."
        )
    )

    parser.add_argument(
        "--files-dir",
        type=Path,
        default=DEFAULT_FILES_DIR,
        help="Directory containing cached banzuke JSON files. Default: files",
    )

    parser.add_argument(
        "--languages",
        nargs="+",
        default=list(DEFAULT_LANGUAGES),
        help="Language codes to scan. Default: en ja",
    )

    return parser.parse_args()


def main() -> None:
    print("This is definitely the new script")
    print("Filtering apparent layout-placeholder rows before blank/null analysis.")
    print()

    args = parse_args()

    for language in args.languages:
        result = explore_language(
            files_dir=args.files_dir,
            language=language,
        )
        print_language_report(result)


if __name__ == "__main__":
    main()
