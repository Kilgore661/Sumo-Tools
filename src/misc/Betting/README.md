# Sumo betting-odds prototypes

## Purpose and status

This folder is an experiment in obtaining external pre-bout odds so that they
can be compared with win probabilities derived from Elo-89 ratings. The aim is
to test Elo-89 as a probabilistic model, not to support or recommend betting.

Only selected sumo bouts receive bookmaker odds, and their availability and
publication time are not yet well understood. This folder therefore contains
two deliberately provisional acquisition scripts rather than a production
betting package:

- `download_sumo_odds.py` for Marathonbet (Mbet)
- `download_bet365_sumo_odds.py` for Bet365

Both depend on public, client-rendered bookmaker pages whose routes, labels,
layout, access rules and publication schedule can change without notice. Unit
tests exercise parsing and control logic, but neither scraper has enough live
history to be considered reliable. The Marathonbet prototype has completed
several successful daily acquisitions; the Bet365 prototype has completed one
successful acquisition using visible Chrome.

Neither script logs in or places bets.

## Output convention

Ordinary generated output should live outside the source tree:

```text
files/output/misc/Betting/marathonbet/
files/output/misc/Betting/bet365/
files/output/misc/Betting/browser_profile/
files/output/misc/Betting/diagnostics/
```

If a small number of captured snapshots later need to be retained in Git as
research evidence or test fixtures, selected copies should be placed under:

```text
src/misc/Betting/special_outputs/marathonbet/
src/misc/Betting/special_outputs/bet365/
```

The prototypes pre-date that decision and currently have inconsistent default
locations under `src/misc/Betting`. That is accepted for the present daily
experiment; it should be corrected when the production package is designed.
Successful JSON downloads are evidence and must not be discarded merely
because their present locations are provisional.

Both prototypes write the same broad JSON model:

- source URL, timezone and acquisition timestamp;
- common event start;
- one entry per priced bout;
- competitors, displayed start, tournament and source page;
- outcome, decimal price and market for each rikishi.

Fractional Bet365 prices such as `4/11` are converted to decimal odds. The
current filenames are based on the event start, so another acquisition for the
same event can replace the earlier file. Preserving multiple intraday snapshots
is a production-design question, not part of these prototypes.

## Marathonbet prototype

`download_sumo_odds.py` opens Marathonbet's public sumo listing, discovers the
currently offered events, follows each event page and reads its visible
two-way fight-result prices. Events with the same start time are grouped into
one JSON file.

Install the shared dependency from this folder:

```powershell
python -m pip install -r src\misc\Betting\requirements.txt
```

Example using the intended runtime-output area:

```powershell
py src\misc\Betting\download_sumo_odds.py `
  --output-dir files\output\misc\Betting\marathonbet
```

The script reports every attempt. If no sumo events are available, or a
transient Playwright error prevents acquisition, it waits 30 minutes and tries
again. It exits after the first successful write. `Ctrl+C` stops it; `--once`
requests one attempt only. Other diagnostic options include `--headed`,
`--browser-channel msedge` and `--retry-minutes N`.

This retry behavior has already provided some evidence about when Marathonbet
publishes the next day's odds.

## Bet365 prototype

`download_bet365_sumo_odds.py` starts an ordinary installed Chrome or Edge and
then attaches Playwright through the browser's debugging interface. Launching
the browser directly is important: Bet365 did not render its sport pages in
Chrome launched by Playwright itself during development.

The prototype:

1. opens Bet365's stable Sumo sport route (`B160`);
2. finds the current `To Win Bout` market;
3. obtains the changing bout-page route from the rendered application;
4. clicks or freshly loads that route as necessary;
5. parses Bet365's column-oriented list of bouts and prices;
6. converts all prices to decimal odds and writes the common JSON model.

Chrome is visible by default because that is the mode in which the prototype
has succeeded. `--headless` is an explicit, currently unproven alternative.

Example using the intended runtime-output area and profile location:

```powershell
py src\misc\Betting\download_bet365_sumo_odds.py `
  --output-dir files\output\misc\Betting\bet365 `
  --profile-dir files\output\misc\Betting\browser_profile
```

The dedicated browser profile preserves local browser state between runs. It
is runtime state, not source data, and must not be committed. On acquisition
failure the current prototype can save a screenshot and rendered page text;
such diagnostics belong under `files/output`, not the source tree.

Unlike the Marathonbet prototype, Bet365 makes one immediate attempt and does
not run a retry loop.

## Current daily experiment

For the remainder of the current basho, run both prototypes each day at
14:30 UK time and retain every successful JSON acquisition. The immediate
questions are:

- Are next-day odds available at that time?
- Does availability differ between the two bookmakers?
- Which bouts receive odds?
- Do the same names, bouts and start times appear at both sources?
- Are repeated daily acquisitions sufficiently reliable to justify a proper
  package?

Failures are also observations about availability or scraper fragility, but
the present goal is to accumulate successful source snapshots rather than to
turn these scripts into production infrastructure during the trial.

## Further work

If the daily experiment succeeds:

1. Create a proper betting package that knows when acquisitions are needed,
   invokes the source-specific adapters and preserves their provenance.
2. Match the externally priced bouts to the relevant pre-bout Elo-89 ratings.
3. Convert Elo-89 win probabilities to decimal odds and compare them with each
   bookmaker's raw and margin-adjusted probabilities.
4. Make the resulting comparison data available to the website-publishing
   pipeline.
5. If that pipeline proves useful and reliable, integrate the comparisons into
   the published website.

Those stages should follow evidence from the daily trial. The two scripts in
this folder should remain recognisable as fragile prototypes until then.
