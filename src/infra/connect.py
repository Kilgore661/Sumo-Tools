import datetime
import os
import sys
import zipfile
from time import time
import pickle  # or whatever your serializer uses

from src.infra.config import EPOCH
from src.infra.live_store.api import get_history

import argparse
import datetime

from src.infra.config import EPOCH
from src.infra.live_store.api import get_history
from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations

def load_history_from_zip(start_year: int, end_year: int):
    path = f"files/output/Historys/{start_year}_01 to {end_year}_11.zip"

    if not os.path.exists(path):
        raise RuntimeError(f"Zip not found: {path}")

    with zipfile.ZipFile(path, "r") as zf:
        # assume single file inside
        name = zf.namelist()[0]
        with zf.open(name) as f:
            return pickle.load(f)


def validate_years(start: int, end: int):
    now_year = datetime.datetime.now().year

    if not (EPOCH <= start <= end <= now_year):
        raise RuntimeError(
            f"Invalid year range: {start}..{end} "
            f"(must satisfy {EPOCH} <= start <= end <= {now_year})"
        )


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")

    return parser.parse_args()


def load_history_from_zip(start_year: int, end_year: int):
    filename = f"files/output/Historys/{start_year}_01 to {end_year}_11"
    return load_history_with_annotations(filename)


def validate_years(start: int, end: int) -> None:
    now_year = datetime.datetime.now().year

    if not (EPOCH <= start <= end <= now_year):
        raise RuntimeError(
            f"invalid year range: {start}..{end} "
            f"(must satisfy {EPOCH} <= start <= end <= {now_year})"
        )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    return parser.parse_args()


def connect():
    args = parse_args()
    validate_years(args.start, args.end)

    t0 = time()
    if args.zip:
        print(f"[loader] loading from zip: {args.start} - {args.end} ...", end = ' ', flush = True )
        history = load_history_from_zip(args.start, args.end)
    else:
        print("[loader] loading from live store ...", end = ' ', flush = True )
        history = get_history()
    print( f'{time()-t0:.0f} seconds.' )

    return history


if __name__ == "__main__":
    connect()
