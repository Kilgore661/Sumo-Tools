# Ozeki promotion analysis

Read the [binary classification experiment](docs/Experiment%20-%20Binary%20Classification%20of%20Ozeki%20Promotion.md)
for the purpose, Xn definitions, data boundaries, results and interpretation.
This is exploratory analysis of observed decisions, not a search for a hidden
JSA rule. Among the seven candidates, A32 has the highest in-sample F1:
77.86%, versus 71.79% for the conventional A33 benchmark (6.07 percentage points).

## Evaluate one classifier

From the repository root, with the live store running:

```powershell
python -m src.analysis.promotion.ozeki.evaluate_rule A 32
```

X is A, B or C; n is an integer from 0 to 45. All require at least n wins
across three consecutive held basho:

| Family | Conditions |
|---|---|
| A | All three basho at K/S |
| B | First at M/K/S, next two at K/S |
| C | All three at K/S, at least ten wins in each |

The command writes `files/output/analysis/promotion/ozeki/rules/A32.json`.
Use `--output-dir PATH` to choose another directory. Repeating the same
classifier in that directory replaces its JSON file.

## Run the experiment

```powershell
python -m src.analysis.promotion.ozeki.score_rules
```

The orchestrator evaluates A31, A32, A33, B31, B32, B33 and C33 on one live
History snapshot. It writes seven Xn.json files into a new UTC timestamped
`_rules` directory beneath `files/output/analysis/promotion/ozeki/`, then reads
those files to generate `report.md`, ranked by F1 with all tied winners named.
Use `--output-dir PATH` to select a directory explicitly.

Each JSON includes definitions, source coverage, TP/FP/FN, precision, recall,
F1, qualifying windows, false-negative events and unresolved windows. Undefined
metric denominators yield 0.0. True negatives are not enumerated.

## Observation contract

Scoring begins with the July 1958 promotion banzuke. The documented run ends
with September 2026. Promotion opportunities, rather than distinct people,
are counted; overlapping windows count separately. Previous ozeki tenure does
not split the population. Immediate reinstatements are excluded, identified
as O-to-S-to-O with at least ten wins in the intervening S basho.

Wins include fusensho and exclude playoffs. Ranks use core enum values,
including annotated ranks. Cancelled tournaments are not inserted; May 2011
is retained. Input is assumed to include every held basho in its date range.
Missing next rank/banzuke is unresolved. Missing historical bout results can
undercount qualifying windows; see the experiment's limitations.

## Supporting audits

```powershell
python -m src.analysis.promotion.ozeki
python -m src.analysis.promotion.ozeki.candidates
```

The first command lists observed promotions and their preceding rank/results,
with reinstatements and boundary cases separately audited. It accepts
`--history-zip PATH` instead of the live store and `--output-root PATH`.
Its timestamped output contains `findings.md`, `promotions.csv`,
`preceding_basho.csv`, `boundary_cases.csv`, `excluded_reinstatements.csv`
and a provenance manifest.

The second enumerates A33 qualifying windows and checks the next banzuke,
writing `qualifying_windows.csv`, `not_promoted.csv`, `findings.md` and a manifest.

These earlier audits include Kotogahama's May 1958 promotion, using the user's
November 1957 S, 10-5 boundary supplement. That evidence is marked
`user_supplied`; it does not modify History. It is outside the scoring cutoff,
so the audit has 72 promotions while the classification experiment has 71.
The [early positive-case findings](findings.md) are retained as an exploratory
stage, not as the final experiment counts.

## Verification

```powershell
python -m pytest tests/test_ozeki_promotion.py
```

Focused checks cover rank/threshold conditions, result counting, boundaries,
reinstatement exclusion, repeated and overlapping opportunities, JSON output,
metrics and report generation. The experiment records the completed checks
and saved output run used for its results.
