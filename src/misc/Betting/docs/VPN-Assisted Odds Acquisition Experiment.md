# VPN-assisted sumo-odds acquisition experiment

## Status and ownership

This is an exploratory design owned by the Sumo-Tools `Betting` project. Its
subject is the acquisition of external sumo odds for comparison with Elo-89,
so its requirements, observations and eventual source adapters belong in this
repository.

`X:\VPN` is a separate sandbox repository. It currently provides useful
ExpressVPN control and URL-survey experiments, but it is not part of the
Betting architecture and must not silently become a production dependency.
The experiment may:

- continue to use and refine the sandbox while the questions are unsettled;
- promote suitable ideas or code into proper packages later;
- create Betting-owned VPN/browser modules where that produces a clearer
  design; or
- conclude that sufficiently reliable acquisition is not possible.

No decision to build a finished "get odds from wherever possible" package has
been made.

## Purpose

The eventual analytical purpose is to compare bookmaker probabilities with
pre-bout probabilities derived from Elo-89. Before that analysis is credible,
we need to know whether external odds can be acquired consistently enough to
form a useful record.

The current research question is:

> Is there a repeatable combination of bookmaker site, connection place, ordinary
> browser state, language and acquisition time that yields sumo odds?

Use the following notation:

- `s` is a candidate bookmaker site;
- `p` is an ExpressVPN place or the special place `none`, meaning the ordinary
  connection with the VPN disconnected;
- `r` is a repeated experimental run; and
- an observation concerns one `(s, p, r)` combination.

The active initial sites are Marathonbet and Bet365, both of which already have
fragile source-specific odds prototypes. NetBet was included in the first HTTP
surveys but has been removed from the active candidate set because obtaining
odds requires a login. Its historical observations remain useful evidence about
the probe itself, but a reachable NetBet homepage does not advance the public
odds-acquisition experiment. Other candidate sites may be added without
changing the experimental model.

## What must be distinguished

Acquisition is a sequence of separate questions:

1. Can the experiment establish `p` and provide a verified exit IP, either by
   connecting ExpressVPN or by explicitly disconnecting it for `none`?
2. Can a client reach `s` through that connection?
3. Can an ordinary browser render the site's real application?
4. In what language and odds format is it rendered?
5. Does the site offer sumo through that place at that time?
6. Are priced bouts currently available?
7. Can a source-specific adapter identify and persist those odds correctly?

Success at one stage does not imply success at the next. In particular, an
HTTP 200 is necessary evidence of a successful HTTP request but is not proof
that the application, sumo market or odds are available. A site can also
return HTTP 200 for a challenge, regional landing page, empty application
shell or unavailability message.

## Why a real browser matters

The `X:\VPN` URL tester uses a fixed, mainstream browser-style HTTP identity.
That avoids the most obvious mistake of identifying the request as a Python
crawler. It still uses Python's networking and TLS implementation, does not
execute JavaScript and does not reproduce a browser's cookies, client hints,
HTTP/2 or HTTP/3 behaviour, connection handling or rendered application.

The purpose of browser-like settings is not to bypass a refusal. It is to
remove avoidable implementation differences so that an observed failure is
more plausibly about the site/VPN combination. The final odds acquisitions
will use a regular browser, so the authoritative experiment should eventually
use one too.

The technology remains an implementation detail. Selenium, Playwright over a
browser debugging connection, or another controller may be suitable. The
requirement is:

> Using a real, normally configured browser, determine whether site `s` is
> usable through connection place `p`, and record the result reproducibly.

The controller may attach to an exposed running browser, launch an installed
browser and attach to it, or create a fresh browser process. The Bet365
prototype already demonstrates one possible arrangement by launching ordinary
Chrome and attaching through its debugging interface.

## Controlled browser experiment

Settings that we control should be internally consistent and as close as
practical to an ordinary browser session. Prefer letting the actual browser
produce its genuine user agent, TLS behaviour and client headers over manually
imitating them.

Keep the following fixed and record them where relevant:

- browser product and version;
- headed or headless mode;
- browser language, initially English UK;
- profile or context policy;
- viewport and other presentation settings;
- JavaScript, cookies and ordinary browser features;
- entry URL and navigation procedure; and
- timeouts and criteria for deciding that rendering succeeded or failed.

Do not manufacture a `Referer`. If a site needs a natural navigation path,
follow that path in the browser. Do not solve or evade CAPTCHAs, authentication,
explicit regional refusals or legal blocks.

Browser language needs explicit observation even with an English UK
preference. A site may choose language from the exit country, URL, cookies,
account or server-side policy. English labels such as `Sumo`, `To Win Bout` and
cookie controls may be absent. Rikishi spelling, decimal separators and odds
presentation may also vary.

### The direct `none` place

`none` is a first-class member of the place matrix, not a fallback after VPN
locations fail. It means that ExpressVPN is explicitly disconnected and the
site is visited over the ordinary network connection. This is an important
baseline and may be the correct route for a UK-facing site.

Record and verify the public exit IP for `none` in the same way as for VPN
places. Apply the same HTTP, rendering, language, market and extraction checks,
and aggregate `(s, none, r)` observations normally. A 451 for `none` has the
same site/place scope and exclusion meaning as a 451 through a named VPN
place. Restore the connection state that existed before the complete
experiment after the run finishes or is interrupted.

### Isolation between connection places

After establishing a connection place, verify the connection state and exit IP
before testing any site. For `none`, this includes verifying that ExpressVPN is
disconnected. Browser networking can retain DNS state, service workers, caches
and TCP, HTTP/2 or QUIC connections associated with an earlier route. The
safest initial design is therefore:

1. establish and verify place `p`, including explicit disconnection for
   `none`;
2. start a fresh ordinary browser process;
3. test each candidate site through `p`, using isolated tabs or contexts;
4. record the observations; and
5. close the browser before changing connection place.

This permits all sites to be tested during one connection state while avoiding
reuse of a browser process across different places.

## HTTP outcomes

Keep network and website outcomes separate.

### HTTP 200

Record a 200 as a successful HTTP observation, not as proof of usable odds.
Continue to sample it in later runs. At browser level, also classify whether
ordinary application content rendered or whether the 200 contained a
challenge, refusal, empty shell or other unexpected content.

### HTTP 403

A 403 is inconclusive. It can arise from geography, a known VPN address, bot
protection, client or TLS identity, transient policy, or some combination of
these. Continue sampling it. A small browser-level control sample of repeated
403 locations is valuable because it reveals whether the lightweight HTTP
client is producing false negatives.

### HTTP 451

HTTP 451 means `Unavailable For Legal Reasons`. It is a completed and
informative response, just as a 200 is. Persist a 451 for the specific
site/place combination and exclude that combination from ordinary later
batches. Do not attempt to bypass it with a browser or another request
technique.

An explicit manual recheck can remain possible because site policies and VPN
endpoints can change. The record should retain the observation date and exit
IP rather than asserting that the restriction is permanent or applies to all
sites in that country.

### VPN and transport failures

A VPN connection failure, stale or unverifiable connection, DNS failure, TLS
failure or request timeout is not a website response. Classify it separately
and leave the site/place pair eligible for a later run.

## Initial evidence

The first near-catalogue HTTP surveys on 2026-11-18 produced:

| Site | Locations attempted | HTTP 200 | HTTP 403 | HTTP 451 | VPN/transport failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Marathonbet | 217 | 31 | 157 | 25 | 4 |
| Bet365, first full run | 217 | 1 | 149 | 1 | 66 |
| Bet365, second full run | 215 | 3 | 194 | 1 | 17 |
| NetBet (subsequently excluded) | 215 | 171 | 0 | 0 | 44 |

Estonia returned HTTP 200 for Bet365 in both full runs. Luxembourg and
Slovenia also returned 200 in the second. This is evidence about those
particular requests, not proof that the places will always work or that the
Bet365 application and sumo odds were available.

The differing VPN failure counts show that rapid switching can degrade the
experiment itself. Conversely, the Marathonbet run received 213 completed HTTP
responses from 213 distinct recorded exit IPs; its 403 and 451 observations
cannot generally be reclassified as simple ExpressVPN connection failures.

These surveys are not maps of bookmaker legality. A response can reflect the
bookmaker, infrastructure provider, VPN-address reputation, client identity,
local regulation or another intermediary.

### Replicated `vpn_probe` evidence

The `X:\VPN` sandbox subsequently implemented a repeatable `vpn_probe`
collector with randomized place order, `Direct` as a first-class place,
append-only observations, verified exit-IP readiness, bounded operations and
recovery from an unresponsive ExpressVPN control plane. Two complete
all-location runs finished on 20 and 21 November 2026.

| Target | First run: HTTP 200 | Second run: HTTP 200 | Places returning 200 in both |
| --- | ---: | ---: | ---: |
| Bet365 | 52/216 | 62/216 | 44 |
| Marathonbet | 31/216 | 32/216 | 31 |
| NetBet, now excluded | 216/216 | 216/216 | 216 |

Seventeen place names returned HTTP 200 for both active sites in both runs.
Most places received a different exit IP in the second run, so this replication
supports treating the ExpressVPN place as the actionable selector and the exit
IP as an observation rather than a permanent identity.

`Direct`, the ordinary UK connection with ExpressVPN disconnected, was also
reproduced: Bet365 returned 200 and Marathonbet returned 403 in both runs. This
confirms the value of keeping `Direct` in the matrix rather than assuming that
a VPN is always helpful.

This supersedes the early impression that Bet365 was necessarily the hardest
site to reach. In the controlled replicated runs, Marathonbet had the lower 200
rate, while Bet365 was more variable between runs. These remain lightweight
HTTP observations, not evidence that either site rendered sumo odds.

The sandbox's current default configuration still includes NetBet. Future
Betting-directed cohorts should omit it. Historical NetBet rows must not be
deleted or silently pooled with later two-target cohorts; the effective target
list and protocol belong in each run's provenance.

## Repeated, non-greedy survey

The next experiment should build a history, not search greedily until one
place works. Treat candidate sites and places as a matrix and observe the
eligible combinations over `n` runs.

To reduce VPN switching, organize a run primarily by place. The eligible set
includes `none` unless a prior 451 excludes it for every site being tested:

1. select an eligible batch of places;
2. randomize their order;
3. connect once to each place;
4. test all candidate sites there, varying site order between runs; and
5. close the browser or HTTP session before the next VPN switch.

Runs should be spread over time rather than executed immediately back to back.
Use batches smaller than the complete 240-plus-location catalogue, allow a
cooling-off period, and repeat a few control places near the beginning and end
of a run. Those controls can reveal deterioration in ExpressVPN or in the
experimental client during a long batch.

The program should not stop after finding one successful place. A single 200
does not estimate reliability, and stopping early would systematically give
more observations to locations early in the ordering.

## Raw observations and aggregation

Each raw observation should be immutable and contain at least:

- run identifier and timestamp;
- target site and requested URL;
- canonical connection place, including `none`, and observed exit IP;
- browser or HTTP-client identity and relevant configuration;
- main-document HTTP status, final URL, elapsed time and response size;
- separately classified VPN, DNS, TLS or transport failure;
- rendered language and presentation, when a browser is used;
- whether ordinary application content rendered;
- whether sumo was present;
- whether priced bouts were present; and
- whether source-specific extraction succeeded.

Preserve raw runs as the evidence. Derive, rather than manually maintain, a
summary for each site/place pair containing:

- attempts and counts by outcome;
- observed 200 rate;
- browser-render success rate;
- first and latest observations;
- exit IPs seen;
- changes in result over time; and
- exclusion after a recorded 451.

"Always works" must mean `n` successes from `n` recorded attempts over the
chosen observation period. It is not a promise of future success. Evidence is
stronger when it covers different days and multiple exit IPs. Depending on the
results, a high observed success rate may be more useful than requiring a
perfect record.

## Decision sequence

The experiment has explicit gates:

1. **HTTP survey:** identify repeatable responses while measuring VPN/client
   failures and retaining inconclusive 403 results.
2. **Browser survey:** determine whether selected site/place pairs render an
   ordinary application consistently, including a small 403 control sample.
3. **Market survey:** determine whether sumo and priced bouts appear at useful
   times and in a presentation we can interpret.
4. **Extraction trial:** run or create a source-specific adapter and persist
   successful odds with provenance.
5. **Analytical decision:** decide whether coverage and reliability justify a
   proper Betting package and Elo-89 comparison pipeline.

Failure at a gate is a valid experimental result. It may lead to abandoning a
source, retaining only opportunistic snapshots, adding other candidate sites,
or deciding not to build generalized acquisition infrastructure.

## Immediate next design task

The sandbox now implements the lightweight repeated HTTP survey well enough to
collect useful evidence. Before changing its target list, it should persist the
complete effective configuration and ordered target manifest for each run so
that the three-target historical cohort cannot be confused with later
Bet365/Marathonbet cohorts.

The next Betting-owned design question is the browser stage: how selected
site/place candidates will be tested with an ordinary browser for rendered
application content, language, sumo availability and priced bouts. Selenium,
Playwright and the eventual package boundary remain implementation choices.
The current proposal for that stage is
[Improved Site-Specific Odds Probes Proposal.md](Improved%20Site-Specific%20Odds%20Probes%20Proposal.md).

