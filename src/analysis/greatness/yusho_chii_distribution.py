"""Write the distribution of Makuuchi yusho winners by grouped chii."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import MSD, Prize
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History


DEFAULT_OUTPUT = Path(
    "files/output/analysis/greatness/yusho_chii_distribution.csv"
)
CHII_GROUPS = ("Y", "O", "S", "K", *(f"M{number}" for number in range(1, 18)))
TOTAL_GROUP = "Total"


@dataclass(frozen=True)
class YushoChiiDistributionRow:
    chii_group: str
    yusho: int
    share_percent: float


def yusho_chii_distribution(
    history: History,
) -> tuple[YushoChiiDistributionRow, ...]:
    """Return rows for Y, O, S, K, M1-M17, followed by a total row.

    Only Makuuchi yusho markers are counted. East/West, numbered positions at
    named ranks, and rank annotations are deliberately combined.
    """

    counts: Counter[str] = Counter()

    for state in history.values():
        for rikishi_id, performance in state.summary.performances.items():
            if Prize.YUSHO not in performance.prizes:
                continue

            chii = state.banzuke.rikchii.get(rikishi_id)
            if chii is None or not isinstance(chii.level, MSD):
                continue

            group = _chii_group(chii)
            if group not in CHII_GROUPS:
                raise ValueError(f"Yusho winner has unsupported chii group: {group}")
            counts[group] += 1

    total = sum(counts.values())
    grouped_rows = tuple(
        YushoChiiDistributionRow(
            chii_group=group,
            yusho=counts[group],
            share_percent=round(100 * counts[group] / total, 2) if total else 0.0,
        )
        for group in CHII_GROUPS
    )
    return grouped_rows + (
        YushoChiiDistributionRow(
            chii_group=TOTAL_GROUP,
            yusho=total,
            share_percent=100.0 if total else 0.0,
        ),
    )


def write_distribution_csv(
    rows: tuple[YushoChiiDistributionRow, ...],
    output_path: Path = DEFAULT_OUTPUT,
) -> None:
    """Write distribution rows to ``output_path``."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=YushoChiiDistributionRow.__dataclass_fields__,
        )
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _chii_group(chii: Chii) -> str:
    abbreviation = chii.level.as_abbreviation()
    return f"M{chii.number}" if chii.level == MSD.MAEGASHIRA else abbreviation


def _load_history(path: Path | None) -> History:
    if path is None:
        return get_history()
    archive = path if path.suffix.lower() == ".zip" else path.with_suffix(".zip")
    return load_history_with_annotations(str(archive.with_suffix("")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load a History zip instead of the live store.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = yusho_chii_distribution(_load_history(args.history_zip))
    write_distribution_csv(rows, args.output)
    print(f"Makuuchi yusho: {rows[-1].yusho}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
