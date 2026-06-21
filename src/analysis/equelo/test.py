import argparse
import datetime
import gzip
import pickle
from dataclasses import dataclass
from time import time

from src.infra.config import EPOCH
from src.infra.connect import connect
from src.sumo_core.Chii import Chii
from src.sumo_core.BasicPrimitives import RikId

from src.analysis.equelo.config_main import OUTPUT_ROOT
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import EloParams
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate

from .helpers import load_equelo


RATINGS_ZIP = OUTPUT_ROOT / "equelo.zip"


@dataclass(frozen=True)
class Ratings:
    basho_start: dict
    day_end: dict

    def the_rating(self, r: RikId, d, da):
        return self.day_end[d][da][r]


def save_ratings_to_zip(ratings: Ratings) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with gzip.open(RATINGS_ZIP, "wb") as f:
        pickle.dump(ratings, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_ratings_from_zip() -> Ratings:
    if not RATINGS_ZIP.exists():
        raise RuntimeError(f"Ratings zip not found: {RATINGS_ZIP}")
    with gzip.open(RATINGS_ZIP, "rb") as f:
        return pickle.load(f)


def validate_years(start: int, end: int) -> None:
    now_year = datetime.datetime.now().year
    if not (EPOCH <= start <= end <= now_year):
        raise RuntimeError(
            f"invalid year range: {start}..{end} "
            f"(must satisfy {EPOCH} <= start <= end <= {now_year})"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Equelo simulation and persist all basho/day ratings."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Use open active-universe semantics (default is closed).",
    )
    return parser.parse_args()


def equelo_initialiser(mu: dict[Chii, float]):
    def initialise(rikid, chii, date) -> float:
        del rikid, date
        return mu[chii]

    return initialise


def main():
    args = parse_args()
    validate_years(args.start, args.end)

    mu = load_equelo()
    print(f'Y1e = {mu[Chii.from_str("Y1e")]:.0f}')

    t0 = time()
    print(
        f"[loader] loading history: {args.start} - {args.end} "
        f"({'zip' if args.zip else 'live'}) ...",
        end=" ",
        flush=True,
    )
    raw_history = connect(args.start, args.end, use_zip=args.zip)
    print(f"{time() - t0:.0f} seconds.")

    oracle = make_oracle(raw_history)

    dates = sorted(oracle.history.keys())
    print(f"{len(dates)} basho, {dates[0]} to {dates[-1]}")

    params = EloParams.constant()
    mode = SimulationMode.OPEN if args.open else SimulationMode.CLOSED

    t1 = time()
    print(f"[simulate] running full simulation ({mode.value}) ...", end=" ", flush=True)
    results = simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=equelo_initialiser(mu),
        mode=mode,
        observer=None,
    )
    print(f"{time() - t1:.0f} seconds.")

    ratings = Ratings(
        basho_start=results.basho_start_ratings,
        day_end=results.day_end_ratings,
    )

    t2 = time()
    print(f"[save] writing ratings to {RATINGS_ZIP} ...", end=" ", flush=True)
    save_ratings_to_zip(ratings)
    print(f"{time() - t2:.0f} seconds.")

    t3 = time()
    print(f"[load] loading ratings from {RATINGS_ZIP} ...", end=" ", flush=True)
    loaded = load_ratings_from_zip()
    print(f"{time() - t3:.0f} seconds.")

    loaded_dates = sorted(loaded.day_end.keys())
    last_date = loaded_dates[-1]
    last_day = max(loaded.day_end[last_date].keys())
    sample_rikishi = next(iter(loaded.day_end[last_date][last_day].keys()))

    print()

    # Top 100 ratings for anyone (all observations)
    all_observations = []

    for date, basho_ratings in loaded.day_end.items():
        for day, daily_ratings in basho_ratings.items():
            for rikishi, rating in daily_ratings.items():
                shikona = oracle.history[date].banzuke.rikshik.get(rikishi, "?")
                all_observations.append((rating, rikishi, shikona, date, day))

    all_observations.sort(key=lambda x: x[0], reverse=True)
    top_100_anyone = all_observations[:100]

    print()
    print("Top 20 ratings for anyone (from top 100):")
    for i, (rating, rikishi, shikona, date, day) in enumerate(top_100_anyone[:20], start=1):
        print(
            f"{i:2d}. "
            f"{rating:.2f} | {shikona} ({rikishi}) | Date: {date} | Day: {day}"
        )

    # Top 100 ratings for unique rikishi (career peaks)
    best_by_rikishi = {}

    for date, basho_ratings in loaded.day_end.items():
        for day, daily_ratings in basho_ratings.items():
            for rikishi, rating in daily_ratings.items():
                current = best_by_rikishi.get(rikishi)
                if current is None or rating > current[0]:
                    shikona = oracle.history[date].banzuke.rikshik.get(rikishi, "?")
                    best_by_rikishi[rikishi] = (rating, shikona, date, day)

    all_peaks = [
        (rating, rikishi, shikona, date, day)
        for rikishi, (rating, shikona, date, day) in best_by_rikishi.items()
    ]

    all_peaks.sort(key=lambda x: x[0], reverse=True)
    top_100_unique = all_peaks[:100]

    print()
    print("Top 20 ratings for unique rikishi (from top 100):")
    for i, (rating, rikishi, shikona, date, day) in enumerate(top_100_unique[:20], start=1):
        print(
            f"{i:2d}. "
            f"{rating:.2f} | {shikona} ({rikishi}) | Date: {date} | Day: {day}"
        )

    best_day15_by_rikishi = {}

    for date, basho_ratings in loaded.day_end.items():
        for day, daily_ratings in basho_ratings.items():
            if int(day) != 15:
                continue

            for rikishi, rating in daily_ratings.items():
                current = best_day15_by_rikishi.get(rikishi)
                if current is None or rating > current[0]:
                    shikona = oracle.history[date].banzuke.rikshik.get(rikishi, "?")
                    best_day15_by_rikishi[rikishi] = (rating, shikona, date, day)

    all_day15_peaks = [
        (rating, rikishi, shikona, date, day)
        for rikishi, (rating, shikona, date, day) in best_day15_by_rikishi.items()
    ]

    all_day15_peaks.sort(key=lambda x: x[0], reverse=True)
    top_100_day15_unique = all_day15_peaks[:100]

    print()
    print("Top 10 Day 15 ratings for unique rikishi (from top 100):")
    for i, (rating, rikishi, shikona, date, day) in enumerate(top_100_day15_unique[:10], start=1):
        print(
            f"{i:2d}. "
            f"{rating:.2f} | {shikona} ({rikishi}) | Date: {date} | Day: {day}"
        )
if __name__ == "__main__":
    main()
