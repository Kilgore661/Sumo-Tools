"""Probe SumoDB rikishi-link title metadata for Japanese shikona headwords.

This module is an additive dirty-boundary probe. It does not change History or
the parser's production model. It scans cached SumoDB daily-results HTML and
writes one CSV row per rikishi id, plus observed metadata variants and
same-source Japanese headword duplicates.
"""

from time import time
t0 = time()

import argparse
import csv
import re
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.infra.parser.parser2 import OUTPUT_DIR


DEFAULT_HTML_RESULTS_ROOT = Path(OUTPUT_DIR) / "HTML results"
DEFAULT_CURRENT_STANDINGS_ROOT = Path(OUTPUT_DIR) / "current standings"
DEFAULT_OUTPUT_CSV = (
    Path(OUTPUT_DIR) / "infra" / "parser" / "sumodb_title_headwords_daily_results.csv"
)
DEFAULT_VARIANT_CSV = (
    Path(OUTPUT_DIR)
    / "infra"
    / "parser"
    / "sumodb_title_headword_variants_daily_results.csv"
)
DEFAULT_DUPLICATE_HEADWORD_CSV = (
    Path(OUTPUT_DIR)
    / "infra"
    / "parser"
    / "sumodb_title_headword_duplicates_daily_results.csv"
)
DEFAULT_BASHO_DUPLICATE_HEADWORD_CSV = (
    Path(OUTPUT_DIR)
    / "infra"
    / "parser"
    / "sumodb_title_headword_duplicates_by_basho_daily_results.csv"
)

DATE_DIR_PAT = re.compile(r"^(\d{4})\s+(\d{2})$")
CURRENT_STANDINGS_FILE_PAT = re.compile(r"^(\d{4})\s+(\d{2})\.html$")
LEADING_CHII_PAT = re.compile(r"^[A-Z][a-z]?\d+(?:[ew])?(?:[A-Z]+)?\s+")


@dataclass(frozen=True)
class LinkObservation:
    source_kind: str
    source_path: Path
    year: str
    month: str
    day: str
    line: int
    rikid: str
    romanised_text: str
    title: str

    @property
    def title_headword(self) -> str:
        return self.title_fields[0] if self.title_fields else ""

    @property
    def title_fields(self) -> tuple[str, ...]:
        return tuple(field.strip() for field in self.title.split(","))

    @property
    def title_field_count(self) -> int:
        return len(self.title_fields)

    @property
    def has_cjk_headword(self) -> bool:
        return contains_cjk_ideograph(self.title_headword)

    @property
    def has_japanese_headword(self) -> bool:
        return contains_japanese_character(self.title_headword)


@dataclass(frozen=True)
class RikishiTitleRecord:
    rikid: str
    romanised_shikona: str
    title_headword: str
    has_cjk_headword: bool
    has_japanese_headword: bool
    title_identity: str


@dataclass(frozen=True)
class RecordObservation:
    record: RikishiTitleRecord
    first_romanised_text: str
    first_title_field_count: int
    first_title: str
    source_kind: str
    source_path: Path
    year: str
    month: str
    day: str
    line: int


@dataclass(frozen=True)
class MetadataVariant:
    rikid: str
    field: str
    first_value: str
    current_value: str
    first_source_path: Path
    first_line: int
    current_source_path: Path
    current_line: int
    first_romanised_text: str
    current_romanised_text: str
    first_title: str
    current_title: str


@dataclass(frozen=True)
class DuplicateHeadword:
    source_kind: str
    source_path: Path
    year: str
    month: str
    day: str
    title_headword: str
    has_cjk_headword: bool
    has_japanese_headword: bool
    rikid: str
    romanised_shikona: str
    romanised_text: str
    title: str
    line: int


@dataclass(frozen=True)
class BashoDuplicateHeadword:
    source_kind: str
    year: str
    month: str
    title_headword: str
    has_cjk_headword: bool
    has_japanese_headword: bool
    rikid: str
    romanised_shikona: str
    romanised_text: str
    title: str
    first_day: str
    first_source_path: Path
    first_line: int
    observed_days: str


class RikishiLinkParser(HTMLParser):
    """Collect SumoDB Rikishi.aspx links and their title metadata."""

    def __init__(
        self,
        *,
        source_kind: str,
        source_path: Path,
        year: str,
        month: str,
        day: str,
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.source_kind = source_kind
        self.source_path = source_path
        self.year = year
        self.month = month
        self.day = day
        self._current_link: tuple[int, str, str] | None = None
        self._current_text: list[str] = []
        self.observations: list[LinkObservation] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        attr_map = dict(attrs)
        href = attr_map.get("href")
        title = attr_map.get("title")

        if href is None or title is None:
            return

        rikid = rikid_from_href(href)
        if rikid == "":
            return

        line, _ = self.getpos()
        self._current_link = (line, rikid, title)
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_link is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_link is None:
            return

        line, rikid, title = self._current_link
        romanised_text = " ".join("".join(self._current_text).split())

        self.observations.append(
            LinkObservation(
                source_kind=self.source_kind,
                source_path=self.source_path,
                year=self.year,
                month=self.month,
                day=self.day,
                line=line,
                rikid=rikid,
                romanised_text=romanised_text,
                title=title,
            )
        )

        self._current_link = None
        self._current_text = []


def record_for_observation(observation: LinkObservation) -> RikishiTitleRecord:
    return RikishiTitleRecord(
        rikid=observation.rikid,
        romanised_shikona=romanised_shikona_from_anchor_text(
            observation.romanised_text
        ),
        title_headword=observation.title_headword,
        has_cjk_headword=observation.has_cjk_headword,
        has_japanese_headword=observation.has_japanese_headword,
        title_identity=title_identity(observation.title_fields),
    )


def record_observation_for(
    observation: LinkObservation,
    record: RikishiTitleRecord,
) -> RecordObservation:
    return RecordObservation(
        record=record,
        first_romanised_text=observation.romanised_text,
        first_title_field_count=observation.title_field_count,
        first_title=observation.title,
        source_kind=observation.source_kind,
        source_path=observation.source_path,
        year=observation.year,
        month=observation.month,
        day=observation.day,
        line=observation.line,
    )


def contains_cjk_ideograph(text: str) -> bool:
    for char in text:
        if "CJK UNIFIED IDEOGRAPH" in unicodedata.name(char, ""):
            return True
    return False


def contains_japanese_character(text: str) -> bool:
    for char in text:
        name = unicodedata.name(char, "")
        if (
            "CJK UNIFIED IDEOGRAPH" in name
            or "HIRAGANA" in name
            or "KATAKANA" in name
        ):
            return True
    return False


def romanised_shikona_from_anchor_text(text: str) -> str:
    return LEADING_CHII_PAT.sub("", text)


def title_identity(title_fields: tuple[str, ...]) -> str:
    return ", ".join(title_fields[:6])


def rikid_from_href(href: str) -> str:
    parsed = urlparse(href)

    if not parsed.path.endswith("Rikishi.aspx"):
        return ""

    values = parse_qs(parsed.query).get("r", ())
    return values[0] if values else ""


def iter_source_files(
    *,
    html_results_root: Path,
    current_standings_root: Path,
    include_current_standings: bool,
) -> list[tuple[str, Path, str, str, str]]:
    rows = iter_html_results_files(html_results_root)

    if include_current_standings:
        rows.extend(iter_current_standings_files(current_standings_root))

    return rows


def infer_source_file(path: Path) -> tuple[str, Path, str, str, str]:
    current_match = CURRENT_STANDINGS_FILE_PAT.fullmatch(path.name)
    if current_match is not None:
        year, month = current_match.groups()
        return "current_standings", path, year, month, ""

    date_match = DATE_DIR_PAT.fullmatch(path.parent.name)
    if date_match is not None:
        year, month = date_match.groups()
        return "daily_results", path, year, month, path.stem

    return "html", path, "", "", ""


def iter_current_standings_files(root: Path) -> list[tuple[str, Path, str, str, str]]:
    rows: list[tuple[str, Path, str, str, str]] = []

    for path in sorted(root.glob("*.html")):
        match = CURRENT_STANDINGS_FILE_PAT.fullmatch(path.name)
        if match is None:
            continue

        year, month = match.groups()
        rows.append(("current_standings", path, year, month, ""))

    return rows


def iter_html_results_files(root: Path) -> list[tuple[str, Path, str, str, str]]:
    rows: list[tuple[str, Path, str, str, str]] = []

    for date_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        match = DATE_DIR_PAT.fullmatch(date_dir.name)
        if match is None:
            continue

        year, month = match.groups()

        for path in sorted(date_dir.glob("*.html")):
            rows.append(("daily_results", path, year, month, path.stem))

    return rows


def parse_observations(
    *,
    source_kind: str,
    source_path: Path,
    year: str,
    month: str,
    day: str,
) -> list[LinkObservation]:
    parser = RikishiLinkParser(
        source_kind=source_kind,
        source_path=source_path,
        year=year,
        month=month,
        day=day,
    )
    parser.feed(source_path.read_text(encoding="utf-8"))
    parser.close()
    return parser.observations


def variants_for(
    rikid: str,
    first: RecordObservation,
    current: RecordObservation,
) -> tuple[MetadataVariant, ...]:
    return tuple(
        MetadataVariant(
            rikid=rikid,
            field=field,
            first_value=str(getattr(first.record, field)),
            current_value=str(getattr(current.record, field)),
            first_source_path=first.source_path,
            first_line=first.line,
            current_source_path=current.source_path,
            current_line=current.line,
            first_romanised_text=first.first_romanised_text,
            current_romanised_text=current.first_romanised_text,
            first_title=first.first_title,
            current_title=current.first_title,
        )
        for field in RikishiTitleRecord.__dataclass_fields__
        if getattr(first.record, field) != getattr(current.record, field)
    )


def variant_key(variant: MetadataVariant) -> tuple[str, str, str, str]:
    return (
        variant.rikid,
        variant.field,
        variant.first_value,
        variant.current_value,
    )


def duplicate_headword_key(row: DuplicateHeadword) -> tuple[str, str, str]:
    return (str(row.source_path), row.title_headword, row.rikid)


def basho_duplicate_headword_key(
    row: BashoDuplicateHeadword,
) -> tuple[str, str, str, str]:
    return (row.year, row.month, row.title_headword, row.rikid)


def write_variant_csv(path: Path, variants: tuple[MetadataVariant, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rikid",
                "field",
                "first_value",
                "current_value",
                "first_source_path",
                "first_line",
                "current_source_path",
                "current_line",
                "first_romanised_text",
                "current_romanised_text",
                "first_title",
                "current_title",
            ],
        )
        writer.writeheader()

        for variant in variants:
            writer.writerow(
                {
                    "rikid": variant.rikid,
                    "field": variant.field,
                    "first_value": variant.first_value,
                    "current_value": variant.current_value,
                    "first_source_path": str(variant.first_source_path),
                    "first_line": variant.first_line,
                    "current_source_path": str(variant.current_source_path),
                    "current_line": variant.current_line,
                    "first_romanised_text": variant.first_romanised_text,
                    "current_romanised_text": variant.current_romanised_text,
                    "first_title": variant.first_title,
                    "current_title": variant.current_title,
                }
            )


def write_duplicate_headword_csv(
    path: Path,
    duplicate_headwords: tuple[DuplicateHeadword, ...],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_kind",
                "year",
                "month",
                "day",
                "source_path",
                "title_headword",
                "has_cjk_headword",
                "has_japanese_headword",
                "rikid",
                "romanised_shikona",
                "romanised_text",
                "title",
                "line",
            ],
        )
        writer.writeheader()

        for row in duplicate_headwords:
            writer.writerow(
                {
                    "source_kind": row.source_kind,
                    "year": row.year,
                    "month": row.month,
                    "day": row.day,
                    "source_path": str(row.source_path),
                    "title_headword": row.title_headword,
                    "has_cjk_headword": row.has_cjk_headword,
                    "has_japanese_headword": row.has_japanese_headword,
                    "rikid": row.rikid,
                    "romanised_shikona": row.romanised_shikona,
                    "romanised_text": row.romanised_text,
                    "title": row.title,
                    "line": row.line,
                }
            )


def write_basho_duplicate_headword_csv(
    path: Path,
    duplicate_headwords: tuple[BashoDuplicateHeadword, ...],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_kind",
                "year",
                "month",
                "title_headword",
                "has_cjk_headword",
                "has_japanese_headword",
                "rikid",
                "romanised_shikona",
                "romanised_text",
                "title",
                "first_day",
                "first_source_path",
                "first_line",
                "observed_days",
            ],
        )
        writer.writeheader()

        for row in duplicate_headwords:
            writer.writerow(
                {
                    "source_kind": row.source_kind,
                    "year": row.year,
                    "month": row.month,
                    "title_headword": row.title_headword,
                    "has_cjk_headword": row.has_cjk_headword,
                    "has_japanese_headword": row.has_japanese_headword,
                    "rikid": row.rikid,
                    "romanised_shikona": row.romanised_shikona,
                    "romanised_text": row.romanised_text,
                    "title": row.title,
                    "first_day": row.first_day,
                    "first_source_path": str(row.first_source_path),
                    "first_line": row.first_line,
                    "observed_days": row.observed_days,
                }
            )


def write_csv(
    path: Path,
    records_by_rikid: dict[str, RecordObservation],
    observation_counts_by_rikid: dict[str, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rikid",
                "romanised_shikona",
                "title_headword",
                "has_cjk_headword",
                "has_japanese_headword",
                "title_identity",
                "observation_count",
                "first_romanised_text",
                "first_title_field_count",
                "first_title",
                "first_source_kind",
                "first_year",
                "first_month",
                "first_day",
                "first_source_path",
                "first_line",
            ],
        )
        writer.writeheader()

        for rikid in sorted(records_by_rikid, key=int):
            record_observation = records_by_rikid[rikid]
            record = record_observation.record
            writer.writerow(
                {
                    "rikid": record.rikid,
                    "romanised_shikona": record.romanised_shikona,
                    "title_headword": record.title_headword,
                    "has_cjk_headword": record.has_cjk_headword,
                    "has_japanese_headword": record.has_japanese_headword,
                    "title_identity": record.title_identity,
                    "observation_count": observation_counts_by_rikid[rikid],
                    "first_romanised_text": record_observation.first_romanised_text,
                    "first_title_field_count": record_observation.first_title_field_count,
                    "first_title": record_observation.first_title,
                    "first_source_kind": record_observation.source_kind,
                    "first_year": record_observation.year,
                    "first_month": record_observation.month,
                    "first_day": record_observation.day,
                    "first_source_path": str(record_observation.source_path),
                    "first_line": record_observation.line,
                }
            )


def build_title_kanji_csv(
    *,
    html_results_root: Path = DEFAULT_HTML_RESULTS_ROOT,
    current_standings_root: Path = DEFAULT_CURRENT_STANDINGS_ROOT,
    include_current_standings: bool = False,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    variant_csv: Path = DEFAULT_VARIANT_CSV,
    duplicate_headword_csv: Path = DEFAULT_DUPLICATE_HEADWORD_CSV,
    basho_duplicate_headword_csv: Path = DEFAULT_BASHO_DUPLICATE_HEADWORD_CSV,
    source_files: tuple[Path, ...] = (),
) -> tuple[
    dict[str, RecordObservation],
    dict[str, int],
    int,
    tuple[MetadataVariant, ...],
    tuple[DuplicateHeadword, ...],
    tuple[BashoDuplicateHeadword, ...],
]:
    records_by_rikid: dict[str, RecordObservation] = {}
    observation_counts_by_rikid: dict[str, int] = {}
    variants_by_key: dict[tuple[str, str, str, str], MetadataVariant] = {}
    duplicate_headwords_by_key: dict[tuple[str, str, str], DuplicateHeadword] = {}
    basho_headwords: dict[tuple[str, str, str], dict[str, list[LinkObservation]]] = {}
    total_observation_count = 0

    sources = (
        [infer_source_file(path) for path in source_files]
        if source_files
        else iter_source_files(
            html_results_root=html_results_root,
            current_standings_root=current_standings_root,
            include_current_standings=include_current_standings,
        )
    )

    nn = len(sources)
    i = 0
    for source_kind, source_path, year, month, day in sources:
        observations = parse_observations(
            source_kind=source_kind,
            source_path=source_path,
            year=year,
            month=month,
            day=day,
        )
        source_headwords: dict[str, dict[str, LinkObservation]] = {}

        for observation in observations:
            record = record_for_observation(observation)
            current = record_observation_for(observation, record)
            if observation.has_japanese_headword:
                rikid_observations = source_headwords.setdefault(
                    observation.title_headword,
                    {},
                )
                rikid_observations.setdefault(observation.rikid, observation)
                basho_rikid_observations = basho_headwords.setdefault(
                    (observation.year, observation.month, observation.title_headword),
                    {},
                ).setdefault(observation.rikid, [])
                basho_rikid_observations.append(observation)

            if record.rikid in records_by_rikid:
                first = records_by_rikid[record.rikid]
                if first.record != record:
                    for variant in variants_for(record.rikid, first, current):
                        variants_by_key.setdefault(variant_key(variant), variant)
            else:
                records_by_rikid[record.rikid] = current
                observation_counts_by_rikid[record.rikid] = 0

            observation_counts_by_rikid[record.rikid] += 1
            total_observation_count += 1

        for title_headword, rikid_observations in source_headwords.items():
            if len(rikid_observations) < 2:
                continue

            for observation in rikid_observations.values():
                duplicate = DuplicateHeadword(
                    source_kind=observation.source_kind,
                    source_path=observation.source_path,
                    year=observation.year,
                    month=observation.month,
                    day=observation.day,
                    title_headword=observation.title_headword,
                    has_cjk_headword=observation.has_cjk_headword,
                    has_japanese_headword=observation.has_japanese_headword,
                    rikid=observation.rikid,
                    romanised_shikona=romanised_shikona_from_anchor_text(
                        observation.romanised_text
                    ),
                    romanised_text=observation.romanised_text,
                    title=observation.title,
                    line=observation.line,
                )
                duplicate_headwords_by_key.setdefault(
                    duplicate_headword_key(duplicate),
                    duplicate,
                )

        i += 1
        if i % 100 == 0:
            print( f'{i}/{nn}' )

    write_csv(output_csv, records_by_rikid, observation_counts_by_rikid)
    variants = tuple(variants_by_key.values())
    duplicate_headwords = tuple(duplicate_headwords_by_key.values())
    basho_duplicate_headwords_by_key: dict[
        tuple[str, str, str, str],
        BashoDuplicateHeadword,
    ] = {}

    for (year, month, title_headword), observations_by_rikid in basho_headwords.items():
        if len(observations_by_rikid) < 2:
            continue

        for rikid, observations in observations_by_rikid.items():
            first = observations[0]
            row = BashoDuplicateHeadword(
                source_kind=first.source_kind,
                year=year,
                month=month,
                title_headword=title_headword,
                has_cjk_headword=first.has_cjk_headword,
                has_japanese_headword=first.has_japanese_headword,
                rikid=rikid,
                romanised_shikona=romanised_shikona_from_anchor_text(
                    first.romanised_text
                ),
                romanised_text=first.romanised_text,
                title=first.title,
                first_day=first.day,
                first_source_path=first.source_path,
                first_line=first.line,
                observed_days=" ".join(sorted({observation.day for observation in observations})),
            )
            basho_duplicate_headwords_by_key.setdefault(
                basho_duplicate_headword_key(row),
                row,
            )

    basho_duplicate_headwords = tuple(basho_duplicate_headwords_by_key.values())
    write_variant_csv(variant_csv, variants)
    write_duplicate_headword_csv(duplicate_headword_csv, duplicate_headwords)
    write_basho_duplicate_headword_csv(
        basho_duplicate_headword_csv,
        basho_duplicate_headwords,
    )

    return (
        records_by_rikid,
        observation_counts_by_rikid,
        total_observation_count,
        variants,
        duplicate_headwords,
        basho_duplicate_headwords,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract SumoDB rikishi-link title metadata to CSV."
    )
    parser.add_argument(
        "--html-results-root",
        type=Path,
        default=DEFAULT_HTML_RESULTS_ROOT,
        help=f"Daily results HTML root. Default: {DEFAULT_HTML_RESULTS_ROOT}",
    )
    parser.add_argument(
        "--current-standings-root",
        type=Path,
        default=DEFAULT_CURRENT_STANDINGS_ROOT,
        help=(
            "Current standings HTML root, used only with --include-current-standings. "
            f"Default: {DEFAULT_CURRENT_STANDINGS_ROOT}"
        ),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DEFAULT_OUTPUT_CSV,
        help=f"Output CSV path. Default: {DEFAULT_OUTPUT_CSV}",
    )
    parser.add_argument(
        "--variant-csv",
        type=Path,
        default=DEFAULT_VARIANT_CSV,
        help=f"Variant CSV path. Default: {DEFAULT_VARIANT_CSV}",
    )
    parser.add_argument(
        "--conflict-csv",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--duplicate-headword-csv",
        type=Path,
        default=DEFAULT_DUPLICATE_HEADWORD_CSV,
        help=(
            "Same-source duplicate Japanese headword CSV path. "
            f"Default: {DEFAULT_DUPLICATE_HEADWORD_CSV}"
        ),
    )
    parser.add_argument(
        "--basho-duplicate-headword-csv",
        type=Path,
        default=DEFAULT_BASHO_DUPLICATE_HEADWORD_CSV,
        help=(
            "Basho-level duplicate Japanese headword CSV path. "
            f"Default: {DEFAULT_BASHO_DUPLICATE_HEADWORD_CSV}"
        ),
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        action="append",
        default=[],
        help=(
            "Scan one cached HTML file. May be supplied more than once. "
            "When omitted, the probe scans the configured roots."
        ),
    )
    parser.add_argument(
        "--include-current-standings",
        action="store_true",
        help=(
            "Also scan files/output/current standings. Default is daily results only."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    variant_csv = args.conflict_csv if args.conflict_csv is not None else args.variant_csv
    (
        records_by_rikid,
        _,
        total_observation_count,
        variants,
        duplicate_headwords,
        basho_duplicate_headwords,
    ) = build_title_kanji_csv(
        html_results_root=args.html_results_root,
        current_standings_root=args.current_standings_root,
        include_current_standings=args.include_current_standings,
        output_csv=args.output_csv,
        variant_csv=variant_csv,
        duplicate_headword_csv=args.duplicate_headword_csv,
        basho_duplicate_headword_csv=args.basho_duplicate_headword_csv,
        source_files=tuple(args.source_file),
    )

    records = [observation.record for observation in records_by_rikid.values()]
    cjk_count = sum(1 for record in records if record.has_cjk_headword)
    japanese_count = sum(1 for record in records if record.has_japanese_headword)
    print(f"Wrote {args.output_csv}")
    print(f"Wrote {variant_csv}")
    print(f"Wrote {args.duplicate_headword_csv}")
    print(f"Wrote {args.basho_duplicate_headword_csv}")
    print(f"observations scanned: {total_observation_count}")
    print(f"unique rikishi records: {len(records_by_rikid)}")
    print(f"unique records with CJK headword: {cjk_count}")
    print(f"unique records with Japanese headword: {japanese_count}")
    print(f"unique variant fields: {len(variants)}")
    print(f"same-source duplicate headword rows: {len(duplicate_headwords)}")
    print(f"basho-level duplicate headword rows: {len(basho_duplicate_headwords)}")


if __name__ == "__main__":
    main()
    print( f'{time()-t0:.0f} sec.' )
