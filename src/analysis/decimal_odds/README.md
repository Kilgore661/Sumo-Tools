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

## Assessment of the current code

The current implementation is a focused proof of concept for one saved odds
JSON file and one selected basho day. It already:

- builds a conservative current-banzuke shikona-to-History-ID index;
- selects the Elo-89 ratings immediately before the requested day;
- computes each rikishi's Elo-89 probability and equivalent decimal odds;
- converts the two quoted prices to raw implied probabilities;
- removes the two-way overround by proportional normalization; and
- prints the comparison, with optional per-rikishi CSV output.

It does **not** yet consume Betting's consolidated odds CSV, calculate a
bookmaker-implied rating difference, compare that difference with the Elo-89
rating difference, or produce data for the website. The command selects a
single JSON file, and its market parser was written around Marathonbet's
`Fight Result (2-Way)` label. Bet365's `To Win Bout` label would currently be
rejected even though its saved prices are also two-way prices.

Identity resolution currently accepts only a normalized shikona found on the
selected banzuke. Of the 29 distinct bookmaker shikona retained for the
November 2026 experiment, 27 resolve directly. The two exceptions are
`Fujseiun` for History's `Fujiseiun` (ID 12702) and `Hoseryu` for `Hoshoryu`
(ID 12451). No bookmaker alias or opponent-based inference exists yet, so
either spelling currently causes the analysis to fail explicitly.

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

## Possible next postprocessor

The next exploratory step, if pursued, is a postprocessor over Betting's
consolidated odds CSV. For each bout it would convert the normalized market
probability to the rating difference implied by Basic Elo at `q=400`:

```text
market_rating_difference = 400 * log10(p / (1 - p))
```

It could then compare that value with the two rikishi's pre-bout Elo-89 rating
difference. This is only a proposed analysis; it has not been implemented.

Identity resolution for that postprocessor should remain conservative. If
one bookmaker shikona resolves and the other does not, an unambiguous canonical
bout for that day can identify the unknown opponent; the program should emit
and retain a warning that inference occurred. If neither shikona resolves, or
the bout lookup is missing or ambiguous, processing should stop with a useful
fatal error. Completed bouts can come from History; a not-yet-completed day's
canonical pairing would require the retained Torikumi schedule.

Bookmaker page details such as displayed chii are outside this proposed first
step. If chii later matters, History should remain the canonical source. The
eventual meaning and presentation of the website's `Torikumi` menu item are
still open questions, so the analysis should not pre-emptively encode page
requirements that may prove moot.
