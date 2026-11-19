"""Compile historical heya observations from cached daily-results HTML."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .heya import DEFAULT_HEYA_INDEX, SCHEMA_VERSION


DEFAULT_HTML_RESULTS_ROOT = Path("files/output/HTML results")
DEFAULT_DIAGNOSTICS = Path(
    "files/output/analysis/torikumi_forcasting/heya_diagnostics.csv"
)
DATE_DIR_PATTERN = re.compile(r"^(\d{4})\s+(\d{2})$")


@dataclass(frozen=True)
class RawHeyaObservation:
    basho: str
    day: int
    rikid: int
    heya: str
    source_path: str
    line: int


@dataclass(frozen=True)
class HeyaDiagnostic:
    kind: str
    basho: str
    day: str
    rikid: str
    values: str
    source_path: str
    line: str
    detail: str


@dataclass(frozen=True)
class CompiledHeyaRecord:
    basho: str
    rikid: int
    heya: str
    observed_days: tuple[int, ...]
    observation_count: int


@dataclass(frozen=True)
class HeyaCompilation:
    records: tuple[CompiledHeyaRecord, ...]
    diagnostics: tuple[HeyaDiagnostic, ...]
    source_file_count: int
    observation_count: int
    first_basho: str | None
    last_basho: str | None

    @property
    def conflicts(self) -> tuple[HeyaDiagnostic, ...]:
        return tuple(row for row in self.diagnostics if row.kind == "conflicting_heya")


class _RikishiLinkParser(HTMLParser):
    def __init__(self, *, basho: str, day: int, source_path: str) -> None:
        super().__init__(convert_charrefs=True)
        self.basho = basho
        self.day = day
        self.source_path = source_path
        self.observations: list[RawHeyaObservation] = []
        self.diagnostics: list[HeyaDiagnostic] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href")
        title = attributes.get("title")
        if href is None or title is None:
            return
        rikid = _rikid_from_href(href)
        if rikid is None:
            return

        line, _ = self.getpos()
        fields = title.split(",", 2)
        if len(fields) < 2:
            self.diagnostics.append(
                HeyaDiagnostic(
                    kind="malformed_title",
                    basho=self.basho,
                    day=str(self.day),
                    rikid=str(rikid),
                    values=title,
                    source_path=self.source_path,
                    line=str(line),
                    detail="rikishi-link title has no second comma-separated field",
                )
            )
            return

        heya = fields[1].strip()
        if heya == "":
            self.diagnostics.append(
                HeyaDiagnostic(
                    kind="blank_heya",
                    basho=self.basho,
                    day=str(self.day),
                    rikid=str(rikid),
                    values="",
                    source_path=self.source_path,
                    line=str(line),
                    detail="rikishi-link title has a blank heya field",
                )
            )
            return

        self.observations.append(
            RawHeyaObservation(
                basho=self.basho,
                day=self.day,
                rikid=rikid,
                heya=heya,
                source_path=self.source_path,
                line=line,
            )
        )


def compile_heya_index(
    html_results_root: Path = DEFAULT_HTML_RESULTS_ROOT,
    *,
    start: str | None = None,
    end: str | None = None,
) -> HeyaCompilation:
    start_key = _parse_optional_basho(start)
    end_key = _parse_optional_basho(end)
    if start_key is not None and end_key is not None and start_key > end_key:
        raise ValueError(f"start basho {start} is after end basho {end}")

    observations: dict[tuple[str, int], list[RawHeyaObservation]] = defaultdict(list)
    diagnostics: list[HeyaDiagnostic] = []
    source_file_count = 0
    observation_count = 0
    represented_bashos: set[str] = set()

    for path, basho, day in _iter_source_files(html_results_root):
        basho_key = _parse_basho(basho)
        if start_key is not None and basho_key < start_key:
            continue
        if end_key is not None and basho_key > end_key:
            continue

        relative_path = path.relative_to(html_results_root).as_posix()
        parser = _RikishiLinkParser(
            basho=basho,
            day=day,
            source_path=relative_path,
        )
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        parser.close()
        source_file_count += 1
        represented_bashos.add(basho)
        diagnostics.extend(parser.diagnostics)
        observation_count += len(parser.observations)
        for observation in parser.observations:
            observations[(basho, observation.rikid)].append(observation)

    records: list[CompiledHeyaRecord] = []
    for (basho, rikid), rows in sorted(observations.items()):
        heya_values = sorted({row.heya for row in rows})
        if len(heya_values) != 1:
            first = rows[0]
            diagnostics.append(
                HeyaDiagnostic(
                    kind="conflicting_heya",
                    basho=basho,
                    day=" ".join(str(day) for day in sorted({row.day for row in rows})),
                    rikid=str(rikid),
                    values=" | ".join(heya_values),
                    source_path=first.source_path,
                    line=str(first.line),
                    detail="rikishi has more than one observed heya in one basho",
                )
            )
            continue

        records.append(
            CompiledHeyaRecord(
                basho=basho,
                rikid=rikid,
                heya=heya_values[0],
                observed_days=tuple(sorted({row.day for row in rows})),
                observation_count=len(rows),
            )
        )

    ordered_bashos = sorted(represented_bashos, key=_parse_basho)
    return HeyaCompilation(
        records=tuple(records),
        diagnostics=tuple(sorted(diagnostics, key=_diagnostic_key)),
        source_file_count=source_file_count,
        observation_count=observation_count,
        first_basho=ordered_bashos[0] if ordered_bashos else None,
        last_basho=ordered_bashos[-1] if ordered_bashos else None,
    )


def write_compilation(
    compilation: HeyaCompilation,
    *,
    output_path: Path = DEFAULT_HEYA_INDEX,
    diagnostics_path: Path = DEFAULT_DIAGNOSTICS,
    html_results_root: Path = DEFAULT_HTML_RESULTS_ROOT,
    generated_at: datetime | None = None,
) -> None:
    _write_diagnostics(diagnostics_path, compilation.diagnostics)
    if compilation.conflicts:
        raise ValueError(
            f"refusing to write heya index: {len(compilation.conflicts)} "
            f"within-basho conflicts; see {diagnostics_path}"
        )

    timestamp = generated_at or datetime.now(timezone.utc)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "html_results_root": str(html_results_root),
            "generated_at": timestamp.isoformat(),
            "source_file_count": compilation.source_file_count,
            "observation_count": compilation.observation_count,
            "record_count": len(compilation.records),
            "diagnostic_count": len(compilation.diagnostics),
            "first_basho": compilation.first_basho,
            "last_basho": compilation.last_basho,
        },
        "records": [
            {
                "basho": record.basho,
                "rikid": record.rikid,
                "heya": record.heya,
                "observed_days": list(record.observed_days),
                "observation_count": record.observation_count,
            }
            for record in compilation.records
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_diagnostics(path: Path, rows: tuple[HeyaDiagnostic, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "kind",
                "basho",
                "day",
                "rikid",
                "values",
                "source_path",
                "line",
                "detail",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def _iter_source_files(root: Path):
    if not root.exists():
        raise FileNotFoundError(f"HTML results root does not exist: {root}")
    for date_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        match = DATE_DIR_PATTERN.fullmatch(date_dir.name)
        if match is None:
            continue
        year, month = match.groups()
        basho = f"{year}/{month}"
        for path in sorted(date_dir.glob("*.html")):
            try:
                day = int(path.stem)
            except ValueError:
                continue
            yield path, basho, day


def _rikid_from_href(href: str) -> int | None:
    parsed = urlparse(href)
    if not parsed.path.endswith("Rikishi.aspx"):
        return None
    values = parse_qs(parsed.query).get("r", ())
    if not values:
        return None
    try:
        return int(values[0])
    except ValueError:
        return None


def _parse_optional_basho(value: str | None) -> tuple[int, int] | None:
    return _parse_basho(value) if value is not None else None


def _parse_basho(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})/(\d{2})", value)
    if match is None:
        raise ValueError(f"invalid basho {value!r}; expected YYYY/MM")
    year, month = (int(part) for part in match.groups())
    if not 1 <= month <= 12:
        raise ValueError(f"invalid basho month in {value!r}")
    return year, month


def _diagnostic_key(row: HeyaDiagnostic):
    return row.basho, int(row.rikid), row.kind, row.day, row.source_path, row.line


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile historical heya by basho from daily-results HTML."
    )
    parser.add_argument(
        "--html-results-root",
        type=Path,
        default=DEFAULT_HTML_RESULTS_ROOT,
    )
    parser.add_argument("--start", help="Optional first basho, YYYY/MM.")
    parser.add_argument("--end", help="Optional last basho, YYYY/MM.")
    parser.add_argument("--output", type=Path, default=DEFAULT_HEYA_INDEX)
    parser.add_argument("--diagnostics", type=Path, default=DEFAULT_DIAGNOSTICS)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    compilation = compile_heya_index(
        args.html_results_root,
        start=args.start,
        end=args.end,
    )
    write_compilation(
        compilation,
        output_path=args.output,
        diagnostics_path=args.diagnostics,
        html_results_root=args.html_results_root,
    )
    print(f"Wrote {args.output}")
    print(f"Wrote {args.diagnostics}")
    print(f"source files: {compilation.source_file_count:,}")
    print(f"observations: {compilation.observation_count:,}")
    print(f"records: {len(compilation.records):,}")
    print(f"diagnostics: {len(compilation.diagnostics):,}")
    print(f"range: {compilation.first_basho} to {compilation.last_basho}")


if __name__ == "__main__":
    main()
