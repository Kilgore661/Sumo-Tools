# Equelo

> **WARNING! The elo calcuation code ignores 5.6% of post-1988 bouts simply because there is no kimarite!**

`analysis/equelo` owns the Equelo rating model and the public API for reading
Equelo ratings.

For the project-level meaning, motivation, limitations, and validation
criteria of an Equelo rating, see
[`docs/What is an Equelo Rating.md`](../../../docs/What%20is%20an%20Equelo%20Rating.md).

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

## Current Scope

Basho Results, Career Comparisons, Banzuke Changes, Highest Equelo, Typical
Equelo Values, and related `make_site2` producers use fixed-supported Equelo
artifacts through this package boundary. New consumers should still review
their timing and public-display semantics before adopting a lookup.
