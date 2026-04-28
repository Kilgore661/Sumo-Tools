import argparse
import datetime
from pathlib import Path

from src.analysis.persistence.division_persistence import compute_division_persistence
from src.analysis.persistence.reports import (
    write_persistence_chart,
    write_persistence_csv,
)
from src.infra.config import EPOCH
from src.infra.live_store.api import get_history
from src.sumo_core.History import History


OUTPUT_DIR = Path("files/output/persistence")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute retrospective division persistence."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--num-basho", type=int, required=True)
    return parser


def _output_stem(start: int, end: int, num_basho: int) -> str:
    return f"division_persistence ({start}-{end}, num_basho={num_basho})"


def _chart_title(start: int, end: int, num_basho: int) -> str:
    return f"Division Persistence over {num_basho} Basho ({start}-{end})"


def _slice_history_years(history: History, start: int, end: int) -> History:
    return History({
        date: history(date)
        for date in sorted(history.keys())
        if start <= date.year <= end
    })


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    history = _slice_history_years(
        history=get_history(),
        start=args.start,
        end=args.end,
    )
    results = compute_division_persistence(
        history=history,
        num_basho=args.num_basho,
    )

    stem = _output_stem(
        start=args.start,
        end=args.end,
        num_basho=args.num_basho,
    )
    csv_path = OUTPUT_DIR / f"{stem}.csv"
    chart_path = OUTPUT_DIR / f"{stem}.html"

    written_csv = write_persistence_csv(
        results=results,
        output_path=csv_path,
    )
    written_chart = write_persistence_chart(
        results=results,
        output_path=chart_path,
        title=_chart_title(
            start=args.start,
            end=args.end,
            num_basho=args.num_basho,
        ),
    )

    print(f"Rows: {len(results.rows)}")
    print(f"CSV: {written_csv}")
    print(f"Chart: {written_chart}")


if __name__ == "__main__":
    main()
