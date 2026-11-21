# Proposal: improved site-specific sumo-odds probes

## Status

This proposal describes the next live experiment for the Betting project. It
does not describe a general bookmaker framework or a finished production
service. There is one day of the November 2026 basho left, so the immediate
priority is to improve and exercise the existing Bet365 and Marathonbet scripts
while next-day odds can still appear.

The separate `X:\VPN` repository remains a sandbox. Its replicated HTTP survey
has supplied useful evidence and proven mechanisms, but Betting must own the
sumo-specific programs, results and requirements. The improved probes must not
depend at runtime on an absolute path to `X:\VPN`.

## Objective

Provide two independently runnable, source-specific probes that try, as far as
reasonably possible, to acquire and persist valid odds for the next basho day:

- a Bet365 probe; and
- a Marathonbet probe.

Each probe should use a real installed browser, try a bounded sequence of
promising connection places, record what happened at every place and stop after
the first valid acquisition. It is successful only when it has persisted a
validated odds snapshot for the intended date.

This is deliberately different from `vpn_probe`:

- `vpn_probe` observes an experimental matrix and does not stop at the first
  HTTP 200;
- a site-specific odds probe is an acquisition attempt and should stop after
  it has the required data; and
- HTTP reachability is only one stage inside an odds attempt.

## Evidence available to the probes

Two complete `vpn_probe` runs tested 216 prepared connection places. For the
active sites:

| Site | First-run HTTP 200 | Second-run HTTP 200 | 200 in both runs |
| --- | ---: | ---: | ---: |
| Bet365 | 52 | 62 | 44 |
| Marathonbet | 31 | 32 | 31 |

Seventeen ExpressVPN places returned 200 for both sites in both runs.
`Direct`, meaning the ordinary UK connection with ExpressVPN disconnected,
returned 200 for Bet365 and 403 for Marathonbet in both runs.

These results select candidates; they do not prove that a browser application,
sumo market or odds will be available. Exit IPs changed substantially between
the two runs, so a place name and numeric ID are the actionable selectors. The
observed exit IP remains important provenance for each attempt.

The initial common candidate set is:

| ID | Place |
| ---: | --- |
| 12 | Luxembourg |
| 45 | Canada - Montreal |
| 78 | Denmark |
| 86 | Romania |
| 96 | Norway |
| 102 | Greece |
| 106 | Iceland |
| 110 | Bulgaria |
| 118 | Croatia |
| 120 | Moldova |
| 121 | Slovenia |
| 126 | Albania |
| 127 | Slovakia |
| 130 | Estonia |
| 146 | North Macedonia |
| 181 | Canada - Vancouver |
| 203 | Sweden - 2 |

The complete source-specific pools are larger: 44 places for Bet365, including
`Direct`, and 31 for Marathonbet. A checked-in candidate snapshot may later be
generated from the two identified VPN run IDs, but the first live trial can
start with `Direct` plus the common set for Bet365 and the common set for
Marathonbet. This avoids turning a time-sensitive acquisition test into another
all-location survey.

## Acquisition window and target date

The normal target is Day `D+1`, searched for on Day `D`.

- A probe may start between 10:00 and 22:00 UK local time.
- Use the `Europe/London` timezone so the rule follows GMT and BST.
- The two-hour runtime allowance explains the latest start time; it is not a
  hard completion deadline.
- Once started, a probe may finish naturally after 22:00 or midnight.
- A successful acquisition ends the probe immediately.
- Day 1 needs a separate pre-basho rule because no preceding basho day exists.
- Do not schedule a next-day probe after Day 15.

Capture the target date when the run starts and retain it even if the run
crosses midnight. Prefer an explicit `--target-date YYYY-MM-DD` option, with the
next UK calendar date as the normal default. An explicit development override
may bypass the start window, but the console and attempt record must say that
the run was outside the normal acquisition window.

An extracted event must match the target date. Odds for a stale day, the
current day or another future day are observations, not a successful
acquisition.

## Proposed package boundary

Keep the two source adapters separate and share only mechanisms that genuinely
have the same behaviour:

```text
src/misc/Betting/probes/
    __init__.py
    bet365.py
    marathonbet.py
    browser.py
    connection.py
    records.py
    candidates.py
```

The existing top-level scripts may initially become thin compatibility entry
points, or their tested parsing functions may be imported by the new modules.
Do not perform a large mechanical move before the final-day live trial.

Source modules own:

- entry URLs and navigation;
- rendered-page recognition;
- language and odds-format handling;
- source-specific parsing;
- validation of extracted bouts; and
- construction of the common odds JSON model.

Shared modules own:

- connection-place values, including `Direct`;
- bounded ExpressVPN switching and verification;
- exit-IP readiness;
- real-browser lifecycle;
- run and attempt records;
- time-window and target-date checks; and
- final restoration of the initial connection state.

The source adapters should not be forced behind a generalized bookmaker
interface until their real differences are better understood.

## Elements to adopt from `X:\VPN`

Adopt the behaviour and tests where useful, rather than importing the sandbox
repository by path.

### Connection places

- Represent `Direct` and named ExpressVPN locations explicitly.
- Resolve ExpressVPN locations against its live catalogue by numeric ID.
- Record both the requested canonical place and the state actually observed.
- Use a process-level lock so two Betting probes cannot control ExpressVPN at
  the same time.

### Preparation and verification

- Capture the initial VPN state before the first attempt.
- Disconnect before establishing each new place.
- For `Direct`, verify that ExpressVPN is disconnected.
- For a VPN place, connect and verify the requested location rather than
  assuming the command succeeded.
- Poll a primary and fallback public-IP service until the route is ready.
- Record the observed exit IP.
- Keep connection, verification and readiness operations bounded by timeouts.

### Failure handling

- A timed-out connect command may still have established the requested place;
  verify state before sending another command.
- Retry a transient control failure in a bounded way without advancing
  silently to the next place.
- A few candidate switches do not initially require the full all-catalogue
  circuit breaker and forced service restart. Abort cleanly after repeated
  ExpressVPN control failures rather than destabilizing the machine during a
  browser acquisition.
- Always attempt to restore the initial VPN state on success, ordinary failure,
  Ctrl+C and handled exceptions.
- Never confuse a VPN or route failure with a website result.

### Records

- Give every run and place attempt stable identifiers.
- Append and flush an attempt record before proceeding.
- Record effective configuration and the ordered candidate list for the run.
- Treat the exit IP as an observation, not a stable identifier for a place.

## Browser policy

Both probes should use a real installed Chrome or Edge process and attach to it
for control. Let the browser provide its genuine TLS, HTTP and client-hint
behaviour. Do not attempt to reproduce those details manually with Python
headers.

For each connection place:

1. establish and verify the place and exit IP;
2. launch a fresh browser process;
3. run the one source-specific browser attempt;
4. close the browser completely; and
5. only then change connection place.

This prevents DNS caches, service workers and TCP, HTTP/2 or QUIC connections
from crossing place boundaries.

Use headed mode by default during the exploratory phase. Keep browser language
at English UK, but record the language actually rendered. A location may still
produce a localized site. Do not manufacture a `Referer`; follow a normal
navigation path when the site requires one.

Use a dedicated profile policy for each source and record it. For the immediate
trial, preserve the existing Bet365 profile because it contains useful cookie
and odds-format state. Marathonbet should move from Playwright-launched Chromium
to the same ordinary-browser attachment pattern so a Python automation identity
is not an avoidable variable. Whether later attempts use a persistent baseline
profile or disposable copies should be decided from live evidence.

## Candidate ordering

The acquisition order is deterministic and source-specific, not randomized.
This minimizes expected time to valid odds and makes console behaviour easy to
understand.

Initial recommendation:

### Bet365

1. Try `Direct` first because it returned 200 in both replicated runs and avoids
   a VPN switch.
2. Try places already shown to render the Bet365 application and odds in a real
   browser, once such evidence exists.
3. Try the 17-place replicated common set.
4. If necessary in later runs, expand to the remaining places among Bet365's 44
   repeated HTTP successes.

### Marathonbet

1. Do not try `Direct` by default because it returned 403 in both replicated
   runs.
2. Try places already shown to render Marathonbet sumo odds in a real browser.
3. Try the 17-place replicated common set.
4. If necessary in later runs, expand to the remaining places among
   Marathonbet's 31 repeated HTTP successes.

The first live run will begin generating browser-level evidence. Later ordering
should rank successful browser acquisitions above HTTP-only candidates. Do not
infer English presentation merely from a country's name.

Allow explicit `--place` arguments for a controlled single-place or ordered
subset test. An automatic run uses the configured source-specific list.

## Per-place outcome model

HTTP status alone is insufficient. Record one terminal outcome for each
site/place attempt, with supporting detail:

- `vpn_failed` - the requested connection state could not be established;
- `network_not_ready` - no verified exit IP was obtained;
- `http_451` - legal refusal; persist the exclusion and do not try to bypass it;
- `http_rejected` - a 403 or another non-success response;
- `browser_failed` - the ordinary browser could not navigate or render;
- `challenge_or_refusal` - a nominal 200 rendered a challenge or refusal page;
- `unexpected_language` - the site rendered but the current adapter cannot
  interpret its language;
- `sumo_absent` - the site rendered but no sumo market was offered;
- `odds_absent` - sumo was present but no priced bouts were available;
- `parse_failed` - relevant content was visible but could not be parsed;
- `target_date_mismatch` - parsed odds did not belong to the requested day;
- `validation_failed` - parsed data did not satisfy the common model; or
- `success` - validated target-day odds were persisted.

A 403 remains useful evidence but does not create a permanent exclusion. A 451
does. `sumo_absent` and `odds_absent` are normal availability observations, not
proof that the scraper is broken.

## Source-specific behaviour

### Bet365

Retain the proven ordinary-Chrome/CDP launch. The adapter should:

- open a normal Bet365 entry route and wait for the application, rather than
  treating a changed hash as proof that content rendered;
- recognize the Sumo sport page independently from the changing bout route;
- follow the rendered `To Win Bout` market or its structural equivalent;
- record rendered language and distinguish missing sumo from failed navigation;
- accept decimal or fractional displayed prices and normalize to decimal;
- validate that two distinct competitors and two valid prices exist per bout;
- validate the listing date against the target date; and
- save only bounded diagnostics when unexpected rendered content prevents
  classification.

The existing direct sport route and UI-click fallbacks remain useful. They
should be observable steps with distinct timeouts and outcomes, not one generic
failure message.

### Marathonbet

Replace Playwright's own browser launch with an ordinary installed-browser
process plus attachment. Retain the existing event discovery and event-page
parsers. The adapter should:

- recognize the listing as rendered before searching it;
- distinguish a localized page, missing sumo listing and empty odds market;
- follow each discovered bout page with bounded navigation;
- retain all valid bouts even if one event has an incomplete displayed start;
- avoid writing a separate `unknown_start.json` when the common listing date
  can safely supply the target date;
- validate two-way prices and target date before success; and
- make one acquisition attempt per place rather than sleeping 30 minutes while
  holding the same run and connection strategy.

Later scheduling can start a fresh run at another time. The old 30-minute loop
can remain available through the compatibility script until the replacement is
proven.

## Persistence

Runtime output belongs under:

```text
files/output/misc/Betting/
    bet365/
    marathonbet/
    probes/
    browser_profiles/
    diagnostics/
```

Successful source JSON retains the established broad model: source, timezone,
acquisition timestamp, event start, bouts, competitors and decimal prices.
Add acquisition provenance without breaking current analysis unnecessarily:

- run ID;
- target date;
- connection place and location ID;
- observed exit IP;
- browser product/version and profile policy; and
- the successful attempt timestamp.

Do not discard a valid acquisition merely because another source failed. Do
not commit routine output. Selected research snapshots may still be copied
intentionally into `special_outputs` or the currently retained evidence area.

Append-only attempt records belong under `probes/` and must survive interruption.
Routine failures should not produce a screenshot and page dump for every place.
Save bounded diagnostics for an unclassified rendered page or parse failure,
or when explicitly requested with a diagnostics option.

## Console behaviour

The operator should be able to see progress without reading diagnostics:

```text
Target: Bet365 odds for 2026-11-22
Window: normal (started 10:14 Europe/London)
Attempt 1/18: Direct
  Exit IP: ...
  Browser: site rendered; sumo absent
Attempt 2/18: 181 Canada - Vancouver
  Exit IP: ...
  Browser: 8 priced bouts for 2026-11-22
  Saved: ...
Restored initial VPN state: Direct
```

Each attempt must say which stage failed. A source-level `no odds` result must
not be presented as a VPN or browser failure.

## Exit status

Use distinct process outcomes so a future scheduler can act sensibly:

- `0` - valid target-day odds persisted;
- `1` - candidates exhausted without valid odds;
- `2` - invocation or configuration error, including the normal time-window
  rule unless explicitly overridden;
- `3` - environment/control failure prevented a trustworthy run; and
- `130` - operator cancellation.

The exact numeric allocation can change during implementation, but success,
ordinary unavailability and broken execution must remain distinguishable.

## Testing

Retain the existing parser tests and add tests for:

- target-date capture and validation, including a run crossing midnight;
- the 10:00--22:00 Europe/London start window under GMT and BST;
- deterministic source-specific candidate ordering;
- `Direct` and verified ExpressVPN preparation;
- connect-command timeout followed by successful state verification;
- exit-IP readiness and fallback provider;
- advancing after an ordinary place outcome;
- stopping immediately after persisted success;
- 451 exclusion and 403 non-exclusion;
- append-and-flush attempt records;
- browser closure before changing place;
- restoration after success, exhaustion, exception and cancellation;
- classification of rendered-no-sumo, no-odds, localization, parse failure and
  target-date mismatch; and
- no partial or invalid odds file being reported as success.

Automated tests must use fakes and recorded page fixtures. They must not switch
the live VPN or contact bookmaker sites.

## Minimal live-trial implementation

Because final-day odds are time-sensitive, the first implementation should be
small:

1. add Betting-owned connection preparation/restoration adapted from the
   tested VPN sandbox;
2. add a simple append-only attempt record;
3. add place iteration and target-date validation to Bet365;
4. change Marathonbet to ordinary-browser attachment, then add the same place
   iteration and validation;
5. use `Direct` plus a short explicit candidate subset for Bet365 and a short
   subset of the replicated 17 for Marathonbet;
6. run each probe manually after 10:00; and
7. preserve successful JSON and only the diagnostics needed to explain a new
   failure class.

Do not delay the live trial to implement all 44 or 31 candidates, a scheduler,
a database, automatic statistical ranking, generalized bookmaker interfaces or
the VPN sandbox's full service-restart circuit breaker.

## Acceptance criteria for the exploratory version

For each source, the probe is ready for a live trial when it can:

1. state the target date and ordered places before changing network state;
2. enforce or explicitly override the UK start window;
3. establish and verify `Direct` or one configured ExpressVPN place;
4. record an exit IP;
5. start and completely stop a real browser for that place;
6. classify the source-specific result;
7. advance to the next place after ordinary failure;
8. persist and validate target-day decimal odds on success;
9. stop after success; and
10. restore the initial VPN state and leave an append-only attempt record.

The experiment does not require both sites to succeed. A well-classified,
restored run that exhausts its candidates is still a valid probe result.

