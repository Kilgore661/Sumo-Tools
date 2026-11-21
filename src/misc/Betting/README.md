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
several successful daily acquisitions; the Bet365 prototype has also completed
acquisitions using visible Chrome.

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

## VPN-assisted source survey

On 2026-11-18 the betting prototypes were considered together for the first
time with the separate exploratory repository at `X:\VPN`. That repository can
request a URL sequentially through ExpressVPN locations and retain one CSV row
per attempt. It does not render JavaScript or scrape odds.

The Betting project owns this research because its subject is sumo-odds
acquisition. `X:\VPN` is a sandbox, not an architectural dependency. We may
refine either prototype, promote code into proper packages, or write
Betting-owned VPN and browser modules later. The technology and package
boundaries remain open.

The full experimental design is in
[docs/VPN-Assisted Odds Acquisition Experiment.md](docs/VPN-Assisted%20Odds%20Acquisition%20Experiment.md).

The combined research question is:

> Is there a repeatable combination of source, VPN location, browser state,
> language and acquisition time that yields sumo odds consistently?

The active sources are Marathonbet and Bet365. There may be others. Both have
experimental odds scrapers in this folder. NetBet appeared in the first HTTP
reachability surveys but has been dropped from consideration because obtaining
odds requires a login. Its historical probe results remain evidence about the
experiment and should not be deleted.

The place matrix must include `none`: an explicit no-VPN state using the
ordinary network connection. It is a first-class baseline, not a fallback, and
may be the correct route for a UK-facing site. Its exit IP and results should
be recorded and aggregated like those of named VPN places.

### Initial observations

The first near-catalogue surveys produced these results:

| Site | Locations attempted | HTTP 200 | HTTP 403 | HTTP 451 | VPN/transport failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Marathonbet | 217 | 31 | 157 | 25 | 4 |
| Bet365, first full run | 217 | 1 | 149 | 1 | 66 |
| Bet365, second full run | 215 | 3 | 194 | 1 | 17 |
| NetBet (subsequently excluded) | 215 | 171 | 0 | 0 | 44 |

The Bet365 200 responses came from Estonia in both full runs and from
Luxembourg and Slovenia in the second. This is evidence that those homepage
requests succeeded on those occasions, not that those locations always work.
The variation in ExpressVPN failures between runs also shows that rapid
location switching can degrade the experiment itself.

The later `X:\VPN\vpn_probe` collector produced two complete all-location runs
with 216 prepared places in each. Bet365 returned 200 at 52 and 62 places, with
44 succeeding in both runs. Marathonbet returned 200 at 31 and 32 places, with
all 31 first-run successes recurring. Seventeen places returned 200 for both
active sites in both runs. This stronger evidence supersedes the early
impression that Bet365 was necessarily hardest to reach: Marathonbet had the
lower 200 rate, while Bet365 varied more. These are still HTTP reachability
results, not proof of rendered sumo odds. `Direct` was consistent across both
runs: Bet365 returned 200 and Marathonbet returned 403.

These counts must not be read as a map of where a bookmaker is legal or where
sumo odds are available. In particular:

- an HTTP 200 means only that the initial HTTP request succeeded;
- the VPN tester does not execute the client-side betting application;
- a Bet365 `#/...` route is a browser fragment and is not sent in an HTTP
  request, so an HTTP survey does not test its rendered Sumo route;
- a 403 is inconclusive: geography, known-VPN blocking, anti-bot controls, the
  Python/TLS identity and transient policy can all produce it;
- a VPN or transport failure says nothing about the website; and
- one successful observation is not evidence of repeatable acquisition.

An HTTP 451, `Unavailable For Legal Reasons`, is different. It is a completed
and informative response. Once a site/location combination has returned 451,
ordinary later batches should record it as a known legal refusal and skip that
combination. They should not try a browser or another technique to bypass it.
An explicit manual recheck can remain possible because VPN endpoints and site
policies can change.

### Language and presentation

Passing the HTTP stage does not imply that an existing scraper can read the
page. A bookmaker may choose its language from the exit location, URL, cookies,
account or browser preferences. `Accept-Language: en-GB` is only a preference.
English labels such as `Sumo`, `To Win Bout` and cookie-button text may
therefore be absent even when the full site renders successfully. Rikishi
spellings, decimal separators and odds presentation may also vary.

Where practical, later source experiments should record the rendered language
and odds format. Source adapters should prefer stable structural identifiers
over visible English text, while recognising that regional versions may also
have different structures. The exploratory scripts need not be generalized
prematurely merely to accommodate every observed presentation.

### Repeated-run experiment

The useful evidence is a history of observations, not a single list of
working locations. Each raw run should remain immutable and retain at least:

- a run identifier and acquisition time;
- target site and requested URL;
- canonical connection place, including `none`, and observed exit IP;
- HTTP result or a separately classified VPN/transport failure;
- final URL, response size and elapsed time; and
- for browser trials, rendered language, availability of sumo, availability
  of priced bouts, and whether extraction succeeded.

A derived site/location summary can then report attempt counts, outcome
counts, first and latest observations, exit IPs and observed success rate.
Known 451 responses should form a persistent exclusion set for normal runs;
200 and 403 observations should continue to be sampled, while VPN and
transport failures should be eligible for later retry.

To reduce distortion from ExpressVPN or the order of testing:

1. use batches smaller than the complete location catalogue;
2. randomize location order between runs;
3. allow a cooling-off period between batches;
4. repeat a few control locations near the start and end of a batch; and
5. do not confuse a verified HTTP response with a failed or stale VPN switch.

Browser-level trials are a separate experimental stage. They should test a
sample of repeatable HTTP-200 locations, and potentially a small control sample
of 403 locations because a real browser can behave differently from the HTTP
client. A successful browser render must still be followed by evidence that
sumo is offered, that odds are present at the relevant time, and that the
source-specific scraper can persist them.

This work remains exploratory. It may show that no sufficiently consistent
multi-source acquisition method exists; the existence of the two current
scrapers and the VPN survey is not a commitment to build a finished
"get odds from wherever possible" package.

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
