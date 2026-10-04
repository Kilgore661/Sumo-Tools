# On Absences

## Status

Working account of the problem and experimental set-up.  This document does
not report the results of the experiment.

## Background

A *torikumi* is the published schedule of bouts for a day of a sumo
tournament.  When a rikishi is unable to compete, they may notify the Japan
Sumo Association that they are *kyujo*.  The JSA then omits them from
forthcoming torikumi.

There is a complication when the relevant torikumi has already been published.
In that case, the rikishi remains listed but does not fight.  Their opponent
receives a *fusen-sho* (`FS`), or win by default, and the absent rikishi
receives a *fusen-pai* (`FP`), or loss by default.

For the purposes of this experiment, a fusen-pai is not called an *absence*.
An FP occurs when the rikishi was named on the torikumi but did not appear.  An
absence occurs when the rikishi was omitted from the torikumi altogether
because their kyujo status was known before it was prepared.

The immediate outcome is essentially the same in either case: the rikishi does
not receive a win.  Conventionally, the final record preserves the
distinction--a fusen-pai is recorded as a loss, whereas an absence is recorded
separately--but the rikishi's score in the sense of their number of wins is
unchanged.  A result might in principle be reported simply as `13`; by
tradition it is written `13-2`, or `13-1-1` if one of the non-wins was an
absence.

There are nevertheless circumstances in which the distinction between a loss
and an absence is significant.  This raises the question of whether the daily
results can tell us when an absence occurred.

## Sekitori and sub-sekitori records

The problem is peculiar to the sub-sekitori divisions.

A sekitori normally fights once on every day of a 15-day basho.  Consequently,
if a sekitori has no result on a particular day, the missing result can
ordinarily be understood as an absence.

A sub-sekitori rikishi normally has only seven bouts during the same 15 days.
Most days on which they have no result are therefore ordinary rest days: they
were not expected to appear on the torikumi.  A day without a result could mean
either:

1. the rikishi was available but was not scheduled to fight that day; or
2. the rikishi was kyujo and was omitted from the torikumi.

The daily record alone does not distinguish between these cases.

## The SumoDB records

SumoDB provides 15 daily result positions for each rikishi, represented in
this analysis by six symbols:

- `W`: a win in a contested bout;
- `L`: a loss in a contested bout;
- `FS`: fusen-sho, or a win by default;
- `FP`: fusen-pai, or a loss by default;
- `d`: a draw; and
- `-`: no recorded result on that day.

SumoDB also gives the rikishi's final record as wins, losses and absences.  The
final record therefore tells us how many absences occurred during the basho,
but its daily record does not tell us which of the `-` entries represent those
absences.

For example, a sub-sekitori rikishi who fought on seven even-numbered days
might have the following daily record:

```text
-W-W-W-W-W-W-W-
```

None of the eight `-` entries need represent an absence.  They are simply days
on which the rikishi was not scheduled.

A similar-looking record containing only six bout results presents a different
problem.  The final record may tell us that the rikishi had one absence, but it
does not directly identify which of the nine `-` entries represents it.

## The JSA scheduling guidance

JSA guidance says that a sub-sekitori rikishi will normally have one bout in
each of seven scheduling windows:

```text
Days 1-2
Days 3-4
Days 5-6
Days 7-8
Days 9-10
Days 11-12
Days 13-15
```

The final window contains three days, but it serves the same function as the
preceding two-day windows.

If this guidance can be relied upon, the daily ambiguity can be resolved at
the level of a window.  A window containing a result records the rikishi's
expected bout opportunity.  A window containing no result can be interpreted
as an absence: the rikishi would normally have fought during that window but
was not placed on the torikumi.

This does not identify the particular day on which the rikishi would otherwise
have fought.  It permits an absence to be assigned only to a scheduling
window.

## Purpose of the experiment

The experiment tests how closely the historical sub-sekitori results conform
to this scheduling model.  If the model describes actual scheduling practice,
an empty window can be distinguished from an ordinary rest day and treated as
an absence.  The experiment therefore asks how often the historical records
allow that inference to be made.

For example, suppose a rikishi's final record is `3-3-1`: three wins, three
losses and one absence.  Suppose also that the six bout results occupy six
different scheduling windows:

```text
(1, 1, 0, 1, 1, 1, 1)
```

There is one recorded absence and one empty window, Days 5-6.  If the JSA
scheduling model applies, the absence can therefore be assigned to that
window.  The record does not reveal whether the rikishi would otherwise have
fought on Day 5 or Day 6.

The proposed conclusion is conditional:

> Given the final number of absences, and assuming that the JSA's normal
> scheduling windows describe the rikishi's expected schedule, the pattern of
> occupied and empty windows may allow the absences to be assigned to
> particular windows.  The experiment determines how often the historical
> records permit that inference.

The experiment does not determine the exact day on which an absent rikishi
would have fought, the reason for the absence, or why an individual record may
depart from the JSA's normal scheduling practice.
The exact result model, exceptional cases and tests are set out in the Stage 1
proposal.
