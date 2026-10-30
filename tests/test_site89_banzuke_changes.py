import csv
import json
from pathlib import Path

import pytest

from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.site89 import banzuke_changes
from src.analysis.site89.shikona_annotations import ShikonaAnnotation
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_next_published_banzuke_is_accepted_before_it_enters_history(
    monkeypatch, tmp_path: Path
) -> None:
    history = _history_ending("2026/09")
    source = _write_bcr(tmp_path, current="2026/11", previous="2026/09")
    captured = {}

    def annotations(_history, date, *, banzuke=None):
        captured.update(date=date, banzuke=banzuke)
        return {RikId(1): ShikonaAnnotation(highest_chii=True)}

    monkeypatch.setattr(banzuke_changes, "banzuke_annotations", annotations)

    _, csv_path = banzuke_changes.produce_banzuke_changes(
        history=history,
        structural_source_root=source,
        ratings=_ratings(),
        output_root=tmp_path / "output",
    )

    assert str(captured["date"]) == "2026/11"
    assert captured["banzuke"].rikchii[RikId(1)] == Chii.from_str("M1e")
    with csv_path.open(newline="", encoding="utf-8") as stream:
        row = next(csv.DictReader(stream))
    assert row["east_rating"] == "1234"
    assert row["east_highest_chii"] == "true"


def test_missing_date_is_rejected_when_bcr_previous_is_not_history_end(
    tmp_path: Path,
) -> None:
    history = _history_ending("2026/09")
    source = _write_bcr(tmp_path, current="2026/11", previous="2026/07")

    with pytest.raises(ValueError, match="not the published successor"):
        banzuke_changes.produce_banzuke_changes(
            history=history,
            structural_source_root=source,
            ratings=_ratings(),
            output_root=tmp_path / "output",
        )


def _history_ending(value: str) -> History:
    year, month = (int(part) for part in value.split("/"))
    date = Date.from_ints(year, month)
    rikishi_id = RikId(1)
    ranks = {rikishi_id: Chii.from_str("M2e")}
    return History(
        {
            date: BashoState(
                banzuke=Banzuke(
                    riks=Riks(ranks),
                    rikchii=RikChii(ranks),
                    rikshik=RikShikona({rikishi_id: Shikona("Existing")}),
                ),
                summary=Summary({}),
            )
        }
    )


def _write_bcr(
    root: Path, *, current: str, previous: str
) -> Path:
    source = root / "bcr"
    (source / "data").mkdir(parents=True)
    (source / "site_config.json").write_text(
        json.dumps({"current_date": current, "previous_date": previous}),
        encoding="utf-8",
    )
    fields = (
        "east_rikishi_id",
        "east_chii",
        "east_shikona",
        "east_equelo",
        "west_rikishi_id",
        "west_chii",
        "west_shikona",
        "west_equelo",
    )
    with (source / "data" / "banzuke_change_report.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "east_rikishi_id": "1",
                "east_chii": "M1e",
                "east_shikona": "Existing",
                "east_equelo": "",
                "west_rikishi_id": "",
                "west_chii": "",
                "west_shikona": "",
                "west_equelo": "",
            }
        )
    return source


def _ratings() -> Elo89Artifacts:
    return Elo89Artifacts(
        root=Path("unused"),
        manifest={},
        prior={},
        basho_start_ratings={},
        day_end_ratings={},
        basho_end_ratings={"2026/09": {"1": 1234.0}},
        bout_ledger=(),
    )
