import argparse
import csv
import datetime
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean, median

try:
    from src.infra.config import EPOCH
    from src.infra.connect import connect
    from src.sumo_core.BasicEnums import Division, MSD, Outcome
    from src.sumo_core.Chii import Chii
    from src.sumo_core.History import History
    from src.misc.finish_by_chii_charting import (
        write_average_finish_chart,
        write_finish_chart,
    )
    from src.misc.finish_by_chii_deploy import (
        LOCAL_AVERAGE_HTML,
        LOCAL_HTML,
        main as upload_chart,
    )
except ImportError:  # pragma: no cover - fallback for package-style execution
    from ..infra.config import EPOCH
    from ..infra.connect import connect
    from ..sumo_core.BasicEnums import Division, MSD, Outcome
    from ..sumo_core.Chii import Chii
    from ..sumo_core.History import History
    from .finish_by_chii_charting import write_average_finish_chart, write_finish_chart
    from .finish_by_chii_deploy import LOCAL_AVERAGE_HTML, LOCAL_HTML, main as upload_chart


OUTPUT_PREFIX = "finish_by_chii"

DEFAULT_DIVISIONS = (Division.MAKUUCHI, Division.JURYO)
MAKUUCHI_LEVELS = {
    MSD.YOKOZUNA,
    MSD.OZEKI,
    MSD.SEKIWAKE,
    MSD.KOMUSUBI,
    MSD.MAEGASHIRA,
}


@dataclass(frozen=True)
class FinishRow:
    date: str
    division: Division
    rikishi: int
    chii: Chii
    wins: int
    top_pos: int
    bottom_pos: int
    position_pct: float


def _build_parser() -> argparse.ArgumentParser:
    default_start, default_end = _default_history_range()
    parser = argparse.ArgumentParser(
        description=(
            "Compute empirical finishing-position distributions by starting Chii "
            "for sekitori divisions."
        )
    )
    parser.add_argument("--start", type=int, default=default_start)
    parser.add_argument("--end", type=int, default=default_end)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--divisions",
        default="makuuchi,juryo",
        help="Comma-separated divisions to include. Supported: makuuchi,juryo.",
    )
    parser.add_argument(
        "--threshold-max",
        type=int,
        default=10,
        help="Largest top/bottom ordinal threshold to emit.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=None,
        help="Optional summary CSV output path.",
    )
    parser.add_argument(
        "--top-output",
        type=Path,
        default=None,
        help="Optional top-threshold CSV output path.",
    )
    parser.add_argument(
        "--bottom-output",
        type=Path,
        default=None,
        help="Optional bottom-threshold CSV output path.",
    )
    parser.add_argument(
        "--html-output",
        type=Path,
        default=None,
        help="Optional Plotly HTML output path. Defaults to the local web root.",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Write the local HTML page but do not upload it to the remote server.",
    )
    parser.add_argument(
        "--average-html-output",
        type=Path,
        default=None,
        help="Optional average-finish HTML output path. Defaults to the local web root.",
    )
    return parser


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_output_path(start: int, end: int, suffix: str) -> Path:
    filename = f"{OUTPUT_PREFIX}_{start}_{end}_{suffix}.csv"
    return _repo_root() / "files" / "output" / "misc" / filename


def _default_html_output_path(start: int, end: int) -> Path:
    return LOCAL_HTML


def _default_average_html_output_path(start: int, end: int) -> Path:
    return LOCAL_AVERAGE_HTML


def _default_history_range() -> tuple[int, int]:
    history_dir = _repo_root() / "files" / "output" / "Historys"
    pattern = re.compile(r"^(\d{4})_01 to (\d{4})_11\.zip$")
    ranges = []

    if history_dir.exists():
        for path in history_dir.iterdir():
            match = pattern.match(path.name)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                ranges.append((start, end))

    if not ranges:
        return EPOCH, datetime.datetime.now().year

    return max(ranges, key=lambda item: (item[1] - item[0], item[1]))


def _division_label(division: Division) -> str:
    labels = {
        Division.MAKUUCHI: "Makuuchi",
        Division.JURYO: "Juryo",
    }
    return labels[division]


def _parse_divisions(value: str) -> tuple[Division, ...]:
    lookup = {
        "makuuchi": Division.MAKUUCHI,
        "juryo": Division.JURYO,
    }
    divisions = []
    for part in value.split(","):
        key = part.strip().lower()
        if not key:
            continue
        if key not in lookup:
            raise ValueError(
                f"Unsupported division {part!r}; supported values are makuuchi,juryo"
            )
        divisions.append(lookup[key])

    if not divisions:
        raise ValueError("At least one division must be selected")
    return tuple(dict.fromkeys(divisions))


def _division_of_chii(chii: Chii) -> Division:
    if chii.level in MAKUUCHI_LEVELS:
        return Division.MAKUUCHI
    if isinstance(chii.level, Division):
        return chii.level
    raise TypeError(f"Cannot map Chii level {chii.level!r} to a division")


def _wins_by_rikishi(basho) -> dict[int, int]:
    wins: dict[int, int] = defaultdict(int)
    win_outcomes = {Outcome.W, Outcome.FS}

    for daily_results in basho.summary.values():
        for bout in daily_results.results_lookup.values():
            if bout.outcome1 in win_outcomes:
                wins[int(bout.rikishi1)] += 1
            if bout.outcome2 in win_outcomes:
                wins[int(bout.rikishi2)] += 1

    return wins


def _division_members(basho, divisions: tuple[Division, ...]) -> dict[Division, list[int]]:
    selected = set(divisions)
    out: dict[Division, list[int]] = {division: [] for division in divisions}

    for rid in basho.banzuke.riks:
        chii = basho.banzuke.rikchii[rid]
        division = _division_of_chii(chii)
        if division in selected:
            out[division].append(int(rid))

    return out


def collect_finish_rows(
    history: History,
    divisions: tuple[Division, ...] = DEFAULT_DIVISIONS,
) -> list[FinishRow]:
    rows: list[FinishRow] = []

    for date, basho in sorted(history.items()):
        wins = _wins_by_rikishi(basho)
        members_by_division = _division_members(basho, divisions)

        for division, members in members_by_division.items():
            if not members:
                continue

            win_values = [wins.get(rid, 0) for rid in members]
            top_positions = {
                rid: 1 + sum(other_wins > wins.get(rid, 0) for other_wins in win_values)
                for rid in members
            }
            bottom_positions = {
                rid: 1 + sum(other_wins < wins.get(rid, 0) for other_wins in win_values)
                for rid in members
            }
            max_top_position = max(top_positions.values())
            denom = max_top_position - 1

            for rid in members:
                chii = basho.banzuke.rikchii[rid]
                top_pos = top_positions[rid]
                position_pct = 0.0 if denom == 0 else (top_pos - 1) / denom
                rows.append(
                    FinishRow(
                        date=str(date),
                        division=division,
                        rikishi=rid,
                        chii=chii,
                        wins=wins.get(rid, 0),
                        top_pos=top_pos,
                        bottom_pos=bottom_positions[rid],
                        position_pct=position_pct,
                    )
                )

    return rows


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("Cannot compute a quantile over an empty list")
    if len(values) == 1:
        return values[0]

    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def _group_by_chii(rows: list[FinishRow]) -> dict[Chii, list[FinishRow]]:
    grouped: dict[Chii, list[FinishRow]] = defaultdict(list)
    for row in rows:
        grouped[row.chii].append(row)
    return grouped


def build_summary_rows(rows: list[FinishRow]) -> list[dict[str, object]]:
    out = []
    for chii, group in sorted(_group_by_chii(rows).items()):
        n = len(group)
        top_positions = [row.top_pos for row in group]
        bottom_positions = [row.bottom_pos for row in group]
        position_pcts = [row.position_pct for row in group]

        out.append(
            {
                "division": _division_label(group[0].division),
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "n": n,
                "mean_top_pos": fmean(top_positions),
                "median_top_pos": median(top_positions),
                "mean_bottom_pos": fmean(bottom_positions),
                "median_bottom_pos": median(bottom_positions),
                "mean_position_pct": fmean(position_pcts),
                "p10_position_pct": _quantile(position_pcts, 0.10),
                "p25_position_pct": _quantile(position_pcts, 0.25),
                "median_position_pct": median(position_pcts),
                "p75_position_pct": _quantile(position_pcts, 0.75),
                "p90_position_pct": _quantile(position_pcts, 0.90),
                "p_top_1": sum(row.top_pos == 1 for row in group) / n,
                "p_bottom_1": sum(row.bottom_pos == 1 for row in group) / n,
            }
        )
    return out


def build_threshold_rows(
    rows: list[FinishRow],
    threshold_max: int,
    from_bottom: bool,
) -> list[dict[str, object]]:
    out = []
    pos_attr = "bottom_pos" if from_bottom else "top_pos"
    probability_name = (
        "p_no_better_than_mth_worst" if from_bottom else "p_no_worse_than_n"
    )

    for chii, group in sorted(_group_by_chii(rows).items()):
        n = len(group)
        for threshold in range(1, threshold_max + 1):
            hits = sum(getattr(row, pos_attr) <= threshold for row in group)
            out.append(
                {
                    "division": _division_label(group[0].division),
                    "chii": str(chii),
                    "chii_ordinal": chii.ordinal(),
                    "threshold": threshold,
                    "n": n,
                    "hits": hits,
                    probability_name: hits / n,
                }
            )
    return out


def write_csv(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {output_path}")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.threshold_max <= 0:
        raise ValueError("--threshold-max must be positive")

    divisions = _parse_divisions(args.divisions)
    history = connect(args.start, args.end, use_zip=args.zip)
    if not history:
        raise ValueError("No history returned by connect()")

    finish_rows = collect_finish_rows(history, divisions=divisions)
    if not finish_rows:
        raise ValueError("No finish rows generated")

    summary_rows = build_summary_rows(finish_rows)
    top_rows = build_threshold_rows(
        finish_rows,
        threshold_max=args.threshold_max,
        from_bottom=False,
    )
    bottom_rows = build_threshold_rows(
        finish_rows,
        threshold_max=args.threshold_max,
        from_bottom=True,
    )

    summary_path = args.summary_output or _default_output_path(
        args.start,
        args.end,
        "summary",
    )
    top_path = args.top_output or _default_output_path(
        args.start,
        args.end,
        "top_thresholds",
    )
    bottom_path = args.bottom_output or _default_output_path(
        args.start,
        args.end,
        "bottom_thresholds",
    )
    html_path = args.html_output or _default_html_output_path(args.start, args.end)
    average_html_path = args.average_html_output or _default_average_html_output_path(
        args.start,
        args.end,
    )

    print(f"Finish rows: {len(finish_rows)}")
    print(f"Summary rows: {len(summary_rows)}")
    print(f"Top threshold rows: {len(top_rows)}")
    print(f"Bottom threshold rows: {len(bottom_rows)}")
    print(f"Summary CSV: {write_csv(summary_rows, summary_path)}")
    print(f"Top thresholds CSV: {write_csv(top_rows, top_path)}")
    print(f"Bottom thresholds CSV: {write_csv(bottom_rows, bottom_path)}")
    print(
        "Chart HTML: "
        f"{write_finish_chart(top_rows, bottom_rows, html_path, args.start, args.end)}"
    )
    print(
        "Average chart HTML: "
        f"{write_average_finish_chart(summary_rows, average_html_path, args.start, args.end)}"
    )

    if not args.no_upload:
        upload_chart()


if __name__ == "__main__":
    main()
