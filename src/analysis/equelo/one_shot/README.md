# one_shot package skeleton

This package wraps `src.analysis.equelo.expt1.simulate` to run modern-era,
closed-mode one-shot simulations and write Plotly HTML charts for probe chii.

## Entry point

```powershell
py -m src.analysis.equelo.one_shot --end 2026
```

## Notes

- Modern era is fixed at 1989 onward.
- Probe chii are configured in `config.py`.
- Random initialisation is by chii and is reused within each run.
- Public observable is the basho-boundary chii-to-rating map.
