# Torikumi Infrastructure and Annotated Torikumi Proposal

## Status

This document records the implemented work-in-progress design. The public
name `Torikumi` remains provisional while the artifact is evaluated.

## Motivation

The public artifact presents published bouts together with Elo-89
ratings and the modelled probability that each rikishi will win. Its purpose
is to help a reader understand action they have not yet watched, not to
evaluate whether the model's forecasts were correct. A reader may be behind
the live results, so the artifact retains every torikumi published for the
represented basho even when its results are already present in `History`.

The artifact remains prospective in intent: no result or winner information
is published. Retaining earlier days is a viewing-lag feature, not model
backtesting.

## Public artifact

The working public menu and artifact name is **Torikumi**.

The page shows every acquired torikumi for the represented basho. The Options
panel always declares Days 1 through 15. Published days are enabled,
unpublished days are disabled, and the latest available day is selected by
default. Fifteen declared values deliberately make the shared UI manager use
a dropdown throughout the basho rather than changing from radio buttons to a
dropdown part-way through. A day is enabled because it exists in the produced
data, not because the browser or site builder infers availability from the
wall clock.

The Options panel also provides division radio buttons from **Makuuchi**
through **Jonokuchi**, with Makuuchi selected by default. A bout involving
rikishi from adjacent banzuke divisions belongs to the higher division, which
matches the section in which a visitor's bout is conventionally presented and
avoids displaying the same bout twice.

The **Torikumi** navigation link is always enabled. When the produced artifact
contains no published days, the page remains reachable and its content
panel displays **No torikumi**. Data availability is a page-content state, not
a navigation state.

The table is conceptually:

| East | | | West | | |
|---|---:|---:|---:|---:|---|
| Shikona | Elo89 | P(win), spanning both probability columns | | Elo89 | Shikona |
| Fred | 1540 | 25% | 75% | 1731 | Bill |

`East` and `West` each span their three associated columns. Ratings and
probabilities are essential properties rather than optional overlays. The two
probabilities must be complementary and calculated from the displayed
pre-bout ratings by Elo-89. A normal Shikona click opens the rikishi's SumoDB
page; Alt-click opens their Elo89 career history, matching The Banzuke.

The first version will not display:

- results, winners, or kimarite;
- whether the favourite won;
- prediction-correctness marks; or
- aggregate forecast evaluation.

Questions such as calibration, favourite accuracy, Brier score, and log loss
belong to model appraisal elsewhere.

## Snapshot semantics

The production system operates on supplied data, not on an inference about
the real-world date. `Current`, `completed`, and `future` are relative to the
production snapshot.

For example, if the newest represented basho has results through Day 12 and
contains a published Day 13 torikumi, Days 1 through 13 are available even if
that snapshot is stale. The page discloses the rating cutoff used for the
selected day, but staleness must not make the build nondeterministic.

The site builder must not decide:

- whether the wall-clock date falls within a basho;
- which results ought to exist at the current time;
- whether the live store is fresh; or
- how many advance torikumi ought to have been published.

It renders the days declared by the produced artifact.

## Source lifecycle

`Results.aspx` is understood primarily as a torikumi page whose bouts may
later acquire results. The same source URL therefore has a lifecycle:

```text
unavailable -> published torikumi -> completed results
```

The page may be revised after its first publication. Acquisition must not
assume that the first downloaded representation is immutable.

The existing results cache, parser, canonical `History`, and live-store path
will not be modified for the first implementation. Their reliability is more
important than avoiding a modest amount of duplicated HTML interpretation.

The new infrastructure will use a separate cache and persistence root under:

```text
files/output/torikumi/
```

A possible initial layout is:

```text
files/output/torikumi/
    future.json
    raw/
        2026 09/
            14.html
            15.html
```

The exact filenames and schema are implementation decisions, but raw
torikumi snapshots must not be written into the existing
`files/output/HTML results` cache.

## Infrastructure boundary

The new package is `src.infra.torikumi`. It owns:

1. identifying the bounded day source URLs from a supplied production
   snapshot;
2. downloading `Results.aspx` pages into its separate raw cache;
3. positively recognizing a usable torikumi;
4. extracting ordered and oriented scheduled bouts;
5. constructing a coherent `Future` object; and
6. persisting that object under `files/output/torikumi`.

It does not:

- calculate ratings or probabilities;
- construct site-facing tables;
- mutate or publish `History`;
- write to the existing results cache; or
- infer artifact availability in browser code.

Initially this may run as a separate explicit production command. Integration
with the continuously running tracker can be considered after the new path
has been exercised during real basho.

## Future domain object

`History` represents completed bout evidence. The provisionally named
`Future` represents published schedules independently of their results. It
may therefore include days at or before `completed_through`; result data is
diagnostic input and is never a site-facing annotation.

A provisional logical shape is:

```python
@dataclass(frozen=True)
class FutureBout:
    order: int
    east: RikId
    west: RikId
    east_shikona: str | None
    west_shikona: str | None


@dataclass(frozen=True)
class FutureDay:
    day: Day
    bouts: tuple[FutureBout, ...]
    source_url: str
    downloaded_at: datetime


@dataclass(frozen=True)
class Future:
    date: Date
    completed_through: Day | None
    days: tuple[FutureDay, ...]
```

The final model may contain additional provenance and validation fields. Its
important initial properties are:

- bout order is preserved;
- East/West orientation is preserved;
- source shikona are retained for new `Mz` rikishi not yet known elsewhere;
- outcomes are not required or represented as forecast annotations;
- availability is represented by membership rather than inferred from time;
- zero through fifteen published days can be represented; and
- completed and result-free schedules have the same site-facing semantics.

Ratings do not belong to `Future`. It is a model-independent representation
of published scheduled bouts.

## Torikumi parser

The new parser will be independent of the mature daily-results parser. It
will parse a downloaded `Results.aspx` document sufficiently to establish:

- basho and day;
- the presence of the expected torikumi table;
- a credible non-empty collection of bout rows;
- the stable rikishi identities on each row;
- East/West orientation; and
- source bout order.

It counts result columns for diagnostics, but continues to extract the whole
schedule. Result values are not copied into the site-facing CSVs.

Some HTML interpretation will initially duplicate the results parser. This is
intentional isolation. Shared low-level parsing should be extracted only if
fixtures and tests later demonstrate a genuinely stable common boundary.

## Retrieval policy

Completed-results retrieval is a historical full-prefix, gap-filling process.
Torikumi retrieval is different: future pages are time-sensitive and cannot
be assumed to be retrospectively recoverable from an evolving source URL.

The updater uses the supplied History's latest represented basho and probes
all Days 1 through 15. A page is retained only when the new parser positively
recognizes a usable torikumi. Probing the full bounded range retains schedules
for viewers who have not yet watched days whose results are already known.

The implementation does not hard-code how many advance days are available on
a particular basho day. It publishes whichever days were actually acquired
and validated. Publication schedules can be tested and documented empirically
without becoming browser logic.

## Site-facing producer

The infrastructure `Future` is not itself the website artifact. A new
producer under `src.analysis.site89` will consume:

```text
Future + existing Elo89Artifacts -> Annotated Torikumi site data
```

For each scheduled bout it:

1. obtains the latest available same-basho Elo-89 rating strictly before that
   bout's day, using basho-start ratings for Day 1;
2. calculate complementary win probabilities;
3. require ratings rather than treating them as an optional display mode; and
4. emit the site-facing rows, day-selection metadata, and the rating snapshot
   cutoff actually used.

An `Mz` rikishi is absent from the banzuke and is not assigned an Elo89 rating.
Their Elo89 is displayed as `-`, and both probabilities for that bout are
displayed as `-`. The source shikona is used when the canonical name store does
not yet know the entrant. An `Mz` bout is classified with its ranked opponent;
an `Mz`-only bout appears under Jonokuchi, the lowest supported presentation
group. Missing ratings for banzuke-listed rikishi remain a hard producer error
rather than being disguised as expected `Mz` absence.

For the initial prospective artifact, producing Torikumi data does not trigger
an Elo-89 replay or rebuild the other site89 producer outputs. The producer
loads the existing `Elo89Artifacts`. For each day it uses the latest available
day-end snapshot from an earlier day, otherwise the basho-start snapshot. It
reports the per-day cutoff rather than implying that the ratings are fresher
than they are.

This deliberately permits a Future snapshot to be newer than the available
within-basho ratings while the artifact is being evaluated. It is sufficient
to produce and inspect a working example so long as the Elo-89 artifacts
contain the represented basho and ratings for every scheduled rikishi. A
future production-orchestration design may enforce synchronized refreshes,
but that is outside this prospective implementation.

## Site integration

`make_site89` remains an assembler. It will not load `History`, `Future`, or an
Elo-89 run and will not calculate probabilities.

Once the produced artifact exists, site integration will add:

- the provisional **Torikumi** menu entry;
- a permanently enabled link to the Torikumi page;
- a **No torikumi** panel state when the artifact contains no available days;
- a page for every published day in the represented basho;
- a stable Days 1-to-15 dropdown with unpublished days disabled;
- grouped three-column East and West table headings;
- standard clickable Shikona links with Alt-click career navigation; and
- the required table renderer and tests.

The menu does not use the wall clock or produced-data availability to decide
whether it is enabled. The artifact data alone determines whether the page
shows available days or the empty state.

## Broader production context

In principle, production would benefit from one coherent in-memory snapshot
containing everything downstream producers need, rather than treating
`History` as the only central object. That snapshot might eventually include
History, Future, ratings, biographies, structural banzuke data, and other
established inputs.

The repository already has producer inputs and outputs that are not contained
in `History`, including Elo-89 artifacts, biography data, banzuke-comparison
structural output, and site-facing bundles. Persisting `Future` as files is
therefore consistent with the present architecture. Designing a unified
production-context object is outside this proposal.

## Initial verification

The implementation is supported by fixtures and tests covering:

- a valid torikumi-only page;
- preservation of bout order and East/West orientation;
- malformed or empty pages;
- a candidate page that unexpectedly contains results;
- completed and result-free torikumi pages;
- all fifteen selector entries and disabled unpublished days;
- Day 15 bounds;
- deterministic Future serialization;
- rating and probability calculation for every published bout;
- day-relative rating cutoffs;
- `Mz` shikona and unknown-rating presentation;
- complementary displayed probabilities; and
- absence of changes to the existing results, History, and live-store path.

## Addendum: decision not to patch the existing scraper or results parser

During design, we considered adapting both parts of the existing results path.
The existing scraper could have been extended to request advance
`Results.aspx` pages, while the daily-results parser could have collected the
scheduled bouts it already encounters. When the page contained no results, or
contained missing results, the parser could have handed the collected
torikumi to a `Future` accumulator before returning `None` to its existing
caller. This would have reused the current downloading and row-parsing code
efficiently and, if carefully implemented, need not have changed the
`History` returned by `parser2`.

We decided not to take that route for the first implementation. The existing
results scraper, results cache, parser, and History-production chain are
mature, important production code. Advance pages also have different
acquisition requirements: they use a separate cache, may need repeated
refreshes, treat an unpublished page as normal absence, and validate the
presence of a torikumi rather than completed results. Extending the existing
path with those responsibilities, a second parser output, and a new side
effect would create a risk of unintended consequences in order to support an
artifact whose usefulness and final form are still prospective.

The independent torikumi scraper and parser therefore accept the cost of
reimplementing some HTTP acquisition and HTML interpretation. At this stage,
isolation and a small failure radius are more valuable than eliminating that
duplication. A failure in the new path should at worst prevent production of
`Future` or Annotated Torikumi; it must not affect completed results, the
existing raw-results cache, canonical History publication, the live store, or
existing producers.

This is not a decision that the two acquisition and parsing paths must remain
separate forever. After the new artifact has been exercised against real
pages and protected by representative fixtures and tests, stable shared HTTP
or parsing operations may be extracted if doing so clearly reduces
duplication without weakening the existing production boundary.

## WIP production commands

The WIP artifact can be refreshed without rebuilding Elo89. First
download every published torikumi for the latest History basho:

```text
python -m src.infra.torikumi --history-zip "files/output/Historys/1989_01 to 2026_11.zip"
```

Then annotate that `Future` using the ratings already present in the site-data
bundle:

```text
python -m src.analysis.site89.torikumi_cli --history-zip "files/output/Historys/1989_01 to 2026_11.zip"
```

Finally build the site locally without deploying to the configured server:

```text
py -m src.products.make_site89 --build-only
```

A complete site-data rebuild also consumes
`files/output/torikumi/future.json` when that file exists, but the WIP commands
above are the shorter path for exercising Torikumi without recomputing Elo89.

