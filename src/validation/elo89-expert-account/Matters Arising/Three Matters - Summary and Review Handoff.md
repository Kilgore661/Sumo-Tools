# Three Matters: Summary and Expert-Account Review Handoff

## Purpose

The Elo-89 expert account exposed three concrete uncertainties in the
model contract:

1. whether a represented W/L result is valid when kimarite is missing;
2. whether a rating should survive disappearance from and return to the
   represented active population; and
3. whether represented bouts involving a rikishi absent from the parsed
   banzuke matter to Elo-89.

All three have now been investigated against the declared Elo-89 epoch. Two
produced accepted changes to the intended model. The third was discounted as
a realised post-1988 issue, while leaving a separate prospective and
source-completeness question visible.

This document is the handoff from investigation to revision of the expert
account. The original account remains the baseline which raised the questions;
it should not be silently edited into a false history of what was previously
known.

## Headline decisions

| Matter | What the evidence established | Decision | Production state |
|---|---|---|---|
| Missing kimarite | 33,521 post-1988 binary W/L bouts have no kimarite; all are in Makushita and below | Kimarite is irrelevant to rating eligibility; adopt the epsilon-10 P1-WL prior | Validated through a complete candidate site; canonical promotion remains to be done |
| Rating persistence | 437 returns affect 365 rikishi; almost all are Jonokuchi/Mz boundary cycles | Freeze the literal rating and provenance while inactive; restore before the return-basho start adjustment | Accepted model rule; canonical promotion remains to be done |
| Off-banzuke results | Five represented bouts exist, each with one Mz endpoint, all in `1974-11`; none is post-1988 | Discount as a realised Elo-89 issue; do not run an empty historical policy comparison | No Elo-89 rating or site change required |

“Accepted” describes the intended successor Elo-89 contract. The retained
canonical production implementation has not yet been promoted to P1-WL plus
frozen persistence. The revised account must distinguish the accepted target
model from the currently installed artifact until code and artifacts are
promoted together.

## 1. Missing kimarite

### Question

Should a represented bout be excluded merely because its winning technique
is not recorded?

### Evidence

The epoch-corrected audit found:

> In the post-1988 era there were 33,521 missing kimarite, all of which
> occurred against results in Makushita and below.

Every affected observation is a represented binary W/L result. The affected
bouts occur from `1989-01` through `1991-05`. Kimarite is not an input to the
Elo equations, so its absence does not remove the known identities, contest or
outcome.

The controlled prior fit compared incumbent P1, which admitted 548,117 of
584,671 represented observations, with P1-WL, which admitted 581,634. P1-WL
included all 33,521 blank-kimarite W/L bouts and continued to exclude four
non-binary observations.

P1-WL retained the established benefit of informed initialisation and made
small, controlled downstream changes. Against the same-History P1 replay it
slightly improved mean log loss and Brier score, although not every secondary
statistic favoured it. A tighter fixed-point threshold was harmful: sparse
literal-chii values became extreme and prediction deteriorated. A broad sweep
confirmed that epsilon 10, stopping after 18 iterations in the adopted run,
lies in the useful early-stopping region.

The complete site-data bundle was compared and a non-deployed P1-WL website
was built and inspected. No invariant failed and no obvious page-level problem
was found.

### Decision and action

- A represented binary W/L result is eligible whether or not kimarite is
  recorded.
- P1-WL replaces P1 as the accepted entrant-prior artifact.
- Epsilon 10 is retained as material regularisation, not described as
  numerical convergence to a uniquely correct fixed point.
- Epsilon-3 P1WL and further iteration were rejected.
- No canonical prior, production replay or deployed site was changed during
  validation. Promotion and regeneration remain required.

## 2. Rating persistence

### Question

When a rikishi leaves the represented active population and later returns,
should Elo-89 discard his rating and initialise him from the current chii
prior, or preserve the earlier rating evidence?

### Evidence

The ranked-banzuke census found 437 return events involving 365 rikishi from
`1989-01` through `2026-09`:

- 436 are Jonokuchi-to-Jonokuchi cycles;
- 424 of those contain an explicit Mz stage;
- Sokokurai is the sole substantively different modern case; and
- no return event contains a represented bout during the gap.

This showed that apparent disappearance is overwhelmingly a boundary effect
of the ranked-only representation rather than evidence of a new career.

The controlled comparison held History, P1-WL, q, K, bouts and all other
rules fixed. Its reset control exactly reproduced canonical Elo-89. The
candidate archived the rating and provenance outside the active population,
gave them no updates or common shifts, excluded them from all active means,
and restored them before the ordinary return-basho start adjustment.

The comparison covered 581,634 forecasts and produced no invariant violation.
Frozen persistence improved both log loss and Brier score globally and in
every aggregate return-focused window. For example:

| Scope | Log-loss difference | Brier difference |
|---|---:|---:|
| Complete replay | -0.000511568 | -0.000259660 |
| First return bout | -0.015474126 | -0.007857711 |
| First seven return bouts | -0.005485247 | -0.001915892 |
| Return basho | -0.005829219 | -0.001899456 |

Negative differences favour persistence. The largest active difference was
854.53 points for Higohikari at Jk20e, where reset discarded a long, weak,
heavily informed career rating and substituted a much higher unstable exact-
Jonokuchi prior. The largest sekitori difference in that basho was 24.67.
Sokokurai's single case was mixed across forecast windows and did not overturn
the aggregate evidence or the information-preservation principle.

### Decision and action

- Absence from the represented active population supplies no new bout
  evidence and does not erase the existing estimate.
- On departure, archive the literal rating and its provenance.
- While absent, the archive is inert: no updates, common shifts, active means
  or normalisation.
- On return, restore the archive before the ordinary start-of-basho active-
  population adjustment.
- Retain the cumulative rated-bout counter across the gap.
- Do not introduce decay, uncertainty growth or Mz-versus-Mz results as part
  of this decision.
- Canonical replay and site promotion remain required.

## 3. Off-banzuke results

### Question

Are represented results with an endpoint absent from the parsed banzuke
actually Mz boundary cases, and do any occur in the post-1988 Elo-89 era?

### Evidence

The complete current-History endpoint census found five bouts, each with one
missing endpoint:

- all five occurred in `1974-11`;
- all five are represented binary W/L results;
- every missing endpoint has the literal same-basho source status `Mz`;
- no status is unresolved or non-Mz; and
- the post-1988 count is zero.

The run exactly reproduced the five older Equelo2 exclusions. It also
reconciled the seven formerly reported `2026-07` cases involving RikId 13011:
the bouts remain represented, but the repaired History correctly places him
on the banzuke at `Sd80eTD`. Those were an earlier parsing defect, not current
off-banzuke observations.

### Decision and action

- There is no realised off-banzuke-result issue in the represented Elo-89
  history.
- An include-versus-exclude historical replay was discounted because its two
  Elo-89 bout streams would be identical.
- No Elo-89 rating, prior or website artifact needs changing for this matter.
- The prospective contract conflict remains: retained code would rate a
  future represented off-banzuke W/L result, whereas older prose says to
  exclude it.
- Source pages may contain Mz results omitted before canonical History is
  formed. That is a separate source-completeness and participation-model
  question; the zero represented-history count does not answer it.

## Combined accepted model delta

Relative to the baseline expert account, the intended successor model changes
in two places and is clarified in a third:

```text
represented result domain
    binary W/L, regardless of kimarite
        -> fitted epsilon-10 P1-WL entrant prior
        -> chronological Elo-89 replay

departure from represented active population
    archive literal rating + provenance + support
    exclude archive from all active operations
    restore on return before start adjustment

off-banzuke represented result
    no realised post-1988 observation
    prospective rule still to be aligned with source/participation policy
```

The accepted changes interact. P1-WL must be the initialisation artifact used
by the promoted replay, while frozen persistence determines that a genuine
returnee normally does not consume that prior again. A first entrant still
does. These policies should therefore be promoted and tested together before
new public artifacts are declared canonical.

## Expert-account revision map

The next account review should at least revisit:

| Chapter | Required review |
|---|---|
| `00 Contents` | Update chapter summaries which name P1, reinitialisation and unresolved matters |
| `01 What is Elo-89` | Replace returning-rikishi P1 initialisation with frozen restoration; name P1-WL |
| `02 Is the Banzuke a Rating System` | Remove the claim that return normally reuses the current chii prior |
| `07 Problems Applying Elo to Chess and Sumo` | Retain the general modelling problem, then state the selected point-estimate rule |
| `08 From Elo to Elo-like Systems` | Distinguish generic policy choices from the now-selected Elo-89 choices |
| `09 The Exact Elo-89 Model` | Rewrite the exact result domain, prior identity, state lifecycle, active set, pseudocode and artifact contract |
| `10 Why Elo-89 Makes Those Choices` | Replace the P1 and reset rationales with the new experiments and decisions |
| `11 Critique of Elo-89` | Mark the kimarite and reset defects resolved in the intended model; retain their limitations and the production gap |
| `12 What Has and Has Not Been Established` | Add the new controlled evidence and remove claims that these comparisons have not been made |
| `13 Other Choices Are Possible` | Reclassify P1-WL and frozen persistence from alternatives to selected policies |

Chapters not listed still need a contradiction sweep. They may use “P1” or
“return” incidentally, and conceptual prose can become misleading even where
the equations do not change.

## Review for further matters arising

After applying the accepted changes to a successor account, review the whole
account in two passes.

### Pass 1: consistency with accepted work

- Search every chapter for P1, kimarite, entrant, departure, absence, return,
  off-banzuke, Mz, active population and unranked fallback.
- Separate descriptions of the baseline implementation from the accepted
  successor contract.
- Check that equations, pseudocode, tables, manifests and prose describe the
  same event ordering and state.
- Do not describe validation code or a candidate website as canonical
  production until promotion has occurred.

### Pass 2: find new issues

Classify each remaining caveat as one of:

- an implementation/prose contradiction;
- a model choice with no supporting comparison;
- a data-domain or epoch ambiguity;
- incomplete provenance or artifact identity;
- a known limitation which needs disclosure but not repair; or
- a genuinely new matter requiring a bounded investigation.

Already visible candidates for review include source-level Mz completeness,
the prospective off-banzuke rule, complete manifest hashing, P1-WL's
future-informed retrospective fit, low-support exact-chii behaviour, and the
absence of an uncertainty coordinate. Listing them does not prejudge that
each deserves a new package: some may be disclosures or engineering work
rather than unresolved model decisions.

## Immediate next step

Create a successor copy of the expert account, apply the revision map there,
and preserve this baseline plus its matters-arising record unchanged. Once the
successor is internally consistent, perform the second-pass issue inventory
and decide which findings deserve new matters-arising investigations.
