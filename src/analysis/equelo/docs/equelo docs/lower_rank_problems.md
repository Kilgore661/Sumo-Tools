# Lower-Rank Problems in Equelo

## Status

This is a working note. It records why the lowest ranks are difficult for an Elo-like rating system, why those ranks have nevertheless been included in Equelo so far, and what kinds of investigation remain open.

It should not be read as the final explanation of the lower-division results. The point is to define the problem clearly enough that later experiments can test whether the observed behaviour is a defect in the model, a real feature of the data, or a mixture of both.

## The Problem

Equelo applies Elo-like rating dynamics across the banzuke. That means a rikishi has a rating, gains or loses rating points after bouts, and carries that rating forward through time. This works best when the rating population is reasonably connected and reasonably stable.

The lowest divisions are not obviously like that.

Jonokuchi, and to a lesser extent low Jonidan, appear to have very high churn. Many rikishi enter the system, lose repeatedly, and disappear after only a small number of ranking events. Other rikishi pass through quickly on the way upward. The result is a population that may not behave like the stable competitive pool that an Elo-style system implicitly wants.

This matters because Elo ratings are not just labels attached to individuals. They work by transferring rating information through bouts. A rating becomes meaningful because a rikishi fights other rated rikishi, who fight other rated rikishi, and so on. The more connected the network, the more interpretable the ratings become.

A high-churn population weakens that process. If many rikishi leave before becoming well connected to the rating network, the system is constantly assigning initial ratings to people who will not remain long enough to contribute much stable information. This creates two related problems:

1. the rating system may have too little evidence to estimate some ranks independently; and
2. the normal Elo assumption of a reasonably persistent competitive pool may be least true precisely where the banzuke is most volatile.

## Sparse Ranks and Unsupported Chii

One visible symptom is the behaviour of rare or sparsely supported chii.

A raw fixed-point process can, in principle, assign an independent value to every chii. In practice, not every chii deserves that treatment. Some ranks have enough observations to support a direct estimate. Others may be represented by very few cases. In an extreme case, a rank might be dominated by one rikishi, one basho, or a small accident of the historical record.

Earlier Equelo experiments produced pathological examples of this kind. The memorable case is a very deep Jonokuchi rank such as `Jk73w` acquiring an absurdly high rating, around 3000 or more, despite the rank itself clearly not representing elite strength in any ordinary sense.

That kind of result is not an interesting discovery about `Jk73w`. It is a warning that the raw fixed-point process can produce nonsense when the data do not support an independent estimate.

The current supported-chii approach is a response to this problem. It distinguishes between chii with enough support and chii without enough support. Supported chii receive direct estimates. Unsupported chii are completed by a defined rule, such as borrowing from the nearest supported chii in rank order.

That solves one problem: it prevents obviously unsupported ranks from acquiring spurious independent values. But it does not solve the deeper question of whether Elo-like dynamics are reliable in the highest-churn parts of the banzuke.

## The Churn Hypothesis

The main hypothesis is this:

> The lowest-rank anomalies may arise because Elo-like rating dynamics are being applied to a population with too much churn.

This is not specifically an Equelo problem. It may be an Elo problem. Equelo adds fixed-point initialisation, mean conservation, support filtering, and completion rules, but the bout-by-bout update mechanism remains Elo-like. If the underlying population does not satisfy the assumptions that make Elo useful, Equelo will inherit that weakness.

In a stable rating pool, competitors remain long enough for ratings to become informative. New entrants join, but they are gradually connected to the existing rating network. Strong competitors tend to move upward; weak competitors tend to move downward or out. The rating scale has time to learn.

In a very high-churn pool, the situation is different. Many entrants may lose, donate rating points to the active population, and leave. Others may be passing through on the way to higher ranks. The population at a given chii may therefore be a mixture of several quite different types:

- new rikishi who will soon leave;
- new rikishi who are under-ranked and will rise quickly;
- injured or returning rikishi;
- rikishi temporarily trapped by banzuke mechanics;
- very weak long-stayers;
- historically unusual cases created by the shape of the banzuke in a particular era.

A rank containing that mixture may not have a single stable meaning in the way a simple rank-rating curve suggests.

## The Jonidan/Jonokuchi Shape

A recurring observation is that the lower-division rank curve is not simply monotone.

In broad terms, the curve can look sensible down through much of Jonidan, but then behave strangely around low Jonidan and Jonokuchi. One reported pattern is that the curve behaves reasonably until roughly `Jd100`, then begins to move in the wrong direction: values rise toward `Jk1`, then drop, and may rise again through Jonokuchi.

The exact shape needs to be checked against the current generated data. But the important point is conceptual: if the lowest-rank curve is non-monotone in a systematic way, smoothing it away would be dishonest. The anomaly should be reported and investigated.

There are at least three broad explanations:

1. **The model is seeing something real.**  
   The population at some lower ranks may genuinely contain a mixture of rikishi whose future strength is not well represented by their current chii.

2. **The model is exposing a data-structure problem.**  
   Some ranks may be too sparse, too historically contingent, or too affected by banzuke shape to support direct interpretation.

3. **The model is failing.**  
   The Elo-like assumptions may be too weak in high-churn regions, so the resulting values are artefacts of the method rather than features of sumo.

These possibilities are not mutually exclusive.

## Why Include the Lowest Ranks At All?

A fair question is: if the lowest ranks are so troublesome, why include them?

There are several reasons.

First, the lower divisions are part of sumo. A rating system that claims to use the banzuke should be cautious about simply cutting away the part of the banzuke that is hardest to model.

Second, the lower divisions are part of the career path. A sekitori does not appear from nowhere. He passes through lower divisions first. Even if the lowest ranks are noisy, they are part of the historical mechanism by which future sekitori enter the rating population.

Third, the banzuke itself supplies information before complete bout records exist. If Equelo is going to use chii as evidence, it should at least attempt to understand the meaning of chii across the whole banzuke, even if confidence varies by division.

Fourth, excluding the lowest ranks might create a different kind of arbitrary boundary. If Jonokuchi is excluded, why not low Jonidan? If low Jonidan is excluded, why not all of Jonidan? Any cut needs a principled justification, not merely aesthetic discomfort with ugly results.

Fifth, including the lowest ranks lets the model reveal its own weaknesses. The strange behaviour is not only a nuisance. It is evidence about where the assumptions are under strain. Removing the difficult region too early may make the outputs look cleaner while teaching us less.

These reasons do not prove that the lowest ranks must always be included. They explain why they have been included so far.

## Current Working Assumption

For now, Equelo effectively makes the following assumption:

> Lower-division churn does not invalidate the rating process enough to justify excluding the affected ranks entirely.

This is a pragmatic assumption, not a settled truth.

It says that the lower ranks are noisy and sometimes suspect, but still worth including while the model is being developed and investigated. It also says that claims based on these ranks should be weaker than claims based on better-supported parts of the banzuke.

A stronger future version of Equelo might handle this differently. It might exclude the lowest ranks, use different entrant rules, use different aggregation rules, treat high-churn ranks as a separate population, or report confidence bands rather than single rank values. Those possibilities remain open.

## What We Should Not Do

There are two tempting but wrong responses.

The first is to hide the problem by smoothing the curve. If the raw or supported model says that a lower rank has a higher value than a rank above it, a public artefact should not silently replace that result with the value we expected. That would turn a descriptive result into a teleological one: what the ranks should mean, not what the model found.

The second is to treat every anomaly as a discovery. If the model says something surprising about `Jd100` or `Jk1`, that is not automatically a fact about sumo. It may be a real structural feature. It may also be an artefact of churn, sparse data, completion rules, or the fixed-point procedure.

The right response is to report the anomaly, identify possible causes, and test them.

## Experiments to Consider

The following experiments would help clarify the issue:

1. **Division-cut experiments**  
   Run Equelo with the lowest ranks excluded at different cut points, such as below `Jd100`, below Jonidan, or below Sandanme, and compare the effect on upper-division ratings.

2. **Churn measurement**  
   Measure survival rates by chii or division: how many rikishi remain active after one, three, six, or ten ranking events?

3. **Connectivity analysis**  
   Examine how strongly low-rank rikishi connect to the wider rating network before leaving.

4. **Entrant-type classification**  
   Separate rikishi who quickly leave from rikishi who rise rapidly and from rikishi who remain long-term at low ranks.

5. **Sensitivity to initial values**  
   Test whether low-rank anomalies persist under different initial maps, baseline ratings, or support thresholds.

6. **Supported-only comparison**  
   Compare raw fixed-point values, supported fixed-point values, and completed values to see which anomalies survive support filtering.

7. **Impact on sekitori ratings**  
   Test whether changing the treatment of low ranks materially changes the ratings of later sekitori. If it does not, then the low-rank problem may matter mainly for lower-division interpretation rather than for the headline use of Equelo.

## Provisional Conclusion

The lower ranks are difficult because they may violate the stable-population assumptions that make Elo-like ratings meaningful. Sparse ranks can produce absurd fixed-point values, and high-churn regions may produce non-monotone rank curves that are hard to interpret.

The current answer is not to pretend the problem does not exist. Nor is it necessarily to exclude the lowest ranks immediately. The current answer is to include them cautiously, use support filtering and completion to prevent the worst pathologies, and treat lower-rank results as less secure than results from better-supported regions.

Equelo is a lens. The lower ranks may be where the lens distorts most. That does not mean the lens is useless. It means this is where we need to understand its shape.
