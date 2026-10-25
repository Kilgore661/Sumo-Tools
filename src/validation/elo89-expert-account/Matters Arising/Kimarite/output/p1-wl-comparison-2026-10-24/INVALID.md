# Invalid comparison run

This run is retained as diagnostic evidence but must not be interpreted as a
P1 versus P1-WL comparison.

Both fits reached the 200-iteration limit without convergence. The control P1
ended with a maximum prior change of 32.568 rating points and P1-WL with
34.638. The `prior.csv` files therefore contain unfinished iterates, not fitted
priors.

The cause was a validation-runner defect: the selected annotated History was
passed directly to the solver instead of through the canonical P1 producer's
`annotation_only` oracle preprocessing. This created 992 distinct chii cells,
including annotation-specific cells such as `Y1eYO` and `Y1eHD`, rather than
the canonical base-rank domain. The runner was corrected after this run.
