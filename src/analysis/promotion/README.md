# Promotion

Exploratory analysis of promotion decisions using the Sumo-Tools History.

The [promotion prospects statistical analysis proposal](docs/Promotion%20Prospects%20Statistical%20Analysis%20Proposal.md)
defines the next phase: descriptive support and uncertainty, score and rank
breakdowns, chronological validation, temporal stability, and the evidence
required before any public promotion annotation or probability is considered.
Its implementation lives in the
[promotion prospects package](prospects/README.md); the Ozeki pipeline and the
selected Yokozuna publication account are recorded there.

- [Ozeki](ozeki/README.md): promotion audits and retrospective evaluation of
  rule-based binary classifiers.
- [Yokozuna](yokozuna/README.md): consecutive-yusho benchmarks, exhaustive
  `{Y,D,J,N}` pair partitions and exact triple-partition optimization.

Start with the [ozeki classification experiment](ozeki/docs/Experiment%20-%20Binary%20Classification%20of%20Ozeki%20Promotion.md).
It defines the Xn classifier families, observation boundaries and exclusions,
compares seven candidates using precision, recall and F1, and discusses what
can and cannot be concluded. Its purpose is to develop a feeling for the data,
not to discover a hidden rule or judge whether JSA decisions were correct.

The highest F1 among those seven is A32 at 77.86%, compared with 71.79% for
A33, a difference of 6.07 percentage points on the documented historical sample.
The ozeki README gives commands for individual JSON evaluations and the
orchestrated comparison report.

The [yokozuna classification experiment](yokozuna/docs/Experiment%20-%20Classification%20of%20Yokozuna%20Promotion.md)
starts from two consecutive yusho at ozeki and progressively broadens the
championship-result representation. The maximum pair F1 is 66.67% on 31
promotions. Adding a third-basho context raises the maximum in-sample F1 from
65.62% to 77.42% on the common 30-promotion sample, with substantial sparsity
and overfitting caveats.

The public-facing [YokYDJ account](prospects/yokozuna/docs/YokYDJ.md) narrows
the product question to current-banzuke prospects. For promotion decisions
from May 2014 through September 2026, `YY, YD, YJ, DY, JY` gives 5 true
positives, 2 false positives and no false negatives, for an F1 score of 83.33%.
The short period and small number of decisions are explicit limitations.

The resulting product contract is recorded in
`src/products/make_site89/docs/Promotion Annotations - Final Proposal.md`.
Its `Here Be Dragons` companion preserves why the site does not publish
per-rikishi probabilities or attempt to decide whether a YokYDJ result remains
possible before the complete torikumi and final results are known.
