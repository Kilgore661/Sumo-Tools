# Promotion

Exploratory analysis of promotion decisions using the Sumo-Tools History.

The [promotion prospects statistical analysis proposal](docs/Promotion%20Prospects%20Statistical%20Analysis%20Proposal.md)
defines the next phase: descriptive support and uncertainty, score and rank
breakdowns, chronological validation, temporal stability, and the evidence
required before any public promotion annotation or probability is considered.
Its implementation lives in the
[promotion prospects package](prospects/README.md); the Ozeki pipeline is
implemented there and the Yokozuna folder is currently reserved.

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
