"""Production entry point for Elo-89 artifacts."""

from __future__ import annotations

from pathlib import Path

from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.equelo_population_policy.predict_candidate import load_alpha_prior
from src.sumo_core.History import History

from .output import Elo89OutputPaths, write_elo89_outputs
from .replay import Q, replay_elo89


DEFAULT_PRIOR = Path("files/output/analysis/equelo_bkp1/prior.csv")
DEFAULT_K_CONFIG = Path("files/input/elo_fide.json")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/elo89")


def produce_elo89(
    *,
    history: History,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    prior_path: Path = DEFAULT_PRIOR,
    k_config_path: Path = DEFAULT_K_CONFIG,
    history_source: str = "provided History",
) -> Elo89OutputPaths:
    dates = sorted(history)
    if not dates or str(dates[0]) != "1989/01":
        first = None if not dates else str(dates[0])
        raise ValueError(
            "Elo-89 production requires a History beginning at 1989/01; "
            f"received {first!r}"
        )
    prior, _conversion = load_alpha_prior(prior_path)
    run = replay_elo89(
        history=history,
        start_date=dates[0],
        end_date=dates[-1],
        prior=prior,
        divisional_k=load_divisional_k_fn(k_config_path),
        q=Q,
    )
    return write_elo89_outputs(
        run=run,
        prior=prior,
        output_root=output_root,
        history_source=history_source,
        start_date=dates[0],
        end_date=dates[-1],
        k_config_path=k_config_path,
        q=Q,
    )
