"""Generate same-History P1 and P1-WL fits and compare their prior maps."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
from time import perf_counter

from src.analysis.equelo_bkp1.model import FixedPointResult
from src.analysis.equelo_bkp1.params import (
    DEFAULT_K_CONFIG,
    MODEL_BASE,
    MODEL_Q,
    load_divisional_k,
)
from src.analysis.equelo_bkp1.simulate import (
    BoutEligibility,
    count_eligibility,
)
from src.analysis.equelo_bkp1.solve import solve
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.sumo_core.BasicEnums import MSD
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.validation.provenance import history_fingerprint

from .audit import load_history


DEFAULT_OUTPUT_PARENT = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/output"
)
ELO89_START = Date.from_ints(1989, 1)


def run_comparison(
    history: History,
    *,
    output_root: Path,
    k_config_path: Path = DEFAULT_K_CONFIG,
    epsilon: float = 10.0,
    max_iterations: int = 200,
    history_source: dict[str, object] | None = None,
) -> Path:
    """Fit the legacy control and P1-WL candidate and write comparison artifacts."""

    started = perf_counter()
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if max_iterations < 1:
        raise ValueError("max_iterations must be at least one")
    dates = sorted(history)
    if not dates or dates[0] != ELO89_START:
        first = None if not dates else str(dates[0])
        raise ValueError(
            "P1-WL validation requires a History beginning at 1989/01; "
            f"received {first!r}"
        )
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite comparison output: {output_root}")

    output_root.mkdir(parents=True)
    divisional_k = load_divisional_k(k_config_path)
    variants: dict[BoutEligibility, FixedPointResult] = {}
    for eligibility in (BoutEligibility.P1, BoutEligibility.P1_WL):
        result = solve(
            history,
            divisional_k,
            epsilon=epsilon,
            max_iterations=max_iterations,
            eligibility=eligibility,
        )
        variants[eligibility] = result
        _write_variant(
            output_root / eligibility.value,
            result,
            eligibility=eligibility,
            counts=asdict(count_eligibility(history, eligibility)),
            epsilon=epsilon,
            max_iterations=max_iterations,
        )

    comparison_root = output_root / "comparison"
    comparison_root.mkdir()
    rows = _comparison_rows(
        variants[BoutEligibility.P1],
        variants[BoutEligibility.P1_WL],
    )
    _write_csv(comparison_root / "prior_comparison.csv", rows)
    summary = _comparison_summary(rows)
    (comparison_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    total_runtime_seconds = perf_counter() - started

    source = dict(history_source or {"kind": "provided History"})
    source["selected_history_sha256"] = history_fingerprint(history)
    manifest = {
        "schema_version": 1,
        "experiment": "P1-WL same-History comparison",
        "history": {
            **source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "basho_count": len(dates),
        },
        "model": {
            "q": MODEL_Q,
            "base": MODEL_BASE,
            "epsilon": epsilon,
            "max_iterations": max_iterations,
            "k_config": str(k_config_path.resolve()),
            "k_config_sha256": _sha256(k_config_path),
            "controlled_difference": "bout eligibility only",
            "history_preprocessing": "oracle annotation_only",
        },
        "variants": {
            eligibility.value: {
                "eligibility": eligibility.value,
                "converged": result.converged,
                "iterations": result.iterations,
                "final_delta": result.final_delta,
                "convergence": {
                    "threshold": epsilon,
                    "maximum_iterations": max_iterations,
                    "iterations_taken": result.iterations,
                    "final_maximum_change": result.final_delta,
                    "converged": result.converged,
                },
                "files": {
                    "prior": f"{eligibility.value}/prior.csv",
                    "iterations": f"{eligibility.value}/iterations.csv",
                    "manifest": f"{eligibility.value}/manifest.json",
                },
            }
            for eligibility, result in variants.items()
        },
        "comparison": {
            "prior_rows": "comparison/prior_comparison.csv",
            "summary": "comparison/summary.json",
        },
        "runtime": {
            "total_seconds": total_runtime_seconds,
        },
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_root


def _write_variant(
    root: Path,
    result: FixedPointResult,
    *,
    eligibility: BoutEligibility,
    counts: dict[str, int],
    epsilon: float,
    max_iterations: int,
) -> None:
    root.mkdir()
    _write_csv(
        root / "prior.csv",
        (
            {
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "support": result.support[chii],
                "rating": result.priors[chii],
            }
            for chii in sorted(result.priors, key=Chii.ordinal)
        ),
    )
    _write_csv(root / "iterations.csv", (asdict(row) for row in result.iteration_rows))
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "eligibility": eligibility.value,
                "counts": counts,
                "converged": result.converged,
                "iterations": result.iterations,
                "final_delta": result.final_delta,
                "convergence": {
                    "threshold": epsilon,
                    "maximum_iterations": max_iterations,
                    "iterations_taken": result.iterations,
                    "final_maximum_change": result.final_delta,
                    "converged": result.converged,
                },
                "prior_count": len(result.priors),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _comparison_rows(
    p1: FixedPointResult,
    p1_wl: FixedPointResult,
) -> list[dict[str, object]]:
    if set(p1.priors) != set(p1_wl.priors):
        raise ValueError("P1 and P1-WL prior domains differ")
    rows = []
    for chii in sorted(p1.priors, key=Chii.ordinal):
        difference = p1_wl.priors[chii] - p1.priors[chii]
        rows.append(
            {
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "division": _division(chii),
                "support_p1": p1.support[chii],
                "support_p1_wl": p1_wl.support[chii],
                "p1_rating": p1.priors[chii],
                "p1_wl_rating": p1_wl.priors[chii],
                "difference": difference,
                "absolute_difference": abs(difference),
            }
        )
    return rows


def _comparison_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    differences = [float(row["difference"]) for row in rows]
    absolute = [abs(value) for value in differences]
    by_division = {}
    for division in sorted({str(row["division"]) for row in rows}):
        selected = [
            float(row["difference"])
            for row in rows
            if row["division"] == division
        ]
        by_division[division] = _difference_stats(selected)
    return {
        **_difference_stats(differences),
        "changed_prior_count": sum(value != 0.0 for value in absolute),
        "by_division": by_division,
    }


def _difference_stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "mean_absolute": 0.0,
            "rms": 0.0,
            "maximum_absolute": 0.0,
        }
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "mean_absolute": sum(abs(value) for value in values) / len(values),
        "rms": math.sqrt(sum(value * value for value in values) / len(values)),
        "maximum_absolute": max(abs(value) for value in values),
    }


def _division(chii: Chii) -> str:
    return "Makuuchi" if isinstance(chii.level, MSD) else chii.level.name.capitalize()


def _write_csv(path: Path, rows) -> None:
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration as error:
        raise ValueError(f"Cannot write empty comparison artifact: {path}") from error
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM")
    try:
        return Date.from_ints(int(match.group(1)), int(match.group(2)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _selected_history(history: History, start: Date, end: Date | None) -> History:
    selected = History(
        {
            date: history[date]
            for date in sorted(history)
            if date >= start and (end is None or date <= end)
        }
    )
    if not selected:
        raise ValueError("Selected P1-WL interval contains no represented basho")
    return make_oracle(selected, collapse_mode="annotation_only").history


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use this annotated History zip instead of the live store.",
    )
    parser.add_argument("--start", type=_parse_date, default=ELO89_START)
    parser.add_argument("--end", type=_parse_date)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--epsilon", type=float, default=10.0)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "New comparison directory. Defaults to a timestamped directory "
            f"under {DEFAULT_OUTPUT_PARENT}."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    full_history = load_history(args.history_zip)
    history = _selected_history(full_history, args.start, args.end)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = args.output or DEFAULT_OUTPUT_PARENT / f"p1-wl-comparison_{stamp}"
    if args.history_zip is None:
        source: dict[str, object] = {"kind": "live store"}
    else:
        path = args.history_zip.resolve()
        if path.suffix.lower() != ".zip":
            path = path.with_suffix(".zip")
        source = {
            "kind": "annotated History zip",
            "path": str(path),
            "sha256": _sha256(path),
        }
    root = run_comparison(
        history,
        output_root=output,
        k_config_path=args.k_config,
        epsilon=args.epsilon,
        max_iterations=args.max_iterations,
        history_source=source,
    )
    print(f"Output: {root.resolve()}")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for name, variant in manifest["variants"].items():
        convergence = variant["convergence"]
        print(
            f"[{name}] convergence threshold: "
            f"{convergence['threshold']:.6f}; iterations taken: "
            f"{convergence['iterations_taken']}; final maximum change: "
            f"{convergence['final_maximum_change']:.6f}; converged: "
            f"{convergence['converged']}",
        )
    print(f"Total run time: {manifest['runtime']['total_seconds']:.3f} seconds")
    converged = all(
        variant["converged"] for variant in manifest["variants"].values()
    )
    if not converged:
        failures = ", ".join(
            f"{name} (delta={variant['final_delta']:.6f})"
            for name, variant in manifest["variants"].items()
            if not variant["converged"]
        )
        print(
            "ERROR: comparison is invalid because the following fits did not "
            f"converge: {failures}",
        )
    return 0 if converged else 2


if __name__ == "__main__":
    raise SystemExit(main())
