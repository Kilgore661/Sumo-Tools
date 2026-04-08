import argparse
import datetime
import gzip
import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from time import time

from src.infra.config import EPOCH
from src.infra.connect import connect
from src.sumo_core.Chii import Chii
from src.sumo_core.BasicPrimitives import RikId

from src.analysis.equelo.config_main import BIOS_PATH, OUTPUT_ROOT
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import (
    EloParams,
    DEFAULT_K_CONFIG_PATH,
)
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate

from .helpers import load_equelo


# -------------------------------
# Ratings container
# -------------------------------

@dataclass(frozen=True)
class Ratings:
    basho_start: dict
    day_end: dict

    def the_rating(self, r: RikId, d, da):
        return self.day_end[d][da][r]


# -------------------------------
# IO helpers
# -------------------------------

def ratings_zip_path(policy: str) -> Path:
    return OUTPUT_ROOT / f"equelo_{policy}.zip"


def save_ratings_to_zip(ratings: Ratings, path: Path) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as f:
        pickle.dump(ratings, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_ratings_from_zip(path: Path) -> Ratings:
    if not path.exists():
        raise RuntimeError(f"Ratings zip not found: {path}")
    with gzip.open(path, "rb") as f:
        return pickle.load(f)


def load_bios() -> dict[RikId, dict]:
    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    return {RikId(int(k)): v for k, v in raw_bios.items()}


# -------------------------------
# CLI
# -------------------------------

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
    parser.add_argument(
        "--k-policy",
        choices=["constant", "divisional"],
        default="constant",
        help="K-factor policy.",
    )
    parser.add_argument(
        "--k-config",
        type=Path,
        default=DEFAULT_K_CONFIG_PATH,
        help="Config file for divisional K.",
    )
    return parser.parse_args()


# -------------------------------
# Param builder
# -------------------------------

def build_params(policy: str, config_path: Path) -> EloParams:
    if policy == "constant":
        return EloParams.constant()
    if policy == "divisional":
        return EloParams.divisional(config_path=config_path)
    raise ValueError(f"Unknown k-policy: {policy}")


# -------------------------------
# Initialiser
# -------------------------------

def equelo_initialiser(mu: dict[Chii, float]):
    def initialise(rikid, chii, date) -> float:
        del rikid, date
        return mu[chii]
    return initialise


# -------------------------------
# Main
# -------------------------------

def main():
    args = parse_args()
    validate_years(args.start, args.end)

    ratings_zip = ratings_zip_path(args.k_policy)
    params = build_params(args.k_policy, args.k_config)

    mu = load_equelo()
    print(f'Y1e = {mu[Chii.from_str("Y1e")]:.0f}')
    print(f"[policy] k-policy = {args.k_policy}")

    if args.k_policy == "divisional":
        print(f"[policy] k-config = {args.k_config}")

    # load history
    t0 = time()
    print(
        f"[loader] loading history: {args.start} - {args.end} "
        f"({'zip' if args.zip else 'live'}) ...",
        end=" ",
        flush=True,
    )
    raw_history = connect(args.start, args.end, use_zip=args.zip)
    print(f"{time() - t0:.0f} seconds.")

    bios = load_bios()
    oracle = make_oracle(raw_history, bios)

    dates = sorted(oracle.history.keys())
    print(f"{len(dates)} basho, {dates[0]} to {dates[-1]}")

    mode = SimulationMode.OPEN if args.open else SimulationMode.CLOSED

    # simulate
    t1 = time()
    print(
        f"[simulate] running full simulation ({mode.value}, {args.k_policy}) ...",
        end=" ",
        flush=True,
    )
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

    # save
    t2 = time()
    print(f"[save] writing ratings to {ratings_zip} ...", end=" ", flush=True)
    save_ratings_to_zip(ratings, ratings_zip)
    print(f"{time() - t2:.0f} seconds.")

    # load (sanity check)
    t3 = time()
    print(f"[load] loading ratings from {ratings_zip} ...", end=" ", flush=True)
    loaded = load_ratings_from_zip(ratings_zip)
    print(f"{time() - t3:.0f} seconds.")

    print("\nDone.")


if __name__ == "__main__":
    main()
