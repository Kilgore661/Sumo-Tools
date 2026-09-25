# Torikumi Infrastructure and Annotated Torikumi Proposal

## Status

This document records the agreed work-in-progress design. It creates no
production behaviour by itself. Names, particularly the public name
`Torikumi`, remain provisional until the first artifact can be inspected.

## Motivation

The initial public artifact presents upcoming bouts together with Elo-89
ratings and the modelled probability that each rikishi will win. Its purpose
is to help a reader understand the upcoming torikumi, not to evaluate whether
the model's forecasts were correct.

The first version is deliberately prospective. Applying the same annotations
retrospectively may later prove useful, but that question should be considered
only after the upcoming-bout artifact has been produced and assessed.

## Public artifact

The working public menu and artifact name is **Torikumi**.

The page will show the available upcoming bouts by basho day. If more than one
future day is available, the reader can select the day in the Options panel.
The earliest available day is selected by default. A day must be offered
because it exists in the produced data, not because the browser or site
builder infers that it ought to be available from the wall clock.

The initial table is conceptually:

| East | | Forecast | | | West |
|---|---:|---:|---:|---:|---|
| Shikona | Elo89 | East wins | West wins | Elo89 | Shikona |
| Fred | 1540 | 25% | 75% | 1731 | Bill |

The `Forecast` heading spans two probability columns. Ratings and
probabilities are essential properties of this artifact rather than optional
overlays. The two probabilities must be complementary and must be calculated
from the displayed pre-bout ratings by the selected Elo-89 model.

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

For example, if the newest represented basho has results only through Day 12
and contains a published Day 13 torikumi, Day 13 is the next available future
day even if that snapshot is stale. The page should disclose its represented
cutoff, but staleness must not make the build nondeterministic.

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
    manifest.json
    future.json
    raw/
        2026 09/
            14.html
            15.html
```

The exact filenames and schema are implementation decisions, but raw
advance-torikumi snapshots must not be written into the existing
`files/output/HTML results` cache.

## Infrastructure boundary

The new package is `src.infra.torikumi`. It owns:

1. identifying plausible future-day source URLs from a supplied production
   snapshot;
2. downloading advance `Results.aspx` pages into its separate raw cache;
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

`History` represents completed bout evidence. `Future` represents published
scheduled bouts whose outcomes are not part of the production snapshot.

A provisional logical shape is:

```python
@dataclass(frozen=True)
class FutureBout:
    order: int
    east: RikId
    west: RikId


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
- outcomes are not required or represented as forecast annotations;
- availability is represented by membership rather than inferred from time;
- zero, one, or several future days can be represented; and
- every represented day is later than the completed-results cutoff of the
  supplied snapshot.

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

It may inspect result columns for diagnostics. If a candidate advance page
contains results, it should report that fact clearly. The exact acceptance
policy can be refined from real fixtures without affecting the existing
History pipeline.

Some HTML interpretation will initially duplicate the results parser. This is
intentional isolation. Shared low-level parsing should be extracted only if
fixtures and tests later demonstrate a genuinely stable common boundary.

## Retrieval policy

Completed-results retrieval is a historical full-prefix, gap-filling process.
Advance-torikumi retrieval is different: it is time-sensitive and cannot be
assumed to be retrospectively recoverable from an evolving source URL.

For the first implementation, the Future updater may use the supplied
History's latest represented basho and completed day to probe a small bounded
set of later days. Any candidate day must also be bounded by Day 15. A page is
retained only when the new parser positively recognizes a usable torikumi.

The implementation must not hard-code an assumption that two advance days are
available on a particular basho day. It should publish whichever future days
were actually acquired and validated. Publication schedules can be tested and
documented empirically without becoming browser logic.

## Site-facing producer

The infrastructure `Future` is not itself the website artifact. A new
producer under `src.analysis.site89` will consume:

```text
Future + existing Elo89Artifacts -> Annotated Torikumi site data
```

For each scheduled bout it will:

1. obtain the applicable pre-bout Elo-89 rating for both rikishi;
2. calculate complementary win probabilities;
3. require ratings rather than treating them as an optional display mode; and
4. emit the site-facing rows and day-selection metadata.

The policy for genuinely unavailable ratings must be decided from real data.
The producer must not silently present an unannotated bout as though the
artifact were complete.

## Site integration

`make_site89` remains an assembler. It will not load `History`, `Future`, or an
Elo-89 run and will not calculate probabilities.

Once the produced artifact exists, site integration will add:

- the provisional **Torikumi** menu entry;
- conditional availability driven by produced artifact metadata;
- a page for the available future days;
- radio controls when day selection is meaningful;
- the grouped Forecast table heading; and
- the required table renderer and tests.

The menu must not be enabled merely because the wall clock appears to be
inside a basho. It is enabled when the production bundle contains a usable
Annotated Torikumi artifact.

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

The first implementation should be supported by fixtures and tests covering:

- a valid torikumi-only page;
- preservation of bout order and East/West orientation;
- malformed or empty pages;
- a candidate page that unexpectedly contains results;
- zero, one, and two available future days;
- Day 15 bounds;
- deterministic Future serialization;
- rating and probability calculation for every published bout;
- complementary displayed probabilities; and
- absence of changes to the existing results, History, and live-store path.

## Addendum: decision not to patch the existing results parser

During design, we considered adapting the existing daily-results parser to
collect the scheduled bouts it already encounters while parsing a
`Results.aspx` page. When the page contained no results, or contained missing
results, it could have handed the collected torikumi to a `Future` accumulator
before returning `None` to its existing caller. This would have reused the
current row-parsing code efficiently and, if carefully implemented, need not
have changed the `History` returned by `parser2`.

We decided not to take that route for the first implementation. The existing
results parser and History-production chain are mature, important production
code. Adding a second output and a new side effect would increase their
responsibilities and create a risk of unintended consequences in order to
support an artifact whose usefulness and final form are still prospective.

The independent torikumi parser therefore accepts the cost of reimplementing
some HTML interpretation. At this stage, isolation and a small failure radius
are more valuable than eliminating that duplication. A failure in the new
path should at worst prevent production of `Future` or Annotated Torikumi; it
must not affect completed results, canonical History publication, the live
store, or existing producers.

This is not a decision that the two parsers must remain separate forever.
After the new artifact has been exercised against real pages and protected by
representative fixtures and tests, stable shared parsing operations may be
extracted if doing so clearly reduces duplication without weakening the
existing production boundary.

