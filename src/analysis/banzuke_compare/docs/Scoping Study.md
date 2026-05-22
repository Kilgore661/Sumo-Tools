# Banzuke News Scoping Study

## Status

Initial discovery note.

This document explores what people may want to know when a new banzuke is
published, and what those questions imply for code. It is intentionally broad:
the goal is to avoid locking the implementation around easy first reports before
we understand the wider shape of the problem.

## 1. Purpose

The `news` package should turn a newly published banzuke into useful statements
about what changed.

The input is conceptually:

```text
previous known banzuke
newly published banzuke
optional previous basho results and career history
```

The output is not merely a raw diff. The user-facing product is banzuke news:
rank changes, promotions, demotions, new entrants, returns, surprises, and other
notable stories.

The first implementation should compute neutral facts before deciding which
facts are newsworthy.

## 2. Stakeholders And Questions

### Casual Fans And Commentators

Likely questions:

- What are the headline changes?
- Who made sanyaku?
- Who entered or left Makuuchi?
- Who entered or left Juryo?
- Who made the biggest move?
- Were there any shocking drops?

Implication:

The code should support filtered headline views over a general banzuke diff.
It should not hard-code one global "biggest movers" report as the central model.

### Followers Of Individual Rikishi

Likely questions:

- What happened to my rikishi?
- Did they move up or down?
- Did they enter a new division?
- Is this a career high?
- Are they back after absence or injury?
- Did they fall off the ranked banzuke?

Implication:

The model needs rikishi-level facts keyed by `RikId`, with names treated as
display data. Shikona can change, so identity must follow rikishi ID rather
than text names.

### Division Watchers

Likely questions:

- Who entered this division?
- Who left this division?
- How much churn was there?
- Which boundary ranks were involved?
- Who replaced whom around the Makuuchi/Juryo or Juryo/Makushita boundary?

Implication:

Division transitions should be first-class facts, not merely side effects of
rank movement. Jonokuchi and Makuuchi have asymmetric boundary semantics:
Jonokuchi has no lower ranked division, and Makuuchi has no higher division.

### Promotion And Banzuke Nerds

Likely questions:

- Was this promotion expected?
- Was this demotion harsh?
- Did a rikishi get held despite a good or bad record?
- Did someone leapfrog another rikishi?
- Is this consistent with recent performance?

Implication:

These questions need previous basho results and possibly local context around
nearby ranks. They should be a later layer over the raw banzuke diff, not part
of the first parser-facing interface.

### Career And History Users

Likely questions:

- Is this a career high?
- Is this a first appearance in the division?
- Is this a return to a previous division?
- Is this a long-awaited promotion or a random walk by a journeyman?
- How fast is the rise compared with career length?

Implication:

Career-history questions need more than two banzuke. They require historical
rank appearances and, for richer stories, bio or career metadata. The first
diff model should leave room for these annotations without requiring them.

### Data And Parser Debug Users

Likely questions:

- Did the parse look plausible?
- Which rikishi appeared, disappeared, or changed shikona?
- Are there duplicate or unexpected ranks?
- Are marginalia/body reconciliation issues visible?

Implication:

The analysis should preserve enough raw identifiers to debug surprising output.
Reports should be explainable from facts such as old rank, new rank, old
division, new division, old shikona, and new shikona.

## 3. Candidate News Facts

The core model should probably start with neutral facts such as:

- `EnteredBanzuke`: present in the new banzuke but absent in the previous one.
- `ExitedBanzuke`: present in the previous banzuke but absent in the new one.
- `RankChanged`: present in both, but old and new `Chii` differ.
- `DivisionChanged`: present in both, but old and new divisions differ.
- `PromotedToDivision`: moved into a higher division.
- `DemotedFromDivision`: moved into a lower division.
- `ShikonaChanged`: same `RikId`, different displayed shikona.

Later facts may include:

- `ReachedCareerHigh`
- `ReachedCareerHighDivision`
- `ReturnedToDivision`
- `FirstSekitoriAppearance`
- `FirstMakuuchiAppearance`
- `NewSanyaku`
- `NewOzeki`
- `NewYokozuna`
- `PerformanceConsistentMove`
- `SurprisingMove`

The distinction matters: core facts should be mechanically derivable and easy
to test. News labels can be opinionated and evolve.

## 4. Movement And Distance

`Chii.ordinal()` is an ordering key, not a numeric distance.

Although ordinals look integer-like, they are tuples such as:

```text
Y1e -> (0, 1, 0, 0)
```

Subtracting one ordinal from another is meaningless. Therefore "up by how much"
requires a domain-specific movement metric.

Possible movement metrics:

- Banzuke slot distance: count positions between old and new rank in a fully
  ordered banzuke list.
- Same-division rank distance: describe moves like `M5e -> M2w` as a movement
  within Maegashira ranks.
- Division transition category: describe `J1e -> M16w` as promoted to
  Makuuchi, rather than as a scalar distance.
- Headline buckets: small rise, big rise, division promotion, sanyaku
  promotion, large demotion, and so on.

The first implementation should avoid pretending that there is one obvious
numeric distance.

## 5. Likely Data Inputs

### Required For First Slice

```text
previous Banzuke
new Banzuke
```

The new banzuke can come from `src.infra.parser.parser2.get_banzuke(date)`.
The previous banzuke can come from the live store:

```text
History(previous_date).banzuke
```

### Required For Performance-Aware News

```text
previous BashoState.summary
previous daily results
previous final record by rikishi
```

These are needed for questions about whether the banzuke movement is consistent
with the previous basho.

### Required For Career-Aware News

```text
full History
possibly bios.json
possibly shikona-change tables from banzuke pages
```

These are needed for career highs, first appearances, returns, and journeyman
versus prospect framing.

## 6. Suggested Code Shape

Avoid making the first report the central abstraction.

Suggested package shape:

```text
src/analysis/news/
  __main__.py
  banzuke_diff.py
  facts.py
  classify.py
  reports.py
```

Responsibilities:

```text
banzuke_diff.py
    Compare two Banzuke objects and produce neutral facts.

facts.py
    Dataclasses for raw facts such as RankChanged and DivisionChanged.

classify.py
    Turn facts plus optional history/results context into news categories.

reports.py
    Render facts/news to console, CSV, HTML, or later richer formats.

__main__.py
    CLI orchestration and smoke-test entry points.
```

The first stable domain boundary could be:

```python
compare_banzuke(previous: Banzuke, current: Banzuke) -> BanzukeDiff
```

Where `BanzukeDiff` contains neutral, reusable facts.

## 7. First Executable Slice

The first useful slice should stay narrow but not distort the design:

```text
Given previous banzuke and new banzuke:
  list entrants
  list exits
  list division promotions
  list division demotions
  list rank changes without scalar distance
```

For movement size, the first report can use cautious language:

```text
old rank -> new rank
direction: up/down
movement kind: same division / division promotion / division demotion
```

It should postpone "up by N" until a movement metric is designed.

## 8. Open Questions

- What should count as "up" across different divisions and rank classes?
- Do we need a banzuke-slot ordering independent of `Chii.ordinal()`?
- How should absences, banzuke-gai, Mae-zumo, and Shinjo be represented?
- Should shikona changes be parsed into news, or treated as display metadata?
- What is the minimum history context needed to say "career high" reliably?
- How should reports distinguish raw facts from editorial headlines?
- Should Makuuchi/Juryo boundary changes be treated as special cases by
  default?
- What output form is most useful first: console text, CSV, or HTML?

## 9. Working Principles

- Parse once, compare later.
- Treat `RikId` as identity and shikona as display/history data.
- Compute neutral facts before news labels.
- Do not use `Chii.ordinal()` as a distance metric.
- Keep performance-aware and career-aware analysis as optional layers.
- Let early reports prove the domain model before refactoring parser internals.
