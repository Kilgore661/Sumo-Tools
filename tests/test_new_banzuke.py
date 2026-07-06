from pathlib import Path

from src.infra.new_banzuke.api import (
    NewBanzuke,
    latest_available_banzuke_source,
    load_new_banzuke,
    source_url_for,
    write_new_banzuke,
)
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


def test_new_banzuke_persists_chii_ordinal_and_display_gloss(tmp_path: Path) -> None:
    date = Date(Year(2026), Month(7))
    rikishi_id = RikId(13005)
    chii = Chii.from_str("Jk16w")
    banzuke = Banzuke(
        riks=Riks({rikishi_id}),
        rikchii=RikChii({rikishi_id: chii}),
        rikshik=RikShikona({rikishi_id: Shikona("Kakizoe")}),
    )
    artifact = NewBanzuke.from_banzuke(
        date=date,
        banzuke=banzuke,
        source_path=Path("files/output/current standings/2026 07.html"),
        generated_at="2026-07-06T10:00:00",
    )

    output_path = tmp_path / "new_banzuke.json"
    write_new_banzuke(artifact, output_path)

    text = output_path.read_text(encoding="utf-8")
    assert f'"chii_ordinal": {chii.ordinal()}' in text
    assert '"chii": "Jk16w"' in text

    loaded = load_new_banzuke(output_path)
    loaded_banzuke = loaded.to_banzuke()

    assert loaded.date == date
    assert loaded.source_url == source_url_for(date)
    assert loaded_banzuke.rikchii[rikishi_id] == chii
    assert loaded_banzuke.rikshik[rikishi_id] == Shikona("Kakizoe")


def test_latest_available_banzuke_source_uses_latest_dated_source_file(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "current standings"
    source_root.mkdir()
    (source_root / "2026 05.html").write_text("<h1>Natsu</h1>", encoding="utf-8")
    (source_root / "2026 07.html").write_text("<h1>Nagoya</h1>", encoding="utf-8")
    (source_root / "notes.txt").write_text("ignored", encoding="utf-8")

    date, path = latest_available_banzuke_source(source_root)

    assert date == Date(Year(2026), Month(7))
    assert path == source_root / "2026 07.html"
