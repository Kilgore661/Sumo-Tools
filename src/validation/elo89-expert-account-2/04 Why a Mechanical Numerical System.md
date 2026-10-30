# 4. Why a Mechanically Derived Numerical System?

> **Draft status:** First continuous-prose draft. The numerical example is
> illustrative; a later editorial pass may replace it with named cases from a
> frozen published standings snapshot.

## Why not just count the wins?

Suppose we want to know who has performed best over the last six basho. An
obvious answer is: count each rikishi's wins and put the largest total first.

That is a legitimate calculation. If the question is literally “who
accumulated the most credited wins in this period?”, the total answers it. The
problem begins when the total is allowed to answer a broader question without
further argument. Rikishi do not all receive or take the same number of bout
opportunities. They may miss individual days or complete basho, enter or leave
the population, compete under different divisional schedules, or move between
divisions during the selected period.

Once exposure differs, “most wins” and “most successful when competing” are
not the same idea.

Consider a deliberately simple example. Rikishi A competes in all six basho,
fights 90 bouts and wins 45. Rikishi B competes in three, fights 45 bouts and
wins 27.

| Rikishi | Wins | Wins per selected basho | Wins per bout fought |
| --- | ---: | ---: | ---: |
| A | 45 | 7.5 | 50% |
| B | 27 | 4.5 | 60% |

The first two columns favour A; the last favours B. No arithmetic error has
occurred. The measures disagree because they retain different meanings.

Wins per selected basho rewards output over the whole period. Absence reduces
the result, so availability is part of what the measure values. Wins per bout
fought asks how often the rikishi won when a recorded contest took place. It
largely removes absence from the denominator and concentrates on realised
success while competing.

Neither is the uniquely correct meaning of performance. If we care about
sustained contribution across a six-basho period, A has the stronger claim. If
we care about success conditional on appearing in a bout, B does. The dispute
cannot be settled by recalculating more accurately; it requires us to decide
which question we mean to ask.

## The site's rolling standings make the choice visible

The **Grand Sumo Standings by Wins Digest** is a working example of this
problem, not a deliberately weak alternative invented to make Elo look good.
It provides a useful rolling view of recent results and publishes two related
scales:

- **Average** is credited wins divided by the selected number of basho; and
- **Win %** is credited wins divided by expected bout opportunities over that
  period.

The second denominator deserves attention. It is not simply the number of
bouts which happen to have a recorded result. The current product uses
*expected* bouts, based on the division in which the rikishi was scheduled to
compete. That policy prevents every missed contest from vanishing harmlessly
from the denominator, but it is itself a choice. Another table could use bouts
actually fought, bouts for which the rikishi was available, basho in which he
appeared, or some other defined exposure.

Expected opportunities also differ across divisions. Consequently, division
history and movement during the window can affect the relation between Average
and Win %. Two published scales therefore appear even before any allowance is
made for the identity of the opponents.

The Combined view does not declare one scale the winner. That is its analytical
value: it lets us see how conclusions change when the denominator changes.

## Every concise table rests on policies

The denominator is only one choice. A rolling wins table must also specify:

- **window:** six basho, twelve basho or another period;
- **endpoint:** the basho at which the retrospective window is anchored;
- **win policy:** whether a credited win such as fusensho counts;
- **bout policy:** actual, available or expected opportunities;
- **basho policy:** all selected basho or only those containing an appearance;
- **population:** current rikishi or everyone represented during the window;
- **division:** one division, the current division, historical divisions or
  the complete population; and
- **ties and filtering:** how the displayed comparison set determines places.

The present standings product makes one coherent set of choices: credited
wins including fusensho, the selected basho window, expected bout opportunity,
and a user-selectable current-versus-all population. Other choices could be
equally reproducible and answer different questions.

This is not a criticism of the product. A useful measure must choose. The
lesson is that simplicity at the point of display can conceal substantial
semantic work underneath. “Wins: 45” is mechanically exact only after we have
said which events count as wins and which period and population are in scope.

## The opposition problem

Even a perfectly specified wins measure leaves another source of
non-comparability. Rikishi do not face identical opposition.

Two rikishi can record the same number or percentage of wins against very
different schedules. Promotion illustrates the issue particularly clearly. A
rikishi may be winning because his present opposition is relatively weak, then
produce a lower percentage after promotion despite performing at least as well
in a meaningful competitive sense. The result total has changed, but so has
the problem he was being asked to solve.

Sumo is not a full round robin. Rank and division strongly constrain the
available opponents, and torikumi within a basho are selective. Some rikishi
meet repeatedly; others do not meet at all. The schedule is also connected to
the same competitive history we are trying to assess. We cannot make records
comparable merely by dividing every total by the number of opportunities.

One response is to assign each opponent a level and weight a result
accordingly. But where does that level come from? Current chii supplies useful
information but not the cardinal scale discussed in Section 2. Recent win
percentage has the same unequal-opposition problem. Asking experts to assign a
number returns us to an informed but case-dependent judgement.

The comparisons are interdependent. X's result against Y tells us something
about X only in relation to what we think about Y; what we think about Y
depends partly on results against Z and others. This is not a logical circle to
be avoided. It is the connected structure of the evidence that a rating model
must represent.

## What “mechanical” can and cannot mean

A mechanically derived system applies declared rules to declared inputs. Once
the version of the rules and the data are fixed, another investigator can
repeat the calculation and obtain the same output. Case-by-case discretion is
not introduced during the replay merely because a particular result or
rikishi looks surprising.

That is valuable, but it is not the same as being assumption-free or
objectively compelled by the data. People still choose the target, evidence,
population, scale, parameters and exceptional-case policies. A formula can
apply those choices consistently; it cannot prove that they were the only
reasonable choices.

The distinction is therefore:

```text
judgement in designing the model
    -> fixed, inspectable rules
    -> mechanical application to the record
    -> outputs which can be criticised and tested
```

This is the relevant advantage over an undefined appeal to “strength”. It does
not eliminate judgement. It moves consequential judgement into an explicit
specification where its effects can be investigated.

## What an Elo-like model adds

An Elo-like system is one response to the opposition problem. Instead of
giving every win the same fixed credit, it interprets a result through the
opponent's current rating. That rating carries forward earlier results against
other opponents. As bouts are processed through time, information propagates
through the connected contest network.

The resulting state combines, under a chosen set of rules:

- wins and losses;
- the model's current estimates of the opponents;
- the chronological order of the evidence;
- movement through changing schedules and divisions; and
- earlier evidence retained in every opponent's rating.

This avoids choosing a fixed six-basho window for the rating itself, but it
does not make time disappear. The update policy determines how later evidence
displaces the influence of earlier states. Nor does Elo automatically model
availability, injury, style, bout importance or non-transitive matchups. It
compresses the admitted opponent-relative evidence into one scalar; it does
not preserve every explanation of the record.

The reason to investigate Elo is therefore not that simple measures are wrong
and Elo is definitive. It is that direct summaries answer several different
questions and do not, by themselves, reconcile unequal opposition. Elo offers
a transparent way to make one connected, opponent-sensitive comparison. Its
own assumptions and failures must then be exposed to exactly the same
scrutiny.

The next chapter begins that scrutiny with ordinary Elo: the probability
equation, the update rule and the role of its parameters.

## Working sources

- `../../analysis/standings/README.md`
- `../../analysis/standings/docs/Specification.md`
- `../../analysis/standings/docs/Rationale.md`
- `../../analysis/standings/docs/UI Feature Impact Taxonomy.md`
- `../../products/make_site2/prose/archive/Elo Ratings.html`
