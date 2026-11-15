from src.analysis.site89.rating_changes import _possible_bouts
from src.products.make_site89.manifest.artifacts.rating_changes import RATING_CHANGES_ARTIFACT
from src.sumo_core.Chii import Chii


def test_expected_bouts_respect_incomplete_sekitori_basho() -> None:
    assert _possible_bouts(Chii.from_str("M1e"), represented_days=7) == 7
    assert _possible_bouts(Chii.from_str("J1w"), represented_days=7) == 7
    assert _possible_bouts(Chii.from_str("M1e"), represented_days=15) == 15


def test_expected_bouts_approximate_incomplete_lower_division_schedule() -> None:
    makushita = Chii.from_str("Ms1e")
    assert _possible_bouts(makushita, represented_days=0) == 0
    assert _possible_bouts(makushita, represented_days=6) == 3
    assert _possible_bouts(makushita, represented_days=7) == 4
    assert _possible_bouts(makushita, represented_days=15) == 7


def test_expected_basis_note_explains_incomplete_basho_policy() -> None:
    note = next(note for note in RATING_CHANGES_ARTIFACT.notes if note.id == "note_basis")
    assert "one per completed day" in note.text
    assert "approximate one per two completed days" in note.text
