# 1. What is Elo-89?

> **Draft status:** First continuous-prose draft. The descriptions here are
> deliberately provisional: later chapters define *rating*, *model* and
> *competitive performance*, then examine whether Elo-89 earns those words.

## The short answer

Elo-89 is an Elo-like numerical rating system for the represented professional
sumo record from January 1989 onward. It processes eligible wins and losses in
chronological order and maintains one number—a rating—for each represented
rikishi.

The ratings are opponent-sensitive. A win does not have one fixed value. Its
effect depends on the two rikishi's ratings before the bout: defeating an
opponent whom the model strongly favoured is more informative, and therefore
causes a larger update, than defeating an opponent whom it expected to lose.
The same principle applies in reverse to a loss.

At any given instant, the difference between two ratings determines the
model's probability that one rikishi would defeat the other. A higher rating
therefore means, in the limited language of the model, that the rikishi would
be favoured against a lower-rated opponent. The larger the difference, the
stronger the preference. It does not mean that the higher-rated rikishi must
win: an upset is an expected possibility in a probabilistic model.

This is the simplest useful interpretation of an Elo-89 rating. The number is
not a win total, an official rank, or a quantity which can be observed
directly. It is the model's compact state after processing the evidence it has
been designed to use.

## What makes it Elo-89?

Elo-89 inherits the central idea of Elo: use the difference between two
ratings to form an expectation, then revise both ratings when the result is
known. It is *Elo-like*, rather than merely an application of a universal Elo
recipe, because several consequential choices must be supplied before that
idea becomes a working sumo model.

In outline, Elo-89:

- begins with the substantially represented record in January 1989—the source
  of “89” in its name;
- uses paired binary win/loss results selected under a declared bout policy;
- gives a newly represented or returning rikishi an initial rating derived
  from his banzuke position through a fixed table called **P1**;
- makes ratings more or less responsive according to broad rank group through
  a divisional **K** schedule; and
- applies common shifts to keep the represented population centred on a fixed
  mean as that population changes.

Those mechanisms are only signposts here. Later chapters explain ordinary Elo,
identify the additional choices required by sumo, specify each Elo-89 rule and
examine its consequences. In particular, a common population shift changes
the displayed level of every affected rating but preserves all rating
differences—and hence all model probabilities—at that instant. It does not
make questions of comparison through historical time disappear.

## What does an Elo-89 number claim to represent?

For now, we will call it an opponent-sensitive summary of *represented
competitive performance*. Every word in that phrase matters.

It is **represented** because the model can use only the evidence admitted by
its data and bout-selection rules. It does not observe an unrecorded bout or
directly observe injury, health, technique, style, motivation or any other
explanation of a result.

It is **opponent-sensitive** because results are interpreted in relation to
the model's current estimate of the opposition, not merely counted. Earlier
results are carried forward in ratings, so evidence can pass through the
network of rikishi who have fought one another even though sumo does not use a
full round-robin schedule.

It is a **summary** because one scalar cannot preserve everything that may
matter about a rikishi or a bout. Elo-89 deliberately compresses a changing,
connected competitive history into a form that supports comparisons and
probabilities.

And *competitive performance* remains provisional. Elo-89 does not directly
measure an independently observable substance called “true strength”. Nor is
it by itself a measure of greatness, merit, achievement, popularity or likely
career value. Before we can judge whether its rating is meaningful, we must
say what work we want a rating system to do and what would make such a system
good.

## But isn't that what the banzuke already does?

Sumo already publishes an ordering of its rikishi. The banzuke reflects
results, separates competitors into ranks and divisions, and strongly shapes
the opposition they will face. If Elo-89 also uses results to put rikishi in
an order, constructing another system may appear redundant—or even like an
attempt to replace the official one.

It is neither. Elo-89 is intended as a different view of the results, not as a
proposal for improving or automating the banzuke. But that answer immediately
raises the question on which the rest of this account depends: in what sense
is the banzuke already a rating system, and in what sense are Elo-89 and the
banzuke doing different jobs?

That is the subject of the next chapter.

## Working sources

- `../2026 10 19 Elo-89 Ratings Narrative Handoff.md`
- `../../prose/Elo-89 Ratings.html`
- `../../../../analysis/elo89/replay.py`
