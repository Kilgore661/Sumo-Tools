# Elo-89 P1 Missing-Kimarite Repair

## Status

Deferred corrective work for the current Elo-89 standard.

This document records the defect, its effect on the canonical `P1` entrant
prior, and the bounded route for correcting, evaluating and adopting a new
prior. It is not authority to change the model automatically during an ordinary
website build.

## Scope and terminology

Elo-89 is the project's current operational rating standard. The 1958-onward
Equelo work is legacy research. A future full-history successor may still use
the additional pre-1989 sekitori evidence, but that question is separate from
this repair.

The defect discussed here does not affect Elo-89's production bout replay
directly. That replay already selects represented binary `W/L` outcomes without
requiring a kimarite. It affects the fixed-point calculation that produced
Elo-89's canonical `P1` mapping from entrant chii to initial rating.

## The defect

`src.analysis.equelo_bkp1.simulate` currently ignores a result when
`bout.decision` is either `"fusen"` or `"blank"`.

For parsed History, `decision="blank"` commonly means that the source did not
provide a kimarite. It does not mean that the result is unknown. When the paired
outcomes are `W/L`, the winner and loser are known and the bout is valid rating
evidence.

Consequently:

- the Elo-89 production replay rates these bouts;
- the solver that produced `P1` does not;
- Elo-89 therefore uses the right bout domain after initialization but an
  entrant prior estimated on an unnecessarily reduced bout domain.

The older warning that about 5.6% of post-1988 bouts were lost through missing
kimarite applies to the legacy decision-based selection. The exact count for a
new `P1` run must be recorded from the selected History rather than copied from
that historical estimate.

## Required semantic correction

The `P1` replay must define rating eligibility by paired outcomes, not by the
kimarite field:

- rate a represented `{W, L}` result regardless of whether `decision` contains
  a named kimarite or `"blank"`;
- exclude `{FS, FP}`;
- exclude draws and other non-binary outcomes; and
- do not infer an unrepresented bout.

Merely changing the existing condition to skip only `"fusen"` is insufficient.
The current update code otherwise treats any result not won by its first
participant as a loss, so eligibility must positively require the binary `W/L`
domain.

The canonical meaning should be shared with, or exactly match,
`src.analysis.prediction.bouts.select_rated_bouts`. The parallel experimental
replay in `src.analysis.equelo_population_policy.simulate` should be aligned so
that later controls do not silently use a different bout population. Legacy
Equelo, probability and other affected packages belong to the wider repository
audit and need not be changed merely to adopt a corrected Elo-89 `P1`.

## Why `P1` must be regenerated

`P1` is the output of an iterative fixed-point calculation. Each iteration
replays the history, aggregates basho-start process ratings by literal chii,
recenters the resulting map, and uses that map in the next iteration. Adding
previously omitted bouts can therefore affect later process ratings and the
whole solved map; patching individual rows in the existing CSV would have no
valid interpretation.

The correction must produce a new complete `prior.csv`, `iterations.csv` and
`manifest.json` from one declared History snapshot.

## Controlled generation

The current canonical artifact predates the latest History archive, and its
manifest does not identify the exact History hash. Direct comparison with that
artifact would therefore confound the eligibility repair with later source-data
changes.

For a controlled comparison, use the same current History snapshot twice:

1. Before changing eligibility, generate an old-semantics baseline into a
   separate output directory.
2. After the correction, generate the candidate into another directory.
3. Do not overwrite the canonical `files/output/analysis/equelo_bkp1` directory
   until the candidate has been evaluated and accepted.

The existing local archive can be used without downloading:

```powershell
python -m src.analysis.equelo_bkp1 `
  --start 1989 `
  --end 2026 `
  --zip `
  --output files/output/analysis/equelo_bkp1_blank_baseline

python -m src.analysis.equelo_bkp1 `
  --start 1989 `
  --end 2026 `
  --zip `
  --output files/output/analysis/equelo_bkp1_wl_candidate
```

The producer manifest should first be extended to record the History source and
hash together with counts for raw results, rated `W/L` bouts, excluded fusen,
excluded draws or other outcomes, and rated bouts whose kimarite is blank. This
is required provenance for the model input, not optional diagnostic detail.

## Tests

The `P1` replay needs focused contract tests proving that:

- a blank-kimarite `W/L` result updates both ratings;
- the same `W/L` result with a named kimarite has identical rating semantics;
- a fusen pair is excluded;
- a draw or other non-binary result is excluded; and
- divisional `k` remains applied to each participant.

The focused regression suite should include at least:

```powershell
python -m pytest -s `
  tests/test_equelo_bkp1.py `
  tests/test_equelo_population_policy.py `
  tests/test_elo89_production.py `
  tests/test_elo_model_selection.py
```

`tests/test_elo89_production.py` already supplies evidence that the production
Elo-89 replay rates a blank-kimarite `W/L` result. It does not currently protect
the `P1` solver from the defect.

## Prior-map comparison

Before predictive evaluation, compare the old-semantics and corrected maps on:

- convergence, iteration count and final delta;
- mean, RMS and maximum rating change;
- changes by division and literal chii;
- east/west paired values and the unranked fallback;
- low-support extremes;
- the Makuuchi--Juryo and Juryo--Makushita boundaries; and
- entrants whose assigned initial rating changes materially.

Support counts should remain unchanged because they count chii observations,
not rated bouts. A support-domain change would therefore require explanation.

## Predictive evaluation

The corrected prior must be tested inside the complete Elo-89 contract: `q=400`,
divisional `k`, whole-population mean preservation, and the canonical binary
`W/L` forecast domain.

The existing population-policy evaluator accepts an explicit candidate prior:

```powershell
python -m src.analysis.equelo_population_policy.predict_population_policy `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07 `
  --prior "files/output/analysis/equelo_bkp1_wl_candidate/prior.csv" `
  --output "files/output/analysis/equelo_population_policy/prediction_p1_wl"
```

This verifies the population-policy result under the candidate but does not
directly compare corrected-`P1` Elo-89 with incumbent-`P1` Elo-89. Before
adoption, extend the evaluator to accept the incumbent prior and perform a
paired, basho-block-bootstrap comparison over identical bouts. Report log loss,
Brier loss, calibration error, new-entrant bouts, rating-maturity bands,
division groups and sekitori/sub-sekitori boundary bouts.

The correction is required by the data semantics even if its predictive effect
is neutral. The evaluation exists to expose unintended consequences, not to
decide whether known `W/L` results count as results.

## Adoption and publication

After acceptance, promote the candidate `prior.csv`, `iterations.csv` and
`manifest.json` to `files/output/analysis/equelo_bkp1`. The Elo-89 producer
already consumes that canonical `prior.csv` by default.

The Elo-89 output manifest should record the source `P1` SHA-256 and sufficient
source-manifest identity to make the published run reproducible. It currently
copies the prior into the run but does not preserve its calculated source hash
in the manifest.

Then rebuild without deployment:

```powershell
.\_boot89.ps1 --build-only
```

This regenerates the Elo-89 run, all rating-dependent site-data artifacts and
the static site from the promoted prior. After tests and human inspection, the
normal production build may deploy it.

## Build boundary

`_boot89.ps1` is a from-scratch publication build, not a from-scratch model-fit
build. It regenerates Elo-89 and the website but intentionally consumes the
existing canonical `P1` artifact.

Do not add automatic `P1` fitting to every `_boot89.ps1` invocation. Doing so
would silently refit the model as History grows and change historical ratings
during an ordinary site refresh. `P1` regeneration, evaluation and promotion
must remain an explicit model-maintenance operation. The routine build should
instead fail loudly if its required canonical prior is absent or invalid.

## Next

When this issue becomes active, first add the outcome-based `P1` eligibility
tests and improve the producer manifest. Then generate the same-History control
and candidate artifacts before changing the canonical prior.
