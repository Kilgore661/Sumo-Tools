# Rating Persistence

## Status

Concluded validation work package for the second matter arising from the
Elo-89 expert account. The descriptive census is recorded in
[`Census Findings.md`](Census%20Findings.md), and the controlled comparison and
decision are recorded under
[`Frozen Persistence Comparison`](Frozen%20Persistence%20Comparison/README.md).

This folder investigates what Elo-89 should do when a rikishi leaves the
represented active population and later reappears. In particular, it will
compare the current rule—discard the old rating and initialise the returnee
from the current P1 prior—with policies that preserve information from the
rikishi's earlier bouts.

Frozen persistence is adopted as the Elo-89 lifecycle policy. The completed
census established that the apparent return population is overwhelmingly
created by the ranked model's mae-zumo boundary: 424 of the 436
Jonokuchi-to-Jonokuchi cycles contain an explicit `Mz` stage. The subsequent
controlled replay found no invariant failure or predictive reason to discard
the existing rating on return.

## The question

Should a returning rikishi:

1. be reinitialised from the P1 rating for his new chii, as in current
   Elo-89;
2. resume his last literal rating;
3. retain a rating carried through the common population shifts made during
   his absence; or
4. receive some other treatment, such as uncertainty or decay?

The present working view is that absence of competition is absence of new
bout evidence. It should therefore neither update nor erase the point estimate
of the rikishi's strength. That view favours persistence, but it does not by
itself decide whether an archived rating should remain numerically fixed or
move with shifts in the rating population's coordinate system.

## Current Elo-89 behaviour

The exact replay removes the ratings of rikishi who leave its active set. A
later return therefore has no carried rating and is treated like a new entry:
the rikishi receives the P1 value associated with his current chii.

This behaviour is documented in the expert account, especially:

- [`09 The Exact Elo-89 Model.md`](../../09%20The%20Exact%20Elo-89%20Model.md);
- [`10 Why Elo-89 Makes Those Choices.md`](../../10%20Why%20Elo-89%20Makes%20Those%20Choices.md); and
- [`12 What Has and Has Not Been Established.md`](../../12%20What%20Has%20and%20Has%20Not%20Been%20Established.md).

It is implemented in `src/analysis/elo89/replay.py`, where departing ratings
are deleted before active rikishi without ratings are initialised from P1.
The expert account records this as a modelling judgement, not a policy shown
to be predictively superior to persistence.

## Prior work and its limits

The principal earlier discussion is
`src/analysis/docs/story/17 Pre-1989 Bout-Data Completeness and Rating
Persistence.md`. Its January 1958–July 2026 audit reports:

- 679 ranked-banzuke gap-and-return events;
- 590 affected rikishi among 9,071 distinct ranked rikishi;
- 666 events of the form `Jonokuchi -> unranked -> Jonokuchi`; and
- 678 events with an explicit intervening `Bg`, `Mz`, `Kg`, or `Sj` status.

It identifies Sokokurai's makuuchi departure and return as the conspicuous
modern exception. The overall picture suggests that most gaps are lower-rank
administrative lifecycle events rather than established rikishi leaving and
later resuming an ordinary career.

Those figures were initially orientation rather than present validation
evidence because:

- the audit starts in 1958, whereas this validation package applies to the
  Elo-89 epoch beginning `1989-01`;
- the committed calculation or output that produced the 679-event census had
  not been identified; and
- the earlier work did not run a controlled Elo-89 comparison of persistence
  against reinitialisation.

The first tranche has now reconstructed all of those headline figures exactly
and has produced a separately scoped Elo-89 census. The later
`src/analysis/equelo2_baseline` replay implements both behaviours
through `persist_inactive_ratings`, and explicitly distinguishes returning
rikishi. Its larger experiment also changes the historical regime, however,
so its headline comparison does not isolate the return policy needed here.

## Cases that must be distinguished

The census must not treat every apparent absence as the same event. It should
separately identify, as far as the represented source permits:

- missing bouts while the rikishi remains on the banzuke;
- absence from the ranked banzuke with an explicit administrative status;
- movement below and back onto the ranked banzuke;
- a genuine departure followed by an exceptional return;
- gaps caused by incomplete or inconsistent source representation; and
- bouts involving an off-banzuke rikishi, which overlap the separate third
  matter arising.

The operational definitions of *active*, *departure*, *absence*, *return* and
*career identity* must be stated before counts are accepted.

## First tranche: reproducible Elo-89 census

The first tranche produced a post-1988 census from an explicitly identified
History source. It records, for every gap event:

- rikishi identity;
- last represented basho and chii before the gap;
- first represented basho and chii after the gap;
- number of intervening basho;
- all represented intervening statuses;
- division before and after the gap;
- whether the rikishi has represented bouts during the gap; and
- whether the event crosses the sekitori boundary or otherwise looks
  exceptional.

Summary outputs give counts of events and distinct rikishi, gap length,
pre- and post-gap division/status combinations, calendar distribution, and a
short inspectable list of exceptional cases. The program, its configuration
and timestamped outputs will be retained under the validation conventions:
code beneath `src/validation`, and generated evidence beneath
`files/output/validation`.

This tranche is implemented by `src.validation.rating_persistence`. It also
reconstructed the earlier 679-event definition exactly, restoring the missing
provenance for that claim. See [`Census Findings.md`](Census%20Findings.md).

Run the current Elo-89 census from the repository root with:

```powershell
py -m src.validation.rating_persistence `
  --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip" `
  --start 1989-01 `
  --end 2026-09
```

The live History is used when `--history-zip` is omitted. Generated runs are
written to `files/output/validation/elo89-expert-account/Matters
Arising/Rating Persistence/output/`. Each timestamped directory contains the
atomic gap-event table, exceptional cases, summaries, findings and a manifest
with source identities and the exact event definition.

## Controlled comparison and decision

The controlled replay held the History source, P1-WL prior, Elo-89 parameters
and all other policies fixed while changing only the treatment of a returning
rikishi. The control deleted the rating and reset from P1-WL. The candidate
archived the literal rating unchanged outside the active population and
restored it on return.

This comparison will not add `Mz`-versus-`Mz` results to the rated bout domain.
Persistence and Mz bout eligibility are separate model decisions. The first
can be tested by retaining an already informed rating while continuing to
treat an unrepresented interval as supplying no new bout evidence. Expanding
the bout domain would additionally require an unranked prior, K policy and
population-membership rules and is not part of this tranche.

The comparison examined:

- how often the policies actually assign different return ratings;
- the size and duration of those differences;
- predictive log loss and Brier score after return;
- effects on sekitori and exceptional individual careers;
- effects on downstream records and site artifacts; and
- whether any aggregate result is dominated by numerous short Jonokuchi gaps.

The detailed specification is in
[`Frozen Persistence Comparison/docs/Proposal.md`](Frozen%20Persistence%20Comparison/docs/Proposal.md).
Its results and accepted decision are in
[`Frozen Persistence Comparison/docs/Findings.md`](Frozen%20Persistence%20Comparison/docs/Findings.md).

The comparison covered all 437 returns and 581,634 rated forecasts. The reset
control exactly reproduced canonical Elo-89, all returns matched the census,
and no invariant failed. Persistence improved log loss and Brier score in the
complete replay and every aggregate return-focused window. The largest
differences were explainable lower-division cases in which reset replaced a
heavily informed weak rating with a much higher exact-rank prior; the evidence
showed no unexplained sekitori disturbance.

The adopted rule is therefore that an absent rating remains numerically
frozen and inert. It receives no bout updates or population shifts and is
excluded from active means and normalisation. If the rikishi returns, the
rating and its provenance are restored before the ordinary start-of-basho
adjustment. This is now part of the intended Elo-89 model contract. Promotion
to canonical production code and regeneration of published artifacts are the
next implementation step, not part of this validation experiment.
