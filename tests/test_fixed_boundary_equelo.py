import json
from pathlib import Path

from src.analysis.equelo.expt1.params import EloParams
from src.analysis.equelo.boundary_reconciliation import _alignment_metrics
from src.analysis.equelo.fixed_boundary.history import build_supported_history
from src.analysis.equelo.fixed_boundary.model import (
    JMS_BOUNDARY,
    LITERAL_CHII,
    LOWER_BANZUKE,
    MJ_BOUNDARY,
    PriorKey,
    build_prior_world,
    build_jms_prior_world,
)
from src.analysis.equelo.fixed_boundary.output import PLOTLY_CDN, _write_plotly_html
from src.analysis.equelo.fixed_boundary.producer import build_fixed_boundary
from src.analysis.equelo.fixed_boundary.solver import solve_modern_then_combined
from src.analysis.equelo.fixed_jms_boundary.producer import build_fixed_jms_boundary
from src.analysis.equelo.fixed_lower_banzuke.model import (
    build_lower_banzuke_prior_world,
)
from src.analysis.equelo.fixed_lower_banzuke.producer import (
    build_fixed_lower_banzuke,
)
from src.analysis.equelo.fixed_dual_boundary.model import build_dual_boundary_world
from src.analysis.equelo.fixed_dual_boundary.producer import build_fixed_dual_boundary
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_boundary_keys_use_complete_banzuke_structure() -> None:
    first = Date(Year(1989), Month(1))
    second = Date(Year(1989), Month(3))
    history = History({
        first: _basho("Y1e", "M16e", "J1e", "J1w", "Ms1e"),
        second: _basho("Y1e", "M16e", "M16w", "J1e", "J1w", "Ms1e"),
    })

    world = build_prior_world(history)

    assert world.key_by_date_rikishi[first][RikId(2)] == PriorKey(MJ_BOUNDARY, -1)
    assert world.key_by_date_rikishi[second][RikId(2)] == PriorKey(MJ_BOUNDARY, -2)
    assert world.key_by_date_rikishi[second][RikId(3)] == PriorKey(MJ_BOUNDARY, -1)
    assert world.key_by_date_rikishi[second][RikId(4)] == PriorKey(MJ_BOUNDARY, 0)
    assert world.key_by_date_rikishi[second][RikId(5)] == PriorKey(MJ_BOUNDARY, 1)
    assert world.key_by_date_rikishi[second][RikId(6)].kind == LITERAL_CHII

    filtered = build_supported_history(history, world, min_appearances=2)
    assert RikId(1) not in filtered.history[second].banzuke.riks
    assert world.key_by_date_rikishi[second][RikId(2)] == PriorKey(MJ_BOUNDARY, -2)


def test_contextual_fixed_point_converges_on_flat_no_bout_history() -> None:
    first = Date(Year(1989), Month(1))
    second = Date(Year(1990), Month(1))
    history = History({
        first: _basho("Y1e", "M16e", "J1e", "J1w", "Ms1e"),
        second: _basho("Y1e", "M16e", "J1e", "J1w", "Ms1e"),
    })
    world = build_prior_world(history)

    result = solve_modern_then_combined(
        history=history,
        world=world,
        params=EloParams.constant(b=1517, q=900, k_value=35),
        base=1517,
        epsilon=0.001,
        max_iter=10,
        modern_start_year=1989,
        modern_end_year=1990,
    )

    assert result.modern.converged
    assert result.combined.converged
    assert set(result.combined.ratings) == world.keys
    assert set(result.combined.ratings.values()) == {1517.0}


def test_jms_keys_follow_contemporaneous_juryo_bottom() -> None:
    first = Date(Year(1989), Month(1))
    second = Date(Year(1989), Month(3))
    history = History({
        first: _basho("J1e", "J1w", "Ms1e", "Ms1w"),
        second: _basho("J1e", "J1w", "J2e", "J2w", "Ms1e", "Ms1w"),
    })

    world = build_jms_prior_world(history)

    assert world.key_by_date_rikishi[first][RikId(1)] == PriorKey(JMS_BOUNDARY, -2)
    assert world.key_by_date_rikishi[second][RikId(1)] == PriorKey(JMS_BOUNDARY, -4)
    assert world.key_by_date_rikishi[first][RikId(3)] == PriorKey(JMS_BOUNDARY, 0)
    assert world.key_by_date_rikishi[second][RikId(5)] == PriorKey(JMS_BOUNDARY, 0)


def test_lower_banzuke_keys_continue_without_division_resets() -> None:
    date = Date(Year(1989), Month(1))
    history = History({
        date: _basho(
            "J1e", "J1w", "Ms1e", "Ms1w", "Sd1e", "Sd1w", "Jd1e", "Jk1e"
        ),
    })

    world = build_lower_banzuke_prior_world(history)
    keys = world.key_by_date_rikishi[date]

    assert {keys[RikId(index)].kind for index in range(1, 9)} == {LOWER_BANZUKE}
    assert keys[RikId(1)].value == -2
    assert keys[RikId(2)].value == -1
    assert keys[RikId(3)].value == 0
    assert keys[RikId(4)].value == 1
    assert keys[RikId(5)].value == 2
    assert keys[RikId(6)].value == 3
    assert keys[RikId(7)].value == 4
    assert keys[RikId(8)].value == 5


def test_dual_boundary_assigns_juryo_to_nearer_boundary_and_splits_tie() -> None:
    date = Date(Year(1989), Month(1))
    history = History({
        date: _basho("M16e", "J1e", "J1w", "J2e", "Ms1e"),
    })

    world = build_dual_boundary_world(history)
    top = world.assignments_by_date_rikishi[date][RikId(2)]
    middle = world.assignments_by_date_rikishi[date][RikId(3)]
    bottom = world.assignments_by_date_rikishi[date][RikId(4)]

    assert [(item.key.kind, item.weight) for item in top] == [(MJ_BOUNDARY, 1.0)]
    assert {(item.key.kind, item.weight) for item in middle} == {
        (MJ_BOUNDARY, 0.5),
        (JMS_BOUNDARY, 0.5),
    }
    assert [(item.key.kind, item.weight) for item in bottom] == [(JMS_BOUNDARY, 1.0)]


def test_dual_boundary_linear_weights_are_fixed_by_relative_position() -> None:
    date = Date(Year(1989), Month(1))
    history = History({
        date: _basho("J1e", "J1w", "J2e", "J2w"),
    })

    world = build_dual_boundary_world(history, juryo_weighting="linear")
    second = world.assignments_by_date_rikishi[date][RikId(2)]
    third = world.assignments_by_date_rikishi[date][RikId(3)]

    assert [round(item.weight, 6) for item in second] == [0.666667, 0.333333]
    assert [round(item.weight, 6) for item in third] == [0.333333, 0.666667]


def test_plotly_output_is_cdn_backed_and_responsive(tmp_path: Path) -> None:
    path = _write_plotly_html(
        tmp_path / "chart.html",
        traces=[{"type": "scatter", "x": [0], "y": [1]}],
        layout={"title": {"text": "Test chart"}},
    )

    markup = path.read_text(encoding="utf-8")
    assert PLOTLY_CDN in markup
    assert "responsive: true" in markup
    assert 'name="viewport"' in markup


def test_boundary_alignment_uses_only_one_common_shift() -> None:
    rows = [
        {
            "mj_rating": 1900.0,
            "jms_aligned_rating": 1898.0,
            "residual_mj_minus_jms": 2.0,
            "relative_position": 0.0,
        },
        {
            "mj_rating": 1800.0,
            "jms_aligned_rating": 1802.0,
            "residual_mj_minus_jms": -2.0,
            "relative_position": 1.0,
        },
    ]

    metrics = _alignment_metrics(rows, shift=7.0)

    assert metrics["additive_shift_to_jms"] == 7.0
    assert metrics["mean_residual"] == 0.0
    assert metrics["root_mean_square_residual"] == 2.0


def test_experimental_producer_writes_isolated_artifacts(tmp_path: Path) -> None:
    earlier = Date(Year(1988), Month(11))
    first = Date(Year(1989), Month(1))
    second = Date(Year(1990), Month(1))
    history = History({
        earlier: _basho("Y1e", "M22e", "J1e", "J1w", "Ms1e"),
        first: _basho("Y1e", "M18e", "J1e", "J1w", "Ms1e"),
        second: _basho("Y1e", "M18e", "J1e", "J1w", "Ms1e"),
    })

    outputs = build_fixed_boundary(
        raw_history=history,
        output_root=tmp_path / "runs",
        min_appearances=1,
        epsilon=0.001,
        max_iter=10,
        start_year=1989,
        end_year=1990,
    )

    assert outputs.prior_map_csv.exists()
    assert outputs.literal_control_prior_map_csv.exists()
    assert outputs.day_end_ratings_json.exists()
    assert outputs.manifest_json.exists()
    assert outputs.comparison_outputs["boundary_chart_html"].exists()
    assert outputs.comparison_outputs["all_chii_chart_html"].exists()
    comparison = outputs.comparison_outputs["makuuchi_chii_comparison_csv"].read_text()
    assert "M18e" in comparison
    assert "M22e" not in comparison
    all_chii_markup = outputs.comparison_outputs["all_chii_chart_html"].read_text()
    assert '"type":"category"' in all_chii_markup
    assert "M18e" in all_chii_markup


def test_jms_producer_writes_boundary_comparisons(tmp_path: Path) -> None:
    first = Date(Year(1989), Month(1))
    second = Date(Year(1990), Month(1))
    history = History({
        first: _basho("M1e", "J1e", "J1w", "Ms1e", "Ms1w", "Sd1e"),
        second: _basho("M1e", "J1e", "J1w", "Ms1e", "Ms1w", "Sd1e"),
    })

    outputs = build_fixed_jms_boundary(
        raw_history=history,
        output_root=tmp_path / "jms-runs",
        min_appearances=1,
        epsilon=0.001,
        max_iter=10,
        start_year=1989,
        end_year=1990,
    )

    assert outputs.prior_map_csv.exists()
    assert outputs.comparison_outputs["boundary_chart_html"].exists()
    assert outputs.comparison_outputs["chii_chart_html"].exists()


def test_lower_banzuke_producer_writes_index_and_chii_comparisons(
    tmp_path: Path,
) -> None:
    first = Date(Year(1989), Month(1))
    second = Date(Year(1990), Month(1))
    history = History({
        first: _basho("M1e", "J1e", "J1w", "Ms1e", "Sd1e", "Jd1e", "Jk1e"),
        second: _basho("M1e", "J1e", "J1w", "Ms1e", "Sd1e", "Jd1e", "Jk1e"),
    })

    outputs = build_fixed_lower_banzuke(
        raw_history=history,
        output_root=tmp_path / "lower-runs",
        min_appearances=1,
        epsilon=0.001,
        max_iter=10,
        start_year=1989,
        end_year=1990,
    )

    assert outputs.prior_map_csv.exists()
    assert outputs.comparison_outputs["index_chart_html"].exists()
    assert outputs.comparison_outputs["chii_chart_html"].exists()
    chii_csv = outputs.comparison_outputs["chii_comparison_csv"].read_text()
    assert "Ms1e" in chii_csv
    assert "Jd1e" in chii_csv


def test_dual_boundary_producer_writes_pair_chart(tmp_path: Path) -> None:
    earlier = Date(Year(1958), Month(1))
    first = Date(Year(1989), Month(1))
    second = Date(Year(1990), Month(1))
    history = History({
        earlier: _basho("M1e", "M1w", "J1e", "J1w", "J2e", "J2w", "Ms1e", "Ms1w", "Sd1e"),
        first: _basho("M1e", "M1w", "J1e", "J1w", "J2e", "J2w", "Ms1e", "Ms1w", "Sd1e"),
        second: _basho("M1e", "M1w", "J1e", "J1w", "J2e", "J2w", "Ms1e", "Ms1w", "Sd1e"),
    })

    outputs = build_fixed_dual_boundary(
        raw_history=history,
        output_root=tmp_path / "dual-runs",
        min_appearances=1,
        epsilon=0.001,
        max_iter=10,
        start_year=1958,
        end_year=1990,
        juryo_weighting="linear",
        modern_start_year=1989,
    )

    assert outputs.prior_map_csv.exists()
    assert outputs.comparison_outputs["focus_pair_chart_html"].exists()
    manifest = json.loads(outputs.manifest_json.read_text(encoding="utf-8"))
    assert manifest["solve_scope"] == {
        "modern_start_year": 1989,
        "combined_start_year": 1958,
    }
    assert manifest["solve"]["joint"]["modern"]["iterations"] == 1
    assert manifest["solve"]["joint"]["combined"]["iterations"] == 1
    assert manifest["solve"]["literal_control"]["modern"]["iterations"] == 1
    assert manifest["solve"]["literal_control"]["combined"]["iterations"] == 1


def _basho(*chiis: str) -> BashoState:
    rikids = [RikId(index) for index in range(1, len(chiis) + 1)]
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikids),
            rikchii=RikChii({
                rikid: Chii.from_str(chii)
                for rikid, chii in zip(rikids, chiis)
            }),
            rikshik=RikShikona({
                rikid: Shikona(f"Rikishi {int(rikid)}")
                for rikid in rikids
            }),
        ),
        summary=Summary({}),
    )
