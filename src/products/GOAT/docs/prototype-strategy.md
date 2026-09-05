# GOAT-o-Matic prototype strategy

## Purpose

The GOAT-o-Matic will be developed as a prototype. The prototype is an
instrument for discovering the requirements, not merely an implementation of
requirements assumed to be final in advance.

The current design process is intentionally iterative: make a defensible
choice, make it inspectable, use it to ask real questions, and revise the
requirements in response to what is learned.

## Development sequence

```text
History
  -> auditable factual CSVs
  -> clearly defined descriptive aggregates
  -> spreadsheet exploration
  -> minimal website prototype
  -> revised ideas about GOAT criteria
  -> additions to the producer where required
```

The website is not required for the first useful experiment. CSV output can be
loaded into a spreadsheet to ask questions such as:

- Who won the most yusho?
- What happens if total wins break a tie in yusho?
- Does changing the priority of two statistics materially change the leading
  group?
- Are apparently useful statistics measuring substantially the same thing?

These experiments should inform which ideas are worth putting into the first
website prototype.

## Facts, descriptive statistics and GOAT criteria

There are three distinct layers.

### Factual data

These are auditable projections of the source `History`, including banzuke
appearances, bouts, outcomes, performance markers and any available playoff
detail. Missing source data remains missing.

### Descriptive aggregates

These are straightforward calculations over the facts, published primarily
to make exploration convenient. Examples include numbers of yusho, recorded
wins and Makuuchi-banzuke basho.

Producing such a value does not assert that it is a measure of GOATness. It
only gives the spreadsheet and later website a precisely defined quantity to
work with.

### GOAT criteria and ranking semantics

These are the user's decisions about which descriptive values matter and how
they should be combined: for example, priority ordering, tie-breakers,
weighting or normalization. These decisions remain provisional until they
have been explored with real output.

## First prototype landmark

The first landmark is a spreadsheet-ready production dataset, not a website.
It should contain:

- `rikishi.csv`, containing identities and useful career boundaries;
- factual banzuke, bout, marker and playoff tables;
- `rikishi_summary.csv`, containing one row per candidate and a deliberately
  small collection of clearly defined descriptive aggregates; and
- a manifest and validation report describing provenance, coverage and
  completeness.

The summary must use names that expose important scope differences rather than
hide them behind labels such as `total_wins`. For example:

- `makuuchi_yusho_1958_onwards`;
- `makuuchi_doten_yusho_1958_onwards`;
- `makuuchi_W_1958_onwards`;
- `all_division_W_1989_onwards`; and
- `makuuchi_banzuke_basho_1958_onwards`.

The exact column set is allowed to evolve. Every column must nevertheless have
an exact definition and a stated data-coverage boundary.

## Date coverage

There is no single date boundary for every descriptive value.

- A Makuuchi-yusho count can use the data epoch beginning in 1958.
- A value requiring complete sub-sekitori bout records can use January 1989
  onwards.
- Future measures may have other dependencies and therefore other admissible
  periods.

The producer must preserve and publish enough coverage information for each
aggregate to declare its own valid period. Earlier missing lower-division
bouts must never be silently treated as zero wins or losses.

## From spreadsheet to website

After spreadsheet exploration identifies useful combinations, a minimal
website prototype can reproduce them with selectable factors and a complete
rikishi ranking. Its purpose is again investigative: seeing and operating the
interface may expose unclear definitions, unhelpful measures or missing data.

If a refined idea can be calculated from the retained facts, a new descriptive
aggregate can be added. If the idea requires facts not yet published, the
factual producer and its contract can be extended. Neither case should require
the product layer to reinterpret raw sumo data.

## Status of the requirements

The documentation should distinguish:

- confirmed domain decisions;
- current design choices that may change after use;
- unresolved questions; and
- deliberately deferred ideas.

The requirements are therefore a living record of the prototype's discoveries.
They become tighter through inspection and use rather than being declared
complete before the first useful artifact exists.

The current neutral-factor and pairwise-candidate approach is recorded in
`comparison-framework.md`.
