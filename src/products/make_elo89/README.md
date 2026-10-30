# make_elo89

`make_elo89` is the independent publication surface for the accepted Elo-89
website. It reuses the tested `make_site89` static-site implementation, but it
has separate operational identities:

- produced data: `files/output/analysis/elo89_site_bundle`;
- generated site: `files/output/make_elo89`;
- local served site: `A:/local/html/sumo-elo89`;
- local URL: `http://192.168.0.146/sumo-elo89/`.

Nothing in this workflow writes to the existing `make_site89`, `sumo-tools89`,
`make_site2`, or `sumo-tools2` output trees.

Build the upload-ready production tree without deployment:

```powershell
py -m src.products.build_elo89 --prod --build-only
```

After inspection, copy that exact existing tree to the local server:

```powershell
py -m src.products.make_elo89 --no-build --local-only
```

The deployment command clears only the configured `sumo-elo89` target before
copying. Remote deployment is deliberately not configured yet.
