import json

from src.analysis.prediction.bouts import BoutSelection
from src.analysis.prediction.definition import Proposal1Definition
from src.analysis.prediction.division_initialisation import (
    DivisionInitialisationResult,
    _division_initial_ratings,
    build_division_prior,
)
from src.analysis.prediction.division_initialisation_output import (
    write_division_initialisation_outputs,
)
from src.analysis.prediction.output import HistorySource
from src.analysis.prediction.randomised_prior import (
    CumulativeScore,
    PreparedPlaceboBouts,
    PriorValue,
    SCOPES,
)
from src.sumo_core.BasicEnums import Division
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


def test_division_prior_is_the_unweighted_mean_of_chii_values() -> None:
    prior = _prior_values()

    rows = {row.division: row for row in build_division_prior(prior)}

    assert rows[Division.MAKUUCHI].initial_rating == 2000.0
    assert rows[Division.MAKUUCHI].chii_count == 2
    assert rows[Division.JURYO].initial_rating == 1700.0
    assert rows[Division.JONOKUCHI].initial_rating == 900.0


def test_division_initialization_uses_actual_division_and_weakest_fallback() -> None:
    prior = build_division_prior(_prior_values())
    prepared = PreparedPlaceboBouts(
        selection=BoutSelection((), 0, 0, 0, 0),
        bouts=(),
        first_chii_by_rikishi={
            RikId(1): Chii.from_str("Y1e"),
            RikId(2): Chii.from_str("M1e"),
            RikId(3): Chii.from_str("J1e"),
        },
        unranked_initial_rikishi=(RikId(4),),
    )

    ratings = _division_initial_ratings(prepared, prior)

    assert ratings[RikId(1)] == ratings[RikId(2)] == 2000.0
    assert ratings[RikId(3)] == 1700.0
    assert ratings[RikId(4)] == 900.0


def test_proposal_5_outputs_include_comparators_and_serializable_manifest(
    tmp_path,
) -> None:
    dates = tuple(
        Date(Year(1989), Month(month)) for month in (1, 3, 5, 7, 9)
    )
    basho_counts = (6, 12, 30, 60, 61)

    def scores(offset: float) -> tuple[CumulativeScore, ...]:
        return tuple(
            CumulativeScore(
                scope=scope,
                end_date=date,
                basho_count=count,
                bout_count=count * 10,
                mean_log_loss=0.70 + offset,
                mean_brier_score=0.25 + offset,
            )
            for scope in SCOPES
            for date, count in zip(dates, basho_counts)
        )

    prior_values = _prior_values()
    prepared = PreparedPlaceboBouts(
        selection=BoutSelection((), 0, 0, 0, 0),
        bouts=(),
        first_chii_by_rikishi={},
        unranked_initial_rikishi=(),
    )
    result = DivisionInitialisationResult(
        definition=Proposal1Definition(end_date=dates[-1]),
        prior_values=prior_values,
        division_prior=build_division_prior(prior_values),
        prepared=prepared,
        equal_scores=scores(0.0),
        genuine_scores=scores(-0.01),
        division_scores=scores(-0.02),
    )
    placebo = tuple(
        {
            "scope": row.scope,
            "date": str(row.end_date),
            "within_division_random_log_p05": "0.67",
            "within_division_random_log_median": "0.68",
            "within_division_random_log_p95": "0.69",
            "within_division_random_brier_p05": "0.22",
            "within_division_random_brier_median": "0.23",
            "within_division_random_brier_p95": "0.24",
        }
        for row in result.equal_scores
    )
    source = HistorySource("test", "abc")

    write_division_initialisation_outputs(
        result,
        placebo,
        tmp_path,
        source,
        source,
        source,
    )

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["division_prior"][0]["division"] == "MAKUUCHI"
    chart = (tmp_path / "division_initialisation.html").read_text(encoding="utf-8")
    assert "Division only" in chart
    assert "Within-division random median" in chart


def _prior_values() -> tuple[PriorValue, ...]:
    return tuple(sorted(
        (
            PriorValue(Chii.from_str("Y1e"), 2100.0),
            PriorValue(Chii.from_str("M1e"), 1900.0),
            PriorValue(Chii.from_str("J1e"), 1700.0),
            PriorValue(Chii.from_str("Ms1e"), 1500.0),
            PriorValue(Chii.from_str("Sd1e"), 1300.0),
            PriorValue(Chii.from_str("Jd1e"), 1100.0),
            PriorValue(Chii.from_str("Jk1e"), 900.0),
        ),
        key=lambda row: row.chii,
    ))
