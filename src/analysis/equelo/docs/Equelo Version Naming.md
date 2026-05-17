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
| `Mark 3.2(b)`   | Alpha-scaled fixed-point Equelo built from `Mark 3.1(b)`; now historical. |
| `Mark 3.2.1(b)` | Public monotone Equelo rating-landmark curve derived from `Mark 3.2(b)`; now historical. |
| `fixed_v2`      | Current Brierless Equelo artefact package using raw fixed-point entrant ratings. |

The current public rating-landmark curve is:

```text
fixed_v2 public landmarks
```

This is the curve used by the `Typical Equelo Ratings` page.

In ordinary public wording, this may later become simply "the Equelo ratings" or
"the standard Equelo ratings", once the surrounding explanation is stable.  The
canonical technical name remains useful for provenance and future revisions.

## Rating Series vs Rating Landmarks

The public landmark curve is a rating-landmark curve, not the canonical source for
individual rikishi ratings.

The distinction is:

* fixed_v2 process ratings are individual, bout-derived ratings at represented
  points in the basho timeline;
* `Typical Equelo Ratings` values are illustrative landmarks
  associated with chii-like labels.

The landmark curve was made monotone so that the public scale is easier to
read.  That does not mean individual process ratings must be monotone with
banzuke order.  A lower-banzuke rikishi may have a higher actual process rating
than a higher-banzuke rikishi.

Public features that need an individual rikishi's rating after a basho should
use the fixed_v2 process rating artefacts or a documented successor.  They
should not derive the rating from the rikishi's current or next chii by looking
up `Typical Equelo Ratings`.

## Additive Base

The `(b)` parameter is the additive base convention used by the Equelo run.

The project currently uses an additive base convention chosen so that current
process ratings and public landmarks live on a readable common scale.  The
exact public convention may still move, for example between a yokozuna landmark
near 2200 and one near 2500, but this should be an additive presentation choice
rather than a rescaling of rating differences.

```text
fixed_v2 base convention
```

Earlier base-shift experiments showed that adding a constant to all initial
ratings shifts absolute values while preserving rating differences and
win-probability behaviour.  Multiplicative scaling does not have that property.
This distinction is why fixed_v2 removes Brier compression from the current
rating scale.

## Diagnostic `v<n>` Names

Names such as `v0`, `v1`, ..., `v5` are not rating-system names.

They are local diagnostic chart stages used by the landmark writer to show how
the public monotone rating-landmark curve was constructed from entrant initial
ratings.

Use them only when referring to those charts or to the audit trail behind the
current curve.

Current chart-stage meanings:

| Local chart name | Meaning                                                                             |
| ---------------- | ----------------------------------------------------------------------------------- |
| `v0`             | Raw entrant initial ratings used as support data.                                  |
| `v1`             | `v0` cut to the public lower-bound area.                                            |
| `v2`             | `v1` with weak Juryo tail support deleted.                                          |
| `v3`             | `v2` with selected rare chii masked.                                                |
| `v4`             | `v3` with rare Maegashira tail support deleted.                                     |
| `v5`             | Monotone diagnostic fit used to construct public landmark support.                  |

There is no public or canonical `v6` chart stage.

## Mapping Table

| Old or local name                                                      | Canonical interpretation                                                |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `fixed_v1`                                                             | Superseded artefact package using Brier-compressed entrant ratings.      |
| `fixed_v2`                                                             | Current artefact package for public/process Equelo ratings.              |
| `entrant_initial_ratings_v0.html`                                      | Diagnostic chart for raw entrant support.                               |
| `entrant_initial_ratings_v1.html` to `entrant_initial_ratings_v4.html` | Diagnostic cleanup stages.                                              |
| `entrant_initial_ratings_v5.html`                                      | Diagnostic chart for the current monotone public landmark construction. |
| `InitialRatingCurve.v5()`                                              | Historical implementation name for the public landmark curve.            |
| `Typical Equelo Ratings`                                               | Public table of fixed_v2 Equelo rating landmarks.                        |
| `V5 Landmark Policy`                                                   | Old placeholder wording; prefer `Equelo Rating Landmark Policy`.        |

## Brier Addendum

`fixed_v1` used a Brier-optimised alpha compression of fixed-point entrant
ratings.  That was useful diagnostically because it asked about predictive
calibration, but it also changed rating differences.  In Elo-style systems,
rating differences are the operative quantities, so this compression was not
just a cosmetic change of units.

The practical problem was that public landmarks and process ratings could end
up on visibly different scales.  For example, a `Typical Equelo Ratings`
yokozuna landmark might sit near 2500 while operational table ratings for a
yokozuna could sit much higher.  The fixed_v2 pivot removes that compression
and treats Brier as a historical comparison layer rather than the current
rating source.

The longer investigation lives in
`src/analysis/equelo/docs/Brierless Pivot.md`.

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

Technical names such as `fixed_v2` should appear where provenance,
methodology, or caveats are needed.  Historical names such as
`Mark 3.2.1(2000)` and local names such as `v5` should not appear in ordinary
public navigation or page titles.
