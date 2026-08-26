"""Generate the canonical q=400, alpha=1 BKP1 entrant prior."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from ...infra.connect import connect
from ..equelo.expt1.Oracle import make_oracle
from .params import DEFAULT_K_CONFIG, MODEL_BASE, MODEL_Q, load_divisional_k
from .solve import solve


DEFAULT_OUTPUT = Path("files/output/analysis/equelo_bkp1")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history = make_oracle(
        connect(args.start, args.end, use_zip=args.zip),
        collapse_mode="annotation_only",
    ).history
    k_config = args.k_config.resolve()
    result = solve(
        history,
        load_divisional_k(k_config),
        epsilon=args.epsilon,
        max_iterations=args.max_iterations,
        progress=_progress,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    _write_csv(
        args.output / "prior.csv",
        ({
            "chii": str(chii),
            "ordinal": chii.ordinal(),
            "observations": result.support[chii],
            "rating": result.priors[chii],
        } for chii in sorted(result.priors, key=lambda item: item.ordinal())),
    )
    _write_csv(
        args.output / "iterations.csv",
        (asdict(row) for row in result.iteration_rows),
    )
    manifest = {
        "model": "BKP1 entrant-prior producer",
        "start": args.start,
        "end": args.end,
        "q": MODEL_Q,
        "base": MODEL_BASE,
        "recentering_alpha": 1.0,
        "population_policy": "legacy_departure",
        "k_config": str(k_config),
        "k_config_sha256": _sha256(k_config),
        "epsilon": args.epsilon,
        "max_iterations": args.max_iterations,
        "converged": result.converged,
        "iterations": result.iterations,
        "final_delta": result.final_delta,
        "prior_count": len(result.priors),
        "minimum_prior": min(result.priors.values()),
        "maximum_prior": max(result.priors.values()),
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if result.converged else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1989)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--epsilon", type=float, default=10.0)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _progress(row) -> None:
    if row.iteration == 1 or row.iteration % 10 == 0 or row.max_prior_change < 10.0:
        print(
            f"[BKP1] iteration={row.iteration} delta={row.max_prior_change:.6f} "
            f"max={row.max_change_chii} n={row.max_change_observation_count}",
            flush=True,
        )


def _write_csv(path: Path, rows) -> None:
    iterator = iter(rows)
    first = next(iterator)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
