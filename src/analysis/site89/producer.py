"""Produce one complete post-1988 Elo-89 site-data bundle."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.analysis.elo89 import Elo89Artifacts, produce_elo89
from src.infra.get_bios.api import load_bio_store
from src.infra.torikumi import Future
from src.sumo_core.History import History

from .banzuke_changes import produce_banzuke_changes
from .basho_results import produce_basho_results
from .career_comparisons import produce_career_comparisons
from .highest_rating import produce_highest_rating
from .model_independent import produce_model_independent
from .rating_changes import produce_rating_changes
from .rikishi_bio_data import produce_rikishi_bio_data
from .standings import produce_standings
from .typical_rating_values import produce_typical_rating_values
from .torikumi import produce_torikumi
from .win_probability import produce_win_probability_by_standing


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/site89_bundle")
DEFAULT_BANZUKE_SOURCE = Path("files/output/bcr")


def produce_site89_bundle(
    *,
    history: History,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    history_source: str = "provided History",
    banzuke_source_root: Path = DEFAULT_BANZUKE_SOURCE,
    future: Future | None = None,
) -> Path:
    dates = sorted(history)
    if not dates or str(dates[0]) != "1989/01":
        raise ValueError("The site89 production History must begin at 1989/01")
    if output_root.exists():
        shutil.rmtree(output_root)
    site_root = output_root / "site"
    work_root = output_root / "sources"
    site_root.mkdir(parents=True)

    elo_root = work_root / "elo89"
    produce_elo89(
        history=history,
        output_root=elo_root,
        history_source=history_source,
    )
    ratings = Elo89Artifacts.load(elo_root)
    current_date = dates[-1]
    current_cutoff = history[current_date].summary.last_defined()
    if future is None:
        future = Future(
            date=current_date,
            completed_through=current_cutoff,
            days=(),
            generated_at=datetime.now(timezone.utc),
        )
    artifacts = {
        "torikumi": produce_torikumi(
            history=history,
            future=future,
            ratings=ratings,
            output_root=site_root / "current-sumo/torikumi/data",
        )
    }
    artifacts.update(
        produce_model_independent(
            history=history,
            work_root=work_root / "model-independent",
            site_root=site_root,
        )
    )

    artifacts["basho_results_browser"] = produce_basho_results(
        history=history,
        ratings=ratings,
        output_root=site_root / "sumo-history/basho-results/data",
    )
    artifacts["career_comparisons"] = produce_career_comparisons(
        history=history,
        ratings=ratings,
        output_root=site_root / "rikishi/career-comparisons/data",
    )
    artifacts["rating_changes"] = produce_rating_changes(
        history=history,
        ratings=ratings,
        output_root=site_root / "current-sumo/rating-changes/data",
    )
    artifacts["highest_rating"] = (
        produce_highest_rating(
            history=history,
            ratings=ratings,
            output_root=site_root / "sumo-history/records/highest-rating/data",
        ),
    )
    artifacts["banzuke_changes"] = produce_banzuke_changes(
        history=history,
        structural_source_root=banzuke_source_root,
        ratings=ratings,
        output_root=site_root / "current-sumo/banzuke-changes",
    )
    artifacts["typical_rating_values"] = (
        produce_typical_rating_values(
            ratings=ratings,
            output_root=site_root / "ratings-models/rating-and-rank/typical-rating-values/data",
        ),
    )
    artifacts["win_probability_by_standing"] = produce_win_probability_by_standing(
        history=history,
        ratings=ratings,
        output_root=site_root / "ratings-models/observed-vs-modelled/win-probability-by-standing/data",
    )
    artifacts["standings_by_wins"] = produce_standings(
        history=history,
        output_root=site_root / "current-sumo/standings-by-wins/data",
    )
    artifacts["rikishi_bio_data"] = (
        produce_rikishi_bio_data(
            history=history,
            bios=load_bio_store(),
            output_root=site_root / "rikishi/bio-data/data",
        ),
    )

    expected = {
        "banzuke_changes", "banzuke_division_by_era", "basho_results_browser",
        "career_comparisons", "career_length", "division_stability", "finish_by_chii",
        "first_chii_appearance", "highest_rating", "longest_careers",
        "fastest_risers",
        "makuuchi_rank_by_era", "most_career_losses", "most_career_wins",
        "most_consecutive_bouts", "rank_at_retirement", "rating_changes",
        "rikishi_bio_data", "standings_by_wins", "torikumi", "typical_rating_values", "win_probability_by_standing",
    }
    if set(artifacts) != expected:
        raise AssertionError(f"Incomplete site89 artifact set: {sorted(set(artifacts) ^ expected)}")
    producer_names = {key: "src.analysis.site89.model_independent" for key in expected}
    producer_names.update(
        {
            "banzuke_changes": "src.analysis.site89.banzuke_changes",
            "basho_results_browser": "src.analysis.site89.basho_results",
            "career_comparisons": "src.analysis.site89.career_comparisons",
            "highest_rating": "src.analysis.site89.highest_rating",
            "longest_careers": "src.analysis.site89.longest_careers",
            "fastest_risers": "src.analysis.fastest.milestone_matrix",
            "rating_changes": "src.analysis.site89.rating_changes",
            "rikishi_bio_data": "src.analysis.site89.rikishi_bio_data",
            "standings_by_wins": "src.analysis.site89.standings",
            "torikumi": "src.analysis.site89.torikumi",
            "typical_rating_values": "src.analysis.site89.typical_rating_values",
            "win_probability_by_standing": "src.analysis.site89.win_probability",
        }
    )
    manifest = {
        "schema_version": 1,
        "model_id": "elo-89",
        "history": {
            "source": history_source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
        },
        "rating_run": "sources/elo89/manifest.json",
        "artifacts": [
            {
                "id": artifact_id,
                "producer": producer_names[artifact_id],
                "files": [path.relative_to(site_root).as_posix() for path in paths],
            }
            for artifact_id, paths in sorted(artifacts.items())
        ],
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return output_root
