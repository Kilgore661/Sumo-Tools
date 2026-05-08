# Equelo Version Naming

## Status

Current make_site-level policy note.

This note records the naming scheme to use when public-site documentation,
navigation, notes, metadata, and producer contracts refer to Equelo ratings and
rating landmarks.

The goal is to avoid confusing model names with local diagnostic chart stages.

## Canonical Model Names

Use `Mark` names for rating systems, rating series, and rating-landmark curves
with semantic force.

The current working scheme is:

| Name            | Meaning                                                                  |
| --------------- | ------------------------------------------------------------------------ |
| `Mark 1`        | Basic Elo-style ratings.                                                 |
| `Mark 2`        | Mean-preserving Elo-style ratings.                                       |
| `Mark 3`        | Equelo: mean-preserving ratings with fixed-point chii-based entry.       |
| `Mark 3.1(b)`   | Raw fixed-point Equelo built with additive base `b`.                     |
| `Mark 3.2(b)`   | Alpha-scaled fixed-point Equelo built from `Mark 3.1(b)`.                |
| `Mark 3.2.1(b)` | Public monotone Equelo rating-landmark curve derived from `Mark 3.2(b)`. |

The current public rating-landmark curve is:

```text
Mark 3.2.1(2000)
```

This is the curve used by the `Typical Equelo Ratings` page.

In ordinary public wording, this may later become simply "the Equelo ratings" or
"the standard Equelo ratings", once the surrounding explanation is stable.  The
canonical technical name remains useful for provenance and future revisions.

## Additive Base

The `(b)` parameter is the additive base convention used by the Equelo run.

The project currently uses:

```text
b = 2000
```

The base-shift experiment showed that rerunning the fixed-point and scaled
pipeline with `b = 2000` shifted the old `b = 1500` values upward by 500 within
floating-point noise.  Rating differences were unchanged.

The public reason for `b = 2000` is presentational: after alpha scaling and
monotone landmark smoothing, the yokozuna landmark sits near 2500.  This does
not give 2500 independent sumo meaning.

## Diagnostic `v<n>` Names

Names such as `v0`, `v1`, ..., `v5` are not rating-system names.

They are local diagnostic chart stages used by the fixed-v1 chart writer to show
how the public monotone rating-landmark curve was constructed from the scaled
entrant initial ratings.

Use them only when referring to those charts or to the audit trail behind the
current curve.

Current chart-stage meanings:

| Local chart name | Meaning                                                                             |
| ---------------- | ----------------------------------------------------------------------------------- |
| `v0`             | Raw scaled fixed-point entrant initial ratings, i.e. `Mark 3.2(2000)` support data. |
| `v1`             | `v0` cut to the public lower-bound area.                                            |
| `v2`             | `v1` with weak Juryo tail support deleted.                                          |
| `v3`             | `v2` with selected rare chii masked.                                                |
| `v4`             | `v3` with rare Maegashira tail support deleted.                                     |
| `v5`             | Current monotone diagnostic fit used to construct `Mark 3.2.1(2000)`.               |

There is no public or canonical `v6` chart stage.

## Mapping Table

| Old or local name                                                      | Canonical interpretation                                                |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `fixed_v1`                                                             | Artefact package for the current fixed Equelo implementation.           |
| `entrant_initial_ratings_v0.html`                                      | Diagnostic chart for raw `Mark 3.2(2000)` entrant support.              |
| `entrant_initial_ratings_v1.html` to `entrant_initial_ratings_v4.html` | Diagnostic cleanup stages.                                              |
| `entrant_initial_ratings_v5.html`                                      | Diagnostic chart for the current monotone public landmark construction. |
| `InitialRatingCurve.v5()`                                              | Historical implementation name for the current public curve.            |
| `Typical Equelo Ratings`                                               | Public table using `Mark 3.2.1(2000)`.                                  |
| `V5 Landmark Policy`                                                   | Old placeholder wording; prefer `Equelo Rating Landmark Policy`.        |

## Chii Wording

Do not use "rank" as a substitute for `Chii`, chii, or `ChiiLabel` in technical
documentation or site contracts.

Use:

* `Chii` for the class/object;
* `chii` for full human-facing chii values such as `M3eHD`;
* `ChiiLabel` for project-defined chii-like labels such as `M3`, `O`, or
  `Jd100`.

This matters especially in rating-landmark contexts, where a `ChiiLabel` is
mapped to an Equelo rating landmark but is not itself a rating.

## Public-Site Rule

Public pages should prefer the stable public terms:

```text
Equelo
Equelo rating
Equelo rating landmark
Typical Equelo Ratings
Equelo Rating Landmark Policy
```

Technical names such as `Mark 3.2.1(2000)` should appear where provenance,
methodology, or caveats are needed.  Local names such as `v5` should not appear
in ordinary public navigation or page titles.
