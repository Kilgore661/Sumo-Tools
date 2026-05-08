from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


OUTPUT_ROOT = Path("files/output/rank_at_retirement")
RANK_GROUPS = ("Y", "O", "S", "K", "M", "J", "Ms", "Sd", "Jd", "Jk")
RANK_AT_RETIREMENT_NOTE = (
    "<strong>Rank at Retirement.</strong> This is the final observed banzuke "
    'rank group for retired rikishi according to <a href="https://sumodb.sumogames.de/">'
    "SumoDB</a>-derived banzuke history. Rikishi listed on the latest available "
    "banzuke are treated as active and excluded."
)


@dataclass(frozen=True)
class RetirementRankRow:
    rikishi_id: int
    shikona: str
    last_appearance: str
    last_chii: str
    rank_group: str


@dataclass(frozen=True)
class RankGroupCount:
    rank_group: str
    count: int
    proportion: float


@dataclass(frozen=True)
class UnmappedRankWarning:
    rikishi_id: int
    shikona: str
    last_appearance: str
    last_chii: str
    rank_group: str

    def message(self) -> str:
        return (
            f"{self.shikona} ({self.rikishi_id}) retired from {self.last_chii} "
            f"in {self.last_appearance}, mapped to unexpected group "
            f"{self.rank_group!r}."
        )


@dataclass(frozen=True)
class RankAtRetirementOutputs:
    output_root: Path
    bundle_dir: Path
    retired_csv: Path
    distribution_csv: Path
    metadata_json: Path
    page_json: Path
    log_path: Path


def compute_rank_at_retirement(
    history: History,
) -> tuple[list[RetirementRankRow], int, list[UnmappedRankWarning]]:
    dates = sorted(history.keys())
    if not dates:
        return [], 0, []

    latest_history_date = dates[-1]
    appearances: dict[RikId, list[Date]] = {}

    for date in dates:
        for rikishi_id in history(date).banzuke.riks:
            appearances.setdefault(rikishi_id, []).append(date)

    rows: list[RetirementRankRow] = []
    warnings: list[UnmappedRankWarning] = []
    active_count = 0

    for rikishi_id in sorted(appearances, key=int):
        last_date = appearances[rikishi_id][-1]
        if last_date == latest_history_date:
            active_count += 1
            continue

        banzuke = history(last_date).banzuke
        shikona = str(banzuke.get_shik(rikishi_id))
        chii = banzuke.get_chii(rikishi_id)
        rank_group = chii.level.as_abbreviation()
        row = RetirementRankRow(
            rikishi_id=int(rikishi_id),
            shikona=shikona,
            last_appearance=str(last_date),
            last_chii=str(chii),
            rank_group=rank_group,
        )
        rows.append(row)
        if rank_group not in RANK_GROUPS:
            warnings.append(
                UnmappedRankWarning(
                    rikishi_id=row.rikishi_id,
                    shikona=row.shikona,
                    last_appearance=row.last_appearance,
                    last_chii=row.last_chii,
                    rank_group=row.rank_group,
                )
            )

    return rows, active_count, warnings


def build_rank_at_retirement_outputs(
    history: History,
    output_root: Path = OUTPUT_ROOT,
    print_summary: bool = True,
) -> RankAtRetirementOutputs:
    rows, active_count, warnings = compute_rank_at_retirement(history)
    range_token = _history_range_token(history)
    output_root.mkdir(parents=True, exist_ok=True)
    bundle_dir = output_root / "site" / f"rank_at_retirement_{range_token}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    outputs = RankAtRetirementOutputs(
        output_root=output_root,
        bundle_dir=bundle_dir,
        retired_csv=output_root / f"rank_at_retirement_{range_token}_rikishi.csv",
        distribution_csv=bundle_dir / "distribution.csv",
        metadata_json=bundle_dir / "metadata.json",
        page_json=bundle_dir / "page.json",
        log_path=output_root / f"rank_at_retirement_{range_token}.log",
    )

    _write_dataclass_csv(rows, outputs.retired_csv)
    _write_dataclass_csv(_distribution(rows), outputs.distribution_csv)
    _write_page_json(outputs.page_json)
    _write_metadata(
        history=history,
        rows=rows,
        active_count=active_count,
        warnings=warnings,
        output_path=outputs.metadata_json,
    )
    log_text = _make_log(
        history=history,
        rows=rows,
        active_count=active_count,
        warnings=warnings,
        include_warning_details=True,
    )
    outputs.log_path.write_text(log_text, encoding="utf-8")
    if print_summary:
        print(
            _make_log(
                history=history,
                rows=rows,
                active_count=active_count,
                warnings=warnings,
                include_warning_details=False,
            ),
            end="",
        )
    return outputs


def load_history_from_zip(path: Path) -> History:
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def _distribution(rows: list[RetirementRankRow]) -> list[RankGroupCount]:
    total = len(rows)
    return [
        RankGroupCount(
            rank_group=rank_group,
            count=sum(1 for row in rows if row.rank_group == rank_group),
            proportion=_safe_probability(
                sum(1 for row in rows if row.rank_group == rank_group),
                total,
            ),
        )
        for rank_group in RANK_GROUPS
    ]


def _safe_probability(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 8)


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


def _write_page_json(output_path: Path) -> None:
    payload = {
        "id": "rank_at_retirement",
        "title": "Rank at Retirement",
        "layout": "single_chart",
        "data_sources": [
            {
                "id": "distribution",
                "label": "Distribution",
                "data": "distribution.csv",
                "kind": "bar",
            }
        ],
        "chart": {
            "x": "rank_group",
            "x_label": "Final observed rank group",
            "y": "count",
            "y_label": "Retired rikishi count",
            "rank_group_order": list(RANK_GROUPS),
        },
        "notes": [
            {
                "id": "rank_at_retirement",
                "placement": "below_chart",
                "format": "html",
                "note_for": "all",
                "notes": RANK_AT_RETIREMENT_NOTE,
            }
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_metadata(
    *,
    history: History,
    rows: list[RetirementRankRow],
    active_count: int,
    warnings: list[UnmappedRankWarning],
    output_path: Path,
) -> None:
    dates = sorted(history.keys())
    payload = {
        "history_basho_count": len(dates),
        "first_history_basho": str(dates[0]) if dates else None,
        "latest_history_basho": str(dates[-1]) if dates else None,
        "retired_count": len(rows),
        "active_excluded_count": active_count,
        "unmapped_count": len(warnings),
        "rank_group_order": list(RANK_GROUPS),
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _make_log(
    *,
    history: History,
    rows: list[RetirementRankRow],
    active_count: int,
    warnings: list[UnmappedRankWarning],
    include_warning_details: bool,
) -> str:
    dates = sorted(history.keys())
    lines = [
        "Rank at retirement",
        "==================",
        f"History basho: {len(dates)}",
        f"First basho: {dates[0] if dates else 'n/a'}",
        f"Latest basho: {dates[-1] if dates else 'n/a'}",
        f"Retired rikishi: {len(rows)}",
        f"Active rikishi excluded: {active_count}",
        f"Unmapped final chii: {len(warnings)}",
        "",
        "Counts",
        "------",
    ]
    counts = {row.rank_group: 0 for row in rows}
    for row in rows:
        counts[row.rank_group] = counts.get(row.rank_group, 0) + 1
    for rank_group in RANK_GROUPS:
        lines.append(f"{rank_group}: {counts.get(rank_group, 0)}")
    if include_warning_details and warnings:
        lines.extend(["", "Unmapped warnings", "-----------------"])
        lines.extend(warning.message() for warning in warnings)
    return "\n".join(lines) + "\n"


def _history_range_token(history: History) -> str:
    dates = sorted(history.keys())
    if not dates:
        return "empty"
    return f"{_date_token(dates[0])}_to_{_date_token(dates[-1])}"


def _date_token(date: Date) -> str:
    return f"{int(date.year):04d}_{int(date.month):02d}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Build from a History zip instead of the live store.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory for rank-at-retirement outputs.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else get_history()
    outputs = build_rank_at_retirement_outputs(history, output_root=args.output_root)
    print(f"Retired CSV: {outputs.retired_csv}")
    print(f"Site bundle: {outputs.bundle_dir}")


if __name__ == "__main__":
    main()
