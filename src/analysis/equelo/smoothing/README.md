# Equelo Initial-Rating Smoothing

## Status

This package contains the retained post-1988 entrant-initial-rating
construction described in
[`Initial Rating Policy`](../../docs/story/10%20Initial%20Rating%20Policy.md).

The first implemented module is the input chart producer:

```powershell
python -m src.analysis.equelo.smoothing.chart `
  path/to/combined_final_with_stats.csv `
  --support-csv path/to/all_chii_support.csv
```

It writes `supported_fixed_point_estimates.html` beside the ratings CSV unless
`--output` is supplied. The chart contains only direct supported fixed-point
estimates, while its x-axis retains every chii in the pre-filter collapsed
support domain. Unsupported chii therefore appear as empty positions rather
than invented rating points. No nearest-supported completion or smoothing is
applied.

The earlier plan was to apply monotone smoothing and full-domain completion.
Smoothing remains a reasonable alternative, but the project chose to retain
the unsmoothed paired post-1988 result because it is already adequate for
shortening the initialisation gap. Pre-1989 completion is outside this
package's current policy.

The exploratory boundary-merge chart projects the independently fitted M/J
and continuous lower-banzuke results onto literal chii. It calculates one
appearance-weighted additive alignment shift over Juryo, blends the estimates
linearly from J1e to J14w, uses the lower estimate through Jd100e, and holds
the retained merge candidate flat below that cutoff:

```powershell
python -m src.analysis.equelo.smoothing.boundary_merge `
  --mj-csv path/to/all_chii_prior_comparison.csv `
  --lower-csv path/to/lower_banzuke_chii_comparison.csv `
  --cutoff-chii Jd100e `
  --output-csv path/to/literal_chii_merge_candidate.csv
```

The producer writes the analytical values to CSV first. The chart module reads
that persisted CSV without calculating ratings and writes a same-named HTML
file. A `.metadata.json` provenance record contains the input paths and
SHA-256 hashes, calculated alignment shift, cutoff, flat-tail rule, output
hashes and row count. This is a candidate construction for inspection, not an
accepted smoothing or production policy.

To inspect the same persisted construction with east and west combined:

```powershell
python -m src.analysis.equelo.smoothing.paired_merge `
  path/to/literal_chii_merge_candidate.csv `
  --output-csv path/to/paired_literal_chii_merge_candidate.csv
```

This second producer takes the unweighted mean of the available east and west
values for each rank number. A singleton retains its value; a pair with no
contextual input remains blank. It writes paired CSV and metadata before its
chart renderer consumes the paired CSV. It does not recenter the resulting
values. The retained paired artifact has an unweighted mean of approximately
1411.087 rather than 1517; this is intentional because expt2's normalisation
domain no longer exists after contextual resolution, merging and pairing.
