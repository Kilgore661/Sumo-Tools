"""Produce highest fixed_v2 Equelo rating records."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.equelo.fixed_v2.api import DayEndRatings, load_day_end_ratings
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History


OUTPUT_ROOT = Path("files/output/analysis/sumo_history/records/highest_equelo")


@dataclass(frozen=True)
class RatingPoint:
    date: str
    day: int

    def label(self) -> str:
        return f"{self.date}/{self.day:02d}"


@dataclass(frozen=True)
class HighestEqueloRecord:
    rikishi_id: RikId
    rating: float
    point: RatingPoint


@dataclass(frozen=True)
class HighestEqueloRow:
    position: int
    rikishi_id: int
    shikona: str
    rating: str
    date: str


@dataclass(frozen=True)
class HighestEqueloOutputs:
    output_root: Path
    highest_equelo_csv: Path


def build_highest_equelo_outputs(
    *,
    day_end_ratings: DayEndRatings | None = None,
    full_shikona_store: FullShikonaStore | None = None,
    history: History | None = None,
    output_root: Path = OUTPUT_ROOT,
) -> HighestEqueloOutputs:
    """Write the site-facing highest-Equelo CSV."""

    ratings = day_end_ratings if day_end_ratings is not None else load_day_end_ratings()
    shikona_store = (
        full_shikona_store
        if full_shikona_store is not None
        else FullShikonaStore.from_json()
    )
    rows = highest_equelo_rows(
        day_end_ratings=ratings,
        full_shikona_store=shikona_store,
        represented_dates=represented_date_labels(history),
    )

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = HighestEqueloOutputs(
        output_root=output_root,
        highest_equelo_csv=output_root / "highest_equelo.csv",
    )
    write_dataclass_csv(rows, outputs.highest_equelo_csv)
    return outputs


def highest_equelo_rows(
    *,
    day_end_ratings: DayEndRatings,
    full_shikona_store: FullShikonaStore,
    represented_dates: frozenset[str] | None = None,
) -> list[HighestEqueloRow]:
    """Return all rikishi ranked by maximum observed fixed_v2 day-end rating."""

    records = highest_equelo_records(
        day_end_ratings,
        represented_dates=represented_dates,
    )
    ranked = sorted(
        records.values(),
        key=lambda record: (
            -record.rating,
            record.point.date,
            record.point.day,
            int(record.rikishi_id),
        ),
    )
    return [
        HighestEqueloRow(
            position=index,
            rikishi_id=int(record.rikishi_id),
            shikona=full_shikona_store.full_shikona(record.rikishi_id),
            rating=f"{record.rating:.3f}",
            date=record.point.label(),
        )
        for index, record in enumerate(ranked, start=1)
    ]


def highest_equelo_records(
    day_end_ratings: DayEndRatings,
    *,
    represented_dates: frozenset[str] | None = None,
) -> dict[RikId, HighestEqueloRecord]:
    """Return the maximum fixed_v2 day-end rating point for each rikishi."""

    records: dict[RikId, HighestEqueloRecord] = {}
    for date in sorted(day_end_ratings):
        if represented_dates is not None and date not in represented_dates:
            continue
        for day_text in sorted(day_end_ratings[date], key=int):
            point = RatingPoint(date=date, day=int(day_text))
            for rikishi_id_text, raw_rating in sorted(
                day_end_ratings[date][day_text].items(),
                key=lambda item: int(item[0]),
            ):
                rikishi_id = RikId(int(rikishi_id_text))
                rating = float(raw_rating)
                current = records.get(rikishi_id)
                if current is None or rating > current.rating:
                    records[rikishi_id] = HighestEqueloRecord(
                        rikishi_id=rikishi_id,
                        rating=rating,
                        point=point,
                    )
    return records


def represented_date_labels(history: History | None) -> frozenset[str] | None:
    """Return the selected History date labels, or None for all rating dates."""

    if history is None:
        return None
    return frozenset(str(date) for date in history)


def write_dataclass_csv(rows: Iterable[object], output_path: Path) -> None:
    """Write dataclass rows to CSV."""

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


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(
        description="Produce highest fixed_v2 Equelo rating records."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory for highest-Equelo output.",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Restrict rating dates to those represented by this History zip.",
    )
    parser.add_argument(
        "--day-end-ratings-root",
        type=Path,
        help="Directory containing fixed_v2 day_end_ratings.json.",
    )
    return parser


def load_history_from_zip(path: Path) -> History:
    """Load a History from a zip-backed annotated serialisation."""

    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> None:
    """Run the producer."""

    args = build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else None
    day_end_ratings = (
        load_day_end_ratings(output_root=args.day_end_ratings_root)
        if args.day_end_ratings_root
        else None
    )
    outputs = build_highest_equelo_outputs(
        day_end_ratings=day_end_ratings,
        history=history,
        output_root=args.output_root,
    )
    print("Wrote:")
    print(f"  Highest Equelo: {outputs.highest_equelo_csv}")


if __name__ == "__main__":
    main()
