from pathlib import Path

from src.products.make_site2.data_output import copy_banzuke_changes_data_output


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
