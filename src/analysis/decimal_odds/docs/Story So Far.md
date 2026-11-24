# Decimal odds: story so far

## Why this exploration exists

The existing Torikumi work prompted a broader idea: for every completed day,
and every later day for which a torikumi has been published, show each bout
with the rikishi's pre-bout ratings and computed win probabilities. Completed
days could also show the result and a tick or cross indicating whether the
higher-probability rikishi won.

That is deliberately separate from changing the existing published Torikumi
page. The current page is prospective: it publishes available schedules but
does not add results. Its exact original requirements were not fully recorded,
so the new analysis should stay exploratory until the two features' boundaries
are agreed.

The final addition to the idea was external odds. They cover only selected
bouts, but allow the computed Elo probabilities to be compared with a market's
view where data is available.

## What has been implemented

`src.analysis.decimal_odds` is an analysis package. Its first script,
`compare_next_day_odds.py`, reads a saved next-day odds JSON file and:

1. resolves the quoted rikishi against the selected banzuke and canonical IDs;
2. loads each rikishi's accepted Elo-89 rating immediately before the bout;
3. computes Elo win probability and fair decimal odds (`1 / p`);
4. converts each quoted decimal price to raw implied probability (`1 / price`);
5. normalizes the two raw probabilities to remove the bookmaker overround; and
6. prints the comparison, with optional CSV output.

Day 1 uses basho-start ratings. A later day uses the ratings at the end of the
preceding day. Identity matching is intentionally conservative: missing or
ambiguous names fail rather than silently selecting a rikishi.

The focused tests are in `tests/test_decimal_odds.py`.

## Initial example and finding

The first input examined was
`src/misc/Betting/odds/2026-11-12_05-00.json`: eight selected bouts quoted by
Marathonbet for Day 5 of 2026/11. The two-way market overround was about 8% for
each bout.

Elo and the normalized market probabilities agreed on the favourite in all
eight bouts, but sometimes disagreed substantially about confidence. Examples:

- Kirishima: Elo 72.4%, market 57.4% (Elo +15.0 percentage points);
- Hoshoryu: Elo 81.4%, market 68.0% (Elo +13.4 points);
- Fujiryoga: Elo 55.3%, market 62.4% (market +7.1 points);
- Kotozakura: Elo 55.1%, market 60.8% (market +5.7 points); and
- Aonishiki: Elo 68.6%, market 68.5% (effectively identical).

Expected return from the standpoint of a person who trusts the Elo model is
`p * quoted_decimal_price - 1` per unit staked. That calculation was discussed
to explain what a disagreement means; this project is analysis, not a betting
recommendation.

## Relevant Torikumi discovery

During the investigation, SumoDB future-day result URLs sometimes returned the
latest available day's page rather than a 404 or blank unpublished-day page.
For example, requested Day 6 or Day 7 content could identify itself as Day 5.
The existing Torikumi collector correctly noticed the day mismatch, treated
the refresh as failed and retained the previous snapshot. No change was made:
the desired unpublished-day behaviour should be specified before reusing or
altering that code.

## Requirements still to settle

- Whether the eventual analysis covers only the active basho or also history.
- The exact as-of time and rating snapshot used for every bout state.
- Which outcomes count for scoring (ordinary wins, fusen, draws and missing
  results).
- Tick/cross behaviour for equal, rounded or unavailable probabilities.
- Which odds snapshot to use: first, latest before the bout, a fixed cutoff, or
  every available snapshot.
- How to retain odds provenance. The present downloader can overwrite a file
  with the same event-start filename, so it is not yet a safe price history.
- Identity resolution for shikona changes and rikishi absent from the current
  banzuke.
- How partial external-odds coverage affects summaries and denominators.
- Whether the result becomes a new page or an extension related to the existing
  prospective Torikumi page.

Until those decisions are made, the package should remain an analysis tool and
should not feed the published site.

## Assessment after the November odds collection

The retained experiment now has a consolidated bout-level CSV under Betting's
`special_outputs` directory. It contains 127 priced-bout observations from
Days 5 through 15: 87 from Marathonbet and 40 from Bet365. It preserves the
bookmaker, quoted decimal prices and available acquisition provenance. Older
prototype captures do not contain VPN place or exit IP, and an event-time
filename may have overwritten an earlier successful acquisition of the same
event. The CSV therefore consolidates the successful snapshots that remain,
not every successful invocation that ever occurred.

The original `compare_next_day_odds` code does not read that CSV. It reads one
source JSON and one day, resolves names only against the current banzuke, and
produces Elo probability versus normalized market probability. Its two-way
market recognition is specific to Marathonbet's label, so the saved Bet365
`To Win Bout` market is not accepted by that original command even though the
acquisition parser has already converted its fractional prices to decimal
prices.

The consolidated data exposes two real identity discrepancies among 29 unique
bookmaker shikona: Bet365 supplied `Fujseiun` for Fujiseiun (History ID 12702),
and Marathonbet supplied `Hoseryu` for Hoshoryu (History ID 12451). The other
27 names resolve through ordinary case-and-whitespace normalization. These are
evidence that the next analysis needs an auditable identity policy, not a
reason to introduce general fuzzy matching.

The new `compare_rating_differences` postprocessor implements the conservative
identity policy discussed after the collection. It infers a single unknown
shikona from the known opponent and the canonical bout for that day, while
printing and retaining a warning. Two unknown shikona, no matching bout or an
ambiguous lookup are fatal. History supplies completed-day pairings and the
retained Torikumi snapshot may supply a future pairing. The two observed
misspellings resolve successfully under this rule without an alias table.

The postprocessor turns the overround-normalized market probability into the
signed Basic-Elo rating difference implied at `q=400`, then compares it with
the signed first-minus-second pre-bout Elo-89 rating difference. Its CSV
retains the inputs, fair probabilities and odds, both rating gaps, their
difference, identity methods and warnings. It requires the exact rating
snapshot immediately before each day and fails rather than substituting stale
ratings. Bookmaker chii, results presentation, ticks and crosses, summaries
and the eventual website `Torikumi` page remain deliberately unspecified.
