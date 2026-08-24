from __future__ import annotations

import csv
import json
from math import isclose

from src.analysis.forgetting.toy.constant_start_ensemble import (
    aggregate_event_rows,
    aggregate_landmarks,
    run_constant_start_ensemble,
    run_inverted_start_ensemble,
)
from src.analysis.forgetting.toy.elo import expected_score, replay_history
from src.analysis.forgetting.toy.experiment import run_development_experiment
from src.analysis.forgetting.toy.history import (
    ToyBout,
    ToyHistory,
    generate_history,
    read_history,
    round_robin_pairs,
    write_history,
)
from src.analysis.forgetting.toy.metrics import (
    build_event_metrics,
    centred_state_distance,
    forecast_distance,
)
from src.analysis.forgetting.toy.model import ToyWorld
from src.analysis.forgetting.toy.random_start_ensemble import (
    generate_random_initialisations,
    run_random_start_batch,
)
from src.analysis.forgetting.toy.results_table import (
    ExtractionContract,
    ModelRun,
    extract_model_results,
    write_results_table,
)
from src.analysis.forgetting.toy.true_start_ensemble import (
    aggregate_replicate_events,
    run_true_start_ensemble,
)


def test_default_world_has_declared_centred_latent_skills() -> None:
    world = ToyWorld()

    assert world.latent_skills == (
        180.0,
        140.0,
        100.0,
        60.0,
        20.0,
        -20.0,
        -60.0,
        -100.0,
        -140.0,
        -180.0,
    )
    assert sum(world.latent_skills) == 0
    assert world.flat_initial_ratings == (0.0,) * 10
    assert world.pairs_per_event == 45


def test_generated_history_is_reproducible_and_complete() -> None:
    world = ToyWorld(player_count=4)

    first = generate_history(world=world, events=3, seed=17)
    second = generate_history(world=world, events=3, seed=17)

    assert first == second
    assert len(first.bouts) == 18
    expected_pairs = set(round_robin_pairs(4))
    for event in range(1, 4):
        event_rows = [row for row in first.bouts if row.event == event]
        assert {(row.player_a, row.player_b) for row in event_rows} == expected_pairs
    for row in first.bouts:
        assert row.a_won == (row.random_draw < row.true_probability_a_wins)


def test_persisted_history_round_trips_exactly(tmp_path) -> None:
    world = ToyWorld(player_count=4)
    generated = generate_history(world=world, events=2, seed=23)
    path = tmp_path / "history.csv"

    write_history(path, generated)
    loaded = read_history(
        path,
        master_seed=generated.master_seed,
        schedule_seed=generated.schedule_seed,
        outcome_seed=generated.outcome_seed,
        events=generated.events,
        player_count=generated.player_count,
    )

    assert loaded == generated


def test_replays_share_outcomes_and_preserve_each_initial_mean() -> None:
    world = ToyWorld(player_count=4)
    history = generate_history(world=world, events=5, seed=3)
    true_run = replay_history(
        history,
        label="true",
        initial_ratings=world.latent_skills,
        q=world.q,
        k=world.k,
    )
    shifted_flat = replay_history(
        history,
        label="shifted_flat",
        initial_ratings=(1500.0,) * world.player_count,
        q=world.q,
        k=world.k,
    )

    assert [row.a_won for row in true_run.forecasts] == [
        row.a_won for row in shifted_flat.forecasts
    ]
    for snapshot in true_run.snapshots:
        assert isclose(sum(snapshot.ratings), sum(world.latent_skills), abs_tol=1e-10)
    for snapshot in shifted_flat.snapshots:
        assert isclose(sum(snapshot.ratings), 6000.0, abs_tol=1e-9)


def test_translation_shift_does_not_change_forecasts_or_centred_distance() -> None:
    world = ToyWorld(player_count=4)
    history = generate_history(world=world, events=4, seed=5)
    base = replay_history(
        history,
        label="base",
        initial_ratings=world.latent_skills,
        q=world.q,
        k=world.k,
    )
    shifted = replay_history(
        history,
        label="shifted",
        initial_ratings=tuple(value + 2000.0 for value in world.latent_skills),
        q=world.q,
        k=world.k,
    )

    for left, right in zip(base.forecasts, shifted.forecasts):
        assert isclose(left.probability_a_wins, right.probability_a_wins, abs_tol=1e-14)
    for left, right in zip(base.snapshots, shifted.snapshots):
        assert isclose(
            centred_state_distance(left.ratings, right.ratings),
            0.0,
            abs_tol=1e-12,
        )


def test_realized_score_cancels_from_one_step_coupled_difference() -> None:
    world = ToyWorld(player_count=2)
    probability = expected_score(20.0, -20.0, q=world.q)

    def history(a_won: bool) -> ToyHistory:
        draw = probability / 2 if a_won else (1.0 + probability) / 2
        return ToyHistory(
            master_seed=1,
            schedule_seed=2,
            outcome_seed=3,
            events=1,
            player_count=2,
            bouts=(
                ToyBout(
                    event=1,
                    bout_in_event=1,
                    global_bout=1,
                    player_a=0,
                    player_b=1,
                    true_probability_a_wins=probability,
                    random_draw=draw,
                    a_won=a_won,
                ),
            ),
        )

    differences = []
    for outcome in (False, True):
        true_run = replay_history(
            history(outcome),
            label="true",
            initial_ratings=(20.0, -20.0),
            q=world.q,
            k=world.k,
        )
        flat_run = replay_history(
            history(outcome),
            label="flat",
            initial_ratings=(0.0, 0.0),
            q=world.q,
            k=world.k,
        )
        differences.append(
            tuple(
                left - right
                for left, right in zip(
                    true_run.snapshots[-1].ratings,
                    flat_run.snapshots[-1].ratings,
                )
            )
        )

    assert all(
        isclose(left, right, abs_tol=1e-14)
        for left, right in zip(differences[0], differences[1])
    )


def test_event_metrics_separate_initial_memory_from_truth_error() -> None:
    world = ToyWorld(player_count=4)
    history = generate_history(world=world, events=10, seed=7)
    true_run = replay_history(
        history,
        label="true",
        initial_ratings=world.latent_skills,
        q=world.q,
        k=world.k,
    )
    flat_run = replay_history(
        history,
        label="flat",
        initial_ratings=world.flat_initial_ratings,
        q=world.q,
        k=world.k,
    )

    rows = build_event_metrics(
        true_run=true_run,
        flat_run=flat_run,
        latent_skills=world.latent_skills,
        q=world.q,
    )

    assert rows[0].true_state_error == 0
    assert rows[0].true_probability_error == 0
    assert rows[0].state_distance > 0
    assert rows[0].forecast_distance > 0
    assert rows[0].forecast_fraction_remaining == 1
    assert rows[1].true_state_error > 0


def test_development_experiment_writes_replayable_audit_outputs(tmp_path) -> None:
    result = run_development_experiment(
        world=ToyWorld(player_count=4),
        events=30,
        seed=11,
        persistence_events=3,
        output_root=tmp_path,
    )

    expected = {
        "history.csv",
        "ratings.csv",
        "true_start_ratings.csv",
        "bout_forecasts.csv",
        "event_summary.csv",
        "true_start_event_summary.csv",
        "forgetting_summary.csv",
        "true_start_report.md",
        "true_start_report.html",
        "paired_report.md",
        "paired_report.html",
        "report.md",
        "report.html",
        "manifest.json",
    }
    assert {path.name for path in result.run_directory.iterdir()} == expected
    manifest = json.loads((result.run_directory / "manifest.json").read_text())
    assert manifest["run_role"] == "development"
    assert manifest["history"]["sha256"] == result.history_sha256
    assert manifest["initializations"]["true"] == list(result.world.latent_skills)
    assert manifest["initializations"]["flat"] == [0.0] * 4
    assert manifest["outputs"]["true_start_report_html"] == "true_start_report.html"

    with (result.run_directory / "event_summary.csv").open(newline="") as stream:
        metrics = list(csv.DictReader(stream))
    assert len(metrics) == 31
    assert float(metrics[0]["true_state_error"]) == 0
    assert float(metrics[0]["forecast_distance"]) > 0
    true_report = (result.run_directory / "true_start_report.md").read_text()
    assert "no counterfactual initialization" in true_report.lower()
    assert "flat-start process" in true_report
    true_html = (result.run_directory / "true_start_report.html").read_text()
    assert "https://cdn.plot.ly/plotly-2.35.2.min.js" in true_html
    assert '"responsive": true' in true_html
    assert '"displayModeBar": true' in true_html
    assert "Round-robin event" in true_html
    assert "Rating-state RMSE (rating points)" in true_html
    assert '"ticks": "outside"' in true_html


def test_forecast_distance_ignores_common_translation() -> None:
    ratings = (60.0, 20.0, -20.0, -60.0)
    shifted = tuple(value + 1500.0 for value in ratings)

    assert isclose(forecast_distance(ratings, shifted, q=400.0), 0.0, abs_tol=1e-15)


def test_true_start_ensemble_aggregates_run_errors_before_summarising(tmp_path) -> None:
    result = run_true_start_ensemble(
        world=ToyWorld(player_count=4),
        events=12,
        runs=5,
        seed=29,
        output_root=tmp_path,
        progress_every=0,
    )

    assert len(result.replicate_events) == 5 * 13
    assert len(result.event_summary) == 13
    assert result.event_summary[0].state_mean == 0
    assert result.event_summary[0].probability_mean == 0
    assert result.event_summary[1].state_mean > 0
    assert result.event_summary[1].probability_mean > 0
    assert result.elapsed_seconds > 0
    assert aggregate_replicate_events(result.replicate_events) == result.event_summary

    expected = {
        "replicate_seeds.csv",
        "replicate_event_metrics.csv",
        "event_summary.csv",
        "final_player_mean_errors.csv",
        "final_mean_error_progress.csv",
        "report.md",
        "report.html",
        "manifest.json",
    }
    assert {path.name for path in result.run_directory.iterdir()} == expected
    manifest = json.loads((result.run_directory / "manifest.json").read_text())
    assert manifest["ensemble"]["replicate_count"] == 5
    assert manifest["ensemble"]["total_simulated_bouts"] == 360
    assert manifest["elapsed_seconds"] > 0
    assert len(result.final_player_mean_errors) == 4
    assert len(result.final_mean_error_progress) == 5
    assert all(
        row.mean_signed_error_standard_error > 0
        for row in result.final_player_mean_errors
    )
    final_check = result.final_mean_error_progress[-1]
    assert final_check.mean_rating_error_rmse >= 0
    assert isclose(
        sum(row.mean_signed_error for row in result.final_player_mean_errors),
        0.0,
        abs_tol=1e-12,
    )
    report = (result.run_directory / "report.md").read_text()
    assert "does not average\nratings before calculating error" in report
    assert "Total run time:" in report
    html_report = (result.run_directory / "report.html").read_text()
    assert "https://cdn.plot.ly/plotly-2.35.2.min.js" in html_report
    assert '"responsive": true' in html_report
    assert '"displayModeBar": true' in html_report
    assert "Round-robin event" in html_report
    assert "All-pair probability RMSE" in html_report
    assert "Final-rating signed-error cancellation" in html_report
    assert "Replicates included" in html_report
    assert '"ticks": "outside"' in html_report
    assert "Run identity" in html_report
    assert "replicates=5; events/replicate=12" in html_report


def test_constant_start_ensemble_separates_tc_and_paired_outputs(tmp_path) -> None:
    result = run_constant_start_ensemble(
        world=ToyWorld(player_count=4),
        events=20,
        runs=5,
        seed=31,
        persistence_events=3,
        output_root=tmp_path,
        progress_every=0,
    )

    assert len(result.replicate_events) == 5 * 21
    assert len(result.event_summary) == 21
    assert len(result.replicate_landmarks) == 5 * 7
    assert len(result.forgetting_summary) == 7
    assert aggregate_event_rows(result.replicate_events) == result.event_summary
    assert aggregate_landmarks(result.replicate_landmarks) == result.forgetting_summary

    initial = result.event_summary[0]
    final = result.event_summary[-1]
    assert initial.true_state_mean == 0
    assert initial.true_probability_mean == 0
    assert isclose(initial.t_prime_state_mean, initial.paired_state_mean)
    assert isclose(
        initial.t_prime_probability_mean,
        initial.paired_probability_mean,
    )
    assert final.paired_state_mean < initial.paired_state_mean
    assert final.paired_probability_mean < initial.paired_probability_mean

    expected = {
        "replicate_seeds.csv",
        "replicate_event_metrics.csv",
        "event_summary.csv",
        "replicate_forgetting_landmarks.csv",
        "forgetting_summary.csv",
        "tc_final_player_mean_errors.csv",
        "tc_final_mean_error_progress.csv",
        "tc_report.md",
        "tc_report.html",
        "paired_report.md",
        "paired_report.html",
        "manifest.json",
    }
    assert {path.name for path in result.run_directory.iterdir()} == expected

    t_prime_report = (result.run_directory / "tc_report.md").read_text(
        encoding="utf-8"
    )
    paired_report = (result.run_directory / "paired_report.md").read_text(
        encoding="utf-8"
    )
    assert "This is Output 1" in t_prime_report
    assert "does not measure forgetting" in t_prime_report.replace("\n", " ")
    assert "This is Output 2" in paired_report
    assert "isolates memory of initialization" in paired_report

    t_prime_html = (result.run_directory / "tc_report.html").read_text(
        encoding="utf-8"
    )
    paired_html = (result.run_directory / "paired_report.html").read_text(
        encoding="utf-8"
    )
    assert "TC truth-relative rating-state RMSE" in t_prime_html
    assert "T0 versus TC rating-state disagreement" in paired_html
    assert '"responsive": true' in t_prime_html
    assert '"displayModeBar": true' in paired_html
    assert "Run identity" in t_prime_html
    assert "Initialization TC" in t_prime_html
    assert "paired_report.html" in paired_html

    manifest = json.loads((result.run_directory / "manifest.json").read_text())
    assert manifest["ensemble"]["paired_histories"] is True
    assert manifest["initializations"]["T0"] == list(result.world.latent_skills)
    assert manifest["initializations"]["TC"] == [0.0] * 4


def test_inverted_start_ensemble_uses_ti_initialization(tmp_path) -> None:
    world = ToyWorld(player_count=4)
    result = run_inverted_start_ensemble(
        world=world,
        events=20,
        runs=5,
        seed=37,
        persistence_events=3,
        output_root=tmp_path,
        progress_every=0,
    )

    assert result.comparison_code == "TI"
    assert result.comparison_initial_ratings == world.inverted_initial_ratings
    initial = result.event_summary[0]
    assert isclose(initial.t_prime_state_mean, 2 * centred_state_distance(
        world.flat_initial_ratings,
        world.latent_skills,
    ))
    assert initial.paired_probability_mean > 0
    assert result.event_summary[-1].paired_probability_mean < initial.paired_probability_mean
    assert (result.run_directory / "ti_report.html").exists()
    manifest = json.loads((result.run_directory / "manifest.json").read_text())
    assert manifest["initializations"]["TI"] == list(world.inverted_initial_ratings)


def test_random_initialisations_are_reproducible_and_centred() -> None:
    world = ToyWorld(player_count=4)

    first = generate_random_initialisations(
        world=world,
        count=3,
        half_range=360.0,
        seed=41,
    )
    second = generate_random_initialisations(
        world=world,
        count=3,
        half_range=360.0,
        seed=41,
    )
    different = generate_random_initialisations(
        world=world,
        count=3,
        half_range=360.0,
        seed=42,
    )

    assert first == second
    assert first != different
    assert [row.code for row in first] == ["TR01", "TR02", "TR03"]
    for row in first:
        assert isclose(sum(row.centred_ratings), 0.0, abs_tol=1e-12)
        assert len(row.centred_ratings) == world.player_count
        assert all(-720.0 <= value <= 720.0 for value in row.centred_ratings)


def test_random_start_batch_writes_one_comparison_per_map(tmp_path, capsys) -> None:
    result = run_random_start_batch(
        world=ToyWorld(player_count=4),
        maps=3,
        half_range=360.0,
        map_seed=43,
        history_seed=47,
        runs=3,
        events=12,
        persistence_events=3,
        output_root=tmp_path,
        progress_every=0,
    )

    assert [row.code for row in result.initialisations] == [
        "TR01",
        "TR02",
        "TR03",
    ]
    assert [row.code for row in result.model_summaries] == [
        "TR01",
        "TR02",
        "TR03",
    ]
    assert (result.run_directory / "random_initialisations.csv").exists()
    assert (result.run_directory / "model_summary.csv").exists()
    assert (result.run_directory / "summary_report.md").exists()
    assert (result.run_directory / "summary_report.html").exists()
    summary_html = (result.run_directory / "summary_report.html").read_text()
    assert "Run identity" in summary_html
    assert "models=3/3" in summary_html

    for code in ("TR01", "TR02", "TR03"):
        model_root = result.run_directory / code
        run_directories = [path for path in model_root.iterdir() if path.is_dir()]
        assert len(run_directories) == 1
        run_directory = run_directories[0]
        assert (run_directory / f"{code.lower()}_report.html").exists()
        assert (run_directory / "paired_report.html").exists()
        manifest = json.loads((run_directory / "manifest.json").read_text())
        assert code in manifest["initializations"]

    manifest = json.loads((result.run_directory / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["batch"]["requested_models"] == 3
    assert manifest["batch"]["completed_models"] == 3
    assert manifest["batch"]["map_master_seed"] == 43
    assert manifest["batch"]["history_master_seed"] == 47
    assert manifest["batch"]["common_histories_across_models"] is True

    console = capsys.readouterr().out
    assert "Starting TR01 (1/3)" in console
    assert "Completed TR03 (3/3)" in console
    assert "completed 3/3 random models" in console


def test_results_table_extracts_declared_tail_and_persistence_rules(tmp_path) -> None:
    run_directory = tmp_path / "model"
    run_directory.mkdir()

    event_rows = [
        {
            "event": event,
            "state_mean": state,
            "state_q05": state_q05,
            "state_q95": state_q95,
            "probability_mean": probability,
            "probability_q05": probability_q05,
            "probability_q95": probability_q95,
        }
        for event, state, state_q05, state_q95, probability, probability_q05,
        probability_q95 in (
            (0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            (1, 9.0, 7.2, 10.8, 0.09, 0.072, 0.108),
            (2, 10.0, 8.0, 12.0, 0.10, 0.080, 0.120),
            (3, 10.5, 8.4, 12.6, 0.105, 0.084, 0.126),
        )
    ]
    with (run_directory / "event_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(event_rows[0]))
        writer.writeheader()
        writer.writerows(event_rows)

    cancel_rows = [
        {"replicate_count": 1, "mean_rating_error_rmse": 3.0},
        {"replicate_count": 2, "mean_rating_error_rmse": 1.1},
        {"replicate_count": 3, "mean_rating_error_rmse": 1.0},
    ]
    with (run_directory / "progress.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cancel_rows[0]))
        writer.writeheader()
        writer.writerows(cancel_rows)

    run = ModelRun(
        model="T0",
        directory=run_directory,
        manifest={
            "ensemble": {
                "replicate_count": 3,
                "events_per_replicate": 3,
            },
            "outputs": {"final_mean_error_progress": "progress.csv"},
        },
    )
    row = extract_model_results(
        run,
        contract=ExtractionContract(
            event_tail=2,
            event_persistence=2,
            event_relative_tolerance=0.10,
        ),
    )

    assert isclose(row.trmse_level, 10.25)
    assert row.trmse_settling_event == 2
    assert isclose(row.trmse_spread_q05_q95, 4.1)
    assert isclose(row.prmse_level, 0.1025)
    assert row.prmse_settling_event == 2
    assert isclose(row.prmse_spread_q05_q95, 0.041)
    assert row.replicates == 3
    assert row.events == 3
    assert isclose(row.cancel_level, 1.0)
    assert row.cancel_replicates == 3

    output = tmp_path / "results.csv"
    write_results_table(output, [row])
    with output.open(newline="", encoding="utf-8") as stream:
        written = list(csv.DictReader(stream))
    assert len(written) == 1
    assert written[0]["model"] == "T0"
    assert len(written[0]) == 11
