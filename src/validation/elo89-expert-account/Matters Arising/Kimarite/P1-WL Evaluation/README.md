# Proposal: P1-WL Evaluation

## Status

Implemented and run against the frozen inputs. The adopted run and findings
are recorded below; this document retains the prospective specification so
that the questions and controls can be distinguished from the conclusions.

This is the next stage of the Kimarite matter. The preceding prior-fit
comparison established that P1-WL is well formed, converges, and changes the
975-cell prior map modestly without visibly changing its overall shape. The
present proposal asks whether it retains the demonstrated value of informed
initialisation and what happens when it replaces P1 inside the exact Elo-89
replay.

The source prior evidence is recorded in
[`../P1-WL Prior Comparison - Findings.md`](../P1-WL%20Prior%20Comparison%20-%20Findings.md).

## Questions

The evaluation must answer two related but distinct questions.

### 1. Initialisation value

Does P1-WL retain the retrospective predictive value which justified using P1
rather than equal initialisation, and how does it compare with the older
informed prior?

This is an initialisation comparison. It must not vary the population policy
at the same time.

### 2. Elo-89 consequence

When the exact final Elo-89 model consumes P1-WL instead of P1, what changes in
forecast performance, historical ratings and publication-facing results?

This is the actual repair comparison. It must hold every part of Elo-89 fixed
except the frozen entrant-prior artifact.

The first question says whether the case for informed initialisation survives
the correction. The second says whether adopting the correction has a
material downstream consequence. Neither question is answered merely by the
visual similarity of the two prior curves.

## Frozen inputs

The evaluation should use the same source and interval as the adopted P1-WL
fit unless a discrepancy is found before implementation:

| Input | Proposed value |
|---|---|
| History | `files/output/Historys/1958_01 to 2026_11.zip` |
| History SHA-256 | `afddcc2a77aa237d539073008bf46414989eb766cad8b281cf719963141793ca` |
| Evaluation interval | `1989-01` through `2026-09` |
| K configuration | `files/input/elo_fide.json` |
| K SHA-256 | `cd69609fbb1c40a90e93afbe8055f4305a4cbae3d6dd8209cf9456d60fd24dd7` |
| q | 400 |
| Forecast observations | Canonical represented binary W/L selection |
| Bootstrap unit | Basho |
| Bootstrap resamples | 2,000 |
| Calibration-bin width | 0.05 |
| Minimum supported-bin participants | 100 |

The two new prior inputs are the control and candidate produced in the adopted
same-History run:

- incumbent-semantics control:
  `../output/p1-wl-comparison-2026-10-25-rerun/p1/prior.csv`;
- P1-WL candidate:
  `../output/p1-wl-comparison-2026-10-25-rerun/p1-wl/prior.csv`.

Their exact file and source-manifest hashes must be calculated and written to
the evaluation manifest. Paths alone are not sufficient provenance.

The older informed prior used in the established comparison should remain the
same artifact:
`files/output/Equelo/boundary_reconciliation/2026-08-19_lower_banzuke_merge/paired_literal_chii_merge_candidate.csv`.
If the implementation audit shows that it cannot cover the selected History
domain, stop and document the problem. Replacing it would be a separate change
and must be justified explicitly.

The currently published P1 at
`files/output/analysis/equelo_bkp1/prior.csv` should also be loaded as a
reference. It predates the adopted frozen History and its manifest does not
bind it to an exact History hash. It must therefore not replace the
same-History P1 control in the causal kimarite comparison.

## Common requirements

Every candidate must see the same ordered bout identities and outcomes.
Before scoring, the evaluator must assert exact equality of the forecast
domain across models using at least basho, day and both rikishi identifiers.

It must also assert that:

- both P1 artifacts cover the same paired rank domain after the established
  east/west pairing rule;
- their unranked fallback is derived by the same rule;
- the same K function is used wherever divisional K is selected;
- no candidate silently refits its prior during evaluation;
- the final Elo-89 comparison uses identical active-population membership,
  entry, departure, normalisation and bout-update rules; and
- neither run writes to or promotes the canonical production P1 directory.

Both P1 and P1-WL are future-informed by the history being scored. The
resulting evidence is retrospective model-selection and internal-coherence
evidence, not prospective validation.

## Test A: initialisation comparison

### Purpose

Repeat the established P1 predictive gate with P1-WL added as an explicit
candidate. Use the established sequential forecast model without Elo-89
population adjustment so that the comparison isolates initialisation.

### Candidate matrix

At minimum, run these models:

| Label | K | Initialisation | Purpose |
|---|---|---|---|
| B | Constant | Equal | Historical Basic Elo reference |
| B_k | Divisional | Equal | Direct equal-initialisation comparator |
| old B_kP | Divisional | Older informed prior | Retained informed-prior benchmark |
| published B_kP1 | Divisional | Current production P1 | Publication reference; not causal control |
| B_kP1 | Divisional | Same-History P1 control | Direct incumbent-semantics control |
| B_kP1-WL | Divisional | P1-WL | Corrected candidate |

The constant-K informed-prior cell may be retained if it falls out naturally
from the existing factorial evaluator, but it is not required to answer the
P1-WL question. Population adjustment must not be introduced in Test A.

### Measures

For every model, report:

- mean log loss, the primary predictive measure;
- mean Brier loss;
- expected calibration error;
- bout count; and
- exact differences from the 50% reference where the established report uses
  them.

For P1-WL, calculate paired differences against B, B_k, old B_kP and P1.
Use deterministic basho-block bootstrap intervals for log and Brier
differences. Negative candidate-minus-comparator values favour P1-WL.
The published P1 reference should be reported separately so that any small
source/refit drift is visible rather than attributed to kimarite eligibility.

Report the established maturity populations, including:

- new entrant;
- fewer than 30 prior rated bouts;
- 30–59;
- 60–119;
- 120–239;
- 240–359;
- 360–479; and
- 480 or more.

The new-entrant and under-30 groups are substantively primary for an
initialisation comparison. Later groups show how quickly any difference
dissipates. Division groups and sekitori/sub-sekitori boundary groups should
be retained if the established evaluator already produces them; they are
diagnostics rather than extra selection criteria.

### Interpretation

The test should establish:

1. whether P1-WL remains better than equal initialisation where an entrant
   prior should matter;
2. whether it still passes the existing retrospective non-inferiority gate
   against Basic Elo;
3. how much of the older informed prior's measured benefit it retains; and
4. whether its difference from P1 is practically detectable or merely
   numerically non-zero.

P1-WL is not required to beat the older informed prior. P1 itself did not do
so. The relevant historical claim was that P1 repaired a construction
pathology while preserving most of the value of informed initialisation.

## Test B: exact Elo-89 replacement comparison

### Purpose

Run the accepted Elo-89 model three times on the same History:

- **Elo-89/published P1:** final model with the current production artifact;
- **Elo-89/P1:** final model with the same-History P1 control;
- **Elo-89/P1-WL:** final model with the corrected candidate.

Both runs must use q=400, divisional K, the canonical binary W/L bout domain,
whole-active-population mean preservation at the start and end of each basho,
and the current lifecycle policy. Those policies are controls in this matter,
not endorsements ahead of their own matters-arising investigations.

The primary causal contrast is same-History P1-WL minus same-History P1. The
other two useful contrasts are:

- same-History P1 minus published P1: source/refit drift unrelated to the
  eligibility correction; and
- P1-WL minus published P1: the actual change a future promotion would make
  relative to current publication.

These contrasts must not be collapsed into one number.

### Forecast comparison

On identical bout rows, report:

- mean log loss, Brier loss and ECE for each run;
- paired P1-WL-minus-P1 log and Brier differences with basho-block intervals;
- the maturity groups listed for Test A;
- mean, RMS, percentile and maximum absolute probability difference; and
- the bouts with the largest probability changes, with enough context to
  identify whether they arise at entry or after repeated propagation.

The evaluator should identify the first divergent forecast and verify that
the divergence is caused by different initialisation, not a changed bout
domain or processing order.

### Rating-state comparison

Compare the complete saved state at basho start, day end and basho end over
every common `(date, rikishi)` observation. Report:

- mean signed, mean absolute, RMS and maximum rating difference;
- selected percentiles of absolute difference;
- differences by basho, division and rating maturity;
- the largest individual differences with rikishi, date, chii and prior rated
  bouts;
- the rate at which initialisation differences decay for continuing rikishi;
  and
- the effect on newly initialised or reinitialised rikishi separately from
  established incumbents.

The two priors may imply different initial active means and therefore
different Elo-89 target means. Preserve and report the raw rating differences,
because those are the publication impact of replacement. Also report a
target-mean-aligned comparison which subtracts the difference between the two
run anchors. The aligned view is diagnostic only: it must not silently replace
the raw production result.

### Publication-facing comparison

Without replacing the production artifact, derive and compare at least:

- ratings at the final represented basho;
- historical peak rating per rikishi and its date;
- ordering changes in current and peak tables;
- changes among the largest or otherwise prominently published ratings; and
- any threshold or milestone crossings used by the site.

A complete static-site rebuild is not required for the first evaluation run.
If the underlying publication tables change materially, a later candidate
site build should be made for human inspection before adoption.

## Decision rules

The result should be classified rather than reduced to a single winner.

### Evidence supporting adoption

Adoption is supported if P1-WL:

- preserves the established benefit of informed initialisation over equal
  initialisation;
- passes the same retrospective gate that canonical P1 passed;
- introduces no unexplained domain, coverage or numerical anomaly; and
- has neutral or acceptably small downstream consequences in exact Elo-89.

### Evidence requiring investigation

Stop before adoption if the run shows:

- unequal bout domains or prior coverage;
- a material loss concentrated among new or immature ratings;
- large or persistent rating changes not explained by the approximately
  40-point upper-division prior shift;
- unexpected ordering or publication changes; or
- dependence on an implementation difference other than the selected prior.

No new arbitrary numerical tolerance should be invented after seeing the
result. The existing non-inferiority gate supplies the formal historical
criterion against Basic Elo. P1-WL-versus-P1 differences should be reported
with paired uncertainty and interpreted for practical scale rather than
turned retrospectively into a pass/fail threshold.

Most importantly, P1-WL does not have to achieve a better point score than P1
to justify the semantic correction. If predictive and publication effects are
effectively neutral, the positive binary-W/L rule is preferred because it
uses the evidence Elo-89 claims to rate. A material degradation would require
explanation and possibly further model work; it would not by itself establish
that known W/L bouts cease to be results.

## Required artifacts

One timestamped evaluation directory should contain:

```text
output/<run-id>/
    manifest.json
    initialisation/
        summary.csv
        paired_comparisons.csv
        calibration.csv
        findings.md
    elo89/
        published-p1/
            manifest.json
            ...complete Elo-89 artifacts...
        p1/
            manifest.json
            ...complete Elo-89 artifacts...
        p1-wl/
            manifest.json
            ...complete Elo-89 artifacts...
        forecast_comparison.csv
        probability_difference_summary.csv
        rating_difference_summary.csv
        rating_difference_by_basho.csv
        rating_difference_by_division.csv
        rating_difference_by_maturity.csv
        rating_difference_by_entry_status.csv
        largest_rating_differences.csv
        publication_comparison.csv
        findings.md
```

The root manifest must record:

- source History path and SHA-256;
- selected interval and exact rated-bout count;
- K path and SHA-256;
- every prior path, SHA-256, source-manifest path and source-manifest SHA-256;
- pairing and fallback rules;
- q, bootstrap parameters and random seed;
- exact model labels and controlled differences;
- elapsed run time; and
- the output file inventory.

Outputs in this folder are validation evidence and should be committed with
the implementation and findings. The runner must refuse to overwrite an
existing run directory.

## Proposed implementation boundary

The evaluation should be implemented under `src.validation.kimarite`. A
dedicated subpackage is justified if separate modules are needed for model
runs, paired scoring, rating-state comparison and output writing. Existing
analysis functions may be reused, but their assumptions must be made explicit
and protected by validation-level tests.

The current `predict_candidate` script is useful source material but is not
the complete answer: it was written for the original P1 gate, assumes a
particular candidate-manifest layout, and does not perform a paired exact
Elo-89 P1-versus-P1-WL state comparison. The new validation runner should
orchestrate the two declared tests directly rather than depending on manual
assembly of several legacy outputs.

The planned command shape is:

```powershell
py -m src.validation.kimarite.p1_wl_evaluation `
  --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip" `
  --start 1989-01 `
  --end 2026-09 `
  --p1 ".\src\validation\elo89-expert-account\Matters Arising\Kimarite\output\p1-wl-comparison-2026-10-25-rerun\p1\prior.csv" `
  --p1-wl ".\src\validation\elo89-expert-account\Matters Arising\Kimarite\output\p1-wl-comparison-2026-10-25-rerun\p1-wl\prior.csv" `
  --output ".\src\validation\elo89-expert-account\Matters Arising\Kimarite\P1-WL Evaluation\output\<run-id>"
```

This interface is part of the proposal and may be refined during
implementation, but any change must preserve the declared controls and
artifacts.

## Work sequence

1. Audit and reuse the established P1 scoring and population code.
2. Add loaders which bind each side-specific prior to its producing manifest
   and apply one common pairing/fallback rule.
3. Add exact domain and prior-coverage assertions.
4. Implement Test A and focused synthetic tests.
5. Implement the two exact Elo-89 runs and state comparison for Test B.
6. Smoke-test only on a small synthetic History.
7. Review the generated manifest schema and proposed report tables.
8. Run the complete frozen-history evaluation only after explicit agreement.
9. Record findings and decide whether to promote P1-WL.

No canonical P1 file, Elo-89 production directory or site artifact is changed
by this proposal.
