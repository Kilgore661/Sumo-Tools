import csv
import json
from pathlib import Path
import re

import pytest

from src.analysis.clean_elo.config import (
    DEFAULT_ELO,
    DEFAULT_FIDE_K_CONFIG_PATH,
    DEFAULT_OUTPUT_ROOT,
)
from src.analysis.clean_elo.policies import (
    ConstantInitialRatingPolicy,
    ConstantKPolicy,
    FileInitialRatingPolicy,
    FideKPolicy,
)
from src.analysis.clean_elo.run import run_clean_elo
from src.analysis.clean_elo.simulate import simulate
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Month,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
    Year,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def test_default_output_root_follows_analysis_package_path() -> None:
    assert DEFAULT_OUTPUT_ROOT == Path("files/output/analysis/clean_elo")


def test_rating_persists_across_an_absent_basho_and_is_reused() -> None:
    a, b, c, d = (RikId(value) for value in range(1, 5))
    january = Date(Year(1989), Month(1))
    march = Date(Year(1989), Month(3))
    may = Date(Year(1989), Month(5))
    history = History(
        {
            january: _basho(
                {a: "J1e", b: "J1w"},
                {1: [_bout(a, b)]},
            ),
            march: _basho(
                {c: "J1e", d: "J1w"},
                {1: [_bout(d, c)]},
            ),
            may: _basho(
                {a: "J1e", c: "J1w"},
                {1: [_bout(a, c)]},
            ),
        }
    )

    result = simulate(
        history=history,
        start_date=january,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
    )

    assert result.basho_ratings[january].final_ratings[a] == pytest.approx(1527.0)
    assert a not in result.basho_ratings[march].final_ratings
    assert result.basho_ratings[may].initial_before_normalisation[a] == pytest.approx(
        1527.0
    )
    assert result.basho_ratings[may].initial_before_normalisation[c] == pytest.approx(
        1507.0
    )
    assert result.basho_ratings[may].initial_normalisation_adjustment == pytest.approx(
        0.0
    )


def test_fide_cross_division_mass_change_is_removed_at_basho_end() -> None:
    yokozuna = RikId(1)
    juryo = RikId(2)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {yokozuna: "Y1e", juryo: "J1e"},
                {1: [_bout(yokozuna, juryo)]},
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=FideKPolicy.load(DEFAULT_FIDE_K_CONFIG_PATH),
    )

    snapshot = result.basho_ratings[date]
    assert snapshot.final_normalisation_adjustment == pytest.approx(3.75)
    assert sum(snapshot.final_ratings.values()) / 2 == pytest.approx(DEFAULT_ELO)
    assert (
        snapshot.final_ratings[yokozuna] - snapshot.final_ratings[juryo]
    ) == pytest.approx(17.5)


def test_python_api_uses_default_initial_rating_and_fide_k_policy() -> None:
    yokozuna = RikId(1)
    juryo = RikId(2)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {yokozuna: "Y1e", juryo: "J1e"},
                {1: [_bout(yokozuna, juryo)]},
            )
        }
    )

    result = simulate(history=history, start_date=date)

    snapshot = result.basho_ratings[date]
    assert result.target_mean == pytest.approx(DEFAULT_ELO)
    assert snapshot.final_normalisation_adjustment == pytest.approx(3.75)
    assert (
        snapshot.final_ratings[yokozuna] - snapshot.final_ratings[juryo]
    ) == pytest.approx(17.5)


def test_default_policies_rate_an_unranked_maezumo_entrant() -> None:
    ranked = RikId(1)
    unranked = RikId(2)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {ranked: "Jk1e"},
                {1: [_bout(unranked, ranked)]},
            )
        }
    )

    result = simulate(history=history, start_date=date)

    snapshot = result.basho_ratings[date]
    assert snapshot.initial_before_normalisation[unranked] == pytest.approx(
        DEFAULT_ELO
    )
    assert snapshot.final_ratings[unranked] == pytest.approx(DEFAULT_ELO + 17.5)
    assert snapshot.final_ratings[ranked] == pytest.approx(DEFAULT_ELO - 17.5)


def test_start_date_excludes_earlier_basho_completely() -> None:
    a, b, c, d = (RikId(value) for value in range(1, 5))
    january = Date(Year(1989), Month(1))
    march = Date(Year(1989), Month(3))
    history = History(
        {
            january: _basho(
                {a: "J1e", b: "J1w"},
                {1: [_bout(a, b)]},
            ),
            march: _basho(
                {c: "J1e", d: "J1w"},
                {1: [_bout(c, d)]},
            ),
        }
    )

    result = simulate(
        history=history,
        start_date=march,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
    )

    assert set(result.basho_ratings) == {march}
    assert set(result.final_registry) == {c, d}


def test_start_date_includes_equal_numeric_date_from_a_date_subclass() -> None:
    class AlternateDate(Date):
        pass

    a, b = RikId(1), RikId(2)
    history_date = AlternateDate(Year(1989), Month(1))
    requested_date = Date(Year(1989), Month(1))
    history = History(
        {
            history_date: _basho(
                {a: "J1e", b: "J1w"},
                {1: [_bout(a, b)]},
            )
        }
    )

    result = simulate(
        history=history,
        start_date=requested_date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
    )

    assert set(result.basho_ratings) == {history_date}


def test_file_initialisation_sets_target_to_first_basho_initial_mean(
    tmp_path: Path,
) -> None:
    ratings_path = tmp_path / "initial.csv"
    ratings_path.write_text(
        "chii,initial_rating\nY1e,1600\nJ1e,1400\n",
        encoding="utf-8",
    )
    yokozuna = RikId(1)
    juryo = RikId(2)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {yokozuna: "Y1e", juryo: "J1e"},
                {1: [_bout(yokozuna, juryo)]},
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=FileInitialRatingPolicy.load(ratings_path),
        k_policy=ConstantKPolicy(20.0),
    )

    assert result.target_mean == pytest.approx(1500.0)
    assert (
        result.basho_ratings[date].initial_normalisation_adjustment
        == pytest.approx(0.0)
    )
    assert (
        sum(result.basho_ratings[date].final_ratings.values()) / 2
        == pytest.approx(1500.0)
    )


def test_file_initialisation_accepts_existing_ordinal_json_format(
    tmp_path: Path,
) -> None:
    yokozuna_chii = Chii.from_str("Y1e")
    ratings_path = tmp_path / "initial.json"
    ratings_path.write_text(
        json.dumps({str(yokozuna_chii.ordinal()): 1600.0}),
        encoding="utf-8",
    )

    policy = FileInitialRatingPolicy.load(ratings_path)

    assert policy.rating_for(yokozuna_chii) == pytest.approx(1600.0)


def test_default_ignores_fusen_but_rates_results_with_blank_decision(
    tmp_path: Path,
) -> None:
    a, b, c, d, e, f = (RikId(value) for value in range(1, 7))
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {
                    a: "J1e",
                    b: "J1w",
                    c: "Ms1e",
                    d: "Ms1w",
                    e: "Sd1e",
                    f: "Sd1w",
                },
                {
                    1: [_bout(a, b)],
                    2: [_fusen(c, d)],
                    3: [_blank(e, f)],
                },
            )
        }
    )

    result, outputs = run_clean_elo(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        output_root=tmp_path,
    )

    snapshot = result.basho_ratings[date]
    assert set(snapshot.final_ratings) == {a, b, c, d, e, f}
    assert snapshot.final_ratings[c] == pytest.approx(DEFAULT_ELO)
    assert snapshot.final_ratings[d] == pytest.approx(DEFAULT_ELO)
    assert result.ignored_fusen_count == 1
    assert result.rated_bout_count == 2
    assert result.inferred_absence_count == 0

    assert len(outputs.basho_csvs) == 1
    assert outputs.base_output_root == tmp_path
    assert outputs.output_root.parent == tmp_path
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}",
        outputs.output_root.name,
    )
    with outputs.basho_csvs[0].open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert {int(row["rikid"]) for row in rows} == {1, 2, 3, 4, 5, 6}
    assert all(row["chii_ordinal"] for row in rows)
    assert all("recorded_appearances" not in row for row in rows)
    assert all("expected_appearances" not in row for row in rows)
    assert all("inferred_absences" not in row for row in rows)
    assert all("raw_absence_rating_adjustment" not in row for row in rows)

    manifest = json.loads(outputs.manifest_json.read_text(encoding="utf-8"))
    assert manifest["target_mean"] == pytest.approx(DEFAULT_ELO)
    assert manifest["count_absences"] is False
    assert manifest["ignored_fusen_count"] == 1
    assert manifest["inferred_absence_count"] == 0
    assert Path(manifest["run_directory"]) == outputs.output_root

    _, second_outputs = run_clean_elo(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        output_root=tmp_path,
    )
    assert second_outputs.output_root != outputs.output_root
    assert outputs.manifest_json.exists()


def test_count_absences_rates_paired_fusen() -> None:
    winner = RikId(1)
    loser = RikId(2)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {winner: "J1e", loser: "J1w"},
                {1: [_fusen(winner, loser)]},
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        count_absences=True,
    )

    ratings = result.basho_ratings[date].final_ratings
    assert ratings[winner] == pytest.approx(1527.0)
    assert ratings[loser] == pytest.approx(1507.0)
    assert result.rated_bout_count == 1
    assert result.ignored_fusen_count == 0


def test_count_absences_scores_sub_sekitori_basho_shortfall(
    tmp_path: Path,
) -> None:
    active1, active2, kyujo = RikId(1), RikId(2), RikId(3)
    date = Date(Year(1989), Month(1))
    bouts_by_day = {
        day: [_bout(active1, active2)] if day <= 7 else []
        for day in range(1, 16)
    }
    history = History(
        {
            date: _basho(
                {
                    active1: "Ms1e",
                    active2: "Ms1w",
                    kyujo: "Ms2e",
                },
                bouts_by_day,
            )
        }
    )

    result, outputs = run_clean_elo(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        count_absences=True,
        output_root=tmp_path,
    )

    snapshot = result.basho_ratings[date]
    assert snapshot.recorded_appearances[kyujo] == 0
    assert snapshot.expected_appearances[kyujo] == 7
    assert snapshot.inferred_absences[kyujo] == 7
    assert snapshot.absence_rating_adjustments[kyujo] == pytest.approx(-70.0)
    assert result.inferred_absence_count == 7
    assert snapshot.final_ratings[kyujo] == pytest.approx(
        DEFAULT_ELO - 70.0 + 70.0 / 3.0
    )
    assert sum(snapshot.final_ratings.values()) / 3 == pytest.approx(DEFAULT_ELO)

    with outputs.basho_csvs[0].open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows
    assert all("recorded_appearances" in row for row in rows)
    assert all("expected_appearances" in row for row in rows)
    assert all("inferred_absences" in row for row in rows)
    assert all("raw_absence_rating_adjustment" in row for row in rows)


def test_default_does_not_initialize_or_score_opponentless_kyujo() -> None:
    active1, active2, kyujo = RikId(1), RikId(2), RikId(3)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {
                    active1: "Ms1e",
                    active2: "Ms1w",
                    kyujo: "Ms2e",
                },
                {
                    day: [_bout(active1, active2)] if day <= 7 else []
                    for day in range(1, 16)
                },
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
    )

    assert kyujo not in result.final_registry
    assert result.inferred_absence_count == 0


def test_count_absences_detects_missing_sekitori_days() -> None:
    a, b, c, d = (RikId(value) for value in range(1, 5))
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {a: "J1e", b: "J1w", c: "J2e", d: "J2w"},
                {
                    day: (
                        [_bout(a, b), _bout(c, d)]
                        if day > 1
                        else [_bout(a, b)]
                    )
                    for day in range(1, 16)
                },
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        count_absences=True,
    )

    snapshot = result.basho_ratings[date]
    assert snapshot.recorded_appearances[c] == 14
    assert snapshot.expected_appearances[c] == 15
    assert snapshot.inferred_absences[c] == 1
    assert snapshot.absence_rating_adjustments[c] == pytest.approx(-10.0)
    assert snapshot.inferred_absences[d] == 1
    assert result.inferred_absence_count == 2


def test_absences_are_not_inferred_before_day_15_is_available() -> None:
    active1, active2, kyujo = RikId(1), RikId(2), RikId(3)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {
                    active1: "Ms1e",
                    active2: "Ms1w",
                    kyujo: "Ms2e",
                },
                {day: [_bout(active1, active2)] for day in range(1, 8)},
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        count_absences=True,
    )

    assert kyujo not in result.final_registry
    assert result.inferred_absence_count == 0


def test_cross_division_bout_alone_does_not_mark_either_division_complete() -> None:
    juryo, makushita = RikId(1), RikId(2)
    date = Date(Year(1989), Month(1))
    history = History(
        {
            date: _basho(
                {juryo: "J1e", makushita: "Ms1e"},
                {
                    day: [_bout(juryo, makushita)] if day == 1 else []
                    for day in range(1, 16)
                },
            )
        }
    )

    result = simulate(
        history=history,
        start_date=date,
        initial_rating_policy=ConstantInitialRatingPolicy(DEFAULT_ELO),
        k_policy=ConstantKPolicy(20.0),
        count_absences=True,
    )

    snapshot = result.basho_ratings[date]
    assert snapshot.expected_appearances[juryo] == 0
    assert snapshot.expected_appearances[makushita] == 0
    assert result.inferred_absence_count == 0


def _basho(
    ranks: dict[RikId, str],
    bouts_by_day: dict[int, list[BoutResult]],
) -> BashoState:
    banzuke = Banzuke(
        riks=Riks(ranks),
        rikchii=RikChii(
            {
                rikid: Chii.from_str(chii)
                for rikid, chii in ranks.items()
            }
        ),
        rikshik=RikShikona(
            {
                rikid: Shikona(f"Rikishi {int(rikid)}")
                for rikid in ranks
            }
        ),
    )
    summary_days = {}
    for day_value, bouts in bouts_by_day.items():
        lookup = ResultLookup(
            {
                Pair(bout.rikishi1, bout.rikishi2): bout
                for bout in bouts
            }
        )
        summary_days[Day(day_value)] = DailyResults(
            torikumi=Torikumi(lookup),
            results_lookup=lookup,
        )
    return BashoState(
        banzuke=banzuke,
        summary=Summary(summary_days),
    )


def _bout(winner: RikId, loser: RikId) -> BoutResult:
    return BoutResult(
        rikishi1=winner,
        outcome1=Outcome.W,
        rikishi2=loser,
        outcome2=Outcome.L,
        decision=Kimarite.OSHIDASHI,
        symbol=Symbol.W,
    )


def _fusen(winner: RikId, loser: RikId) -> BoutResult:
    return BoutResult(
        rikishi1=winner,
        outcome1=Outcome.FS,
        rikishi2=loser,
        outcome2=Outcome.FP,
        decision="fusen",
        symbol=Symbol.FS,
    )


def _blank(rikishi1: RikId, rikishi2: RikId) -> BoutResult:
    return BoutResult(
        rikishi1=rikishi1,
        outcome1=Outcome.W,
        rikishi2=rikishi2,
        outcome2=Outcome.L,
        decision="blank",
        symbol=Symbol.W,
    )
