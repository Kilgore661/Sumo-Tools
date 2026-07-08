from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_interdivision_matchups")
DEFAULT_START = "1989/01"

DIVISION_ORDER = (
    Division.MAKUUCHI,
    Division.JURYO,
    Division.MAKUSHITA,
    Division.SANDANME,
    Division.JONIDAN,
    Division.JONOKUCHI,
)

DIVISION_LABELS = {
    Division.MAKUUCHI: "makuuchi",
    Division.JURYO: "juryo",
    Division.MAKUSHITA: "makushita",
    Division.SANDANME: "sandanme",
    Division.JONIDAN: "jonidan",
    Division.JONOKUCHI: "jonokuchi",
}


@dataclass(frozen=True)
class Boundary:
    upper: Division
    lower: Division

    @property
    def key(self) -> str:
        return f"{DIVISION_LABELS[self.upper]}_{DIVISION_LABELS[self.lower]}"


@dataclass
class BoundaryRow:
    date: str
    upper_division: str
    lower_division: str
    inter_division_matches: int
    upper_division_size: int
    lower_division_size: int
    inter_division_match_pct_of_anticipated_bouts: float
    upper_rikishi_in_inter_division_matches: int
    lower_rikishi_in_inter_division_matches: int


def parse_date(value: str) -> Date:
    year_text, month_text = value.replace("-", "/").split("/")
    return Date(Year(int(year_text)), Month(int(month_text)))


def date_token(date: Date) -> str:
    return f"{int(date.year):04d}_{int(date.month):02d}"


def load_history(history_zip: Path | None) -> History:
    if history_zip is None:
        return get_history()
    zipless = history_zip.with_suffix("") if history_zip.suffix == ".zip" else history_zip
    return load_history_with_annotations(str(zipless))


def division_for_chii(chii: Chii) -> Division:
    if isinstance(chii.level, MSD):
        return Division.MAKUUCHI
    if isinstance(chii.level, Division):
        return chii.level
    raise TypeError(f"Unexpected chii level {chii.level!r}")


def adjacent_boundaries() -> tuple[Boundary, ...]:
    return tuple(
        Boundary(upper=DIVISION_ORDER[index], lower=DIVISION_ORDER[index + 1])
        for index in range(len(DIVISION_ORDER) - 1)
    )


def boundary_for_pair(div_a: Division, div_b: Division) -> Boundary | None:
    if div_a == div_b:
        return None
    ordered = {div_a, div_b}
    for boundary in adjacent_boundaries():
        if ordered == {boundary.upper, boundary.lower}:
            return boundary
    return None


def compute_boundary_rows(
    history: History,
    *,
    start: Date,
    end: Date | None,
) -> dict[Boundary, list[BoundaryRow]]:
    rows_by_boundary: dict[Boundary, list[BoundaryRow]] = {
        boundary: [] for boundary in adjacent_boundaries()
    }

    for date in sorted(history):
        if date < start:
            continue
        if end is not None and date > end:
            continue

        basho = history[date]
        division_by_rikishi = {
            rikishi: division_for_chii(chii)
            for rikishi, chii in basho.banzuke.rikchii.items()
        }
        sizes = defaultdict(int)
        for division in division_by_rikishi.values():
            sizes[division] += 1

        match_counts = defaultdict(int)
        upper_bridge_rikishi: dict[Boundary, set] = defaultdict(set)
        lower_bridge_rikishi: dict[Boundary, set] = defaultdict(set)

        for daily in basho.summary.values():
            for pair in daily.torikumi:
                rikishi_a, rikishi_b = pair
                div_a = division_by_rikishi.get(rikishi_a)
                div_b = division_by_rikishi.get(rikishi_b)
                if div_a is None or div_b is None:
                    continue

                boundary = boundary_for_pair(div_a, div_b)
                if boundary is None:
                    continue

                match_counts[boundary] += 1
                if div_a == boundary.upper:
                    upper_bridge_rikishi[boundary].add(rikishi_a)
                    lower_bridge_rikishi[boundary].add(rikishi_b)
                else:
                    upper_bridge_rikishi[boundary].add(rikishi_b)
                    lower_bridge_rikishi[boundary].add(rikishi_a)

        for boundary in adjacent_boundaries():
            anticipated_bouts = (
                (15 * sizes[boundary.upper]) + (15 * sizes[boundary.lower])
            ) / 2
            inter_division_pct = (
                100 * match_counts[boundary] / anticipated_bouts
                if anticipated_bouts
                else 0.0
            )
            rows_by_boundary[boundary].append(
                BoundaryRow(
                    date=str(date),
                    upper_division=DIVISION_LABELS[boundary.upper],
                    lower_division=DIVISION_LABELS[boundary.lower],
                    inter_division_matches=match_counts[boundary],
                    upper_division_size=sizes[boundary.upper],
                    lower_division_size=sizes[boundary.lower],
                    inter_division_match_pct_of_anticipated_bouts=inter_division_pct,
                    upper_rikishi_in_inter_division_matches=len(
                        upper_bridge_rikishi[boundary]
                    ),
                    lower_rikishi_in_inter_division_matches=len(
                        lower_bridge_rikishi[boundary]
                    ),
                )
            )

    return rows_by_boundary


def write_boundary_csv(path: Path, rows: list[BoundaryRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "date",
        "upper_division",
        "lower_division",
        "inter_division_matches",
        "upper_division_size",
        "lower_division_size",
        "inter_division_match_pct_of_anticipated_bouts",
        "upper_rikishi_in_inter_division_matches",
        "lower_rikishi_in_inter_division_matches",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "date": row.date,
                    "upper_division": row.upper_division,
                    "lower_division": row.lower_division,
                    "inter_division_matches": row.inter_division_matches,
                    "upper_division_size": row.upper_division_size,
                    "lower_division_size": row.lower_division_size,
                    "inter_division_match_pct_of_anticipated_bouts": (
                        f"{row.inter_division_match_pct_of_anticipated_bouts:.6f}"
                    ),
                    "upper_rikishi_in_inter_division_matches": (
                        row.upper_rikishi_in_inter_division_matches
                    ),
                    "lower_rikishi_in_inter_division_matches": (
                        row.lower_rikishi_in_inter_division_matches
                    ),
                }
            )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Write one CSV per adjacent division boundary showing how often "
            "scheduled torikumi crosses that boundary."
        )
    )
    parser.add_argument("--start", default=DEFAULT_START, help="Start basho YYYY/MM.")
    parser.add_argument("--end", default=None, help="Optional end basho YYYY/MM.")
    parser.add_argument(
        "--history-zip",
        type=Path,
        default=None,
        help="Optional zip-backed History path. Defaults to the live store.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    start = parse_date(args.start)
    end = parse_date(args.end) if args.end else None
    history = load_history(args.history_zip)

    rows_by_boundary = compute_boundary_rows(history, start=start, end=end)
    end_for_token = end if end is not None else max(history)
    period = f"{date_token(start)}-{date_token(end_for_token)}"

    for boundary, rows in rows_by_boundary.items():
        output_path = args.output_root / f"{period}_{boundary.key}.csv"
        write_boundary_csv(output_path, rows)
        print(f"Wrote {output_path}")
        percentages = [
            row.inter_division_match_pct_of_anticipated_bouts for row in rows
        ]
        mean_pct = statistics.mean(percentages) if percentages else 0.0
        stdev_pct = statistics.stdev(percentages) if len(percentages) > 1 else 0.0
        print(
            f"  {boundary.key}: mean={mean_pct:.6f}%, "
            f"stdev={stdev_pct:.6f} percentage points"
        )


if __name__ == "__main__":
    main()
