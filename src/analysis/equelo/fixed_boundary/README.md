# Fixed-Boundary Equelo Experiment

## Status

Experimental producer. It does not replace `fixed_supported` and its artifacts
are not consumed by the public Equelo API or `make_site2`.

The experiment is complete. Its result and limits are consolidated in the
[M12 research record](../../docs/story/08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md),
with the matched run recorded in the
[experiment catalogue](../../docs/story/09%20M12%20Experiment%20Catalogue.md).

## Question

The experiment asks whether the 1989-onward M12 initial-rating problem is
substantially a consequence of grouping ratings by timeless literal
maegashira chii rather than by position relative to the contemporaneous
Makuuchi--Juryo boundary.

The default history scope is 1989 onward. The producer applies that scope
before Oracle cleaning, prior-key assignment, support measurement, fixed-point
solving, process-rating generation and chart aggregation. Pre-1989 banzuke
therefore cannot affect either the estimated priors or the ranks shown in the
charts.

The entrant-prior key is:

```text
Makuuchi: negative position from the bottom; bottommost is -1
Juryo:    position from the top minus one; J1e is 0
Others:   the existing annotation-free literal-chii key
```

Keys are assigned from the complete Oracle banzuke before supported-domain
filtering. Exact positions are used by the prior. Pairing adjacent positions is
reserved for analysis.

## Run

From the repository root with the live History available:

```powershell
python -m src.analysis.equelo.fixed_boundary
```

The scope can be changed explicitly:

```powershell
python -m src.analysis.equelo.fixed_boundary --start-year 1989 --end-year 2026
```

An explicit annotated History zip may be supplied instead of the live store:

```powershell
python -m src.analysis.equelo.fixed_boundary `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip"
```

Each run writes a timestamped directory beneath:

```text
files/output/Equelo/fixed_boundary
```

The output includes:

- the complete contextual entrant-prior map;
- a literal-chii control map estimated from exactly the same scoped history;
- primary and same-scope refinement diagnostics;
- experimental day-end ratings;
- CSV comparisons against the like-for-like literal-chii control;
- responsive CDN Plotly charts for the boundary-index curve, the same result
  viewed by literal maegashira chii, the complete 1989-onward chii sequence, and
  convergence for both models. The all-chii chart retains every east/west chii
  as an ordered categorical point; it is not binned or downsampled.

The literal-chii line is not loaded from the full-history production map. It
is solved afresh with the same period, parameters, tolerance and support rule,
so the chart is a like-for-like comparison of prior representations.

## Interpretation

The comparison must not be judged only by whether the experimental curve is
more monotone. The experiment also records support, convergence, resolved
entrant priors and the resulting process ratings. Production policies for
`q`, divisional `k`, population normalisation, map centring, support threshold,
and result eligibility remain unchanged as far as the changed prior-key domain
permits. Full-history refinement is intentionally not retained: both models
are fitted and run only over the explicitly declared history scope.
