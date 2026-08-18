# Fixed Juryo--Makushita Boundary Experiment

This standalone post-1988 experiment tests whether the J13/J14/Ms1 prior
shape is caused by grouping historically variable Juryo banzuke by literal
chii. It does not attempt to merge its priors with the Makuuchi--Juryo model.

The experiment is complete and remains a research artifact rather than a
production model. Start with the
[consolidated M12 record](../../docs/story/08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md)
and use the [experiment catalogue](../../docs/story/09%20M12%20Experiment%20Catalogue.md)
for its matched run and interpretation.

The contextual key is:

```text
Juryo:     negative position from the bottom; bottommost is -1
Makushita: position from the top minus one; Ms1e is 0
Others:    annotation-free literal chii
```

Run with:

```powershell
python -m src.analysis.equelo.fixed_jms_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --epsilon 0.01
```

The producer scopes the history to 1989 onward before every calculation and
builds a like-for-like literal-chii control over the same data.
