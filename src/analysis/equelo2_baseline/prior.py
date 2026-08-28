"""Extend the frozen Elo-89 prior over historical-only chii."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.elo_model_selection.model import AdoptedPrior, rank_pair
from src.analysis.equelo_population_policy.predict_candidate import load_alpha_prior
from src.sumo_core.Chii import Chii


@dataclass(frozen=True, slots=True)
class PriorEntry:
    rank_pair: str
    rating: float
    source_rank_pair: str
    provenance: str


@dataclass(frozen=True, slots=True)
class CompletedPrior:
    source_path: str
    source_sha256: str
    entries: dict[str, PriorEntry]

    def rating_for(self, chii: Chii) -> tuple[float, str]:
        pair = rank_pair(chii)
        try:
            entry = self.entries[pair]
        except KeyError as error:
            raise KeyError(f"Completed Equelo2 prior has no value for {chii}") from error
        if entry.provenance == "elo89":
            source = f"Elo-89 prior {entry.rank_pair}"
        else:
            source = (
                f"historical nearest-higher completion {entry.rank_pair} "
                f"from {entry.source_rank_pair}"
            )
        return entry.rating, source


def load_and_complete_prior(
    path: Path,
    required_chii: Iterable[Chii],
) -> CompletedPrior:
    """Pair the literal canonical P1 artifact and add historical-only ranks."""

    base, _conversion = load_alpha_prior(path)
    return complete_historical_prior(base, required_chii)


def complete_historical_prior(
    base: AdoptedPrior,
    required_chii: Iterable[Chii],
) -> CompletedPrior:
    """Fill absent pairs from the nearest represented rank above in its division."""

    entries = {
        pair: PriorEntry(pair, rating, pair, "elo89")
        for pair, rating in base.rating_by_pair.items()
    }
    required = {rank_pair(chii): _pair_chii(chii) for chii in required_chii}
    base_by_level: dict[object, list[tuple[int, str]]] = {}
    for pair in base.rating_by_pair:
        chii = Chii.from_str(f"{pair}e")
        base_by_level.setdefault(chii.level, []).append((chii.number, pair))

    for pair, chii in sorted(required.items(), key=lambda item: item[1].ordinal()):
        if pair in entries:
            continue
        candidates = [
            (number, candidate)
            for number, candidate in base_by_level.get(chii.level, ())
            if number < chii.number
        ]
        if not candidates:
            raise ValueError(
                f"Cannot complete historical chii {pair}: no Elo-89 chii above it "
                "in the same division"
            )
        _, source_pair = max(candidates)
        entries[pair] = PriorEntry(
            rank_pair=pair,
            rating=base.rating_by_pair[source_pair],
            source_rank_pair=source_pair,
            provenance="historical_nearest_higher",
        )

    unresolved = sorted(set(required) - set(entries))
    if unresolved:
        raise AssertionError(f"Historical prior completion left gaps: {unresolved}")
    return CompletedPrior(
        source_path=base.source_path,
        source_sha256=base.sha256,
        entries=entries,
    )


def _pair_chii(chii: Chii) -> Chii:
    """Return a canonical east-side representative for ordering a rank pair."""

    return Chii.from_str(f"{rank_pair(chii)}e")
