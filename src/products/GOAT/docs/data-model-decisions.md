# GOAT data-model decisions and open questions

Status: working decision log as of 2026-09-03.

This document records what has actually been agreed. It deliberately separates
domain and product decisions from plausible implementation ideas. A physical
file contract must be derived from these decisions rather than treated as a
source of new requirements.

## 1. Settled decisions

### 1.1 History and dates

- The fact producer receives and publishes the complete supplied `History` from
  the 1958 data epoch.
- Users do not select dates or a historical sub-period.
- There is no universal analytical start date. Every future metric declares
  the facts it needs and the earliest date for which they are complete.
- Makuuchi facts, including yusho, may be used from 1958.
- Metrics requiring complete sub-sekitori bouts may use only January 1989
  onwards.
- If Elo is added later, the product may need a separate switch governing
  whether pre-1989 rating evidence is admissible. That switch is not part of
  the initial model.
- The two scheduled but canceled basho do not count as basho, banzuke-basho
  opportunities or positions in a fixed window.

### 1.2 Active rikishi

A rikishi is active for a banzuke if and only if he appears anywhere on that
banzuke. For a dataset describing the complete supplied History, current active
status is determined from the latest supplied banzuke, regardless of division.

### 1.3 Complete and partial careers

Career completeness is metric-dependent. It is determined by comparing the
relevant part of the rikishi's career with the completeness boundary of the
facts required by that metric. A rikishi can therefore have a complete yusho
career and a partial all-division win career.

Eligibility for the GOAT population still requires a Makuuchi-banzuke
appearance.

### 1.4 Divisional scope

- Win rate and contested-bout win rate cover all represented divisions.
- Longest winning streak covers all represented divisions and may continue
  across promotion or demotion.
- Facts explicitly named Makuuchi facts, such as Makuuchi wins, Makuuchi yusho
  and Makuuchi-banzuke basho, remain Makuuchi-only.
- The model retains lower-division performance rather than deciding in advance
  that it cannot affect a user's GOAT criteria.

### 1.5 Result vocabulary

- A **win** is a contested `W`.
- A **loss** is a contested `L`.
- `FS` is a **fusen win** or **administrative win**, not an ordinary win.
- `FP` is a **fusen loss** or **administrative loss**, not an ordinary loss.
- The win total in a recorded basho score is `W + FS`.
- The loss total in a recorded basho score is `L + FP`.

The term **official win** is not used by the product because it obscures the
difference between winning a bout and receiving a fusensho.

Winning streaks follow the contender's wins and availability:

- `W` extends a streak;
- `L` ends it;
- `FS` neither extends nor ends it, because the contender was available and the
  opponent did not appear;
- `FP`, kyujo or another genuine absence by the contender ends it; and
- a normal unscheduled day, including a day between lower-division bouts, does
  not end it.

### 1.6 Scheduled opportunities

Win rate covers all divisions. Its numerator is `W`; its denominator is the
sum of the nominal scheduled bout opportunities associated with each banzuke
appearance:

- normally 15 for a sekitori; and
- normally 7 below Juryo.

A banzuke-gai period has no banzuke appearance and contributes no scheduled
bout opportunity.

Absence, `FP` and `FS` consume the relevant opportunity without adding a win.
Thus a 7-0-8 sekitori basho contributes `7/15` to the component totals. The
separate contested-bout win rate is `W / (W + L)`.

The product does not require separate total-absence, partial-absence or
partial-withdrawal classifications. For the relevant rate, the necessary facts
are wins (`W`) and the division-appropriate scheduled opportunities.

Availability is not a separate GOAT factor or statistic. A rikishi who does not
appear for a scheduled opportunity receives no `W`, and that opportunity
remains in the win-rate denominator.

The historical source data must be checked for any departures from these normal
division schedules before this rule is implemented as an invariant.

### 1.7 Fixed-basho windows

- A 6-, 12-, 24-, 36- or 60-basho window follows consecutive non-canceled
  banzuke in the global historical sequence.
- The sequence does not close up around a rikishi's absence from the banzuke.
- A banzuke-gai period therefore occupies a window position.
- It contributes no bouts or scheduled opportunities, but time has still
  passed within the window.
- The initial best-window measure is the number of wins (`W`) in the window.
- Fusen wins (`FS`) do not increase the window's win count.
- Alternative window measures are deferred.
- Every window tied for the maximum win count is retained as co-best. The
  producer does not select an arbitrary earliest or latest representative.

### 1.8 Championship and prize facts

The producer should retain separate counts for all recorded administrative
markers:

- `Y`: yusho;
- `D`: doten-yusho/playoff loser;
- `J`: non-playoff jun-yusho; and
- `K`, `G`, `S`: the three special prizes.

The championship score is also retained, so that a 15-0 and a 12-3 yusho
remain distinguishable as facts. Retaining a fact does not automatically make
it an initial selectable GOAT factor.

The initial requirements use **doten-yusho**, not jun-yusho, as the runner-up
achievement statistic. Zensho-yusho count and rate are descriptive data rather
than initial GOAT ranking factors.

Yusho while ranked at yokozuna is an initial selectable GOAT factor. Yusho at
ozeki or below is retained as descriptive data but is not an initial factor.

`J`, `K`, `G` and `S` are descriptive data only in the initial product. They
remain counted and can be reconsidered later without changing the underlying
facts.

Playoff appearances, playoff wins and playoff losses are descriptive data only
in the initial product. `D` remains a separate initial factor.

### 1.9 Observed J/D semantics

The Makuuchi probe over 410 basho found:

- 325 basho with at least one `J`;
- 85 basho with at least one `D`;
- no basho in which `J` and `D` coexist;
- all 534 `J` recipients at the second-highest distinct basho-score win total;
  and
- two basho where another rikishi shared that total without receiving `J`.

Consequently, `J` is retained as an administrative source marker and is not
reconstructed mechanically from the score ordering. `D` identifies a losing
participant in a playoff for the leading score.

### 1.10 Playoff detail

- `Y` and `D` reliably identify the participants in known Makuuchi playoffs.
- Old histories without bout detail remain valid inputs.
- Missing playoff detail is unavailable, not a zero-win/zero-loss record.
- A proposed future `History.playoffs` contract and the parked `d=16`
  investigation are described in `playoffs.md`.

## 2. Questions still to resolve

Questions should be considered individually. The next unanswered question is
listed first.

### 2.1 Ranking combination

Before the ranking interface can be specified, decide:

- normalization of unlike measures;
- weighted versus priority-order modes;
- tie handling;
- treatment of unavailable values; and
- whether descriptive-only facts can be promoted to criteria by the user.

### 2.2 Evidence presentation

The requirement to inspect the basho and bouts underlying every statistic is
agreed, but the necessary depth and user interaction have not been specified.
This affects how much evidence data the producer must publish.

### 2.3 Exceptional tournament status

May 2011 requires explicit treatment. Its precise contribution to championship
opportunities, rates and fixed-window positions remains to be confirmed.

### 2.4 Age measures

Age at first and last yusho requires a verified birth-date source and a policy
for unavailable or uncertain biographical data.

### 2.5 Physical publication contract

File formats, file partitioning, schema versioning, integrity metadata and
atomic publication have not been agreed. They are implementation questions to
answer only after the logical data model is sufficiently settled.
