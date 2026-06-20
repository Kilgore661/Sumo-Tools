from pathlib import Path

from src.products.make_site2.data_output import (
    build_basho_results_data_output,
    build_career_comparisons_data_output,
    copy_banzuke_changes_data_output,
    copy_banzuke_division_by_era_data_output,
    copy_career_length_data_output,
    copy_division_stability_data_output,
    copy_first_chii_appearance_data_output,
    copy_highest_equelo_data_output,
    copy_makuuchi_rank_by_era_data_output,
    copy_rank_at_retirement_data_output,
    copy_standings_by_wins_data_output,
    copy_typical_equelo_values_data_output,
    copy_win_probability_by_standing_data_output,
)
from src.products.make_site2.perf_chart.build import MasterDataOutput


def test_copy_banzuke_changes_data_output_stages_producer_files(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = tmp_path / "files" / "output" / "bcr"
    (source_root / "data").mkdir(parents=True)
    (source_root / "site_config.json").write_text("config", encoding="utf-8")
    (source_root / "data" / "banzuke_change_report.csv").write_text(
        "csv",
        encoding="utf-8",
    )

    output = copy_banzuke_changes_data_output(output_root=tmp_path / "site")

    assert output.site_config_path.read_text(encoding="utf-8") == "config"
    assert output.report_csv_path.read_text(encoding="utf-8") == "csv"
    assert output.site_config_path == (
        tmp_path / "site" / "current-sumo" / "banzuke-changes" / "site_config.json"
    )
    assert output.report_csv_path == (
        tmp_path
        / "site"
        / "current-sumo"
        / "banzuke-changes"
        / "data"
        / "banzuke_change_report.csv"
    )


def test_build_basho_results_data_output_reuses_public_shikona_map(
    monkeypatch,
    tmp_path: Path,
) -> None:
    history = object()
    ratings = object()
    full_shikona_store = object()
    dates = ("1980/01", "1980/03")
    seen_maps = []
    store_calls = []

    monkeypatch.setattr(
        "src.products.make_site2.data_output.represented_dates",
        lambda history: dates,
    )
    monkeypatch.setattr(
        "src.products.make_site2.data_output.build_index",
        lambda history: object(),
    )
    monkeypatch.setattr(
        "src.products.make_site2.data_output.write_index",
        lambda index, route_data_root: route_data_root / "basho_results_index.json",
    )
    monkeypatch.setattr(
        "src.products.make_site2.data_output.EqueloLookup.load",
        lambda supplied_history: ratings,
    )

    def fake_full_shikona_store_from_sources(supplied_history):
        store_calls.append(supplied_history)
        return full_shikona_store

    def fake_build_payload_rows(
        *,
        history,
        date,
        ratings,
        full_shikona_store,
    ):
        seen_maps.append(full_shikona_store)
        return (f"row:{date}",)

    monkeypatch.setattr(
        "src.products.make_site2.data_output.FullShikonaStore.from_sources",
        fake_full_shikona_store_from_sources,
    )
    monkeypatch.setattr(
        "src.products.make_site2.data_output.build_payload_rows",
        fake_build_payload_rows,
    )
    monkeypatch.setattr(
        "src.products.make_site2.data_output.write_payload",
        lambda date, rows, route_data_root: route_data_root / f"{date}.csv",
    )

    output = build_basho_results_data_output(
        history=history,
        output_root=tmp_path,
    )

    assert store_calls == [history]
    assert seen_maps == [full_shikona_store, full_shikona_store]
    assert output.payload_paths == (
        tmp_path / "sumo-history" / "basho-results" / "data" / "1980/01.csv",
        tmp_path / "sumo-history" / "basho-results" / "data" / "1980/03.csv",
    )


def test_copy_standings_by_wins_data_output_stages_producer_files(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = tmp_path / "files" / "output" / "standings" / "publisher" / "latest_data"
    source_root.mkdir(parents=True)
    (source_root / "site_config.json").write_text("config", encoding="utf-8")
    (source_root / "page_bundle.json").write_text("bundle", encoding="utf-8")
    (source_root / "multiple basho standings view (2026_03, BACKWARDS, 6).csv").write_text(
        "csv",
        encoding="utf-8",
    )
    (source_root / "multiple basho standings view (2026_03, BACKWARDS, 6).json").write_text(
        "json",
        encoding="utf-8",
    )

    output = copy_standings_by_wins_data_output(output_root=tmp_path / "site")

    route_data_root = tmp_path / "site" / "current-sumo" / "standings-by-wins" / "data"
    assert output.site_config_path == route_data_root / "site_config.json"
    assert output.site_config_path.read_text(encoding="utf-8") == "config"
    assert sorted(path.name for path in output.data_paths) == [
        "multiple basho standings view (2026_03, BACKWARDS, 6).csv",
        "multiple basho standings view (2026_03, BACKWARDS, 6).json",
    ]
    assert not (route_data_root / "page_bundle.json").exists()


def test_copy_banzuke_division_by_era_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "banzuke_division_era"
        / "site"
        / "banzuke_division_by_era"
    )
    source_root.mkdir(parents=True)
    (source_root / "divisions.csv").write_text("csv", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_banzuke_division_by_era_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "banzuke-rank"
        / "banzuke-structure-over-time"
        / "banzuke-division-by-era"
        / "data"
    )
    assert output.csv_path == route_data_root / "divisions.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_makuuchi_rank_by_era_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "rank_era"
        / "site"
        / "makuuchi_rank_by_era"
    )
    source_root.mkdir(parents=True)
    (source_root / "ranks.csv").write_text("csv", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_makuuchi_rank_by_era_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "banzuke-rank"
        / "banzuke-structure-over-time"
        / "makuuchi-rank-by-era"
        / "data"
    )
    assert output.csv_path == route_data_root / "ranks.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_division_stability_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "persistence"
        / "site"
        / "division_stability"
    )
    source_root.mkdir(parents=True)
    (source_root / "persistence.csv").write_text("csv", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_division_stability_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "banzuke-rank"
        / "division-stability"
        / "data"
    )
    assert output.csv_path == route_data_root / "persistence.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_first_chii_appearance_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "first_app"
        / "site"
        / "first_chii_appearance"
    )
    source_root.mkdir(parents=True)
    (source_root / "appearances.csv").write_text("csv", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_first_chii_appearance_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "banzuke-rank"
        / "rank-history"
        / "first-chii-appearance"
        / "data"
    )
    assert output.csv_path == route_data_root / "appearances.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_rank_at_retirement_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "rank_at_retirement"
        / "site"
        / "rank_at_retirement_1958_01_to_2026_05"
    )
    source_root.mkdir(parents=True)
    (source_root / "distribution.csv").write_text("csv", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_rank_at_retirement_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "sumo-history"
        / "career-lifecycle"
        / "rank-at-retirement"
        / "data"
    )
    assert output.csv_path == route_data_root / "distribution.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_career_length_data_output_stages_csv_set(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "career_length"
        / "site"
        / "career_length_1958_01_to_2026_05"
    )
    source_root.mkdir(parents=True)
    for name in ("distribution.csv", "pmf.csv", "cdf.csv", "survival.csv", "longest.csv"):
        (source_root / name).write_text(name, encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_career_length_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "sumo-history"
        / "career-lifecycle"
        / "career-length"
        / "data"
    )
    assert sorted(path.name for path in output.data_paths) == [
        "cdf.csv",
        "distribution.csv",
        "longest.csv",
        "pmf.csv",
        "survival.csv",
    ]
    for path in output.data_paths:
        assert path.parent == route_data_root
        assert path.read_text(encoding="utf-8") == path.name
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_typical_equelo_values_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "Equelo"
        / "fixed_supported"
        / "landmarks"
        / "site"
        / "typical_equelo_values"
    )
    source_root.mkdir(parents=True)
    (source_root / "typical_equelo_values.csv").write_text("csv", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_typical_equelo_values_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "ratings-models"
        / "rating-and-rank"
        / "typical-equelo-values"
        / "data"
    )
    assert output.csv_path == route_data_root / "typical_equelo_values.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_copy_highest_equelo_data_output_stages_only_csv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "analysis"
        / "sumo_history"
        / "records"
        / "highest_equelo"
    )
    source_root.mkdir(parents=True)
    (source_root / "highest_equelo.csv").write_text("csv", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_highest_equelo_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "sumo-history"
        / "records"
        / "highest-equelo"
        / "data"
    )
    assert output.csv_path == route_data_root / "highest_equelo.csv"
    assert output.csv_path.read_text(encoding="utf-8") == "csv"
    assert not (route_data_root / "metadata.json").exists()


def test_copy_win_probability_by_standing_data_output_stages_csv_set(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_root = (
        tmp_path
        / "files"
        / "output"
        / "probability"
        / "matchups"
        / "site"
        / "win_probability_by_standing"
    )
    source_root.mkdir(parents=True)
    (source_root / "observed_trace_points.csv").write_text(
        "observed",
        encoding="utf-8",
    )
    (source_root / "equelo_trace_points.csv").write_text("equelo", encoding="utf-8")
    (source_root / "page.json").write_text("page", encoding="utf-8")
    (source_root / "metadata.json").write_text("metadata", encoding="utf-8")

    output = copy_win_probability_by_standing_data_output(output_root=tmp_path / "site")

    route_data_root = (
        tmp_path
        / "site"
        / "ratings-models"
        / "observed-vs-modelled"
        / "win-probability-by-standing"
        / "data"
    )
    assert sorted(path.name for path in output.data_paths) == [
        "equelo_trace_points.csv",
        "observed_trace_points.csv",
    ]
    assert (route_data_root / "observed_trace_points.csv").read_text(
        encoding="utf-8"
    ) == "observed"
    assert (route_data_root / "equelo_trace_points.csv").read_text(
        encoding="utf-8"
    ) == "equelo"
    assert not (route_data_root / "page.json").exists()
    assert not (route_data_root / "metadata.json").exists()


def test_build_career_comparisons_data_output_writes_producer_then_stages(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    selected_history = object()
    producer_root = Path("files") / "output" / "perf_chart" / "career_comparisons"

    def fake_write_master_data(*, history, output_root):
        assert history is selected_history
        assert output_root == producer_root
        output_root.mkdir(parents=True)
        data_path = output_root / "trajectory_master.json"
        report_path = output_root / "trajectory_master_report.json"
        data_path.write_text("data", encoding="utf-8")
        report_path.write_text("report", encoding="utf-8")
        return MasterDataOutput(data_path=data_path, report_path=report_path)

    monkeypatch.setattr(
        "src.products.make_site2.data_output.write_master_data",
        fake_write_master_data,
    )

    output = build_career_comparisons_data_output(
        history=selected_history,
        output_root=tmp_path / "site",
    )

    route_data_root = tmp_path / "site" / "rikishi" / "career-comparisons" / "data"
    absolute_producer_root = tmp_path / producer_root
    assert (absolute_producer_root / "trajectory_master.json").read_text(encoding="utf-8") == "data"
    assert (absolute_producer_root / "trajectory_master_report.json").read_text(
        encoding="utf-8"
    ) == "report"
    assert output.data_path == route_data_root / "trajectory_master.json"
    assert output.report_path == route_data_root / "trajectory_master_report.json"
    assert output.data_path.read_text(encoding="utf-8") == "data"
    assert output.report_path.read_text(encoding="utf-8") == "report"
