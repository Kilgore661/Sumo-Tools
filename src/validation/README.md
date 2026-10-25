# Validation

This package contains reproducible investigations which test documented model
claims and unresolved questions. It is separate from `src.analysis`: analysis
retains the project's research history, while validation work must preserve a
clear route from a stated question to inspectable evidence.

Each validation project should keep together:

- its question, scope and definitions;
- runnable code;
- the exact input identity, including hashes where practical;
- the invocation and relevant code version;
- persisted outputs; and
- findings and any resulting decision.

Outputs stored inside this package are intentional repository artifacts. They
must be committed with the code and documentation that explain them. A rerun
must not silently overwrite an adopted result without recording the changed
input or implementation.

## Scope: the January 1989 Elo-89 line

Within this package, unqualified *validation* means validation of the Elo-89
work whose rating epoch is `1989-01`. It does not mean validation of every
claim which might be made about the full represented History beginning in
`1958-01`.

The project did not move from `1958-01` to `1989-01` in one identifiable code
change or decision commit. Earlier work tried to retain the 1958 epoch while
accommodating the incomplete and irregular lower-division evidence. Repeated
investigations showed that doing so required increasingly substantial
compromises to the common methodology and interpretation intended for the
published ratings. The 1989 epoch emerged incrementally as those problems
accumulated, until moving the boundary became the only credible route to the
model now being documented and published.

That history creates an important discipline. Earlier analyses, utilities and
saved findings may assume a `1958-01` epoch even when their subject now forms
part of Elo-89. Their conclusions must not be imported into validation merely
because the code still runs or the result looks relevant. Counts, coverage
claims and other data findings must be regenerated or explicitly restricted to
the `1989-01` epoch before they can support the current work.

Every validation question and persisted output must therefore state:

- the model or publication line being validated;
- the selected date interval, independently of the wider interval represented
  by the input History; and
- whether cited earlier evidence was produced on that same interval or has
  been checked again for it.

Work deliberately concerning another epoch must say so explicitly and remains
separate evidence; it does not silently alter the scope of Elo-89 validation.

## History input convention

Validation commands which consume `History` should use the published live
store by default through `src.infra.live_store.api.get_history()`. The tracker
is part of the normal development environment and may be assumed to be
running. If it is not available, `get_history()` already terminates with an
explicit operational message; validation code should not catch that failure
and silently substitute another source.

For an intentionally fixed or offline run, a command should accept:

```text
--history-zip PATH
```

Supplying that option selects the named annotated History zip instead of the
live store. New validation commands should prefer this explicit path over the
older `--zip` Boolean convention, which derives a filename from start and end
years and makes the actual input less visible.

Every persisted run must identify the source it actually used. For a zip this
includes its resolved path and SHA-256. For the live store it includes the
published store name, represented date range and a reproducible fingerprint of
the selected History content. The represented range of the source is not the
validation epoch: a full `1958-01` History may be used as input while the
declared selection begins at `1989-01`. There is no automatic live-to-zip
fallback.

The Elo-89 expert account and its matters arising live in
[`elo89-expert-account`](elo89-expert-account/00%20Contents.md).

## Migration and traceability

The Elo-89 expert account was originally drafted and committed under
`src/products/make_site89/docs/elo89-expert-account` in commit `aa311ee`. On
24 October 2026 it was moved to
`src/validation/elo89-expert-account` so that the account, its unresolved
questions, the code used to investigate them and the resulting evidence can be
maintained together. The first matter folder was also renamed from
`1. Kimarite` to `Kimarite` during that move.

The account still contains references to material under `src/analysis`. These
references are part of the evidential history and may identify exploratory
code, documentation or outputs whose provenance is less complete than the
standard required here. As each matter is validated, the relevant reference
should be replaced or supplemented by the corresponding reproducible material
under `src/validation`. References must not be rewritten merely to make the
path look current: the validation record should distinguish historical
evidence from evidence actually regenerated and adopted here.
