# Prospects

This package owns the production 1989+ calculation of historical san'yaku
prospects by division, rank number and completed age. January 1989 is boundary
support: rikishi already present there are excluded from the complete-record
population.

The implementation was forked from
`src.analysis.greatness.sanyaku_prospects` after commit `b010770`. The
greatness package is a legacy 1958+ research implementation and is not imported
by this package.

`src.analysis.site89.prospects` validates and packs these outputs for the
website. It does not recalculate probabilities.

The calculation, publication contract, interface and caveats are specified in
[the public artifact proposal](docs/Proposal%20-%20Public%20Sanyaku%20Prospects%20Artifact.md).
