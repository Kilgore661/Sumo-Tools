# Equelo

`analysis/equelo` owns the Equelo rating model and the public API for reading
Equelo ratings.

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

For first appearances, the API uses the fixed_v2 entrant-initial rating for the
annotation-free chii when one exists. If the chii is in the explicit no-rating
domain, the rating is `None`.

## Current Scope

Basho Results uses this API for before/after rating display. Other consumers
should migrate only after their timing and public-display semantics are
reviewed.
