New folder for brute force approach to finding deployment issues. "fails"
contains various structured AST-based approaches to this problem that have been
abandoned.

If this process is repeated, snapshot or diff the relevant output tree before
and after each pipeline stage. The most useful empirical fact is often the exact
set of files created or updated by one command. Record those deltas while
running the stage, rather than trying to reconstruct them afterwards.

`make_site2` deployment targets are configured in `deploy/make_site2_targets.json`.
The file names each destination and declares the transfer method, target
location and inspection URL. `win_copy` targets are ordinary filesystem copies
and do not use passwords. `sftp` targets carry host/user information and may
name a password environment variable such as `GEOLOCATION`.
