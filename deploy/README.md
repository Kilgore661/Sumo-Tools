New folder for brute force approach to finding deployment issues. "fails"
contains various structured AST-based approaches to this problem that have been
abandoned.

If this process is repeated, snapshot or diff the relevant output tree before
and after each pipeline stage. The most useful empirical fact is often the exact
set of files created or updated by one command. Record those deltas while
running the stage, rather than trying to reconstruct them afterwards.
