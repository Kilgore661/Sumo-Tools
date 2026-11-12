from src.products.make_site89.manifest.artifacts.banzuke import (
    BANZUKE_CHANGES_ARTIFACT,
)
from src.products.make_site89.manifest.filters import BANZUKE_CHANGES_FILTERS


def test_banzuke_change_is_not_a_filter_and_delta_note_is_always_relevant() -> None:
    filters = {item.id: item for item in BANZUKE_CHANGES_FILTERS}
    assert "delta" not in filters
    assert filters["ratings_fit"].label == "Ratings Fit"
    assert filters["ratings_fit"].default is False
    notes = {note.id: note for note in BANZUKE_CHANGES_ARTIFACT.notes}
    assert notes["note_delta"].applies_to == ("all",)
    assert notes["note_delta_chii"].applies_to == ("ratings_fit",)
    assert notes["note_nu_chii"].applies_to == ("ratings_fit",)
