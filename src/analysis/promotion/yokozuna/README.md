# Yokozuna promotion analysis

Read the
[classification experiment](docs/Experiment%20-%20Classification%20of%20Yokozuna%20Promotion.md)
for the observation contract, boundary evidence, methods, results, case
interpretation and limitations. The experiment begins with consecutive yusho,
expands to all ordered `Y/D/J/N` pairs, and then adds a third-basho context.

The current experiment classifies every two-basho ozeki window by its ordered
pair of Makuuchi championship markers. `Y` is yusho, `D` is doten-yusho, `J`
is jun-yusho and `N` means none of those markers.

To evaluate all 65,536 subsets of the 16 ordered pairs and retain every tied
maximum-F1 partition:

```powershell
python -m src.analysis.promotion.yokozuna.score_partitions
```

The command writes a timestamped JSON file beneath
`files/output/analysis/promotion/yokozuna/` and prints a human-readable summary.
The output location is fixed and cannot be changed through the CLI. The
artifact contains the 4-by-4 cell counts, all maximizing partitions, resolved
and unresolved opportunities, and provenance.

To test the 64 ordered triples, treating the first basho as Makuuchi context
and requiring the final two basho to be at Ozeki:

```powershell
python -m src.analysis.promotion.yokozuna.score_triples
```

The triple command prints numbered progress stages and a human-readable final
summary. It finds the exact maximum by testing the finite set of cell-promotion
rate thresholds rather than attempting to enumerate `2^64` subsets. Its fixed
timestamped JSON artifact also contains a pair optimization restricted to the
same three-basho-eligible observations, allowing a like-for-like comparison.

The search is descriptive and in-sample. Its maximum F1 is not held-out
predictive performance and need not identify a coherent historical policy.
Wakanohana's November 1957 Ozeki 12-3 jun-yusho is retained as explicitly
user-supplied boundary evidence; it does not modify History.

## Recorded results

On the full 31-promotion pair sample, two partitions tie at F1 66.67%:
`YY, YD, DD, JY`, with `DY` optional. On the 30-promotion sample with complete
three-basho context, the best pair F1 is 65.62% and the best triple F1 is
77.42%. These are maximum retrospective fits on the data used to select them,
not estimates of future performance.

## Verification

```powershell
python -m pytest -s tests/test_yokozuna_promotion.py `
  tests/test_yokozuna_partitions.py `
  tests/test_yokozuna_triples.py
```
