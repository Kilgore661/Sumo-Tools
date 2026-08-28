# Preliminary Production Sanity Checks and Fan Challenges

## Status and purpose

This is a developing production-readiness record for Equelo2. It approaches
the model from the perspective of people who may encounter the eventual web
site: casual sumo fans, statistically literate readers and people with deep
knowledge of sumo history.

This exercise is deliberately different from model selection. A change in the
second decimal place of a log-loss value may be statistically or technically
important, but it will not answer a reader who asks why the ratings look
credible, why Hakuho ranks above Taiho, or why Kakuryu appears unusually high.
The purpose here is to anticipate those reactions, state the strongest honest
response and identify cases where the response exposes a model weakness rather
than resolving the challenge.

These checks complement quantitative evaluation; they do not replace it. A
historically plausible table can still be predictively useless, and a useful
predictor can still encode assumptions which make a particular historical
comparison difficult to defend.

## Observation convention

A published Equelo2 rating is observed after the named basho's eligible bouts
and all post-basho processing. Career peaks and records use only this processed
basho-end value. Internal start-state values are not rating observations.

## Challenge: “Where did the initial ratings come from?”

The entrant priors are constructed from the historical relationship between
banzuke position and the ratings produced by the accepted Elo/Equelo dynamics.
The fixed-point process deliberately uses later historical results to obtain
useful initial values. It is not claimed to create an out-of-sample forecast of
the same construction history.

The first practical test is whether the complete system containing those
priors extracts useful information at all. Proto-Equelo2 beats the neutral
50--50 predictor over the complete represented history:

| Measure | Proto-Equelo2 | Neutral 50--50 |
|---|---:|---:|
| Mean log loss | 0.679354 | 0.693147 |
| Mean Brier loss | 0.243025 | 0.250000 |

This is a retrospective sanity check, not a prospective claim. If the system
performed poorly even under this deliberately favourable test, the prior
construction would have failed a basic usefulness requirement. Passing the
test shows that the chosen priors participate in a coherent and useful rating
system; it does not show that they are uniquely optimal.

Once a named Equelo2 version and its prior map are frozen, genuinely later
results can be used for prospective evaluation without changing that version.

## Challenge: “Were the pre-1989 results added to improve later predictions?”

No. The purpose of extending Elo-89 backwards is to create one continuous
rating account in which historical rikishi such as Taiho can be compared with
modern rikishi such as Hakuho. Elo-89 supplies the priors, scale and update
machinery needed to incorporate the incomplete earlier evidence.

The common post-1988 forecast comparison is a compatibility check. It asks
whether carrying the historical state across January 1989 materially damages
the established later account. Proto-Equelo2's post-1988 log loss is 0.675281,
compared with 0.675498 for a fresh Elo-89 start, so no such damage is observed.
The small favourable difference is incidental. It is not the benefit the
historical extension was designed to obtain, and no claim that pre-1989
evidence improves modern ratings is required.

## Challenge: “Does the pre-1989 replay itself beat 50--50?”

The two proper scores give mixed answers over the 165,780 rated pre-1989 bouts:

| Measure | Proto-Equelo2 | Neutral 50--50 | Difference |
|---|---:|---:|---:|
| Mean log loss | 0.693589 | 0.693147 | +0.000442 |
| Mean Brier loss | 0.249519 | 0.250000 | -0.000481 |

The log score is minutely worse than neutral and the Brier score minutely
better. Both differences are at roughly the fourth decimal place and point in
opposite directions. They must be disclosed, but they are not treated as a
substantive concern or concealed behind the stronger all-history result. The
pre-1989 extension was not introduced to establish forecasting power on that
incomplete interval; its purpose is historical inclusion and comparison.

## Challenge: “Hakuho only leads because Taiho's rating had not stabilised”

The processed Equelo2 peak comparison is:

| Rikishi | Peak rating | Basho | Rated bouts accumulated |
|---|---:|---:|---:|
| Hakuho | 3031.291 | 2010/09 | 701 |
| Taiho | 2891.554 | 1969/01 | 783 |

Taiho had accumulated more rated bouts than Hakuho at their respective peaks.
The 139.737-point difference therefore cannot reasonably be dismissed as
Taiho merely lacking time to move away from his initial rating.

## Challenge: “Hakuho competed later, when there were more rating points to win”

Equelo2 restores the active population to a fixed mean after every basho.
Consequently, the rating origin cannot simply drift upward across the decades
as an unnormalised Elo implementation can. Hakuho's higher peak is not the
known mechanical artefact in which later competitors inherit an inflated
rating pool.

This does not prove that every population effect has disappeared. The model
still assumes that its active-population anchor is comparable across eras, and
population composition, schedule structure and entrant policy can affect the
rating distribution around that anchor.

## Conditional conclusion: Hakuho and Taiho

Under `q=400`, Hakuho's 139.737-point peak advantage corresponds to an
approximately 69% expected score in a hypothetical peak-versus-peak matchup.
The appropriate claim is therefore conditional but substantive:

> If the reader accepts the Equelo2 model contract and accepts peak rating as
> the meaning of “better”, Equelo2 says that Hakuho was better than Taiho.

A Taiho supporter may still dispute the model's cross-era assumptions, the
historical invariance of chii meaning, the active-population anchor, or the use
of peak performance as the definition of greatness. Those are genuine
substantive objections. Uncorrected rating inflation and insufficient time for
Taiho's rating to stabilise are not.

The result is not offered as proof of the GOAT. It is evidence that Equelo2 can
give a clear answer to one familiar historical question while making the
assumptions behind that answer visible.

No further Hakuho--Taiho robustness sweep is required for the Equelo2 candidate.
Such a sweep could expand indefinitely across choices about era strength,
population composition, anchoring and the definition of greatness. The project
records the conditional model result and its assumptions rather than making
that fractal exercise a production gate. This is also proportionate to the
ordinary public prior that Hakuho is the leading post-1958 GOAT candidate.

## Comparative observation: Kakuryu

Using processed basho-end peaks, proto-Equelo2 ranks Kakuryu eleventh and he
does not appear in its top ten. The older fixed-supported production Equelo
ranks him fifth, at 2677.432 after 2016/11. His top-ten position is therefore a
legacy-Equelo observation, not an Equelo2 candidate problem, and it is not
caused by selecting an intrabasho maximum.

The contrast is still worth preserving: it shows that materially different
Equelo constructions can produce different elite rankings. It may motivate an
investigation of legacy Equelo, but Kakuryu's absence from Equelo2's top ten is
not something the Equelo2 candidate must defend or repair.

## Scope limit: pre-1958 candidates

The represented History begins in January 1958. Equelo2 therefore cannot
adjudicate claims for Futabayama, Raiden or other earlier candidates. A public
“greatest ever” description must either state that scope or use language such
as “highest in the represented 1958-onward history.”

## Current production-readiness questions

Before treating the candidate as ready for public historical claims:

1. examine the November 1988 endpoint, the January 1989 handover and the
   historical chii-to-rating maps;
2. complete the fixed-pool realised-outcome comparison with 50--50 recorded in
   the story index;
3. decide which claims describe peak performance, career achievement,
   dominance over contemporaries or another meaning of “greatness”;
4. express the statistical evidence in language that answers the reader's
   actual challenge rather than substituting a small score difference for an
   explanation.

This document should grow by adding concrete challenges, the best available
response, the evidence supporting it and any unresolved model vulnerability.
