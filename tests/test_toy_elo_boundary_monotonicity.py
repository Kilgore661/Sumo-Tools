import csv
from pathlib import Path

from src.analysis.toy_elo.boundary_monotonicity.experiment import (
    ExperimentConfig,
    build_boundary_groups,
    fit_non_increasing,
    is_non_increasing,
    maximum_reversal,
    run_experiment,
    write_outputs,
)
from src.analysis.toy_elo.evidence_bridge import (
    BridgeSlot,
    EvidenceBridgeProfile,
)


def test_boundary_groups_are_ordered_from_better_to_boundary() -> None:
    config = ExperimentConfig(
        top_size=8,
        bottom_size=4,
        events=1,
        runs=2,
        tail_groups=3,
        group_size=2,
        bootstrap_samples=10,
    )
    groups = build_boundary_groups(config)
    assert [group.players for group in groups] == [
        (2, 3),
        (4, 5),
        (6, 7),
    ]
    assert [group.boundary_distance for group in groups] == [3, 2, 1]


def test_reversal_and_isotonic_helpers() -> None:
    values = [10.0, 8.0, 9.0, 4.0]
    assert maximum_reversal(values) == 1.0
    assert not is_non_increasing(values)
    assert fit_non_increasing(
        values,
        [1.0, 1.0, 1.0, 1.0],
    ) == (10.0, 8.5, 8.5, 4.0)
    assert maximum_reversal([10.0, 9.0, 8.0]) == 0.0
    assert is_non_increasing([10.0, 9.0, 8.0])


def test_small_experiment_writes_both_scenarios(
    tmp_path: Path,
) -> None:
    profile = _profile(tmp_path / "profile.csv", top_size=8)
    config = ExperimentConfig(
        top_size=8,
        bottom_size=4,
        days_per_event=3,
        events=2,
        runs=6,
        q=100.0,
        gap=10.0,
        tail_groups=3,
        group_size=2,
        bootstrap_samples=30,
        historical_endpoint_difference=-1.0,
        historical_maximum_reversal=10.0,
        historical_q=100.0,
        seed=7,
    )
    result = run_experiment(profile=profile, config=config)
    assert [item.summary.scenario for item in result.scenarios] == [
        "evidence_bridge",
        "rank_local_control",
    ]
    assert all(len(item.groups) == 3 for item in result.scenarios)
    assert all(len(item.run_reversals) == 6 for item in result.scenarios)
    assert all(
        earlier > later
        for earlier, later in zip(
            result.hidden_skills,
            result.hidden_skills[1:],
        )
    )
    evidence, control = result.scenarios
    assert evidence.summary.mean_bridge_bouts_per_run_event > 0.0
    assert control.summary.mean_bridge_bouts_per_run_event == 0.0

    outputs = write_outputs(
        result=result,
        profile=profile,
        output_root=tmp_path / "output",
    )
    assert outputs.manifest_json.exists()
    assert outputs.boundary_groups_csv.exists()
    with outputs.scenario_summary_csv.open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert {row["scenario"] for row in rows} == {
        "evidence_bridge",
        "rank_local_control",
    }


def _profile(path: Path, *, top_size: int) -> EvidenceBridgeProfile:
    path.write_text("synthetic profile\n", encoding="utf-8")
    return EvidenceBridgeProfile(
        source_path=path,
        support_threshold=1,
        upper_slots=(
            BridgeSlot(
                player=top_size - 1,
                source_group="M bottom 1",
                probability=1.0,
                scheduled_bout_count=10,
                interdivision_bout_count=10,
            ),
        ),
        lower_slots=(
            BridgeSlot(
                player=top_size,
                source_group="J top 1",
                probability=1.0,
                scheduled_bout_count=10,
                interdivision_bout_count=10,
            ),
        ),
    )
