import argparse
import time
from pathlib import Path

from .config import DEFAULT_SEED_BASE
from .run import run_one_shot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="One-shot convergence charts for modern closed-mode Equelo"
    )
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--seed-base", type=int, default=DEFAULT_SEED_BASE)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    t0 = time.perf_counter()
    output_dir: Path = run_one_shot(
        end_year=args.end,
        use_zip=args.zip,
        seed_base=args.seed_base,
    )
    elapsed_seconds = time.perf_counter() - t0

    print(output_dir)
    print(f"Execution time: {elapsed_seconds:.3f} seconds")
