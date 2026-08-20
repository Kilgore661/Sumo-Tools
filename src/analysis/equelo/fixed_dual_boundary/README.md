# Joint Dual-Boundary Equelo Experiment

This 1989-onward experiment combines the independently successful Makuuchi--
Juryo and Juryo--Makushita representations without fitting a merge to the
desired curve.

The investigation is complete. The 1989-onward result was encouraging, but the
1958--2026 modern-then-combined run retained a material Juryo--Makushita
reversal. This producer is therefore a preserved research artifact, not the
production entrant-prior model. See the
[consolidated M12 record](../../docs/story/08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md)
and [experiment catalogue](../../docs/story/09%20M12%20Experiment%20Catalogue.md).

Makuuchi uses distance from the M/J boundary and Makushita uses distance from
the J/Ms boundary. A Juryo observation uses whichever boundary is geometrically
nearer in the contemporaneous banzuke. An exactly central observation receives
equal weight in both maps, both when initialised and when contributing back to
the fixed point.

The alternative `linear` rule lets every interior Juryo observation contribute
to both maps. M/J weight falls linearly from 1 at the top of Juryo to 0 at the
bottom; J/Ms weight rises from 0 to 1. These weights depend only on the
contemporaneous banzuke geometry.

The support threshold is applied to weighted key appearances. During the
supported solve, an unsupported fractional component is omitted and the
remaining supported weights are renormalised to one. The completed process map
then supplies unsupported keys from the nearest supported key of the same
boundary family, consistently with the other fixed-supported experiments.

Run with:

```powershell
python -m src.analysis.equelo.fixed_dual_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --juryo-weighting linear `
  --epsilon 0.01
```

To reproduce the Expt2 modern-then-combined process, retain all history from
1958 but solve 1989 onward first:

```powershell
python -m src.analysis.equelo.fixed_dual_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --start-year 1958 `
  --modern-start-year 1989 `
  --juryo-weighting linear `
  --epsilon 0.01
```
