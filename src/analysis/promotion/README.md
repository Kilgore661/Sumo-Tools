# Promotion

Exploratory analysis of promotion decisions using the Sumo-Tools History.

- [Ozeki](ozeki/README.md): promotion audits and retrospective evaluation of
  rule-based binary classifiers.
- `yokozuna`: reserved for a separate investigation; not yet implemented.

Start with the [ozeki classification experiment](ozeki/docs/Experiment%20-%20Binary%20Classification%20of%20Ozeki%20Promotion.md).
It defines the Xn classifier families, observation boundaries and exclusions,
compares seven candidates using precision, recall and F1, and discusses what
can and cannot be concluded. Its purpose is to develop a feeling for the data,
not to discover a hidden rule or judge whether JSA decisions were correct.

The highest F1 among those seven is A32 at 77.86%, compared with 71.79% for
A33, a difference of 6.07 percentage points on the documented historical sample.
The ozeki README gives commands for individual JSON evaluations and the
orchestrated comparison report.
