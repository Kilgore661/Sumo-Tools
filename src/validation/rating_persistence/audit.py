"""Produce a reproducible census of ranked-banzuke gaps and returns."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
from html import unescape
import json
from pathlib import Path
import re
from time import perf_counter
from typing import Iterable

from src.infra.live_store.api import get_history, published_name_file
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.validation.paths import RATING_PERSISTENCE_OUTPUT_ROOT


DEFAULT_RIKISHI_PAGES = Path("files/output/infra/get_bios/rikishi")
DEFAULT_OUTPUT_ROOT = RATING_PERSISTENCE_OUTPUT_ROOT / "output"

ROW_PATTERN = re.compile(r"<tr>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
BASHO_PATTERN = re.compile(r"Banzuke\.aspx\?b=(\d{6})", re.IGNORECASE)
CELL_PATTERN = re.compile(r"<td\b[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)
TAG_PATTERN = re.compile(r"<[^>]+>")


@dataclass(frozen=True, slots=True)
class CareerRow:
    date: Date
    status: str


@dataclass(frozen=True, slots=True)
class GapEvent:
    event_id: int
    rikishi_id: int
    shikona_before: str
    shikona_after: str
    last_ranked_basho: str
    last_chii: str
    last_chii_ordinal: int
    last_division: str
    return_basho: str
    return_chii: str
    return_chii_ordinal: int
    return_division: str
    represented_gap_basho_count: int
    represented_gap_bashos: str
    source_gap_row_count: int
    intervening_statuses: str
    status_sequence: str
    represented_status_complete: bool
    represented_bouts_during_gap: int
    bout_bashos_during_gap: str
    sekitori_before: bool
    sekitori_after: bool
    crosses_sekitori_boundary: bool
    exceptional: bool


@dataclass(frozen=True, slots=True)
class Census:
    events: tuple[GapEvent, ...]
    first_basho: Date
    last_basho: Date
    represented_basho_count: int
    distinct_ranked_rikishi: int


def census_gap_events(
    history: History,
    *,
    start: Date,
    end: Date,
    rikishi_pages: Path = DEFAULT_RIKISHI_PAGES,
) -> tuple[Census, dict[str, object]]:
    """Find every ranked disappearance followed by a ranked return."""

    if start > end:
        raise ValueError(f"Start date {start} is after end date {end}")
    dates = [date for date in sorted(history) if start <= date <= end]
    if not dates:
        raise ValueError("Selected History interval contains no represented basho")

    appearances: dict[RikId, list[tuple[int, Date, Chii, str]]] = defaultdict(list)
    bout_counts: Counter[tuple[Date, RikId]] = Counter()
    distinct: set[RikId] = set()
    for index, date in enumerate(dates):
        basho = history[date]
        distinct.update(basho.banzuke.riks)
        for rikishi in basho.banzuke.riks:
            appearances[rikishi].append(
                (
                    index,
                    date,
                    basho.banzuke.rikchii[rikishi],
                    str(basho.banzuke.rikshik[rikishi]),
                )
            )
        for day in basho.summary.values():
            for bout in day.results_lookup.values():
                bout_counts[(date, bout.rikishi1)] += 1
                bout_counts[(date, bout.rikishi2)] += 1

    raw_gaps: list[tuple[RikId, tuple, tuple, list[Date]]] = []
    for rikishi in sorted(appearances, key=int):
        observed = appearances[rikishi]
        for before, after in zip(observed, observed[1:], strict=False):
            if after[0] <= before[0] + 1:
                continue
            missing = dates[before[0] + 1 : after[0]]
            raw_gaps.append((rikishi, before, after, missing))

    required_ids = {rikishi for rikishi, *_ in raw_gaps}
    careers, page_source = _load_career_rows(rikishi_pages, required_ids)
    events: list[GapEvent] = []
    for event_id, (rikishi, before, after, missing) in enumerate(raw_gaps, start=1):
        _, before_date, before_chii, before_name = before
        _, after_date, after_chii, after_name = after
        source_rows = [
            row
            for row in careers[rikishi]
            if before_date < row.date < after_date
        ]
        source_by_date = {row.date: row.status for row in source_rows}
        status_complete = all(date in source_by_date for date in missing)
        bouts_by_date = {
            date: bout_counts[(date, rikishi)]
            for date in missing
            if bout_counts[(date, rikishi)]
        }
        before_sekitori = _is_sekitori(before_chii)
        after_sekitori = _is_sekitori(after_chii)
        last_division = _division(before_chii)
        return_division = _division(after_chii)
        exceptional = (
            last_division != "Jonokuchi"
            or return_division != "Jonokuchi"
            or bool(bouts_by_date)
            or not status_complete
            or before_sekitori
            or after_sekitori
        )
        events.append(
            GapEvent(
                event_id=event_id,
                rikishi_id=int(rikishi),
                shikona_before=before_name,
                shikona_after=after_name,
                last_ranked_basho=_date_text(before_date),
                last_chii=str(before_chii),
                last_chii_ordinal=before_chii.ordinal(),
                last_division=last_division,
                return_basho=_date_text(after_date),
                return_chii=str(after_chii),
                return_chii_ordinal=after_chii.ordinal(),
                return_division=return_division,
                represented_gap_basho_count=len(missing),
                represented_gap_bashos=";".join(_date_text(date) for date in missing),
                source_gap_row_count=len(source_rows),
                intervening_statuses=";".join(
                    f"{_date_text(row.date)}={row.status}" for row in source_rows
                ),
                status_sequence="->".join(row.status for row in source_rows),
                represented_status_complete=status_complete,
                represented_bouts_during_gap=sum(bouts_by_date.values()),
                bout_bashos_during_gap=";".join(
                    f"{_date_text(date)}={count}"
                    for date, count in sorted(bouts_by_date.items())
                ),
                sekitori_before=before_sekitori,
                sekitori_after=after_sekitori,
                crosses_sekitori_boundary=before_sekitori != after_sekitori,
                exceptional=exceptional,
            )
        )

    return (
        Census(
            events=tuple(events),
            first_basho=dates[0],
            last_basho=dates[-1],
            represented_basho_count=len(dates),
            distinct_ranked_rikishi=len(distinct),
        ),
        page_source,
    )


def parse_career_rows(html: str, *, rikishi_id: int) -> tuple[CareerRow, ...]:
    """Parse the date and rank/status cell from each SumoDB career row."""

    result: list[CareerRow] = []
    seen: set[Date] = set()
    for row_match in ROW_PATTERN.finditer(html):
        row_html = row_match.group(1)
        date_match = BASHO_PATTERN.search(row_html)
        if date_match is None:
            continue
        cells = CELL_PATTERN.findall(row_html)
        if len(cells) < 2:
            raise ValueError(
                f"Rikishi {rikishi_id} career row {date_match.group(1)} "
                "has fewer than two cells"
            )
        raw_date = date_match.group(1)
        date = Date.from_ints(int(raw_date[:4]), int(raw_date[4:]))
        if date in seen:
            raise ValueError(f"Rikishi {rikishi_id} has duplicate career row {date}")
        seen.add(date)
        status = _cell_text(cells[1]) or "??"
        result.append(CareerRow(date=date, status=status))
    if not result:
        raise ValueError(f"Rikishi {rikishi_id} page has no dated career rows")
    return tuple(sorted(result, key=lambda item: item.date))


def write_outputs(
    census: Census,
    *,
    history_source: dict[str, object],
    page_source: dict[str, object],
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    timestamp: datetime | None = None,
    run_seconds: float | None = None,
) -> Path:
    """Write atomic events, summaries, findings and provenance."""

    stamp = (timestamp or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    scope = f"{_date_file(census.first_basho)}_to_{_date_file(census.last_basho)}"
    output = output_root / f"rating-persistence-census_{scope}_{stamp}"
    output.mkdir(parents=True, exist_ok=False)

    events = list(census.events)
    _write_csv(output / "gap_events.csv", [asdict(event) for event in events])
    _write_csv(
        output / "exceptional_events.csv",
        [asdict(event) for event in events if event.exceptional],
        fieldnames=tuple(GapEvent.__dataclass_fields__),
    )

    transitions = Counter((e.last_division, e.return_division) for e in events)
    _write_csv(
        output / "division_transitions.csv",
        (
            {
                "last_division": before,
                "return_division": after,
                "event_count": count,
            }
            for (before, after), count in sorted(transitions.items())
        ),
    )
    gap_lengths = Counter(e.represented_gap_basho_count for e in events)
    _write_csv(
        output / "gap_length_distribution.csv",
        (
            {"represented_gap_basho_count": length, "event_count": count}
            for length, count in sorted(gap_lengths.items())
        ),
    )
    status_counts: Counter[str] = Counter()
    for event in events:
        for item in event.intervening_statuses.split(";"):
            if item:
                status_counts[item.split("=", maxsplit=1)[1]] += 1
    _write_csv(
        output / "intervening_statuses.csv",
        (
            {"status": status, "intervening_row_count": count}
            for status, count in sorted(status_counts.items())
        ),
    )

    returning_ids = {event.rikishi_id for event in events}
    jk_jk = sum(
        event.last_division == event.return_division == "Jonokuchi"
        for event in events
    )
    headline = {
        "first_basho": _date_text(census.first_basho),
        "last_basho": _date_text(census.last_basho),
        "represented_basho_count": census.represented_basho_count,
        "distinct_ranked_rikishi": census.distinct_ranked_rikishi,
        "gap_event_count": len(events),
        "distinct_returning_rikishi": len(returning_ids),
        "affected_ranked_rikishi_percent": (
            100.0 * len(returning_ids) / census.distinct_ranked_rikishi
            if census.distinct_ranked_rikishi
            else 0.0
        ),
        "jonokuchi_to_jonokuchi_events": jk_jk,
        "jonokuchi_to_jonokuchi_percent": (
            100.0 * jk_jk / len(events) if events else 0.0
        ),
        "status_complete_events": sum(e.represented_status_complete for e in events),
        "events_with_bouts_during_gap": sum(
            e.represented_bouts_during_gap > 0 for e in events
        ),
        "events_sekitori_before_or_after": sum(
            e.sekitori_before or e.sekitori_after for e in events
        ),
        "events_crossing_sekitori_boundary": sum(
            e.crosses_sekitori_boundary for e in events
        ),
        "exceptional_event_count": sum(e.exceptional for e in events),
    }
    _write_csv(
        output / "headline.csv",
        ({"metric": key, "value": value} for key, value in headline.items()),
    )
    manifest = {
        "created_at": (timestamp or datetime.now()).isoformat(timespec="seconds"),
        "interpretation": {
            "population": "ranked banzuke members in each represented History basho",
            "gap_event": (
                "two consecutive ranked appearances for one rikishi separated "
                "by at least one selected represented banzuke on which he is absent"
            ),
            "epoch_boundary": (
                "both bounding ranked appearances must occur in the selected interval"
            ),
            "bout_count": "represented result records involving the rikishi while off banzuke",
            "source_status": (
                "literal second cell in intervening cached SumoDB Rikishi.aspx career rows"
            ),
        },
        "history_source": history_source,
        "rikishi_page_source": page_source,
        "headline": headline,
        "wall_clock_seconds": run_seconds,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output / "findings.md").write_text(
        _findings(census, headline, transitions, status_counts),
        encoding="utf-8",
    )
    return output


def main(argv: list[str] | None = None) -> int:
    started = perf_counter()
    args = _parser().parse_args(argv)
    history, history_source = _load_history(args.history_zip)
    available = sorted(history)
    start = args.start or Date.from_ints(1989, 1)
    end = args.end or available[-1]
    census, page_source = census_gap_events(
        history,
        start=start,
        end=end,
        rikishi_pages=args.rikishi_pages,
    )
    elapsed = perf_counter() - started
    output = write_outputs(
        census,
        history_source=history_source,
        page_source=page_source,
        output_root=args.output_root,
        run_seconds=elapsed,
    )
    returning = {event.rikishi_id for event in census.events}
    jk_jk = sum(
        event.last_division == event.return_division == "Jonokuchi"
        for event in census.events
    )
    print(f"History: {_date_text(census.first_basho)} to {_date_text(census.last_basho)}")
    print(f"Gap events: {len(census.events):,}")
    print(f"Distinct returning rikishi: {len(returning):,}")
    print(f"Jonokuchi -> Jonokuchi: {jk_jk:,}")
    print(f"Output: {output.resolve()}")
    print(f"Total wall-clock time: {elapsed:.3f} seconds")
    return 0


def _load_career_rows(
    root: Path, required_ids: set[RikId]
) -> tuple[dict[RikId, tuple[CareerRow, ...]], dict[str, object]]:
    resolved = root.resolve()
    if not resolved.is_dir():
        raise FileNotFoundError(f"Rikishi-page directory not found: {resolved}")
    result: dict[RikId, tuple[CareerRow, ...]] = {}
    digest = hashlib.sha256()
    for rikishi in sorted(required_ids, key=int):
        path = resolved / f"{int(rikishi):05d}.html"
        if not path.is_file():
            raise FileNotFoundError(f"No cached Rikishi.aspx page for {int(rikishi)}: {path}")
        data = path.read_bytes()
        try:
            html = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"Cached rikishi page is not UTF-8: {path}") from error
        result[rikishi] = parse_career_rows(html, rikishi_id=int(rikishi))
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return result, {
        "path": str(resolved),
        "sha256": digest.hexdigest(),
        "file_count": len(required_ids),
    }


def _load_history(history_zip: Path | None) -> tuple[History, dict[str, object]]:
    if history_zip is None:
        history = get_history()
        return history, {
            "kind": "live_store",
            "published_name_file": str(published_name_file().resolve()),
            "sha256": None,
        }
    supplied = history_zip.resolve()
    zip_path = supplied if supplied.suffix.lower() == ".zip" else supplied.with_suffix(".zip")
    if not zip_path.is_file():
        raise FileNotFoundError(f"History zip not found: {zip_path}")
    history = load_history_with_annotations(str(zip_path.with_suffix("")))
    return history, {
        "kind": "history_zip",
        "path": str(zip_path),
        "sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
    }


def _write_csv(
    path: Path,
    rows: Iterable[dict[str, object]],
    *,
    fieldnames: tuple[str, ...] | None = None,
) -> None:
    materialised = list(rows)
    fields = fieldnames or (tuple(materialised[0]) if materialised else ())
    with path.open("x", newline="", encoding="utf-8") as stream:
        if not fields:
            return
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(materialised)


def _findings(
    census: Census,
    headline: dict[str, object],
    transitions: Counter[tuple[str, str]],
    status_counts: Counter[str],
) -> str:
    transition_lines = "\n".join(
        f"| {before} | {after} | {count:,} |"
        for (before, after), count in sorted(
            transitions.items(), key=lambda item: (-item[1], item[0])
        )
    )
    status_lines = "\n".join(
        f"| `{status}` | {count:,} |"
        for status, count in sorted(status_counts.items(), key=lambda item: (-item[1], item[0]))
    )
    return f"""# Rating-persistence census findings

## Scope and definition

The selected History interval is `{_date_text(census.first_basho)}` through
`{_date_text(census.last_basho)}`, containing
{census.represented_basho_count:,} represented basho and
{census.distinct_ranked_rikishi:,} distinct ranked rikishi.

A gap event is two consecutive ranked appearances for the same rikishi with at
least one selected represented banzuke between them on which he is absent.
Both bounding appearances must lie within this interval.

## Headline result

- Gap events: **{int(headline['gap_event_count']):,}**
- Distinct returning rikishi: **{int(headline['distinct_returning_rikishi']):,}**
- Share of ranked rikishi affected: **{float(headline['affected_ranked_rikishi_percent']):.3f}%**
- Jonokuchi-to-Jonokuchi events: **{int(headline['jonokuchi_to_jonokuchi_events']):,}**
  ({float(headline['jonokuchi_to_jonokuchi_percent']):.3f}%)
- Events with a represented bout while off-banzuke: **{int(headline['events_with_bouts_during_gap']):,}**
- Events involving sekitori rank before or after the gap: **{int(headline['events_sekitori_before_or_after']):,}**
- Events crossing the sekitori boundary: **{int(headline['events_crossing_sekitori_boundary']):,}**
- Events without a cached career status for every represented gap basho:
  **{int(headline['gap_event_count']) - int(headline['status_complete_events']):,}**

## Division transitions

| Last division | Return division | Events |
|---|---|---:|
{transition_lines}

## Intervening source statuses

These are literal rank/status cells in cached SumoDB career rows strictly
between the two ranked appearances.

| Status | Rows |
|---|---:|
{status_lines}

## Interpretation limit

This is a lifecycle census, not a comparison of rating policies. It establishes
how often the current Elo-89 replay discards a previously informed rating and
which kinds of careers are affected. It does not yet show whether persistence,
reinitialisation, decay, or another rule predicts post-return bouts better.
"""


def _cell_text(value: str) -> str:
    return unescape(TAG_PATTERN.sub("", value)).replace("\xa0", " ").strip()


def _division(chii: Chii) -> str:
    if isinstance(chii.level, MSD):
        return "Makuuchi"
    return {
        Division.JURYO: "Juryo",
        Division.MAKUSHITA: "Makushita",
        Division.SANDANME: "Sandanme",
        Division.JONIDAN: "Jonidan",
        Division.JONOKUCHI: "Jonokuchi",
    }[chii.level]


def _is_sekitori(chii: Chii) -> bool:
    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def _date_text(date: Date) -> str:
    return f"{int(date.year):04d}-{int(date.month):02d}"


def _date_file(date: Date) -> str:
    return _date_text(date)


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})[-/](\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM or YYYY/MM")
    try:
        return Date.from_ints(int(match.group(1)), int(match.group(2)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, help="Annotated History zip; otherwise use the live store.")
    parser.add_argument("--rikishi-pages", type=Path, default=DEFAULT_RIKISHI_PAGES)
    parser.add_argument("--start", type=_parse_date, help="First selected basho; default 1989-01.")
    parser.add_argument("--end", type=_parse_date, help="Last selected basho; default latest represented.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser
