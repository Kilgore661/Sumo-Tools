import csv
import math
from pathlib import Path

from src.analysis.clean_elo.index_probe import BinningPolicy
from src.analysis.clean_elo.rating_probe import (
    RunningStats,
    probe_index_ratings,
    write_rating_probe_outputs,
)
from src.sumo_core.History import Date

from test_clean_elo_index_probe import _probe_history


def test_running_stats_and_student_t_interval() -> None:
    stats = RunningStats()
    stats.add(10.0)

    assert stats.n == 1
    assert stats.mean == 10.0
    assert stats.sample_standard_deviation is None
    assert stats.standard_error is None
    assert stats.naive_ci95() is None

    stats.add(14.0)

    assert stats.n == 2
    assert stats.mean == 12.0
    assert math.isclose(
        stats.sample_standard_deviation,
        math.sqrt(8.0),
    )
    assert math.isclose(stats.standard_error, 2.0)
    assert math.isclose(
        stats.naive_margin_of_error,
        25.412409,
        abs_tol=1e-6,
    )
    assert math.isclose(
        stats.relative_margin_of_error,
        25.412409 / 12.0,
        abs_tol=1e-6,
    )
    lower, upper = stats.naive_ci95()
    assert math.isclose(lower, -13.412409, abs_tol=1e-6)
    assert math.isclose(upper, 37.412409, abs_tol=1e-6)


def test_probe_uses_one_start_rating_per_rikishi_basho() -> None:
    history, date = _probe_history()

    result = probe_index_ratings(history, date)

    for policy in BinningPolicy:
        assert sum(
            summary.n
            for summary in result.index_stats[policy].values()
        ) + result.conversion_exception_counts[policy] == 4
    bp1 = result.index_stats[BinningPolicy.BP1]
    m1e = next(index for index in bp1 if index.display == "M1e")
    assert bp1[m1e].n == 1
    assert bp1[m1e].mean == result.simulation.basho_ratings[
        date
    ].initial_after_normalisation[next(
        rikid
        for rikid, chii in history[date].banzuke.rikchii.items()
        if str(chii) == "M1e"
    )]
    assert result.missing_banzuke_occurrences == 1


def test_rating_probe_writes_blank_interval_for_singleton(
    tmp_path: Path,
) -> None:
    history, date = _probe_history()
    result = probe_index_ratings(history, date)

    outputs = write_rating_probe_outputs(result, tmp_path)
    assert outputs.standard_error_relative_margin_html.exists()
    assert outputs.bp4_mean_ci95_html.exists()
    bp4_chart = outputs.bp4_mean_ci95_html.read_text(encoding="utf-8")
    assert "cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2" in bp4_chart
    assert '"type":"category"' in bp4_chart
    assert '"categoryarray":' in bp4_chart
    assert '"range":[' in bp4_chart
    assert '"error_y":' in bp4_chart
    assert '"fill":"tonexty"' not in bp4_chart

    with outputs.index_rating_statistics_csv.open(
        newline="",
        encoding="utf-8",
    ) as stream:
        rows = list(csv.DictReader(stream))
    singleton = next(row for row in rows if row["n"] == "1")
    assert singleton["sample_standard_deviation"] == ""
    assert singleton["standard_error"] == ""
    assert singleton["naive_margin_of_error"] == ""
    assert singleton["naive_relative_margin_of_error"] == ""
    assert singleton["naive_ci95_lower"] == ""
    assert singleton["naive_ci95_upper"] == ""
    assert singleton["naive_ci95_width"] == ""
