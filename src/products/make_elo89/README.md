# make_elo89

`make_elo89` is the independent publication surface for the accepted Elo-89
website. It reuses the tested `make_site89` static-site implementation, but it
has separate operational identities:

- produced data: `files/output/analysis/elo89_site_bundle`;
- generated site: `files/output/make_elo89`;
- local served site: `A:/local/html/sumo-elo89`;
- local URL: `http://192.168.0.146/sumo-elo89/`;
- remote served site: `/var/www/html/sumo-elo89`; and
- remote URL: `http://68.66.241.105/sumo-elo89/`.

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

After inspection, deploy that exact existing tree both locally and remotely:

```powershell
py -m src.products.make_elo89 --no-build
```

The remote target uses SFTP and reads its password from the `GEOLOCATION`
environment variable, prompting if the variable is unavailable. The command
checks the remote connection before touching either deployment target. Local
deployment replaces the configured `sumo-elo89` tree. Remote deployment
uploads and replaces generated files but does not delete stale remote files.

The normal full production command deploys to both default targets. Add
`--local-only` to skip SFTP:

```powershell
.\_boot_elo89.ps1 --prod
.\_boot_elo89.ps1 --prod --local-only
```
