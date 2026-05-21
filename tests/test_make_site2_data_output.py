from pathlib import Path

from src.products.make_site2.data_output import (
    copy_banzuke_changes_data_output,
    copy_banzuke_division_by_era_data_output,
    copy_division_stability_data_output,
    copy_first_chii_appearance_data_output,
    copy_makuuchi_rank_by_era_data_output,
    copy_standings_by_wins_data_output,
)


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
