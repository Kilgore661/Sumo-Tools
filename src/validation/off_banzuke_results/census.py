"""Census represented bouts whose endpoints are absent from the parsed banzuke."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from time import perf_counter
from typing import Iterable

from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History
from src.validation.paths import OFF_BANZUKE_RESULTS_OUTPUT_ROOT
from src.validation.rating_persistence.audit import parse_career_rows


DEFAULT_HISTORY = Path("files/output/Historys/1958_01 to 2026_11.zip")
DEFAULT_RIKISHI_PAGES = Path("files/output/infra/get_bios/rikishi")
DEFAULT_EQUELO_EXCLUSIONS = Path(
    "files/output/analysis/equelo2_baseline/full_history_1958_01_to_2026_07/"
    "excluded_bouts.csv"
)
DEFAULT_OUTPUT_ROOT = OFF_BANZUKE_RESULTS_OUTPUT_ROOT / "output"
ELO89_START = Date.from_ints(1989, 1)


@dataclass(frozen=True, slots=True)
class OffBanzukeBout:
    basho: str
    day: int
    post_1988: bool
    result_type: str
    rikishi_1: int
    shikona_1: str
    outcome_1: str
    on_banzuke_1: bool
    chii_1: str
    source_status_1: str
    rikishi_2: int
    shikona_2: str
    outcome_2: str
    on_banzuke_2: bool
    chii_2: str
    source_status_2: str
    decision: str
    missing_endpoint_count: int
    missing_statuses: str
    every_missing_endpoint_is_mz: bool
    elo89_selector_would_rate: bool


@dataclass(frozen=True, slots=True)
class Census:
    first_basho: Date
    last_basho: Date
    represented_result_count: int
    bouts: tuple[OffBanzukeBout, ...]
    missing_page_ids: tuple[int, ...]
    page_source: dict[str, object]
    sawada_2026_07_result_count: int
    sawada_2026_07_on_banzuke: bool
    sawada_2026_07_chii: str


def census_off_banzuke_results(
    history: History,
    *,
    start: Date,
    end: Date,
    career_statuses: dict[RikId, dict[Date, str]],
    page_source: dict[str, object] | None = None,
    missing_page_ids: Iterable[int] = (),
) -> Census:
    """Return every represented result with at least one absent endpoint."""

    dates = [date for date in sorted(history) if start <= date <= end]
    if not dates:
        raise ValueError("Selected History interval contains no represented basho")

    known_names: dict[RikId, str] = {}
    for date in sorted(history):
        for rikishi, shikona in history[date].banzuke.rikshik.items():
            known_names[rikishi] = str(shikona)

    represented_result_count = 0
    bouts: list[OffBanzukeBout] = []
    sawada_results = 0
    sawada_present = False
    sawada_chii = ""
    sawada = RikId(13011)
    sawada_date = Date.from_ints(2026, 7)

    for date in dates:
        basho = history[date]
        if date == sawada_date:
            sawada_present = sawada in basho.banzuke.riks
            if sawada_present:
                sawada_chii = str(basho.banzuke.rikchii[sawada])
        for day in sorted(basho.summary):
            results = sorted(
                basho.summary[day].results_lookup.values(),
                key=lambda row: (int(row.rikishi1), int(row.rikishi2)),
            )
            for result in results:
                represented_result_count += 1
                endpoints = (result.rikishi1, result.rikishi2)
                if date == sawada_date and sawada in endpoints:
                    sawada_results += 1
                membership = tuple(rikishi in basho.banzuke.riks for rikishi in endpoints)
                if all(membership):
                    continue
                statuses = tuple(
                    ""
                    if present
                    else career_statuses.get(rikishi, {}).get(date, "NO_CAREER_ROW")
                    for rikishi, present in zip(endpoints, membership, strict=True)
                )
                missing_statuses = [
                    status for status, present in zip(statuses, membership, strict=True)
                    if not present
                ]
                result_type = _result_type(result.outcome1, result.outcome2)
                bouts.append(
                    OffBanzukeBout(
                        basho=_date_text(date),
                        day=int(day),
                        post_1988=date >= ELO89_START,
                        result_type=result_type,
                        rikishi_1=int(result.rikishi1),
                        shikona_1=known_names.get(result.rikishi1, ""),
                        outcome_1=result.outcome1.name,
                        on_banzuke_1=membership[0],
                        chii_1=(
                            str(basho.banzuke.rikchii[result.rikishi1])
                            if membership[0]
                            else ""
                        ),
                        source_status_1=statuses[0],
                        rikishi_2=int(result.rikishi2),
                        shikona_2=known_names.get(result.rikishi2, ""),
                        outcome_2=result.outcome2.name,
                        on_banzuke_2=membership[1],
                        chii_2=(
                            str(basho.banzuke.rikchii[result.rikishi2])
                            if membership[1]
                            else ""
                        ),
                        source_status_2=statuses[1],
                        decision=str(result.decision),
                        missing_endpoint_count=2 - sum(membership),
                        missing_statuses=";".join(missing_statuses),
                        every_missing_endpoint_is_mz=all(
                            status == "Mz" for status in missing_statuses
                        ),
                        elo89_selector_would_rate=result_type == "W/L",
                    )
                )

    return Census(
        first_basho=dates[0],
        last_basho=dates[-1],
        represented_result_count=represented_result_count,
        bouts=tuple(bouts),
        missing_page_ids=tuple(sorted(set(missing_page_ids))),
        page_source=page_source or {},
        sawada_2026_07_result_count=sawada_results,
        sawada_2026_07_on_banzuke=sawada_present,
        sawada_2026_07_chii=sawada_chii,
    )


def required_missing_ids(history: History, *, start: Date, end: Date) -> set[RikId]:
    """Find identities needing same-basho source-status lookup."""

    result: set[RikId] = set()
    for date in sorted(date for date in history if start <= date <= end):
        basho = history[date]
        for daily in basho.summary.values():
            for bout in daily.results_lookup.values():
                for rikishi in (bout.rikishi1, bout.rikishi2):
                    if rikishi not in basho.banzuke.riks:
                        result.add(rikishi)
    return result


def load_career_statuses(
    root: Path, required_ids: set[RikId]
) -> tuple[dict[RikId, dict[Date, str]], dict[str, object], tuple[int, ...]]:
    """Load literal same-basho statuses for missing bout endpoints."""

    resolved = root.resolve()
    if not resolved.is_dir():
        raise FileNotFoundError(f"Rikishi-page directory not found: {resolved}")
    statuses: dict[RikId, dict[Date, str]] = {}
    missing: list[int] = []
    digest = hashlib.sha256()
    loaded = 0
    for rikishi in sorted(required_ids, key=int):
        path = resolved / f"{int(rikishi):05d}.html"
        if not path.is_file():
            missing.append(int(rikishi))
            statuses[rikishi] = {}
            continue
        data = path.read_bytes()
        rows = parse_career_rows(data.decode("utf-8"), rikishi_id=int(rikishi))
        statuses[rikishi] = {row.date: row.status for row in rows}
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
        loaded += 1
    return statuses, {
        "path": str(resolved),
        "sha256": digest.hexdigest(),
        "requested_file_count": len(required_ids),
        "loaded_file_count": loaded,
        "missing_file_count": len(missing),
    }, tuple(missing)


def write_outputs(
    census: Census,
    *,
    history_source: dict[str, object],
    equelo_exclusions: Path | None,
    output_root: Path,
    elapsed_seconds: float,
) -> Path:
    """Write the atomic census, two-question summary and provenance."""

    output = output_root / (
        f"off-banzuke-census_{_date_text(census.first_basho)}_to_"
        f"{_date_text(census.last_basho)}_{datetime.now():%Y-%m-%d_%H-%M-%S}"
    )
    output.mkdir(parents=True, exist_ok=False)
    rows = [asdict(row) for row in census.bouts]
    fields = tuple(OffBanzukeBout.__dataclass_fields__)
    _write_csv(output / "off_banzuke_bouts.csv", rows, fieldnames=fields)

    summaries = _summary_rows(census)
    _write_csv(output / "epoch_status_summary.csv", summaries)
    statuses = Counter(
        status
        for row in census.bouts
        for status in row.missing_statuses.split(";")
        if status
    )
    _write_csv(
        output / "missing_status_summary.csv",
        (
            {"source_status": status, "missing_endpoint_count": count}
            for status, count in sorted(statuses.items())
        ),
        fieldnames=("source_status", "missing_endpoint_count"),
    )
    reconciliation = _reconcile_equelo(census, equelo_exclusions)
    _write_csv(
        output / "known_case_reconciliation.csv",
        reconciliation,
        fieldnames=(
            "basho", "day", "rikishi_1", "rikishi_2",
            "found_in_current_census", "current_missing_statuses",
        ),
    )
    violations: list[str] = []
    if census.missing_page_ids:
        violations.append(
            "Missing cached career pages for IDs: "
            + ", ".join(map(str, census.missing_page_ids))
        )
    if census.sawada_2026_07_result_count != 7:
        violations.append(
            "Expected seven represented 2026-07 results involving RikId 13011, "
            f"found {census.sawada_2026_07_result_count}"
        )
    if not census.sawada_2026_07_on_banzuke:
        violations.append("RikId 13011 is absent from the repaired 2026-07 banzuke")
    _write_csv(
        output / "violations.csv",
        ({"violation": item} for item in violations),
        fieldnames=("violation",),
    )

    post = next(row for row in summaries if row["epoch"] == "post_1988")
    pre = next(row for row in summaries if row["epoch"] == "pre_1989")
    headline = {
        "post_1988_off_banzuke_bouts": post["off_banzuke_bout_count"],
        "post_1988_missing_endpoints": post["missing_endpoint_count"],
        "post_1988_mz_endpoints": post["mz_endpoint_count"],
        "pre_1989_off_banzuke_bouts": pre["off_banzuke_bout_count"],
        "pre_1989_missing_endpoints": pre["missing_endpoint_count"],
        "pre_1989_mz_endpoints": pre["mz_endpoint_count"],
        "all_missing_endpoints_are_mz": all(
            row.every_missing_endpoint_is_mz for row in census.bouts
        ),
        "sawada_2026_07_results": census.sawada_2026_07_result_count,
        "sawada_2026_07_on_banzuke": census.sawada_2026_07_on_banzuke,
        "sawada_2026_07_chii": census.sawada_2026_07_chii,
        "violation_count": len(violations),
    }
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "definition": (
            "represented History result with at least one endpoint absent from "
            "the same basho's parsed banzuke.riks"
        ),
        "history_source": history_source,
        "career_page_source": census.page_source,
        "headline": headline,
        "wall_clock_seconds": elapsed_seconds,
        "git": _git_state(),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "findings.md").write_text(
        _findings(census, headline), encoding="utf-8"
    )
    return output


def _summary_rows(census: Census) -> list[dict[str, object]]:
    result = []
    for epoch, selected in (
        ("pre_1989", [row for row in census.bouts if not row.post_1988]),
        ("post_1988", [row for row in census.bouts if row.post_1988]),
        ("all", list(census.bouts)),
    ):
        missing_statuses = [
            status
            for row in selected
            for status in row.missing_statuses.split(";")
            if status
        ]
        result.append({
            "epoch": epoch,
            "off_banzuke_bout_count": len(selected),
            "wl_bout_count": sum(row.result_type == "W/L" for row in selected),
            "missing_endpoint_count": sum(row.missing_endpoint_count for row in selected),
            "mz_endpoint_count": sum(status == "Mz" for status in missing_statuses),
            "non_mz_endpoint_count": sum(status != "Mz" for status in missing_statuses),
            "all_missing_endpoints_are_mz": (
                all(status == "Mz" for status in missing_statuses)
                if missing_statuses
                else ""
            ),
        })
    return result


def _reconcile_equelo(
    census: Census, path: Path | None
) -> list[dict[str, object]]:
    if path is None or not path.is_file():
        return []
    current = {
        (row.basho.replace("-", "/"), str(row.day), str(row.rikishi_1), str(row.rikishi_2)): row
        for row in census.bouts
    }
    result = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            if row.get("reason") != "participant_not_on_banzuke":
                continue
            key = (row["basho"], row["day"], row["rikishi_1"], row["rikishi_2"])
            matched = current.get(key)
            result.append({
                "basho": row["basho"],
                "day": row["day"],
                "rikishi_1": row["rikishi_1"],
                "rikishi_2": row["rikishi_2"],
                "found_in_current_census": matched is not None,
                "current_missing_statuses": "" if matched is None else matched.missing_statuses,
            })
    return result


def _findings(census: Census, headline: dict[str, object]) -> str:
    return f"""# Off-banzuke result census findings

## The two questions

1. **Are the absent participants actually Mz?**

   Across the complete selected History, there are
   **{sum(row.missing_endpoint_count for row in census.bouts):,}** missing bout
   endpoints. **{sum(status == 'Mz' for row in census.bouts for status in row.missing_statuses.split(';')):,}**
   have the literal same-basho source status `Mz`. Every missing endpoint is
   Mz: **{headline['all_missing_endpoints_are_mz']}**.

2. **Do any occur in the post-1988 Elo-89 era?**

   Post-1988 off-banzuke bouts: **{int(headline['post_1988_off_banzuke_bouts']):,}**.
   Pre-1989 off-banzuke bouts: **{int(headline['pre_1989_off_banzuke_bouts']):,}**.

## Known repaired case

RikId 13011 has **{int(headline['sawada_2026_07_results']):,}** represented
results in `2026-07`. He is present on the repaired parsed banzuke:
**{headline['sawada_2026_07_on_banzuke']}**, at
`{headline['sawada_2026_07_chii']}`. Those bouts are therefore not current
off-banzuke observations.

## Interpretation

This census concerns results already represented in canonical `History`. It
does not claim that the upstream source contains no additional Mz bouts which
the ranked-only parser omits. If the post-1988 count is zero, the current
include-versus-exclude contract has no numerical effect on Elo-89's represented
history; source completeness remains a separate question.
"""


def _result_type(left: Outcome, right: Outcome) -> str:
    outcomes = {left, right}
    if outcomes == {Outcome.W, Outcome.L}:
        return "W/L"
    if outcomes == {Outcome.FS, Outcome.FP}:
        return "fusen"
    return "other"


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


def _git_state() -> dict[str, object]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
    return {"commit": commit, "dirty": dirty}


def _date_text(date: Date) -> str:
    return f"{int(date.year):04d}-{int(date.month):02d}"


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})[-/](\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM or YYYY/MM")
    return Date.from_ints(int(match.group(1)), int(match.group(2)))


def _identity(path: Path) -> dict[str, object]:
    resolved = path.resolve()
    return {"kind": "history_zip", "path": str(resolved), "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--rikishi-pages", type=Path, default=DEFAULT_RIKISHI_PAGES)
    parser.add_argument("--start", type=_parse_date, default=Date.from_ints(1958, 1))
    parser.add_argument("--end", type=_parse_date, default=Date.from_ints(2026, 9))
    parser.add_argument("--equelo-exclusions", type=Path, default=DEFAULT_EQUELO_EXCLUSIONS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    started = perf_counter()
    args = _parser().parse_args(argv)
    history_path = args.history_zip.resolve()
    if history_path.suffix.lower() != ".zip":
        history_path = history_path.with_suffix(".zip")
    if not history_path.is_file():
        raise FileNotFoundError(f"History zip not found: {history_path}")
    history = load_history_with_annotations(str(history_path.with_suffix("")))
    missing_ids = required_missing_ids(history, start=args.start, end=args.end)
    statuses, page_source, missing_pages = load_career_statuses(
        args.rikishi_pages, missing_ids
    )
    census = census_off_banzuke_results(
        history,
        start=args.start,
        end=args.end,
        career_statuses=statuses,
        page_source=page_source,
        missing_page_ids=missing_pages,
    )
    elapsed = perf_counter() - started
    output = write_outputs(
        census,
        history_source=_identity(history_path),
        equelo_exclusions=args.equelo_exclusions,
        output_root=args.output_root,
        elapsed_seconds=elapsed,
    )
    post = sum(row.post_1988 for row in census.bouts)
    mz = sum(
        status == "Mz"
        for row in census.bouts
        for status in row.missing_statuses.split(";")
    )
    endpoints = sum(row.missing_endpoint_count for row in census.bouts)
    print(f"Off-banzuke bouts: {len(census.bouts):,}")
    print(f"Missing endpoints classified Mz: {mz:,} / {endpoints:,}")
    print(f"Post-1988 off-banzuke bouts: {post:,}")
    print(f"RikId 13011 in 2026-07: {census.sawada_2026_07_result_count} bouts; banzuke={census.sawada_2026_07_chii or 'absent'}")
    print(f"Output: {output.resolve()}")
    print(f"Total wall-clock time: {perf_counter() - started:.3f} seconds")
    return 0
