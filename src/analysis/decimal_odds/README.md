# Decimal odds comparison

This exploratory package joins a saved next-day external odds file to the
selected banzuke and the accepted Elo-89 rating artifacts. For each externally
covered bout it reports:

- canonical rikishi identity;
- Elo-89 rating immediately before the selected day;
- Elo-89 win probability and equivalent fair decimal odds;
- quoted external decimal price; and
- raw and margin-normalized market-implied probability.

It does not yet load results, score forecasts, retain a market price history or
publish website data.

## Relationship to Torikumi infrastructure

[`src.infra.torikumi`](../../infra/torikumi/README.md) already acquires the
complete published bout schedule for an active or immediate upcoming basho.
This package does not currently consume its `Future` artifact: the first
script starts from the selected bouts present in an external-odds file and
resolves those rikishi independently.

A later day-by-day analysis could use `Future` as the canonical source of
published future pairings, use `History` for completed pairings and outcomes,
then add pre-bout ratings and optional external odds here in the analysis
layer. External odds will remain partial coverage. Torikumi infrastructure
should continue to own acquisition and schedule identity, while this package
owns probability and market comparisons. This is a potential integration
boundary, not an existing dependency or a settled site requirement.

The package is split into:

- `analysis.py`: name resolution, rating selection and probability calculations;
- `compare_next_day_odds.py`: the command-line analysis script; and
- `docs/Story So Far.md`: background, findings and open requirements.

Run the script against the newest JSON in `src/misc/Betting/odds` and the live
History:

```powershell
py -m src.analysis.decimal_odds.compare_next_day_odds
```

Or make every principal input explicit:

```powershell
py -m src.analysis.decimal_odds.compare_next_day_odds `
  src\misc\Betting\odds\2026-11-12_05-00.json `
  --history-zip ".\files\output\Historys\1989_01 to 2026_11.zip" `
  --ratings-root ".\files\output\analysis\site89_bundle\sources\elo89" `
  --basho 2026/11 `
  --day 5 `
  --output-csv ".\files\output\analysis\decimal_odds\2026-11-day-05.csv"
```

By default, the command selects the latest History basho and the day after its
last completed day. Day 1 uses basho-start ratings; later days use ratings at
the end of the preceding day. Names are joined conservatively against the
selected banzuke and unmatched or ambiguous identities fail explicitly.

Elo fair decimal odds are `1 / p`. Market implied probabilities begin as
`1 / quoted_price`; the displayed market comparison removes the two-way
overround by normalizing those two values to sum to one.
