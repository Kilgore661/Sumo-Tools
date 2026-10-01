import os
from pathlib import Path
import stat

from src.infra.tracker.scraper import downloader
from src.infra.tracker.types import BashoDayRef, RetrievalPlan, RetrievalResult
from src.sumo_core.BasicPrimitives import Day
from src.sumo_core.History import Date


def test_new_day_15_refreshes_reused_banzuke_after_results_download(
    tmp_path: Path,
    monkeypatch,
) -> None:
    standings_root = tmp_path / "current standings"
    results_root = tmp_path / "HTML results"
    standings_root.mkdir()
    cached_banzuke = standings_root / "2026 09.html"
    cached_banzuke.write_text("<h1>pre-basho</h1>", encoding="utf-8")
    os.chmod(cached_banzuke, stat.S_IREAD)

    fetched_urls: list[str] = []

    def fetch(url: str) -> str:
        fetched_urls.append(url)
        if "Results.aspx" in url:
            return "results" * 1000
        return "<h1>post-basho with final scores and prizes</h1>"

    monkeypatch.setattr(downloader, "CURRENT_STANDINGS_ROOT", standings_root)
    monkeypatch.setattr(downloader, "HTML_RESULTS_ROOT", results_root)
    monkeypatch.setattr(downloader, "_fetch_text", fetch)
    monkeypatch.setattr(downloader, "sleep", lambda _seconds: None)

    date = Date.from_ints(2026, 9)
    plan = RetrievalPlan(
        banzuke_dates=[date],
        daily_results=[BashoDayRef(date, Day(15))],
    )

    assert downloader.download(plan) is RetrievalResult.SUCCESS_CHANGED
    assert fetched_urls == [
        "https://sumodb.sumogames.de/Results.aspx?b=202609&d=15&simple=on",
        "https://sumodb.sumogames.de/Banzuke.aspx?b=202609&heya=-1&shusshin=-1",
    ]
    assert "post-basho" in cached_banzuke.read_text(encoding="utf-8")


def test_new_day_14_does_not_refresh_reused_banzuke(
    tmp_path: Path,
    monkeypatch,
) -> None:
    standings_root = tmp_path / "current standings"
    results_root = tmp_path / "HTML results"
    standings_root.mkdir()
    cached_banzuke = standings_root / "2026 09.html"
    cached_banzuke.write_text("<h1>pre-basho</h1>", encoding="utf-8")

    fetched_urls: list[str] = []

    def fetch(url: str) -> str:
        fetched_urls.append(url)
        return "results" * 1000

    monkeypatch.setattr(downloader, "CURRENT_STANDINGS_ROOT", standings_root)
    monkeypatch.setattr(downloader, "HTML_RESULTS_ROOT", results_root)
    monkeypatch.setattr(downloader, "_fetch_text", fetch)
    monkeypatch.setattr(downloader, "sleep", lambda _seconds: None)

    date = Date.from_ints(2026, 9)
    plan = RetrievalPlan(
        banzuke_dates=[date],
        daily_results=[BashoDayRef(date, Day(14))],
    )

    assert downloader.download(plan) is RetrievalResult.SUCCESS_CHANGED
    assert fetched_urls == [
        "https://sumodb.sumogames.de/Results.aspx?b=202609&d=14&simple=on"
    ]
    assert cached_banzuke.read_text(encoding="utf-8") == "<h1>pre-basho</h1>"
