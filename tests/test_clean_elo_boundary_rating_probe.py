import csv
import json
from pathlib import Path

from src.analysis.clean_elo.boundary_rating_probe import (
    BoundaryRatingProbeResult,
    analyse_boundary_curve,
    probe_boundary_ratings,
    write_outputs,
)
from src.analysis.clean_elo.rating_probe import RunningStats
from src.analysis.clean_elo.simulate import SimulationResult
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from test_clean_elo_index_probe import _probe_history


def test_probe_places_sanyaku_and_maegashira_on_same_boundary_axis() -> None:
    history, date = _probe_history()

    result = probe_boundary_ratings(history, date)

    assert result.slot_stats[1].n == 1
    assert result.slot_stats[2].n == 1
    assert result.paired_group_stats[1].n == 2
    assert sum(item.n for item in result.paired_group_stats.values()) == 2


def test_curve_analysis_and_outputs(tmp_path: Path) -> None:
    group_stats = {
        3: _stats(1890.0, 1900.0, 1910.0),
        2: _stats(1940.0, 1950.0, 1960.0),
        1: _stats(1990.0, 2000.0, 2010.0),
    }
    result = BoundaryRatingProbeResult(
        start_date=Date(Year(1989), Month(1)),
        tail_groups=3,
        simulation=SimulationResult(target_mean=1517.0),
        slot_stats={},
        paired_group_stats=group_stats,
        missing_banzuke_occurrences=0,
    )

    curve = analyse_boundary_curve(
        result,
        bootstrap_samples=99,
        random_seed=5,
    )

    assert curve.ordered_distances == (3, 2, 1)
    assert curve.endpoint_reversal == 100.0
    assert curve.monotonicity.p_value <= 0.05

    outputs = write_outputs(
        result=result,
        curve=curve,
        output_root=tmp_path,
    )
    assert outputs.chart_html.exists()
    chart = outputs.chart_html.read_text(encoding="utf-8")
    assert "plotly.js-dist-min@2.35.2" in chart
    assert '"type":"category"' in chart
    assert '"error_y":' in chart

    with outputs.curve_summary_csv.open(
        newline="", encoding="utf-8"
    ) as stream:
        summary = next(csv.DictReader(stream))
    assert summary["first_group"] == "top_bottom_3"
    assert summary["last_group"] == "top_bottom_1"
    assert summary["endpoint_reversal"] == "100.000000000"

    manifest = json.loads(
        outputs.manifest_json.read_text(encoding="utf-8")
    )
    assert manifest["coordinates"]["paired_group"].startswith(
        "ceil(raw_slot / 2)"
    )


def _stats(*values: float) -> RunningStats:
    result = RunningStats()
    for value in values:
        result.add(value)
    return result
