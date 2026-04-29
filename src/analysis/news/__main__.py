import argparse

from src.infra.parser.parser2 import get_banzuke
from src.infra.parser.parser2_IntDate import IntDate as Date


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Toy caller for parsing one banzuke for change analysis."
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Basho date in YYYY/MM format.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of parsed entries to print.",
    )
    return parser


def _parse_date(date_text: str) -> Date:
    year_text, month_text = date_text.split("/", 1)
    return Date(int(year_text), int(month_text))


def main() -> None:
    args = _build_parser().parse_args()
    date = _parse_date(args.date)

    banzuke = get_banzuke(date)
    if banzuke is None:
        print(f"No banzuke parsed for {date}")
        return

    ranked_riks = sorted(
        banzuke.riks,
        key=lambda rid: banzuke.get_chii(rid),
    )

    print(f"Banzuke: {date}")
    print(f"Rikishi: {len(banzuke)}")
    print(f"First {min(args.limit, len(ranked_riks))} by rank:")

    for rid in ranked_riks[: args.limit]:
        print(f"{banzuke.get_chii(rid)} {banzuke.get_shik(rid)} ({int(rid)})")


if __name__ == "__main__":
    main()
