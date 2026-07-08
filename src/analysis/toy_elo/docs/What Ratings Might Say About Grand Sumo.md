# What Ratings Might Say About Grand Sumo

This note records the current usefulness lens for the toy Elo and bridge
experiments. It is not a conclusion about Grand Sumo, and it is not a
metaphysical account of what rank "really" means. The point is narrower: to
state what kind of question the ratings can help us ask.

## The Modelling Claim

The toy experiments begin with an intentionally artificial world:

```text
a fixed pool of players
a fixed latent skill for each player
match outcomes generated probabilistically from those latent skills
an initial rating estimate
```

In that world, the Elo process can recover the latent skill structure within a
chosen tolerance. In the two-division version, the players are split into
skill-contiguous upper and lower divisions, most bouts occur within divisions,
and a sparse bridge connects the division boundary. Under the evidence-aligned
Makuuchi-Juryo bridge model tested so far, Elo still recovers a commensurate
rating scale across the two divisions.

That is the modest experimental result. It says that one family of controlled
experiments is consistent with the hypothesis that sparse inter-division
matching can be enough to keep ratings on a shared scale.

It does not show that all plausible sumo worlds behave this way.

## From Players To Labels

There is a useful shift from thinking about toy players to thinking about
ordered labels.

If the players are ordered by true skill and assigned labels:

```text
A, B, C, ...
```

then the labels can be read as names for ordered skill slots. In that reading,
Elo is not only estimating the players. It is estimating the rating value of
the labelled slots.

This is the bridge to chii. If chii are treated as ordered labels, and if their
ordering is assumed to correspond to latent skill, then ratings can be used to
estimate something like the typical value of each chii slot.

That assumption is doing real work. The model does not prove that chii are
skill slots. It gives us a disciplined way to ask what follows if we treat
them as if they were.

## The Useful Fiction

One possible fiction is that the banzuke reveals the right order. On this view,
`M3e` is not merely an administrative position created by records, vacancies,
and precedent. It is a meaningful station, and the JSA assigns a rikishi to
that station because the rikishi belongs there.

The opposite fiction is that Elo measures the real fighting strength, while
the banzuke is theatre, convention, or institutional convenience.

Neither fiction should be allowed to win by temperament. Ratings are useful
because they let us make the disagreement visible:

```text
What does Elo see that the banzuke does not encode?
What does the banzuke encode that Elo does not see?
Which disagreements are transient?
Which disagreements are structural?
```

The aim is not to decide in advance whether Elo is truer than the banzuke, or
whether the banzuke is truer than Elo. The aim is to create measurements that
make those positions testable enough to argue with.

## What A Rating Is Saying

An Elo rating in this project should be read narrowly:

```text
under this outcome model
over this evidence window
with this update rule
and this schedule structure
the inferred bout-winning strength is ...
```

That is already useful, but it is not the same as:

```text
the rikishi's true worth
the true meaning of the chii
the JSA's true judgement
```

Those larger claims may be interesting, but they are not directly measured by
the rating.

## When Ratings And Chii Disagree

Suppose rikishi X is ranked `M3e`, rikishi Y is ranked `M2w`, and the rating of
X is higher than the rating of Y. There are several possible interpretations:

```text
1. The rating process has not yet converged, or the inversion is sampling noise.
2. X and Y are imperfect instances of their assigned chii slots.
3. Chii are not absolute skill stations; they are constrained banzuke positions.
4. Ratings and banzuke are answering different time-window questions.
```

The fourth possibility matters. A banzuke rank may reflect recent record,
promotion history, injury context, and slot availability at banzuke-making
time. A rating may reflect a different evidence window and a different concept
of strength. Disagreement is therefore not automatically an error.

It is a diagnostic.

## Bias Guardrails

There are two tempting extremes:

```text
A. Elo does not lie; persistent disagreement shows the banzuke is made up.
B. The banzuke is authoritative; persistent disagreement shows the model is wrong.
```

The middle path is not automatically safer. It can become just as biased if it
is chosen because it feels more reasonable. The useful discipline is to keep
measurement and interpretation separate.

The model should avoid claims framed as:

```text
what rank really means
who is really stronger
what the JSA really knows
```

and prefer claims framed as:

```text
under this model, this rating inversion persists
under this evidence window, this chii has this inferred value
under this bridge structure, the two divisions become commensurate
```

That does not eliminate bias, but it makes the bias visible enough to inspect.

## Anti-Teleology Guardrail

The chii pivot is especially dangerous because it invites an Elo-like model to
become an explanation engine. Once the target is "explain what we see at the
level of chii", it becomes easy to add mechanisms until the model produces an
interpretation that feels satisfying.

That is not the aim.

The aim is not to create an Elo-like model that explains chii. The aim is to
test whether a deliberately constrained rating model produces stable,
interpretable signals at the level of chii. If it does not, that is a result,
not an invitation to keep adding mechanisms until it does.

This guardrail applies to both attractive extremes:

```text
If the model disagrees with chii, we should not immediately conclude that the
JSA is biased, theatrical, or inconsistent.

If the model agrees with chii, we should not immediately conclude that chii are
true skill stations or that the JSA has special access to hidden order.
```

It also applies to the comfortable middle. A moderate explanation can be just
as teleological as an extreme one if it is chosen because it feels plausible
rather than because it survived a constrained test.

Before adding a new sumo-specific mechanism, we should state:

```text
what problem it is meant to solve
what observable output it is expected to change
what simpler alternative it is being preferred over
what result would count against adding it
```

The model should be allowed to fail. A failure to produce stable chii-level
signals is not a defect to be patched away automatically; it may be the thing
we needed to learn.

## Current Assessment

The toy work is currently useful because it establishes a controlled baseline:

```text
Elo can recover fixed latent skill slots in a closed world.
Elo can still do so when that world is split into two skill-contiguous divisions.
An evidence-aligned Makuuchi-Juryo bridge appears sufficient in the tested setup.
```

This gives us permission to use ratings as a probe of chii-like labels, but
not permission to treat ratings as final truth. The next value of the model is
not that it will settle what Grand Sumo really is. It is that it can make
specific disagreements between rating, rank, schedule, and interpretation
visible enough to study.
