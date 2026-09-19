# Ozeki promotion prospects

This pipeline implements the Ozeki portion of the
[promotion-prospects proposal](../../docs/Promotion%20Prospects%20Statistical%20Analysis%20Proposal.md).
It produces research artifacts, not public-site data.

From the repository root:

```powershell
python -m src.analysis.promotion.prospects.ozeki
```

The default run uses the live History and writes a new timestamped directory
under `files/output/analysis/promotion/prospects/ozeki/`. It prints numbered
progress stages to the console. Progress messages are not written to the
artifacts.

Options:

```text
--history-zip PATH        use a saved History zip instead of the live store
--output-root PATH        change the parent output directory
--bootstrap-samples N     rikishi-cluster bootstrap repetitions (default 2000)
--seed N                  deterministic bootstrap seed (default 20260919)
```

The run writes:

- `opportunities.csv`: resolved and unresolved M/K/S, K/S, K/S windows;
- `promotions.csv`: audited promotion events, including events outside that
  candidate pool;
- `total_wins.csv`, `rank_patterns.csv`, `minimum_wins.csv` and
  `weak_result_position.csv`: descriptive support tables;
- `rules.csv`: the predeclared A/B threshold ladder and C33, including Wilson
  and rikishi-cluster bootstrap intervals;
- `period_rules.csv`: fixed broad-period diagnostics;
- `forward_validation.csv`: expanding-window rule selection and later-period
  evaluation;
- `report.md`: a human-readable summary; and
- `manifest.json`: definitions, coverage, provenance and artifact hashes.

The fixed periods are diagnostics, not claims about institutional eras. The
forward validation selects a rule only on the earlier period and evaluates the
frozen selection on the later period.

