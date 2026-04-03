from pathlib import Path
import json

from ...infra.connect import connect
from ...sumo_core.History import Date
from ...sumo_core.BasicPrimitives import RikId, Day, Year, Month

from .EloParams import EloParams
from .Oracle import make_oracle
from .ratings import get_ratings_and_diagnostics
from .config import BIOS_PATH


def main() -> None:
    raw_history = connect()
    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        bios = json.load(f)
    oracle = make_oracle(raw_history, bios)

    params = EloParams()
    results = get_ratings_and_diagnostics(oracle.history, params)

    dates = sorted(results.ratings.keys())
    if not dates:
        print("No ratings produced.")
        return

    first_date = dates[0]
    last_date = dates[-1]
    print(f"Computed ratings for {len(dates)} basho: {first_date} to {last_date}")

    last_basho = results.ratings[last_date]
    last_day = max(last_basho.keys())
    n = len(last_basho[last_day])
    print(f"Rikishi rated at end of {last_date} day {last_day}: {n}")

    test_date = Date(Year(2026), Month(3))
    test_day = Day(3)
    test_rikishi = RikId(12451)

    print()
    print("Test query:")
    print(f"  Date:    {test_date}")
    print(f"  Day:     {test_day}")
    print(f"  Rikishi: {test_rikishi}")

    rating = results.ratings[test_date][test_day][test_rikishi]
    print(f"  Rating:  {rating}")

    print()
    print("Diagnostics:")
    for note in results.diagnostics.notes:
        print(f"  - {note}")


if __name__ == "__main__":
    main()
