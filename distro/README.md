This folder contains distribution and release-support material for Sumo-Tools.
It is deliberately outside `src` because these files describe how to package,
bootstrap and publish the project rather than being part of a product runtime.

`fails` contains various structured AST-based approaches to this problem that
have been abandoned.

If this process is repeated, snapshot or diff the relevant output tree before
and after each pipeline stage. The most useful empirical fact is often the exact
set of files created or updated by one command. Record those deltas while
running the stage, rather than trying to reconstruct them afterwards.

`make_site2` deployment targets are configured in `distro/make_site2_targets.json`.
The file names each destination and declares the transfer method, target
location and inspection URL. `win_copy` targets are ordinary filesystem copies
and do not use passwords. `sftp` targets carry host/user information and may
name a password environment variable such as `GEOLOCATION`.

> [!WARNING]
> Before running `_boot.ps1` from an extracted distro, edit
> `distro/make_site2_targets.json`. `_boot.ps1` builds and deploys at the end,
> so stale or machine-specific target paths will be used if this file is not
> customised first.

`package_make_site2.py` creates a runnable make_site2 distro zip.

Basic distro:

```powershell
py distro/package_make_site2.py
```

This includes the true input files and writes a distro-specific `_boot.ps1`
with the downloader stages and fixed-supported Equelo refresh enabled.

Extended distro:

```powershell
py distro/package_make_site2.py --extended
```

This also includes bulky generated caches that make a fresh bootstrap much
faster. Its bundled `_boot.ps1` leaves the expensive refresh stages commented so
the extracted copy consumes the bundled caches first.
