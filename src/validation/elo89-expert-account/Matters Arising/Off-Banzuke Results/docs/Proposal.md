# Proposal: classify off-banzuke results by status and epoch

## 1. Purpose

Answer two questions before considering any rating-policy experiment:

1. Are rikishi who occur in represented results while absent from the parsed
   banzuke actually recorded as `Mz` for that basho?
2. Do any such bouts occur in the post-1988 Elo-89 era?

Those answers determine whether this is an Elo-89 issue at all. A more general
include-versus-exclude comparison is conditional work, not part of the first
experiment.

## 2. Definition and frozen input

An *off-banzuke bout* is a result already represented in canonical `History`
for which either endpoint is absent from `History[date].banzuke.riks` for that
basho.

The experiment will use the repaired frozen History:

```text
files/output/Historys/1958_01 to 2026_11.zip
```

It will inspect `1958-01` through `2026-09`, but report the two epochs
separately:

- pre-1989: `1958-01` through `1988-11`;
- Elo-89: `1989-01` through `2026-09`.

The History path and SHA-256 must be retained. Counts inherited from older
live-store runs are reconciliation evidence rather than inputs.

## 3. Experiment A: endpoint census

Inspect every represented result before Elo-89 outcome selection. Retain one
row for every bout having at least one missing endpoint, recording:

- basho, day and result type;
- both rikishi IDs, outcomes and represented names;
- same-basho parsed-banzuke membership and chii for each endpoint;
- number and identity of missing endpoints;
- whether the current Elo-89 selector would rate the result; and
- whether the basho is pre-1989 or post-1988.

The output must include an atomic exception table even when the Elo-89 subset
is empty.

## 4. Experiment B: is the missing endpoint Mz?

For each missing endpoint, read the literal rank/status cell for the same
basho from the locally cached SumoDB `Rikishi.aspx` career page. Report the
status without inference: `Mz`, `Bg`, `Kg`, a formal rank, no row, or missing
page.

The primary result is a status-by-epoch table. It must answer directly:

- total missing endpoints;
- how many have status `Mz`;
- whether every missing endpoint is `Mz`; and
- whether any non-Mz or unresolved endpoint needs separate explanation.

Absence from the parsed banzuke must be determined by RikId membership, not by
status text or shikona matching.

## 5. Reconciliation checks

The run must reconcile two known observations.

### Five `1974-11` exclusions

Compare the full-history census by exact bout identity with the five rows
previously retained by the Equelo2 baseline. Record whether every old row is
reproduced and give the newly recovered same-basho status of each missing
endpoint.

The rating-persistence census found only Tatsuwaka because it counted bouts
during a gap followed by a return. This experiment instead inspects every
bout endpoint, so the differing counts are not necessarily contradictory.

### RikId 13011 in `2026-07`

Verify that the seven known results remain represented and that the repaired
History now contains RikId 13011 on the same-basho banzuke as `Sd80eTD`. If
either assertion fails, report an input-version violation. These seven bouts
must not be classified as current off-banzuke cases merely because an older
History omitted the TD entry.

## 6. Interpretation

The immediate conclusion follows the evidence matrix:

| Result | Meaning |
|---|---|
| All cases pre-1989 | No effect on the current Elo-89 history |
| All missing endpoints are Mz | The cases arise at the ranked/Mz representation boundary |
| A missing endpoint has a formal rank | Parser or History defect, not an Mz policy case |
| A post-1988 case exists | A real Elo-89 include-versus-exclude decision is required |
| Status is unresolved | Source provenance must be repaired before classifying the case |

This experiment concerns results already represented in `History`. Source
pages may contain additional Mz bouts discarded upstream. That is a separate
source-completeness question and must not be used to alter this census's
denominator.

If the Elo-89 count is zero, do not run a historical rating comparison whose
two sides are necessarily identical. Record that the current contract conflict
has no realised numerical effect. A prospective policy can be addressed later
with synthetic cases or after source completeness is considered.

If genuine post-1988 cases exist, the next proposal will compare inclusion
and exclusion while holding accepted P1-WL and frozen rating persistence
fixed.

## 7. Outputs and tests

The timestamped output directory will contain:

- `off_banzuke_bouts.csv`;
- `epoch_status_summary.csv`;
- `missing_status_summary.csv`;
- `known_case_reconciliation.csv`;
- `violations.csv`;
- `manifest.json`; and
- `findings.md` answering the two questions in plain language.

Focused tests will establish that:

- a missing endpoint is classified from its same-basho career status;
- a present annotated `TD` rikishi is not classified as off-banzuke;
- epoch classification is correct; and
- output ordering and schemas are deterministic.

The experiment will not add Mz to `Chii`, reconstruct unrepresented results,
change Elo-89, refit P1-WL, or reopen frozen persistence.
