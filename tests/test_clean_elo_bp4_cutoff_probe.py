import csv
import json
from pathlib import Path

from src.analysis.clean_elo.bp4_cutoff_probe import (
    collect_bp4_ratings,
    filter_tail_bouts,
    find_violations,
    included_indices,
    run_cutoff,
    run_cutoff_series,
    write_outputs,
)
from src.analysis.clean_elo.rating_probe import RunningStats
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
from src.sumo_core.Summary import (
    BoutResult,
    DailyResults,
    ResultLookup,
    Summary,
)


def test_included_indices_follow_bp4_sequence() -> None:
    indices = included_indices(4)

    assert [index.display for index in indices] == [
        "Y",
        "O",
        "S",
        "K",
        "M1",
        "M2",
        "M3",
    ]


def test_filter_removes_selected_tail_without_replacement() -> None:
    history, date = _cutoff_history()

    baseline, baseline_removed = filter_tail_bouts(
        history,
        start_date=date,
        first_excluded_m=19,
    )
    filtered, removed = filter_tail_bouts(
        history,
        start_date=date,
        first_excluded_m=18,
    )

    assert baseline is history
    assert baseline_removed == 0
    assert removed == 1
    assert _bout_count(filtered[date]) == 11


def test_cutoff_counts_adjacent_increases() -> None:
    indices = included_indices(3)
    means = [2000.0, 1900.0, 1800.0, 1700.0, 1600.0, 1650.0]
    ratings = {
        index: _stats(mean)
        for index, mean in zip(indices, means)
    }

    violations = find_violations(indices, ratings)

    assert len(violations) == 1
    assert violations[0].stronger_index.display == "M1"
    assert violations[0].weaker_index.display == "M2"
    assert violations[0].increase == 50.0


def test_runner_and_wide_outputs(tmp_path: Path) -> None:
    history, date = _cutoff_history()

    result = run_cutoff_series(
        history,
        date,
        first_cutoff=19,
        last_cutoff=18,
    )
    outputs = write_outputs(result, output_root=tmp_path)

    assert [item.first_excluded_m for item in result.cutoffs] == [19, 18]
    assert result.cutoffs[0].removed_bout_count == 0
    assert result.cutoffs[1].removed_bout_count == 1

    with outputs.ratings_csv.open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["first_excluded_m"] == "19"
    assert rows[0]["M18"]
    assert rows[1]["first_excluded_m"] == "18"
    assert rows[1]["M17"]
    assert rows[1]["M18"] == ""

    with outputs.index_ordinals_csv.open(
        newline="", encoding="utf-8"
    ) as stream:
        ordinal_rows = list(csv.DictReader(stream))
    assert next(
        row for row in ordinal_rows if row["index"] == "M18"
    )["index_ordinal"]

    manifest = json.loads(
        outputs.manifest_json.read_text(encoding="utf-8")
    )
    assert manifest["cutoffs"] == [19, 18]
    assert manifest["count_absences"] is False


def test_single_cutoff_collects_only_retained_sequence() -> None:
    history, date = _cutoff_history()

    result = run_cutoff(history, date, first_excluded_m=18)

    assert "M18" not in {
        index.display for index in result.ratings
    }
    assert result.removed_bout_count == 1


def _cutoff_history() -> tuple[History, Date]:
    rank_names = ["Y1e", "O1e", "S1e", "K1e"] + [
        f"M{number}e" for number in range(1, 19)
    ]
    rikishi = [RikId(value) for value in range(1, len(rank_names) + 1)]
    ranks = dict(zip(rikishi, rank_names))
    bouts = [
        _bout(rikishi[index], rikishi[index + 1])
        for index in range(0, len(rikishi) - 1, 2)
    ]
    bouts.append(_bout(rikishi[-3], rikishi[-2]))
    days = {}
    for day_number, bout in enumerate(bouts, start=1):
        pair = Pair(bout.rikishi1, bout.rikishi2)
        lookup = ResultLookup({pair: bout})
        days[Day(day_number)] = DailyResults(
            torikumi=Torikumi(lookup.keys()),
            results_lookup=lookup,
        )
    banzuke = Banzuke(
        riks=Riks(ranks),
        rikchii=RikChii(
            {
                rikid: Chii.from_str(rank)
                for rikid, rank in ranks.items()
            }
        ),
        rikshik=RikShikona(
            {
                rikid: Shikona(f"Rikishi {int(rikid)}")
                for rikid in ranks
            }
        ),
    )
    date = Date(Year(1989), Month(1))
    return (
        History(
            {
                date: BashoState(
                    banzuke=banzuke,
                    summary=Summary(days),
                )
            }
        ),
        date,
    )


def _bout(winner: RikId, loser: RikId) -> BoutResult:
    return BoutResult(
        rikishi1=winner,
        outcome1=Outcome.W,
        rikishi2=loser,
        outcome2=Outcome.L,
        decision=Kimarite.YORIKIRI,
        symbol=Symbol.W,
    )


def _bout_count(basho: BashoState) -> int:
    return sum(
        len(daily.results_lookup)
        for daily in basho.summary.values()
    )


def _stats(mean: float) -> RunningStats:
    result = RunningStats()
    result.add(mean)
    return result
