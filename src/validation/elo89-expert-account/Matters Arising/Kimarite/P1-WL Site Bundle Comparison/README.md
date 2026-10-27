# P1-WL site-bundle comparison

## Status

Controlled comparison completed. The adopted full run found no invariant
violations and supports proceeding to a complete, non-deployed web-site build
using P1-WL. Results, interpretation, limitations and the decision are in
[`Findings.md`](Findings.md).

The earlier work accepted P1-WL as a sufficiently close replacement for P1
and retained epsilon 10. This tranche no longer investigates how the prior was
derived or whether it is predictively preferable. P1-WL is treated as one
fixed input to the publication process.

The question here is narrower:

> If the fixed production prior is changed from published P1 to accepted
> P1-WL, does the complete site-data build change exactly the outputs which
> depend on Elo-89 ratings, while leaving all other outputs unchanged?

The work built comparable P1 and P1-WL site-data bundles from identical
inputs and classified and compared every artifact. Inspection of an assembled
candidate site is the next tranche. This work does not promote P1-WL,
overwrite the canonical prior, deploy a site, or decide the separate
disappearance/reappearance and off-banzuke matters.

The detailed experiment specification is in
[`docs/Proposal.md`](docs/Proposal.md).

## Fixed candidate

Unless superseded by an explicitly recorded correction, the candidate input
is:

```text
src/validation/elo89-expert-account/Matters Arising/Kimarite/
  output/p1-wl-comparison-2026-10-25-rerun/p1-wl/prior.csv
```

Its SHA-256 recorded by the adopted evaluation is
`6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486`.
The baseline is the currently published canonical P1 at
`files/output/analysis/equelo_bkp1/prior.csv`, recorded with SHA-256
`bd2ed9868c883fda5a52615ed96b4430f4d6c2c06db53474bd0e84757497f003`.

These identities make the comparison reproducible. They do not make prior
provenance part of the site-build question.

## Implementation

The comparison runner is `src.validation.p1_wl_site_bundle`. It:

1. refuses to overwrite an existing experiment directory;
2. records the History, prior and ancillary-input identities;
3. builds isolated baseline and candidate bundles through the normal
   `produce_site89_bundle` path;
4. validates both bundles with the normal `make_site89` bundle validator;
5. compares every declared site-data file and the underlying Elo-89 run;
6. reports schemas, record counts, identity keys, ordering, changed fields and
   numerical differences;
7. separately reports post-bout rating differences for Makuuchi, Juryo and all
   sekitori, including distribution summaries and inspectable observations; and
8. treats any semantic change to a model-independent artifact as an invariant
   violation.

The required production seam is deliberately small:
`produce_site89_bundle` now accepts an explicit `prior_path` and passes it to
`produce_elo89`. Its default remains the canonical production prior. The
Elo-89 manifest also records the selected prior's SHA-256.

## Full run

From the repository root:

```powershell
py -m src.validation.p1_wl_site_bundle `
  --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip" `
  --start 1989-01 `
  --end 2026-09 `
  --baseline-prior ".\files\output\analysis\equelo_bkp1\prior.csv" `
  --candidate-prior ".\src\validation\elo89-expert-account\Matters Arising\Kimarite\output\p1-wl-comparison-2026-10-25-rerun\p1-wl\prior.csv" `
  --banzuke-source-root ".\files\output\bcr" `
  --future ".\files\output\torikumi\future.json" `
  --output ".\src\validation\elo89-expert-account\Matters Arising\Kimarite\P1-WL Site Bundle Comparison\output\site-bundle-comparison-2026-10-27-run3"
```

The program returns zero when both bundles validate and no comparison
invariant is violated. It returns two after writing the reports when the
comparison completes but finds violations. An execution failure is also
recorded in the root manifest before the exception is re-raised.

The retained reports are:

- `comparison/files.csv`;
- `comparison/numeric_differences.csv`;
- `comparison/largest_numeric_differences.csv`;
- `comparison/sekitori_rating_summary.csv`;
- `comparison/sekitori_rating_differences.csv`;
- `comparison/violations.csv`;
- `comparison/summary.json`; and
- `comparison/findings.md`.

Both complete generated bundles remain under the experiment output as
`baseline/` and `candidate/`.

The adopted run completed in 200.101 seconds, compared 305 files and reported
261 expected semantic changes, zero changes among 40 model-independent files,
and zero invariant violations.

## Smoke test

The focused smoke suite covers the production seam, prior provenance,
synthetic bundle comparison and the existing bundle/build contracts:

```powershell
python -m pytest `
  tests/test_validation_p1_wl_site_bundle.py `
  tests/test_elo89_production.py `
  tests/test_make_site89_bundle.py `
  tests/test_build_site89.py -q
```

The focused comparison suite was rerun after the final identity and sekitori
reporting changes and completed with `4 passed`. No historical bundle is
generated by that focused smoke test.

## Outcome

The controlled site-data comparison produced:

1. two provenance-bound site-data bundles differing only in their prior;
2. a complete artifact-level comparison;
3. explanations for every changed and unchanged file;
4. focused automated checks for the publication boundary; and
5. a decision that P1-WL is ready for a non-deployed site-generation and
   inspection step.

Visual inspection of the assembled pages, and any subsequent canonical
promotion, remain explicit later steps.
