# Equelo

> **WARNING! The Elo calculation code ignores 5.6% of 1989-onward bouts simply because there is no kimarite!**

`analysis/equelo` owns the Equelo rating model and the public API for reading
Equelo ratings.

For the project-level meaning, motivation, limitations, and validation
criteria of an Equelo rating, see
[`docs/What is an Equelo Rating.md`](../../../docs/What%20is%20an%20Equelo%20Rating.md).

For the lower-maegashira initial-rating problem, start with the
[consolidated M12 research record](../docs/story/08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md).
Its [experiment catalogue](../docs/story/09%20M12%20Experiment%20Catalogue.md)
documents the contextual boundary producers in this package, while the
[initial-rating policy](../docs/story/10%20Initial%20Rating%20Policy.md) governs
the next integration and predictive-validation work.

## Public API

The normative way to obtain an Equelo rating is:

```python
get_equelo(
    rikid: RikId,
    date: Date,
    h: History,
    when: EqueloTiming = EqueloTiming.AFTER,
) -> float | None
```

`BEFORE` means the rating at the start of the selected basho. `AFTER` means the
rating after the selected basho has been processed.

The result may be `None`. Equelo is defined on the observable SumoDB bout
domain, not on every raw banzuke chii. Some early lower-division chii appear in
raw History but never appear in SumoDB bout data, so no Equelo rating exists for
a rikishi whose first represented chii is in that domain. See `no_rating(...)`
in `api.py` and the validation report in `validate.py`.

Bulk producers should construct an `EqueloLookup` once and call its
`get_equelo(...)` method. This uses the same contract while avoiding repeated
loading and context construction.

For first appearances, the API uses the fixed-supported chii initial rating for
the annotation-free chii when one exists. If the chii is in the explicit
no-rating domain, the rating is `None`.

This is the current production contract. The adopted 1989-onward contextual
entrant-prior policy has not yet replaced it.

## Current Scope

Basho Results, Career Comparisons, Banzuke Changes, Highest Equelo, Typical
Equelo Values, and related `make_site2` producers use fixed-supported Equelo
artifacts through this package boundary. New consumers should still review
their timing and public-display semantics before adopting a lookup.
