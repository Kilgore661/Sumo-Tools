import argparse
import datetime
import json
from pathlib import Path

from src.infra.config import EPOCH

from ...infra.connect import connect
from ...sumo_core.BasicPrimitives import RikId
from ..equelo.config_main import BIOS_PATH, CONSTANT_K, OUTPUT_ROOT
from ..equelo.expt1.params import DEFAULT_K_CONFIG_PATH
from ..equelo.expt1.Oracle import make_oracle
from .builder import build_probability_rows, load_ratings_csv, write_probability_csv


VALID_K_POLICIES = ("constant", "divisional")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build observed vs estimated chii-pair probabilities"
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")

    parser.add_argument(
        "--ratings-csv",
        type=Path,
        default=None,
        help="Explicit path to an Expt2 final ratings CSV. If omitted, derive it from the parameter flags below.",
    )

    parser.add_argument("--variant", choices=["a", "b"], default="b")
    parser.add_argument("--open", action="store_true", help="Use open-mode ratings filename")
    parser.add_argument("--k-policy", choices=VALID_K_POLICIES, default="divisional")
    parser.add_argument(
        "--k-value",
        type=float,
        default=None,
        help="Constant K value. Valid only with --k-policy constant.",
    )
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG_PATH)

    parser.add_argument(
        "--q",
        type=float,
        default=400.0,
        help="Elo logistic scale parameter used to generate the estimated probabilities (default: 400).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV path. Default is derived from the resolved ratings CSV stem.",
    )
    return parser


def _validate_k_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.k_policy == "constant":
        if args.k_config is not None:
            parser.error("--k-config may only be used with --k-policy divisional")
        if args.k_value is None:
            args.k_value = CONSTANT_K
        return

    if args.k_policy == "divisional":
        if args.k_value is not None:
            parser.error("--k-value may only be used with --k-policy constant")
        if args.k_config is None:
            args.k_config = DEFAULT_K_CONFIG_PATH
        return

    parser.error(f"Unsupported --k-policy: {args.k_policy}")


def _mode_stem(args: argparse.Namespace) -> str:
    return "open" if args.open else "closed"


def _policy_stem(args: argparse.Namespace) -> str:
    if args.k_policy == "constant":
        return f"constant_k{args.k_value:g}"
    config_stem = Path(args.k_config).stem
    return f"divisional_{config_stem}"


def _resolve_ratings_csv(args: argparse.Namespace) -> Path:
    if args.ratings_csv is not None:
        return args.ratings_csv

    stem = f"expt2_variant_{args.variant}_{_mode_stem(args)}_{_policy_stem(args)}"
    return OUTPUT_ROOT / f"{stem}_final.csv"


def _default_output_path(ratings_csv: Path) -> Path:
    return OUTPUT_ROOT / f"{ratings_csv.stem}_probabilities.csv"


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_k_args(parser, args)

    ratings_csv = _resolve_ratings_csv(args)
    if not ratings_csv.exists():
        raise FileNotFoundError(f"Ratings CSV not found: {ratings_csv}")

    raw_history = connect(args.start, args.end, use_zip=args.zip)

    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    bios = {RikId(int(k)): v for k, v in raw_bios.items()}

    oracle = make_oracle(raw_history, bios)
    ratings = load_ratings_csv(ratings_csv)

    rows = build_probability_rows(
        history=oracle.history,
        ratings=ratings,
        q=args.q,
    )

    output_path = args.output if args.output is not None else _default_output_path(ratings_csv)
    written = write_probability_csv(rows, output_path)

    print(f"Ratings CSV: {ratings_csv}")
    print(f"Variant: {args.variant}")
    print(f"Mode: {_mode_stem(args)}")
    print(f"K policy: {args.k_policy}")
    if args.k_policy == "constant":
        print(f"K value: {args.k_value:g}")
    else:
        print(f"K config: {args.k_config}")
    print(f"q: {args.q:g}")
    print(f"Rows written: {len(rows)}")
    print(f"Output CSV: {written}")


if __name__ == "__main__":
    main()
