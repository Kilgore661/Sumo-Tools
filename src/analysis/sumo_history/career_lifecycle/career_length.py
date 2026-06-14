from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.sumo_history.constants import TOP_N_LIMIT
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


OUTPUT_ROOT = Path("files/output/career_length")
SITE_BUNDLE_DIR = "site/career_length"
TAMAWASHI_RIKISHI_ID = 5944
FIRST_BASHO_PARTIAL_NOTE = (
    "Rikishi first observed in the first available basho are marked partial_start "
    "because their true start may predate the canonical history."
)
ACTIVE_NOTE = (
    "Active rikishi are marked active when their last observed banzuke is the "
    "latest basho in the supplied history. Their length is a lower bound."
)
LENGTH_POLICY = (
    "participation_years is the elapsed calendar time between first and last "
    "observed banzuke dates, divided by 365.2425. Gaps are ignored for endpoint "
    "calculation but emitted as warnings."
)
OBSERVED_CAREER_LENGTH_NOTE = (
    '<strong>Years.</strong> This is the observed Career Length; i.e. the difference in years '
    "between the first and last basho dates in which the rikishi appeared on "
    'the banzuke according to <a href="https://sumodb.sumogames.de/">SumoDB</a>. '
    "It follows that an observed career length <em>does</em> include periods "
    "where a rikishi was at least notionally involved in Grand Sumo, but not "
    'active, e.g. <a href="https://sumodb.sumogames.de/Rikishi.aspx?r=4980">'
    "Sokokurai</a>. The apparent hatsu/intai dates may not correspond "
    "precisely to the hatsu/intai dates at SumoDB."
)


@dataclass(frozen=True)
class CareerSpan:
    rikishi_id: int
    shikona: str
    graph_shikona: str
    first_appearance: str
    last_appearance: str
    first_index: int
    last_index: int
    appearance_count_basho: int
    span_basho_count: int
    participation_years: float
    nearest_years: int
    active: bool
    partial_start: bool
    gap_count: int
    gap_basho_count: int


@dataclass(frozen=True)
class GapWarning:
    rikishi_id: int
    shikona: str
    last_seen_before_gap: str
    first_missing: str
    reappears: str
    missing_basho_count: int

    def message(self) -> str:
        return (
            f"{self.shikona} ({self.rikishi_id}) appears in "
            f"{self.last_seen_before_gap}, disappears in {self.first_missing}, "
            f"then reappears in {self.reappears} "
            f"({self.missing_basho_count} missing basho)."
        )


@dataclass(frozen=True)
class CareerLengthOutputs:
    output_root: Path
    bundle_dir: Path
    rikishi_csv: Path
    log_path: Path
    page_json: Path
    distribution_csv: Path
    pmf_csv: Path
    cdf_csv: Path
    survival_csv: Path
    longest_csv: Path
    shortest_csv: Path
    metadata_json: Path


def compute_career_spans(history: History) -> tuple[list[CareerSpan], list[GapWarning]]:
    dates = sorted(history.keys())
    if not dates:
        return [], []

    first_history_date = dates[0]
    latest_history_date = dates[-1]
    date_index = {date: index for index, date in enumerate(dates)}
    date_by_index = {index: date for date, index in date_index.items()}

    appearances: dict[RikId, list[Date]] = {}
    full_shikona_store = FullShikonaStore.from_sources(history)

    for date in dates:
        banzuke = history(date).banzuke
        for rikishi_id in banzuke.riks:
            appearances.setdefault(rikishi_id, []).append(date)

    spans: list[CareerSpan] = []
    warnings: list[GapWarning] = []

    for rikishi_id in sorted(appearances, key=int):
        seen_dates = appearances[rikishi_id]
        first_date = seen_dates[0]
        last_date = seen_dates[-1]
        indices = [date_index[date] for date in seen_dates]
        first_index = indices[0]
        last_index = indices[-1]
        missing_segments = _missing_segments(indices)
        gap_basho_count = sum(len(segment) for segment in missing_segments)
        shikona = full_shikona_store.full_shikona(rikishi_id)
        graph_shikona = _graph_shikona_for(rikishi_id, shikona)

        for segment in missing_segments:
            warnings.append(
                GapWarning(
                    rikishi_id=int(rikishi_id),
                    shikona=shikona,
                    last_seen_before_gap=str(date_by_index[segment[0] - 1]),
                    first_missing=str(date_by_index[segment[0]]),
                    reappears=str(date_by_index[segment[-1] + 1]),
                    missing_basho_count=len(segment),
                )
            )

        span_basho_count = last_index - first_index + 1
        participation_years = _elapsed_years(first_date, last_date)
        spans.append(
            CareerSpan(
                rikishi_id=int(rikishi_id),
                shikona=shikona,
                graph_shikona=graph_shikona,
                first_appearance=str(first_date),
                last_appearance=str(last_date),
                first_index=first_index,
                last_index=last_index,
                appearance_count_basho=len(seen_dates),
                span_basho_count=span_basho_count,
                participation_years=round(participation_years, 6),
                nearest_years=int(round(participation_years)),
                active=last_date == latest_history_date,
                partial_start=first_date == first_history_date,
                gap_count=len(missing_segments),
                gap_basho_count=gap_basho_count,
            )
        )

    return spans, warnings


def build_career_length_outputs(
    history: History,
    output_root: Path = OUTPUT_ROOT,
    print_summary: bool = True,
) -> CareerLengthOutputs:
    spans, warnings = compute_career_spans(history)
    range_token = _history_range_token(history)
    output_root.mkdir(parents=True, exist_ok=True)
    bundle_dir = output_root / "site" / f"career_length_{range_token}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    outputs = CareerLengthOutputs(
        output_root=output_root,
        bundle_dir=bundle_dir,
        rikishi_csv=output_root / f"career_length_{range_token}_rikishi.csv",
        log_path=output_root / f"career_length_{range_token}.log",
        page_json=bundle_dir / "page.json",
        distribution_csv=bundle_dir / "distribution.csv",
        pmf_csv=bundle_dir / "pmf.csv",
        cdf_csv=bundle_dir / "cdf.csv",
        survival_csv=bundle_dir / "survival.csv",
        longest_csv=bundle_dir / "longest.csv",
        shortest_csv=bundle_dir / "shortest.csv",
        metadata_json=bundle_dir / "metadata.json",
    )

    _write_dataclass_csv(spans, outputs.rikishi_csv)
    _write_distribution(spans, outputs.distribution_csv)
    _write_pmf(spans, outputs.pmf_csv)
    _write_cdf(spans, outputs.cdf_csv)
    _write_survival(spans, outputs.survival_csv)
    _write_dataclass_csv(_longest(spans), outputs.longest_csv)
    _write_dataclass_csv(_shortest(spans), outputs.shortest_csv)
    _write_page_json(outputs.page_json, spans)
    _write_metadata(
        history=history,
        spans=spans,
        warnings=warnings,
        output_path=outputs.metadata_json,
    )
    log_text = _make_log(history, spans, warnings, include_gap_details=True)
    outputs.log_path.write_text(log_text, encoding="utf-8")
    if print_summary:
        print(_make_log(history, spans, warnings, include_gap_details=False), end="")
    return outputs


def load_history_from_zip(path: Path) -> History:
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def _history_range_token(history: History) -> str:
    dates = sorted(history.keys())
    if not dates:
        return "empty"
    return f"{_date_token(dates[0])}_to_{_date_token(dates[-1])}"


def _date_token(date: Date) -> str:
    return f"{int(date.year):04d}_{int(date.month):02d}"


def _graph_shikona_for(rikishi_id: RikId, fallback: str) -> str:
    try:
        from src.analysis.banzuke_compare.shikona_links import graph_shikona_for
    except (FileNotFoundError, ImportError):
        return fallback
    return graph_shikona_for(rikishi_id, fallback)


def _elapsed_years(first_date: Date, last_date: Date) -> float:
    start = _date_to_calendar_date(first_date)
    end = _date_to_calendar_date(last_date)
    return (end - start).days / 365.2425


def _date_to_calendar_date(date: Date) -> datetime.date:
    return datetime.date(int(date.year), int(date.month), 1)


def _missing_segments(indices: list[int]) -> list[list[int]]:
    segments: list[list[int]] = []
    for previous, current in zip(indices, indices[1:]):
        if current == previous + 1:
            continue
        segments.append(list(range(previous + 1, current)))
    return segments


def _write_dataclass_csv(rows: Iterable[object], output_path: Path) -> None:
    rows = tuple(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tuple(rows[0].__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _bucket_counts(spans: list[CareerSpan]) -> list[dict[str, int]]:
    if not spans:
        return []
    max_bucket = max(span.nearest_years for span in spans)
    rows = []
    for bucket in range(max_bucket + 1):
        retired_count = sum(
            1 for span in spans if span.nearest_years == bucket and not span.active
        )
        active_count = sum(
            1 for span in spans if span.nearest_years == bucket and span.active
        )
        rows.append(
            {
                "nearest_years": bucket,
                "retired_count": retired_count,
                "active_count": active_count,
                "total_count": retired_count + active_count,
            }
        )
    return rows


def _write_distribution(spans: list[CareerSpan], output_path: Path) -> None:
    _write_dict_csv(
        _bucket_counts(spans),
        output_path,
        ("nearest_years", "retired_count", "active_count", "total_count"),
    )


def _write_pmf(spans: list[CareerSpan], output_path: Path) -> None:
    total = len(spans)
    rows = []
    for row in _bucket_counts(spans):
        total_count = row["total_count"]
        rows.append(
            {
                **row,
                "probability": _safe_probability(total_count, total),
                "retired_probability": _safe_probability(row["retired_count"], total),
                "active_probability": _safe_probability(row["active_count"], total),
            }
        )
    _write_dict_csv(
        rows,
        output_path,
        (
            "nearest_years",
            "retired_count",
            "active_count",
            "total_count",
            "probability",
            "retired_probability",
            "active_probability",
        ),
    )


def _write_cdf(spans: list[CareerSpan], output_path: Path) -> None:
    total = len(spans)
    cumulative_retired = 0
    cumulative_active = 0
    rows = []
    for row in _bucket_counts(spans):
        cumulative_retired += row["retired_count"]
        cumulative_active += row["active_count"]
        cumulative_total = cumulative_retired + cumulative_active
        rows.append(
            {
                "nearest_years": row["nearest_years"],
                "cumulative_retired_count": cumulative_retired,
                "cumulative_active_count": cumulative_active,
                "cumulative_total_count": cumulative_total,
                "cumulative_probability": _safe_probability(cumulative_total, total),
            }
        )
    _write_dict_csv(
        rows,
        output_path,
        (
            "nearest_years",
            "cumulative_retired_count",
            "cumulative_active_count",
            "cumulative_total_count",
            "cumulative_probability",
        ),
    )


def _write_survival(spans: list[CareerSpan], output_path: Path) -> None:
    total = len(spans)
    rows = []
    for row in _bucket_counts(spans):
        bucket = row["nearest_years"]
        retired_at_least = sum(
            1 for span in spans if span.nearest_years >= bucket and not span.active
        )
        active_at_least = sum(
            1 for span in spans if span.nearest_years >= bucket and span.active
        )
        total_at_least = retired_at_least + active_at_least
        rows.append(
            {
                "nearest_years": bucket,
                "retired_at_least_count": retired_at_least,
                "active_at_least_count": active_at_least,
                "total_at_least_count": total_at_least,
                "survival_probability": _safe_probability(total_at_least, total),
            }
        )
    _write_dict_csv(
        rows,
        output_path,
        (
            "nearest_years",
            "retired_at_least_count",
            "active_at_least_count",
            "total_at_least_count",
            "survival_probability",
        ),
    )


def _write_dict_csv(
    rows: list[dict],
    output_path: Path,
    fieldnames: tuple[str, ...],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _safe_probability(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 8)


def _longest(spans: list[CareerSpan], limit: int = TOP_N_LIMIT) -> list[CareerSpan]:
    return sorted(
        spans,
        key=lambda span: (
            -span.participation_years,
            span.first_index,
            span.rikishi_id,
        ),
    )[:limit]


def _shortest(spans: list[CareerSpan], limit: int = 50) -> list[CareerSpan]:
    return sorted(
        spans,
        key=lambda span: (
            span.participation_years,
            span.first_index,
            span.rikishi_id,
        ),
    )[:limit]


def _write_page_json(output_path: Path, spans: list[CareerSpan]) -> None:
    notes = [
        {
            "id": "observed_career_length",
            "placement": "below_chart",
            "format": "html",
            "note_for": "all",
            "notes": OBSERVED_CAREER_LENGTH_NOTE,
        },
    ]
    tamawashi_note = _tamawashi_note(spans)
    if tamawashi_note is not None:
        notes.append(tamawashi_note)
    notes.append(
        {
            "id": "bg_count",
            "placement": "below_chart",
            "format": "html",
            "note_for": "longest",
            "notes": (
                "<strong>Bg.</strong> The number of basho for which the "
                "rikishi was absent."
            ),
        }
    )
    notes.extend(
        [
            {
                "id": "partial_starts",
                "placement": "metadata",
                "format": "text",
                "notes": FIRST_BASHO_PARTIAL_NOTE,
            },
            {
                "id": "active_lower_bounds",
                "placement": "metadata",
                "format": "text",
                "notes": ACTIVE_NOTE,
            },
            {
                "id": "length_policy",
                "placement": "metadata",
                "format": "text",
                "notes": LENGTH_POLICY,
            },
        ]
    )
    payload = {
        "id": "career_length",
        "title": "Career Length",
        "layout": "chart_with_options",
        "default_view": "distribution",
        "controls": [
            {
                "id": "view",
                "label": "View",
                "kind": "enum",
                "default": "distribution",
                "values": [
                    {"value": "distribution", "label": "Distribution"},
                    {"value": "pmf", "label": "PMF"},
                    {"value": "cdf", "label": "CDF"},
                    {"value": "survival", "label": "Survival"},
                    {"value": "longest", "label": "Longest"},
                ],
            }
        ],
        "data_sources": [
            {
                "id": "distribution",
                "label": "Distribution",
                "data": "distribution.csv",
                "kind": "stacked_bar",
            },
            {"id": "pmf", "label": "PMF", "data": "pmf.csv", "kind": "line"},
            {"id": "cdf", "label": "CDF", "data": "cdf.csv", "kind": "line"},
            {
                "id": "survival",
                "label": "Survival",
                "data": "survival.csv",
                "kind": "line",
            },
            {"id": "longest", "label": "Longest", "data": "longest.csv", "kind": "table"},
        ],
        "chart": {
            "x": "nearest_years",
            "x_label": "Nearest integer years",
            "y_label": "Rikishi count",
            "stack_fields": ["retired_count", "active_count"],
        },
        "notes": notes,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _tamawashi_note(spans: list[CareerSpan]) -> dict[str, str] | None:
    tamawashi = next(
        (span for span in spans if span.rikishi_id == TAMAWASHI_RIKISHI_ID),
        None,
    )
    if tamawashi is None:
        return None
    rank = _career_length_rank(spans, tamawashi)
    years, months = _whole_years_months(
        first_appearance=tamawashi.first_appearance,
        last_appearance=tamawashi.last_appearance,
    )
    duration = f"{years} years"
    if months:
        duration += f" and {months} months"
    return {
        "id": "tamawashi_context",
        "placement": "below_chart",
        "format": "html",
        "note_for": "longest",
        "notes": (
            '<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=5944">'
            f"Tamawashi</a>, at {duration}, is currently "
            f"{rank}{_ordinal_suffix(rank)}."
        ),
    }


def _career_length_rank(spans: list[CareerSpan], target: CareerSpan) -> int:
    ranked = sorted(
        spans,
        key=lambda span: (
            -span.participation_years,
            span.first_index,
            span.rikishi_id,
        ),
    )
    for index, span in enumerate(ranked, start=1):
        if span.rikishi_id == target.rikishi_id:
            return index
    raise ValueError(f"Target rikishi not found: {target.rikishi_id}")


def _whole_years_months(
    *,
    first_appearance: str,
    last_appearance: str,
) -> tuple[int, int]:
    first_year, first_month = (int(part) for part in first_appearance.split("/"))
    last_year, last_month = (int(part) for part in last_appearance.split("/"))
    total_months = (last_year - first_year) * 12 + (last_month - first_month)
    return divmod(total_months, 12)


def _ordinal_suffix(value: int) -> str:
    if 10 <= value % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")


def _write_metadata(
    *,
    history: History,
    spans: list[CareerSpan],
    warnings: list[GapWarning],
    output_path: Path,
) -> None:
    dates = sorted(history.keys())
    payload = {
        "history_basho_count": len(dates),
        "first_history_basho": str(dates[0]) if dates else None,
        "latest_history_basho": str(dates[-1]) if dates else None,
        "rikishi_count": len(spans),
        "active_count": sum(1 for span in spans if span.active),
        "retired_count": sum(1 for span in spans if not span.active),
        "partial_start_count": sum(1 for span in spans if span.partial_start),
        "gap_warning_count": len(warnings),
        "length_policy": LENGTH_POLICY,
        "partial_start_note": FIRST_BASHO_PARTIAL_NOTE,
        "active_note": ACTIVE_NOTE,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _make_log(
    history: History,
    spans: list[CareerSpan],
    warnings: list[GapWarning],
    *,
    include_gap_details: bool,
) -> str:
    dates = sorted(history.keys())
    rikishi_with_gaps = len({warning.rikishi_id for warning in warnings})
    lines = [
        "Career Length",
        "=============",
        "",
        f"History basho: {len(dates)}",
        f"First history basho: {dates[0] if dates else 'n/a'}",
        f"Latest history basho: {dates[-1] if dates else 'n/a'}",
        f"Rikishi: {len(spans)}",
        f"Active: {sum(1 for span in spans if span.active)}",
        f"Retired/absent from latest banzuke: {sum(1 for span in spans if not span.active)}",
        f"Partial starts: {sum(1 for span in spans if span.partial_start)}",
        f"Rikishi with gaps: {rikishi_with_gaps}",
        f"Gap segments: {len(warnings)}",
        "",
        LENGTH_POLICY,
        FIRST_BASHO_PARTIAL_NOTE,
        ACTIVE_NOTE,
        "",
        "Stats",
        "-----",
    ]
    groups = {
        "all observed": spans,
        "completed only": [span for span in spans if not span.active],
        "non-partial completed only": [
            span for span in spans if not span.active and not span.partial_start
        ],
        "active only": [span for span in spans if span.active],
    }
    for label, rows in groups.items():
        lines.extend(_stats_lines(label, [span.participation_years for span in rows]))
    if include_gap_details:
        lines.extend(["", "Gap Warnings", "------------"])
        if warnings:
            lines.extend(warning.message() for warning in warnings)
        else:
            lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def _stats_lines(label: str, values: list[float]) -> list[str]:
    if not values:
        return [f"{label}: n=0"]
    mean = statistics.fmean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    ci95_half_width = 1.96 * stdev / math.sqrt(len(values)) if values else 0.0
    return [
        f"{label}:",
        f"  n={len(values)}",
        f"  min={min(values):.3f}",
        f"  max={max(values):.3f}",
        f"  mean={mean:.3f}",
        f"  median={statistics.median(values):.3f}",
        f"  stdev={stdev:.3f}",
        f"  ci95=[{mean - ci95_half_width:.3f}, {mean + ci95_half_width:.3f}]",
    ]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build career-length public-site bundle and debug outputs."
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help=(
            "Load History from a zip path instead of the live store. The .zip suffix "
            "is optional."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Output directory for career-length artefacts.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else get_history()
    outputs = build_career_length_outputs(history, args.output_root)
    print("Wrote:")
    print(f"  Bundle: {outputs.bundle_dir}")
    print(f"  Rikishi CSV: {outputs.rikishi_csv}")
    print(f"  Log: {outputs.log_path}")


if __name__ == "__main__":
    main()
