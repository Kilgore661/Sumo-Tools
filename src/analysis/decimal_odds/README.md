# Decimal odds comparison

This exploratory package joins saved external odds to the selected banzuke and
the accepted Elo-89 rating artifacts. It contains the original one-JSON
comparison and a consolidated-CSV rating-difference postprocessor. Across
those tools it can report:

- canonical rikishi identity;
- Elo-89 rating immediately before the selected day;
- Elo-89 win probability and equivalent fair decimal odds;
- quoted external decimal price; and
- raw and margin-normalized market-implied probability.

It does not yet load results, score forecasts, retain a market price history or
publish website data.

## Assessment of the original one-file comparison

`compare_next_day_odds.py` is the original focused proof of concept for one
saved odds JSON file and one selected basho day. It:

- builds a conservative current-banzuke shikona-to-History-ID index;
- selects the Elo-89 ratings immediately before the requested day;
- computes each rikishi's Elo-89 probability and equivalent decimal odds;
- converts the two quoted prices to raw implied probabilities;
- removes the two-way overround by proportional normalization; and
- prints the comparison, with optional per-rikishi CSV output.

That command does not consume Betting's consolidated odds CSV or calculate
rating differences. Its market parser was written around Marathonbet's
`Fight Result (2-Way)` label, so Bet365's `To Win Bout` label is rejected even
though its saved prices are also two-way prices. The separate postprocessor
documented below handles the consolidated CSV directly and therefore does not
depend on those source market labels.

The original command accepts only a normalized shikona found on the selected
banzuke. Of the 29 distinct bookmaker shikona retained for the November 2026
experiment, 27 resolve directly. The two exceptions are
`Fujseiun` for History's `Fujiseiun` (ID 12702) and `Hoseryu` for `Hoshoryu`
(ID 12451). The new postprocessor resolves these from the known opponent and
canonical bout, while the original command still fails on them explicitly.

## Relationship to Torikumi infrastructure

[`src.infra.torikumi`](../../infra/torikumi/README.md) already acquires the
complete published bout schedule for an active or immediate upcoming basho.
The original command does not consume its `Future` artifact: it starts from
the selected bouts present in an external-odds file and resolves those rikishi
independently. The rating-difference postprocessor can use `Future` only when
it must infer one unknown shikona from a not-yet-completed canonical bout.

A later day-by-day analysis could use `Future` as the canonical source of
published future pairings, use `History` for completed pairings and outcomes,
then add pre-bout ratings and optional external odds here in the analysis
layer. External odds will remain partial coverage. Torikumi infrastructure
should continue to own acquisition and schedule identity, while this package
owns probability and market comparisons. This is a potential integration
boundary, not an existing dependency or a settled site requirement.

The package is split into:

- `analysis.py`: name resolution, rating selection and probability calculations;
- `compare_next_day_odds.py`: the original one-JSON command-line analysis;
- `rating_differences.py`: consolidated-row identity resolution and rating-gap
  calculations;
- `compare_rating_differences.py`: the consolidated CSV postprocessor;
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

## Odds/Elo rating-difference postprocessor

`compare_rating_differences.py` reads Betting's consolidated odds CSV. For
each bout it converts the normalized market probability to the rating
difference implied by Basic Elo at `q=400`:

```text
market_rating_difference = 400 * log10(p / (1 - p))
```

It compares that signed first-rikishi-minus-second-rikishi value with the two
pre-bout Elo-89 ratings and writes both differences and
`market_minus_elo89_difference`. The output also retains the quoted prices,
overround, no-overround probabilities and fair odds, rating cutoff, History
IDs and identity-resolution method.

Identity resolution remains conservative. If one bookmaker shikona resolves
and the other does not, an unambiguous canonical bout for that day identifies
the unknown opponent. The program prints a warning and retains it in the
output row. If neither shikona resolves, or the bout lookup is missing or
ambiguous, processing stops with a fatal error. Completed bouts come from
History; the retained Torikumi schedule can supply a not-yet-completed day.
Rows whose two shikona resolve do not require a schedule lookup.

Run all rows for which the rating artifacts contain an exact pre-day snapshot:

```powershell
py -m src.analysis.decimal_odds.compare_rating_differences `
  --history-zip ".\files\output\Historys\1989_01 to 2026_11.zip"
```

Use repeatable `--day` options for a partial run while later rating snapshots
are not yet available:

```powershell
py -m src.analysis.decimal_odds.compare_rating_differences `
  --history-zip ".\files\output\Historys\1989_01 to 2026_11.zip" `
  --day 10 --day 11
```

Ordinary output is
`files/output/analysis/decimal_odds/2026-11-odds-elo-differences.csv`.
Missing exact pre-bout ratings are fatal; the comparer never substitutes an
older, stale rating snapshot.

Bookmaker page details such as displayed chii are outside this first step. If
chii later matters, History should remain the canonical source. The
eventual meaning and presentation of the website's `Torikumi` menu item are
still open questions, so the analysis should not pre-emptively encode page
requirements that may prove moot.
