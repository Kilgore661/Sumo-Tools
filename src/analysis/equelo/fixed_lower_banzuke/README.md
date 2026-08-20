# Continuous Lower-Banzuke Equelo Experiment

## Status

Experimental producer. It does not replace `fixed_supported`, and its outputs
are not consumed by the public Equelo API or the site.

## Question

Can the successful 1989-onward Juryo--Makushita boundary representation be
continued down the banzuke far enough to provide a broadly coherent curve
through upper Jonidan?

## Prior coordinate

The complete Oracle banzuke is indexed before support filtering:

```text
Juryo: negative position from its bottom; bottommost is -1
Ms1e:  0
Below: one uninterrupted position sequence through Ms, Sd, Jd and Jk
Makuuchi: existing annotation-free literal-chii key
```

The index does not reset at divisional boundaries. Consequently, the index of
a literal rank such as Jd100e can vary with the structure of its contemporary
banzuke. Output charts resolve the contextual estimates back onto actual chii
by averaging over their appearances.

## Run

From the repository root:

```powershell
python -m src.analysis.equelo.fixed_lower_banzuke `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --start-year 1989 `
  --epsilon 0.01
```

Timestamped outputs are written beneath:

```text
files/output/Equelo/fixed_lower_banzuke/
```

The producer fits the complete represented lower coordinate, including Jk,
so that the experiment can reveal where the result ceases to be credible. A
later smoothing policy may choose a higher evidence cutoff such as Jd100 and
extrapolate below it; this experimental producer does not impose that cutoff.
